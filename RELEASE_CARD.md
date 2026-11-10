# RELEASE CARD — NyayaSeal (Walrus Haulout Hackathon)

**Date:** 10 Nov 2026 · **Status: IN_PROGRESS** (NOT complete — Gates E, F, G are BLOCKED, see below)
**Hackathon:** Walrus Haulout Hackathon (Sui/Walrus, DeepSurge) — $105,000 prize pool,
Truth Engine + Trust Oracle track. Closes **Mon 23 Nov 2026**. Solo, online, free.
**Builder:** M S Abhishek (solo) · **Project folder:** `~/workspace/hackathons/walrus-haulout/`

## Project identity

**NyayaSeal — "NyayaLedger reborn for Walrus": provably authentic legal documents.**
A user seals a document (file upload / pasted text); the server hashes the exact bytes
(SHA-256) and stores them in a real content-addressed blob store where the hash IS the
address — the same addressing idea as a Walrus blob id. Anyone can then verify: upload
the file or paste the blob id → **AUTHENTIC** (hash match, with timestamp, issuer, blob
id) or **TAMPERED** (one changed character changes the hash completely) or **NOT FOUND**.
A one-click tamper demo proves the check is real. Every seal/verify writes a receipt to
a hash-chained audit log, re-verifiable in one click. Seeded with 3 clearly-labelled
SAMPLE Indian legal documents (Freelance Services Agreement, Affidavit, Legal Notice).
General legal information, not legal advice.

**Design:** Neo-Brutalism — the Evidence Board + the Rubber Stamp. Dossier cream
`#FFF3D6`, ink, vermilion `#E8380D`, teal `#0E7C6B`, gold `#FFB000`; Archivo Black
display type; verdicts as rotated rubber stamps. Distinct from NyayaLedger (Swiss
Minimalism, paper/ink/red), TapeOut Gate (Cinematic/Film Noir — the reason Noir was
NOT reused), PollPulse (Glassmorphism) and CageCheck. See
`design/DESIGN_CONSTITUTION.md` + `design/PROJECT_DESIGN_REGISTRY.md`.

## Deliverables / evidence

| Deliverable | Evidence |
|---|---|
| Project identity | This card + `README.md` |
| Research | `design/DESIGN_CONSTITUTION.md` — 5 real references, inspected 10 Nov 2026 (Proof/Notarize, Walrus Docs, Linear, NYT design system doc, three.js) |
| Live application | **BLOCKED — no live HTTPS deployment yet** (needs user approval / deploy step; see Gates) |
| GitHub | **BLOCKED — no repo created** (GitHub App cannot create repos — known 403; repo creation needs the user) |
| Deployment | **BLOCKED** — no provider, no build ID, no manifest |
| UI quality | Design constitution + registry comparison, both PASS; QA screenshots at 1280/768/390 in `/tmp/nyayaseal-qa/shots/` (QA evidence, not a deliverable) |
| 3D experience | CSS-3D Vault Stack — real sealed docs as fanned 3D cards, rotate via buttons + drag, arrow-key selection, 2D fallback (`.no3d`, code-inspected, render BLOCKED — headless Chrome supports 3D), static in low-motion |
| Functional controls | `qa/INTERACTION_INVENTORY.md` — 46 controls: **40 PASS · 1 FAIL · 5 BLOCKED** at QA time; the 1 FAIL (arrow-key selection) + 3 of the low issues were fixed after QA — see `qa/FIXES_POST_QA.md` |
| QA | `qa/QA_REPORT.md` — unit tests **17/17 PASS** (16 at QA + 1 new test for fix I-4); live smoke seal→AUTHENTIC, tampered→TAMPERED, unknown→NOT FOUND, chain OK; zero console errors; no horizontal overflow at 1280/768/390 |
| Demo video | **BLOCKED — not recorded** (requires a live deployment first) |
| Published video | **BLOCKED** |
| Submission | **BLOCKED — not submitted to DeepSurge** (needs user approval + live URL + video) |

## Run locally (verified 10 Nov 2026)

```bash
cd ~/workspace/hackathons/walrus-haulout
python3 -m app.server        # → http://127.0.0.1:8902
python3 -m unittest discover -s tests   # 17 tests, all PASS (0.023 s)
```

Python 3 stdlib only — no pip installs, no CDN, no external assets, no secrets, no env vars.

## What is REAL vs STUBBED / BLOCKED (honesty)

- **Real:** SHA-256 sealing, content-addressed blob store (`data/blobs/<sha256>`),
  verify (AUTHENTIC / TAMPERED / NOT FOUND), tamper demo (real byte flip), register,
  hash-chained audit log + chain re-verification, full UI, CSS-3D vault.
- **Stub:** `WalrusTestnetAdapter` raises `NotImplementedError` — testnet store was NOT
  attempted. Blocker (recorded in the UI badge, hero, §05, footer, every API response
  as `backend: "local-vault"`): storing a blob needs a funded SUI wallet / publisher
  endpoint; no wallet, no account, no card in this sandbox (rulebook §11). The
  aggregator read path was probed live 10 Nov 2026 and is reachable (`BLOB_NOT_FOUND`
  for unknown ids). No Walrus blob id is ever faked. Swap in the testnet adapter when
  a funded testnet wallet exists.
- **Divergences from the design constitution (recorded in README, confirmed by QA):**
  hashing is server-side (not client-side `crypto.subtle`); 3D is CSS 3D (no Three.js).
- **NOT claimed:** no Daml, no Canton/DevNet, no live Walrus storage, no deployment,
  no repo, no video, no submission.

## Release gates

| Gate | Verdict |
|---|---|
| A — Research and design | **PASS** (5 references, constitution, registry PASS) |
| B — Functional product | **PASS** (46 controls inventoried; post-QA fixes applied, 17/17 tests) |
| C — 3D and visual quality | **PASS** (CSS-3D vault live; 2D fallback render BLOCKED — observation limit, code-inspected) |
| D — QA | **PASS** (17/17 unit; live smoke; responsive 1280/768/390; reduced-motion; keyboard focus; known issues in QA report + post-QA fixes) |
| E — GitHub and deployment | **BLOCKED** (no repo — GitHub App 403, user must create; no live HTTPS deploy yet) |
| F — Demo video | **BLOCKED** (needs live deployment first) |
| G — Final handoff | **BLOCKED** (depends on E + F + user approval to submit) |

## Final status summary

- `LIVE_DEPLOYMENT`: **BLOCKED**
- `GITHUB_COMMIT_MATCH`: **BLOCKED**
- `ALL_VISIBLE_CONTROLS`: **PASS** (post-QA fixes; 5 inventory rows remain BLOCKED only as headless-observation limits — native file-picker dialog + `.no3d` fallback render)
- `3D_EXPERIENCE`: **PASS**
- `UI_DISTINCTIVENESS`: **PASS**
- `RESPONSIVE_AND_ACCESSIBLE`: **PASS**
- `DEMO_VIDEO_RECORDED_FROM_LIVE`: **BLOCKED**
- `VIDEO_PUBLISHED_AND_URL_VERIFIED`: **BLOCKED**
- `HACKATHON_RULE_COMPLIANCE`: **PASS** (free-only, solo, online; fresh build; no rule breached; no fake Walrus claims)
- `OVERALL_RELEASE`: **IN_PROGRESS**

## Next steps (need user / parent-agent approval)

1. Create the GitHub repo (user — the GitHub App cannot create repos) and push this folder.
2. Deploy free (Vercel Hobby or equivalent, no card) and verify the live URL from a fresh session.

**Deploy prep DONE 10 Nov 2026 (deploy coordinator):** Vercel serverless
adapter `api/index.py` + `vercel.json` + `.python-version` (3.12) written;
WSGI harness **14/14 PASS**, unit tests still **17/17 PASS**; secret scan
clean (0 hits); push manifest ready at `~/workspace/hackathons/nyayaseal-paths`;
`deployment/DEPLOYMENT_RUNBOOK.md` + `deployment/RELEASE_MANIFEST.json`
written (live URL / commit SHA still `null` — no deploy exists yet). Repo
`MSAbhishek22/nyayaseal` confirmed NOT to exist (search total_count 0).
Brand aligned to NyayaSeal in the UI (`<title>`, H1, footer). Gate E stays
**BLOCKED** until the repo is created (browser) and the live URL is verified.
3. Record the demo video from the live URL, publish it, then submit to DeepSurge
   (https://www.deepsurge.xyz) before **Mon 23 Nov 2026** (exact cut-off time unverified —
   check the DeepSurge page before submitting).
4. Optional, before submitting: verify Walrus prize payout currency + exact 23 Nov
   cut-off on the DeepSurge page (flagged in batch-9 findings as unverified).
