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
import sfx as SFX  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

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
BAND_H_X, BAND_H_Y = 239, 935      # نفس موضع ومقاس المستطيل السابق
BAND_H_W, BAND_H_H = 1441, 117


def _glass_panel(W: int, H: int, r: int, pad: int = 0, alpha: int = 214) -> Image.Image:
    """زجاج دافئ شفّاف: تدرّج + لمعة علوية + إشراقة خلف النص + خطوط ذهبية رقيقة."""
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    top, bot = (58, 50, 40), (28, 24, 20)
    for y in range(H):
        k = y / max(1, H - 1)
        pd.line([(pad, y), (W - 1 - pad, y)],
                fill=(int(top[0] + (bot[0] - top[0]) * k),
                      int(top[1] + (bot[1] - top[1]) * k),
                      int(top[2] + (bot[2] - top[2]) * k), alpha))
    # إشراقة دافئة في قلب اللوح (حيث يجلس النص) — تعطي «حيوية» بدل السطح المسطّح
    glow = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(glow)
    cx, cy = W // 2, int(H * 0.5)
    steps = 26
    for i in range(steps, 0, -1):
        k = i / steps
        gd.ellipse([cx - W * 0.46 * k, cy - H * 0.95 * k,
                    cx + W * 0.46 * k, cy + H * 0.95 * k],
                   fill=int(46 * (1 - k) ** 0.7))
    warm = Image.new("RGBA", (W, H), (250, 214, 150, 0))
    warm.putalpha(glow)
    panel = Image.alpha_composite(panel, warm)
    # لمعة زجاجية أعلى اللوح
    sheen = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sheen)
    hh = max(8, int(H * 0.6))
    for y in range(hh):
        k = (1 - y / hh) ** 1.5
        sd.line([(pad, y), (W - 1 - pad, y)], fill=(240, 228, 205, int(34 * k)))
    panel = Image.alpha_composite(panel, sheen)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([pad, pad, W - 1 - pad, H - 1 - pad],
                                           radius=r, fill=255)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(panel, (0, 0), mask)
    return out


def band_h() -> str:
    """زجاج بنفس مقاس/موضع المستطيل القديم تمامًا (1441×117 عند 239,935)."""
    os.makedirs(WORK, exist_ok=True)
    path = f"{WORK}/band_h_glass.png"
    if os.path.exists(path):
        return path
    W, H, r = BAND_H_W, BAND_H_H, 10
    img = _glass_panel(W, H, r, alpha=138)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=r, outline=G.GOLD + (150,), width=2)
    d.rounded_rectangle([5, 5, W - 6, H - 6], radius=max(4, r - 4),
                        outline=(214, 192, 152, 34), width=1)
    d.line([(26, 2), (W - 27, 2)], fill=(244, 226, 188, 125), width=1)
    d.line([(60, H - 3), (W - 61, H - 3)], fill=(228, 198, 145, 46), width=1)
    d.polygon([(W // 2, 1), (W // 2 + 5, 5), (W // 2, 9), (W // 2 - 5, 5)],
              fill=G.GOLD_L + (240,))
    img.save(path)
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
    info = K.build_ass(rows, f"{d}/captions.ass", fmt=fmt,
                       audio=meta.get("audio") or meta.get("base"))
    dur = float(meta.get("dur", 0) or 0)
    sfx = f"{d}/sfx.wav"
    sfx_info = SFX.build(info["timeline"], dur + ENDPAD, sfx)
    info.update({"scrim": sc,
                 "ass": f"{d}/captions.ass", "dir": d, "sfx": sfx, "sfx_info": sfx_info})
    json.dump(info, open(f"{d}/info.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[{fmt}] captions OK: {info['cards']} بطاقة / {info['words']} كلمة / "
          f"مؤثرات: {sfx_info['words']} نقرة + {sfx_info['cards']} هوشة")
    return info


# ------------------------------------------------------------------ filters
def span_enable(spans: list) -> str:
    """تعبير إظهار: اللوح الزجاجي يظهر فقط أثناء وجود كابشن (لا لوح فارغ)."""
    if not spans:
        return "1"
    return "+".join("between(t,%.2f,%.2f)" % (a, min(b + 0.25, 1e6)) for a, b in spans)


def wm_enable(dur: float) -> str:
    parts, t = [], 20.0
    while t < dur - 1:
        parts.append(f"between(t,{t:.2f},{min(t + WM_LEN, dur - 0.3):.2f})")
        t += WM_PERIOD
    return "+".join(parts) if parts else "0"


def vfilter_h(d: str, dur: float, sc: str = "", t_off: float = 0.0,
              enable: str = "1") -> str:
    total = dur + ENDPAD
    f = []
    shift = f",setpts=PTS+{t_off:.3f}/TB" if t_off else ""
    # 1) محو الكابشن القديم المدفون (delogo) ثم لوح زجاجي بنفس مقاس المستطيل القديم
    f.append(f"[0:v]trim=0:{dur:.3f},setpts=PTS-STARTPTS,fps=25{shift},"
             "delogo=x=232:y=928:w=1455:h=131[b0]")
    f.append("[1:v]format=rgba[gl]")
    f.append(f"[b0][gl]overlay={BAND_H_X}:{BAND_H_Y}:enable='{enable}'[b1]")
    f.append(f"[b1]ass={d}/captions.ass:fontsdir={FONTS}[b2]")
    f.append("[2:v]format=rgba[bug]")
    f.append(f"[b2][bug]overlay=54:H-h-118:enable='{wm_enable(dur)}'[b4]")
    f.append(f"[3:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1,fade=t=out:st={IDENT_END - 0.45:.2f}:d=0.45:alpha=1[idn]")
    f.append(f"[b4][idn]overlay=0:0:enable='between(t,0,{IDENT_END:.2f})'[b5]")
    f.append(f"[4:v]format=rgba,trim=0:{ENDPAD + 2:.2f},setpts=PTS-STARTPTS[ec]")
    f.append(f"[b5][ec]overlay=0:0:enable='gte(t,{dur:.3f})':eof_action=pass[b6]")
    f.append("[6:a]atrim=0:%.3f,asetpts=N/SR/TB,aresample=48000,volume=1.0[fx]" % (dur + ENDPAD))
    f.append("[5:a]atrim=0:%.3f,asetpts=N/SR/TB,aresample=48000[vc]" % (dur + ENDPAD))
    f.append("[vc][fx]amix=inputs=2:duration=longest:normalize=0[aout]")
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
           "-i", base,                                  # 0 نسخة نظيفة بلا كابشن
           "-loop", "1", "-i", info["scrim"],           # 1 لوح الزجاج
           "-loop", "1", "-i", f"{d}/bug.png",          # 2
           "-loop", "1", "-i", f"{d}/ident.png",        # 3
           "-loop", "1", "-i", f"{d}/endcard.png",      # 4
           "-i", audio,                                 # 5 الصوت النهائي (موسيقى + معايرة)
           "-i", info["sfx"],                           # 6 مؤثرات صوتية
           "-filter_complex", vfilter_h(d, dur, info["scrim"], t_off=(t0 or 0.0),
                                        enable=span_enable(info.get("spans"))),
           "-map", "[vout]", "-map", "[aout]",
           "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
           "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
           "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-color_range", "tv", "-movflags", "+faststart", "-t", f"{total:.3f}"]
    if t0 is not None and t1 is not None:
        cmd += ["-frames:v", str(max(1, int((t1 - t0) * 25)))]
    cmd.append(out)
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[-4000:])
    print(f"render OK -> {out} ({os.path.getsize(out)/1e6:.1f} MB)")
    return out


# ================================================================== SHORTS (رأسي)
# الصندوق القديم في الشورتس كان من y=1196 إلى y=1612 — اللوح الزجاجي يغطّيه بالكامل
BAND_Y, BAND_H = 1298, 212
TXT_CY = 1404  # مركز اللوح = 1298 + 106


def band_assets() -> dict:
    """لوح زجاجي رأسي واحد: يغطّي الصندوق القديم بالكامل ويتمركز حوله النص."""
    d = f"{WORK}/v"
    os.makedirs(d, exist_ok=True)
    path = f"{d}/glass.png"
    if not os.path.exists(path):
        W, H, r = 1080, BAND_H, 22
        img = _glass_panel(W, H, r, pad=28, alpha=142)
        dr = ImageDraw.Draw(img)
        dr.rounded_rectangle([28, 0, W - 29, H - 1], radius=r,
                             outline=G.GOLD + (150,), width=2)
        dr.rounded_rectangle([37, 9, W - 38, H - 10], radius=max(6, r - 9),
                             outline=(212, 190, 150, 32), width=1)
        dr.line([(66, 3), (W - 67, 3)], fill=(244, 226, 188, 110), width=1)
        dr.line([(88, H - 4), (W - 89, H - 4)], fill=(228, 198, 145, 40), width=1)
        dr.polygon([(540, 0), (546, 5), (540, 10), (534, 5)], fill=G.GOLD_L + (235,))
        img.save(path)
    return {"glass": path, "rules": path, "mask": path, "dir": d}


def prep_v(srt: str, dur: float, audio: str | None = None) -> dict:
    a = band_assets()
    d = a["dir"]
    rows = K.parse_srt(srt)
    info = K.build_ass(rows, f"{d}/captions.ass", fmt="v", audio=audio)
    sfx = f"{d}/sfx.wav"
    sfx_info = SFX.build(info["timeline"], dur, sfx)
    info.update({"dur": dur, "sfx": sfx, "sfx_info": sfx_info, **a})
    print(f"[v] captions OK: {info['cards']} بطاقة / {info['words']} كلمة")
    return info


def vfilter_v(info: dict, t_off: float = 0.0, enable: str = "1") -> str:
    d = info["dir"]
    dur = info["dur"]
    f = []
    shift = f",setpts=PTS+{t_off:.3f}/TB" if t_off else ""
    # محو الصندوق القديم المدفون ثم اللوح الزجاجي فوقه
    f.append(f"[0:v]trim=0:{dur:.3f},setpts=PTS-STARTPTS,fps=25{shift},"
             "delogo=x=30:y=1186:w=1020:h=444[b0]")
    f.append("[1:v]format=rgba[gl]")
    f.append(f"[b0][gl]overlay=0:{BAND_Y}:enable='{enable}'[b1]")
    f.append(f"[b1]ass={d}/captions.ass:fontsdir={FONTS}[b2]")
    f.append("[b2]format=yuv420p,setsar=1[vout]")
    f.append("[2:a]atrim=0:%.3f,asetpts=N/SR/TB,aresample=48000,volume=1.0[fx]" % dur)
    f.append("[0:a]atrim=0:%.3f,asetpts=N/SR/TB,aresample=48000[vc]" % dur)
    f.append("[vc][fx]amix=inputs=2:duration=longest:normalize=0[aout]")
    return ";".join(f)


def render_v(base: str, srt: str, out: str, dur: float, crf: int = 19,
             preset: str = "medium", t0: float | None = None, t1: float | None = None) -> str:
    info = prep_v(srt, dur, audio=base)
    cmd = [FF, "-y", "-hide_banner", "-nostdin"]
    if t0 is not None:
        cmd += ["-ss", f"{t0:.3f}"]
    cmd += ["-i", base,
            "-loop", "1", "-i", info["glass"],
            "-i", info["sfx"],
            "-filter_complex", vfilter_v(info, t_off=(t0 or 0.0),
                                        enable=span_enable(info.get("spans"))),
            "-map", "[vout]", "-map", "[aout]",
            "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
            "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
            "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p", "-r", "25",
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
            "-color_range", "tv", "-movflags", "+faststart", "-t", f"{dur:.3f}"]
    if t0 is not None and t1 is not None:
        cmd += ["-frames:v", str(max(1, int((t1 - t0) * 25)))]
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
