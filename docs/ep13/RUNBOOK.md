# EP13 — runbook (exact, reproducible)

Everything is a pure function of the frame number: no clocks, no CSS animation, no
browser. A frame rendered today is byte-identical to a frame rendered in a month.

## 1. Environment

```bash
cd /home/user/Riwaq_System_Repo
python3 -m venv .venv                     # already present
.venv/bin/pip install pillow==9.5.0 numpy imageio-ffmpeg uharfbuzz freetype-py
```

Why these: this machine's Pillow has no `raqm` (no native Arabic shaping), so Arabic
is shaped with **uharfbuzz** (HarfBuzz) and rasterised with **freetype-py** — see
`tools/ep13/text.py`. `imageio-ffmpeg` supplies the ffmpeg binary used for encoding.

Versions actually used: Pillow 9.5.0, numpy 2.4.6, imageio-ffmpeg 9.0.2
(ffmpeg-linux-x86_64-v9.0.2), uharfbuzz 0.57.0, freetype-py (FreeType 2.13.2).

## 2. Verify the inputs (G0)

```bash
cd episode/ep13/spec && sha256sum -c SHA256SUMS.txt   # 37/37 OK
cd /home/user/Riwaq_System_Repo && .venv/bin/python episode/ep13/spec/tools/preflight.py
sha256sum public/ep13/audio/chapter01.mp3 public/ep13/brand/logo.svg
```

Expected: `83be0fd3…09e8` for the narration take, `267e5bd1…a204f` for the official
logo. The handoff's `preflight.py` still reports five items as missing *from the
handoff*; four of them exist in this repo (audio, logo) or are built in code
(fish, glass). See `QC.md` §1.

## 3. Measure the audio (timing authority)

```bash
.venv/bin/python tools/ep13/audio_analysis.py \
  --input public/ep13/audio/chapter01.mp3 \
  --out episode/ep13/measured_audio.json
```

Phrase onsets land in `tools/ep13/timeline.py` (`PHRASES`, `BEATS`). Only onsets are
measured; word-level sync is **not** claimed.

## 4. Styleframes (G1, 1920×1080)

```bash
.venv/bin/python tools/ep13/render.py still --frame 54  --size 1920x1080 --out render/ep13/STYLEFRAME_A_1920.png
.venv/bin/python tools/ep13/render.py still --frame 150 --size 1920x1080 --out render/ep13/STYLEFRAME_B_1920.png
```

Both are the *same* renderer as the proof, sampled at a later beat — so the
styleframe cannot drift from the film. All Arabic type is set by code
(`tools/ep13/text.py`); nothing is baked into a bitmap.

## 5. The 6-second proof (G2, 1280×720 @ 30 fps)

```bash
# 180 frames, ~2.2 s/frame
.venv/bin/python tools/ep13/render.py frames --out render/ep13/frames_v2

# control pass with the camera push disabled (proves the motion is not the camera)
.venv/bin/python tools/ep13/render.py frames --out render/ep13/frames_v2_nocam --camera-off

# contact sheet: frames 0/20/40/60/90/120/150/179
.venv/bin/python tools/ep13/render.py contact --frames render/ep13/frames_v2 \
  --out render/ep13/PROOF_CONTACT.jpg

# MP4 with the original take, first 6.00 s, never stretched
.venv/bin/python tools/ep13/render.py video --frames render/ep13/frames_v2 \
  --out render/ep13/PROOF_0_6_v2.mp4
```

`video` encodes H.264/yuv420p at CRF 17, then muxes `chapter01.mp3` trimmed to
6.000 s. Span check:

```bash
ffmpeg -i render/ep13/PROOF_0_6_v2.mp4    # 6.00 s, 1280x720, 30 fps, aac 44.1 kHz
```

## 6. Measure the result (QC)

```bash
.venv/bin/python tools/ep13/qc.py --frames render/ep13/frames_v2 \
  --control render/ep13/frames_v2_nocam --out render/ep13/QC_REPORT.json
.venv/bin/python tools/ep13/manifest.py     # rebuild docs/ep13/ASSET_MANIFEST_UPDATED.json
```

## 7. Re-render one beat without touching the rest

Frames are independent, so a fix can be applied and only the affected range re-rendered:

```bash
.venv/bin/python tools/ep13/render.py frames --out render/ep13/frames_v2 --start 26 --end 59
.venv/bin/python tools/ep13/render.py video --frames render/ep13/frames_v2 --out render/ep13/PROOF_0_6_v2.mp4
```

## 8. Guard rails baked into the code

* `Canvas` renders at 2× and downsamples with Lanczos — no browser AA, no dither noise.
* Blur is only ever applied to small sprites/tiles, never to a full frame
  (`gfx.blur` on a hero or a card shadow; dust is a pre-computed numpy field).
* Grain is a deterministic per-frame field added through `gfx.screen`, never a shader.
* Nothing is randomised at run time (`random` is not imported anywhere in `tools/ep13`).
