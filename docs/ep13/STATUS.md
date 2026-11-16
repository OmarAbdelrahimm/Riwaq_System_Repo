# EP13 — STATUS (round 2: G0 verification → G1 styleframes → G2 6-second proof)

| | |
|---|---|
| Episode | 13 — «إوعى تشرب لبن بعد السمك» (the fish-and-milk claim) |
| Round | 2 — asset verification + two styleframes + first 6-second motion proof |
| Branch | `arena/04ab0678-riwaq-system-repo` |
| Gate | **G2 delivered — awaiting visual approval. G3/G4 NOT started.** |
| Date | 2026-11-16 |

Nothing beyond 6.00 s was rendered. No 30-second segment, no full episode, no
publication — per the standing instruction.

---

## 1. What exists now

| Deliverable | Path | Notes |
|---|---|---|
| 6-second proof, 30 fps | `render/ep13/PROOF_0_6_v2.mp4` | 1280×720, H.264, 6.00 s, original S01 take muxed from 0.00 s |
| Contact sheet | `render/ep13/PROOF_CONTACT.jpg` | frames 0 / 20 / 40 / 60 / 90 / 120 / 150 / 179 |
| Styleframe A (hook) | `render/ep13/STYLEFRAME_A_1920.png` | 1920×1080, frame 54 |
| Styleframe B (claim) | `render/ep13/STYLEFRAME_B_1920.png` | 1920×1080, frame 150 |
| Reference comparison | `docs/ep13/QC_REFERENCE_COMPARISON.jpg` | reference vs ours at three matching beats |
| QC | `docs/ep13/QC.md` + `render/ep13/QC_REPORT.json` | measured, not asserted |
| Asset manifest | `docs/ep13/ASSET_MANIFEST_UPDATED.json` | 21 assets + 11 code files, sha256 of each |
| Code | `tools/ep13/*.py` | 11 modules, no browser, no Remotion |
| Commands | `docs/ep13/RUNBOOK.md` | exact, reproducible |

The 180 source PNGs live in `render/ep13/frames_v2/` (187 MB, git-ignored —
regenerate with one command; see RUNBOOK §5).

## 2. Gate status

| Gate | Requirement | State |
|---|---|---|
| G0 | assets verified, provenance known | **PASS** — 37/37 handoff checksums, audio + logo hashes match, 5 handoff gaps resolved (see `QC.md` §1) |
| G1 | two styleframes, 1920×1080, Arabic set in code | **DELIVERED** — A/B above |
| G2 | 6 s, 30 fps, 2 grounded heroes, ≥2 depth planes, kinetic Arabic, one motivated transition, contact sheet | **DELIVERED — awaiting your judgement** |
| G3 | 30-second segment | **BLOCKED** on G2 approval |
| G4 | full episode | **BLOCKED** |

## 3. The 6 seconds, beat by beat

| Frames | Time | What happens | Why |
|---|---|---|---|
| 0–20 | 0.00–0.67 s | dark stage; glass stage-tile + dot pagination fade up, plate and fish enter, camera starts a 2 % push | measured P1 onset is 0.12 s — the stage must be alive before the voice |
| 4–34 | 0.13–1.13 s | headline «إوعى تشرب لبن بعد السمك» assembles word by word, «لبن» in gold | one gold stress word only |
| 28–46 | 0.93–1.53 s | gold connector arcs from the fish to the glass | the claim's two nouns are physically linked |
| 54–76 | 1.80–2.53 s | the arc breaks into a «؟»; the claim card rises | P2 onset 2.08 s → the question arrives on the word |
| 91–150 | 3.03–5.00 s | claim card travels forward, two muted echo cards stack behind it; a new line «سمعتها قبل كده» sets up the repetition idea | P3 onset 3.24 s |
| 164–179 | 5.47–5.97 s | cards recede and dissolve; an evidence card («المصدر قيد التحقق») slides in from the right | motivated transition into the next shot, not a fade |

## 4. Measured vs claimed

| Claim | Status |
|---|---|
| 6.00 s, 30 fps, 180 frames, 1280×720 | **measured** (ffprobe) |
| Audio is the original take, locked at 0 ms | **measured** (cross-correlation 1.000 at 0 ms, see `QC.md` §2) |
| Phrase onsets follow the voice | **measured** from the file (speech-run detection) |
| Motion is authored, not a camera push | **measured** (camera-off control pass; see `QC.md` §3) |
| Arabic is shaped correctly (HarfBuzz, RTL order) | **rendered + inspected** at 1×, 0.25× and 4× zoom |
| Word-level lip/word sync | **NOT claimed** |
| Native Arabic listen of the whole take | **NOT done** — needs a human |
| 3-D geometry for the fish and glass | **NOT claimed** — they are 2.5-D vector sprites (§5) |

## 5. Declared limitation (non-negotiable to state)

There is no separate fish or glass 3-D asset in the source material, and none was
faked from the reference. Both heroes are **procedural 2.5-D vector sprites** built
from Bézier silhouettes, gradient fills, rim light and a floor reflection
(`tools/ep13/heroes.py`). Consequences:

* they cannot be orbited, and the camera may only push/pan a few percent;
* no true perspective deformation on the heroes — their tilt is a shear, not geometry;
* a 3-D pass would need an actual GLB (or a modelling budget) — not in scope here.

This is why the proof is a **motion/art-direction** test, not a rendering-technology test.

## 6. Decisions taken this round (reversible)

1. **Glass stage-tile + dot pagination.** The reference's signature is a rounded glass
   tile holding the hero, with dot pagination beneath. Round 1 had the heroes floating on
   an empty field; the tile is now in every frame of S1–S2 and reads as the RUWAQ stage.
2. **Cards, not bubbles.** The claim is a tilted glass card with a label / title / footer
   (`قول شعبي متكرر` / `هيجيلك بهاق؟` / `بلا مصدر طبي`), stacked with muted echoes rather
   than a pile of equal cards.
3. **Honest evidence card.** `بطاقة دليل` + `المصدر قيد التحقق` + `لا نعرض مصدرًا غير
   موثّق` — no invented citation, no fake screenshot, no government logo.
4. **No talking head.** None in 0–6 s, as instructed.

## 7. What I need from you to proceed (G3)

Please answer with approve / change:

1. **Palette** — the approved brand core plus cyan `#47B8CC` and coral `#E48672`, used
   *only* in the two light pools and rim light, never in type, logo or fills. Sign off or
   give me the corrected values.
2. **The glass stage-tile** — keep it as the identity carrier, or return to the free-floating
   stage of round 1?
3. **Hero treatment** — is a 2.5-D stylised fish + glass acceptable for the episode, or do
   you want a 3-D asset sourced/budgeted before any further animation?
4. **Motion rhythm** — is the 1.8 s hold on the hook too long, and is the 0.5 s evidence
   slide-in long enough for the next cut?
5. **Type** — the display face is Amiri (Naskh, calligraphic) at 96 design px; the UI face is
   IBM Plex Sans Arabic. Confirm or replace before we set the whole episode.

Once you approve, G3 is the 30-second segment (`config/scenes_0_30.json`, S01–S10) using
the same renderer, same tokens, same timing method — nothing re-invented.
