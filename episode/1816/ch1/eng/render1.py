#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eng1/render1.py — frame pipe for Chapter 1, with restartable segments.

A 3285-frame render is ~25 minutes; if the sandbox dies at frame 2600 there is no reason
to redo 2600 frames. Each segment is an independent x264 file and the join is a concat
demuxer pass with stream copy, so nothing is re-encoded twice.
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, '/home/user/work')

FF = '/home/user/ffmpeg'
OUT = '/home/user/work/out1'
W, H, FPS = 1920, 1080, 30


def _seg_cmd(dst, crf):
    return [FF, '-hide_banner', '-loglevel', 'error', '-y',
            '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', str(crf),
            '-pix_fmt', 'yuv420p', '-g', '60', dst]


def render(i0, i1, tag='ch1', crf=17, log=True):
    from ch1.eng import ch1 as P
    import numpy as np
    os.makedirs(OUT, exist_ok=True)
    dst = os.path.join(OUT, f'{tag}_{i0:05d}_{i1:05d}.mp4')
    proc = subprocess.Popen(_seg_cmd(dst, crf), stdin=subprocess.PIPE)
    fh = open(os.path.join(OUT, f'log_{tag}_{i0:05d}_{i1:05d}.jsonl'), 'w') if log else None
    t0 = time.time()
    prev = None
    layers = P.levels()
    for i in range(i0, i1):
        t = i / FPS
        im = P.frame_at(t)
        a = np.asarray(im.convert('RGB'), dtype=np.int16)
        diff = 0.0 if prev is None else float(np.abs(a - prev).mean())
        prev = a
        shot = P.shot_name(t)
        if fh:
            key, idx, n, bsf = P.plate_src(t)
            fh.write(json.dumps(dict(
                i=i, t=round(t, 3), shot=shot, layers=len(layers[shot]),
                layer_names=layers[shot], diff=round(diff, 3),
                tags=[tg.name for tg, _ in P.QUEUE.active(t)],
                plate=key, plate_idx=idx, plate_n=n, bsf=bsf,
                cut=P.cut_of(t))) + '\n')
        proc.stdin.write(a.astype(np.uint8).tobytes())
        if i % 150 == 0:
            print(f'   {i}/{i1} t={t:6.2f} {shot:14s} diff={diff:5.2f}', flush=True)
    proc.stdin.close()
    proc.wait()
    if fh:
        fh.close()
    print(f'segment {i0}-{i1} in {time.time()-t0:.1f}s -> {dst}', flush=True)
    return dst


def concat(parts, dst):
    lst = dst + '.txt'
    with open(lst, 'w') as f:
        for p in parts:
            f.write(f"file '{p}'\n")
    subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat',
                    '-safe', '0', '-i', lst, '-c', 'copy', dst], check=True)
    return dst


if __name__ == '__main__':
    if len(sys.argv) > 2:
        a, b = int(sys.argv[1]), int(sys.argv[2])
        render(a, b, tag=(sys.argv[3] if len(sys.argv) > 3 else 'ch1'))
    else:
        n = int(round(109.48 * FPS))
        render(0, n)
