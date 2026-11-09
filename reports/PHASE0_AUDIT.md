# PHASE 0 — AUDIT REPORT
## RUWAQ | 1816: The Year Summer Disappeared — final publishable cut
Auditor: production lead · Date: 2026-11-09 · Branch: `arena/679e0e02-riwaq-system-repo`
Status: **Phase 0 complete. Nothing generated, nothing rendered. Waiting for your OK.**

---

## 0. Executive summary — 4 blockers before Phase 2 can produce a publishable frame

| # | Blocker | Impact | Fix (needs your decision) |
|---|---|---|---|
| **B1** | **The locked master is not the file described in the brief.** `master_vo_LOSSLESS.flac` on Drive measures **675.08 s**, not 626.37 s. | Every window in CHAPTER_MAP, every shot timecode in SHOT_LIST (b0.070 s → 626.25 s) and every word anchor is mapped to a 626.37 s timeline. 48.7 s of audio with no planned picture. | Pick one: (a) the 626.37 s version exists elsewhere — send the file; (b) trim **1.2 s of silence from 28 gaps** (first fit, ends at 626.35 s) and I rebuild all timings; (c) keep 675.08 s and I re-map all 15 scenes (adds ~50 s of picture). Cannot be decided silently. |
| **B2** | **Images come back at 1376×768 (1.06 MP), not "at least 3840 px wide".** The image route in this sandbox caps there. | 2.5D push-ins and parallax at 1080p need ≥2× oversample. From 1376×768 a 1080p crop is **1.78× upscale** → soft, breaks the "no flat AI look / stays sharp" rule. | I do **not** silently ship upscales. Options: accept a 1080p-safe crop with a hard cap on push-in (≈1.1×) and no parallax oversample → visibly compromised; or you approve a 2× upscale-and-regrain pipeline (honest, documented, still soft on edges); or you allow me to source public-domain plates for the hero establishing shots only. **My recommendation: (b) + restrict parallax to 1.06–1.10×, and reserve the 3 hero moments (opening field, atmosphere cutaway, Villa Diodati) for a second generation pass at a higher-res route if you can enable one.** |
| **B3** | **No Remotion/Chromium video render path.** `remotion browser ensure` is blocked (TLS reset to `remotion.media`). I installed a standalone Chromium shell, but **Remotion cannot drive it**, and the repo's own `Episode` composition crashes at frame 45 (`inputRange must be monotonically increasing [125,0]` — `src/engine/timing.ts:16`). No GPU (no CUDA, no Vulkan), 2 vCPU, 3.8 GB RAM, no swap. | The brand's documented engine (Remotion + GitHub Actions) is not usable here as-is. | I propose an FFmpeg-native pipeline: headless Chromium screenshots the **motion-graphics layer only** (maps, thread, stamps, Arabic type — verified working), FFmpeg composites 2.5D plates, grade, grain, particle passes and the audio mix. Motion graphics still come from the same brand tokens. **Measured:** 124 ms/frame (1920×1080 JPEG), 378 ms/frame (PNG+alpha). Approve or redirect. |
| **B4** | **The repo has no logo files.** `brand.json` points to `assets/riwaq-icon-gold.svg`, `riwaq-horizontal-*.svg`, `riwaq-watermark-gold.svg` — none exist in the repo. | The "transparent logo, no rectangle behind it" rule is unenforceable until the vector exists. | I found `riwaq-icon-gold-ink.png` (512×512, RGBA, transparent) on Drive and can use it as the icon. **You need to give me the four SVGs** (horizontal/stacked × light/dark + watermark) for the end card. |

Everything else in this report is measured fact. Where I could not measure, I say so.

---

## 1. What I read

**Repo (`Riwaq_System_Repo`, 62 files, no media):** `README.md`, `ASSETS_LICENSE.md`, `package.json`, `remotion.config.ts`, `data/brand.json` (full token dump), `data/voice_profiles.json`, `data/projects/GOLDEN_001/episode_meta.json`, `05_Template_Kit/{AGENT_PROMPT,NAMING,brand}.{md,json}`, `05_Template_Kit/episode_meta.schema.json`, `docs/{RUNBOOK,GITHUB_SETUP}.md`, `scripts/{qc,make_srt,make_props,pitch_match,voice_finish}.py`, `src/engine/*`, `src/compositions/Episode.tsx`, all 11 `src/components/*`.

**Drive — the 1816 branch actually in use** (`1816 Ep/1816/`):
- `01_FINAL_SCRIPT_v2.md` (56 KB) and `01_FINAL_SCRIPT_v3.md` (55 KB) — **two scripts, different scene windows.** v3 is newer and its scene 1 runs 0:00–0:32.65, while the approved shot list's scene 1 ends at 0:32.65 too but the shot list's scene 2 starts at 0:32.79. They agree on scene order; they disagree on durations after scene 5.
- `02_Audio_Master_and_Clips/` — `master_vo_LOSSLESS.flac` (46.99 MB), 12 TTS clip WAVs (`01.wav`…`13-15.wav`), `master_vo_part1/part2.wav`.
- `03_Motion_HTML_and_Timestamps/` — `vo_timestamps_REAL.json` (252 KB, 1032 words, faster-whisper large-v3-turbo), 10 motion HTML modules `M1…M10` (~80 KB each), `render_frames.py`, `motion_README.md`.
- `04_Subtitles/` — `RUWAQ_1816_AR.srt` (15 KB), `RUWAQ_1816_EN_draft.srt`.
- `05_Reports_QA/` — `audio_sanity.md`, `audio_sanity_findings.json`.
- `09_FinalCut_APPROVAL/` — `SHOT_LIST.csv` (164 rows), `SHOT_LIST.md`, `shotlist.json`, `00_APPROVAL_PACKAGE.md`, `RUWAQ_1816_FINALCUT_APPROVAL_PACK.zip`.
- `01_Script_and_SEO/02_VISUAL_BIBLE.md` (32 KB) — not yet cross-read against the shot list; will be in Phase 1.
- `08_Rendered_MP4/RUWAQ_1816_v4_ROUGHCUT.mp4` — **the rejected rough cut. I will not open it for design reference**; only its narration and scene order survive, per your instruction.

**Drive — assets I inventoried but will not regenerate:** brand icon PNGs/SVGs (`riwaq-icon-*`, `riwaq-logo-*`, `riwaq-watermark-*`), `RIWAQ_ORIGINAL_PROCEDURAL_SCORE.mp3` (4.8 MB), `RIWAQ_EPISODE_ORIGINAL_VOICEOVER.mp3`, `RIWAQ_EXPANDED_PAPER_ASSETS.zip` (50 MB), `RIWAQ_PAPER_COLLAGE_AND_CUTOUTS.zip` (17 MB), `sfx_manifest.csv`, `MUSIC_LICENSE_REGISTER.md`, `R8_AUDIO_VISUAL_EVENTS_UNVERIFIED.json`, `RIWAQ_EDITORIAL_SCENE_TABLE_AR.md`.

**Explicitly missing from Drive (I must generate or you must send):** any approved hero stills, any depth maps, any parallax clips, any storm/lightning plate, the four logo SVGs named in `brand.json`.

---

## 2. Drive inventory — measured

| Asset | Type | Measured spec | Status |
|---|---|---|---|
| `master_vo_LOSSLESS.flac` | audio | 48 kHz · **stereo** · 24-bit · **675.08 s** · **−16.5 LUFS integrated** · **true peak −1.0 dBTP** · LRA 8.2 LU | ⚠ duration conflict (B1) |
| `04.wav` (TTS clip) | audio | 24 kHz · **mono** · 26.64 s | ⚠ source clips are mono/24 k — the master is an up-mixed assembly, not a clean 48 k recording |
| `vo_timestamps_REAL.json` | data | 1032 words, 493.6 s pure speech, 1.529 w/s overall, 2.091 w/s in-speech, 21 low-confidence words | usable, but see §5 |
| `SHOT_LIST.csv` | data | 164 rows × 15 cols | conditionally approved |
| `RUWAQ_1816_AR.srt` | captions | 15 KB | usable as base, must be re-timed |
| `riwaq-icon-gold-ink.png` | image | 512×512 RGBA, alpha 0–255 (true transparency) | ✅ usable as icon |
| `RIWAQ_ORIGINAL_PROCEDURAL_SCORE.mp3` | audio | 4.8 MB | ✅ exists, do not regenerate |
| `M1…M10_*.html` | motion | ~80 KB each, self-contained | ✅ exists, may be reusable |

**Nothing visual for the film exists yet.** No stills, no plates, no depth maps, no particle passes.

---

## 3. Environment — measured, not assumed

| Item | Measured |
|---|---|
| CPU | Intel Xeon @ 2.60 GHz · **2 vCPU** |
| RAM | **3.8 GB total**, 3.6 GB available, **no swap** |
| GPU | **none** (no `nvidia-smi`; FFmpeg has no usable device; Remotion forces SwiftShader) |
| Disk | 21 GB total, 20 GB free |
| `/dev/shm` | 2.0 GB |
| Node / npm | v22.22.3 / 10.9.8 · `npm install` OK (260 pkgs) |
| FFmpeg | **v9.0.2 static**, `libx264`, `libass`, `libharfbuzz`, `libfribidi`, `libfreetype`, `fontconfig`, `zoompan`, `drawtext`, `gblur`, `vignette`, `noise`, `curves`, `geq` ✅ |
| ffprobe | **absent** in that build (probe via `ffmpeg -i`) |
| Chromium | ✅ standalone headless shell (Chrome 131) + puppeteer-core, launched with `LD_LIBRARY_PATH` shim |
| Remotion | ❌ **cannot render** — browser download blocked (`ECONNRESET` to `remotion.media`); own composition crashes at frame 45 |
| Arabic shaping | ✅ **verified on a rendered frame** — Amiri + IBM Plex Sans Arabic, correct RTL joining, correct ١٨١٦ glyphs (see `audit/ar_test.png`) |
| Python | 3.11 venv: numpy 2.4.6, Pillow 13.0.0, imageio-ffmpeg, brotli, puppeteer path |
| WhisperX / wav2vec2 CTC | ❌ cannot install/run (no torch, 3.8 GB RAM, no GPU) |
| Image generation | 3840-px prompt → **1376×768 output** (1.06 MP) |
| Render speed (measured) | screenshot 1920×1080 JPEG **124 ms/frame**, PNG+alpha **378 ms/frame**; FFmpeg 10 s of 1080p30: 1-layer push-in **23.7 s**, +grain plate **34.4 s**, 2-layer parallax+grain **60.6 s** |
| Extrapolation at those rates | 626 s × 30 = 18,780 frames → single-layer ≈ **12.4 h**; 2-layer parallax ≈ **31.6 h**; motion-graphics overlay pass on top ≈ **+2 h**. **Not hours — days, on this box.** Must be staged chapter by chapter. |

---

## 4. Brand rules found (and where each comes from)

**Palette (locked, `brand.json → theme.colors`, with max in-frame ratios):** `ink_deep #1C1B19` (≤70 %), `ink_second #242218` (≤10 %), `parchment #F3EBDB` (≤25 %), `parchment2 #EDE6D6` (≤20 %), `gold #A98A4B` (≤8 %), `gold_light #C2A469` (≤2 %), `gold_pale #EFE6D2` (≤5 %), `burgundy #5E2230` (≤5 %), `stone #8A7F6B` (≤5 %), `stone_light #B9AE94` (≤2 %). `palette_lock: true`.
**Type:** Amiri 400/700 (headline, quotes, big numbers, end screen) · IBM Plex Sans Arabic 400/500/700 (captions, lower thirds, sources, CTA). **Forbidden: Cairo, Inter, system-ui-as-a-design-choice.** Min legible 28 px.
**Captions:** ≤2 lines, ≤28 Arabic chars/line, keywords gold_light (≤3 words), numbers always highlighted, never cover a face.
**Motion:** one ease curve `cubic-bezier(.2,.8,.2,1)`; text in 380 ms / out 280 ms / rise 12 px; Ken Burns 1.00→1.06; cut rhythm default 3.5–6.0 s, hook 1.5–2.5 s; transitions **hard cut + fade 200 ms only**; **forbidden: flash, whip, spin, bounce, zoom-punch**.
**Look:** paper texture soft-light 10 %, grain 0.12, vignette 0.18, bloom 0.10.
**Logo:** `max_width_px 130`, clear space = half the arch height each side, **no gradients, no shadows, no 3D, no re-lettering**, gold_light dot. **Watermark:** top-center, 72 px, opacity 0.8, **not animated**.
**Negative rules (verbatim):** no colour outside the palette; no gradients/heavy shadows/3D on logo or text; **no flash or hard light change**; no caption over a face or source card; no loud music or stock SFX; **no draft voice layer in any delivery**; **no English text outside the end screen**.
**Audio targets:** YouTube VOD **−14 LUFS / −1 dBTP**, VO −16 LUFS, duck −12 dB.
**Naming:** `MASTER_FINAL_<ID>.mp4`, `CAPTIONS_AR_<ID>.srt`, `QC_<ID>.md`, `SOURCES_<ID>.txt`; no spaces, no Arabic in delivery filenames; `DRAFT_VO` tag mandatory on any non-official voice mix.

### Conflicts between the brand kit and this brief — flagged, not resolved by me

1. **Transitions.** Brand allows only `hard_cut` / `fade_black_200ms` and forbids flash. Brief asks for dissolves, ink/smoke wipes and golden-thread wipes. → I propose declaring **three named motifs** (ink wipe, smoke wipe, thread wipe) as approved extensions in the exception log, each ≤0.5 s, all built from palette colours only, using the brand ease. **Needs your sign-off.**
2. **Logo geometry.** Brief: "transparent logo with no rectangle behind it". Brand: watermark 72 px top-centre at 0.8 opacity, symbol only, clear space = half arch height. → Compatible **if** we use the symbol, not a lockup, and no plate. Confirmed in writing below.
3. **Caption rule vs. "no permanent burned-in captions".** Brand's `Captions` component burns captions into the frame. Brief wants a separate SRT and no permanent burn-in. → **I resolve this as: no burned captions in the master; Arabic SRT as a separate file; on-screen text limited to the ≤40 % key-phrase/lower-third budget.** This is a departure from `episode_meta.captions` behaviour and I am logging it as an exception.
4. **Loudness.** Brand target −14 LUFS; the delivered master VO already sits at −16.5 LUFS with −1.0 dBTP. Final mix must be mastered up to −14 LUFS integrated / ≤−1 dBTP **after** the mix, not by touching the VO file.
5. **English on screen.** Brand forbids English outside the end screen. The brief's two quote cards need **original English + Arabic translation labelled «ترجمة»**. → I read the brief as overriding here, but it needs your explicit yes, since it is a written negative rule.
6. **`brand.json` logo paths do not exist** in the repo (B4).

---

## 5. Timing reality — the brief says "replace the interpolated timestamps"; they have already been replaced, partly

`vo_timestamps_REAL.json` is **not** derived-from-script: 1032 words, faster-whisper large-v3-turbo word timestamps projected onto the recorded audio, **21 low-confidence words**, 142 gaps >0.6 s. So a usable word layer exists. What does **not** exist is CTC forced alignment (WhisperX/wav2vec2), which is impossible here (no torch/GPU/RAM). Two consequences:

- Word-level cuts can be built now from the existing JSON (I will re-project them onto whichever master length you choose in B1).
- The `QA_PRECHECK.md` claim "13 PASS / 0 FAIL" is a **table-only self-check**. It does not survive contact with the actual CSV:
  - it says "zero text-only frames" — true, but the real defect is **81.7 % of shots carry on-screen text** (134/164), not the claimed design.
  - it says "shot change 3.82 s, within 3–5 s" — **measured mean 3.19 s**, median 3.06 s, range 1.11–4.87 s, **0 shots over 5 s**.
  - it claims "golden thread at every location change (10+)" — CSV has `thread=YES` on **13** rows and `shot_type=THREAD` on 16.
  - it claims "every shot ≤5.0 s" — true, which **contradicts brief item 5** (5–8 s breathing shots).

---

## 6. Measured defects in `SHOT_LIST.csv` v1 — against your 10 decisions

| Your gate | Measured | Verdict |
|---|---|---|
| Zero duplicate visuals | **27 distinct visual texts reused across 54 shots = 32.9 %** (exact-string, after normalising whitespace/punctuation). Near-duplicate fuzzy pass at ratio ≥0.85 finds **0** extra — so it is *copy-paste*, not paraphrase. | ❌ FAIL (you said 69/42 %; the honest number is **54/32.9 %**) |
| On-screen text ≤40 % | **134/164 = 81.7 %** — 1 word ×56, 2 words ×48, 3 words ×26, 4 words ×4, **0 over 6 words** | ❌ FAIL |
| Villa Diodati / ghost-story challenge gets weight | scene 14 = **10 shots**, but the **challenge itself is scene 10 with only 3 shots (98–100, 8.6 s in 2.9 s cuts)**. Scene 11 (22 shots) repeats its visuals: 115–122 are a **1:1 copy** of 101–108. | ❌ FAIL |
| Storm / lightning / rain at the villa | **`رعد`/`برق`/`صاعق`/`عاصف`: 0 hits across every column of the CSV.** Only 1 window-rain visual (scene 6), 11 rain mentions total, all in narration or SFX of scene 11 (`rain + thunder` is in **SFX only** — the sound is there, the picture is not) | ❌ FAIL |
| MACRO ≤18 % | **42/164 = 25.6 %** (your figure 26 % — confirmed) | ❌ FAIL |
| Human-scale world-building | market **2** (one is a thread-over-market), bare table **1**, price board **1**, stove **3**, **extra clothing 0**, **snow-blocked road 0** | ❌ FAIL |
| Breathing shots 5–8 s | **0 shots over 5 s**; max 4.87 s; 9 shots under 2 s | ❌ FAIL |
| Atmosphere cutaway uninterrupted 20–30 s | scene 5 = **15 shots, 168.89–221.90 s = 53.0 s** — not 20–30 s; the approve-pack report quotes 168.27–198.27 s (30 s) against the same CSV. It must be rebuilt to 20–30 s as an unbroken chain. | ❌ FAIL |
| Max 3 numbers, documented, linked | 3 dates are shown (8 يونيو, إبريل 1815, 1831, 1819, 1818) — the sheet already **DO-NOT-DISPLAY**s 5 numeric items (VEI 7, ~3 °C, 43 km/150 km³/60 Mt, 60 000/10 000/80 000, 1790–1820) and marks 5 more VERIFY-LINK. Acceptable **only** if I keep exactly 3 and hold the rest as graphics without numbers. | ⚠ achievable |
| Two quote cards, EN + AR «ترجمة» | **none exist in the CSV** (0 rows match "اقتباس"). Sources sheet says S7 (Gutenberg 1831 preface) is the only quotable source | ❌ FAIL |
| Line 84 / C11a kept + warned | **line 84 = shots 102 and 103** (the four shadows / doctor's hand). Kept as recorded; will carry a ⚠ in the Phase 1 report. | ✅ held |
| Report real measured averages | this section | ✅ |

Also unmeasured in any prior report and worth noting: **19 shots are explicitly `static` or `locked-off`**, and **0 shots are tagged with the "single extended camera move into the next shot"** that `QA_PRECHECK.md` claims for all 75 sub-3-s shots.

---

## 7. What I need from you to close Phase 0

1. **B1 — which master?** (a) send the real 626.37 s file, (b) approve the 1.2 s × 28-gap silence trim, or (c) approve re-mapping all scenes to 675.08 s.
2. **B2 — resolution.** Accept the honest 1376×768 plates with restricted parallax, or approve a documented 2× upscale-and-regrain, or allow public-domain plates for the 3 hero establishing shots.
3. **B3 — engine.** Approve the FFmpeg + headless-Chromium motion-graphics pipeline (Remotion cannot render here), or tell me to stop and wait for a cloud runner.
4. **B4 — logo SVGs.** Send the four files, or confirm I use only `riwaq-icon-gold-ink.png` and drop the horizontal lockup from the end card.
5. **Exceptions to sign (4):** three wipe motifs; English on the two quote cards; no burned-in captions (SRT only); final master to −14 LUFS regardless of the −16.5 LUFS VO source.
6. **CTA wording** whose recorded line is «اشترك علشان توصلك… سلااااام» — keep as is, or I re-cut the tail?

Nothing has been generated, rendered or uploaded. Phase 1 (SHOT_LIST v2 + changelog + QA precheck) starts on your OK.
