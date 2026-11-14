#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eng5/render5.py — frame pipe to libx264 plus the per-frame log the QA reads."""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, '/home/user/work')

FF = '/home/user/ffmpeg'
OUT = '/home/user/work/out'
W, H, FPS = 1920, 1080, 30

LAYERS = dict(
    S1_cold_open=['plate 09 + camera', 'snow mid', 'grade drift'],
    S2_farmers=['plate 01 + push', 'snow mid', 'snow fg'],
    S3_europe=['plate 02 + push', 'rain', 'snow fg'],
    S4_map=['map plate + drift', 'ash drift', 'route + pins', 'counter'],
    S5_monster=['plate 03 + camera', 'lightning flash', 'ash drift'],
    S6_return=['plate 01 + push', 'snow mid', 'wordmark'],
)


def render(dur=30.0, tag='pilot5', crf=17):
    from eng5 import pilot5 as P
    import numpy as np
    os.makedirs(OUT, exist_ok=True)
    dst = os.path.join(OUT, f'{tag}.mp4')
    n = int(round(dur * FPS))
    cmd = [FF, '-hide_banner', '-loglevel', 'error', '-y',
           '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', str(crf),
           '-pix_fmt', 'yuv420p', '-movflags', '+faststart', dst]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    log = open(os.path.join(OUT, f'layerlog_{tag}.jsonl'), 'w')
    t0 = time.time()
    prev = None
    for i in range(n):
        t = i / FPS
        im = P.frame_at(t)
        a = np.asarray(im.convert('RGB'), dtype=np.int16)
        diff = 0.0 if prev is None else float(np.abs(a - prev).mean())
        prev = a
        shot = P.shot_name(t)
        log.write(json.dumps(dict(
            i=i, t=round(t, 3), shot=shot, layers=len(LAYERS[shot]),
            layer_names=LAYERS[shot], diff=round(diff, 3),
            tags=[tg.name for tg, _ in P.QUEUE.active(t)],
            cut=P.cut_of(t))) + '\n')
        proc.stdin.write(a.astype(np.uint8).tobytes())
        if i % 90 == 0:
            print(f'   {i}/{n} t={t:5.2f} {shot:14s} diff={diff:5.2f}', flush=True)
    proc.stdin.close()
    proc.wait()
    log.close()
    print(f'rendered {n} frames in {time.time()-t0:.1f}s -> {dst}', flush=True)
    return dst


if __name__ == '__main__':
    dur = float(sys.argv[1]) if len(sys.argv) > 1 else 30.0
    tag = sys.argv[2] if len(sys.argv) > 2 else 'pilot5'
    crf = int(sys.argv[3]) if len(sys.argv) > 3 else 17
    render(dur, tag, crf)
