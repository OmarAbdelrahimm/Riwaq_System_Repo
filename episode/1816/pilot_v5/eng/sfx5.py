#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eng5/sfx5.py — the text-hit design for v5.

v4's text hits were sharp, bright and clicksome, which the review called out as harsh.
Every voice here is a soft-body sound:

  paper     filtered noise with a slow attack and a long tail -- a sheet sliding on felt
  wood      a low damped thud with almost no click -- a strip of card being laid down
  fabric    band-limited noise -- a sleeve or a cloth
  thunder   a long, low swell

No oscillator click, no short bright transient, no beep. `LEVEL_DB` is the design level
relative to the VOICE rms; eng5/audio5.py calibrates each hit against the speech it sits
under, so the delivered numbers are measured, not assumed.
"""
import numpy as np

SR = 48000


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def noise(dur, seed=1):
    return np.random.default_rng(seed).normal(0, 1, int(dur * SR))


def lowpass(x, fc, order=2):
    X = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1.0 / (1.0 + (fr / fc) ** (2 * order))
    return np.fft.irfft(X, len(x))


def highpass(x, fc, order=2):
    X = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1.0 / (1.0 + (fc / np.maximum(fr, 1e-6)) ** (2 * order))
    return np.fft.irfft(X, len(x))


def bandpass(x, lo, hi, order=2):
    return highpass(lowpass(x, hi, order), lo, order)


def env(dur, attack, decay, curve=2.0):
    t = t_axis(dur)
    a = np.clip(t / max(attack, 1e-4), 0, 1) ** 0.6
    d = np.exp(-np.maximum(0.0, t - attack) / max(decay, 1e-4))
    return a * d


def stereo(x, width=0.0, seed=2):
    if width <= 0:
        return np.stack([x, x], 1).astype(np.float32)
    r = np.random.default_rng(seed).normal(0, 1, len(x))
    r = lowpass(r, 3000.0)
    r /= max(1e-9, np.abs(r).max())
    l = x * (1 - width * 0.5) + r * width * 0.05 * np.abs(x).max()
    rr = x * (1 - width * 0.5) - r * width * 0.05 * np.abs(x).max()
    return np.stack([l, rr], 1).astype(np.float32)


def norm(x):
    m = np.abs(x).max()
    return x / m if m > 0 else x


# ---------------------------------------------------------------- the kit
def paper_slide(dur=0.55, seed=11, lo=600.0, hi=4200.0):
    """a sheet of paper sliding: soft attack, grainy middle, long gentle tail"""
    t = t_axis(dur)
    n = noise(dur, seed)
    body = bandpass(n, lo, hi)
    # a slight "grain" modulation makes it read as paper rather than as static
    grain = 1.0 + 0.35 * np.sin(2 * np.pi * 21.0 * t + 1.0) * np.sin(2 * np.pi * 7.0 * t)
    e = env(dur, 0.09, 0.16, 1.4)
    x = body * e * grain
    x = lowpass(x, 7000.0)
    return stereo(norm(x) * 0.5, width=0.35, seed=seed + 1)


def paper_lift(dur=0.50, seed=21):
    """the sheet leaving the table: softer and shorter than the slide"""
    t = t_axis(dur)
    n = noise(dur, seed)
    body = bandpass(n, 700.0, 3600.0)
    e = env(dur, 0.06, 0.11, 1.2)
    x = lowpass(body * e, 6000.0)
    return stereo(norm(x) * 0.42, width=0.30, seed=seed + 3)


def wood_tap(dur=0.18, f=196.0, seed=31):
    """a strip laid down: a damped low body, no click at the front"""
    t = t_axis(dur)
    body = (np.sin(2 * np.pi * f * t) * np.exp(-t * 22.0)
            + 0.35 * np.sin(2 * np.pi * f * 2.02 * t) * np.exp(-t * 33.0))
    body += 0.06 * bandpass(noise(dur, seed), 300.0, 1400.0) * np.exp(-t * 40.0)
    body *= np.clip(t / 0.012, 0, 1)          # 12 ms fade-in removes the click
    return stereo(norm(body) * 0.55, width=0.15, seed=seed)


def needle_drop(dur=0.22, seed=41):
    """a fine pointer settling onto paper"""
    t = t_axis(dur)
    body = np.sin(2 * np.pi * 620.0 * t) * np.exp(-t * 30.0)
    body += 0.4 * bandpass(noise(dur, seed), 800.0, 2600.0) * np.exp(-t * 45.0)
    body *= np.clip(t / 0.010, 0, 1)
    return stereo(norm(body) * 0.40, width=0.10, seed=seed)


def thread_draw(dur=0.90, seed=51):
    """a thread pulled across a map: a narrow band of noise that swells and fades"""
    t = t_axis(dur)
    n = noise(dur, seed)
    drift = 900.0 + 500.0 * (t / dur)
    X = np.fft.rfft(n)
    fr = np.fft.rfftfreq(len(n), 1 / SR)
    X *= np.exp(-((fr - drift.mean()) / 900.0) ** 2)
    body = np.fft.irfft(X, len(n))
    e = np.clip(t / 0.18, 0, 1) * np.clip((dur - t) / 0.30, 0, 1)
    return stereo(norm(body * e) * 0.45, width=0.25, seed=seed)


def sleet(dur=1.10, seed=61):
    """fine ice on a window: filtered noise, no individual ticks"""
    t = t_axis(dur)
    n = noise(dur, seed)
    body = bandpass(n, 2200.0, 7000.0)
    body *= 0.6 + 0.4 * np.sin(2 * np.pi * 3.0 * t)
    e = np.clip(t / 0.35, 0, 1) * np.clip((dur - t) / 0.45, 0, 1)
    return stereo(norm(body * e) * 0.34, width=0.55, seed=seed + 1)


def water(dur=1.30, seed=71):
    """rain at full weight: low, wide, and soft"""
    t = t_axis(dur)
    n = noise(dur, seed)
    body = bandpass(n, 300.0, 2600.0)
    body = lowpass(body, 2200.0)
    e = np.clip(t / 0.30, 0, 1) * np.clip((dur - t) / 0.50, 0, 1)
    return stereo(norm(body * e) * 0.36, width=0.70, seed=seed + 2)


def stamp(dur=0.50, f=118.0, seed=81):
    """a rubber stamp: a soft, low, rounded body rather than a thump with a click"""
    t = t_axis(dur)
    body = np.sin(2 * np.pi * f * t) * np.exp(-t * 14.0)
    body += 0.30 * np.sin(2 * np.pi * f * 1.98 * t) * np.exp(-t * 20.0)
    body += 0.10 * bandpass(noise(dur, seed), 120.0, 900.0) * np.exp(-t * 16.0)
    body *= np.clip(t / 0.015, 0, 1)
    return stereo(norm(body) * 0.60, width=0.20, seed=seed)


def sting(dur=2.40, seed=91):
    """the brand sting: a low swell with a soft bell on top, no attack spike"""
    t = t_axis(dur)
    x = np.zeros_like(t)
    for f, a in ((73.4, 1.0), (110.0, 0.55), (146.8, 0.32), (220.0, 0.18)):
        x += a * np.sin(2 * np.pi * f * t) * np.exp(-t * 1.4)
    x *= np.clip(t / 0.10, 0, 1)
    for f, a, d in ((587.3, 0.16, 3.2), (880.0, 0.09, 4.6)):
        x += a * np.sin(2 * np.pi * f * t) * np.exp(-t * d) * np.clip(t / 0.03, 0, 1)
    return stereo(norm(x) * 0.55, width=0.30, seed=seed)


def thunder(dur=2.60, seed=101):
    """distant thunder: a slow, low roar"""
    t = t_axis(dur)
    n = noise(dur, seed)
    body = lowpass(n, 180.0, order=2) * 6.0
    body += 0.5 * lowpass(n, 420.0, order=2)
    e = np.clip(t / 0.45, 0, 1) * np.exp(-np.maximum(0, t - 0.45) / 1.5)
    mod = 0.75 + 0.25 * np.sin(2 * np.pi * 0.9 * t + 0.4)
    return stereo(norm(body * e * mod) * 0.5, width=0.6, seed=seed)


KIT = dict(paper_in=paper_slide, paper_out=paper_lift, pin=wood_tap, needle=needle_drop,
           thread_draw=thread_draw, sleet=sleet, water=water, stamp=stamp,
           sting=sting, thunder=thunder)

# design levels, relative to the VOICE rms. audio5 calibrates each hit against the
# speech in its own window for the text hits, so these are targets, not fader guesses.
LEVEL_DB = dict(paper_in=-15.0, paper_out=-17.0, pin=-18.0, needle=-19.0,
                thread_draw=-17.5, sleet=-21.0, water=-18.5, stamp=-16.0,
                sting=-10.0, thunder=-13.0)


if __name__ == '__main__':
    for k, fn in KIT.items():
        x = fn()[:, 0]
        X = np.abs(np.fft.rfft(x))
        fr = np.fft.rfftfreq(len(x), 1 / SR)
        print(f'{k:12s} {len(x)/SR:5.2f}s  centroid {(X*fr).sum()/X.sum():6.0f} Hz  '
              f'{LEVEL_DB[k]:+5.1f} dB')
