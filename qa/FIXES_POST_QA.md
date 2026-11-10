# Fixes applied after QA (10 Nov 2026, coordinator)

QA report (`QA_REPORT.md`, 10 Nov ~10:42–10:46 IST) found 46 controls:
40 PASS · 1 FAIL · 5 BLOCKED, plus low issues I-1…I-6. The coordinator fixed the
four suggested pre-submit fixes directly (no new subagent). No other app code changed.

| Issue | Fix | File(s) |
|---|---|---|
| I-1 (low–medium) — anchor jumps land headings under the sticky nav | `scroll-margin-top: 76px` on `section` | `app/static/style.css` |
| I-2 (low) — fixed low-motion toggle overlaps content at bottom-right | `main { padding-bottom: 84px }` so page content clears the toggle | `app/static/style.css` |
| I-4 (low) — malformed `expected_blob_id` + file returned TAMPERED instead of 400 | `verify()` now validates the expected id against `_HEX64` first and raises `VaultError` (400) with a plain typo message; it is never reported as tampering | `app/vault.py` |
| I-5 (low) — `verify-chain` had no `try/catch` | Wrapped in try/catch; network failure now shows "Could not verify the chain — server unreachable. Try again." | `app/static/app.js` |
| I-6 / inventory D7 (the 1 FAIL) — vault ←/→ arrow-key selection missing | ArrowRight/ArrowLeft on a vault card now moves focus to the next/previous card (wraps); Enter/Space still selects | `app/static/app.js` |

I-3 (vault 3D caps at 8 cards, no `+N EARLIER` indicator) was left as-is: latent only
(max 3–6 docs in practice), cosmetic, and changing the render risks the verified 3D
behaviour this close to the release card. Noted here, not hidden.

## Re-verification after the fixes (coordinator, fresh /tmp copy, port 8902)

- `python3 -m unittest discover -s tests` → **17 tests, all PASS** (0.023 s) —
  the 16 QA tests plus a new `test_malformed_expected_id_refused_not_tampered`.
- `node --check app/static/app.js` → syntax OK.
- Live: malformed `expected_blob_id` + file → **HTTP 400** with the typo message
  (was TAMPERED); `GET /api/audit/verify` → `{"ok": true, "checked": 3}`;
  `GET /` → 200.
- Real `data/` untouched by all verification runs (still 3 pristine sample blobs);
  `__pycache__` removed from the deliverable folder.

The QA report itself was not rewritten — it is a dated record of the pre-fix state.
This addendum is the post-fix record. Inventory status after fixes: the 1 FAIL is
resolved; the 5 BLOCKED rows remain observation limits only (native file-picker
dialog opening, `.no3d` fallback render — underlying inputs proven via adjacent
paths during QA).
