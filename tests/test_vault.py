"""Tests for NyayaLedger for Walrus — stdlib unittest (no pytest here).

Run from the project root::

    python3 -m unittest discover -s tests -v

Every test uses a fresh temp dir, so the real data/ vault is untouched.
"""
import hashlib
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.vault import MAX_BYTES, Vault, VaultError, sha256_hex  # noqa: E402
from app.walrus_adapter import LocalVaultAdapter, WalrusTestnetAdapter  # noqa: E402


class VaultTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = Vault(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    # -- hashing ------------------------------------------------------
    def test_sha256_known_vector(self):
        # NIST vector: sha256("abc")
        self.assertEqual(
            sha256_hex(b"abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
        self.assertEqual(sha256_hex(b"abc"), hashlib.sha256(b"abc").hexdigest())

    def test_hash_is_address_content_addressed(self):
        blob_id = self.vault.store_blob(b"same bytes")
        self.assertEqual(blob_id, sha256_hex(b"same bytes"))
        self.assertEqual(self.vault.read_blob(blob_id), b"same bytes")
        # storing identical bytes twice yields the same id, one file
        self.assertEqual(self.vault.store_blob(b"same bytes"), blob_id)
        self.assertEqual(self.vault.store_blob(b"different"), sha256_hex(b"different"))

    # -- seal / verify ------------------------------------------------
    def test_seal_verify_round_trip_authentic(self):
        data = b"Freelance Services Agreement -- Acme / Abhishek, INR 50,000."
        sealed = self.vault.seal(data, title="Test Agreement",
                                 doc_type="Contract", issuer="Acme Pvt Ltd")
        doc = sealed["document"]
        self.assertEqual(doc["status"], "SEALED")
        self.assertEqual(doc["blob_id"], sha256_hex(data))
        self.assertEqual(sealed["receipt"]["backend"], "local-vault")
        result = self.vault.verify(data)
        self.assertEqual(result["verdict"], "AUTHENTIC")
        self.assertEqual(result["document"]["title"], "Test Agreement")
        self.assertEqual(result["backend"], "local-vault")

    def test_verify_with_expected_id_authentic(self):
        data = b"affidavit text"
        sealed = self.vault.seal(data, title="Aff", doc_type="Affidavit", issuer="X")
        result = self.vault.verify(data, expected_blob_id=sealed["document"]["blob_id"])
        self.assertEqual(result["verdict"], "AUTHENTIC")

    def test_malformed_expected_id_refused_not_tampered(self):
        # QA I-4: a typo in the expected blob id must be a plain error,
        # never a TAMPERED verdict.
        data = b"affidavit text"
        self.vault.seal(data, title="Aff", doc_type="Affidavit", issuer="X")
        with self.assertRaises(VaultError):
            self.vault.verify(data, expected_blob_id="not-a-hash")

    def test_tampered_bytes_tampered(self):
        data = bytearray(b"Settlement Deed: party A pays party B INR 10,000.")
        sealed = self.vault.seal(bytes(data), title="Deed",
                                 doc_type="Settlement Deed", issuer="A")
        tampered = bytearray(data)
        tampered[10] ^= 0x01  # flip one bit, deep inside the text
        result = self.vault.verify(bytes(tampered),
                                  expected_blob_id=sealed["document"]["blob_id"])
        self.assertEqual(result["verdict"], "TAMPERED")
        self.assertNotEqual(result["computed_hash"], sealed["document"]["blob_id"])

    def test_tamper_demo_proves_tampered(self):
        sealed = self.vault.seal(b"Legal Notice: pay within 15 days.",
                                 title="Notice", doc_type="Legal Notice", issuer="X")
        demo = self.vault.tamper_demo(sealed["document"]["blob_id"])
        self.assertEqual(demo["verdict"], "TAMPERED")
        self.assertNotEqual(demo["tampered_hash"], sealed["document"]["blob_id"])

    def test_unknown_hash_not_found(self):
        result = self.vault.verify(b"never sealed anywhere")
        self.assertEqual(result["verdict"], "NOT FOUND")
        self.assertIsNone(result["document"])
        result2 = self.vault.verify_hash("0" * 64)
        self.assertEqual(result2["verdict"], "NOT FOUND")

    def test_verify_hash_known_id_authentic(self):
        sealed = self.vault.seal(b"power of attorney text", title="PoA",
                                 doc_type="Power of Attorney", issuer="X")
        result = self.vault.verify_hash(sealed["document"]["blob_id"])
        self.assertEqual(result["verdict"], "AUTHENTIC")

    # -- limits / refusals --------------------------------------------
    def test_file_size_limit(self):
        with self.assertRaises(VaultError):
            self.vault.seal(b"x" * (MAX_BYTES + 1), title="Too big",
                            doc_type="Other", issuer="X")
        with self.assertRaises(VaultError):
            self.vault.verify(b"x" * (MAX_BYTES + 1))

    def test_empty_input_refused(self):
        with self.assertRaises(VaultError):
            self.vault.seal(b"", title="Empty", doc_type="Other", issuer="X")
        with self.assertRaises(VaultError):
            self.vault.seal_text("   ", title="Empty", doc_type="Other", issuer="X")
        with self.assertRaises(VaultError):
            self.vault.verify(b"")
        with self.assertRaises(VaultError):
            self.vault.seal(b"some bytes", title="  ", doc_type="Other", issuer="X")
        with self.assertRaises(VaultError):
            self.vault.seal(b"some bytes", title="T", doc_type="NotAType", issuer="X")
        with self.assertRaises(VaultError):
            self.vault.verify_hash("not-a-hash")

    def test_blob_on_disk_matches_hash(self):
        sealed = self.vault.seal(b"disk check", title="Disk", doc_type="Other", issuer="X")
        path = os.path.join(self.tmp.name, "blobs", sealed["document"]["blob_id"])
        self.assertTrue(os.path.exists(path))
        with open(path, "rb") as f:
            self.assertEqual(f.read(), b"disk check")

    # -- audit chain ---------------------------------------------------
    def test_audit_chain_verify_ok(self):
        self.vault.seal(b"doc one", title="One", doc_type="Other", issuer="X")
        self.vault.verify(b"doc one")
        self.vault.verify(b"unknown doc")
        result = self.vault.verify_chain()
        self.assertTrue(result["ok"])
        self.assertGreaterEqual(result["checked"], 3)

    def test_audit_chain_tampered_detected(self):
        self.vault.seal(b"doc one", title="One", doc_type="Other", issuer="X")
        self.vault.seal(b"doc two", title="Two", doc_type="Other", issuer="X")
        audit_path = os.path.join(self.tmp.name, "audit.jsonl")
        with open(audit_path, encoding="utf-8") as f:
            lines = f.readlines()
        entry = json.loads(lines[0])
        entry["detail"] = "FORGED ENTRY"
        lines[0] = json.dumps(entry, sort_keys=True) + "\n"
        with open(audit_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        result = self.vault.verify_chain()
        self.assertFalse(result["ok"])
        self.assertEqual(result["bad_at"], 1)

    # -- samples -------------------------------------------------------
    def test_samples_seeded_on_first_run(self):
        docs = self.vault.list_docs()
        self.assertEqual(len(docs), 3)
        types = {d["doc_type"] for d in docs}
        self.assertEqual(types, {"Contract", "Affidavit", "Legal Notice"})
        for d in docs:
            self.assertTrue(d["title"].startswith("SAMPLE"))
            self.assertEqual(d["status"], "SEALED")
            self.assertEqual(self.vault.read_blob(d["blob_id"]) is not None, True)

    # -- adapter -------------------------------------------------------
    def test_local_adapter_round_trip(self):
        adapter = LocalVaultAdapter(self.vault)
        blob_id = adapter.store_blob(b"adapter bytes")
        self.assertEqual(adapter.read_blob(blob_id), b"adapter bytes")
        status = adapter.status()
        self.assertEqual(status["backend"], "local-vault")
        self.assertTrue(status["connected"])

    def test_walrus_testnet_adapter_is_stub(self):
        adapter = WalrusTestnetAdapter()
        self.assertFalse(adapter.status()["connected"])
        with self.assertRaises(NotImplementedError):
            adapter.store_blob(b"nope")
        with self.assertRaises(NotImplementedError):
            adapter.read_blob("0" * 64)


if __name__ == "__main__":
    unittest.main()
