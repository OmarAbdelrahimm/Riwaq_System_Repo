#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eng4/render4.py — frame pipe to libx264, plus the frame log the QA reads."""
import json, os, subprocess, sys, time
sys.path.insert(0, '/home/user/work')

FF = '/home/user/ffmpeg'
OUT = '/home/user/work/out'
W, H, FPS = 1920, 1080, 30


def render(dur=30.0, tag='pilot4', crf=17):
    from eng4 import pilot4 as P
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
    from PIL import Image
    import numpy as np
    prev = None
    for i in range(n):
        t = i / FPS
        shot = P.shot_at(t)
        im = shot.fn(t)
        a = np.asarray(im.convert('RGB'), dtype=np.int16)
        diff = 0.0 if prev is None else float(np.abs(a - prev).mean())
        prev = a
        log.write(json.dumps(dict(i=i, t=round(t, 3), shot=shot.name, layers=shot.layers,
                                  diff=round(diff, 3))) + '\n')
        proc.stdin.write(a.astype(np.uint8).tobytes())
        if i % 60 == 0:
            print(f'   {i}/{n} t={t:5.2f} {shot.name:14s} layers={shot.layers} diff={diff:5.2f}', flush=True)
    proc.stdin.close()
    proc.wait()
    log.close()
    print(f'rendered {n} frames in {time.time()-t0:.1f}s -> {dst}', flush=True)
    return dst


if __name__ == '__main__':
    dur = float(sys.argv[1]) if len(sys.argv) > 1 else 30.0
    tag = sys.argv[2] if len(sys.argv) > 2 else 'pilot4'
    render(dur, tag)
