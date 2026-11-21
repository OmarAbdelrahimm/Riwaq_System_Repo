#!/usr/bin/env python3
"""
mix_shorts.py — مكس صوت الشورتات V2
=====================================
نفس فلسفة الفيلم الطويل بس للـ30/32 ثانية:
  · سرد معالج (EQ + de-esser + كومبرس) — نفس سلسلة الفيلم
  · موسيقى ستيريو بـducking (18–22 dB تحت السرد في الكلام)
  · عند سكتات الصوت → الموسيقى ترتفع (مش صمت ميت)
  · لوب سلس بكريسفيد
  · −14 LUFS مدمج · ≤ −1.5 dBTP (BS.1770-4)
"""
import sys, os, math, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audio_master import read_wav, write_wav, biquad, de_ess, compress, lufs
from audio_mix import (read_wav_stereo, write_wav_stereo, lufs_stereo,
                       true_peak_stereo, resample_48_to_24, build_bed,
                       envelope_db, smooth_curve, curve_to_samples,
                       master_stereo, rms_db)

FF = "node_modules/@remotion/compositor-linux-x64-gnu/ffmpeg"


def decode_mp3(src, dst):
    r = subprocess.run([FF, "-y", "-i", src, "-ar", "24000", "-ac", "1",
                        "-c:a", "pcm_s16le", dst], capture_output=True)
    if not os.path.exists(dst):
        raise RuntimeError(f"فشل فك {src}: {r.stderr.decode()[-400:]}")


def process_vo(x, sr):
    """نفس سلسلة الفيلم — EQ + de-esser + كومبرس."""
    y = [float(v) for v in x]
    pk = max(abs(v) for v in y)
    y = [v * ((10 ** (-6 / 20) * 32768) / pk) for v in y]
    y = biquad(y, sr, "hpf", 75, q=0.7)
    y = biquad(y, sr, "peak", 340, gain_db=-2.5, q=1.0)
    y = biquad(y, sr, "peak", 1300, gain_db=+3.0, q=0.9)
    y = biquad(y, sr, "peak", 3200, gain_db=+1.5, q=1.0)
    y = biquad(y, sr, "highshelf", 9000, gain_db=+0.5, q=0.7)
    y = de_ess(y, sr, lo=5000, hi=9000, thresh_db=-26.0, ratio=3.5)
    y = compress(y, sr, thresh_db=-22.0, ratio=2.0, attack_ms=18, release_ms=260)
    return y


def mix_one(vo_mp3, music, out, total_s):
    sr = 24000
    tmp = f"/tmp/{os.path.basename(vo_mp3)}.wav"
    decode_mp3(vo_mp3, tmp)
    vo, _ = read_wav(tmp)
    D = len(vo) / sr
    print(f"\n{'='*70}\n  {os.path.basename(vo_mp3)}  →  {os.path.basename(out)}")
    print(f"{'='*70}")
    print(f"  السرد: {D:.2f}s (الفيلم {total_s:.0f}s → {total_s-D:.2f}s بدون كلام)")

    vo = process_vo(vo, sr)
    print(f"  بعد المعالجة: {lufs(vo, sr):+.1f} LUFS")

    # ── تمديد ذكي: نوزّع الفراغ على الجمل بدل ما يبقى كله في الآخر ──
    # نلاقي الجمل بـsilence detection محلي
    win = int(0.02 * sr)
    env = []
    for i in range(0, len(vo) - win, win):
        seg = vo[i:i + win]
        r = math.sqrt(sum(v * v for v in seg) / win)
        env.append((i / sr, 20 * math.log10(r / 32768) if r > 0 else -99))
    thr = max(e[1] for e in env) - 30
    # حدود الجمل
    bounds = []
    prev = False
    for t, d in env:
        cur = d > thr
        if cur and not prev:
            bounds.append([t, t])
        elif cur and bounds:
            bounds[-1][1] = t
        prev = cur
    bounds = [b for b in bounds if b[1] - b[0] > 0.25]
    print(f"  الجمل المكتشفة: {len(bounds)}")

    pad_total = total_s - D
    if bounds and pad_total > 0.2:
        # نوزّع الفراغ: 30% قبل أول جملة، 70% موزّع على الفراغات بين الجمل
        gaps = []
        for k in range(len(bounds) - 1):
            g = bounds[k+1][0] - bounds[k][1]
            if g > 0.05:
                gaps.append((k, g))
        extra = pad_total * 0.7
        if gaps:
            per = extra / len(gaps)
            out = []
            pos = 0
            for k, (bi, g) in enumerate(gaps):
                end = int((bounds[bi][1] + per) * sr)
                out.extend(vo[pos:end])
                sil = int((extra / len(gaps)) * sr)
                out.extend([0.0] * sil)
                pos = int(bounds[bi][1] * sr) + int((bounds[bi+1][0] - bounds[bi][1]) * sr)
            out.extend(vo[pos:])
            # نضبط الطول
            lead = int(pad_total * 0.3 * sr)
            out = [0.0] * lead + out
            vo = out[:int(total_s * sr)]
            vo += [0.0] * (int(total_s * sr) - len(vo))
            print(f"  وزّعت {pad_total:.1f}s على {len(gaps)} فراغ + {lead/sr:.1f}s مقدمة")
        D = len(vo) / sr

    mL, mR, msr = read_wav_stereo(music)
    if msr == 48000:
        mL = resample_48_to_24(mL)
        mR = resample_48_to_24(mR)

    n = int(total_s * sr)
    voL = vo[:n] + [0.0] * max(0, n - len(vo))
    voL = voL[:n]

    bedL, loops = build_bed(mL, n, sr, xfade_s=0.8)
    bedR, _ = build_bed(mR, n, sr, xfade_s=0.8)
    print(f"  لوب: {loops} لفة")

    env, hop_s = envelope_db(voL, sr)
    thr = -38.0
    speech = sum(1 for e in env if e > thr) / len(env)
    print(f"  كلام: {speech*100:.0f}% من الزمن")

    vo_speech = rms_db([v for v in voL if abs(v) > 200])
    mus_rms = rms_db(bedL)
    # الشورتات أسرع: الموسيقى أقرب شوية (18 dB تحت)
    target = [-18.0 if e > thr else -8.0 for e in env]
    sm = smooth_curve(target, sr, hop_s, attack_ms=60, release_ms=380)
    gains = curve_to_samples([(vo_speech - mus_rms) + r for r in sm], hop_s, n, sr)
    musL = [bedL[i] * gains[i] for i in range(n)]
    musR = [bedR[i] * gains[i] for i in range(n)]

    ML = [voL[i] + musL[i] for i in range(n)]
    MR = [voL[i] + musR[i] for i in range(n)]

    ML, MR, log = master_stereo(ML, MR, sr, target_lufs=-14.0, ceiling=-1.5)
    L = lufs_stereo(ML, MR, sr)
    TP = true_peak_stereo(ML, MR, sr)

    # قياس الموسيقى تحت السرد
    voiced = [i for i, e in enumerate(env) if e > thr]
    rels = []
    for i in voiced[::3]:
        j = int(i * hop_s * sr)
        seg = musL[j:j + int(hop_s * sr)]
        vg = voL[j:j + int(hop_s * sr)]
        if seg and vg:
            rels.append(rms_db(seg) - rms_db(vg))
    rels.sort()
    rel = rels[len(rels)//2] if rels else 0

    print(f"\n  LUFS مدمج : {L:+.2f}  (الهدف −14.0)")
    print(f"  True peak : {TP:+.2f} dBTP (السقف −1.5)")
    print(f"  موسيقى/سرد: {rel:+.1f} dB")
    ok = TP <= -1.5 and abs(L + 14) < 0.6
    print(f"  {'✅' if ok else '⚠️'}")
    write_wav_stereo(out, ML, MR, sr)
    print(f"✅ {out}  {os.path.getsize(out)/1024/1024:.1f} MB")
    return ok


if __name__ == "__main__":
    A = "public/projects/TMB_001"
    ok = []
    ok.append(mix_one(f"{A}/vo/shortA_vo.mp3", f"{A}/audio/music.wav",
                      f"{A}/audio/SHORT_A_MIX_V2.wav", 30.0))
    ok.append(mix_one(f"{A}/vo/shortB_vo.mp3", f"{A}/audio/music.wav",
                      f"{A}/audio/SHORT_B_MIX_V2.wav", 32.0))
    sys.exit(0 if all(ok) else 1)
