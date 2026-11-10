# DEPLOYMENT RUNBOOK — NyayaSeal (Walrus Haulout Hackathon)

**Project:** NyayaSeal — provably authentic legal documents (Truth Engine +
Trust Oracle track) · **Repo (to create):** https://github.com/MSAbhishek22/nyayaseal
· **Target host:** Vercel Hobby (free, no card) · **Status: NOT YET DEPLOYED**
— Vercel adaptation (`api/index.py`) is written and verified locally
(14/14 WSGI harness checks, 17/17 unit tests); the live deploy itself needs
the user's signed-in Vercel browser session (see §2).

## 1. What is deployed

- **Stack:** Python 3.12 stdlib only — no pip installs, no external assets,
  no env vars required, no secrets anywhere in the repo.
- **Local entry:** `python3 -m app.server` → http://127.0.0.1:8902
- **Vercel entry:** `api/index.py` exposes WSGI `app(environ, start_response)`;
  `vercel.json` rewrites `/(.*)` → `/api/index` (same pattern as CageCheck's
  `cagecheck.vercel.app`). `.python-version` pins `3.12`.
- **Why a separate adapter:** `app/server.py` instantiates a Vault rooted at
  the project `data/` directory at import time; the deployed filesystem is
  read-only except `/tmp`. `api/index.py` therefore builds its own Vault
  rooted at `NYAYASEAL_DATA_DIR` (default `/tmp/nyayaseal-data`) and
  re-implements the identical routes against it. Vault logic is unchanged.
- **Routes (identical locally and on Vercel):** `GET /`, `GET /static/*`,
  `GET /api/status`, `GET /api/docs`, `GET /api/doc?id=`, `GET /api/audit`,
  `GET /api/audit/verify`, `POST /api/seal`, `POST /api/verify`,
  `POST /api/tamper-demo`.

## 2. Deploy steps (Vercel dashboard, signed-in browser session)

1. Create the GitHub repo first (see §6): public `MSAbhishek22/nyayaseal`,
   **empty — no README / .gitignore / licence initialisation** (the snapshot
   push supplies `README.md` itself; a provider-generated README would be an
   extra commit to reconcile).
2. Push the snapshot with the GitHub connector (`github push-files`,
   manifest `~/workspace/hackathons/nyayaseal-paths`, branch `main`).
   Record the confirmed head SHA and verify it with `list_commits`.
3. In Vercel (already signed in as the user, Hobby/free plan, no card):
   **Add New → Project → Import** `MSAbhishek22/nyayaseal`.
   Framework preset: **Other**. Root directory: repo root. No build command.
   No environment variables are required; optionally set
   `NYAYASEAL_DATA_DIR=/tmp/nyayaseal-data` (that is already the default).
4. **Deploy.** Expected production URL: `https://nyayaseal.vercel.app`
   (confirm the actual assigned URL from the deployment page — do not assume
   the slug is free until Vercel confirms it).
5. Verify from a fresh browser session (see §3). Only after §3 passes is the
   deploy LIVE. Record the URL, build/deployment ID, deployed commit SHA and
   timestamps in `deployment/RELEASE_MANIFEST.json`.

## 3. Production verification (must be done on the real HTTPS URL)

Open the live URL in a fresh session and confirm, in order:

1. Home page loads (200), hero shows "NyayaSeal", backend badge reads
   `local-vault`, 3 SAMPLE documents listed.
2. `GET /api/status` → 200, `"backend": "local-vault"`, `documents: 3`.
3. Seal flow: paste text → seal → blob id returned (64-char hex).
4. Verify flow: same text → **AUTHENTIC**; tamper demo on the sealed doc →
   **TAMPERED**; unknown hash (`000…0`) → **NOT FOUND**.
5. `GET /api/audit/verify` → `{"ok": true}`.
6. No console errors; layout clean at desktop + mobile widths.

## 4. Environment variables (names only — no values)

| Name | Required? | Value / note |
|---|---|---|
| `NYAYASEAL_DATA_DIR` | No | `/tmp/nyayaseal-data` (default). Vault root on the serverless host. |

No API keys, no database URL, no secrets of any kind.

## 5. Known limits — read before judging the deploy

- **Per-instance ephemeral vault (serverless honesty note) — and the fix.**
  On Vercel each serverless instance has its own `/tmp`, so seals and the
  register persist only within one instance; a cold instance starts with
  only the 3 seeded SAMPLE documents. **Verification does not depend on
  that:** since the 10 Nov 2026 stateless fix, `verify()` compares the
  SHA-256 of the supplied document with the claimed blob id — no server
  storage needed — so seal-on-one-instance + verify-on-another returns
  AUTHENTIC. Only a blob-id-alone lookup consults the per-instance
  register, and its NOT FOUND is labelled registry-only, never proof the
  document was never sealed. (The earlier runbook wording — "seal-then-
  verify in one session normally hits the same warm instance" — was WRONG
  live: an immediate verify hit a different instance and returned
  NOT FOUND. Fixed by the stateless path, not by assuming stickiness.)
  The audit log is still per-instance (same class of caveat as
  CageCheck's per-instance audit log on Vercel).
- **Walrus testnet is NOT connected.** Every receipt and API response says
  `backend: "local-vault"`; the UI badge says so too. Storing a blob needs a
  funded SUI wallet / publisher endpoint; none exists in this sandbox
  (rulebook §11). No Walrus blob id is ever faked.
- **2 MB per file; pasted text ≤ 200,000 chars.** No auth / multi-user:
  anyone with the URL can seal and verify (by design for a hackathon demo).

## 6. GitHub repo creation (browser — the GitHub App cannot do this)

The Muse GitHub App cannot create repositories (403 `Resource not accessible
by integration`, confirmed twice before, e.g. `tapeout-gate`). Create the repo
in the user's signed-in GitHub browser session:

1. https://github.com/new → Repository name `nyayaseal` → Description
   `NyayaSeal — provably authentic legal documents for the Walrus Haulout Hackathon`
   → **Public** → **do NOT tick** "Add a README file", "Add .gitignore" or
   "Choose a license" → **Create repository**.
2. Then push the snapshot via the GitHub connector (see §2 step 2) — the
   connector CAN push to an existing empty repo; it only cannot create one.
3. Verify: `list_commits` on `MSAbhishek22/nyayaseal` shows the snapshot
   commit; `README.md` at the repo root renders.

## 7. Rollback

- Vercel keeps every deployment: roll back from the Vercel dashboard →
  Deployments → promote the previous deployment. No data migration exists
  (vault is ephemeral by design, §5), so rollback is a pure code revert.
- If the live URL is broken, mark Gate E **BLOCKED** with the exact error
  and do NOT claim a live deployment.

## 8. After the deploy is verified

1. Record the live URL + deployed commit SHA in
   `deployment/RELEASE_MANIFEST.json` (fields are `null` until then).
2. Record the demo video from the live URL (Gate F — separate task).
3. Submit to DeepSurge (https://www.deepsurge.xyz) before
   **Mon 23 Nov 2026** — exact cut-off time still unverified; check the
   DeepSurge page before submitting (Gate G — separate task).
