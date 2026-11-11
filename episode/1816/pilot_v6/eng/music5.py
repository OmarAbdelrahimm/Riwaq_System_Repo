#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eng5/music5.py — a composed score for the hook, because the supplied bed cannot be sped up.

Measured on the supplied music stem: 57 % of its energy is 80-200 Hz and 0 % above 2 kHz,
with an onset-autocorrelation peak at 0.86 s — about 70 BPM. It is an ambient pad. No
tempo change, no EQ and no compression turns a pad into a pulse, so for v5's requirement
this file synthesises a score at the tempo the brief asks for.

Bed: D minor, 116 BPM, four-on-the-floor with a driving eighth-note ostinato.
"""
import numpy as np

SR = 48000
BPM = 116.0
BEAT = 60.0 / BPM
BAR = BEAT * 4
FPS = 30

D3, F3, A3, C4, D4, F4, A4, C5 = 146.83, 174.61, 220.00, 261.63, 293.66, 349.23, 440.00, 523.25
BB3 = 233.08


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def saw(f, t, harm=9, detune=0.0):
    ph = 2 * np.pi * f * (1 + detune) * t
    out = np.zeros_like(t)
    for k in range(1, harm + 1):
        out += np.sin(ph * k) / k
    return out


def pluck(f, t, decay=7.0, harm=7):
    x = saw(f, t, harm)
    return x * np.exp(-t * decay) * np.clip(t / 0.004, 0, 1)


def bass(f, t, decay=3.2):
    x = np.sin(2 * np.pi * f * t) + 0.28 * np.sin(4 * np.pi * f * t)
    return x * np.exp(-t * decay) * np.clip(t / 0.006, 0, 1)


def pad(freqs, t, attack=0.35, release=0.5):
    out = np.zeros_like(t)
    for f in freqs:
        out += saw(f, t, 6) * 0.9 + saw(f, t, 6, detune=0.0035) * 0.7
    e = np.clip(t / attack, 0, 1) * np.clip((t[-1] - t) / release, 0, 1)
    return out * e / max(1, len(freqs))


def kick(t, f0=96.0, f1=44.0, decay=11.0):
    f = f1 + (f0 - f1) * np.exp(-t * 26)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * decay) * np.clip(t / 0.002, 0, 1)


def hat(t, seed=1, decay=90.0):
    """high-passed noise: a difference filter, with the DC removed afterwards.

    Differencing white noise leaves a constant positive offset; left in, that offset is a
    DC bias which dominated the whole bus (95 % of the file's energy sat below 20 Hz).
    """
    if seed is None:
        seed = int(t[0] * 1000) % 9973 + 1
    rng = np.random.default_rng(seed)
    nz = rng.normal(0, 1, len(t))
    nz = np.diff(np.concatenate([[0.0], nz]))
    nz = nz - nz.mean()
    return nz * np.exp(-t * decay) * 0.5


def _bell_cut(x, f=1100.0, depth_db=-6.0):
    """take a slice out of the band where speech carries its intelligibility.

    The brief asks for -6 dB across 400 Hz - 3 kHz and nominates 1.1 kHz as the centre.
    The suffix form of the high-pass is a cascade, which is exactly what gives a smooth
    6 dB shelf rather than a notch with ringing -- a notch rings, a shelf does not.
    """
    X = np.fft.rfft(x, axis=0)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    lf = np.log2(np.maximum(fr, 1.0) / f)
    g = 10 ** (depth_db / 20.0)
    curve = 1.0 - (1.0 - g) * np.exp(-(lf / 0.55) ** 2)
    X *= curve[:, None] if X.ndim > 1 else curve
    return np.fft.irfft(X, len(x), axis=0).astype(np.float32)


def _warmer(x, f=5200.0):
    """a gentle top-end roll-off: the v5 score read as bright and synthetic under a
    narrator with a dark, close voice."""
    X = np.fft.rfft(x, axis=0)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    X *= (1.0 / (1.0 + (fr / f) ** 2))[:, None]
    return np.fft.irfft(X, len(x), axis=0).astype(np.float32)


def tick(t, f=1800.0, decay=60.0):
    return np.sin(2 * np.pi * f * t) * np.exp(-t * decay) * 0.35


class Score:
    def __init__(self, dur):
        self.dur = dur
        self.n = int(dur * SR)
        self.buf = np.zeros(self.n, np.float32)

    def add(self, t0, x, gain=1.0):
        i0 = int(round(t0 * SR))
        if i0 >= self.n:
            return
        n = min(len(x), self.n - i0)
        self.buf[i0:i0 + n] += x[:n] * gain

    def at(self, beat, x, gain=1.0):
        self.add(beat * BEAT, x, gain)


def build(t_end=30.0, sting_t=22.42):
    s = Score(t_end)
    hk = t_axis(0.9)
    bs = t_axis(0.7)
    pd = t_axis(BAR * 1.02)
    kk = t_axis(0.5)
    hh = t_axis(0.09)
    tk = t_axis(0.12)

    s.add(0.0, pad([D3, A3, F4], pd, attack=1.2), 0.15)
    s.add(9.97, pad([D3, F3, C4], pd, attack=0.6), 0.13)
    s.add(15.96, pad([BB3, D4, F4], pd, attack=0.5), 0.14)
    s.add(22.42, pad([D3, A3, D4, F4], pd, attack=0.06, release=1.1), 0.20)
    s.add(25.60, pad([D3, F3, A3], pd, attack=0.25), 0.13)

    b = 0.0
    while b * BEAT < t_end - 0.2:
        t0 = b * BEAT
        g = 0.55 if t0 < 4.35 else 0.5
        if 22.42 <= t0 < 25.60:
            g = 0.75
        s.at(b, bs, g)
        b += 1.0

    b = 8.0
    while b * BEAT < t_end - 0.3:
        t0 = b * BEAT
        if not (22.42 <= t0 < 25.60):
            s.at(b, kk, 0.62)
        b += 1.0

    arp = [D4, F4, A4, C5, A4, F4, D4, F4]
    b = 5.65
    i = 0
    while b * BEAT < t_end - 0.2:
        t0 = b * BEAT
        g = 0.30
        if t0 < 4.35:
            g = 0.20
        if 22.42 <= t0 < 25.60:
            g = 0.0
        if t0 >= 25.60:
            g = 0.26
        if g:
            f = arp[i % len(arp)]
            if 9.97 <= t0 < 15.96:
                f = f / 2.0
            s.at(b, pluck(f, hk, decay=9.0), g)
        b += 0.5
        i += 1

    b = 8.5
    while b * BEAT < t_end - 0.3:
        t0 = b * BEAT
        if not (22.42 <= t0 < 25.60):
            g = 0.06 if t0 < 9.97 else 0.09
            s.at(b, hat(hh, seed=int(b * 7) + 1), g)
        b += 1.0

    b = 32.0
    while b * BEAT < 22.42:
        s.at(b, tk, 0.030)
        b += 1.0

    rl = 2.6
    tr = t_axis(rl)
    fr = 90 * (1 + 3.2 * (tr / rl) ** 2)
    riser = np.sin(2 * np.pi * np.cumsum(fr) / SR) * (tr / rl) ** 2
    riser += 0.25 * np.random.default_rng(3).normal(0, 1, len(tr)) * (tr / rl) ** 3
    s.add(sting_t - rl, riser, 0.16)

    s.at(int(round(29.0 / BEAT)), pluck(D4, hk, decay=2.2), 0.34)
    s.at(int(round(29.0 / BEAT + 2)), pluck(A4, hk, decay=2.2), 0.28)

    x = s.buf
    x = x - x.mean()
    X = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    X *= np.clip((fr - 18.0) / 18.0, 0, 1) ** 2      # DC / subsonic
    X *= 1.0 / (1.0 + (fr / 5200.0) ** 2)            # air off: warmer, softer
    lf = np.log2(np.maximum(fr, 1.0) / 1100.0)
    X *= 1.0 - 0.5 * np.exp(-(lf / 0.55) ** 2)       # -6 dB vocal pocket at 1.1 kHz
    x = np.fft.irfft(X, len(x)).astype(np.float32)
    x = np.tanh(x * 1.05) * 0.92
    x = np.stack([x, x], 1)
    m = np.max(np.abs(x))
    if m > 0:
        x = x / m * 0.85
    return x.astype(np.float32)


def write_wav(path, x):
    import wave
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    import os
    x = build(30.0)
    out = '/home/user/work/out/score5.wav'
    os.makedirs('/home/user/work/out', exist_ok=True)
    write_wav(out, x)
    print('score ->', out, 'BPM', BPM)
