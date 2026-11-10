# PROJECT DESIGN REGISTRY — NyayaSeal (Walrus Haulout, 10 Nov 2026)

Recorded so the next project can be checked against the last three (here,
four) and be recognisably different in more than accent colour. Rulebook
§1.3. Previous designs were read from their actual source files and
constitutions on 10 Nov 2026 — nothing below is from memory alone.

## The new project

### NyayaSeal — Walrus Haulout (10 Nov 2026)
- **Concept / metaphor:** the Evidence Board + the Rubber Stamp. Chunky
  bordered dossier panels pinned in a strict grid; the verdict is a
  physical stamp slammed onto the evidence. The ledger is an isometric
  stack of document slabs in a vault.
- **Palette:** dossier cream `#FFF3D6`, card white, ink `#111111`,
  seal vermilion `#E8380D`, vault teal `#0E7C6B`, seal gold `#FFB000`,
  vault blue `#2547F4`. Flat colour only — no gradients, no blur, no glow.
- **Typography:** Archivo Black (900, display/verdict) + Space Grotesk
  (UI/body) + IBM Plex Mono (hashes/evidence).
- **Layout:** sticky chunky top bar (logo block + button nav) → split
  hero (7/5, headline left, live Vault Stack right) → gold "How proof
  works" band (3 panels) → two-panel workbench (Seal / Verify side by
  side) → full-width evidence ledger table → ink footer.
- **Hero:** split hero, giant "PROVE IT. / OR IT DIDN'T / HAPPEN." with
  "PROVE IT." on a gold flat block; live 3D vault beside it.
- **Signature interaction:** the verdict stamp slam (rotated teal /
  vermilion stamp, 180ms overshoot) + click-a-slab-to-inspect in the
  Vault Stack + copy-every-hash controls.
- **Motion:** stamp slam + snap scroll-reveal (transform + opacity only).
- **3D:** "The Vault Stack" — Three.js, lazy, orthographic isometric,
  flat-shaded slabs, rotation clamped ±25°, render-on-demand; CSS 3D
  isometric fallback, then a flat 2D stepped stack. One canvas only.
- **Style:** Neo-Brutalism.

## Previous projects (as actually built / specified)

### NyayaLedger — HackCanton S4 (9 Nov 2026)
- **Source read:** `~/workspace/hackathons/hackcanton/nyayaledger/web.py`
  (CSS + markup) and `~/workspace/hackathons/hackcanton/design/DESIGN_CONSTITUTION.md`.
- **Concept:** a printed register / broadsheet — a book of record.
- **Palette:** paper `#fafaf7`, ink `#111110`, signal red `#d42b1e`,
  hairline `#d8d8d0`, amber local-adapter badge. No gradients, no glass.
- **Typography:** Helvetica grotesk (system stack), uppercase display,
  system monospace for hashes/receipts. No webfonts.
- **Layout:** full-bleed masthead + kicker lines + 5-column lifecycle
  strip + numbered sections (01–05) + full-width ruled table. One route,
  no sidebar, no hero split.
- **Hero:** giant uppercase "NYAYA—LEDGER" (clamp up to 7.5rem) with a
  clip-path mask reveal.
- **Signature interaction:** role bar (Issuer/Verifier/Holder/Auditor)
  re-rendering the action panel; hash-chain verify button.
- **Motion:** mask reveal + scroll-reveal stagger (transform/opacity).
- **3D:** none on Day 1 (stated gap); lifecycle strip is the spatial
  element.

### TapeOut Gate — OKX TapeOut Accelerate (9 Nov 2026)
- **Source read:** `~/workspace/hackathons/okx-tapeout/design/DESIGN_CONSTITUTION.md`
  and `~/workspace/hackathons/okx-tapeout/design/DESIGN_REGISTRY.md`.
- **Concept:** a night-desk security guard — desk lamp + signal lamps +
  paper receipt. (Cinematic / Film Noir.)
- **Palette:** night `#0b0a08`, desk `#14120e`, paper `#e8e2d4`, dim
  `#9a937f`, line `#3a332a`, lamp amber `#e8a33d`, alarm red `#e5484d`,
  clear green `#4cc38a`. Dark; amber spotlight gradient.
- **Typography:** Georgia serif (display + body) + ui-monospace
  (labels/receipts). Verdict letters stagger in (kinetic typography).
- **Layout:** single centred column, max 880px, three numbered beats
  (paste → verdict → receipt) + onchain coda. One scroll, no tabs, no
  sidebar.
- **Hero:** "The night desk for onchain agents." with amber spotlight.
- **Signature interaction:** signal-lamp pills (ALLOW/HOLD/BLOCK, one
  lit at a time); kinetic verdict stagger (45ms per letter).
- **Motion:** scroll reveal + stagger; kinetic verdict typography.
- **3D:** deliberately minimal in v1 — depth from the spotlight, no
  3D scene. (A later 3D element would be one object only.)

### PollPulse — TanStack Start × Convex (10 Nov 2026)
- **Source read:** `~/workspace/hackathons/tanstack-pollpulse/src/styles.css`
  (full file).
- **Concept:** live polls on a deep-indigo night sky. Glassmorphism.
- **Palette:** deep indigo `#0a0f2e` → `#141031` gradient background,
  fuchsia `#d946ef` / cyan `#22d3ee` radial orbs, glass panels
  (`backdrop-filter: blur(18px)`), gradient text (fuchsia → indigo →
  cyan), near-white text `#f4f6ff`.
- **Typography:** system sans (`ui-sans-serif, system-ui, …`); gradient
  text for display.
- **Layout:** glass cards over a fixed gradient sky; staggered card
  entrance; live result bars growing by scaleX.
- **Hero:** glass hero over glowing orbs (gradient + blur treatment).
- **Signature interaction:** live voting with animated result bars;
  floating ambient orbs.
- **Motion:** rise-on-enter (0.7s), slow ambient orb float (9s infinite),
  bar-fill scaleX transitions. Transform + opacity only.
- **3D:** none (depth from glass/blur/orbs, not a scene).

### CageCheck — SafeSpace / Vultr lineage (3 Nov 2026; serverless 10 Nov 2026)
- **Source read:** `~/workspace/hackathons/cagecheck/design/DESIGN_CONSTITUTION.md`.
- **Concept:** a border inspector's stamp desk — cage + stamp + receipt.
- **Palette:** paper `#F7F4ED`, ink `#1A1A18`, stamp red `#B42318`,
  stamp green `#1F6B3A`, stamp amber `#8A6D00`. No gradients, no glass,
  no dark mode.
- **Typography:** Georgia serif headings + Inter/system sans body +
  ui-monospace receipts/stamps. No webfonts (no CDN).
- **Layout:** single column, centred, max-width 720px. h1 + tagline →
  dashed cage card → paste box → buttons → stamp + receipt → small
  links. No nav, no sidebar, no dashboard grid.
- **Hero:** plain "CageCheck" h1 + one-line tagline (no hero treatment).
- **Signature interaction:** circular rotated stamp (PASSED / HELD /
  BLOCKED) + monospace JSON receipt slip.
- **Motion:** none in the built UI (stamp simply appears).
- **3D:** planned only, not implemented (CSS 3D cage view proposed).

## Comparison — NyayaSeal vs the previous four

| Dimension | NyayaLedger | TapeOut Gate | PollPulse | CageCheck | **NyayaSeal** |
|---|---|---|---|---|---|
| Style | Swiss / Editorial | Film Noir | Glassmorphism | Stamp-desk (paper) | **Neo-Brutalism** |
| Canvas | Light paper `#fafaf7` | Near-black `#0b0a08` | Dark indigo gradient | Warm paper `#F7F4ED` | **Light cream `#FFF3D6`, flat blocks** |
| Accent logic | One signal red | One lamp amber | Fuchsia/cyan gradient | Stamp red/green/amber | **Vermilion + teal + gold, each reserved to one meaning** |
| Display type | Helvetica grotesk, uppercase | Georgia serif, light | System sans, gradient text | Georgia serif | **Archivo Black 900, uppercase** |
| Borders | 1px hairlines | 1px lines | 1px glass borders + blur | 1px grey / dashed cage | **3px ink + hard offset shadows** |
| Shadows | None | Spotlight glow | 18px blur + orbs | None | **Hard `6px 6px 0 ink` only** |
| Layout | Masthead + numbered sections + ruled table | Single 880px column, 3 beats | Glass cards over sky | Single 720px column | **Sticky bar + split hero + 2-panel workbench + ledger** |
| Hero | Giant masthead, mask reveal | Lamp-lit headline, kinetic verdict | Glass hero, floating orbs | No hero (h1 + tagline) | **Split hero, gold-block headline + live 3D vault** |
| Signature interaction | Role bar re-render | Signal lamps + kinetic verdict | Live vote bars + orbs | Circular stamp + receipt | **Stamp slam + slab inspection + copy-every-hash** |
| Motion | Mask reveal + stagger | Scroll reveal + kinetic type | Rise + 9s orb float | None | **Stamp slam + snap reveal** |
| 3D | None | None (spotlight only) | None (glass depth) | Planned only | **Vault Stack (Three.js iso, CSS 3D + 2D fallback)** |

## Verdict

NyayaSeal is recognisably different from all four predecessors in
**concept** (evidence board + stamp vs register vs night desk vs glass
polls vs stamp desk), **palette** (flat cream/vermilion/teal/gold vs
paper+red, night+amber, indigo gradient, paper+stamp colours),
**typography** (Archivo Black 900 poster type vs Helvetica grotesk,
Georgia serif ×2, system sans), **layout** (split hero + two-panel
workbench vs broadsheet sections, single columns ×2, glass cards),
**hero** (gold-block headline + live vault vs masthead, lamp headline,
glass hero, no hero), **signature interaction** (stamp slam + slab
inspection vs role bar, signal lamps, vote bars, circular stamp),
**motion** (slam + snap vs mask, kinetic type, orb float, none), and
**3D** (a real isometric vault stack vs none/planned-only in all four).

No hero treatment, card grid, sidebar, gradient, glass panel, spotlight,
hairline-table, or single-column layout is reused from any previous
project. The only deliberately shared DNA is engineering-level, not
visual: client-side hashing honesty, mono evidence text, a low-motion
toggle + `prefers-reduced-motion`, and transform+opacity-only motion.
**UI distinctiveness: PASS** under rulebook §1.3. Gate A design half
is satisfied by this registry + `DESIGN_CONSTITUTION.md`.
