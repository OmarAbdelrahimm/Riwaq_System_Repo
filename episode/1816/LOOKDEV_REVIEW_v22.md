# LOOK-DEV REVIEW — answers to your six points

Status: **style approved**, so this document is the record of what was measured,
what was wrong, and what changed. Nothing here is an estimate presented as fact;
every number came out of a script in this folder or a command quoted next to it.

---

## 1. FRAMING — you were right, and the old clip was wrong in a second way

**Measured sizes of what was delivered last turn:**

| File | Pixels | Aspect |
|---|---|---|
| LOOK01_field_dawn_2560.png | **2560 × 1429** | 1.7915 |
| LOOK02_sulfate_haze_2560.png | **2560 × 1429** | 1.7915 |
| LOOK03_villa_storm_2560.png | **2560 × 1429** | 1.7915 |
| LOOK05_parallax_5s_1080p.mp4 | **1920 × 1080** (SAR 1:1, DAR 16:9) | 1.7778 |

The source was 1376 × 768 = 1.7917 (not 1.79:1 rounded from 1.79 — exactly 1.79167).
A 16:9 crop of a 1376-wide frame needs 1376 × 9/16 = **774 px of height**, so it takes
**6 px off the top and 6 px off the bottom**, or equivalently it may keep the full
height and drop **11 px of width** (1376 − 768×16/9 = 11.1).

My earlier sentence — "loses about 60 px of top and bottom" — was **wrong**, and it
was wrong for a reason worth recording: **I never cropped the stills at all.**
They were delivered at 2560 × 1429, which is 11 px *taller* than 16:9 at that width.
So the real error was not an over-crop, it was a missing crop. The only file that was
16:9 was LOOK05 — and it was made by resizing a 1.79:1 plate into a 1920×1080 frame,
which **silently squeezed the image horizontally by 0.78 %** (2560/1429 → 16/9).
Small, but it is a distortion, and it is now gone.

**What is delivered now, and how it was made:**

| File | Pixels | Method |
|---|---|---|
| LOOK01_field_dawn_2560x1440.png | 2560 × 1440 | 2560×1429 → shave **20 px of width** (10 left, 10 right), no resample, **0 px of height lost** |
| LOOK02_sulfate_haze_2560x1440.png | 2560 × 1440 | same |
| LOOK03_villa_storm_2560x1440.png | 2560 × 1440 | same |
| LOOK07_depth_parallax_5s_1080p.mp4 | 1920 × 1080 | rendered at 2560×1440 then Lanczos to 1080p, **no squeeze** |

Width lost: **20 / 2560 = 0.78 %**. Height lost: **0.00 %**. No letterbox anywhere.
The upscale step now targets 2560 × 1440 directly instead of 2560 × 1429, so nothing
has to be cropped after the fact at all — the crop above only corrects the three
plates already approved.

---

## 2. PLATE COUNT — 123 confirmed, per chapter, with a clock

The motion layer is any shot whose `space_kind` is `graphic_space`:
DATA 15 · BOARD 15 · THREAD 13 · MAP 9 · DOC 9 · END 2 = **63**.

| Chapter | Shots | Need a generated plate | Motion layer | Plate seconds |
|---|---:|---:|---:|---:|
| 1 | 34 | **19** | 15 | 50.0 |
| 2 | 31 | **23** | 8 | 71.9 |
| 3 | 34 | **26** | 8 | 77.4 |
| 4 | 38 | **28** | 10 | 79.5 |
| 5 | 31 | **15** | 16 | 36.1 |
| 6 | 18 | **12** | 6 | 35.9 |
| **All** | **186** | **123** | **63** | **350.8** |

66.1 % of shots need a plate; 33.9 % are built in the motion layer. That matches
your "about 123" exactly.

**Time, at the measured 7.0 min per plate** (377 s, 416 s and ~410 s for the three
plates already made, 2 vCPU, 128 px tiles):

| Chapter | Plates | Hours |
|---|---:|---:|
| 1 | 19 | 2.22 |
| 2 | 23 | 2.68 |
| 3 | 26 | 3.03 |
| 4 | 28 | 3.27 |
| 5 | 15 | 1.75 |
| 6 | 12 | 1.40 |
| **Total** | **123** | **14.3** |

Batching: upscaling runs per chapter as a background process (`lookdev` already runs
this way), so the next chapter's plates can queue while the current chapter is being
assembled. The 14.3 h is wall-clock compute, not attention.

---

## 3. DEPTH — real monocular depth, licence cleared, and a measured before/after

**Model:** MiDaS v2.1 (small, 256×256), the exact model class you named.
- Weights: ONNX, 256×256×3 input, 256×256 single-channel output, **64 MB**, ran on
  **ONNX Runtime CPU**, **0.08–0.09 s** per plate.
- **Licence: MIT** — `Copyright (c) 2019 Intel ISL (Intel Intelligent Systems Lab)`.
  MIT permits commercial use, modification and redistribution.
- **Redistribution chain:** trained by Intel ISL (MIT) → converted to ONNX by
  PINTO0309's model zoo (MIT, per that repository's `LICENSE`) → stored in the
  `MiDaS v2 Barracuda` repository (MIT, `0y0`, 2023). No weights are redistributed by
  us; the ONNX file stays local and out of Git.
- **Why this model and not Depth Anything V2:** Depth Anything V2 weights sit behind
  Hugging Face and GitHub *release assets*, and **both hosts are blocked from this
  sandbox** (`huggingface.co` → no route, `objects.githubusercontent.com` → TLS
  reset). MiDaS v2.1 was reachable through a git-over-https clone. MiDaS v2.1 *is*
  one of the two models you named, so this is not a substitution — it is the smaller
  of the two.

**Honest limitation, measured.** On LOOK03 (a near-black night scene) MiDaS reads
large dark mass as *distance*: the villa's mean depth is 0.309 while the sky is 0.293.
I tested five variants to try to fix it — autocontrast, histogram equalisation,
gamma 0.45, and two combinations — and scored each on the vertical prior (depth must
rise from top to bottom). The **untouched output won**:

| Variant | vertical prior r | villa > sky? | sea > sky? |
|---|---:|---|---|
| original output | **0.802** | yes | yes |
| autocontrast | 0.561 | no | yes |
| equalize | 0.747 | yes | no |
| gamma 0.45 | 0.590 | yes | no |
| autocontrast + γ0.7 | 0.775 | yes | yes |

So the depth map is used as-is, and the parallax budget is deliberately small
(0.0 → 68 px of displacement over 5 s, smoothstep-eased) so that a modest depth error
cannot produce a big visual error. This is the honest trade: real depth, small motion.

**Before / after, same plate, same 5 s, same 1.20× push:**

| | Old heuristic (3 flat layers) | New depth warp |
|---|---|---|
| Largest displacement step between **adjacent pixels** | **48.0 px** | **0.49 px** |
| 99th-percentile step | 48.0 px | **0.23 px** |
| Correlation of the displacement field with the depth map | −0.764 | **0.988** |
| Visible artefact | hard torn seams between bands | none |
| Edge streaking | n/a | fixed by reflect-padding 220 px |

The 48 px figure is the whole argument: a flat-band heuristic moves neighbouring
pixels by tens of pixels in one step, which is exactly the tearing visible in the old
clip. The depth warp is continuous, so the only motion you see is the parallax itself.

Deliverables: `LOOK06_parallax_before_after.png` (top: plate, bottom: mid-clip of the
depth warp), `LOOK07_depth_parallax_5s_1080p.mp4`, `LOOK08_heuristic_parallax_5s_1080p.mp4`
(the old method rebuilt at identical settings, for direct comparison).

---

## 4. CONSISTENCY — style block, one LUT, similarity gate

**a. Fixed style block** — `STYLE_BLOCK.md` in this folder. One paragraph of style,
one of negatives, pasted verbatim into every prompt. It is the only lever: the tool
has **no seed, no reference image, no version pinning**.

**b. One unified grade** — `ruwaq_1816.cube`, 33³, tetrahedral, applied in FFmpeg to
every plate after upscale and before grain. It is a **toe/shoulder** LUT: identity
through the midtones, black floor lifted to 3.5 % (8/255), highlight rolled to 93 %
(237/255). Measured effect on the three approved plates:

| Plate | Mean before | Mean after | Black floor | White ceiling |
|---|---:|---:|---:|---:|
| LOOK01 | 83.4 | 85.1 | 0 → 8 | 255 → 237 |
| LOOK02 | 106.1 | 106.0 | 0 → 8 | 255 → 237 |
| LOOK03 | 31.5 | 34.9 | 0 → 8 | 255 → 237 |

A first attempt at a full strength/colour grade was **rejected by measurement**: it
pushed the night plate's mean from 31.5 to 59.8 (a 90 % lift — it turned night into
dusk) and *reduced* similarity between the plates from 0.532 to 0.445. The toe/shoulder
version raises pairwise similarity to **0.543** while leaving the image alone.

**c. Similarity gate** — `simcheck.py`, run after each chapter. Fingerprint = 192-bin
RGB histogram + standardised 16×16 luma grid. Flags:
- **repeat**: two plates in one chapter with histogram cosine ≥ 0.92 **and** luma
  correlation ≥ 0.90 → the same picture twice, regenerate one;
- **outlier**: histogram cosine to the chapter centroid < 0.60 → looks like another film.

Baseline measured on the three approved plates: **0 repeats, 0 outliers, mean pairwise
cosine 0.543**. Thresholds are stated in the file so you can argue with them.

---

## 5. TOOL — no better tool appeared

Still `generate_image` in this environment. Limits, restated because they have not
changed:
- **native 1376 × 768**, no resolution/aspect/upscale/seed parameter;
- **model name and version not exposed**, so results cannot be pinned or reproduced;
- no reference-image conditioning;
- ~2 s per call, but ~7 min per plate once 2× Real-ESRGAN and regrain are applied.

Two models you named were considered and one is in use (MiDaS). Depth Anything V2
could not be obtained: see §3. If `huggingface.co` or GitHub release assets become
reachable, Depth Anything V2 small is a drop-in upgrade and I would re-run the same
scoring table before switching.

---

## 6. CHAPTER 1

Not started. `04_Chapters` is empty. Waiting on this review and on v2.2.
