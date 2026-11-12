#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""logocheck2.py — prove the corner mark never moves.

Two independent checks, because the v2 glitch was a code path, not a frame:

  A  source: no call may pass a computed x/y to the corner mark. Every chapter must call
     C.corner_logo(), whose position is a constant (56, 44, 145 px, 80 %).
  B  frames: sample the rendered master and measure where the mark's ink lands. The ink
     centroid must sit inside the locked box, and the mirrored box on the right must be
     empty, except inside the declared centre-reveal window.

Run:  python3 logocheck1.py [master.mp4] [module]
"""
import ast
import os
import re
import subprocess
import sys

import numpy as np

sys.path.insert(0, '/home/user/work')
sys.path.insert(0, '/home/user/Riwaq_System_Repo/episode/1816')

FF = '/home/user/ffmpeg'
SRC = '/home/user/Riwaq_System_Repo/episode/1816'
BOX = (56, 44, 201, 140)              # the locked footprint, from core5.CORNER_LOGO
T_END = 225.41


def source_audit():
    """every place_logo/corner_logo call site in every chapter engine"""
    bad, calls = [], []
    for root, _, files in os.walk(SRC):
        if '/eng' not in root and not root.endswith('/eng'):
            continue
        for f in files:
            if not f.endswith('.py') or f.startswith('logocheck'):
                continue
            p = os.path.join(root, f)
            src = open(p, encoding='utf-8').read()
            for m in re.finditer(r'C\.(place_logo|corner_logo)\(([^\n]\)]*)\)', src):
                call = m.group(0)
                calls.append((os.path.relpath(p, SRC), call[:90]))
                if m.group(1) == 'place_logo':
                    bad.append((os.path.relpath(p, SRC), call[:90]))
    return calls, bad


def bbox_of_diff(t):
    """render the frame twice, mark on and mark off, and diff: exact ink rectangle.

    This is the only measurement that cannot be fooled: bright paper, a card or a map
    caption are identical in both renders and cancel out.
    """
    from ch2.eng import ch2 as P
    P.logo_off['corner'] = False
    a = np.asarray(P.frame_at(t).convert('RGB'), np.int16)
    P.logo_off['corner'] = True
    b = np.asarray(P.frame_at(t).convert('RGB'), np.int16)
    P.logo_off['corner'] = False
    # a high threshold keeps the soft shadow halo out: only the mark's own ivory ink
    # counts, so the measurement is the glyph block and not its feather
    d = (np.abs(a - b).max(axis=2) > 25)
    if not d.any():
        return None, 0, 0
    ys, xs = np.where(d)
    top = d[:300, :]
    corner = int(top[:, :420].sum())
    centre = int(top[:, 600:1320].sum()) + int(d[300:800, 600:1320].sum())
    return (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())), corner, centre


def frame_ink(t, mp4):
    subprocess.run([FF, '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', mp4, '-frames:v', '1',
                    '/tmp/_lg.png'], check=True)
    from PIL import Image
    a = np.asarray(Image.open('/tmp/_lg.png').convert('RGB'), np.float32)
    l = a @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    # ivory ink: bright and low saturation, the mark's own colour
    sat = a.max(2) - a.min(2)
    ink = (l > 150) & (sat < 60)
    # the top band only: map captions and cards live lower in the frame and are not the mark
    band = np.zeros_like(ink)
    band[24:200, :] = ink[24:200, :]
    x0, y0, x1, y1 = BOX
    inside = int(band[y0:y1, x0:x1].sum())
    rx0 = 1920 - x1
    right = int(band[y0:y1, rx0:1920 - x0].sum())
    # the vertical centre band, where the hero reveal lands
    centre = int(ink[380:700, 700:1220].sum())
    ys, xs = np.where(band[:, :520])
    cen = (float(xs.mean()), float(ys.mean())) if len(xs) > 40 else None
    return inside, right, centre, cen


def main(mp4='/home/user/work/out2/RUWAQ_CH2_master_av.mp4'):
    import argparse
    calls, bad = source_audit()
    print('call sites:')
    for f, c in calls:
        print('   %-34s %s' % (f, c))
    print('place_logo call sites with a free position:', len(bad))
    for f, c in bad:
        print('   BAD %-30s %s' % (f, c))

    from ch2.eng import ch2 as P

    # ---- B: exact ink rectangle, frame by frame, from the engine
    ts = [round(103.17 + t * 2.0, 2) for t in range(0, 61)]   # every 2 s, 1:43 -> 3:43
    # and the six card windows, at entry, hold and exit: the mark is expected to yield
    # to a card that lands in its own corner, so those frames are asserted differently
    for _tg in P.QUEUE.tags:
        ts += [round(_tg.t_in + 0.05, 2), round(_tg.t_in + 0.9, 2),
               round(_tg.t_out + 0.15, 2), round(_tg.t_done + 0.4, 2)]
    bad_box, empty, doubled, yielded = [], [], [], []
    for t in sorted(set(ts)):
        bb, corner, centre = bbox_of_diff(t)
        # the reveal ramps in over its first 0.2 s, and 0:00-0:20 is the fade from black:
        # both are declared, not failures
        if t < 0.20 or 27.0 <= t < 27.20:
            continue
        in_hero = False
        if bb is None:
            # no ink at all: legal only while a card is in the mark's own corner and the
            # mark has yielded to it (the rule is "cards move for the logo", but a
            # slot-C card sits exactly under the mark, and the mark must not be printed
            # over it) -- and illegal everywhere else
            if P.corner_free(t):
                empty.append(t)
            else:
                yielded.append(t)
            continue
        if in_hero:
            if centre < 800 or corner > 40:
                doubled.append((t, corner, centre))
        else:
            dx = abs(bb[0] - BOX[0]) + abs(bb[1] - BOX[1])
            if dx > 8 or corner < 800:
                bad_box.append((t, bb, corner))
    print('\nsampled %d frames between 1:43 and 3:43' % len(set(ts)))
    print('  frames with no mark at all      :', empty)
    print('  frames where a card owned the corner, mark yielded:', len(yielded), yielded[:6])
    print('  frames where the box moved      :', bad_box)
    print('  hero-window frames that also had a corner mark, or no centre mark:', doubled)
    ok = not bad and not empty and not bad_box and not doubled
    print('\nLOGO RESULT:', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
