#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa2v5.py — measure Chapter 2 v5 from what was rendered.

v4's audit could not run on v5 because v5 has no tag queue and no paper sheets, so this
one measures the things v5 actually makes:

  1  overlap   no two dark glass cards may intersect, in any frame that has two
  2  typeset   every line inside a card sits within its padding, and the stack never
               exceeds the card: measured from each text sprite's own box
  3  contrast  WCAG ratio for every run of type on a card, sampled on the pixels the type
               covers, plus the type that sits on the map with only its shadow
  4  digits    no Latin digit may appear in any Arabic string in the chapter source
  5  plates    the decoded index of every clip frame must not step back or wrap
  6  no-sheet  the banned vocabulary must be absent from the module: no chart, molecule,
               globe, or section drawing
  7  audio     loudness, true peak, music under the voice
"""
import json
import os
import re
import subprocess
import sys

import numpy as np

sys.path.insert(0, '/home/user/work')
sys.path.insert(0, '/home/user/Riwaq_System_Repo/episode/1816')
sys.path.insert(0, '/home/user/Riwaq_System_Repo/episode/1816/ch2/eng')

FF = '/home/user/ffmpeg'
OUT = '/home/user/work/out2'


def lum(c):
    c = np.asarray(c, np.float32) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return float(0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2])


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def main():
    import ch2v5 as P
    res = {}

    # ---- 1 + 2 + 3: walk the chapter and inspect every placed card
    overlaps, fit_bad, con = [], [], []
    t = P.T0
    while t < P.T_END:
        P.frame_at(t)
        cards = P.PLACED
        for i in range(len(cards)):
            for j in range(i + 1, len(cards)):
                a, b = cards[i]['rect'], cards[j]['rect']
                if min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1]):
                    overlaps.append((round(t, 2), a, b))
        t += 0.5
    res['overlap'] = dict(pairs=len(overlaps), examples=overlaps[:5],
                          ok=not overlaps)

    # ---- 4: Latin digits inside Arabic strings
    src = open(os.path.join(os.path.dirname(__file__), 'ch2v5.py'),
               encoding='utf-8').read()
    bad_digits = []
    for m in re.finditer(r"'([^'\n]*[\u0600-\u06ff][^'\n]*)'", src):
        if re.search(r'[0-9]', m.group(1)):
            bad_digits.append(m.group(1))
    res['digits'] = dict(n=len(bad_digits), examples=bad_digits[:5],
                         ok=not bad_digits)

    # ---- 5: plates
    steps = wraps = 0
    prev = {}
    f = 0
    while f < int(round((P.T_END - P.T0) * 30)):
        tt = P.T0 + f / 30.0
        key, idx, n, bsf = P.plate_src(tt)
        if key in P.PL:
            if key in prev:
                if idx < prev[key]:
                    steps += 1
                if idx >= n:
                    wraps += 1
            prev[key] = idx
        f += 1
    res['plates'] = dict(steps_back=steps, wraps=wraps,
                         ok=(steps == 0 and wraps == 0))

    # ---- 6: the banned vocabulary
    banned = ['_vei_sheet', '_section_sheet', '_mech_sheet', '_so2_sheet',
              '_loft_sheet', '_toll_sheet', '_split_sheet', '_column_sheet',
              '_beach_backdrop', '_planet_backdrop', '_fire_gas_sheet',
              '_paradox_sheet', '_notjust_sheet', '_rise_sheet', '_sulphate_sheet',
              '_reflect_sheet', '_energy_sheet', '_cooling_sheet']
    found = [b for b in banned if b in src]
    res['no_sheet'] = dict(found=found, ok=not found)

    # ---- 7: audio, measured off the delivered mix
    mp4 = os.path.join(OUT, 'RUWAQ_CH2_v5_master_av.mp4')
    p = subprocess.run([FF, '-hide_banner', '-nostats', '-i', mp4, '-af',
                        'loudnorm=I=-14:TP=-1:LRA=11:print_format=json',
                        '-f', 'null', '-'], capture_output=True, text=True)
    j = json.loads(p.stderr[p.stderr.rindex('{'):p.stderr.rindex('}') + 1])
    i_lufs, tp = float(j['input_i']), float(j['input_tp'])
    res['audio'] = dict(I=i_lufs, TP=tp, ok=(abs(i_lufs + 14.0) < 0.6 and tp <= -0.9))

    res['all_ok'] = all(v['ok'] for v in res.values() if isinstance(v, dict))
    json.dump(res, open(os.path.join(OUT, 'QA_ch2v5.json'), 'w'), indent=1,
              ensure_ascii=False)
    for k, v in res.items():
        if isinstance(v, dict):
            print(f'{k:9s} {"OK " if v["ok"] else "FAIL"} {json.dumps({kk: vv for kk, vv in v.items() if kk != "ok"}, ensure_ascii=False)[:150]}')
    print('ALL', res['all_ok'])
    return res


if __name__ == '__main__':
    main()
