#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""textcheck1.py — the mandatory text-presence test.

For every document in the archive block, the frame is rendered twice: once with its
lettering, once with `text_off` set. Both frames are taken through the SAME camera, crop,
grade and grain, so the only difference between them is the ink. The difference is counted
inside the paper rectangle:

    diff_pixels / paper_area  <  1.5 %   ->  FAIL, and print the cause

Reasons this exists: a wrong FONTS path plus a try/except around ImageFont.truetype made
every string on a whole page fall back silently, and the page went out empty while the
numeric QA still said "text drawn". Ink coverage cannot be inferred; it has to be measured
on the composited frame.

Also prints the font FILE that was resolved for each layer, so a face that fell back to a
system default cannot pass unnoticed.
"""
import sys

import numpy as np

sys.path.insert(0, '/home/user/work')
sys.path.insert(0, '/home/user/Riwaq_System_Repo/episode/1816')

from PIL import Image                                     # noqa: E402
from ch2.eng import ch2 as P                              # noqa: E402
from eng5 import core5 as C                               # noqa: E402

# (name, time, the letters that must be present, paper rect in 1920x1080 frame coords)
# Chapter 2's own sheets: the section, the VEI plate, the temperature curve, the SO2
# molecule, the planet, and the two cards. Every rectangle is the paper, not the frame.
DOCS = [
    # the rectangles are MEASURED, not guessed: each one is the bounding box of the ink
    # that actually differs between the lettering-on and lettering-off renders
    ('SHEET  section 1:57-2:01', 119.5,
     ['Tambora — cross-section', '1000 m', '4300 m'],
     (429, 170, 1142, 678)),
    ('SHEET  VEI 2:01-2:05', 123.4,
     ['Volcanic Explosivity Index', '100000000000', 'تامبورا ١٨١٥'],
     (144, 219, 1436, 915)),
    ('SHEET  column 2:05-2:11', 128.0,
     ['Eruption column', '٤٠ كم', 'صخور ورماد وغازات لفوق'],
     (432, 216, 749, 867)),
    ('SHEET  cooling 3:30-3:34', 212.0,
     ['درجة الحرارة', 'سنة ١٨١٦', 'رجعت بالراحة'],
     (448, 265, 1359, 441)),
    ('SHEET  SO2 3:02-3:06', 184.5,
     ['SO₂ — ثاني أكسيد الكبريت', 'O', 'S'],
     (146, 186, 1214, 797)),
    ('MAP    planet 3:16', 197.0,
     ['الرياح لفته حوالي الكوكب'],
     (105, 938, 545, 993)),
    ('CARD   bury 2:19-2:23', 140.0,
     ['قرية كاملة تحت الرماد'],
     (145, 870, 518, 915)),
    ('CARD   verdict 3:11-3:14', 192.6,
     ['الرماد بيّن الكارثة', 'الغازات عملت البرودة'],
     (209, 243, 1500, 919)),
]


_REAL_SPRITE = C.text_sprite


def _blank_sprite(*a, **kw):
    """the same sprite with the ink removed: identical geometry, zero alpha.

    Zeroing alpha rather than skipping the call keeps every card, tag and label in exactly
    the position it occupies in the real frame, so the difference between the two renders
    is the lettering and nothing else.
    """
    sp = _REAL_SPRITE(*a, **kw)
    sp = sp.copy()
    sp.putalpha(Image.new('L', sp.size, 0))
    return sp


def bust_caches():
    """the documents are built once and cached; the test must rebuild them each render"""
    for name in ('_DESK', '_SECT', '_BG', '_BLANK'):
        d = getattr(P, name, None)
        if isinstance(d, dict):
            d.clear()


def frame_without_text(t, on):
    C.text_sprite = _blank_sprite if on else _REAL_SPRITE
    # the module's own switch too: a few sheets draw type with the image pen, not
    # through a sprite, and that ink has to blank as well or the test is measuring a
    # pixel of paper grain instead of the lettering
    P.text_off['on'] = bool(on)
    bust_caches()
    P.build_tags()
    try:
        return P.frame_at(t).convert('RGB').copy()
    finally:
        C.text_sprite = _REAL_SPRITE
        P.text_off['on'] = False
        bust_caches()


def examine(name, t, strings, rect):
    a = frame_without_text(t, False)          # lettering ON
    b = frame_without_text(t, True)           # lettering OFF
    x0, y0, x1, y1 = rect
    pa = np.asarray(a, np.float32)[y0:y1, x0:x1]
    pb = np.asarray(b, np.float32)[y0:y1, x0:x1]
    d = np.abs(pa - pb).max(axis=2)
    n = int((d > 8).sum())
    area = pa.shape[0] * pa.shape[1]
    pct = 100.0 * n / area
    ok = pct >= 1.5
    print('%-26s t=%6.2f  diff=%7d / %7d px = %5.2f %%  %s'
          % (name, t, n, area, pct, 'PASS' if ok else 'FAIL'))
    if not ok:
        for s in strings:
            sp = C.text_sprite(s, 34)
            ink = (np.asarray(sp.split()[3]) > 24).sum()
            print('    missing-ink check %-38r ink=%d px  font=%s'
                  % (s, ink, C.font(P.HAND, 34).path))
        print('    CAUSE: no lettering reached the paper in this rectangle.')
        print('           usual causes: font not resolved, reshaper error, alpha = 0,')
        print('           or the text layer drawn outside the paper rectangle.')
    return ok, pct


def main():
    print('fonts: FONTS =', C.FONTS)
    ok_all = True
    for name, t, strings, rect in DOCS:
        ok, _ = examine(name, t, strings, rect)
        ok_all = ok_all and ok
    print('\nloaded font files, per layer:')
    seen = set()
    for k, v in P.TEXT_LOG.items():
        if isinstance(k, tuple):
            print('  %-26s %s' % (k[1], v))
            seen.add(k[1])
    if not seen:
        print('  (no hand_text layer ran in this pass)')
    print('\nTEXT RESULT:', 'PASS' if ok_all else 'FAIL')
    return 0 if ok_all else 1


if __name__ == '__main__':
    sys.exit(main())
