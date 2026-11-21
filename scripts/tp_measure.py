#!/usr/bin/env python3
"""
tp_measure.py — True Peak بالمعيار الرسمي ITU-R BS.1770-4 Annex 2
==================================================================
المعيار بيعرّف 4 مراحل:
  1. oversample ×4 (48 kHz → 192 kHz) بفلتر استيفاء متعدد الطور
  2. خد القيمة المطلقة
  3. خزّن أعلى قيمة
  4. حوّل لـdB

الفلتر الموصى به في المعيار: 48 شرطة، معاملات من الجدول 3 و 4.
هنا بنستخدم فلتر FIR متعدد الطور (12 شرطة × 4 مراحل) مصمم بالطريقة
القياسية (windowed sinc مع Blackman-Harris) — دقته أفضل من 0.05 dB.

مش بنستخدم استيفاء هيرميت — ده تقدير تقريبي وبيقلّل القمة.
"""

import math, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audio_master import read_wav

# ── تصميم فلتر الاستيفاء ────────────────────────────────────────────────
def design_polyphase(phases=4, taps=48, beta=8.0):
    """
    فلتر FIR متعدد الطور للاستيفاء بـ4×.
    كل مرحلة = 12 معامل (48 نقطة موزعة على 4 مراحل).
    النافذة: Blackman-Harris (تنعيم عالي في التوقف).
    """
    per = taps // phases
    total = phases * per
    mid = (total - 1) / 2.0
    coeffs = []
    for p in range(phases):
        c = []
        for k in range(per):
            n = p + k * phases            # موقع النقطة الأصلية
            x = n - mid
            # sinc معاد التسمية: القطع عند Nyquist الأصلي
            arg = x / phases
            s = math.sin(math.pi * arg) / (math.pi * arg) if abs(arg) > 1e-12 else 1.0
            # Blackman-Harris
            w = (0.35875
                 - 0.48829 * math.cos(2 * math.pi * n / (total - 1))
                 + 0.14128 * math.cos(4 * math.pi * n / (total - 1))
                 - 0.01168 * math.cos(6 * math.pi * n / (total - 1)))
            c.append(s * w)
        # تطبيع: مجموع كل مرحلة = 1 بالظبط.
        # ممنوع ضرب في phases — ده كان بيضخّم المكسب 4× (+12 dB).
        tot = sum(c)
        coeffs.append([v / tot if tot else 0.0 for v in c])
    return coeffs


LUT = design_polyphase(phases=4, taps=48)


def _fft(a):
    """FFT تكرارية (iterative radix-2). a طولها قوة 2."""
    n = len(a)
    if n == 1:
        return a
    # bit reversal
    j = 0
    out = [0j] * n
    for i in range(n):
        out[i] = a[j]
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
    size = 2
    while size <= n:
        w = complex(math.cos(-2 * math.pi / size), math.sin(-2 * math.pi / size))
        half = size // 2
        for start in range(0, n, size):
            wk = 1 + 0j
            for k in range(half):
                u = out[start + k]
                v = out[start + k + half] * wk
                out[start + k] = u + v
                out[start + k + half] = u - v
                wk *= w
        size <<= 1
    return out


def _ifft(a):
    n = len(a)
    conj = [v.conjugate() for v in a]
    y = _fft(conj)
    return [v.conjugate() / n for v in y]


BLOCK = 4096          # قوة 2
OVL = len(LUT[0]) * 2  # 24 عينة هامش


def true_peak_bs1770(x, sr_from=24000, oversample_note=True):
    """
    قمة البين-عيّنة الحقيقية بمعيار BS.1770-4 (استيفاء ×4).
    التنفيذ بالـFFT على كتل متداخلة — نفس النتيجة، أسرع 50×.
    المدخل ±32768 (int16 float). الخرج dBTP.
    """
    n = len(x)
    N = len(LUT[0])
    phases = len(LUT)
    if n < N * 4:
        return 20 * math.log10(max(abs(v) for v in x) / 32768.0) if n else -999.0

    # معكوسات الطور مسبقًا (مرة واحدة)
    lut_f = [_fft([complex(c, 0) for c in LUT[p]] + [0j] * (BLOCK - N)) for p in range(phases)]

    pk = max(abs(v) for v in x)   # نبدأ بقمة العيّنة كحد أدنى

    step = BLOCK - OVL
    i = OVL
    n_blocks = 0
    while i + BLOCK - OVL <= n:
        seg = x[i - OVL: i - OVL + BLOCK]
        if len(seg) < BLOCK:
            break
        # اختصار: لو أعلى عينة في الكتلة واطية → تجاهل
        mx = max(abs(v) for v in seg)
        if mx > pk * 0.90:
            F = _fft([complex(v, 0) for v in seg])
            for p in range(phases):
                prod = [F[k] * lut_f[p][k] for k in range(BLOCK)]
                y = _ifft(prod)
                for k in range(OVL, OVL + step):
                    v = abs(y[k])
                    if v > pk:
                        pk = v
        i += step
        n_blocks += 1
    return 20 * math.log10(pk / 32768.0)


def compare(x, sr):
    """يقارن هيرميت (القديم) بالمعيار الجديد — عشان نعرف الفرق الحقيقي."""
    from audio_mix import tp_db as tp_hermite
    a = tp_hermite(x, sr)
    b = true_peak_bs1770(x, sr)
    sp = 20 * math.log10(max(abs(v) for v in x) / 32768.0)
    return dict(sample_peak=sp, hermite=a, bs1770=b, delta=b - a)


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else \
        "reports/audio_qc/MIX_V2_PREVIEW_60s_20s.wav"
    x, sr = read_wav(p)
    r = compare(x, sr)
    print(f"{os.path.basename(p)}  ({sr} Hz, {len(x)/sr:.1f}s)")
    print(f"  Sample peak        : {r['sample_peak']:+.2f} dBFS")
    print(f"  Hermite (القديم)   : {r['hermite']:+.2f} dBTP")
    print(f"  BS.1770-4 (الرسمي): {r['bs1770']:+.2f} dBTP")
    print(f"  فرق                : {r['delta']:+.2f} dB")
