# EP13 — QC (round 2, G2 6-second proof)

Everything in this file was produced by a command in `RUNBOOK.md`. Where a number is
not available, the row says **NOT MEASURED** instead of guessing.

Machine: this sandbox, CPU only. Pillow 9.5.0 / numpy 2.4.6 / uharfbuzz 0.57.0 /
freetype-py (FT 2.13.2) / imageio-ffmpeg 9.0.2.

---

## 1. G0 — asset verification

| Check | Command | Result |
|---|---|---|
| Handoff integrity | `sha256sum -c SHA256SUMS.txt` in `episode/ep13/spec` | **37 / 37 OK** |
| Handoff preflight | `preflight.py` | 7 FOUND, 5 MISSING (all 5 resolved here — see below) |
| Narration take | `sha256sum public/ep13/audio/chapter01.mp3` | `83be0fd3…09e8` — matches the take referenced by the handoff |
| Official logo | `sha256sum public/ep13/brand/logo.svg` | `267e5bd1…a204f` — unmodified, never re-traced |
| Fonts | `public/fonts/` | Amiri (Regular/Bold), IBM Plex Sans Arabic (Regular/Medium/Bold) |

The five items `preflight.py` reports missing are the ones the handoff itself declares
absent, and their disposition is:

| Handoff item | Disposition |
|---|---|
| `VOICE_S01` | **found** in this repo — `public/ep13/audio/chapter01.mp3`, hash-verified |
| `LOGO_RUWAQ` | **found** — `public/ep13/brand/logo.svg` |
| `FISH_SEPARATE` | **not supplied, not faked** — built as a 2.5-D vector sprite in code |
| `GLASS_SEPARATE` | **not supplied, not faked** — built as a 2.5-D vector sprite in code |
| `MEDICAL_MODEL` | out of scope for 0–6 s; no medical claim is visualised in the proof |

No asset was downloaded from the internet this round. The reference video was used for
design grammar only; **not one frame of it appears in the render**.

## 2. Audio is the original take and is locked at 0 ms

The proof MP4's audio track was decoded to 48 kHz mono and compared with the first
6.000 s of `chapter01.mp3` decoded the same way:

| Metric | Value |
|---|---|
| Samples compared | 288 000 + 288 000 (6.000 s each) |
| Best cross-correlation lag | **0 ms**, r = **1.0000** |
| Max sample difference | 200 / 32768 ≈ 0.6 % — AAC re-encode only |

So the narration is bit-faithful in alignment: nothing was stretched, shifted or
re-timed. The video is laid out *on top of* the voice, not the other way round.

Speech runs measured from the same file (`episode/ep13/measured_audio.json`):
0.12–1.66, 2.08–2.78, 3.24–5.04, 5.46–… s. The 0–6 s cut therefore covers P1, P2, P3
and the onset of P4 exactly.

## 3. Motion is authored, not a camera push

Two full 180-frame passes were rendered: **camera on** and **camera off**
(`--camera-off` sets `Camera.enabled = False`, so only the elements move).
Mean absolute RGB difference between consecutive frames, inside a fixed screen region:

| Region (1280×720 box) | camera on | camera off | frames moving | S1a fish 0–21 | S1b 22–53 | S2 54–90 | S3 91–179 |
|---|---|---|---|---|---|---|---|
| fish body (250,425)–(425,505) | 1.92 | 1.86 | 179/179 | 3.56 | 1.61 | 2.09 | 1.57 |
| fish tail (185,420)–(250,520) | 1.62 | 1.56 | 179/179 | 2.04 | 1.56 | 1.90 | 1.43 |
| glass + milk (855,400)–(955,505) | 5.21 | 5.06 | 179/179 | 7.77 | 1.62 | 3.07 | 6.79 |
| claim card (620,400)–(960,570) | 3.21 | 3.14 | 179/179 | 3.38 | 1.39 | 3.31 | 3.77 |
| headline (338,160)–(950,235) | 1.86 | 1.85 | 179/179 | 2.34 | 2.01 | 1.84 | 1.70 |
| background dust control (60,210)–(170,270) | 1.15 | 1.15 | 179/179 | 1.13 | 1.16 | 1.14 | 1.16 |

Reading: the camera contributes **0.04–0.17** of the mean delta — i.e. the motion is
the elements, and removing the push changes almost nothing. The background control
region moves at a steady 1.15 (dust drift + grain), which is the intended floor of
"nothing is frozen".

**Frozen pairs: 0** in both passes (no two consecutive frames are identical).

Note on the fish: it is articulated (tail / dorsal / pectoral, travelling sheen) only
during S1a — after it settles on the plate it holds with micro-motion, which is why its
phase deltas fall from 3.56 to 1.6. That is a deliberate hold, not a stall.

## 4. Type legibility, including at phone size

Contrast spread inside the type box (p95−p5 luminance), full size and after a 25 %
downsample (≈320 px wide, i.e. how the proof looks in a phone feed):

| Frame | Headline full | Headline @25 % | Kicker @25 % | Gold word full | Gold word @25 % |
|---|---|---|---|---|---|
| 0 | 6 | 5 | 2 | 5 | 3 |
| 20 | 206 | 143 | 85 | 30 | 22 |
| 54 | **217** | **206** | 85 | **214** | **173** |
| 70 | 63 | 59 | 2 | 62 | 49 |
| 120 | 148 | 120 | 3 | 151 | 153 |
| 179 | 18 | 16 | 3 | 5 | 3 |

`6` / `2` / `3` mean *no type in that box at that frame* (f0 before the reveal, f179
after the cards have left). Type holds ≥ 85 % of its full-size contrast at 25 % scale,
so the Arabic survives a phone feed. Word order, ligatures and the gold stress word were
inspected at 4× zoom (`render/ep13/STYLEFRAME_A_1920.png`).

## 5. Frame health

| Metric | Value | Meaning |
|---|---|---|
| Mean luminance, all 180 frames | min **14.08**, max **21.89** (0–255) | no black frame, no flash frame |
| Border strips (top/bottom/left/right) | 2.4–14.0 | nothing is clipped hard at the edges |
| Frozen pairs | 0 | every pair of frames differs |
| Render time | ~2.4 s / frame at 2560×1440 internal | 180 frames ≈ 7 min on this CPU |

## 6. Palette discipline

Share of pixels matching each hue family:

| Frame | gold | cyan | coral |
|---|---|---|---|
| 20 | 1.54 % | 30.0 % | 0.36 % |
| 54 | 1.78 % | 28.7 % | 0.44 % |
| 120 | 2.03 % | 24.0 % | 0.34 % |
| 179 | 0.27 % | 34.2 % | 0.02 % |

Gold stays under ~2 % (it is the stress word, the arc, the dots and the card keyline —
never a fill). Cyan and coral appear only as the two light pools and the rim light.
`cyan_pct` is inflated by counting the whole navy field as cool; the pools themselves
are the only saturated sources.

## 7. What is honestly not done

| Item | Status |
|---|---|
| Native Arabic listen of the whole take | **NOT DONE** — needs a human with the language |
| Word-level sync (Arabic speech) | **NOT CLAIMED** — only phrase onsets are measured |
| 3-D geometry for fish / glass | **NOT CLAIMED** — 2.5-D vector sprites, see STATUS §5 |
| Refraction / real glass optics | **NOT DONE** — the glass is gradient + rim, not a ray-traced medium |
| 30 s segment, full episode | **NOT STARTED** — blocked on your visual approval |
| Logo animation | **NOT IN THIS PROOF** — the official SVG is untouched and unused here |

## 8. Known visual defects (my own criticism, at 1920)

1. **The fish reads as an illustration, not a photograph.** Silhouette and rim light
   work at 1280; at 1920 the eye and the fins show their vector origin.
2. **The glass reads as a frosted tumbler.** The milk column and the dark air gap above
   it are correct, but there is no refraction at the rim, and the base ellipse is soft.
3. **The plate's cast shadow is heavier than the light on the plate.** It reads as a
   soft blob rather than a contact shadow at 1920.
4. **The claim card is a dark slab** on a dark field: at 1280 it works, at 25 % scale it
   loses its top edge (the gold keyline carries it).
5. **Frame 0 is very dark** (mean 14/255) because the stage tile fades up from f2. If you
   want content at 0.00 s exactly, move the tile fade to start at f0.
6. **0.5 s of spark particles** at the arc break (f56–76) is one beat shorter than the
   break itself, so two or three specks can read as dust.

Composition-level comparison with the reference sits in
`docs/ep13/QC_REFERENCE_COMPARISON.jpg` — the grammar matches (navy field, glass stage
tile with dot pagination, tilted glass cards, rim light, one gold accent); the content
density does not (the reference is a product UI with real screenshots; ours is a claim
being examined, and we deliberately do not fake a source).
