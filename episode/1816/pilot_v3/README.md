# Chapter 1 rebuild — pilot v3 (0:00–0:30)

`eng/` builds the 30 s hook: `core.py` (plates, paper, frost, thread, brand mark),
`maps.py` (Natural Earth projection + physical map sheets), `pilot.py` (the ten shots and
their events), `render.py` (raw-frame pipe + contrast instrumentation), `audio.py` (stem
mix, ducking, designed prop hits, loudnorm), `qa.py` (measured QA + contact sheet).

Reproduce:
```
pip install pillow numpy pyshp arabic-reshaper python-bidi imageio-ffmpeg
pip download --no-deps -d /tmp/ne geopandas==0.14.4   # Natural Earth vectors
python eng/audio.py && python eng/render.py 30 pilot && python eng/qa.py pilot
```
`eng/maps.py` expects the extracted shapefile at `/tmp/ne/geopandas/datasets/...`.
`qa/QA_REPORT_pilot.md` is the measured report; `qa/ASSET_SIDECARS.md` lists prompt,
tool and licence for every generated plate.
