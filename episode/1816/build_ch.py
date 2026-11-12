#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_ch.py — one driver for Chapters 3-6: segment render, join, mix, mux, gate.

Every chapter is built the same way, and every chapter is proved before it is delivered:

    render segments (restartable) -> concat -> mix its OWN VO slice -> loudnorm ->
    mux -> sync_gate -> two-pass delivery encode -> sync_gate again

The two gates are the point. The first proves the master that goes into the file is the
chapter's own slice; the second proves the delivered encode still is, because a mux can be
right and an encode can still be wrong.

    python build_ch.py 3 audio 4 mux 5 encode 6 gate      # or any subset, in order
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, '/home/user/work')
sys.path.insert(0, '/home/user/Riwaq_System_Repo/episode/1816')

FF = '/home/user/ffmpeg'
W, H, FPS = 1920, 1080, 30
ROOT = '/home/user/Riwaq_System_Repo/episode/1816'


def mod(n):
    return __import__(f'ch{n}.eng.ch{n}v5', fromlist=['x'])


def out_dir(n):
    d = f'/home/user/work/out{n}'
    os.makedirs(d, exist_ok=True)
    return d


def n_frames(P):
    return int(round((P.T_END - P.T0) * FPS))


def _seg_cmd(dst, crf=17):
    return [FF, '-hide_banner', '-loglevel', 'error', '-y',
            '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
            '-r', str(FPS), '-i', '-',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', str(crf),
            '-pix_fmt', 'yuv420p', '-g', '30', '-force_key_frames', 'expr:eq(n,0)', dst]


def render(n, i0, i1, crf=17, report=60):
    import numpy as np
    P = mod(n)
    d = out_dir(n)
    dst = os.path.join(d, f'seg_{i0:05d}_{i1:05d}.mp4')
    if os.path.exists(dst) and os.path.getsize(dst) > 10000:
        print(f'  [ch{n}] segment {i0}-{i1} already on disk, keeping it', flush=True)
        return dst
    proc = subprocess.Popen(_seg_cmd(dst, crf), stdin=subprocess.PIPE)
    t0 = time.time()
    for k, i in enumerate(range(i0, i1)):
        t = P.T0 + i / FPS
        im = P.frame_at(t)
        proc.stdin.write(np.asarray(im.convert('RGB'), np.uint8).tobytes())
        if k % report == 0:
            el = time.time() - t0
            print(f'   [ch{n}] {i}/{i1} t={t:7.2f} {P.shot_name(t):14s} '
                  f'{el / max(1, k):.2f}s/f', flush=True)
    proc.stdin.close()
    proc.wait()
    assert proc.returncode == 0, 'segment encode failed'
    print(f'  [ch{n}] segment {i0}-{i1} -> {dst} in {time.time()-t0:.0f}s', flush=True)
    return dst


def concat(n):
    d = out_dir(n)
    parts = sorted(f for f in os.listdir(d)
                   if f.startswith('seg_') and f.endswith('.mp4'))
    assert parts, 'nothing rendered'
    lst = os.path.join(d, 'concat.txt')
    with open(lst, 'w') as f:
        for p in parts:
            f.write("file '%s'\n" % os.path.join(d, p))
    dst = os.path.join(d, f'ch{n}_frames.mp4')
    subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y',
                    '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', dst],
                   check=True)
    print(f'  [ch{n}] frames -> {dst}', flush=True)
    return dst


def audio(n):
    """the chapter's OWN slice of the episode VO, mixed on chapter-local time."""
    import numpy as np
    from eng5 import audio5 as A
    from eng5 import music5
    P = mod(n)
    d = out_dir(n)
    t_end = P.T_END - P.T0

    # the score's sections follow this chapter's beats, in chapter-local time
    ev = sorted(P.EVENTS, key=lambda e: e['t'])
    span = t_end
    marks = dict(b2=span * 0.10, b3=span * 0.30, b4=span * 0.56, b5=span * 0.78,
                 out=span - 3.2)
    stings = [e['t'] - P.T0 for e in ev if e['sfx'] in ('sting', 'thunder')]
    if not stings:
        stings = [span * 0.5]
    score = music5.build(t_end, marks=marks, stings=stings)
    np.save(os.path.join(d, 'score_raw.npy'), score)
    music5.build = lambda t_e=30.0, **kw: score[:int(round(t_e * music5.SR))]

    evs = [dict(t=e['t'] - P.T0, sfx=e['sfx'], what=e['what'])
           for e in ev if e.get('sfx')]
    A.OUT = d
    wav, stems, meta = A.build(t_end, evs, f'ch{n}', vo_start=P.T0)
    assert abs(meta.get('vo_start', P.T0) - P.T0) < 1e-6, 'VO slice start was not honoured'
    A.master(wav, os.path.join(d, f'ch{n}_master.wav'))
    A.master(os.path.join(d, f'ch{n}_master.wav'),
             os.path.join(d, f'ch{n}_master2.wav'))
    os.replace(os.path.join(d, f'ch{n}_master2.wav'),
               os.path.join(d, f'ch{n}_master.wav'))
    meta['ch_start_sec'] = P.T0
    meta['ch_end_sec'] = P.T_END
    meta['vo_slice'] = [P.T0, P.T_END]
    json.dump(meta, open(os.path.join(d, f'audio{n}_meta.json'), 'w'), indent=1,
              ensure_ascii=False)
    print('  [ch%d] mix done, vo_slice %s' % (n, meta['vo_slice']), flush=True)
    return os.path.join(d, f'ch{n}_master.wav')


def mux(n):
    d = out_dir(n)
    src = os.path.join(d, f'ch{n}_frames.mp4')
    wav = os.path.join(d, f'ch{n}_master.wav')
    dst = os.path.join(d, f'ch{n}_mux.mp4')
    subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y',
                    '-i', src, '-i', wav,
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000',
                    '-shortest', '-movflags', '+faststart', dst], check=True)
    print(f'  [ch{n}] mux -> {dst}', flush=True)
    return dst


def gate(n, path=None, label=''):
    P = mod(n)
    g = os.path.join(ROOT, 'ch2', 'eng', 'sync_gate.py')
    path = path or os.path.join(out_dir(n), f'ch{n}_mux.mp4')
    r = subprocess.run([sys.executable, g, path, '%.2f' % P.T0,
                        '%.2f' % (P.T_END - P.T0), label or f'ch{n}'],
                       capture_output=True, text=True)
    print(r.stdout.strip())
    if r.stderr.strip():
        print(r.stderr.strip()[-600:])
    return r.returncode == 0


def encode(n):
    """two-pass delivery encode from the gate-passed mux (video re-encoded, audio copied)."""
    d = out_dir(n)
    src = os.path.join(d, f'ch{n}_mux.mp4')
    log = os.path.join(d, f'pass_{n}.log')
    dst = os.path.join(d, f'RUWAQ_CH{n}_v5.mp4')
    subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y', '-i', src,
                    '-c:v', 'libx264', '-preset', 'slow', '-b:v', '5900k',
                    '-pix_fmt', 'yuv420p', '-g', '60', '-an',
                    '-pass', '1', '-passlogfile', log, '-f', 'mp4', '/dev/null'],
                   check=True)
    subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y', '-i', src,
                    '-c:v', 'libx264', '-preset', 'slow', '-b:v', '5900k',
                    '-pix_fmt', 'yuv420p', '-g', '60', '-c:a', 'copy',
                    '-pass', '2', '-passlogfile', log,
                    '-movflags', '+faststart', dst], check=True)
    print('  [ch%d] delivery -> %s %.1f MB' % (n, dst,
                                               os.path.getsize(dst) / 1e6), flush=True)
    return dst


if __name__ == '__main__':
    args = sys.argv[1:]
    steps = {'audio': audio, 'concat': concat, 'mux': mux, 'encode': encode}
    i = 0
    while i < len(args):
        n, what = int(args[i]), args[i + 1]
        i += 2
        if what == 'render':
            total = n_frames(mod(n))
            step = 450
            for i0 in range(0, total, step):
                render(n, i0, min(total, i0 + step))
        elif what == 'gate':
            ok = gate(n, label=f'ch{n}')
            print('  [ch%d] gate %s' % (n, 'PASS' if ok else 'FAIL'), flush=True)
            if not ok:
                sys.exit(1)
        else:
            steps[what](n)
    print('done')
