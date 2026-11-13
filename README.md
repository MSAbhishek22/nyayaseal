# NyayaLedger for Walrus — "NyayaSeal"

**GenHacks entry (Devpost, submitted 12 Nov 2026) · solo · online**
Live: **https://nyayaseal.vercel.app** · Repo: https://github.com/MSAbhishek22/nyayaseal ·
Demo video: https://www.youtube.com/watch?v=p7f7yZwR_QI

(Originally built towards the Walrus Haulout "Truth Engine + Trust Oracle" theme — that
event turned out to be the ended 2025 edition, so the Walrus testnet store was never
connected; see "What is stubbed / BLOCKED". The sealing engine is storage-agnostic.)

A legal document you can prove is real — sealed by its own content hash, verified in one click.
The hash of a document *is* its address: change one character and the address changes, so a
tampered copy can never pass as the original.

> General legal information, not legal advice. Sample documents are clearly labelled SAMPLE.
> Verification proves the bytes are unchanged — not that the content is legally true.

## Run it

```bash
cd ~/workspace/hackathons/walrus-haulout
python3 -m app.server        # http://127.0.0.1:8902  [local-vault]
```

Python 3 stdlib only — no pip installs, no CDN, no external assets, no env vars, no secrets.
First run seeds 3 sample documents (Freelance Services Agreement, Affidavit, Legal Notice).

## Deploy (Vercel, free tier, no card)

`api/index.py` is a WSGI adapter for Vercel serverless (same routes as
`app/server.py`; vault rooted at `NYAYASEAL_DATA_DIR`, default
`/tmp/nyayaseal-data`). `vercel.json` rewrites `/(.*)` → `/api/index`.
Verified locally with a WSGI harness — 14/14 PASS
(`/tmp/nyayaseal-wsgi-test.py`: home, static, status, seal, verify
AUTHENTIC, tamper-demo TAMPERED, unknown NOT FOUND, audit chain,
multipart, error paths). Full steps + serverless honesty note (vault is
per-instance ephemeral on Vercel) in `deployment/DEPLOYMENT_RUNBOOK.md`.
Live URL: **https://nyayaseal.vercel.app** — deployed on Vercel and verified
13 Nov 2026 (home 200, `GET /api/status` ok, backend `local-vault`).

## Tests

```bash
python3 -m unittest discover -s tests -v
# 24 tests, all passing (re-verified 13 Nov 2026)
```

Covers: SHA-256 known vector (`abc`), seal → verify round-trip AUTHENTIC, tampered bytes →
TAMPERED, unknown hash → NOT FOUND, audit chain verify OK + forged-entry detection, 2 MB
file-size limit, empty input refused, content-addressed blob round-trip, adapter behaviour.

## What is real

| Piece | Status |
|---|---|
| SHA-256 sealing of exact bytes | Real — `app/vault.py`, NIST vector tested |
| Content-addressed blob store | Real — bytes stored at `data/blobs/<sha256>`; the hash *is* the address |
| Verify (file / pasted text / pasted hash) | Real — re-hash + compare; AUTHENTIC / TAMPERED / NOT FOUND with plain explanations |
| Tamper demo | Real — flips one byte of a sealed sample and shows the genuine TAMPERED verdict |
| Register + document detail | Real — `data/register.json`, click a row for the full record |
| Hash-chained audit log | Real — every seal/verify writes a receipt; `verify_chain` recomputes it (same pattern as Day-1 NyayaLedger `ledger.py`) |
| UI (seal / verify / vault / audit / how-it-works) | Real — every visible control works; no dead buttons, no fake toasts |
| 3D vault stack | Real CSS 3D — one card per sealed document, rotate with buttons + drag; 2D grid fallback; static in low-motion mode |
| Low-motion toggle + `prefers-reduced-motion` | Real |
| Copy-hash buttons, receipt download (`.json`), `?blob=<id>` deep link | Real |

## What is stubbed / BLOCKED

**Walrus testnet — NOT connected.** `app/walrus_adapter.py` has the clean seam:

- `LocalVaultAdapter` — the real backend today (local content-addressed store).
- `WalrusTestnetAdapter` — stub; `store_blob` / `read_blob` raise
  `NotImplementedError("testnet not connected — needs a funded wallet / publisher endpoint; not attempted")`.
  No Walrus blob id is ever faked. Every receipt and API response carries `backend: "local-vault"`,
  and the UI badge reads `[local-vault] — Walrus testnet not connected: <reason>`.

Probed from this sandbox, 10 Nov 2026 (~5 min, read-only, no secrets, no account creation):

- Aggregator (read) **is reachable**: `https://aggregator.walrus-testnet.walrus.space/v1/blobs/<id>`
  returns a structured Walrus `BLOB_NOT_FOUND` (HTTP 404) for an unknown blob — the testnet is live.
- Publisher (write) `https://publisher.walrus-testnet.walrus.space/` is reachable but returns 404
  on read paths, and **storing a blob requires a SUI payment via a funded wallet / publisher
  endpoint**. This sandbox has no wallet, no SUI, and the rulebook forbids account creation,
  spending and credential sharing — so the store path was **not attempted**.
- No free, no-wallet, no-card, no-account testnet store path was found. When a funded testnet
  wallet + publisher URL exist, implement `WalrusTestnetAdapter.store_blob` (PUT bytes to the
  publisher, return the real Walrus blob id) and flip over only after a live round-trip test.
  The swap changes where bytes live, not how authenticity works — the hash is the address
  in both backends.

Also **not** claimed: Daml / Canton integration (Day-1 NyayaLedger lineage only — the ledger
pattern and grounded-citation idea were reused, the code is fresh). Deployment, public repo,
demo video and the GenHacks submission all exist (links at the top) — the one thing that does
**not** exist is a Walrus testnet connection.

## Architecture

```
app/
  vault.py            core: sha256, blob store, seal/verify, register, audit chain, samples
  walrus_adapter.py   adapter seam: LocalVaultAdapter (real) + WalrusTestnetAdapter (stub)
  server.py           stdlib http.server, port 8902; serves page + JSON API + multipart upload
  static/
    index.html        single page (hero, seal, verify, vault, audit, how-it-works)
    style.css         Neo-Brutalism per design/DESIGN_CONSTITUTION.md; restyle via :root vars
    app.js            fetch API, drop zones, 3D vault rotation, copy/receipt/?blob=
tests/
  test_vault.py       24 stdlib-unittest tests (no pytest in this sandbox)
data/                 created at runtime (gitignored): blobs/<sha256>, register.json, audit.jsonl
design/               DESIGN_CONSTITUTION.md + PROJECT_DESIGN_REGISTRY.md (design researcher)
```

API (all JSON carries `backend: "local-vault"`):

- `GET /api/status` — backend + Walrus blocker note
- `GET /api/docs` · `GET /api/doc?id=<blob_id>` — register / one document
- `GET /api/audit` · `GET /api/audit/verify` — receipts / chain re-verification
- `POST /api/seal` — multipart file **or** JSON `{text, title, doc_type, issuer}` (≤ 2 MB)
- `POST /api/verify` — multipart file (+ optional `expected_blob_id`) **or** JSON `{hash}` / `{text}`
- `POST /api/tamper-demo` — JSON `{blob_id}`

## Design notes (where the build differs from the constitution)

`design/DESIGN_CONSTITUTION.md` is the binding design spec and the stylesheet implements it
(Neo-Brutalism: cream `#FFF3D6`, ink borders, hard offset shadows, teal/vermilion/gold/blue
tokens, stamp verdicts, Archivo Black fallbacks). Two deliberate divergences, both from the
build brief, which wins on implementation:

1. **Hashing is server-side**, not client-side `crypto.subtle` (§2/§8 of the constitution).
   The server computes SHA-256 of the exact uploaded bytes, so the seal is verifiable
   end-to-end without trusting the browser; the hash is still shown in full with COPY controls.
2. **No Three.js** (§9). The brief forbids it; the CSS-3D isometric stack is the constitution's
   own specified fallback tier, and it carries the same information (one slab per sealed doc).

## Limits (honest)

- 2 MB per file; pasted text ≤ 200,000 chars; titles ≤ 200 chars.
- Local vault only — documents live on this machine's disk, not on Walrus (see stub above).
- No auth / multi-user: anyone with access to the server can seal and verify.
- A hash match proves the bytes are unchanged, not that the content is legally true.
