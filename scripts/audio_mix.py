#!/usr/bin/env python3
"""
audio_mix.py — Riwaq TMB_001 · V2 المكس السينمائي (ستيريو)
===========================================================
سرد مونو + موسيقى ستيريو + SFX ستيريو → مكس ستيريو 24 kHz.

المتطلبات المنفّذة (من مراجعتك):
  · الموسيقى 18–22 dB تحت السرد وقت الكلام
  · في الوقفات ترتفع 4–6 dB (swells طبيعية، مفيش pumping)
  · sidechain ducking بهجوم 90ms وإفراج 520ms
  · الموسيقى بتفضل ستيريو — مفيش دمج للمونو
  · SFX عند تحولات المشاهد (stinger_in / stinger_out)
  · الخرج −14 LUFS مدمج · ≤ −1.5 dBTP بـBS.1770-4 الرسمي
"""

import wave, array, math, sys, os, functools
print = functools.partial(print, flush=True)
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audio_master import biquad, lufs, read_wav, write_wav
from tp_measure import true_peak_bs1770 as tp_bs

FS = 32768.0
MIX_SR = 24000


# ══ قراءة WAV ستيريو ═════════════════════════════════════════════════════
def read_wav_stereo(path):
    """يرجّع (يسار, يمين, sr). مونو → يتكرر في القناتين."""
    w = wave.open(str(path), "rb")
    ch, sr, sw, n = w.getnchannels(), w.getframerate(), w.getsampwidth(), w.getnframes()
    raw = w.readframes(n)
    w.close()
    a = array.array("h")
    a.frombytes(raw)
    if ch == 1:
        m = [float(v) for v in a]
        return m, list(m), sr
    L = [float(v) for v in a[0::2]]
    R = [float(v) for v in a[1::2]]
    return L, R, sr


def write_wav_stereo(path, L, R, sr):
    n = min(len(L), len(R))
    out = array.array("h", [0] * (n * 2))
    for i in range(n):
        l = max(-32768, min(32767, int(round(L[i]))))
        r = max(-32768, min(32767, int(round(R[i]))))
        out[2 * i] = l
        out[2 * i + 1] = r
    w = wave.open(str(path), "wb")
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(sr)
    w.writeframes(out.tobytes())
    w.close()


def lufs_stereo(L, R, sr, chunk_s=20.0):
    """LUFS (BS.1770-4) للستيريو — طاقة القناتين مجموع، على كتل.
    القناة اليسرى وزنها 1 واليمنى وزنها 1، فالمجموع = L²+R².
    بنحسب على كتل 20 ثانية عشان الذاكرة."""
    from audio_master import _k_filters, _apply
    n = min(len(L), len(R))
    if n == 0:
        return -999.0
    (b1, a1), (b2, a2) = _k_filters(sr)
    blk = int(0.4 * sr)
    hop = int(0.1 * sr)
    step = int(chunk_s * sr)

    block_loud = []
    i = 0
    while i < n:
        j = min(n, i + step)
        segL = [v / 32768.0 for v in L[i:j]]
        segR = [v / 32768.0 for v in R[i:j]]
        yL = _apply(_apply(segL, b2, a2), b1, a1)
        yR = _apply(_apply(segR, b2, a2), b1, a1)
        for k in range(0, len(yL) - blk, hop):
            ms = sum(yL[k + m] * yL[k + m] + yR[k + m] * yR[k + m]
                     for m in range(blk)) / blk
            if ms > 1e-12:
                block_loud.append(-0.691 + 10 * math.log10(ms))
        i = j

    if not block_loud:
        return -999.0
    gated = [l for l in block_loud if l > -70.0]
    if not gated:
        return -999.0
    rel = 10 * math.log10(sum(10 ** (l / 10) for l in gated) / len(gated)) - 10.0
    final = [l for l in gated if l > rel]
    if not final:
        return rel
    return 10 * math.log10(sum(10 ** (l / 10) for l in final) / len(final))


def true_peak_stereo(L, R, sr):
    return max(tp_bs(L, sr), tp_bs(R, sr))


# ══ ليمتر سريع بـlook-ahead (deque — O(n)) ═══════════════════════════════
def limiter(x, sr, ceiling_db=-1.5, lookahead_ms=6.0, release_ms=140.0):
    """ليمتر look-ahead. ذاكرة: ليست خرج واحد + مصفوفة req بحجم n."""
    from collections import deque
    ceil = 10 ** (ceiling_db / 20.0) * FS
    n = len(x)
    la = max(1, int(lookahead_ms * 1e-3 * sr))
    r = math.exp(-1.0 / (release_ms * 1e-3 * sr))

    # req بحجم n (فلوت أو 1.0)
    req = [1.0] * n
    for i in range(n):
        av = abs(x[i])
        if av > ceil:
            req[i] = ceil / av

    # أدنى قيمة في النافذة المنزلقة [i-la, i+la] بـdeque رتيبة
    win = 2 * la + 1
    dq = deque()
    out = [0.0] * n
    g = 1.0
    # نهيّئ النافذة الأولى
    for k in range(0, min(n, la)):
        while dq and req[dq[-1]] >= req[k]:
            dq.pop()
        dq.append(k)
    nxt = min(n, la)
    for i in range(n):
        hi = i + la
        while nxt <= hi and nxt < n:
            while dq and req[dq[-1]] >= req[nxt]:
                dq.pop()
            dq.append(nxt)
            nxt += 1
        while dq and dq[0] < i - la:
            dq.popleft()
        target = req[dq[0]] if dq else 1.0
        g = target if target < g else r * g + (1 - r) * target
        out[i] = x[i] * g
    return out


def _scale_inplace(L, R, g):
    for i in range(len(L)):
        L[i] *= g
    for i in range(len(R)):
        R[i] *= g


def limiter_stereo(L, R, sr, ceiling_db=-1.5, chunk=24000 * 20):
    """ليمتر على القناتين بنفس النسبة — الصورة الستيريو محفوظة."""
    n = min(len(L), len(R))
    outL = [0.0] * n
    outR = [0.0] * n
    i = 0
    while i < n:
        j = min(n, i + chunk)
        pk = [max(abs(L[k]), abs(R[k])) for k in range(i, j)]
        lim = limiter(pk, sr, ceiling_db=ceiling_db)
        for k in range(len(pk)):
            g = lim[k] / pk[k] if pk[k] > 1e-9 else 1.0
            outL[i + k] = L[i + k] * g
            outR[i + k] = R[i + k] * g
        i = j
    return outL, outR


def _mem(tag):
    import resource
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(f"    [mem] {tag}: {r/1024:.0f} MB")


def master_stereo(L, R, sr, target_lufs=-14.0, ceiling=-1.5, iters=6):
    """معايرة الستيريو: gain ثم ليـمتر ثم تصحيح تعويضي.

    ملاحظة مهمة: الليـمتر بيعمل 'leap' +0.2–0.3 dB بعد أول تطبيق،
    فبنضيف التعويض مباشرة بدل ما نكرر الحلقة (كان بياخد 5 دقايق).
    """
    log = []
    _mem("بداية master")

    # 1 · ليـمتر أولي (يضمن إن القمم متحكَّم فيها)
    L, R = limiter_stereo(L, R, sr, ceiling_db=ceiling + 0.3)
    tp = true_peak_stereo(L, R, sr)
    if tp > ceiling:
        _scale_inplace(L, R, 10 ** ((ceiling - tp - 0.05) / 20.0))
    log.append((lufs_stereo(L, R, sr), 0.0,
                lufs_stereo(L, R, sr), true_peak_stereo(L, R, sr)))

    # 2 · دورة تعويض: gain → ليـمتر → قياس
    for k in range(iters):
        cur = lufs_stereo(L, R, sr)
        d = target_lufs - cur
        if abs(d) < 0.05:
            break
        _scale_inplace(L, R, 10 ** (d / 20.0))
        tp_before = true_peak_stereo(L, R, sr)
        L, R = limiter_stereo(L, R, sr, ceiling_db=ceiling)
        # الليـمتر 'بيزيد' القمة شوية — نصحّح بعدّه
        tp_after = true_peak_stereo(L, R, sr)
        if tp_after > ceiling:
            _scale_inplace(L, R, 10 ** ((ceiling - tp_after - 0.05) / 20.0))
        log.append((cur, d, lufs_stereo(L, R, sr), true_peak_stereo(L, R, sr)))

    # 3 · تصحيح نهائي للـLUFS (بعد كل الليمتر) مع الحفاظ على السقف
    for _ in range(6):
        cur = lufs_stereo(L, R, sr)
        d = target_lufs - cur
        if abs(d) < 0.10:
            break
        # لو لازم نرفع، نرفع بس لحد ما الـtrue peak يوصل السقف
        tp = true_peak_stereo(L, R, sr)
        head = ceiling - tp          # المسافة للسقف
        g_db = min(d, max(0.0, head))
        if g_db <= 0.01:
            break
        _scale_inplace(L, R, 10 ** (g_db / 20.0))
    log.append((lufs_stereo(L, R, sr), 0.0,
                lufs_stereo(L, R, sr), true_peak_stereo(L, R, sr)))
    return L, R, log


# ══ أدوات الإشارة ════════════════════════════════════════════════════════
def resample_48_to_24(x):
    """تنزيل 48k→24k مع فلتر مضاد للتعرية."""
    y = biquad([float(v) for v in x], 48000, "hpf", 20, q=0.7)
    y = biquad(y, 48000, "highshelf", 10000, gain_db=-18.0, q=0.7)
    return y[::2]


def envelope_db(x, sr, hop_ms=20.0, smooth_ms=40.0):
    hop = max(1, int(hop_ms * 1e-3 * sr))
    env = []
    for i in range(0, len(x), hop):
        seg = x[i:i + hop]
        if not seg:
            break
        ms = sum(v * v for v in seg) / len(seg)
        env.append(10 * math.log10(ms / (FS * FS)) if ms > 1e-14 else -98.0)
    k = max(1, int(smooth_ms / hop_ms))
    if k > 1 and len(env) > k:
        sm = []
        acc = sum(env[:k])
        for i in range(len(env)):
            sm.append(acc / k)
            if i + k < len(env):
                acc += env[i + k]
            if i < len(env) - k:
                acc -= env[i]
        env = sm
    return env, hop / sr


def smooth_curve(target, sr, hop_s, attack_ms, release_ms):
    a = math.exp(-hop_s / (attack_ms * 1e-3))
    r = math.exp(-hop_s / (release_ms * 1e-3))
    out, cur = [], target[0] if target else 0.0
    for t in target:
        c = a if t < cur else r
        cur = c * cur + (1 - c) * t
        out.append(cur)
    return out


def curve_to_samples(curve, hop_s, n, sr):
    out = [0.0] * n
    last = len(curve) - 1
    for i in range(n):
        pos = i / sr / hop_s
        j = int(pos)
        if j >= last:
            f = curve[-1]
        else:
            f0 = pos - j
            f = curve[j] * (1 - f0) + curve[j + 1] * f0
        out[i] = 10 ** (f / 20.0)
    return out


def build_bed(music, need_n, sr, xfade_s=1.6):
    """لوب سلس بكريسفيد متساوي القوة."""
    P = len(music)
    xf = int(xfade_s * sr)
    if P <= xf * 2:
        raise ValueError("الموسيقى قصيرة جدًا للوب")
    out = [0.0] * need_n
    out[:min(P, need_n)] = music[:min(P, need_n)]
    loops = 1
    while True:
        start = loops * (P - xf)
        if start >= need_n:
            break
        for j in range(xf):
            idx = start + j
            if idx >= need_n:
                break
            t = j / xf
            out[idx] = out[idx] * math.cos(t * math.pi / 2) + music[j] * math.sin(t * math.pi / 2)
        for j, v in enumerate(music[xf:]):
            idx = start + xf + j
            if idx >= need_n:
                break
            out[idx] = v
        loops += 1
    return out, loops


def rms_db(x):
    if not x:
        return -99.0
    return 10 * math.log10(sum(v * v for v in x) / len(x) / (FS * FS))


def mix(vo_path, music_path, out_path, total_s=288.3,
        rel_speech_db=-20.0, rel_pause_db=-15.0,
        scene_bounds=None, emotion_windows=None,
        stingers=None, preview=None, sfx_gain_db=-13.0):

    print(f"\n{'='*74}\n  المكس السينمائي الستيريو — V2\n{'='*74}")
    vo, _vo_sr = read_wav(vo_path)
    voL, voR, vo_sr = read_wav_stereo(vo_path)
    musL, musR, mus_sr = read_wav_stereo(music_path)
    sr = MIX_SR
    print(f"  السرد   : {len(voL)/vo_sr:.1f}s @{vo_sr//1000}k مونو")
    print(f"  الموسيقى: {len(musL)/mus_sr:.1f}s @{mus_sr//1000}k ستيريو")

    n = int(total_s * sr)
    if len(voL) < n:
        pad = n - len(voL)
        voL += [0.0] * pad; voR += [0.0] * pad
    else:
        voL, voR = voL[:n], voR[:n]

    # ── تنزيل الموسيقى لـ24k مع الحفاظ على القناتين ──
    if mus_sr == 48000:
        mL = resample_48_to_24(musL)
        mR = resample_48_to_24(musR)
    else:
        mL, mR = musL, musR
    # نضمن نفس الطول
    if len(mL) < len(mR): mR = mR[:len(mL)]
    else: mL = mL[:len(mR)]

    bedL, loops = build_bed(mL, n, sr)
    bedR, _ = build_bed(mR, n, sr)
    print(f"  اللوب: {loops} لفة · كريسفيد 1.6s · ستيريو محفوظ")

    # ── تحليل السرد ──
    env, hop_s = envelope_db(voL, sr)
    voiced_thr = -38.0
    speech_frac = sum(1 for e in env if e > voiced_thr) / len(env)
    print(f"  الكلام: {speech_frac*100:.0f}% من الزمن")

    vo_speech = rms_db([v for v in voL if abs(v) > 200])
    mus_rms = rms_db(bedL)
    print(f"  RMS السرد (كلام): {vo_speech:+.1f} dBFS   RMS الموسيقى: {mus_rms:+.1f} dBFS")

    # ── منحنى الكتم ──
    target = [rel_speech_db if e > voiced_thr else rel_pause_db for e in env]

    emo = 0
    if emotion_windows:
        for (a, b, rel) in emotion_windows:
            for i in range(max(0, int(a/hop_s)), min(len(target), int(b/hop_s))):
                if target[i] <= rel_pause_db + 0.01:
                    target[i] = rel
                    emo += 1
    print(f"  لحظات انفعالية: {emo*hop_s:.0f}s")

    sw = 0
    if scene_bounds:
        for b in scene_bounds:
            i0, i1 = int((b-1.2)/hop_s), int((b+0.6)/hop_s)
            for i in range(max(0, i0), min(len(target), i1)):
                if target[i] <= rel_pause_db + 0.01:
                    pos = (i-i0)/max(1, (i1-i0))
                    target[i] = rel_pause_db + 2.5*math.sin(pos*math.pi)
                    sw += 1
    print(f"  swells: {sw} نقطة")

    sm = smooth_curve(target, sr, hop_s, attack_ms=90, release_ms=520)
    offset = vo_speech - mus_rms
    gains = curve_to_samples([offset + r for r in sm], hop_s, n, sr)
    musL_t = [bedL[i]*gains[i] for i in range(n)]
    musR_t = [bedR[i]*gains[i] for i in range(n)]

    # ── SFX ──
    sfxL = [0.0]*n; sfxR = [0.0]*n
    sfx_count = 0
    if stingers:
        g = 10 ** (sfx_gain_db/20.0)
        for (t, path) in stingers:
            if not os.path.exists(path):
                continue
            sL, sR, s_sr = read_wav_stereo(path)
            if s_sr == 48000:
                sL = resample_48_to_24(sL); sR = resample_48_to_24(sR)
            j0 = int(t*sr)
            for k in range(len(sL)):
                j = j0 + k
                if 0 <= j < n:
                    sfxL[j] += sL[k]*g
                    sfxR[j] += sR[k]*g
            sfx_count += 1
    print(f"  SFX: {sfx_count} حدث @ {sfx_gain_db:+.0f} dB")

    # ── خلط ──
    ML = [voL[i] + musL_t[i] + sfxL[i] for i in range(n)]
    MR = [voR[i] + musR_t[i] + sfxR[i] for i in range(n)]

    ML, MR, log = master_stereo(ML, MR, sr, target_lufs=-14.0, ceiling=-1.5)
    for cur, d, after, tp in log:
        print(f"    {cur:+6.2f} → {d:+5.2f} dB → {after:+6.2f} LUFS · {tp:+.2f} dBTP")

    L = lufs_stereo(ML, MR, sr)
    TP = true_peak_stereo(ML, MR, sr)
    print(f"\n  ── النتيجة ──")
    print(f"  LUFS مدمج : {L:+.2f}   (الهدف −14.0)")
    print(f"  True peak : {TP:+.2f} dBTP (السقف −1.5)   BS.1770-4")
    ok = "✅" if (TP <= -1.5 and abs(L + 14) < 0.5) else "⚠️"
    print(f"  {ok}")

    voiced_idx = [i for i, e in enumerate(env) if e > voiced_thr]
    if voiced_idx:
        rels = []
        for i in voiced_idx[::7][:3000]:
            j = int(i*hop_s*sr)
            seg = musL_t[j:j+int(hop_s*sr)]
            vseg = voL[j:j+int(hop_s*sr)]
            if seg and vseg:
                rels.append(rms_db(seg) - rms_db(vseg))
        if rels:
            rels.sort()
            print(f"  الموسيقى تحت السرد: {rels[len(rels)//2]:+.1f} dB (الهدف −18…−22)")

    write_wav_stereo(out_path, ML, MR, sr)
    print(f"\n✅ {out_path}  {Path(out_path).stat().st_size/1024/1024:.1f} MB")

    if preview:
        t0, dur = preview
        a, b = int(t0*sr), int((t0+dur)*sr)
        pv = out_path.replace(".wav", f"_PREVIEW_{int(t0)}s.wav")
        write_wav_stereo(pv, ML[a:b], MR[a:b], sr)
        print(f"🎧 معاينة: {pv}  ({dur:.0f}s من {t0:.0f}s)  "
              f"{lufs_stereo(ML[a:b], MR[a:b], sr):+.1f} LUFS · "
              f"{true_peak_stereo(ML[a:b], MR[a:b], sr):+.2f} dBTP")
    return ML, MR


# ══ نقطة الدخول ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    SCENES = [20.2, 18.4, 24.5, 26.0, 19.3, 36.9, 39.5, 30.2, 27.7, 9.3, 10.0, 13.0, 13.3]
    st = [0.0]
    for d in SCENES:
        st.append(st[-1] + d)
    emotion = [(st[5], st[7], -16.5), (st[8], st[9], -16.0), (st[11], st[12]+13.3, -17.0)]
    A = "public/projects/TMB_001/audio"
    # stinger_in عند أول ظهور للرقم 4203 (S01) وعند الحريق، stinger_out عند النهاية
    sting = [(0.6, f"{A}/stinger_in.wav"),
             (st[5], f"{A}/stinger_in.wav"),
             (st[12] + 6.0, f"{A}/stinger_out.wav")]

    vo = sys.argv[1] if len(sys.argv) > 1 else "public/projects/TMB_001/vo/VO_V2_master.wav"
    mus = sys.argv[2] if len(sys.argv) > 2 else f"{A}/music.wav"
    out = sys.argv[3] if len(sys.argv) > 3 else "public/projects/TMB_001/audio/MIX_V2_full.wav"
    preview = (float(sys.argv[4]), float(sys.argv[5])) if len(sys.argv) > 5 else None

    mix(vo, mus, out, total_s=288.3, scene_bounds=st[:-1],
        emotion_windows=emotion, stingers=sting, preview=preview)
