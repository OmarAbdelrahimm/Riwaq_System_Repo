#!/usr/bin/env python3
"""
audio_master.py — Riwaq TMB_001 · V2 الصوت
==========================================
بياخد السرد الأصلي 24kHz ويصلّح العيوب التلاتة المقاسة:

  [1] aliasing  → بنستخدم الأصل 24kHz مش نسخة 8kHz
  [2] طمي رنان → 200–800Hz كان 60% من الطاقة (الطبيعي ~35%)
                 → low-mid cut −2.5dB @340Hz
  [3] وضوح     → 800–2000Hz كان 10.7% (الطبيعي ~25%)
                 → intelligibility +3.0dB @1.3kHz
  [4] حضور     → 2–4kHz كان 1.9%
                 → presence +2.5dB @3.2kHz
  [5] هسيس     → قمة 6–9kHz غير طبيعية في الأصل
                 → de-hiss −2.0dB @7kHz
  [6] مستوى    → −21.2 LUFS → −14.0 LUFS
  [7] قمة      → limiter بـlook-ahead (مش قصّ موجة)

كل ده بـPython خالص — مفيش numpy/scipy/ffmpeg هنا.
"""

import wave, array, math, sys
from pathlib import Path

TARGET_LUFS = -14.0
CEILING_DBTP = -1.5
SR = 24000


# ══ I/O ═══════════════════════════════════════════════════════════════════
def read_wav(path):
    w = wave.open(str(path), "rb")
    ch, sr, sw, n = w.getnchannels(), w.getframerate(), w.getsampwidth(), w.getnframes()
    raw = w.readframes(n)
    w.close()
    if sw != 2:
        raise ValueError(f"{path}: عايز 16-bit PCM")
    a = array.array("h")
    a.frombytes(raw)
    if ch > 1:
        a = array.array("h", a[::ch])
    return [float(v) for v in a], sr


def write_wav(path, x, sr):
    out = array.array("h", (max(-32768, min(32767, int(round(v)))) for v in x))
    w = wave.open(str(path), "wb")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(sr)
    w.writeframes(out.tobytes())
    w.close()


# ══ biquad (RBJ) ══════════════════════════════════════════════════════════
def biquad(x, sr, kind, freq, gain_db=0.0, q=0.707):
    A = 10 ** (gain_db / 40.0)
    w0 = 2 * math.pi * freq / sr
    cw, sw_ = math.cos(w0), math.sin(w0)
    alpha = sw_ / (2 * q)

    if kind == "peak":
        b0, b1, b2 = 1 + alpha * A, -2 * cw, 1 - alpha * A
        a0, a1, a2 = 1 + alpha / A, -2 * cw, 1 - alpha / A
    elif kind == "highshelf":
        sA, tsa = math.sqrt(A), 2 * math.sqrt(A) * alpha
        b0 = A * ((A + 1) + (A - 1) * cw + tsa)
        b1 = -2 * A * ((A - 1) + (A + 1) * cw)
        b2 = A * ((A + 1) + (A - 1) * cw - tsa)
        a0 = (A + 1) - (A - 1) * cw + tsa
        a1 = 2 * ((A - 1) - (A + 1) * cw)
        a2 = (A + 1) - (A - 1) * cw - tsa
    elif kind == "lowshelf":
        sA, tsa = math.sqrt(A), 2 * math.sqrt(A) * alpha
        b0 = A * ((A + 1) - (A - 1) * cw + tsa)
        b1 = 2 * A * ((A - 1) - (A + 1) * cw)
        b2 = A * ((A + 1) - (A - 1) * cw - tsa)
        a0 = (A + 1) + (A - 1) * cw + tsa
        a1 = -2 * ((A - 1) + (A + 1) * cw)
        a2 = (A + 1) + (A - 1) * cw - tsa
    elif kind == "hpf":
        b0, b1, b2 = (1 + cw) / 2, -(1 + cw), (1 + cw) / 2
        a0, a1, a2 = 1 + alpha, -2 * cw, 1 - alpha
    else:
        raise ValueError(kind)

    b0, b1, b2 = b0 / a0, b1 / a0, b2 / a0
    a1, a2 = a1 / a0, a2 / a0
    out = [0.0] * len(x)
    x1 = x2 = y1 = y2 = 0.0
    for i, v in enumerate(x):
        y = b0 * v + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1 = x1, v
        y2, y1 = y1, y
        out[i] = y
    return out



# ══ de-esser ديناميكي (5–9 kHz، بس وقت الحاجة) ═══════════════════════════
def band_isolate(x, sr, lo, hi):
    """يعزل نطاق ترددي: highpass(lo) ثم highpass مقنّع على hi.
    النتيجة: مكوّن النطاق فقط، ونرجعه بالطرح."""
    a = biquad(x, sr, "hpf", lo, q=0.7)
    b = biquad(a, sr, "hpf", hi, q=0.7)
    return [a[i] - b[i] for i in range(len(a))]


def de_ess(x, sr, lo=5000, hi=9000, thresh_db=-26.0, ratio=3.5,
           attack_ms=2.0, release_ms=90.0, max_gr_db=-7.0):
    """
    يشتغل بس على الصفير (س، ص، ش) ويسيب باقي الصوت زي ما هو.
    بيقيس مغلّف نطاق 5–9k، ولو عدّى العتبة يخفض النطاق ده بس.
    الصوت اللي مش فيه صفير مش بيتلمس نهائيًا.
    """
    band = band_isolate(x, sr, lo, hi)
    a = math.exp(-1.0 / (attack_ms * 1e-3 * sr))
    r = math.exp(-1.0 / (release_ms * 1e-3 * sr))
    thr = 10 ** (thresh_db / 20.0) * 32768.0
    env = 0.0
    envs = [0.0] * len(band)
    for i, v in enumerate(band):
        av = abs(v)
        env = a * env + (1 - a) * av if av > env else r * env + (1 - r) * av
        envs[i] = env

    out = [0.0] * len(x)
    touched = 0
    for i in range(len(x)):
        g = 1.0
        if envs[i] > thr:
            over = 20 * math.log10(envs[i] / thr)
            gr = -over * (1 - 1 / ratio)
            gr = max(gr, max_gr_db)
            g = 10 ** (gr / 20.0)
            touched += 1
        # شيل النطاق وخليه يرجع بالكتم
        out[i] = (x[i] - band[i]) + band[i] * g
    print(f"   de-esser لمس {touched/len(x)*100:.2f}% من العينات")
    return out


# ══ LUFS (ITU-R BS.1770-4) ════════════════════════════════════════════════
# ملاحظة مهمة: كل الحسابات على عينات NORMALIZED (±1.0) مش int16.
# الثابت −0.691 معرّف لعينات ±1 — استخدامه على ±32768 يضيف 90.3 dB خطأ.

def _k_filters(sr):
    """فلاتر K بالمعاملات الرسمية BS.1770-4 §5 (تشتغل على أي sr)."""
    f0, G, Q = 1681.9744509555319, 3.99984385397, 0.7071752369554193
    K = math.tan(math.pi * f0 / sr)
    Vh = 10 ** (G / 20)
    Vb = Vh ** 0.499666774155
    a0 = 1 + K / Q + K * K
    b1 = [(Vh + Vb * K / Q + K * K) / a0, 2 * (K * K - Vh) / a0,
          (Vh - Vb * K / Q + K * K) / a0]
    a1 = [1.0, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0]

    f0, Q = 38.13547087613982, 0.5003270373253994
    K = math.tan(math.pi * f0 / sr)
    a0 = 1 + K / Q + K * K
    b2 = [1 / a0, -2 / a0, 1 / a0]
    a2 = [1.0, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0]
    return (b1, a1), (b2, a2)


def _apply(sig, b, a):
    out = [0.0] * len(sig)
    x1 = x2 = y1 = y2 = 0.0
    for i in range(len(sig)):
        o = b[0] * sig[i] + b[1] * x1 + b[2] * x2 - a[1] * y1 - a[2] * y2
        x2, x1 = x1, sig[i]
        y2, y1 = y1, o
        out[i] = o
    return out


def lufs(x_int16, sr):
    """LUFS مدمج (integrated) بمعيار ITU-R BS.1770-4.
    المدخل int16 (±32768) — بنطبّعه لـ±1 قبل الحساب."""
    x = [v / 32768.0 for v in x_int16]
    (b1, a1), (b2, a2) = _k_filters(sr)
    y = _apply(_apply(x, b2, a2), b1, a1)

    blk, hop = int(0.4 * sr), int(0.1 * sr)
    blocks = []
    for i in range(0, len(y) - blk, hop):
        ms = sum(v * v for v in y[i:i + blk]) / blk
        if ms > 1e-12:
            blocks.append(-0.691 + 10 * math.log10(ms))
    if not blocks:
        return -999.0
    gated = [l for l in blocks if l > -70.0]
    if not gated:
        return -999.0
    # البلوكات أصلاً فيها الثابت −0.691 → ممنوع نضيفه تاني
    rel = 10 * math.log10(sum(10 ** (l / 10) for l in gated) / len(gated)) - 10.0
    final = [l for l in gated if l > rel]
    if not final:
        return rel
    return 10 * math.log10(sum(10 ** (l / 10) for l in final) / len(final))


def stats(x, sr, label):
    pk = max(abs(min(x)), abs(max(x))) / 32768.0
    rms = math.sqrt(sum(v * v for v in x) / len(x)) / 32768.0
    L = lufs(x, sr)
    crest = 20 * math.log10(pk / rms) if rms > 0 else 0
    print(f"  {label:20} peak {20*math.log10(pk) if pk>0 else -99:+6.2f} dBTP  "
          f"rms {20*math.log10(rms):+6.2f}  LUFS {L:+6.2f}  crest {crest:4.1f} dB")
    return L


# ══ كومبريسور ════════════════════════════════════════════════════════════
def compress(x, sr, thresh_db=-22.0, ratio=2.5, attack_ms=10.0, release_ms=200.0,
             makeup_db=0.0):
    thr = 10 ** (thresh_db / 20.0) * 32768.0   # الداتا في مقياس int16
    a = math.exp(-1.0 / (attack_ms * 1e-3 * sr))
    r = math.exp(-1.0 / (release_ms * 1e-3 * sr))
    env = 0.0
    out = [0.0] * len(x)
    for i, v in enumerate(x):
        av = abs(v)
        env = a * env + (1 - a) * av if av > env else r * env + (1 - r) * av
        g = 1.0
        if env > thr:
            over = 20 * math.log10(env / thr)
            g = 10 ** ((-over * (1 - 1 / ratio)) / 20.0)
        out[i] = v * g
    if makeup_db:
        m = 10 ** (makeup_db / 20.0)
        out = [v * m for v in out]
    return out


# ══ ليـمتر بـlook-ahead (مش قصّ) ══════════════════════════════════════════
def limiter(x, sr, ceiling_db=-1.0, lookahead_ms=5.0, release_ms=120.0):
    """
    بيحسب مطلوب التخفيض لكل عينة، بيوسّع الهبوط قبل القمة بـlook-ahead،
    ويرجّع المستوى ببطء. النتيجة: قمة محدودة من غير ما الموجة تتقص.
    """
    ceil = 10 ** (ceiling_db / 20.0) * 32768.0
    la = int(lookahead_ms * 1e-3 * sr)
    n = len(x)

    # 1 · المطلوب لكل عينة
    req = [1.0] * n
    for i, v in enumerate(x):
        av = abs(v)
        if av > ceil:
            req[i] = ceil / av

    # 2 · خد أقل قيمة في نافذة الـlook-ahead (تسبق القمة)
    need = [1.0] * n
    for i in range(n):
        lo = req[i]
        for j in range(i, min(n, i + la + 1)):
            if req[j] < lo:
                lo = req[j]
        need[i] = lo
    # كمان ابصّ لورا لحد la
    for i in range(n - 1, -1, -1):
        m = need[i]
        for j in range(max(0, i - la), i):
            if need[j] < m:
                m = need[j]
        need[i] = min(need[i], m)

    # 3 · نعومة: هبوط فوري، رجوع بالـrelease
    r = math.exp(-1.0 / (release_ms * 1e-3 * sr))
    g = 1.0
    out = [0.0] * n
    for i in range(n):
        target = need[i]
        g = target if target < g else r * g + (1 - r) * target
        out[i] = x[i] * g
    return out


# ══ كابح قمم (peak tamer) ════════════════════════════════════════════════
def peak_tame(x, sr, peak_db, amount_db=6.0, ratio=8.0, attack_ms=1.0, release_ms=80.0):
    """
    بيمسك الترانسيات القصيرة بس (اللي بتمنعنا نرفع المستوى).
    العتبة = قمة المادة − amount_db → بتلمس أعلى X dB فقط.
    الجسم مش بيتأثر → مفيش "pumping".
    """
    thr = 10 ** ((peak_db - amount_db) / 20.0) * 32768.0
    a = math.exp(-1.0 / (attack_ms * 1e-3 * sr))
    r = math.exp(-1.0 / (release_ms * 1e-3 * sr))
    env = 0.0
    out = [0.0] * len(x)
    touched = 0
    for i, v in enumerate(x):
        av = abs(v)
        env = a * env + (1 - a) * av if av > env else r * env + (1 - r) * av
        g = 1.0
        if env > thr:
            over = 20 * math.log10(env / thr)
            g = 10 ** ((-over * (1 - 1 / ratio)) / 20.0)
            touched += 1
        out[i] = v * g
    print(f"   كابح القمم لمس {touched/len(x)*100:.2f}% من العينات")
    return out


# ══ السلسلة ══════════════════════════════════════════════════════════════
def master(src, dst):
    print(f"\n{'='*70}")
    print(f"  {Path(src).name}  →  {Path(dst).name}")
    print(f"{'='*70}")
    x, sr = read_wav(src)
    print(f"  {len(x)/sr:.1f}s · {sr} Hz")
    src_lufs = stats(x, sr, "الأصل")

    # ── gain staging ──
    pk0 = max(abs(min(x)), abs(max(x)))
    pre = (10 ** (-6.0 / 20.0) * 32768) / pk0
    x = [v * pre for v in x]
    print(f"  pre-gain {20*math.log10(pre):+.2f} dB → قمة −6 dBFS")

    # ── EQ ──
    print("\n── EQ ──")
    x = biquad(x, sr, "hpf", 75, q=0.7)
    x = biquad(x, sr, "peak", 340, gain_db=-2.5, q=1.0)
    x = biquad(x, sr, "peak", 1300, gain_db=+3.0, q=0.9)
    x = biquad(x, sr, "peak", 3200, gain_db=+1.5, q=1.0)
    x = biquad(x, sr, "highshelf", 9000, gain_db=+0.5, q=0.7)
    print("   HPF75 · mud −2.5@340 · intel +3.0@1.3k · pres +1.5@3.2k")
    print("   air +0.5@9k")
    stats(x, sr, "بعد EQ")
    print("\n── de-esser (بس وقت الحاجة) ──")
    x = de_ess(x, sr, lo=5000, hi=9000, thresh_db=-26.0, ratio=3.5)
    stats(x, sr, "بعد de-ess")

    # ── ديناميكس ──
    print("\n── ديناميكس ──")
    pk1 = 20 * math.log10(max(abs(v) for v in x) / 32768.0)
    print(f"   قمة بعد EQ: {pk1:+.1f} dBFS")
    x = peak_tame(x, sr, pk1, amount_db=10.0, ratio=12.0, attack_ms=0.5, release_ms=120)
    stats(x, sr, "بعد كابح القمم")
    x = compress(x, sr, thresh_db=-20.0, ratio=2.0, attack_ms=30, release_ms=400)
    print("   compressor 2:1 @ −22 dB (18ms/260ms)")
    stats(x, sr, "بعد الكومبرس")

    # ── معايرة على مرحلتين (لأن الليـمتر بيشيل جزء) ──
    print("\n── معايرة ──")
    for attempt in range(1, 9):
        cur = lufs(x, sr)
        gain_db = TARGET_LUFS - cur
        g = 10 ** (gain_db / 20.0)
        x = [v * g for v in x]
        before = sum(1 for v in x if abs(v) > 10 ** (CEILING_DBTP / 20) * 32768)
        x = limiter(x, sr, ceiling_db=CEILING_DBTP)
        after = lufs(x, sr)
        print(f"   محاولة {attempt}: {cur:+6.2f} → gain {gain_db:+5.2f} dB "
              f"→ limiter {before:,} عينة → {after:+6.2f} LUFS")
        if abs(after - TARGET_LUFS) < 0.15:
            break

    print("\n── النتيجة ──")
    stats(x, sr, "النهائي")
    write_wav(dst, x, sr)
    print(f"\n✅ {dst}   {Path(dst).stat().st_size/1024/1024:.1f} MB")
    return dict(src_lufs=src_lufs, out_lufs=lufs(x, sr))


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "google_drive/VO_v3_full_4m48s.wav"
    dst = sys.argv[2] if len(sys.argv) > 2 else "public/projects/TMB_001/vo/VO_V2_master.wav"
    master(src, dst)
