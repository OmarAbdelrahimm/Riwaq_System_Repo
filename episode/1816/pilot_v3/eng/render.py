#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
eng/render.py — frame renderer + instrumentation, piping raw frames into ffmpeg.

Every frame's layer stack is recorded from the same list the compositor consumed, so
QA counts what was actually drawn rather than trusting the shot notes. Text on paper
props is measured on the same frame with the prop's ink hidden, so the background is
the real paper, not a guess.
"""
import json, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from PIL import Image
from eng.core import W, H, FPS, COL, hexrgb, TextReveal, contrast_ratio, bg_stats
import eng.pilot as P

OUT = '/home/user/work/out'
os.makedirs(OUT, exist_ok=True)
FF = '/home/user/ffmpeg'


def text_layers(t):
    outs = []
    for (t0, t1, txt, y, color, scrim, size, fk, mw) in P.TEXTS:
        if not (t0 <= t <= t1 + 0.30):
            continue
        k_in = min(1.0, (t - t0) / 0.38)
        k_out = 1.0 if t < t1 - 0.28 else max(0.0, (t1 + 0.28 - t) / 0.28)
        k = min(k_in, k_out)
        if k <= 0.001:
            continue
        tr = TextReveal(txt, size=size, color=color, fontkey=fk, max_words=mw, scrim=scrim)
        lay = tr.draw(progress=k_in, y=None if y is None else int(H * y) + int(12 * (1 - k_in)),
                      alpha=int(255 * min(1.0, k_out)))
        outs.append((txt, lay, tr, k_out))
    return outs


def frame_at(shots, fi, suppress=()):
    t = fi / FPS
    sh = next((s for s in shots if s.t0 <= t < s.t1), shots[-1])
    lt = t - sh.t0
    try:
        raw = sh.render(lt, fi, suppress=suppress)
    except TypeError:
        raw = sh.render(lt, fi)
    ls = [l for l in raw if l is not None and l.im is not None]
    im = None
    for l in ls:
        im = l.im.convert('RGBA') if im is None else Image.alpha_composite(im, l.im.convert('RGBA'))
    rgb = im.convert('RGB')
    leak = 0.09 if sh.name in ('S1_wheat', 'S7_sting', 'S9_return') else 0.03
    rgb = P.FILM.apply(rgb, fi, leak)
    names = [l.name for l in ls] + ['film.grain+leak']
    txts = text_layers(t)
    for (txt, lay, tr, ko) in txts:
        rgb = Image.alpha_composite(rgb.convert('RGBA'), lay).convert('RGB')
    if txts:
        names = names + ['kinetic.text']
    if t >= 24.0:
        a = min(1.0, (t - 24.0) / 0.4)
        rgb = Image.alpha_composite(rgb.convert('RGBA'), P.LOGO.draw(alpha=a)).convert('RGB')
        names = names + ['brand.logo']
    return sh, t, rgb, sorted(set(names)), txts, ls


def render(t_end=30.0, tag='pilot', verbose=True):
    shots = P.build_shots()
    n = int(round(t_end * FPS))
    mp4 = os.path.join(OUT, f'PILOT_{tag}.mp4')
    cmd = [FF, '-hide_banner', '-loglevel', 'error', '-y',
           '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p',
           '-movflags', '+faststart', mp4]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    recs = []
    prev = None
    static_run = 0
    t0 = time.time()
    for fi in range(n):
        sh, t, rgb, names, txts, ls = frame_at(shots, fi)
        proc.stdin.write(rgb.tobytes())
        g = np.asarray(rgb.convert('L'), np.uint8)
        diff = 999.0 if prev is None else float(
            np.abs(g.astype(np.int16) - prev.astype(np.int16)).mean())
        static_run = static_run + 1 if diff < 0.35 else 0
        prev = g
        rec = dict(fi=fi, t=round(t, 3), shot=sh.name, cam=sh.cam, layers=len(names),
                   live=names, frame_diff=round(diff, 3), static_run=static_run)
        # every paper-borne text reports its own ink box; only measure it once the
        # prop has faded up, or the ratio describes a half-transparent sprite
        propbox = [(l.info.get('text'), tuple(l.info.get('box')), l.info.get('fg'))
                   for l in ls if getattr(l, 'info', {}).get('text')
                   and l.info.get('k', 1.0) >= 0.99]
        if propbox and fi % 5 == 0:
            _, _, bare, _, _, _ = frame_at(shots, fi, suppress={'prop.text'})
            cs = []
            for (ptxt, pbox, pfg) in propbox:
                b = bg_stats(bare, pbox, percentile=85)
                cs.append(dict(text=ptxt, fg=list(pfg), bg_p85=list(b),
                               ratio=round(contrast_ratio(pfg, b), 2), kind='prop'))
            rec['contrast'] = cs
        if txts and fi % 5 == 0:
            _, _, bare, _, _, _ = frame_at(shots, fi, suppress={'kinetic.text'})
            cs = []
            for (txt, lay, tr, ko) in txts:
                x0, yy = tr.anchor(None, None)
                b = bg_stats(bare, (x0 - 6, yy - 6, x0 + tr.tw + 6, yy + tr.th + 12),
                             percentile=85)
                cs.append(dict(text=txt, fg=list(hexrgb(COL[tr.color])), bg_p85=list(b),
                               ratio=round(contrast_ratio(hexrgb(COL[tr.color]), b), 2),
                               kind='kinetic'))
            rec['contrast'] = rec.get('contrast', []) + cs
        recs.append(rec)
        if verbose and fi % 60 == 0:
            print(f'  {fi:4d}/{n}  t={t:5.2f}  {sh.name:16s} layers={len(names)} '
                  f'diff={diff:5.2f}', flush=True)
    proc.stdin.close()
    proc.wait()
    with open(os.path.join(OUT, f'layerlog_{tag}.jsonl'), 'w') as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f'rendered {n} frames in {time.time() - t0:.1f}s -> {mp4}')
    return recs, mp4


if __name__ == '__main__':
    end = float(sys.argv[1]) if len(sys.argv) > 1 else 30.0
    tag = sys.argv[2] if len(sys.argv) > 2 else 'pilot'
    render(t_end=end, tag=tag)
