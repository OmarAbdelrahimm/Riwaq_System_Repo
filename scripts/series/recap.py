"""إعادة بناء الكابشن المحروق (نظام v2) على فيديوهات منشورة بالفعل.

الفكرة: الفيديو الأصلي «النظيف» (قبل حرق الكابشن) + الكابشن الجديد + نفس هوية رواق،
مع إعادة استخدام المسار الصوتي النهائي كما هو (موسيقى + معايرة صوت) فلا تتغيّر جودة الصوت.

    python3 recap.py still h 40            # إطار تجريبي للمراجعة السريعة
    python3 recap.py render h              # الماستر الجديد (حلقة 01)
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

import graphics as G  # noqa: E402
import kinetic as K  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

REPO = "/home/user/Riwaq_System_Repo"
DRIVE = f"{REPO}/google_drive"
WORK = f"{REPO}/google_drive/work/capfix"
OUT = f"{REPO}/outputs/SERIES_RIWAQ/CAPFIX"
FONTS = f"{REPO}/public/fonts"


def ffmpeg() -> str:
    env = os.environ.get("FFMPEG")
    if env and os.path.exists(env):
        return env
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


FF = ffmpeg()
ENDPAD = 4.0
IDENT_END = 1.7
WM_PERIOD = 30.0
WM_LEN = 6.0

# ------------------------------------------------------------------ scrim
def scrim(fmt: str = "h") -> str:
    """تدرّج تعتيم ناعم يلتصق بالنص (بدل المستطيل الفارغ) — يُبنى مرة واحدة."""
    os.makedirs(WORK, exist_ok=True)
    path = f"{WORK}/scrim_{fmt}.png"
    if os.path.exists(path):
        return path
    if fmt == "h":
        W, H = 1920, 420
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        px = img.load()
        for y in range(H):
            t = y / (H - 1)              # 0 أعلى الشريط → 1 أسفل الإطار
            a = 236 * (t ** 2.35)
            a *= 0.86 + 0.14 * math.sin(min(1.0, t * 1.4) * 3.14159)
            for x in range(W):
                # تعتيم أوسع قليلًا في الوسط ليحتضن النص
                px[x, y] = (9, 8, 7, int(round(min(236, max(0, a)))))
    else:
        W, H = 1080, 850
        y0, y1 = 1070, 1920
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        px = img.load()
        for y in range(H):
            t = y / (H - 1)
            # منحنى جرسيّ: شفاف أعلى وأسفل، أقصى تعتيم عند ثلث النص
            a = int(round(200 * max(0.0, min(1.0, (t ** 0.85) * (1 - max(0.0, t - 0.55) / 0.65)))))
            for x in range(W):
                px[x, y] = (8, 7, 6, a)
    from PIL import ImageFilter as _IF
    img = img.filter(_IF.GaussianBlur(26))
    img.save(path)
    return path


def _hairline(fmt: str, cy: int) -> Image.Image:
    """خط ذهبي رفيع + معيّن صغير فوق الكابشن — لمسة رواق (لا صندوق)."""
    if fmt == "h":
        W, H = 1920, 60
    else:
        W, H = 1080, 70
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = H // 2
    cx = W // 2
    half = 150 if fmt == "h" else 120
    for k in range(2):
        a = 150 - k * 60
        d.line([(cx - half, y), (cx - 14, y)], fill=G.GOLD_L + (a,), width=1)
        d.line([(cx + 14, y), (cx + half, y)], fill=G.GOLD_L + (a,), width=1)
    d.polygon([(cx, y - 6), (cx + 6, y), (cx, y + 6), (cx - 6, y)], fill=G.GOLD_L + (190,))
    return img


# ------------------------------------------------------------------ assets
def band_h() -> str:
    """شريط رواق السفلي (lower third): تغطية أنيقة لنصّ المصدر المحروق + وعاء الكابشن الكينتيك."""
    os.makedirs(WORK, exist_ok=True)
    path = f"{WORK}/band_h.png"
    if os.path.exists(path):
        return path
    W, Hh = 1560, 206
    img = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # تعبئة متدرّجة من الحبر
    for y in range(Hh):
        t = y / (Hh - 1)
        a = 255
        d.line([(8, y), (W - 8, y)], fill=(15, 13, 11, a))
    mask = Image.new("L", (W, Hh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, W - 1, Hh - 1], radius=14, fill=255)
    out = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    d = ImageDraw.Draw(out)
    d.rounded_rectangle([0, 0, W - 1, Hh - 1], radius=14, outline=G.GOLD + (150,), width=2)
    d.rounded_rectangle([7, 7, W - 8, Hh - 8], radius=10, outline=G.GOLD_L + (46,), width=1)
    # خط ذهبي علوي + معيّن في المنتصف
    d.line([(34, 4), (W - 34, 4)], fill=G.GOLD_L + (120,), width=1)
    d.polygon([(W // 2, 1), (W // 2 + 5, 5), (W // 2, 9), (W // 2 - 5, 5)], fill=G.GOLD_L + (215,))
    out.save(path)
    return path


def prep(fmt: str = "h", meta: dict | None = None) -> dict:
    os.makedirs(WORK, exist_ok=True)
    d = f"{WORK}/{fmt}"
    os.makedirs(d, exist_ok=True)
    meta = meta or {}
    sc = band_h() if fmt == "h" else scrim(fmt)
    hl = _hairline(fmt, 0)
    hl.save(f"{d}/hairline.png")
    G.watermark_bug(96 if fmt == "h" else 78).save(f"{d}/bug.png")
    G.ident_lockup().save(f"{d}/ident.png") if fmt == "h" else None
    if meta.get("endcard"):
        meta["endcard"].save(f"{d}/endcard.png")
    rows = K.parse_srt(meta["srt"])
    info = K.build_ass(rows, f"{d}/captions.ass", fmt=fmt)
    info.update({"scrim": sc, "hairline": f"{d}/hairline.png", "ass": f"{d}/captions.ass",
                 "dir": d})
    json.dump(info, open(f"{d}/info.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[{fmt}] captions OK: {info}")
    return info


# ------------------------------------------------------------------ filters
def wm_enable(dur: float) -> str:
    parts, t = [], 20.0
    while t < dur - 1:
        parts.append(f"between(t,{t:.2f},{min(t + WM_LEN, dur - 0.3):.2f})")
        t += WM_PERIOD
    return "+".join(parts) if parts else "0"


def vfilter_h(d: str, dur: float, sc: str = "") -> str:
    total = dur + ENDPAD
    f = []
    f.append(f"[0:v]trim=0:{dur:.3f},setpts=PTS-STARTPTS,fps=25[base]")
    f.append("[1:v]format=rgba[sc]")
    f.append("[base][sc]overlay=180:858[b1]")
    f.append(f"[b1]ass={d}/captions.ass:fontsdir={FONTS}[b2]")
    f.append("[2:v]format=rgba[bug]")
    f.append(f"[b2][bug]overlay=54:H-h-118:enable='{wm_enable(dur)}'[b4]")
    f.append(f"[3:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1,fade=t=out:st={IDENT_END - 0.45:.2f}:d=0.45:alpha=1[idn]")
    f.append(f"[b4][idn]overlay=0:0:enable='between(t,0,{IDENT_END:.2f})'[b5]")
    f.append(f"[4:v]format=rgba,trim=0:{ENDPAD:.2f},setpts=PTS-STARTPTS[ec]")
    f.append(f"[b5][ec]overlay=0:0:enable='gte(t,{dur:.3f})'[b6]")
    f.append(f"[b6]fade=t=in:st=0:d=0.30,fade=t=out:st={total - 0.55:.2f}:d=0.55,"
             "format=yuv420p,setsar=1[vout]")
    return ";".join(f)


def render_h(base: str, audio: str, srt: str, out: str, meta: dict | None = None,
             crf: int = 19, preset: str = "medium", t0: float | None = None,
             t1: float | None = None) -> str:
    meta = dict(meta or {})
    meta["srt"] = srt
    info = prep("h", meta)
    d = info["dir"]
    dur = meta["dur"]
    total = dur + ENDPAD
    cmd = [FF, "-y", "-hide_banner", "-nostdin",
           "-i", base,                                  # 0
           "-i", info["scrim"],                         # 1 الشريط
           "-loop", "1", "-i", f"{d}/bug.png",          # 2
           "-loop", "1", "-i", f"{d}/ident.png",        # 3
           "-loop", "1", "-i", f"{d}/endcard.png",      # 4
           "-i", audio,                                 # 5
           "-filter_complex", vfilter_h(d, dur, info["scrim"]),
           "-map", "[vout]", "-map", "5:a", "-c:a", "copy",
           "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
           "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-color_range", "tv", "-movflags", "+faststart", "-t", f"{total:.3f}"]
    if t0 is not None and t1 is not None:
        cmd += ["-frames:v", str(int((t1 - t0) * 25)), "-ss", str(t0)]
    cmd.append(out)
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[-4000:])
    print(f"render OK -> {out} ({os.path.getsize(out)/1e6:.1f} MB)")
    return out


# ================================================================== SHORTS (رأسي)
BAND_Y, BAND_H = 1128, 380


def band_assets() -> dict:
    """قناع تدرّج + خطّان ذهبيان للشريط الزجاجي (frosted band) في الشورتس."""
    d = f"{WORK}/v"
    os.makedirs(d, exist_ok=True)
    mask_p, rules_p = f"{d}/mask.png", f"{d}/rules.png"
    if not os.path.exists(mask_p):
        m = Image.new("L", (1080, BAND_H), 0)
        px = m.load()
        top, bot = 120, 45
        for y in range(BAND_H):
            if y < top:
                a = int(255 * (y / top) ** 1.5)
            elif y > BAND_H - bot:
                a = int(255 * ((BAND_H - y) / bot) ** 1.5)
            else:
                a = 255
            for x in range(1080):
                px[x, y] = a
        m.save(mask_p)
    if not os.path.exists(rules_p):
        r = Image.new("RGBA", (1080, BAND_H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(r)
        y = BAND_H - 62
        for x in range(150, 930):
            k = min(1.0, (x - 150) / 190, (930 - x) / 190)
            dd.point((x, y), fill=G.GOLD_L + (int(190 * max(0.0, k)),))
        dd.polygon([(540, y - 7), (547, y), (540, y + 7), (533, y)], fill=G.GOLD_L + (235,))
        r.save(rules_p)
    return {"mask": mask_p, "rules": rules_p, "dir": d}


def prep_v(srt: str, dur: float) -> dict:
    a = band_assets()
    d = a["dir"]
    G.watermark_bug(78).save(f"{d}/bug.png")
    rows = K.parse_srt(srt)
    info = K.build_ass(rows, f"{d}/captions.ass", fmt="v")
    info.update({"dur": dur, **a})
    print(f"[v] captions OK: {info['cards']} بطاقة / {info['words']} كلمة")
    return info


def vfilter_v(info: dict) -> str:
    d = info["dir"]
    dur = info["dur"]
    f = []
    f.append(f"[0:v]trim=0:{dur:.3f},setpts=PTS-STARTPTS,fps=25,split[bA][bB]")
    f.append(f"[bB]crop=1080:{BAND_H}:0:{BAND_Y},boxblur=38:3,eq=brightness=-0.02:saturation=0.9,"
             "colorchannelmixer=rr=0.28:gg=0.26:bb=0.24[bl]")
    f.append("[1:v]format=gray,colorchannelmixer=aa=0.88[mk]")
    f.append("[bl][mk]alphamerge[band]")
    f.append(f"[bA][band]overlay=0:{BAND_Y}:format=auto[b1]")
    f.append(f"[b1]ass={d}/captions.ass:fontsdir={FONTS}[b2]")
    f.append("[2:v]format=rgba[rl]")
    f.append(f"[b2][rl]overlay=0:{BAND_Y}[b3]")
    f.append("[3:v]format=rgba[bug]")
    f.append(f"[b3][bug]overlay={(1080 - 171) // 2}:1730:enable='{wm_enable(dur)}'[b4]")
    f.append("[b4]format=yuv420p,setsar=1[vout]")
    return ";".join(f)


def render_v(base: str, srt: str, out: str, dur: float, crf: int = 19,
             preset: str = "medium", t0: float | None = None, t1: float | None = None) -> str:
    info = prep_v(srt, dur)
    cmd = [FF, "-y", "-hide_banner", "-nostdin", "-i", base,
           "-loop", "1", "-i", info["mask"],
           "-loop", "1", "-i", info["rules"],
           "-loop", "1", "-i", f"{info['dir']}/bug.png",
           "-filter_complex", vfilter_v(info),
           "-map", "[vout]", "-map", "0:a", "-c:a", "copy",
           "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
           "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p", "-r", "25",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-color_range", "tv", "-movflags", "+faststart", "-t", f"{dur:.3f}"]
    if t0 is not None and t1 is not None:
        cmd += ["-frames:v", str(int((t1 - t0) * 25)), "-ss", str(t0)]
    cmd.append(out)
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[-4000:])
    print(f"render V OK -> {out} ({os.path.getsize(out)/1e6:.1f} MB)")
    return out


# ------------------------------------------------------------------ pilot config
PILOT = {
    "key": "01",
    "base": f"{DRIVE}/MASTER_WEB_RELATIONSHIP_002.mp4",
    "audio": f"{DRIVE}/الفيديو 01 — العلاقات أعمق من التواصل (ماستر).mp4",
    "srt": f"{DRIVE}/05_CAPTIONS_AR.srt",
    "dur": 293.88,
    "order": 1, "total": 6,
    "next": "المقارنة أداة لا معيار: كيف تسعى للأفضل دون قسوة؟",
}

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "still"
    os.makedirs(OUT, exist_ok=True)
    if mode == "still":
        t = float(sys.argv[2]) if len(sys.argv) > 2 else 40.0
        ec = G.endcard(PILOT["order"], PILOT["total"], PILOT["next"])
        m = dict(PILOT)
        m["endcard"] = ec
        render_h(PILOT["base"], PILOT["audio"], PILOT["srt"], f"{OUT}/STILL.mp4",
                 meta=m, t0=t, t1=t + 0.08)
    elif mode in ("still_v", "render_v"):
        base = f"{DRIVE}/الشورت 01 — العلاقات أعمق من التواصل (ماستر).mp4"
        srt = f"{REPO}/outputs/SERIES_RIWAQ/SHORTS/S01/CAPTIONS_AR.srt"
        if mode == "still_v":
            t = float(sys.argv[2]) if len(sys.argv) > 2 else 20.0
            render_v(base, srt, f"{OUT}/STILL_V.mp4", 53.16, t0=t, t1=t + 0.08)
        else:
            render_v(base, srt, f"{OUT}/SHORT_CAPFIX_S01.mp4", 49.96)
    elif mode == "render":
        ec = G.endcard(PILOT["order"], PILOT["total"], PILOT["next"])
        m = dict(PILOT)
        m["endcard"] = ec
        render_h(PILOT["base"], PILOT["audio"], PILOT["srt"],
                 f"{OUT}/MASTER_CAPFIX_01.mp4", meta=m)
