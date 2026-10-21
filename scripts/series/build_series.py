"""خط إنتاج سلسلة رواق: كابشن كينتيك + علامة مائية + معرّف بداية + بطاقة ختام + موسيقى + ترميز نظيف.

الاستخدام:
    python build_series.py prep 002          # يبني أصول الفيديو (كارت، ASS، SRT، موسيقى، بطاقة ختام)
    python build_series.py render 002 [--from 0 --to 30]   # يرمّز الماستر النهائي
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

import captions as CAP  # noqa: E402
import graphics as G  # noqa: E402
import music as M  # noqa: E402
import series_data as D  # noqa: E402
import srtlib as S  # noqa: E402

REPO = "/home/user/Riwaq_System_Repo"
DRIVE = f"{REPO}/google_drive"
WORK = f"{DRIVE}/work"
ASSETS = f"{REPO}/assets/series_riwaq"
OUT = f"{REPO}/outputs/SERIES_RIWAQ"
FF = "/tmp/venv/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
FONTS = f"{REPO}/public/fonts"

ENDPAD = 4.0          # بطاقة الختام
IDENT_END = 1.7       # معرّف البداية
WM_PERIOD = 30.0      # كل 30 ثانية
WM_LEN = 6.0
WM_FADE = 0.5
BED_DB = -26.0
STING_DB = -21.0
OUTRO_DB = -14.0


def sh(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    p = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if p.returncode != 0:
        raise RuntimeError(f"FAILED: {' '.join(cmd[:8])}...\n{p.stderr[-3000:]}")
    return p


# وقفات الكلام الحقيقية (من silencedetect على المصادر) — تُحفظ في التوقيت ولا يفرغ فيها الشريط
SILENCES = {
    "002": [(19.84, 20.89), (71.38, 71.88), (112.43, 113.31), (123.04, 124.21),
            (133.07, 133.57), (164.82, 165.25), (204.84, 205.50)],
    "003": [(30.66, 31.42), (41.09, 41.73), (60.71, 61.28), (91.71, 92.42),
            (123.23, 124.28), (163.52, 164.05), (164.89, 165.39), (183.89, 184.29)],
    "004": [(50.62, 51.33), (91.93, 92.43), (102.19, 103.03), (184.13, 185.13),
            (194.66, 195.17), (225.49, 226.18)],
}


def vdir(key: str) -> str:
    d = f"{OUT}/{key}"
    os.makedirs(d, exist_ok=True)
    return d


def adir(key: str) -> str:
    d = f"{WORK}/build_{key}"
    os.makedirs(d, exist_ok=True)
    return d


def src(key: str) -> str:
    return f"{DRIVE}/MASTER_WEB_RELATIONSHIP_{key}.mp4"


# ---------------------------------------------------------------- assets
def build_assets(key: str) -> dict:
    v = D.by_key(key)
    a = adir(key)
    dur = v["duration"]

    # كارت الكابشن + العلامة المائية + بطاقة الختام
    G.caption_card().crop((239, 935, 1681, 1053)).save(f"{a}/card.png")
    G.watermark_bug(96).save(f"{a}/bug.png")
    G.ident_lockup().save(f"{a}/ident.png")
    nxt = D.by_key(v["next"])["title_a"] if v["next"] else None
    G.endcard(v["order"], D.TOTAL, nxt, series=D.SERIES, channel=D.CHANNEL).save(f"{a}/endcard.png")

    # الكابشن: استعادة النص المتصل، ثم النص المحرّر يدويًا، ثم إعادة تقطيع وتوقيت
    cues = S.parse_srt(f"{WORK}/srt_{key}.srt")
    words = S.reconstruct(cues)
    rows = S.build_caption_rows(words, dur)
    ar_final = json.load(open(f"{WORK}/ar_{key}.json", encoding="utf-8")) if os.path.exists(f"{WORK}/ar_{key}.json") else None
    en_final = json.load(open(f"{WORK}/en_{key}.json", encoding="utf-8")) if os.path.exists(f"{WORK}/en_{key}.json") else None
    if ar_final:
        assert len(ar_final) == len(rows), f"AR rows mismatch {len(ar_final)} != {len(rows)}"
    rows = CAP.apply_final(rows, ar_final, en_final, silences=SILENCES.get(key, []))
    CAP.build_ass(rows, f"{a}/captions.ass")
    CAP.build_ar_srt(rows, f"{a}/CAPTIONS_AR.srt")
    if en_final:
        en_rows = [{"start": r["start"], "end": r["end"], "text": r["en"] or r["text"]} for r in rows]
    else:
        en_rows = S.build_en_rows(rows, cues)
    CAP.build_en_srt(en_rows, f"{a}/CAPTIONS_EN.srt")
    CAP.build_bilingual_srt(rows, en_rows, f"{a}/CAPTIONS_AR_EN.srt")

    # الموسيقى: إنترو/أوترو مشتركة + طبقة بطول الفيديو
    os.makedirs(f"{ASSETS}/music", exist_ok=True)
    if not os.path.exists(f"{ASSETS}/music/MUSIC_INTRO_riwaq.wav"):
        M.write_wav(f"{ASSETS}/music/MUSIC_INTRO_riwaq.wav", M.intro())
        M.write_wav(f"{ASSETS}/music/MUSIC_OUTRO_riwaq.wav", M.outro())
    if not os.path.exists(f"{ASSETS}/music/MUSIC_BED_series.wav"):
        # طبقة طويلة تُستخدم لكل الفيديوهات (ثبات الهوية)
        M.write_wav(f"{ASSETS}/music/MUSIC_BED_series.wav", M.bed(120.0, dbfs=-18.0))

    meta = {
        "key": key, "order": v["order"], "duration": dur,
        "rows": len(rows), "words": len(words),
        "total_out": dur + ENDPAD,
    }
    json.dump(meta, open(f"{a}/assets.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[{key}] assets OK: {len(rows)} بطاقة، {len(words)} كلمة، مدة الخروج {meta['total_out']:.2f}s")
    return meta


# ---------------------------------------------------------------- filters
def watermark_enable(dur: float) -> str:
    """نافذة ظهور كل 30 ثانية: من 20s من كل دورة، لمدة 6s، مع تلاشي."""
    parts = []
    t = 20.0
    while t < dur - 1:
        st = t
        en = min(t + WM_LEN, dur - 0.3)
        parts.append(
            f"between(t,{st:.2f},{en:.2f})"
            if not parts else f"between(t,{st:.2f},{en:.2f})"
        )
        t += WM_PERIOD
    return "+".join(parts) if parts else "0"


def video_filter(key: str, dur: float, upto: float | None = None) -> str:
    a = adir(key)
    total = dur + ENDPAD
    wm_enable = watermark_enable(dur)
    # تلاشي داخل/خارج العلامة المائية: نستخدم enable + alpha عبر fade على وقت ثابت غير ممكن،
    # لذا نعتمد على شفافية PNG (58%) مع ظهور/اختفاء عبر enable — مقبول بصريًا.
    f = []
    f.append("[0:v]trim=0:%.3f,setpts=PTS-STARTPTS[base]" % total)
    # كارت الكابشن + ASS كينتيك
    f.append("[1:v]format=rgba[card]")
    f.append("[base][card]overlay=239:935:enable='between(t,0,%.3f)'[b1]" % dur)
    f.append("[b1]ass=%s/captions.ass:fontsdir=%s[b2]" % (a, FONTS))
    # العلامة المائية الدورية
    f.append("[2:v]format=rgba,scale=iw:ih[bug]")
    f.append("[b2][bug]overlay=54:H-h-118:enable='%s'[b3]" % wm_enable)
    # معرّف البداية
    f.append("[3:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1,fade=t=out:st=%.2f:d=0.45:alpha=1[idn]"
             % (IDENT_END - 0.45))
    f.append("[b3][idn]overlay=0:0:enable='between(t,0,%.2f)'[b4]" % IDENT_END)
    # بطاقة الختام في النهاية
    f.append("[4:v]trim=0:%.2f,setpts=PTS-STARTPTS[ec]" % ENDPAD)
    f.append("[b4][ec]overlay=0:0:enable='gte(t,%.3f)'[b5]" % dur)
    # انتقال ناعم إلى البطاقة (تلاشي أبيض/أسود خفيف) + خروج
    f.append("[b5]fade=t=in:st=0:d=0.30,fade=t=out:st=%.2f:d=0.55[b6]" % (total - 0.55))
    f.append("[b6]format=yuv420p,scale=1920:1080:flags=lanczos,setsar=1[vout]")
    return ";".join(f)


def audio_filter(key: str, dur: float) -> str:
    a = adir(key)
    total = dur + ENDPAD
    f = []
    f.append("[0:a]atrim=0:%.3f,asetpts=N/SR/TB,aresample=48000,asplit=2[voice][sc]" % dur)
    # الطبقة الموسيقية: تُقصّ لطول الفيديو وتُخفض تحت الكلام (ducking)
    f.append("[5:a]atrim=0:%.3f,asetpts=N/SR/TB,volume=0.5,aresample=48000[bedraw]" % dur)
    f.append("[bedraw][sc]sidechaincompress=threshold=0.03:ratio=9:attack=25:release=420:"
             "makeup=1:level_sc=1[bed]" % ())
    # إنترو: تحت أول 4.4 ثانية بمستوى هادئ
    f.append("[6:a]atrim=0:4.4,asetpts=N/SR/TB,volume=0.42,aresample=48000[in]")
    # أوترو: يبدأ قبل نهاية الكلام بـ 0.6s ويمتد على بطاقة الختام
    f.append("[7:a]atrim=0:%.2f,asetpts=N/SR/TB,volume=0.62,adelay=%d|%d,aresample=48000[out]"
             % (ENDPAD + 0.6, int((dur - 0.6) * 1000), int((dur - 0.6) * 1000)))
    f.append("[voice][bed][in][out]amix=inputs=4:duration=longest:normalize=0[premix]")
    f.append("[premix]apad=pad_dur=%.2f,atrim=0:%.3f,loudnorm=I=-14:TP=-1.5:LRA=11,"
             "aresample=48000,alimiter=limit=0.89:level=disabled[aout]" % (ENDPAD, total))
    return ";".join(f)


def render(key: str, t0: float | None = None, t1: float | None = None, crf: int = 18,
           preset: str = "medium", out_name: str | None = None) -> str:
    v = D.by_key(key)
    a = adir(key)
    dur = v["duration"]
    total = dur + ENDPAD
    os.makedirs(f"{OUT}/{key}", exist_ok=True)
    out = out_name or f"{OUT}/{key}/MASTER_FINAL_{key}.mp4"

    cmd = [FF, "-y", "-hide_banner", "-nostdin",
           "-i", src(key),
           "-loop", "1", "-i", f"{a}/card.png",
           "-loop", "1", "-i", f"{a}/bug.png",
           "-loop", "1", "-i", f"{a}/ident.png",
           "-loop", "1", "-i", f"{a}/endcard.png",
           "-stream_loop", "-1", "-i", f"{ASSETS}/music/MUSIC_BED_series.wav",
           "-i", f"{ASSETS}/music/MUSIC_INTRO_riwaq.wav",
           "-i", f"{ASSETS}/music/MUSIC_OUTRO_riwaq.wav",
           "-filter_complex", video_filter(key, dur) + ";" + audio_filter(key, dur),
           "-map", "[vout]", "-map", "[aout]",
           "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
           "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-color_range", "tv",
           "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
           "-movflags", "+faststart",
           "-t", f"{total:.3f}"]
    if t0 is not None:
        cmd += ["-ss", str(t0)]
    if t1 is not None:
        cmd += ["-frames:v", str(int((t1 - (t0 or 0)) * 25))]
    cmd.append(out)
    sh(cmd)
    print(f"[{key}] render OK -> {out} ({os.path.getsize(out)/1e6:.1f} MB)")
    return out


if __name__ == "__main__":
    mode = sys.argv[1]
    key = sys.argv[2]
    if mode == "prep":
        build_assets(key)
    elif mode == "render":
        t0 = float(sys.argv[sys.argv.index("--from") + 1]) if "--from" in sys.argv else None
        t1 = float(sys.argv[sys.argv.index("--to") + 1]) if "--to" in sys.argv else None
        name = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
        render(key, t0, t1, out_name=name)
    else:
        raise SystemExit("unknown mode")
