"""NyayaLedger for Walrus — single-page server (Python 3 stdlib only).

Run from the project root::

    python3 -m app.server          # http://127.0.0.1:8902  [local-vault]

Routes:
  GET  /                     index.html
  GET  /static/<file>        style.css / app.js / index.html
  GET  /api/status           backend + Walrus blocker note
  GET  /api/docs             sealed register
  GET  /api/doc?id=<blob>    one document
  GET  /api/audit            audit receipts
  GET  /api/audit/verify     re-verify the hash chain
  POST /api/seal             multipart file OR JSON {text,title,doc_type,issuer}
  POST /api/verify           multipart file (+optional expected_blob_id)
                             OR JSON {hash} / {text} / {expected_blob_id}
  POST /api/tamper-demo      JSON {blob_id}

Every JSON response carries ``backend: "local-vault"``. No secrets,
no env vars, no external assets.
"""

from __future__ import annotations

import json
import mimetypes
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from app.vault import BACKEND_LABEL, DOC_TYPES, MAX_BYTES, Vault, VaultError
from app.walrus_adapter import TESTNET_BLOCKER, LocalVaultAdapter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
PORT = 8902
HOST = "127.0.0.1"

vault = Vault(DATA_DIR)
adapter = LocalVaultAdapter(vault)  # the real backend; WalrusTestnetAdapter is a stub


# ---------------------------------------------------------------- multipart
def parse_multipart(body: bytes, boundary: bytes) -> dict[str, tuple[str | None, bytes]]:
    """Minimal multipart/form-data parser. Returns {name: (filename, bytes)}.

    Stdlib-only (``cgi`` is deprecated); good enough for one file field
    plus small text fields. Raises VaultError on malformed input.
    """
    parts: dict[str, tuple[str | None, bytes]] = {}
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


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    # -- helpers ------------------------------------------------------
    def _json(self, payload: dict, status: int = 200) -> None:
        payload.setdefault("backend", BACKEND_LABEL)
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self, limit: int = MAX_BYTES + 1024 * 1024) -> bytes:
        length = int(self.headers.get("Content-Length") or 0)
        if length > limit:
            raise VaultError(
                f"Upload is {length:,} bytes — the limit is {MAX_BYTES:,} bytes (2 MB).")
        if length <= 0:
            return b""
        return self.rfile.read(length)

    def _read_json(self) -> dict:
        try:
            return json.loads(self._read_body().decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return {}

    def _static(self, name: str) -> None:
        safe = os.path.basename(name)
        path = os.path.join(STATIC_DIR, safe)
        if not os.path.exists(path):
            self._json({"ok": False, "error": "Not found."}, 404)
            return
        with open(path, "rb") as f:
            body = f.read()
        ctype, _ = mimetypes.guess_type(path)
        self.send_response(200)
        self.send_header("Content-Type", ctype or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # -- GET ----------------------------------------------------------
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path, query = parsed.path, urllib.parse.parse_qs(parsed.query)
        try:
            if path == "/":
                self._static("index.html")
                return
            if path.startswith("/static/"):
                self._static(path[len("/static/"):])
                return
            if path == "/api/status":
                self._json({"ok": True, "backend": BACKEND_LABEL,
                            "adapter": adapter.status(),
                            "walrus_testnet": "not connected",
                            "walrus_blocker": TESTNET_BLOCKER,
                            "verification": {
                                "primary": "stateless content-hash: SHA-256 of the supplied document compared with the claimed blob id — needs no server storage, works on any instance",
                                "registry": "per-instance/ephemeral on serverless; secondary signal only"},
                            "documents": len(vault.list_docs()),
                            "max_bytes": MAX_BYTES,
                            "doc_types": list(DOC_TYPES)})
                return
            if path == "/api/docs":
                self._json({"ok": True, "documents": vault.list_docs()})
                return
            if path == "/api/doc":
                doc = vault.get_doc((query.get("id") or [""])[0])
                if doc is None:
                    self._json({"ok": False, "error": "No sealed document with that blob id."}, 404)
                    return
                self._json({"ok": True, "document": doc})
                return
            if path == "/api/audit":
                self._json({"ok": True, "entries": vault.audit_log()})
                return
            if path == "/api/audit/verify":
                result = vault.verify_chain()
                self._json({"ok": result["ok"], **result},
                           200 if result["ok"] else 409)
                return
        except VaultError as exc:
            self._json({"ok": False, "error": str(exc)}, 400)
            return
        self._json({"ok": False, "error": "Not found."}, 404)

    # -- POST ---------------------------------------------------------
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        try:
            if parsed.path == "/api/seal":
                ctype = self.headers.get("Content-Type") or ""
                if ctype.startswith("multipart/form-data"):
                    boundary = ctype.split("boundary=")[-1].encode()
                    parts = parse_multipart(self._read_body(), boundary)
                    file_item = parts.get("file")
                    title = field_text(parts, "title")
                    doc_type = field_text(parts, "doc_type", "Other")
                    issuer = field_text(parts, "issuer")
                    if file_item and file_item[0]:
                        result = vault.seal(file_item[1], title=title,
                                            doc_type=doc_type, issuer=issuer)
                    else:
                        text = field_text(parts, "text")
                        result = vault.seal_text(text, title=title,
                                                 doc_type=doc_type, issuer=issuer)
                else:
                    payload = self._read_json()
                    if "text" in payload:
                        result = vault.seal_text(
                            payload.get("text", ""), title=payload.get("title", ""),
                            doc_type=payload.get("doc_type", "Other"),
                            issuer=payload.get("issuer", ""))
                    else:
                        raise VaultError("Seal needs a file upload or pasted text.")
                self._json({"ok": True, **result})
                return
            if parsed.path == "/api/verify":
                ctype = self.headers.get("Content-Type") or ""
                if ctype.startswith("multipart/form-data"):
                    boundary = ctype.split("boundary=")[-1].encode()
                    parts = parse_multipart(self._read_body(), boundary)
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
                            raise VaultError(
                                "Verify needs a file upload or a pasted hash.")
                else:
                    payload = self._read_json()
                    if payload.get("hash"):
                        result = vault.verify_hash(payload["hash"])
                    elif payload.get("text"):
                        result = vault.verify(
                            payload["text"].encode("utf-8"),
                            expected_blob_id=payload.get("expected_blob_id"))
                    else:
                        raise VaultError(
                            "Verify needs a file, pasted text, or a blob id.")
                self._json({"ok": True, **result})
                return
            if parsed.path == "/api/tamper-demo":
                payload = self._read_json()
                text = payload.get("text", "")
                data = text.encode("utf-8") if (text or "").strip() else None
                result = vault.tamper_demo(payload.get("blob_id", ""), data=data)
                self._json({"ok": True, **result})
                return
        except VaultError as exc:
            self._json({"ok": False, "error": str(exc)}, 400)
            return
        self._json({"ok": False, "error": "Not found."}, 404)


def main(host: str = HOST, port: int = PORT) -> None:
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"NyayaLedger for Walrus listening on http://{host}:{port} [{BACKEND_LABEL}]")
    print(f"Sealed documents: {len(vault.list_docs())} "
          f"(samples seeded on first run); audit receipts: {len(vault.audit_log())}")
    print("Walrus testnet: NOT connected — " + TESTNET_BLOCKER[:120] + "…")
    server.serve_forever()


if __name__ == "__main__":
    main()
