"""HARUN v4 — المؤثرات الصوتية + موسيقى الخلفية (توليد رقمي، بلا حقوق طرف ثالث).

هوية رواق الصوتية: حجاز على «د»، درون دافئ، نقرات عود، هواء ونحاس.

المخطوطة:
  0.06s   معرّف البداية: نقرة عود + رنين خفيف + ثَم
  37.55s  تغميق: ووش ناعم + ثَم خفيف
  125.80s تغميق: ووش ناعم + ثَم خفيف
  131.05s بطاقة «اللغز»: ووش + رنين صاعد + ثَم
  157.90s الخاتمة: ووش + عود منفرد ينطفئ

المخرجات → public/projects/HARUN_001/audio_v4/{bed,sfx}.wav
"""
from __future__ import annotations

import math
import wave
from pathlib import Path

import numpy as np

SR = 48000
DUR = 159.45
OUT = Path("/home/user/Riwaq_System_Repo/public/projects/HARUN_001/audio_v4")

D2, A2, D3 = 73.42, 110.00, 146.83
Eb3, Fs3, G3, A3, Bb3, C4, D4 = 155.56, 185.00, 196.00, 220.00, 233.08, 261.63, 293.66
RNG = np.random.default_rng(20261028)


def adsr(n: int, a: float, d: float, s: float, r: float) -> np.ndarray:
    e = np.ones(n) * s
    an, dn, rn = max(1, int(a*SR)), max(1, int(d*SR)), max(1, int(r*SR))
    e[:min(an, n)] = np.linspace(0, 1, min(an, n))
    if an + dn < n:
        e[an:an+dn] = np.linspace(1, s, dn)
    if rn < n:
        e[-rn:] *= np.linspace(1, 0, rn)
    return e


def pluck(f: float, dur: float, amp: float = 0.3) -> np.ndarray:
    n = int(dur*SR)
    t = np.arange(n)/SR
    sig = (np.sin(2*math.pi*f*t) + 0.30*np.sin(2*math.pi*f*2*t+0.4)
           + 0.12*np.sin(2*math.pi*f*3*t+0.9))
    sig *= np.exp(-t/(dur*0.30))
    sig[:int(0.008*SR)] += RNG.normal(0, 0.04, int(0.008*SR))
    return amp*sig/(np.max(np.abs(sig))+1e-9)


def drone(dur: float, amp: float = 0.2) -> np.ndarray:
    n = int(dur*SR)
    t = np.arange(n)/SR
    sig = np.zeros(n)
    for f, w in ((D2, 1.0), (A2, 0.55), (D3, 0.30), (Fs3, 0.10)):
        vib = 1.0 + 0.0016*np.sin(2*math.pi*0.13*t)
        sig += w*np.sin(2*math.pi*f*t*vib) + 0.4*w*np.sin(2*math.pi*f*1.003*t)
    return amp*(sig/2.2)*adsr(n, 2.4, 3.0, 0.9, 3.5)


def whoosh(dur: float = 0.9, amp: float = 0.34) -> np.ndarray:
    n = int(dur*SR)
    t = np.arange(n)/SR
    noise = RNG.normal(0, 1, n)
    lo = np.convolve(noise, np.ones(24)/24, mode="same")
    hi = noise - np.convolve(noise, np.ones(180)/180, mode="same")
    sig = 0.55*lo + 0.45*hi
    sig *= 0.6 + 0.4*np.sin(2*math.pi*(380+1500*(t/dur)**1.4)*t/240)
    sig *= np.sin(np.pi*np.clip(t/dur, 0, 1))**1.8
    return amp*sig/(np.max(np.abs(sig))+1e-9)


def bell(f: float, dur: float = 2.4, amp: float = 0.22) -> np.ndarray:
    n = int(dur*SR)
    t = np.arange(n)/SR
    sig = np.zeros(n)
    for k, w in ((1, 1.0), (2.01, 0.45), (3.02, 0.22), (4.9, 0.10), (6.7, 0.05)):
        sig += w*np.sin(2*math.pi*f*k*t)
    sig *= np.exp(-t/(dur*0.22))
    return amp*sig/(np.max(np.abs(sig))+1e-9)


def thump(f: float = 58.0, dur: float = 1.2, amp: float = 0.30) -> np.ndarray:
    n = int(dur*SR)
    t = np.arange(n)/SR
    sig = np.sin(2*math.pi*f*t*(1-0.22*t/dur))*np.exp(-t/(dur*0.16))
    return amp*sig/(np.max(np.abs(sig))+1e-9)


def riser(dur: float = 1.0, amp: float = 0.14) -> np.ndarray:
    """صعود ضجيحي خفيف ينتهي عند لحظة الانتقال."""
    n = int(dur*SR)
    t = np.arange(n)/SR
    noise = RNG.normal(0, 1, n)
    band = np.convolve(noise, np.ones(60)/60, mode="same")
    sig = band * np.linspace(0.05, 1.0, n)**2
    sig *= np.sin(np.pi*np.clip(t/dur, 0, 1))**0.7
    return amp*sig/(np.max(np.abs(sig))+1e-9)


def tick(amp: float = 0.12) -> np.ndarray:
    """نقرة خشب قصيرة (٦٠ مللي) تُسمع بوضوح ولا تُشتّت."""
    n = int(0.075*SR)
    t = np.arange(n)/SR
    sig = (np.sin(2*math.pi*320*t)*0.7 + np.sin(2*math.pi*680*t)*0.3)
    sig *= np.exp(-t/0.012)
    sig += 0.35*RNG.normal(0, 1, n)*np.exp(-t/0.004)
    return amp*sig/(np.max(np.abs(sig))+1e-9)


def place(buf: np.ndarray, sig: np.ndarray, at: float, gain: float = 1.0) -> None:
    i = int(at*SR)
    n = min(len(sig), len(buf)-i)
    if i < len(buf) and n > 0:
        buf[i:i+n] += sig[:n]*gain


def save(path: Path, data: np.ndarray) -> None:
    pcm = (np.clip(data, -1, 1)*32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(path.name, f"{path.stat().st_size/1e6:.1f} MB", f"{len(data)/SR:.2f}s")


def bed() -> np.ndarray:
    n = int(DUR*SR)
    out = np.zeros(n)
    chords = [(D3, A3, D4), (D3, Fs3, A3), (D3, G3, Bb3), (D3, Eb3, A3)]
    t, k = 0.0, 0
    while t < DUR:
        place(out, drone(min(23.0, DUR-t), 0.16), t)
        k += 1
        t += 20.0
    rng = np.random.default_rng(7)
    notes = [D4, C4, Bb3, A3, G3, Fs3, Eb3, D3]
    tt = 4.0
    while tt < DUR - 4:
        place(out, pluck(notes[rng.integers(0, len(notes))], 2.6, 0.10), tt, 0.55)
        tt += float(rng.uniform(6.5, 11.0))
    air = np.convolve(RNG.normal(0, 1, n), np.ones(400)/400, mode="same")
    out += 0.035*air
    f = int(2.5*SR)
    out[:f] *= np.linspace(0, 1, f)
    out[-int(4.0*SR):] *= np.linspace(1, 0, int(4.0*SR))
    return out


def sfx() -> np.ndarray:
    n = int(DUR*SR)
    out = np.zeros(n)

    # ١) المعرّف (0.25 – 1.70)
    place(out, pluck(D4, 2.2, 0.34), 0.22, 0.95)
    place(out, bell(A3, 2.8, 0.16), 0.25)
    place(out, thump(D2, 1.1, 0.22), 0.20)

    # ٢) الانتقالات الكبيرة: صعود ← وش ← ضربة منخفضة
    for dip, sw in ((37.85, 37.75), (126.10, 126.00)):
        place(out, riser(1.15, 0.16), sw - 1.05)
        place(out, whoosh(1.15, 0.44), sw - 0.10)
        place(out, thump(D2, 1.0, 0.20), dip)
        place(out, bell(D4, 2.2, 0.10), dip + 0.05)

    # ٣) بطاقة «اللغز» (131.48)
    place(out, riser(1.0, 0.14), 130.30)
    place(out, whoosh(1.35, 0.40), 130.95)
    place(out, thump(52.0, 1.5, 0.24), 131.42)
    place(out, bell(D4, 3.2, 0.26), 131.46)
    place(out, bell(A3, 3.6, 0.16), 131.88)
    place(out, bell(D3, 4.0, 0.10), 132.30)

    # ٤) نقرات المشاهد (خفيفة، كل ~١٥–٢٠ ث)
    for at in (17.90, 55.30, 70.10, 83.40, 96.60, 110.40, 141.30):
        place(out, tick(0.24), at)
        place(out, thump(64.0, 0.60, 0.12), at + 0.02)

    # ٥) تأكيدات على لحظات المعنى (٤ فقط، بلا مغالاة)
    for at in (13.10, 62.35, 88.20, 120.10):
        place(out, pluck(A3, 2.0, 0.18), at, 0.8)

    # ٦) الخاتمة
    place(out, whoosh(1.6, 0.20), 157.60)
    place(out, pluck(D3, 3.2, 0.30), 158.25, 0.85)
    place(out, pluck(A3, 3.4, 0.18), 158.72, 0.75)
    place(out, bell(D2, 4.0, 0.22), 158.30, 0.8)
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    b, s = bed(), sfx()
    save(OUT / "bed.wav", np.stack([b, b], axis=1))
    save(OUT / "sfx.wav", np.stack([s, s], axis=1))


if __name__ == "__main__":
    main()
