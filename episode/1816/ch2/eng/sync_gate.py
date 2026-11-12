#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sync_gate.py — prove a chapter's audio is ITS OWN slice of the episode VO.

This is the check that was missing. It compares the delivered file's soundtrack, envelope
for envelope, against three candidate slices of the episode VO and refuses the file unless
the chapter's own slice wins by a wide margin at zero lag:

  * the chapter's own range  [start, start+len)   <- must win
  * the episode from 0:00                          <- the bug that shipped
  * one chapter-length earlier and later           <- off-by-one-chapter guards

It also re-times the speech: the audio at t=0 must align with the VO at `start` to within
a fraction of a frame, so a file that is merely the right chapter but slipped cannot pass.
"""
import sys
import numpy as np
import subprocess

FF = '/home/user/ffmpeg'
SR = 48000
VO = '/home/user/Riwaq_System_Repo/google_drive/1816_OMAR_VO_FULL_MIX_48k.flac'


def decode(path, ss=0.0, dur=None):
    cmd = [FF, '-v', 'error', '-ss', f'{ss:.6f}', '-i', path]
    if dur:
        cmd += ['-t', f'{dur:.6f}']
    cmd += ['-f', 'f32le', '-ac', '1', '-ar', str(SR), '-']
    raw = subprocess.run(cmd, capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


def env(x, hop=240):
    n = len(x) // hop
    return np.abs(x[:n * hop].reshape(n, hop)).mean(1)


def score(a, b):
    m = min(len(a), len(b))
    a, b = a[:m], b[:m]
    if a.std() < 1e-9 or b.std() < 1e-9:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def lag(a, b, maxlag=6000):
    """best lag in samples of a relative to b, by envelope cross-correlation"""
    a = a - a.mean()
    b = b - b.mean()
    n = 1 << int(np.ceil(np.log2(len(a) + len(b))))
    c = np.fft.irfft(np.fft.rfft(b, n) * np.conj(np.fft.rfft(a, n)), n)
    c = np.concatenate([c[-maxlag:], c[:maxlag]])
    return int(np.arange(-maxlag, maxlag)[np.argmax(c)])


def check(mp4, start, length, label=''):
    A = env(decode(mp4))
    dur = len(A) * 240 / SR
    cand = {
        f'chapter slice [{start:.2f}, {start + dur:.2f})': env(decode(VO, start, dur + 0.5)),
        'episode from 0:00': env(decode(VO, 0.0, dur + 0.5)),
        f'one chapter earlier [{start - dur:.2f})': env(decode(VO, max(0.0, start - dur), dur + 0.5)),
        f'one chapter later [{start + dur:.2f})': env(decode(VO, start + dur, dur + 0.5)),
    }
    res = {k: score(A, v) for k, v in cand.items()}
    own_key = f'chapter slice [{start:.2f}, {start + dur:.2f})'
    own = res[own_key]
    others = max(v for k, v in res.items() if k != own_key)
    l = lag(A, cand[own_key]) * 240 / SR
    ok = own >= 0.80 and own - others >= 0.30 and abs(l) <= 0.042
    print(f'--- {label or mp4}')
    print(f'    length {dur:.2f}s, expected {length:.2f}s'
          f' {"OK" if abs(dur - length) < 0.10 else "MISMATCH"}')
    for k, v in res.items():
        print(f'    {v:+.3f}  {k}' + ('   <- must win' if k == own_key else ''))
    print(f'    margin over the best wrong slice: {own - others:+.3f}')
    print(f'    residual slip: {l:+.3f}s')
    print(f'    SYNC {"PASS" if ok else "FAIL"}')
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    mp4, start, length = a[0], float(a[1]), float(a[2])
    sys.exit(0 if check(mp4, start, length, a[3] if len(a) > 3 else '') else 1)
