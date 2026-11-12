#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""relog2.py — rebuild Chapter 2's per-frame log from the delivered master.

The first render wrote its log with a placeholder plate index, so the plate audit
reported a 197-frame freeze on a clip that is in fact advancing (verified: source index
0 -> 156 across the shot). Rather than re-encode 3667 frames to fix a text file, the log
is rebuilt from two measured sources:

  * the plate index / shot / tags / cut: read from the engine at that time (cheap, no
    rendering -- these are pure functions of t);
  * the frame-to-frame difference: measured on the DECODED master, which is stricter than
    the old value because it includes the encoder.

The output is the same JSONL schema render2 writes, so qa2 reads it unchanged.
"""
import json
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, '/home/user/work')
sys.path.insert(0, '/home/user/Riwaq_System_Repo/episode/1816')

FF = '/home/user/ffmpeg'
OUT = '/home/user/work/out2'
FPS = 30
W, H = 1920, 1080


def main(mp4='RUWAQ_CH2_master.mp4'):
    from ch2.eng import ch2 as P

    n = int(round((P.T_END - P.T0) * FPS))
    proc = subprocess.Popen([FF, '-v', 'error', '-i', os.path.join(OUT, mp4),
                             '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                            stdout=subprocess.PIPE)
    rows, prev = [], None
    layers = P.levels()
    out = open(os.path.join(OUT, 'log_%s.jsonl' % os.environ.get('CH2_TAG', 'ch2')), 'w')
    for i in range(n):
        t = P.T0 + i / FPS
        buf = proc.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            print('short read at', i, file=sys.stderr)
            break
        a = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.int16)
        diff = 0.0 if prev is None else float(np.abs(a - prev).mean())
        prev = a
        shot = P.shot_name(t)
        key, idx, pn, bsf = P.plate_src(t)
        rec = dict(i=i, t=round(t, 3), shot=shot, layers=len(layers[shot]),
                   layer_names=layers[shot], diff=round(diff, 3),
                   tags=[tg.name for tg, _ in P.QUEUE.active(t)],
                   plate=key, plate_idx=idx, plate_n=pn, bsf=bsf, cut=P.cut_of(t))
        rows.append(rec)
        out.write(json.dumps(rec) + '\n')
    proc.stdout.close()
    proc.wait()
    out.close()
    print('rows', len(rows), 'static', sum(1 for r in rows[1:] if r['diff'] < 0.30))
    return len(rows)


if __name__ == '__main__':
    main(*sys.argv[1:])
