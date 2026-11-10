# QA Report — NyayaSeal (Walrus Haulout Hackathon entry)

**Date:** 10 Nov 2026, ~05:12–05:16 UTC (10:42–10:46 IST)
**QA agent:** subagent (no app code changed; no bug fixed)
**Scope:** `~/workspace/hackathons/walrus-haulout/` — app already built and
unit-tested (16/16 claimed by the coordinator). No deploy, repo, video, or
submission was done or attempted.

## 1. How I tested

- **Pristine-data rule:** all live testing ran against a **fresh copy** in
  `/tmp/nyayaseal-qa` (`cp -r app/ tests/ README.md`), started with
  `python3 -m app.server` from that copy on port 8902. Real `data/`
  md5s were recorded before QA (`register.json d3d7c176…`,
  `audit.jsonl 9e6efe87…`, 3 blobs) and re-checked after every test run —
  **unchanged at the end; all QA seals (7 extra docs, 19 receipts) exist
  only in the /tmp copy**, which was left on disk for the record and is
  not part of the deliverable.
- **Unit tests:** `cd ~/workspace/hackathons/walrus-haulout &&
  python3 -m unittest discover -s tests -v` — see §2.
- **API smoke:** `curl` against the /tmp server — seal (text + file),
  verify (file / hash / text), tamper-demo, chain verify, doc lookup,
  and 10 error/edge cases — see §3.
- **Real browser:** headless Chrome 156 (Playwright cache build at
  `~/.cache/ms-playwright/chromium-1248/chrome-linux64/chrome`),
  driven over CDP by small dependency-free Node scripts
  (`/tmp/nyayaseal-qa/cdp.mjs`, `cdp2.mjs`, `cdp3.mjs`, `cdp4.mjs`).
  This exercised the actual UI: clicks, real file drop (in-page `File`),
  real file inputs (`DOM.setFileInputFiles`), real Tab presses
  (`Input.dispatchKeyEvent`), pointer drag, emulated
  `prefers-reduced-motion`, and a real receipt download
  (`Page.setDownloadBehavior`). Screenshots at 1280 / 768 / 390 px are in
  `/tmp/nyayaseal-qa/shots/` (`viewport-*.png`, `vault-1280.png`,
  `deeplink-1280.png`).
- **Static checks:** `node --check app/static/app.js`; `grep` for
  `crypto.subtle` / Three.js / gradients / blur; contrast ratios computed
  in Python from the `:root` tokens.
- **What I did not do:** no deploy, no repo, no video, no submission
  (out of scope); no test of the native file-picker dialog opening
  (unobservable in headless Chrome — recorded as BLOCKED in the
  inventory, not as a pass); no test of the `.no3d` 2D fallback rendering
  (this Chrome supports 3D — BLOCKED, code inspected instead).

## 2. Unit test re-run

Command (from the real folder, read-only for the tests — they use temp
dirs):

```
cd ~/workspace/hackathons/walrus-haulout && python3 -m unittest discover -s tests -v
```

Result: **16 tests, all OK, 0.024 s.** Every test passed, including
SHA-256 NIST vector (`abc`), seal→verify AUTHENTIC round-trip, tampered
bytes → TAMPERED, unknown hash → NOT FOUND, audit chain OK + forged-entry
detection (`bad_at: 1`), 2 MB limit, empty-input refusals, blob-on-disk
round-trip, sample seeding (3 docs), and both adapter tests (local
round-trip; Walrus stub raises `NotImplementedError`). Matches the
coordinator's claim exactly.

## 3. Live smoke results (all on the /tmp copy, port 8902)

| # | Flow | Method | Result |
|---|---|---|---|
| 1 | Seal by pasted text (JSON) | `POST /api/seal` `{text, title "QA Smoke Doc", doc_type Other, issuer "QA Agent"}` | **PASS.** Blob `3cff358c7eed74f8…` — independently recomputed with Python `hashlib.sha256` over the exact bytes: identical. Receipt `NLW-20261110-051212-CF87`, `backend: local-vault`, `duplicate: false`. |
| 2 | Seal same bytes by file upload | `POST /api/seal` multipart `qa-doc.txt` | **PASS.** `duplicate: true`, same blob id — content addressing works across text/file paths. |
| 3 | Verify by file | `POST /api/verify` multipart `qa-doc.txt` | **PASS — AUTHENTIC.** `The file's SHA-256 matches the sealed record exactly…` |
| 4 | Verify tampered file + expected id | Same file with `!` instead of `.` + `expected_blob_id` | **PASS — TAMPERED.** Computed `3cad878b…` ≠ claimed id. |
| 5 | Verify unknown hash | `POST /api/verify` `{hash: 000…0}` | **PASS — NOT FOUND.** |
| 6 | Verify known hash | `{hash: 3cff358c…}` | **PASS — AUTHENTIC.** |
| 7 | Tamper demo | `POST /api/tamper-demo` `{blob_id}` | **PASS — TAMPERED.** `tampered_hash` genuinely differs from original (byte 0 XORed server-side). |
| 8 | Chain verify | `GET /api/audit/verify` | **PASS — `{"ok": true, "checked": 10, "bad_at": null}`** (3 seed seals + QA seals/verifies). UI button showed `Chain OK — 10 receipt(s) re-hashed, no break.` |
| 9 | Doc lookup | `GET /api/doc?id=<blob>` | **PASS.** Full record returned. Unknown id → HTTP 404 `No sealed document with that blob id.` |
| 10 | Deep link | `GET /?blob=<id>` | **PASS — HTTP 200**; in-browser run auto-verified `AUTHENTIC`. Unknown id → `NOT FOUND` stamp; malformed id → clean error message (see §5). |
| 11 | Error cases (10) | curl, all on /tmp server | **All PASS** (plain-language 400s): empty text; missing title; seal with neither file nor text; malformed hash; empty verify body; tamper-demo unknown id; bad doc type; unknown route → 404; `/static/../server.py` traversal → 404; >2 MB file on seal *and* verify → 400 `File is 2,097,153 bytes — the limit is 2,097,152 bytes (2 MB).` |

UI-level repeats of the same flows (CDP, real browser): seal-by-text,
seal-by-dropped-file, verify-by-file (AUTHENTIC), verify-tampered-file
(TAMPERED), verify-by-hash (AUTHENTIC), tamper demo (TAMPERED),
chain verify, row/card click → detail, detail → verify, receipt
download (real file landed, §5) — **all PASS**. Zero console errors or
uncaught exceptions observed across all CDP sessions (Runtime + Log
domains enabled).

## 4. HTTP status + syntax

| Route | Status |
|---|---|
| `GET /` | **200** |
| `GET /static/style.css` | **200** |
| `GET /static/app.js` | **200** |
| `GET /api/status` | **200** (`backend: local-vault`, `walrus_testnet: not connected`, full blocker text) |
| `GET /?blob=<id>` | **200** |
| `GET /api/nope` (unknown) | **404** JSON |
| `GET /static/../server.py` (traversal) | **404** JSON (basename-sanitised) |

`node --check app/static/app.js` → **syntax OK**. No external assets:
no CDN links, no external fonts loaded (font stacks are system
fallbacks), no fetch to any third-party origin in `app.js`.

## 5. Responsive checks (real headless Chrome, screenshots inspected)

| Viewport | `documentElement.scrollWidth` vs `innerWidth` | Horizontal overflow? | Notes |
|---|---|---|---|
| Desktop ~1280×900 | 1265 vs 1280 | **No** | Clean render (screenshot `viewport-1280.png`): nav, hero, stats, §01 all legible; primary actions unclipped. |
| Tablet ~768×1024 | 768 vs 768 | **No** | Clean (screenshot `viewport-768.png`): `.grid2` collapses to one column at ≤860 px, `.steps` to one column at ≤760 px, as designed. |
| Mobile ~390×844 | 394 vs 394 | **No** | No page-level overflow (screenshot `viewport-390.png`). Nav wraps to two rows of chunky buttons; badge wraps below; h1 fits. Two caveats: (a) the register table is wider than the viewport — **by design**, it sits in `.tablewrap { overflow-x: auto }`, i.e. the constitution's intended inner scroll (§11); (b) the fixed low-motion toggle overlaps the third hero stat card at this width (issue I-2). |

All three viewports were genuinely rendered and measured (CDP
`documentElement.scrollWidth` + element rect scan), not inferred from
CSS alone. No clipped primary action anywhere; the Seal / Verify buttons
are full-width and visible at 390 px.

## 6. Reduced motion + low-motion behaviour

- **Toggle:** click → `data-motion="low"`, label `Low motion: on`,
  `aria-pressed="true"`, vault stage `transform: none`; click again →
  fully restored. Drag-rotate is inert while low (pointer events
  dispatched, transform stayed `none`). **PASS.**
- **OS preference:** with `prefers-reduced-motion: reduce` emulated,
  the page auto-set low-motion on load (same label/`aria-pressed`/static
  stage as the toggle) — the `matchMedia` branch works. The CSS
  `@media (prefers-reduced-motion: reduce)` rule also forces sections
  visible with no transitions and no stamp animation. **PASS.**
- **Scroll reveal:** `.rv` sections gain `.in` via IntersectionObserver
  on scroll (0 → 4 revealed after scrolling to `#audit`; `#audit`
  gained `.in`). Transform + opacity only, 240 ms. **PASS.**

## 7. Keyboard + focus visibility

- Six real Tab presses moved focus through nav anchors → seal dropzone;
  **every** focused element matched `:focus-visible` with computed
  outline `3px solid rgb(255, 176, 0)` — the constitution's gold focus
  ring, verified on the live element, not just in the stylesheet.
- Dropzones and vault cards are `tabindex="0"`, `role="button"`; vault
  cards have full `aria-label`s; verdict/detail regions are
  `aria-live="polite"`; every input has a real `<label>` (or
  `aria-label` for the visually-hidden file inputs).
- **Gap:** vault ←/→ arrow-key selection is specified by constitution
  §8 but not implemented (see issue I-6 / inventory row D7).

## 8. Error / empty / loading states

- **Errors:** all server refusals are plain-language 400s rendered in
  `.err` panels (empty seal, missing title, bad hash, oversize,
  unknown tamper id, bad doc type). Client-side pre-checks: verify with
  nothing → inline `Nothing to verify…`; tamper with no selection →
  `Pick a sealed document first.` **PASS.**
- **Empty states:** register/audit empty messages exist in code
  (`No documents sealed yet…`, `No receipts yet.`); not triggered live
  because the vault always seeds 3 samples — noted, not scored.
- **Loading states:** `Sealing…`, `Verifying — re-hashing and
  comparing…`, `Flipping one character and re-checking…`,
  `Loading sealed documents…` placeholders present and observed
  transiently during CDP runs. **PASS.**
- **Duplicate seal:** `Already sealed — identical bytes.` (API-verified;
  UI string in `app.js`). **PASS.**
- **Receipt download:** real file landed —
  `nyayaseal-receipt-9a33d71e5d73.json` (959 bytes, valid JSON with
  `document` + `receipt`, `backend: local-vault`). **PASS.**

## 9. Design-constitution compliance

Checked against `design/DESIGN_CONSTITUTION.md`:

| Requirement | Result |
|---|---|
| Tokens: cream `#FFF3D6`, vermilion `#E8380D`, teal `#0E7C6B`, gold `#FFB000`, blue `#2547F4`, ink `#111111`, muted `#5C564A` | **PASS** — exact values in `:root`, used semantically (vermilion = Seal CTA / TAMPERED / errors; teal = AUTHENTIC / SEALED; gold = seal motif + focus ring; blue = links/blob identity). |
| No gradients / glass / blur / glow; hard offset shadows only | **PASS** — `grep` finds no `linear-gradient`, `radial-gradient`, `backdrop-filter`, or `blur(` in CSS (only a comment stating the rule). Shadows are `6px 6px 0` / `4px 4px 0` hard offsets. |
| Stamp verdicts (rotated, Archivo Black, word + colour) | **PASS** — `.verdict` 900-weight, `AUTHENTIC` teal at −4°, `TAMPERED`/`NOT FOUND` vermilion at +3°, stamp-slam keyframes (scale + opacity, 180 ms). Observed live in screenshots/DOM. |
| Motion: transform + opacity only | **PASS** — transitions/animations in CSS touch only `transform`/`opacity` (`.rv` reveal, `.vault-stage`, `.verdict` stamp, button `translate` on hover/press). No width/height/top/left animation. No continuous animation, no particles, no second canvas. |
| Contrast (constitution's own figures) | **PASS, verified by computation:** ink on cream 17.12:1 (claimed 17.1), white on vermilion 4.2:1 (claimed 4.2, large display type only), white on teal 5.1:1 (claimed 5.1), muted on cream 6.6:1 (claimed 6.6), ink on gold 10.31:1, blue on cream 5.79:1. |
| 3D vault (CSS 3D, no Three.js) + 2D fallback + low-motion static | **PASS (3D + low-motion), BLOCKED (fallback render).** 3D stack renders real cards fanned in depth (screenshot `vault-1280.png`), rotate/drag/reset all live. Low-motion → static (`transform: none`). The `.no3d` grid fallback is code-coherent but could not be triggered in this Chrome (`supports3d === true`). |
| Recorded divergences (README) | **Both confirmed true in code, not surprises:** (1) hashing is server-side — `grep` finds zero `crypto.subtle` in `app/static/`; `vault.py:sha256_hex` computes it; the UI says so (`The server hashes the exact bytes`). (2) No Three.js — zero matches for `three`/`THREE` in app code; the vault is CSS 3D (`perspective`, `preserve-3d`, `translateZ`). |
| Honesty (no fake Walrus claims) | **PASS.** Every receipt/API response carries `backend: "local-vault"`; the nav badge, hero disclaimer, §05 note, and footer all say Walrus testnet is not connected and why; `WalrusTestnetAdapter` raises `NotImplementedError` and is never wired into the server. No Walrus blob id is ever shown or faked. |

**Undocumented constitution deltas (all low severity, none breaks a
workflow):** no hero CTA buttons (§6 specifies two); no `NYAYA—SEAL`
logo block in the top bar (§6); no `aria-current` on nav (§7);
drag-over changes only the dropzone background, not the label text to
`DROP IT — WE HASH IT HERE` (§8); no jagged crack edge on the TAMPERED
stamp (§8); no tampered-slab tilt in the vault (§9); no `+N EARLIER`
collapse indicator for >8 docs (§9 — see I-3); no ←/→ vault selection
(§8 — see I-6/D7); no client-side hashing progress bar / hash
typewriter (§8 — a direct consequence of the recorded server-side
hashing divergence, not a separate surprise).

## 10. Known issues (severity-ordered)

| ID | Severity | Issue | Evidence |
|---|---|---|---|
| I-1 | Low–medium | **No `scroll-margin-top` on sections:** anchor jumps (nav links, `?blob=` scroll, detail→verify) land the section heading underneath the sticky nav bar. | `vault-1280.png`: `03 THE VAULT` heading is half-hidden behind the nav after `scrollIntoView()`. Fix: `section { scroll-margin-top: 70px; }` (one line). |
| I-2 | Low | **Fixed low-motion toggle overlaps content** at bottom-right (register table at 1280 px, third hero stat at 390 px). | Visible in `viewport-390.png` and `vault-1280.png` (toggle sits on top of the table's last visible row area). Cosmetic; toggle is usable. |
| I-3 | Low (latent) | **Vault 3D caps at 8 cards with no indicator:** `renderRegister` does `docs.slice(0,8)`; docs 9+ silently vanish from the 3D view (table still lists all). Constitution §9 wants a `+N EARLIER` base slab. | Code-reading (`app.js`); not triggered live (max 6 docs during QA). |
| I-4 | Low | **Malformed `expected_blob_id` + file → `TAMPERED` instead of 400.** Verify-by-hash alone correctly 400s on a malformed id; verify-by-file with a malformed expected id reports TAMPERED (`The file's hash does not match the claimed blob id…`), which mislabels a user typo as tampering. | Verified live: `POST /api/verify` file + `expected_blob_id=not-a-hash` → `TAMPERED`; same file + well-formed wrong id → `TAMPERED` (correct); + correct id → `AUTHENTIC`. Fix: validate `_HEX64` on `expected_blob_id` in `vault.verify` / the handler. |
| I-5 | Low | **`verify-chain` has no `try/catch`:** a network failure would leave an uncaught promise rejection (console) instead of a UI message. Other buttons (`seal`, `verify`, `tamper`) all catch and render. | Code-reading (`app.js`); not triggered live (server was up). |
| I-6 | Low | **Vault ←/→ arrow-key selection missing** (constitution §8). Keyboard users can still Tab to cards and press Enter, and the table is a full text equivalent — so no workflow is blocked. | CDP: `ArrowRight` on stage + body changed nothing (inventory row D7, the single FAIL). |

No other issues found. In particular: **no dead buttons, no fake
toasts, no invented data, no broken links, no console errors.**

## 11. Gate verdicts

- **Gate B — functional completeness (every control live, core flows
  real): PASS.** 40/46 inventory rows PASS live in a real browser;
  the single FAIL (arrow-key selection) is a minor missing keyboard
  convenience with working equivalents; the 5 BLOCKED rows are
  headless-observation limits, with the underlying inputs proven via
  adjacent paths (real drag-drop seal, real file-input verify). All
  four core verdicts (AUTHENTIC / TAMPERED / NOT FOUND / chain OK)
  were produced by the real server from real bytes, in the UI and via
  the API.
- **Gate C — design-constitution compliance: PASS (with noted deltas).**
  Tokens, stamp verdicts, transform+opacity-only motion, contrast
  figures, responsive behaviour, and the honest local-vault posture all
  verify. The deltas in §9 are cosmetic or direct consequences of the
  two recorded divergences; the one functional delta (arrow keys) is
  I-6.
- **Gate D — honesty / no-fake-claims: PASS.** No Walrus blob id is
  faked anywhere; the stub is disclosed in the UI (badge, hero, §05),
  in every API response (`backend: local-vault`), and in the README;
  the two README divergences (server-side hashing, CSS 3D) were both
  confirmed true in the code. Sample documents are labelled SAMPLE;
  the UI states verification proves bytes unchanged, not legal truth.

**Overall: the entry is submittable on quality grounds once the
recording/deploy/submission steps (out of scope here) are done.
Suggested pre-submit fixes, in order: I-1 (one-line CSS),
I-4 (one validation check), I-6 (arrow-key handler), I-2 (toggle
placement or page bottom padding). None is a gate-blocker.**

## 12. Files produced

- `qa/INTERACTION_INVENTORY.md` — 46-row control inventory (40 PASS / 1 FAIL / 5 BLOCKED).
- `qa/QA_REPORT.md` — this file.

Supporting evidence (not deliverables, kept in `/tmp/nyayaseal-qa/`):
CDP scripts (`cdp.mjs`, `cdp2.mjs`, `cdp3.mjs`, `cdp4.mjs`), result
JSONs, screenshots (`shots/`), the downloaded receipt
(`downloads/nyayaseal-receipt-9a33d71e5d73.json`), and the /tmp server
copy with its QA-only data. Test processes (server on 8902, Chrome on
9222) were stopped at the end of QA; the real `data/` was verified
pristine (md5s unchanged).
