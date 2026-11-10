"""NyayaSeal on Vercel — WSGI entrypoint (serverless adaptation).

The vault logic is unchanged (app/vault.py: same SHA-256 seal, same
content-addressed store, same audit chain, same receipts); this file is
only a transport adapter. Vercel's Python runtime calls
``app(environ, start_response)``.

Deliberately does NOT import app.server: that module instantiates a
Vault rooted at the project ``data/`` directory at import time, and the
deployed filesystem is read-only except /tmp. This adapter builds its
own Vault rooted at ``NYAYASEAL_DATA_DIR`` (default
``/tmp/nyayaseal-data``) and re-implements the same routes against it.
The multipart parser is copied from app/server.py (same behaviour).

Serverless honesty notes (also in deployment/DEPLOYMENT_RUNBOOK.md):
- The vault lives in /tmp on Vercel: each serverless instance has its
  own /tmp, so seals and the register are per-instance and ephemeral —
  a cold instance starts with only the 3 seeded SAMPLE documents.
  VERIFICATION DOES NOT DEPEND ON THAT: verify() is stateless (SHA-256
  of the supplied document compared with the claimed blob id), so
  seal-on-one-instance + verify-on-another returns AUTHENTIC. Only a
  blob-id-alone lookup consults the per-instance register, and its
  NOT FOUND is labelled registry-only, never proof the doc was never
  sealed. (Earlier wording claimed seal-then-verify "normally hits the
  same warm instance" — that was WRONG live on 10 Nov 2026; fixed by
  the stateless path, not by assuming instance stickiness.)
- No credentials are needed. Backend is "local-vault" everywhere;
  Walrus testnet is still not connected (see app/walrus_adapter.py).
"""

import json
import mimetypes
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.vault import BACKEND_LABEL, DOC_TYPES, MAX_BYTES, Vault, VaultError  # noqa: E402
from app.walrus_adapter import TESTNET_BLOCKER, LocalVaultAdapter  # noqa: E402

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")
DATA_DIR = os.environ.get("NYAYASEAL_DATA_DIR", "/tmp/nyayaseal-data")

vault = Vault(DATA_DIR)
adapter = LocalVaultAdapter(vault)


# ---------------------------------------------------------------- multipart
# Copied from app/server.py (same minimal parser) so this module does not
# import app.server, which would instantiate a Vault on the read-only
# project data directory at import time.
def parse_multipart(body: bytes, boundary: bytes) -> dict:
    """Minimal multipart/form-data parser. Returns {name: (filename, bytes)}."""
    parts: dict = {}
    if not boundary:
        raise VaultError("Malformed upload (no boundary).")
    for chunk in body.split(b"--" + boundary):
        chunk = chunk.strip(b"\r\n")
        if not chunk or chunk == b"--":
            continue
        head, sep, payload = chunk.partition(b"\r\n\r\n")
        if not sep:
            continue
        headers = head.decode("utf-8", "replace")
        name = filename = None
        for line in headers.split("\r\n"):
            if line.lower().startswith("content-disposition:"):
                for seg in line.split(";"):
                    seg = seg.strip()
                    if seg.startswith("name="):
                        name = seg[5:].strip('"')
                    elif seg.startswith("filename="):
                        filename = seg[9:].strip('"')
        if name:
            parts[name] = (filename, payload)
    return parts


def field_text(parts: dict, name: str, default: str = "") -> str:
    item = parts.get(name)
    if item is None:
        return default
    return item[1].decode("utf-8", "replace")


# ---------------------------------------------------------------- routing
def _json_body(payload: dict) -> bytes:
    payload.setdefault("backend", BACKEND_LABEL)
    return json.dumps(payload).encode()


def _static(name: str):
    safe = os.path.basename(name)
    path = os.path.join(STATIC_DIR, safe)
    if not os.path.exists(path):
        return 404, "application/json", _json_body(
            {"ok": False, "error": "Not found."})
    with open(path, "rb") as f:
        body = f.read()
    ctype, _ = mimetypes.guess_type(path)
    return 200, ctype or "application/octet-stream", body


def handle_get(path: str, query: dict):
    if path == "/":
        return _static("index.html")
    if path.startswith("/static/"):
        return _static(path[len("/static/"):])
    if path == "/api/status":
        return 200, "application/json", _json_body({
            "ok": True, "backend": BACKEND_LABEL, "adapter": adapter.status(),
            "walrus_testnet": "not connected", "walrus_blocker": TESTNET_BLOCKER,
            "verification": {
                "primary": "stateless content-hash: SHA-256 of the supplied document compared with the claimed blob id — needs no server storage, works on any instance",
                "registry": "per-instance/ephemeral on serverless; secondary signal only"},
            "documents": len(vault.list_docs()), "max_bytes": MAX_BYTES,
            "doc_types": list(DOC_TYPES)})
    if path == "/api/docs":
        return 200, "application/json", _json_body(
            {"ok": True, "documents": vault.list_docs()})
    if path == "/api/doc":
        doc = vault.get_doc((query.get("id") or [""])[0])
        if doc is None:
            return 404, "application/json", _json_body(
                {"ok": False, "error": "No sealed document with that blob id."})
        return 200, "application/json", _json_body({"ok": True, "document": doc})
    if path == "/api/audit":
        return 200, "application/json", _json_body(
            {"ok": True, "entries": vault.audit_log()})
    if path == "/api/audit/verify":
        result = vault.verify_chain()
        return (200 if result["ok"] else 409), "application/json", _json_body(
            {"ok": result["ok"], **result})
    return 404, "application/json", _json_body({"ok": False, "error": "Not found."})


def handle_post(path: str, ctype: str, raw: bytes):
    if path == "/api/seal":
        if ctype.startswith("multipart/form-data"):
            boundary = ctype.split("boundary=")[-1].encode()
            parts = parse_multipart(raw, boundary)
            file_item = parts.get("file")
            title = field_text(parts, "title")
            doc_type = field_text(parts, "doc_type", "Other")
            issuer = field_text(parts, "issuer")
            if file_item and file_item[0]:
                result = vault.seal(file_item[1], title=title,
                                    doc_type=doc_type, issuer=issuer)
            else:
                result = vault.seal_text(field_text(parts, "text"), title=title,
                                         doc_type=doc_type, issuer=issuer)
        else:
            payload = json.loads(raw.decode("utf-8") or "{}")
            if "text" in payload:
                result = vault.seal_text(
                    payload.get("text", ""), title=payload.get("title", ""),
                    doc_type=payload.get("doc_type", "Other"),
                    issuer=payload.get("issuer", ""))
            else:
                raise VaultError("Seal needs a file upload or pasted text.")
        return 200, "application/json", _json_body({"ok": True, **result})
    if path == "/api/verify":
        if ctype.startswith("multipart/form-data"):
            boundary = ctype.split("boundary=")[-1].encode()
            parts = parse_multipart(raw, boundary)
            file_item = parts.get("file")
            expected = field_text(parts, "expected_blob_id") or None
            if file_item and file_item[0]:
                result = vault.verify(file_item[1], expected_blob_id=expected)
            else:
                text = field_text(parts, "text")
                if text.strip():
                    result = vault.verify(text.encode("utf-8"),
                                          expected_blob_id=expected)
                else:
                    raise VaultError("Verify needs a file upload or a pasted hash.")
        else:
            payload = json.loads(raw.decode("utf-8") or "{}")
            if payload.get("hash"):
                result = vault.verify_hash(payload["hash"])
            elif payload.get("text"):
                result = vault.verify(
                    payload["text"].encode("utf-8"),
                    expected_blob_id=payload.get("expected_blob_id"))
            else:
                raise VaultError("Verify needs a file, pasted text, or a blob id.")
        return 200, "application/json", _json_body({"ok": True, **result})
    if path == "/api/tamper-demo":
        payload = json.loads(raw.decode("utf-8") or "{}")
        text = payload.get("text", "")
        data = text.encode("utf-8") if (text or "").strip() else None
        result = vault.tamper_demo(payload.get("blob_id", ""), data=data)
        return 200, "application/json", _json_body({"ok": True, **result})
    return 404, "application/json", _json_body({"ok": False, "error": "Not found."})


_STATUSES = {
    200: "200 OK", 400: "400 Bad Request", 404: "404 Not Found",
    409: "409 Conflict", 500: "500 Internal Server Error",
}


def app(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET").upper()
    raw_path = environ.get("PATH_INFO", "/") or "/"
    # Vercel rewrites /(.*) to /api/index: treat the function root as app root.
    path = "/" if raw_path in ("/api/index", "/api") else raw_path
    query = urllib.parse.parse_qs(environ.get("QUERY_STRING", ""))
    try:
        if method == "GET":
            code, ctype, body = handle_get(path, query)
        elif method == "POST":
            try:
                length = int(environ.get("CONTENT_LENGTH") or 0)
            except ValueError:
                length = 0
            if length > MAX_BYTES + 1024 * 1024:
                raise VaultError(
                    f"Upload is {length:,} bytes — the limit is {MAX_BYTES:,} "
                    "bytes (2 MB).")
            raw = environ["wsgi.input"].read(length) if length else b""
            code, ctype, body = handle_post(
                path, environ.get("CONTENT_TYPE") or "", raw)
        else:
            code, ctype, body = 404, "application/json", _json_body(
                {"ok": False, "error": "Not found."})
    except VaultError as exc:
        code, ctype, body = 400, "application/json", _json_body(
            {"ok": False, "error": str(exc)})
    except Exception as exc:  # never leak a stack trace to the client
        code, ctype, body = 500, "application/json", _json_body(
            {"ok": False, "error": f"Server error: {type(exc).__name__}"})
    start_response(_STATUSES.get(code, "200 OK"),
                   [("Content-Type", ctype),
                    ("Content-Length", str(len(body)))])
    return [body]
