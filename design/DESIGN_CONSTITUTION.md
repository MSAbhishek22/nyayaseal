# DESIGN CONSTITUTION — NyayaSeal (Walrus Haulout Hackathon)

> **Project:** NyayaSeal — "NyayaLedger reborn for Walrus: provably authentic
> legal documents" (Truth Engine + Trust Oracle track, $105,000 prize pool,
> closes Mon 23 Nov 2026).
> **Status:** Design constitution written 10 Nov 2026, BEFORE implementation.
> It is the binding spec for the builder agent working in `app/` in parallel.
> Where the built UI differs from this file later, the built UI wins and the
> difference must be stated here.
> **Rulebook:** `~/workspace/ABHI_22_GLOBAL_PROJECT_QUALITY_RULEBOOK.md` §1.2.
> Gate A (research + design) is satisfied by this file + `PROJECT_DESIGN_REGISTRY.md`.

## 0. Style pick — Neo-Brutalism (and why the Film Noir leaning was overridden)

**Chosen: Neo-Brutalism.** The parent brief leaned Cinematic / Film Noir
(dark vault, amber seal). That leaning is **overridden with reasons**:

1. **Film Noir is already taken — by the most recent project.**
   TapeOut Gate (9 Nov 2026, `~/workspace/hackathons/okx-tapeout/design/`)
   IS Cinematic / Film Noir: night `#0b0a08`, desk `#14120e`, lamp amber
   `#e8a33d`, Georgia serif, single 880px column, signal-lamp pills,
   kinetic verdict typography. Reusing it one day later would violate
   rulebook §1.3 (recognisably different in more than accent colour).
   The leaning is recorded here and rejected for this reason, not ignored.
2. **Neo-Brutalism fits the product's emotional promise better than Noir
   does for THIS product.** TapeOut Gate is a quiet night-desk guard; its
   verdict must whisper. NyayaSeal is a public claim of authenticity:
   "this document is real, and here is the proof, in your face." A
   verdict that looks like a rubber stamp slammed onto a dossier — huge,
   flat, rotated, impossible to miss — is the honest visual form of
   AUTHENTIC / TAMPERED. Brutalism shouts the verdict; Noir would
   underplay the one thing the judges must see in two seconds.
3. **It is maximally distant from all four predecessors at once** (see
   `PROJECT_DESIGN_REGISTRY.md`): light where TapeOut Gate and PollPulse
   are dark; loud flat colour blocks and 3px borders with hard offset
   shadows where NyayaLedger is hairline-restrained and CageCheck is a
   soft paper stamp-desk; a chunky two-panel workbench layout where
   TapeOut Gate and CageCheck are single centred columns and NyayaLedger
   is a broadsheet with numbered sections.

**Rejected alternatives:** Cinematic/Film Noir (taken by TapeOut Gate);
Glassmorphism (taken by PollPulse; glass + blur also fights hash
readability); Swiss Minimalism/Editorial (taken by NyayaLedger);
Organic/Liquid and Hand-drawn/Claymorphism (wrong tone — a legal-proof
tool must look certain, not soft or sketchy); Parallax Scrollytelling
(wrong shape — this is a tool, not a story page); Retro-Futurism/Y2K
(chrome/iridescence would cheapen a trust product).

## 1. Product personality and emotional tone

**A stamp desk in a government archive that has been redesigned by a
poster artist.** Loud, flat, certain. No whispering, no glow, no blur,
no gradients, no decoration that does not carry information. The product
says: "Upload. We hash it. We seal it in the vault. Anyone can re-check
it. The answer is a stamp, not a vibe."

Tone: confident, procedural, slightly playful in the visuals (rotated
stamps, chunky blocks) but deadly serious in the evidence (hashes,
timestamps, blob IDs are always shown in full, never truncated into
meaninglessness, never faked).

## 2. Target user and context of use

- **Primary user:** an Indian lawyer, paralegal, auditor, or citizen
  with a legal document (agreement, affidavit, certificate, will) who
  needs to prove — to a counterparty, a court, or a client — that the
  file they hold is byte-for-byte the file that was sealed.
- **Secondary user:** the hackathon judge on a laptop screen share, who
  must understand the whole loop (upload → hash → seal → verify →
  verdict) in one scroll, with no tab hunting.
- **Context:** laptop browser first, phone second. The user may be in a
  law office, a court corridor, or a cyber-café — so the page must work
  on a mid-range phone, on a slow connection, with no account and no
  install. Everything is client-side hashing (SHA-256 in the browser)
  plus a content-addressed blob store (Walrus); the document's bytes
  never need to leave the user's machine to be *verified* — only the
  hash travels.

## 3. Visual metaphor — the Evidence Board + the Stamp

Two linked metaphors, one per half of the product:

- **The Evidence Board:** the page is a corkboard/dossier wall of
  chunky bordered panels pinned in a strict grid — each panel is one
  fact (the document, its hash, its blob ID, its issuer, its timestamp).
  Panels have 3px ink borders and hard offset shadows (`6px 6px 0 ink`),
  like paper cards pinned to a board. Nothing floats, nothing blurs.
- **The Stamp:** the verdict is a physical rubber stamp. AUTHENTIC is a
  teal block stamped at −4°; TAMPERED is a vermilion block stamped at
  +3°, with a cracked edge. The stamp is the only rotated element on the
  page, which is exactly why it reads as a stamp.
- **The Vault Stack (3D):** sealed documents are chunky slabs stacked
  in an isometric vault (see §9). The stack IS the ledger, in depth.

## 4. Colour palette — semantic roles (exact tokens for the builder)

| Token | Value | Semantic role | Where used |
|---|---|---|---|
| Dossier cream | `#FFF3D6` | Page background | `body` |
| Card white | `#FFFFFF` | Panel surface | All panels, inputs |
| Ink | `#111111` | Text, all borders, hard shadows | Everything structural |
| Seal vermilion | `#E8380D` | TAMPERED, danger, primary CTA | Verdict stamp (tampered), Seal button, errors |
| Vault teal | `#0E7C6B` | AUTHENTIC, success, sealed state | Verdict stamp (authentic), verified badges |
| Seal gold | `#FFB000` | The seal itself, highlights, hash accents | Seal badge, hash highlights, focus ring |
| Vault blue | `#2547F4` | Links, blob/Walrus identity, info | Links, Walrus blob IDs, info states |
| Muted | `#5C564A` | Secondary text, labels, captions | Small print, labels |
| Paper line | `#111111` | Borders are always ink, 2–3px | All panel borders |

**Rules (non-negotiable):**
- No gradients, no glassmorphism, no blur, no glow, no drop-shadow
  blur — shadows are hard offsets only (`6px 6px 0 #111111`, `4px 4px 0`
  on small elements). This is the single most visible difference from
  PollPulse (glass + gradient orbs) and TapeOut Gate (spotlight glow).
- Vermilion is used ONLY for TAMPERED / danger / the Seal CTA.
  Teal is used ONLY for AUTHENTIC / sealed-success. Gold is used ONLY
  for the seal motif and hash accents. Blue is used ONLY for links and
  Walrus/blob identity. A verdict is never colour-only: the word
  AUTHENTIC / TAMPERED is printed in the stamp itself, at 900 weight.
- Flat colour blocks only — a panel is one solid colour, never a tint
  gradient. Section backgrounds alternate cream / white / gold-tint
  (`#FFE9A8` at most once, for the "How proof works" band).

## 5. Typography and type hierarchy

- **Display:** **Archivo Black** (900) for the hero headline and the
  verdict stamp — the loudest voice on the page. Fallback:
  `"Arial Black", "Helvetica Neue", sans-serif`. Hero: `clamp(3rem, 8vw,
  6rem)`, uppercase, tight leading (0.95), letter-spacing −0.01em.
- **UI / body:** **Space Grotesk** (400/500/700) for labels, buttons,
  body copy. Fallback: `system-ui, "Segoe UI", sans-serif`. Body 17px,
  line-height 1.55.
- **Data:** **IBM Plex Mono** (400/600) for hashes, blob IDs,
  timestamps, receipts — the evidence voice. Fallback: `ui-monospace,
  Menlo, Consolas, monospace`. Hashes render at 13–14px, `word-break:
  break-all`, never truncated below 16 visible characters without a
  "copy full hash" control next to them.
- **Hierarchy:** hero display (Archivo Black, uppercase) → section
  titles (Space Grotesk 700, uppercase, 28–32px, with a 3px underline
  bar) → panel titles (Space Grotesk 700, 18px, uppercase, letterspaced)
  → body (17px) → mono evidence (13px) → micro-labels (12px, uppercase,
  0.12em letterspacing, muted).
- **Why this differs:** NyayaLedger is Helvetica grotesk uppercase +
  system mono (restrained editorial); TapeOut Gate is Georgia serif
  (cinematic); CageCheck is Georgia serif headings + system sans.
  Archivo Black at 900 weight with flat colour blocks is a different
  register from all three — poster type, not editorial or cinematic type.

## 6. Layout grid, spacing and page composition

- **Grid:** 12-column, `max-width: 1200px`, centred, 24px gutters.
  Spacing scale (4px base): 8 / 16 / 24 / 32 / 48 / 64 / 96.
- **Top bar (sticky):** 3px bottom border, cream background. Left: a
  solid ink logo block ("NYAYA—SEAL" in white Archivo Black, rotated
  −1°) + gold seal dot. Centre/right: nav as chunky bordered buttons
  (Seal / Verify / Vault / Evidence) — NOT text links, NOT a sidebar.
- **Hero (split, NOT a centred masthead):** left 7 cols — kicker chip
  ("WALRUS HAULOUT · TRUTH ENGINE + TRUST ORACLE"), giant headline
  "PROVE IT. / OR IT DIDN'T / HAPPEN." with "PROVE IT." on a gold flat
  block, one-line lede, two chunky CTAs (Seal a document — vermilion;
  Verify a document — white with ink border). Right 5 cols — the Vault
  Stack 3D scene (§9) in a bordered panel with a hard shadow.
  No full-bleed masthead, no numbered editorial sections (NyayaLedger),
  no single centred column (TapeOut Gate, CageCheck), no glass hero
  (PollPulse).
- **"How proof works" band:** gold-tint background, three chunky panels
  in a row (01 HASH — SHA-256 in your browser; 02 SEAL — blob stored on
  Walrus, hash = address; 03 VERIFY — re-hash + compare, stamp the
  verdict). Each panel: big mono number, title, one line, hard shadow.
  On mobile they stack, in order, with the numbers intact.
- **Workbench (the product):** two big panels side by side (Seal /
  Verify), each 3px border, 8px hard shadow, white. Seal panel: drop
  zone (dashed 3px ink border, gold on drag-over), file name + size +
  SHA-256 (live, computed client-side as the file loads), issuer name
  field, "SEAL IT" vermilion button, receipt output (blob ID, timestamp,
  hash). Verify panel: drop zone or paste-a-blob-ID, "VERIFY" teal
  button, verdict stamp + evidence table (expected hash vs computed
  hash, match/mismatch row-by-row, blob ID, sealed-at timestamp,
  issuer). A TAMPERED result also shows a "what changed" line (hashes
  differ at first differing byte position — computed, never invented).
- **Evidence ledger:** full-width bordered table, 2px ink rules,
  columns: Document / SHA-256 (truncated + copy) / Blob ID / Sealed at /
  Issuer / Verdict. Rows are flat; hover shifts the row 2px up-left
  (transform only) and deepens the hard shadow. No ruled-paper table
  like NyayaLedger's — this one has thick rules and a solid ink header
  row with white text.
- **Footer:** solid ink bar, cream text, mono links (Walrus docs,
  hackathon track, repo). No fine print in grey-on-grey.

## 7. Navigation and information architecture

Single page, four anchor sections, all reachable from the sticky top
bar (chunky buttons, `aria-current` on the active section):
`#seal` → `#verify` → `#vault` (3D) → `#evidence` (ledger).
Plus a "How proof works" band between hero and workbench (no nav item
— it is read, not jumped to). No sidebar, no multi-page routing, no
tabs. The workbench is the product; the hero sells it; the vault shows
it; the ledger proves it. Deep-linking: pasting a blob ID in the URL
(`?blob=<id>`) opens the Verify panel pre-filled and runs the check —
the shareable proof link.

## 8. Component behaviour and interaction patterns

- **Drop zones:** dashed 3px ink border; drag-over → gold background
  + border solid + label changes to "DROP IT — WE HASH IT HERE".
  Click opens the file picker. Accepted: any file (PDF, image, text);
  size cap shown in the label (state the real cap from the build, do
  not invent one here). Invalid/oversize → vermilion error panel with
  the reason in words, retry possible.
- **Hashing:** SHA-256 computed client-side with `crypto.subtle` as
  the file streams in; a chunky stepped progress bar (scaleX, teal
  fill, hard border) shows progress; the hash appears character by
  character in mono (typewriter is opacity-only per-character reveal,
  capped at 300ms total — it is evidence appearing, not decoration).
- **Buttons:** 3px ink border, hard shadow `4px 4px 0 ink`, uppercase
  Space Grotesk 700. Hover: `translate(-2px, -2px)` + shadow becomes
  `6px 6px 0` (transform only; shadow changes are instant, not
  animated). Active/pressed: `translate(2px, 2px)` + shadow `2px 2px 0`.
  Disabled: 50% opacity + "not-allowed" cursor + the reason in text
  beside it. Every button has a visible `:focus-visible` state: 3px
  gold outline + 2px offset.
- **Verdict stamp:** appears with the stamp-slam animation (§10);
  rotated (−4° authentic / +3° tampered); 3px border in its verdict
  colour; the word is Archivo Black, white on teal / white on
  vermilion; below it, the evidence table. A TAMPERED stamp also gets a
  jagged "crack" edge (CSS clip-path polygon, static) — the crack is
  part of the stamp, not an animation.
- **Copy controls:** every hash and blob ID has a "COPY" mini-button
  (mono, bordered); on copy it reads "COPIED ✓" for 1.5s, then reverts.
- **Receipt:** after sealing, a bordered receipt panel (mono) shows
  document name, SHA-256, blob ID, sealed-at timestamp, issuer, and
  the verify link. "Download receipt (.json)" produces a real file.
- **Vault blocks (§9):** clicking a block selects it; the evidence
  panel below the vault shows that document's hash/blob/verdict.
  Keyboard: ←/→ move selection, Enter opens evidence.
- **Loading / empty / error states:** hashing → stepped progress bar;
  verifying → "RE-HASHING…" + progress; no documents yet → ledger
  shows a bordered empty state ("NO DOCUMENTS SEALED YET — seal the
  first one above ↑"), never a blank table; network/Walrus failure →
  vermilion error panel with the real error text and a RETRY button.
  No fake success toasts, no dead buttons.

## 9. 3D concept — "The Vault Stack" (the ledger, in depth)

- **What it is:** an isometric stack of chunky document slabs inside
  a bordered vault panel (hero, right column; also a larger instance
  in the `#vault` section). Each sealed document is one slab: a flat
  box with a paper-white top face carrying the document name and the
  first 12 chars of its hash, a teal or vermilion side face by verdict,
  and a gold seal dot on the top face. Slabs stack in seal order,
  newest on top; the stack casts one hard flat shadow (no soft blur).
- **Why 3D is meaningful here:** the stack IS the product's claim —
  every sealed document is a physical, ordered, inspectable block in a
  vault, and tampering with one slab visibly breaks the stack (the
  tampered slab tilts 6° and shifts out of alignment, in red). A flat
  list cannot show "one block out of line" the way a stack can. The
  vault also visualises the Walrus model: content-addressed blobs are
  discrete, immutable units — slabs, not a soup.
- **Technology:** Three.js, lazy-loaded (only when the vault panel
  scrolls into view), ONE canvas, orthographic camera at a fixed
  isometric angle, flat-shaded `BoxGeometry` slabs, no textures, no
  post-processing. Budget: ≤ 24 slabs rendered; older slabs collapse
  into a single "＋N EARLIER" base slab. If WebGL is unavailable, or
  the device is low-power, or the user has reduced motion on, the
  fallback is a **CSS 3D isometric stack** (same slabs built from
  `transform: rotateX(60deg) rotateZ(-45deg)` divs) — and if CSS 3D is
  also unavailable, a flat 2D stepped-stack diagram with identical
  labels. The fallback shows the same information; the 3D never holds
  information hostage.
- **Interaction:** drag (pointer) or ←/→ keys rotate the stack ±25°
  around the vertical axis (transform only, eased, stops at the limits
  — no free spin, no auto-rotation); click / tap / Enter on a slab
  selects it and fills the evidence panel; hover lifts the slab 6px
  (translateY, transform only). A "RESET VIEW" button returns to the
  default angle. All 3D interactions have a text equivalent (the
  ledger table below the vault lists the same documents in the same
  order).
- **Loading / error / fallback:** the vault panel renders its 2D
  fallback immediately; the Three.js scene replaces it only after it
  loads successfully. If the script fails, the 2D fallback stays and
  no error wall appears. Reduced motion: static isometric render, no
  rotation, slabs appear instantly.
- **Mobile / performance:** the canvas is capped at the panel size
  (max ~520×420px desktop, full-width ~320px tall on mobile);
  `devicePixelRatio` capped at 2; no continuous render loop — render
  on demand (on interaction or state change) plus one render on load.
  No particles, no second canvas anywhere on the page.

## 10. Motion language (at least two techniques, transform + opacity only)

1. **Stamp slam (the verdict moment):** the verdict stamp enters with
   `scale(1.35) → scale(1)` + `opacity 0 → 1` + its final rotation,
   180ms, `cubic-bezier(0.2, 1.4, 0.4, 1)` (one overshoot, then dead
   still). It happens exactly once per verdict. This is the product's
   signature motion — a stamp hitting paper.
2. **Snap reveal (scroll):** panels and ledger rows enter with
   `translateY(14px) → 0` + `opacity 0 → 1`, 240ms, staggered 60ms
   per item via IntersectionObserver, unobserved after reveal. The
   easing is a hard `steps`-free ease-out — a snap, not a float.
   (Deliberately NOT PollPulse's slow float/rise and NOT NyayaLedger's
   clip-path mask reveal.)
3. **Micro:** buttons translate on hover/press (§8); the hash
   typewriter is per-character opacity only, ≤300ms total; the vault
   slabs lift on hover (translateY, §9). No other motion.
- **Rules:** animate `transform` and `opacity` only — never width,
  height, top, left, or box-shadow (shadow changes are instant).
  No continuous animation, no auto-rotation, no particles, no floating
  blobs, no ambient drift, no multiple canvases. Motion communicates
  cause-and-effect (you sealed it → the stamp lands; you scrolled →
  the evidence appears) and nothing else.
- **Reduced motion:** `prefers-reduced-motion: reduce` AND a visible
  **Low-motion toggle** (top bar, right) both disable all of the above:
  stamps appear instantly, reveals are off, vault is static, hash
  appears whole. Every workflow works identically without motion.

## 11. Responsive behaviour

- **Desktop (≥1024px):** 1200px grid; hero split 7/5; workbench two
  panels side by side; ledger full table; vault canvas ~520×420px.
- **Tablet (600–1023px):** hero stacks (headline, then vault panel);
  workbench stacks Seal above Verify; "How proof works" becomes one
  column of three panels; ledger scrolls horizontally inside its
  bordered panel (never breaks the page).
- **Mobile (<600px):** single column throughout; hero headline
  `clamp` floor 3rem; top-bar nav collapses to the four section buttons
  in a 2×2 grid under the logo block (no hamburger — four chunky
  buttons fit); drop zones full-width; verdict stamp scales to fit
  (max-width 100%, font clamps down); vault canvas ~320px tall.
- **No horizontal overflow anywhere** except the ledger's intentional
  inner scroll. Touch targets ≥44px. The stamp and the CTAs are never
  clipped.

## 12. Accessibility and reduced-motion behaviour

- Contrast: ink `#111111` on cream `#FFF3D6` ≈ 17.1:1; white on
  vermilion `#E8380D` ≈ 4.2:1 — verdict stamps are large display type
  (≥24px bold), which passes AA for large text, AND the verdict word
  is always accompanied by the full evidence table in ink-on-white, so
  no information is colour-only or contrast-only. White on teal
  `#0E7C6B` ≈ 5.1:1 (AA). Muted `#5C564A` on cream ≈ 6.6:1 (AA, near AAA).
  (Builder: verify with a real contrast check before claiming a pass;
  do not claim WCAG AA until measured.)
- Verdicts, states and errors are always words + colour, never colour
  alone. Hashes are text, selectable, copyable.
- Keyboard: full Tab order (top bar → hero CTAs → drop zones →
  workbench controls → vault slabs → ledger); visible gold focus
  outlines everywhere; vault slabs are focusable buttons with
  `aria-label` ("Document <name>, sealed <date>, verdict authentic");
  verdict region is `aria-live="polite"`.
- Forms: every input has a real `<label>` (CageCheck's missing-label
  gap is not repeated). Errors are announced and linked to their field.
- Reduced motion: §10 — OS preference + toggle, both kill all motion.
- No information is conveyed by motion, rotation, or 3D alone.

## 13. Design research — 5 references inspected 10 Nov 2026

All five were inspected on **10 Nov 2026** by opening the pages listed.
Where a page could not be opened, that is stated honestly below — no
reference is claimed as inspected when it was not.

### R1 — Proof / Notarize (same category: document notarization & trust)
- **URL:** https://www.proof.com/product/notarize
- **Inspected:** full product page (hero, "Faster, Simpler, Safer"
  checklist, Notarize Network stats, industry sections, compliance
  badges, Defend deepfake-detection section, screenshots of the signing
  workflow). Page crawled 10 Nov 2026, 05:07 UTC.
- **Learned:** trust is sold with *numbers and checkmarks*, not adjectives
  — "99.99% uptime, <1s wait, accepted in all 50 states" as a stat strip;
  the workflow is shown as real product screenshots, not illustrations;
  compliance is a badge row (SOC 2, IAL2, AATL, WebTrust, WCAG AA);
  identity verification is presented as layers (credential analysis +
  knowledge-based auth + biometric), which maps directly onto our
  evidence table (hash + timestamp + issuer + blob ID as layers of proof).
- **NOT to copy:** the soft corporate SaaS look (rounded cards, pastel
  checkmarks, stock photography of people on couches); the marketing
  page's length and testimonial filler; the "Notarize Now" funnel that
  hides the actual product behind signup — our product IS the page.
- **Translation:** a stat strip under the hero ("SHA-256 · WALRUS BLOB ·
  VERIFIABLE BY ANYONE · NO ACCOUNT"); the evidence table structured as
  Proof's layered-verification idea (one row per proof layer); a
  compliance-style badge row naming the real guarantees (client-side
  hash, content-addressed storage, public re-verification).

### R2 — Walrus Docs (same category: the storage/provenance layer itself)
- **URL:** https://docs.wal.app/llms.txt (Walrus documentation index;
  current docs host — docs.walrus.site is the same documentation)
- **Inspected:** the full docs index (system overview, core concepts,
  data security, HTTP API, TypeScript SDK, examples). Page crawled
  10 Nov 2026, 05:07 UTC.
- **Learned:** the mental model to teach the user in one line — "blobs
  are immutable byte arrays; the blob ID is derived from the content,
  so the ID *is* the proof"; erasure-coded slivers across shards (the
  vault metaphor, literally distributed); blobs are public by default
  and have a lifetime in epochs (honest limitation to state in the UI,
  not hide); aggregator (read) vs publisher (write) are different
  endpoints — our Verify path reads via aggregator, our Seal path
  writes via publisher, and the UI should say which it is doing.
- **NOT to copy:** docs-site aesthetics (dense text index, no visual
  hierarchy for a demo audience); the CLI-first framing — judges will
  not run a CLI; do not expose raw CLI commands as the primary UI.
- **Translation:** the "How proof works" band teaches the blob-ID =
  content-address model in three panels; the Seal receipt names the
  publisher and the Verify panel names the aggregator; the footer links
  the real Walrus docs; the vault stack visualises slivers-as-slabs
  (one document = one slab, distributed = stacked in a shared vault).

### R3 — Linear (exceptional interaction / motion)
- **URL:** https://linear.app/
- **Inspected:** homepage — hero ("The product development system for
  teams and agents"), live product UI rendered as the hero imagery,
  activity feed, issue lists, "Fig 0.1/0.2/0.3" feature panels.
  Page crawled 10 Nov 2026, 05:07 UTC. (Motion timing claims below
  come from Linear's documented design tokens as summarised in public
  design-system notes, not from a frame-by-frame inspection.)
- **Learned:** the hero shows the ACTUAL product working, not a
  picture of it — issues moving, activity updating; motion is fast
  (100–300ms), physical, and never decorative — a press is a
  `scale(0.97)`, a reveal is a 200ms fade-up with 50ms stagger;
  hierarchy is built by luminance and type, not by colour noise.
- **NOT to copy:** the dark near-black canvas and the single indigo
  accent (that is TapeOut Gate's and PollPulse's territory); the
  manifesto copy voice; the frosted/glowing panels.
- **Translation:** our hero shows the actual product working too — the
  Vault Stack is live, not a screenshot, and the first demo document
  is pre-sealed so the stack is never empty on first load; our motion
  budget copies Linear's discipline (fast, ≤300ms, purposeful) but
  with brutalist snap instead of Linear's soft ease; button presses
  use a small scale/translate, exactly as Linear does.

### R4 — The New York Times (strong typography / hierarchy)
- **URL (inspected):** https://www.webdesignhot.com/design.md/nytimes/
  — the published design-system documentation of nytimes.com
  (source_url https://www.nytimes.com). **Honest note:** nytimes.com
  itself was blocked by the fetch policy on 10 Nov 2026, so the live
  homepage was NOT directly inspected; the type system, tokens, scale,
  components, motion and accessibility values below come from this
  published design-system file, inspected in full (2,153 lines) on
  10 Nov 2026.
- **Inspected:** the full NYT design token file — Cheltenham display
  serif, Imperial body, Franklin Gothic labels; type scale from 11px
  micro-meta to 64px masthead; flat elevation (hierarchy from type
  weight and grid columns, never shadow); hairline rules as the only
  separators; one reserved red (`#d0021b`) for LIVE/breaking only;
  focus ring in link blue; reduced-motion behaviour (pulsing live dot
  becomes static).
- **Learned:** hierarchy can be carried by type scale and weight alone
  — masthead 64px → headline 56/44/36 → deck italic 18 → body 18 →
  byline 13 bold caps → micro-meta 11; a single reserved signal colour
  gains power by being used almost nowhere else; flat is a choice, and
  it reads as trust.
- **NOT to copy:** the serif editorial voice (Cheltenham/Imperial) —
  that is NyayaLedger's and TapeOut Gate's register, and a newspaper's
  dense multi-column river layout; the red — our reserved signal
  colour is vermilion, and it means TAMPERED, not "breaking news".
- **Translation:** our type scale is built the same way (display 900 →
  section 700 caps → body → mono evidence → 12px micro-labels), and
  our "one reserved colour" discipline is copied exactly — vermilion
  appears only for TAMPERED/danger/Seal-CTA, nowhere else; the
  evidence ledger's row rules and the byline-style micro-labels
  (uppercase, letterspaced, muted) are NYT's hierarchy idea rendered
  in brutalist form (thick rules instead of hairlines).

### R5 — three.js (3D / spatial / data-viz experience)
- **URL:** https://threejs.org/
- **Inspected:** homepage — the project gallery (200+ live WebGL
  projects as thumbnails: isometric rooms, configurators, data
  visualisations, games), docs/examples links, r187 release note.
  Page crawled 10 Nov 2026, 05:07 UTC.
- **Learned:** the strongest 3D on the web is *one scene, one idea* —
  an isometric baked room, a car configurator, a single data
  visualisation — not a world; the gallery proves flat-shaded,
  low-poly, orthographic/isometric scenes read clearly and run fast
  on ordinary hardware; the best examples are explorable (orbit,
  click) but never require exploration to understand the point.
- **NOT to copy:** the gallery-as-homepage (a wall of thumbnails with
  no hierarchy); heavy shader/particle showpieces; free-orbit cameras
  with no limits; any scene that needs a loading screen.
- **Translation:** the Vault Stack follows the "one scene, one idea"
  rule — a single orthographic isometric stack, flat-shaded boxes, no
  textures, no particles, rotation clamped to ±25°, render-on-demand;
  the baked-isometric-room example specifically informed the fallback
  choice (CSS 3D isometric slabs read almost identically to the WebGL
  version, so the fallback is not a downgrade).

## 14. Original design decisions (this project only)

- Neo-Brutalism chosen by explicit override of the Film Noir leaning,
  because the most recent project already owns Noir (§0).
- The verdict as a rotated rubber stamp — the loudest element on the
  page, and the only rotated element.
- Hard offset shadows instead of any blur/glow/gradient — the single
  most visible break from PollPulse and TapeOut Gate.
- The evidence board layout: chunky bordered panels in a strict grid,
  not a hero + card grid, not a broadsheet, not a single column.
- The Vault Stack: the ledger as an isometric stack of slabs, where a
  tampered document visibly breaks the stack — 3D as evidence, not
  decoration.
- Hashes shown in full mono with copy controls; nothing about the proof
  is hidden behind a tooltip or a truncated string.
- Honest limitations stated in the UI: blobs are public by default;
  storage lasts for epochs (state the real epoch behaviour from the
  build); verification proves the bytes are unchanged, not that the
  content is legally true — the UI must say so in one line under the
  verdict, so no judge mistakes a hash match for legal advice.
