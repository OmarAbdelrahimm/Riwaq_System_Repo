#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eng4/contrast4.py — WCAG contrast per text element, measured, not asserted.

Two kinds of element, measured differently because they are built differently:

  paper props  the ink is drawn on an opaque paper sheet at full alpha, so the pair that
               actually reaches the eye is ink-vs-paper inside that sprite. The sprite is
               rebuilt here with the same call the shot makes and measured directly.
  type on the   there is no paper: the glyphs sit on the graded plate, so the glyph
  dark map     colour and the plate behind it are read off the rendered frame.

Nothing is compared against a colour that is not on screen.
"""
import json
import sys

sys.path.insert(0, '/home/user/work')
import numpy as np

from eng5 import core5 as C
from eng5 import pilot5 as P


def lum(rgb):
    c = np.asarray(rgb, np.float64) / 255.0
    c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return float(0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2])


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def from_sprite(name, prop):
    """ink vs paper inside a paper prop, using only opaque pixels"""
    a = np.asarray(prop['sprite'].convert('RGBA'), np.float32)
    x0, y0, x1, y1 = prop['box']
    crop = a[y0:y1, x0:x1]
    op = crop[crop[..., 3] > 250][:, :3]
    if len(op) < 200:
        return dict(text=name, ratio=0.0, ok=False, note='sprite box misses the ink')
    l = op @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    ink = op[l <= np.percentile(l, 12)].mean(0)
    paper = np.median(op[l >= np.percentile(l, 55)], axis=0)
    r = ratio(ink, paper)
    return dict(text=name, ink=[int(v) for v in ink], bg=[int(v) for v in paper],
                ratio=round(r, 2), ok=bool(r >= 4.5), kind='ink on paper')


def from_frame(name, t, box):
    """glyph colour vs the graded plate behind it, read off the rendered frame"""
    # measure the frame the film actually draws, with all overlays on
    C.HIDE_TEXT[0] = False
    im = np.asarray(P.frame_at(t).convert('RGB'), np.float32)
    x, y, w, h = box
    crop = im[y:y + h, x:x + w].reshape(-1, 3)
    l = crop @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    ink = crop[l >= np.percentile(l, 97)].mean(0)
    bg = np.median(crop[l <= np.percentile(l, 45)], axis=0)
    r = ratio(ink, bg)
    return dict(text=name, t=t, ink=[int(v) for v in ink], bg=[int(v) for v in bg],
                ratio=round(r, 2), ok=bool(r >= 4.5), kind='gold on dark')


if __name__ == '__main__':
    res = []
    # every paper prop, rebuilt by the same call the film makes
    for tg in P.QUEUE.tags:
        res.append(from_sprite(tg.name, tg.sprite))
    # the year card is in the queue now, so it is measured there like every other card.
    # The disclaimer is the one element with no paper under it, so it is measured against
    # the plate it actually lands on, at the moment it is at full strength.
    res.append(from_frame('disclaimer', 1.55, (80, 60, 460, 110)))
    # gold type straight on the dark map, read off the rendered frame
    res.append(from_frame('map counter', 21.30, (1120, 40, 700, 210)))
    res.append(from_frame('map label', 17.60, (80, 50, 800, 120)))
    P.frame_at(29.50)
    cx = P.CORNER_SHOT[0]
    res.append(from_frame('corner wordmark', 29.50, (int(cx[0]) - 10, 40, 330, 200)))

    bad = [r for r in res if not r['ok']]
    out = dict(elements=res, n=len(res), n_ok=len(res) - len(bad),
               min_ratio=min(r['ratio'] for r in res), failures=bad,
               threshold=4.5, ok=not bad)
    json.dump(out, open('/home/user/work/out/contrast_pilot5.json', 'w'), indent=1,
              ensure_ascii=False)
    for r in res:
        print(f"{r['text']:18s} {r['ratio']:6.2f}:1  {'ok ' if r['ok'] else 'FAIL'}  {r['kind']}")
    print('min', out['min_ratio'], 'ok', out['n_ok'], '/', out['n'])
