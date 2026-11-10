"""NyayaLedger reborn for Walrus — core vault (local-vault backend).

Content-addressed blob store + document register + hash-chained audit log.
Python 3 stdlib only. Every receipt / API response carries
``backend: "local-vault"``.

Design lineage: the Day-1 NyayaLedger ``ledger.py`` (SHA-256 content hash,
hash-chained audit log, fail-closed refusal). The hash-chain pattern here
is the same ``verify_chain`` shape: GENESIS -> sha256(prev + canonical).

The hash IS the address: a document's blob id is the SHA-256 of its exact
bytes, so any one-byte change produces a different address and the
original record no longer matches — that is the whole authenticity check.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from datetime import datetime, timezone

BACKEND_LABEL = "local-vault"
BACKEND_NOTE = (
    "Real content-addressed store on local disk (data/blobs/<sha256>). "
    "NOT Walrus testnet — see app/walrus_adapter.py for the live-Walrus path."
)

# Honest serverless caveat (live fix, 10 Nov 2026): on Vercel the register
# is per-instance and ephemeral — one serverless instance only knows the
# documents sealed in THAT instance. A verdict must therefore never depend
# on the register. Every verify result carries this note plus
# ``verification_basis`` ("content-hash" / "content-hash+registry" /
# "registry-only") and ``registered_in_this_vault`` (bool).
REGISTRY_NOTE = (
    "The sealed-document register is per-instance and ephemeral on serverless: "
    "this server instance only knows the documents sealed in this instance. "
    "The verdict comes from the content hash, not the register."
)

MAX_BYTES = 2 * 1024 * 1024  # 2 MB upload limit
MAX_TITLE = 200
MAX_TEXT_CHARS = 200_000  # pasted-text guard (bytes still capped at 2 MB)

DOC_TYPES = (
    "Contract",
    "Affidavit",
    "Power of Attorney",
    "Settlement Deed",
    "Legal Notice",
    "Other",
)

_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def sha256_hex(data: bytes) -> str:
    """SHA-256 of exact bytes, hex-encoded. The hash is the address."""
    return hashlib.sha256(data).hexdigest()


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class VaultError(ValueError):
    """A refused seal / verify — fail-closed, with a plain reason."""


def new_receipt_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"NLW-{stamp}-{uuid.uuid4().hex[:4].upper()}"


# ---------------------------------------------------------------- samples
SAMPLE_DOCS = [
    {
        "title": "SAMPLE — Freelance Services Agreement (Acme / Abhishek)",
        "doc_type": "Contract",
        "issuer": "Acme Pvt Ltd",
        "text": (
            "SAMPLE DOCUMENT — general legal information, not legal advice.\n\n"
            "FREELANCE SERVICES AGREEMENT\n\n"
            "This Agreement is made on 10 November 2026 between Acme Pvt Ltd "
            "(\"Client\") and M S Abhishek (\"Consultant\").\n\n"
            "1. Services. The Consultant will build and deliver a web application "
            "as described in Annexure A, within 30 days of signing.\n\n"
            "2. Fees. The Client will pay INR 50,000 on delivery and acceptance "
            "of the application.\n\n"
            "3. Ownership. On full payment, all rights in the delivered work pass "
            "to the Client. The Consultant retains the right to show the work in "
            "a portfolio.\n\n"
            "4. Termination. Either party may end this Agreement with 7 days' "
            "written notice; work completed up to termination is payable pro rata.\n\n"
            "Signed: Acme Pvt Ltd (Client) — M S Abhishek (Consultant)."
        ),
    },
    {
        "title": "SAMPLE — Affidavit of Identity (Abhishek)",
        "doc_type": "Affidavit",
        "issuer": "M S Abhishek",
        "text": (
            "SAMPLE DOCUMENT — general legal information, not legal advice.\n\n"
            "AFFIDAVIT\n\n"
            "I, M S Abhishek, aged 20 years, resident of Meerut, Uttar Pradesh, "
            "do hereby solemnly affirm and declare as under:\n\n"
            "1. That my full name is M S Abhishek and I am a student of BTech "
            "Computer Science, Shobhit University, Meerut.\n\n"
            "2. That the documents submitted by me in support of my identity are "
            "true and genuine to the best of my knowledge.\n\n"
            "3. That I make this affidavit to confirm my identity for official "
            "purposes.\n\n"
            "DEPONENT\n"
            "Verified at Meerut on 10 November 2026. The contents of this "
            "affidavit are true to my knowledge."
        ),
    },
    {
        "title": "SAMPLE — Legal Notice for Non-Payment of Dues",
        "doc_type": "Legal Notice",
        "issuer": "M S Abhishek",
        "text": (
            "SAMPLE DOCUMENT — general legal information, not legal advice.\n\n"
            "LEGAL NOTICE\n\n"
            "To: Acme Pvt Ltd, Meerut, Uttar Pradesh.\n\n"
            "Under instructions from my client M S Abhishek, I hereby serve you "
            "with this notice:\n\n"
            "1. That my client rendered freelance services to you under an "
            "agreement dated 10 October 2026.\n\n"
            "2. That an amount of INR 50,000 remains unpaid despite repeated "
            "requests.\n\n"
            "3. You are hereby called upon to pay the said amount within 15 days "
            "of receipt of this notice, failing which my client will pursue "
            "appropriate legal remedies, at your cost and consequence.\n\n"
            "— Advocate (on behalf of M S Abhishek), Meerut, 10 November 2026."
        ),
    },
]


class Vault:
    """Blob store + register + audit log, rooted at ``root``.

    Layout under root::
        blobs/<sha256>        raw bytes, filename IS the address
        register.json         {backend, documents: [...]}
        audit.jsonl           one JSON receipt per line, hash-chained
    """

    def __init__(self, root: str):
        self.root = root
        self.blobs_dir = os.path.join(root, "blobs")
        self.register_path = os.path.join(root, "register.json")
        self.audit_path = os.path.join(root, "audit.jsonl")
        os.makedirs(self.blobs_dir, exist_ok=True)
        self.documents: dict[str, dict] = {}
        self._load()
        if not self.documents:
            self.seed_samples()

    # -- persistence -------------------------------------------------
    def _load(self) -> None:
        if os.path.exists(self.register_path):
            with open(self.register_path, encoding="utf-8") as f:
                raw = json.load(f)
            for row in raw.get("documents", []):
                self.documents[row["blob_id"]] = row

    def _save(self) -> None:
        os.makedirs(self.root, exist_ok=True)
        with open(self.register_path, "w", encoding="utf-8") as f:
            json.dump(
                {"backend": BACKEND_LABEL,
                 "documents": [self.documents[k] for k in sorted(self.documents)]},
                f, indent=2, sort_keys=True,
            )

    # -- audit chain (same pattern as Day-1 ledger.py) ---------------
    def _audit(self, entry: dict) -> dict:
        prev_hash = "GENESIS"
        if os.path.exists(self.audit_path):
            with open(self.audit_path, encoding="utf-8") as f:
                lines = [ln for ln in f if ln.strip()]
            if lines:
                prev_hash = json.loads(lines[-1])["hash"]
        entry["prev_hash"] = prev_hash
        canonical = json.dumps(entry, sort_keys=True, separators=(",", ":"))
        entry["hash"] = sha256_hex((prev_hash + canonical).encode("utf-8"))
        with open(self.audit_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")
        return entry

    def audit_log(self) -> list[dict]:
        if not os.path.exists(self.audit_path):
            return []
        with open(self.audit_path, encoding="utf-8") as f:
            return [json.loads(ln) for ln in f if ln.strip()]

    def verify_chain(self) -> dict:
        """Recompute the hash chain. {"ok": bool, "checked": n, "bad_at": seq|None}."""
        entries = self.audit_log()
        prev = "GENESIS"
        for i, e in enumerate(entries):
            check = dict(e)
            claimed = check.pop("hash")
            if check.get("prev_hash") != prev:
                return {"ok": False, "checked": i, "bad_at": e.get("seq")}
            canonical = json.dumps(check, sort_keys=True, separators=(",", ":"))
            if sha256_hex((prev + canonical).encode("utf-8")) != claimed:
                return {"ok": False, "checked": i, "bad_at": e.get("seq")}
            prev = claimed
        return {"ok": True, "checked": len(entries), "bad_at": None}

    def _record(self, action: str, blob_id: str, detail: str) -> dict:
        entry = {
            "seq": len(self.audit_log()) + 1,
            "receipt_id": new_receipt_id(),
            "timestamp_utc": utcnow(),
            "backend": BACKEND_LABEL,
            "blob_id": blob_id,
            "action": action,
            "detail": detail[:500],
        }
        return self._audit(entry)

    # -- blob store: the hash is the address -------------------------
    def store_blob(self, data: bytes) -> str:
        if not data:
            raise VaultError("Cannot seal an empty file or empty text.")
        if len(data) > MAX_BYTES:
            raise VaultError(
                f"File is {len(data):,} bytes — the limit is {MAX_BYTES:,} bytes (2 MB).")
        blob_id = sha256_hex(data)
        path = os.path.join(self.blobs_dir, blob_id)
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(data)
        return blob_id

    def read_blob(self, blob_id: str) -> bytes | None:
        if not _HEX64.match(blob_id or ""):
            return None
        path = os.path.join(self.blobs_dir, blob_id)
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            return f.read()

    # -- seal / verify / register ------------------------------------
    def seal(self, data: bytes, *, title: str, doc_type: str, issuer: str) -> dict:
        title = (title or "").strip()
        issuer = (issuer or "").strip() or "Issuer"
        if not title:
            raise VaultError("A title is required to seal a document.")
        if len(title) > MAX_TITLE:
            raise VaultError(f"Title must be ≤ {MAX_TITLE} characters.")
        if doc_type not in DOC_TYPES:
            raise VaultError(f"Unknown document type: {doc_type!r}.")
        if len(issuer) > 200:
            raise VaultError("Issuer name must be ≤ 200 characters.")
        blob_id = self.store_blob(data)
        if blob_id in self.documents:
            receipt = self._record(
                "seal-duplicate", blob_id,
                f"Re-sealed (identical bytes); existing record kept: {title}")
            return {"document": self.documents[blob_id], "receipt": receipt,
                    "duplicate": True}
        doc = {
            "blob_id": blob_id,
            "title": title,
            "doc_type": doc_type,
            "issuer": issuer,
            "timestamp_utc": utcnow(),
            "status": "SEALED",
            "size_bytes": len(data),
            "sha256": blob_id,
            "backend": BACKEND_LABEL,
        }
        self.documents[blob_id] = doc
        self._save()
        receipt = self._record(
            "seal", blob_id, f"Sealed {doc_type}: {title} (issuer {issuer})")
        return {"document": doc, "receipt": receipt, "duplicate": False}

    def seal_text(self, text: str, *, title: str, doc_type: str, issuer: str) -> dict:
        if not (text or "").strip():
            raise VaultError("Cannot seal empty text — paste the document text first.")
        if len(text) > MAX_TEXT_CHARS:
            raise VaultError(f"Pasted text must be ≤ {MAX_TEXT_CHARS:,} characters.")
        return self.seal(text.encode("utf-8"), title=title, doc_type=doc_type,
                         issuer=issuer)

    def verify(self, data: bytes, expected_blob_id: str | None = None) -> dict:
        """Verify bytes — STATELESS primary path (live-serverless fix, 10 Nov 2026).

        The verdict comes from the content hash alone, never from the
        per-instance register:
        - expected given and hash != expected  -> TAMPERED
        - expected given and hash == expected  -> AUTHENTIC (the hash IS the
          address: these bytes are byte-for-byte the document sealed under
          that id, wherever it was sealed)
        - no expected and hash in this register -> AUTHENTIC
        - no expected and hash in no register   -> NOT FOUND
        The register is only a SECONDARY signal: ``registered_in_this_vault``
        says whether this server instance also holds a record, and
        ``registry_note`` says the register is per-instance/ephemeral on
        serverless. A registry miss is never the verdict.
        Every verify writes an audit receipt (per-instance on serverless).
        """
        if not data:
            raise VaultError("Nothing to verify — upload a file or paste a hash.")
        if len(data) > MAX_BYTES:
            raise VaultError(
                f"File is {len(data):,} bytes — the limit is {MAX_BYTES:,} bytes (2 MB).")
        digest = sha256_hex(data)
        expected = (expected_blob_id or "").strip().lower() or None
        if expected and not _HEX64.match(expected):
            raise VaultError(
                "That expected blob id is not a valid 64-character hex "
                "SHA-256 — check for a typo. It was not treated as tampering.")
        doc = self.documents.get(digest)
        registered = doc is not None
        if expected and expected != digest:
            expected_doc = self.documents.get(expected)
            receipt = self._record(
                "verify", expected,
                f"TAMPERED: bytes hash {digest[:16]}… does not match claimed "
                f"blob id {expected[:16]}…")
            return {"ok": False, "verdict": "TAMPERED", "backend": BACKEND_LABEL,
                    "computed_hash": digest, "expected_blob_id": expected,
                    "document": expected_doc,
                    "verification_basis": "content-hash",
                    "registered_in_this_vault": registered,
                    "registry_note": REGISTRY_NOTE,
                    "explanation": (
                        "The file's hash does not match the claimed blob id. "
                        "Even one changed character changes the hash completely, "
                        "so this file is NOT the document that was sealed under "
                        "that id."),
                    "receipt": receipt}
        if expected:
            receipt = self._record(
                "verify", digest,
                "AUTHENTIC (content-hash): bytes hash equals the claimed blob id"
                + ("; also in this instance's register" if registered
                   else "; not in this instance's register (verdict is from the hash, not the register)"))
            return {"ok": True, "verdict": "AUTHENTIC", "backend": BACKEND_LABEL,
                    "computed_hash": digest, "expected_blob_id": expected,
                    "document": doc,
                    "verification_basis": "content-hash",
                    "registered_in_this_vault": registered,
                    "registry_note": REGISTRY_NOTE,
                    "explanation": (
                        "The file's SHA-256 equals the claimed blob id. The hash "
                        "IS the address — these bytes are byte-for-byte the "
                        "document sealed under that id. This check needs no "
                        "server storage, so it works on any server instance."),
                    "receipt": receipt}
        if registered:
            receipt = self._record(
                "verify", digest, f"AUTHENTIC: hash matches sealed record: {doc['title']}")
            return {"ok": True, "verdict": "AUTHENTIC", "backend": BACKEND_LABEL,
                    "computed_hash": digest, "expected_blob_id": None,
                    "document": doc,
                    "verification_basis": "content-hash+registry",
                    "registered_in_this_vault": True,
                    "registry_note": REGISTRY_NOTE,
                    "explanation": (
                        "The file's SHA-256 matches a sealed record in this "
                        "vault — same bytes, same address. This is the authentic document."),
                    "receipt": receipt}
        receipt = self._record(
            "verify", digest,
            "NOT FOUND: no sealed record has this hash.")
        return {"ok": False, "verdict": "NOT FOUND", "backend": BACKEND_LABEL,
                "computed_hash": digest, "expected_blob_id": None,
                "document": None,
                "verification_basis": "content-hash",
                "registered_in_this_vault": False,
                "registry_note": REGISTRY_NOTE,
                "explanation": (
                    "No document with this hash is in this vault's register. "
                    "To check it against a claimed blob id, paste that id too — "
                    "the hash comparison then works on any server instance."),
                "receipt": receipt}

    def verify_hash(self, blob_id: str) -> dict:
        """Verify by pasted hash / blob id alone (no file).

        Registry-only lookup — a SECONDARY signal, never the verdict on
        content. On serverless the register is per-instance/ephemeral, so
        NOT FOUND here means "not in THIS instance's register", not "never
        sealed anywhere": the honest check is to paste the document itself
        (file or text) together with this blob id — see verify().
        """
        blob_id = (blob_id or "").strip().lower()
        if not _HEX64.match(blob_id):
            raise VaultError(
                "That is not a valid blob id — paste the full 64-character "
                "hex SHA-256 (shown as 'blob id' on any sealed document).")
        doc = self.documents.get(blob_id)
        if doc is not None:
            receipt = self._record(
                "verify", blob_id, f"AUTHENTIC (by hash): {doc['title']}")
            return {"ok": True, "verdict": "AUTHENTIC", "backend": BACKEND_LABEL,
                    "computed_hash": blob_id, "expected_blob_id": blob_id,
                    "document": doc,
                    "verification_basis": "registry-only",
                    "registered_in_this_vault": True,
                    "registry_note": REGISTRY_NOTE,
                    "explanation": "This blob id is a sealed record in this server instance's register.",
                    "receipt": receipt}
        receipt = self._record(
            "verify", blob_id, "NOT FOUND (by hash): no sealed record in this instance.")
        return {"ok": False, "verdict": "NOT FOUND", "backend": BACKEND_LABEL,
                "computed_hash": blob_id, "expected_blob_id": blob_id,
                "document": None,
                "verification_basis": "registry-only",
                "registered_in_this_vault": False,
                "registry_note": REGISTRY_NOTE,
                "explanation": (
                    "No sealed document with this blob id is in this server "
                    "instance's register. On serverless the register is "
                    "per-instance and ephemeral, so this does NOT prove the "
                    "document was never sealed — paste the document itself "
                    "(file or text) together with this blob id to verify by "
                    "its content hash, which works on any instance."),
                "receipt": receipt}

    def tamper_demo(self, blob_id: str, data: bytes | None = None) -> dict:
        """Take a sealed doc, flip one character, prove TAMPERED.

        The flip is real: byte 0 of the bytes is XORed, so the recomputed
        hash genuinely differs, and the check runs through the stateless
        verify() path (expected_blob_id=blob_id) — no server register
        needed. ``data`` lets the caller supply the document bytes (e.g.
        the just-sealed content); without it the bytes are read from this
        instance's store, which always holds the 3 seeded SAMPLE docs.
        """
        if data is None:
            data = self.read_blob(blob_id)
        if data is None:
            raise VaultError(
                "No sealed document with that blob id in this server instance. "
                "Paste the document text (or pick a SAMPLE document, which is "
                "seeded in every instance) and try again.")
        tampered = bytearray(data)
        tampered[0] ^= 0x01
        result = self.verify(bytes(tampered), expected_blob_id=blob_id)
        return {"original_blob_id": blob_id,
                "tampered_hash": result["computed_hash"],
                "verdict": result["verdict"],
                "verification_basis": result["verification_basis"],
                "registered_in_this_vault": result["registered_in_this_vault"],
                "registry_note": result["registry_note"],
                "explanation": result["explanation"],
                "document": result["document"],
                "receipt": result["receipt"],
                "backend": BACKEND_LABEL}

    # -- register ------------------------------------------------------
    def get_doc(self, blob_id: str) -> dict | None:
        return self.documents.get((blob_id or "").strip().lower())

    def list_docs(self) -> list[dict]:
        return [self.documents[k] for k in sorted(
            self.documents, key=lambda b: self.documents[b]["timestamp_utc"])]

    def seed_samples(self) -> list[dict]:
        sealed = []
        for sample in SAMPLE_DOCS:
            result = self.seal(sample["text"].encode("utf-8"),
                               title=sample["title"], doc_type=sample["doc_type"],
                               issuer=sample["issuer"])
            sealed.append(result["document"])
        return sealed
