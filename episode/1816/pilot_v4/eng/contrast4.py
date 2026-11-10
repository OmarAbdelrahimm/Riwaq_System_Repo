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

from eng4 import core4 as C
from eng4 import pilot4 as P


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
    im = np.asarray(P.shot_at(t).fn(t).convert('RGB'), np.float32)
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
    # props, rebuilt exactly as the shots build them
    res.append(from_sprite('disclaimer', C.paper_tag('مشاهد مُعاد تخيّلها', size=34, padx=22,
                                                    pady=12, tape=False, seed=4)))
    res.append(from_sprite('stamp 1816', C.stamp_sprite('يونيو 1816', size=88)))
    res.append(from_sprite('tag USA', C.paper_tag('فلاحين · أمريكا', size=56, rotate=-1.6, seed=5)))
    res.append(from_sprite('tag snow', C.paper_tag('والتلج بينزل عليه', size=52, rotate=1.4, seed=6)))
    res.append(from_sprite('tag Europe', C.paper_tag('أوروبا · مطر وبرد', size=54, rotate=1.2, seed=8)))
    res.append(from_sprite('tag crops', C.paper_tag('المحاصيل ما كبرتش', size=50, rotate=-1.1, seed=9)))
    res.append(from_sprite('tag monster', C.paper_tag('أشهر وحش في الأدب', size=54, rotate=-1.3, seed=12)))
    # type that sits directly on the plate
    res.append(from_frame('map counter', 21.30, (1080, 700, 640, 200)))
    res.append(from_frame('map label', 18.00, (56, 60, 700, 90)))

    for r in res:
        print(f"{r['text']:14s} {r['ratio']:6.2f}:1 {'PASS' if r['ok'] else 'FAIL'}  "
              f"ink={r.get('ink')} bg={r.get('bg')}  [{r.get('kind')}]"
              f"{'  ' + r['note'] if r.get('note') else ''}")
    json.dump(res, open('/home/user/work/out/contrast_pilot4.json', 'w'), indent=1)
    print('all pass:', all(r['ok'] for r in res), ' min:', min(r['ratio'] for r in res))
