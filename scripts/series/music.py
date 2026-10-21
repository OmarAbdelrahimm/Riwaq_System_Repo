"""موسيقى سلسلة رواق — توليد آلي (سِنتسيز) لهوية صوتية موحّدة.

الطابع: مقام حجاز على درجة «د»، طبقات دافئة، نقرات عود/قانون خفيفة، إيقاع منخفض
ناعم جدًا. كل النغمات مولّدة رقميًا (لا حقوق طرف ثالث).
"""
from __future__ import annotations

import math
import wave

import numpy as np

SR = 48000

# ترددات (حجاز على د)
NOTE = {
    "D2": 73.42, "A2": 110.00, "D3": 146.83, "Eb3": 155.56, "F3": 174.61,
    "F#3": 185.00, "G3": 196.00, "A3": 220.00, "Bb3": 233.08, "C4": 261.63,
    "D4": 293.66, "Eb4": 311.13, "F#4": 369.99, "G4": 392.00, "A4": 440.00,
    "Bb4": 466.16, "C5": 523.25, "D5": 587.33,
}


def _env(n: int, attack: float, decay: float, sr: int = SR) -> np.ndarray:
    a = max(1, int(attack * sr))
    d = max(1, int(decay * sr))
    env = np.ones(n)
    env[:min(a, n)] = np.linspace(0, 1, min(a, n))
    tail = np.arange(n)
    env *= np.exp(-tail / d)
    return env


def pluck(freq: float, dur: float, amp: float = 0.3, bright: float = 0.35) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for k, w in ((1, 1.0), (2, 0.35 * bright), (3, 0.18 * bright), (4, 0.08 * bright)):
        sig += w * np.sin(2 * math.pi * freq * k * t + 0.15 * k)
    sig *= _env(n, 0.006, dur * 0.32)
    # نقر خفيف في البداية
    sig[: int(0.012 * SR)] += np.random.default_rng(7).normal(0, 0.05, int(0.012 * SR))
    return amp * sig / (np.max(np.abs(sig)) + 1e-9)


def pad(freqs: list[float], dur: float, amp: float = 0.2, attack: float = 0.8) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for f in freqs:
        det = 1.0 + 0.0018 * np.sin(2 * math.pi * 0.17 * t)
        sig += np.sin(2 * math.pi * f * t * det)
        sig += 0.5 * np.sin(2 * math.pi * f * 1.004 * t)
    sig /= len(freqs) * 1.6
    env = _env(n, attack, dur * 1.1)
    return amp * sig * env


def thump(freq: float = 55.0, dur: float = 1.1, amp: float = 0.32) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.sin(2 * math.pi * freq * t * (1 - 0.25 * t / dur))
    sig *= _env(n, 0.004, dur * 0.16)
    return amp * sig


def air(dur: float, amp: float = 0.05, seed: int = 3) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    w = rng.normal(0, 1, n)
    # مرشّح تمرير منخفض بسيط (متوسط متحرك) لصنع «هواء» دافئ
    k = 220
    ker = np.ones(k) / k
    w = np.convolve(w, ker, mode="same")
    return amp * w * _env(n, 0.5, dur * 1.2)


def _place(buf: np.ndarray, sig: np.ndarray, at: float, gain: float = 1.0) -> None:
    i = int(at * SR)
    n = min(len(sig), len(buf) - i)
    if n > 0:
        buf[i:i + n] += gain * sig[:n]


def reverb(sig: np.ndarray, mix: float = 0.22, decay: float = 0.9) -> np.ndarray:
    """صدى بسيط (comb + allpass شبيه) لعمق سينمائي بلا مكتبات خارجية."""
    out = sig.copy()
    for delay_ms, g in ((37, 0.32), (61, 0.24), (97, 0.17), (143, 0.1)):
        d = int(delay_ms / 1000 * SR)
        tail = np.zeros_like(sig)
        tail[d:] = sig[:-d] * g
        tail *= np.exp(-np.arange(len(sig)) / (decay * SR))
        out += mix * tail
    return out


def write_wav(path: str, sig: np.ndarray) -> None:
    sig = np.asarray(sig, dtype=np.float64)
    peak = np.max(np.abs(sig)) or 1.0
    if peak > 0.98:
        sig = sig * (0.98 / peak)
    pcm = (np.clip(sig, -1, 1) * 32767).astype("<i2")
    stereo = np.repeat(pcm[:, None], 2, axis=1).reshape(-1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(stereo.tobytes())


def _norm(sig: np.ndarray, dbfs: float) -> np.ndarray:
    peak = np.max(np.abs(sig)) or 1.0
    return sig * (10 ** (dbfs / 20) / peak)


def intro(dur: float = 4.4) -> np.ndarray:
    n = int(dur * SR)
    buf = np.zeros(n)
    _place(buf, pad([NOTE["D3"], NOTE["A3"], NOTE["D4"]], 4.4, amp=0.20, attack=0.55), 0.0)
    _place(buf, thump(NOTE["D2"], 1.4, 0.30), 0.02)
    _place(buf, air(4.4, 0.045), 0.0)
    for at, note, g in ((0.30, "D4", 0.30), (0.78, "A4", 0.24), (1.34, "F#4", 0.22),
                        (2.05, "D5", 0.20), (2.62, "C5", 0.16)):
        _place(buf, pluck(NOTE[note], 2.6, amp=g), at)
    buf = reverb(buf, 0.26)
    # خروج ناعم كي ينساب تحت أول كلمة
    fade = np.ones(n)
    f = int(1.1 * SR)
    fade[-f:] = np.linspace(1, 0, f) ** 1.4
    return _norm(buf * fade, -14.0)


def outro(dur: float = 9.0) -> np.ndarray:
    n = int(dur * SR)
    buf = np.zeros(n)
    _place(buf, pad([NOTE["D3"], NOTE["A3"], NOTE["D4"], NOTE["F#4"]], 9.0, amp=0.20, attack=0.7), 0.0)
    _place(buf, pad([NOTE["Bb3"], NOTE["F3"], NOTE["D3"]], 4.6, amp=0.10, attack=0.9), 4.2)
    _place(buf, thump(NOTE["D2"], 1.6, 0.24), 0.0)
    for at, note, g in ((0.55, "D5", 0.24), (1.45, "C5", 0.22), (2.35, "Bb4", 0.20),
                        (3.25, "A4", 0.19), (4.20, "G4", 0.17), (5.25, "F#4", 0.15),
                        (6.35, "D4", 0.14)):
        _place(buf, pluck(NOTE[note], 3.4, amp=g), at)
    buf = reverb(buf, 0.3)
    fade = np.ones(n)
    fi = int(0.35 * SR)
    fo = int(2.4 * SR)
    fade[:fi] = np.linspace(0, 1, fi)
    fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
    return _norm(buf * fade, -13.0)


def bed(dur: float, dbfs: float = -26.0) -> np.ndarray:
    """طبقة موسيقية هادئة بطول الفيديو — تُخفض تلقائيًا تحت الكلام (ducking)."""
    n = int(dur * SR)
    buf = np.zeros(n)
    chords = [
        [NOTE["D3"], NOTE["A3"], NOTE["D4"]],
        [NOTE["D3"], NOTE["Bb3"], NOTE["F3"]],
        [NOTE["D3"], NOTE["A3"], NOTE["F#3"]],
        [NOTE["C4"], NOTE["G3"], NOTE["D4"]],
    ]
    cyc = 9.5
    t = 0.0
    i = 0
    while t < dur:
        ch = chords[i % len(chords)]
        _place(buf, pad(ch, min(cyc + 2.2, dur - t + 2.2), amp=0.16, attack=1.6), t)
        _place(buf, pluck(NOTE[["D4", "A4", "F#4", "C5", "D5"][i % 5]], 3.2, amp=0.10), t + 0.8)
        t += cyc
        i += 1
    buf = reverb(buf, 0.18, decay=1.2)
    # ترشيح ناعم: إزالة الترددات العالية جدًا
    k = 3
    buf = np.convolve(buf, np.ones(k) / k, mode="same")
    return _norm(buf, dbfs)


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    write_wav(f"{out}/MUSIC_INTRO_riwaq.wav", intro())
    write_wav(f"{out}/MUSIC_OUTRO_riwaq.wav", outro())
    print("ok")
