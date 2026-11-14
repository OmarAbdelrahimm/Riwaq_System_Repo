# Chapter 1 pilot v4 — built on the supplied AI footage

v3 was rejected because it painted its backgrounds in Python instead of cutting the
fourteen AI clips. v4 decodes real footage at 1920x1080 and composites on top of it.

## Pipeline
1. `src_manifest/AI_CLIPS.csv` — the 14 supplied clips with Drive IDs and real metadata.
2. Frames are extracted from the clips used in 0-30 s (decode to 1920x1080 @30fps).
3. `eng/core4.py` — sub-pixel camera, analytic snow/rain/ash, paper props, the portico
   mark, per-frame grain.
4. `eng/world.py` — the dark-mode map from public-domain Natural Earth vectors,
   built at 2600x1462 so the camera has room to pan.
5. `eng/pilot4.py` — six shots, 24 events on the measured word anchors.
6. `eng/render4.py` — raw frame pipe to libx264.
7. `eng/audio4.py` — stems, 11 dB duck, designed prop hits, -14 LUFS / -1 dBTP.
8. `eng/qa4.py` + `eng/contrast4.py` — every figure in `qa/QA_REPORT_pilot_v4.md`.

## Reproduce
```
pip install pillow numpy pyshp arabic-reshaper python-bidi imageio-ffmpeg
# Natural Earth 1:110m, public domain
pip download --no-deps -d /tmp/ne geopandas==0.14.4 && unzip -q /tmp/ne/*.whl -d /tmp/ne
python eng/audio4.py && python eng/render4.py 30 pilot4 && python eng/qa4.py pilot4
python eng/contrast4.py
```
