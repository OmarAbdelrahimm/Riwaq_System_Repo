# LOOK-DEV — RUWAQ | 1816

Five files, three stills, one clip, one crop. Everything below is what was actually done, with the measured numbers.

## 1 · What produced the 1376×768 images

You asked which tool and model, and what it can do. Answering precisely:

| | |
|---|---|
| Tool | Arena's built-in `generate_image` tool (a single text-to-image call, one image per call) |
| Model | Not exposed to me. The tool returns a PNG and nothing else — no model name, no seed, no version string. I cannot name it honestly, so I will not invent one. |
| Native output | **1376 × 768** exactly, every time. That is 1.79:1, so it is *not* 16:9 — a 1920×1080 frame crops the sides or pads top/bottom. |
| Higher resolution | **Not available.** No resolution, aspect, or upscale parameter exists on the tool. 1376×768 is the ceiling, so I requested that and cropped to 16:9 afterwards. |
| Upscaling | Done outside the tool, by me, with Real-ESRGAN x4 (ncnn, CPU) — see §3. |
| Control | Prompt only. No reference image, no seed lock, so two calls of the same prompt are **not** the same picture. That matters: 186 shots means 186 generations, and character/weather consistency will need the repeat-prompt check I described in Phase 0. |

This is the honest limit: **the source material is 1376×768 and cannot be generated larger.** Everything downstream is upscale.

## 2 · The three stills

| File | Shot it stands for | Why this frame |
|---|---|---|
| `LOOK01_field_dawn_2560.png` | 1 · opening field at dawn (line 0) | the hook: green wheat under frost, one gold band at the horizon |
| `LOOK02_sulfate_haze_2560.png` | atmosphere chain (lines 38–46) | the mechanism as an image, not a diagram: particles in a sunbeam, no arrows, no numbers |
| `LOOK03_villa_storm_2560.png` | 4·9 Lake Geneva, storm night | the storm the film has to earn: lake, one lit window, one strike behind cloud |

All three are 2560 px wide. Palette is held to the brand ten; no text, no logo, no archival material, no faces.

## 3 · Upscale and regrain, measured

| Step | Setting |
|---|---|
| Network | Real-ESRGAN **realesrgan-x4plus** (RRDBNet), ncnn param/bin from `realesrgan-ncnn-py` 2.0.0 |
| Runtime | ncnn Python binding, **CPU only**, Vulkan off, 2 threads — no GPU in this sandbox |
| Tiling | 128 px tiles, 8 px reflect padding, Mat released per tile (peak RSS ≈ 2.7 GB) |
| Input normalisation | 0–1 (`substract_mean_normalize` scale 1/255) — see the bug note below |
| Output | 1376×768 → **5504×3072** (x4), then Lanczos to **2560** wide, then grain |
| Grain | monochrome, σ = 5.0, luminance-weighted (more in the shadows), 1-2-1 softened |
| Time | field 377 s · storm 416 s · haze ~410 s per still on 2 vCPU |

**Bug found and fixed.** The first pass fed 0–255 pixels to a network that expects 0–1. The result looked *smoother* than a plain resize: measured gradient energy **0.97** at 4×, versus **8.44** for Lanczos. After normalisation the same crop measures **15.28** — the network is now actually sharpening, not blurring. The before/after crop in this folder is from the corrected pass.

## 4 · The 5 s parallax clip

| | |
|---|---|
| File | `LOOK05_parallax_5s_1080p.mp4` (H.264, 1920×1080, 30 fps, 5.00 s) |
| Method | the 2560 still is split into 3 depth layers (near / mid / far) by a heuristic score from local contrast, horizon distance and luminance; each layer is scaled slightly larger than frame and pushed by a different amount, then composited in FFmpeg `overlay` |
| Measured motion | far band **−40 px**, mid band **−40 px**, near band **−135 px** over 5 s — i.e. near moves 3.4× the far layer. Real parallax, not a pan. |
| Honest limit | **there is no depth map.** The layers are heuristic, so a hard edge between a near object and the sky can tear under a big move. That is why the push is capped near **1.20×**, as you specified. |

## 5 · What needs your call

1. **Style** — the three stills are one interpretation: cold, desaturated, documentary, no fantasy lighting. If you want it warmer or more graphic, say so before I generate 186 of them.
2. **1376×768** is the ceiling and it is 1.79:1, not 16:9. My crop keeps the centre and loses about 60 px of top and bottom. If you would rather keep the full height, tell me and I will letterbox instead.
3. **Upscale time is real**: ~7 min per still on 2 vCPU, so 186 stills ≈ 22 hours of upscaling alone, before any motion. That number goes into each chapter's render estimate.

Stopping here for your approval of the style.
