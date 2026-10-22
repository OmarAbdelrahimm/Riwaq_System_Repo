"""مؤثرات صوتية مركّبة محليًا (بلا ملفات خارجية): نقرة لكل كلمة + هوشة عند دخول كل بطاقة.

كل الأصوات تُولَّد بـ numpy ثم تُخلط في مسار منفصل يُضاف للصوت الأصلي عند التصدير،
فلا يُعاد ترميز الصوت الأصلي أكثر من مرة واحدة ولا تُفقد جودته.
"""
from __future__ import annotations

import json
import os
import wave

import numpy as np

SR = 48000


def _env(n: int, attack: int, decay_pow: float = 2.6) -> np.ndarray:
    a = max(1, attack)
    e = np.ones(n)
    e[:a] = np.linspace(0, 1, a) ** 0.6
    tail = n - a
    if tail > 0:
        e[a:] = np.exp(-decay_pow * np.linspace(0, 1, tail)) ** 1.0
    return e


def tick(f: float = 1150.0, dur: float = 0.055, seed: int = 0) -> np.ndarray:
    """نقرة قصيرة «تِك» — جسم نغمي + شرطة ضجيج خفيفة تعطي إحساس الطرقعة."""
    rng = np.random.default_rng(seed)
    n = int(SR * dur)
    t = np.arange(n) / SR
    tone = (0.7 * np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.02 * t))
    noise = rng.normal(0, 1, n) * np.exp(-np.linspace(0, 1, n) * 22) * 0.35
    x = (tone * np.exp(-np.linspace(0, 1, n) * 9) + noise) * _env(n, 24, 3.0)
    return x / (np.max(np.abs(x)) + 1e-9)


def whoosh(dur: float = 0.30, up: bool = True) -> np.ndarray:
    """هوشة انتقال: ضجيج مُرشَّح بتمرير منخفض متغيّر + مظروف سريع."""
    rng = np.random.default_rng(7)
    n = int(SR * dur)
    noise = rng.normal(0, 1, n)
    # مرشّح تمرير منخفض متغيّر (متوسط متحرك بنافذة متغيّرة)
    out = np.zeros(n)
    win = 1
    acc = 0.0
    for i in range(n):
        k = i / max(1, n - 1)
        target = 26 + (2 if up else 26) * (1 - k)
        win = int(2 + target * (k if up else 1 - k))
        acc = acc + (noise[i] - acc) * (1.0 / max(1, win))
        out[i] = acc
    env = np.sin(np.linspace(0, np.pi, n)) ** 1.6
    out = out * env
    return out / (np.max(np.abs(out)) + 1e-9)


def build(events: list[dict], total: float, path: str,
          word_gain: float = 0.075, card_gain: float = 0.135,
          with_cards: bool = True) -> dict:
    """events: [{'t': sec, 'kind': 'word'|'card'}] → ملف WAV ستيريو بطول total."""
    n_total = int(SR * total) + SR
    buf = np.zeros(n_total, dtype=np.float32)
    last_card = -9.0
    n_words = 0
    for e in events:
        t = float(e["t"])
        if t < 0 or t >= total:
            continue
        i0 = int(t * SR)
        if e["kind"] == "card":
            if not with_cards:
                continue
            s = whoosh(0.34) * card_gain
            last_card = t
        else:
            if t - last_card < 0.10:
                continue
            f = 1080.0 + (int(t * 7) % 5) * 55.0
            s = tick(f) * word_gain
            n_words += 1
        i1 = min(n_total, i0 + len(s))
        buf[i0:i1] += s[: i1 - i0].astype(np.float32)
    buf = np.clip(buf, -0.9, 0.9)
    stereo = np.stack([buf, buf], axis=1)
    pcm = (stereo * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return {"path": path, "seconds": total, "words": n_words,
            "cards": sum(1 for e in events if e["kind"] == "card")}


if __name__ == "__main__":
    ev = json.load(open(__import__("sys").argv[1], encoding="utf-8"))
    total = float(__import__("sys").argv[2])
    print(build(ev, total, __import__("sys").argv[3]))
