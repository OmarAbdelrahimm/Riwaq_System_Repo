"""خط إنتاج شورتس رواق: معرّف رأسي + علامة دورية + بطاقة ختام + صوت موحّد + أغلفة A/B.

الاستخدام:
    python3 build_shorts.py assets            # يبني أصول الشورتس التسعة
    python3 build_shorts.py render S01        # يرمّز شورتًا واحدًا
    python3 build_shorts.py all               # الأصول + التسعة + الحزم
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

import graphics as G  # noqa: E402
import shorts_captions as SC  # noqa: E402
import shorts_data as D  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

REPO = "/home/user/Riwaq_System_Repo"
WORK = f"{REPO}/google_drive/work"
OUT = f"{REPO}/outputs/SERIES_RIWAQ/SHORTS"
ASSETS = f"{REPO}/assets/series_riwaq/music"
W, H = 1080, 1920

IDENT_END = 1.5
ENDPAD = 3.2
WM_PERIOD = 30.0
WM_LEN = 5.0


def ffmpeg() -> str:
    env = os.environ.get("FFMPEG")
    if env and os.path.exists(env):
        return env
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


FF = ffmpeg()


def sh(cmd: list[str]) -> None:
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"FAILED: {' '.join(cmd[:6])}...\n{p.stderr[-2500:]}")


def probe_dur(path: str) -> float:
    p = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True, text=True)
    for line in p.stderr.splitlines():
        if "Duration:" in line:
            t = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = t.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError("no duration")


def sdir(key: str) -> str:
    d = f"{WORK}/build_short_{key}"
    os.makedirs(d, exist_ok=True)
    return d


# ------------------------------------------------------------------ graphics
def _frame(w=W, h=H, inset=22) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([inset, inset, w - inset, h - inset], outline=G.GOLD + (255,), width=3)
    d.rectangle([inset + 12, inset + 12, w - inset - 12, h - inset - 12],
                outline=(120, 99, 54, 255), width=1)
    return img, d


def _veil(alpha: int = 168) -> Image.Image:
    """تعتيم متدرّج: أغمق في الوسط حيث النص، مع بقاء أثر الصورة."""
    v = Image.new("RGBA", (W, H), (8, 7, 6, alpha))
    return v


def caption_card() -> Image.Image:
    """بطاقة الكابشن الرأسية: تغطّي شريط الإيجنت الآخر القديم بنفس لغة رواق."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x0, x1 = 44, W - 44
    y0, y1 = 1196, 1612
    d.rounded_rectangle([x0, y0, x1, y1], radius=12, fill=(13, 12, 10, 255),
                        outline=G.GOLD + (130,), width=2)
    d.line([(x0 + 26, y0 + 2), (x1 - 26, y0 + 2)], fill=G.GOLD_L + (80,), width=1)
    d.line([(x0 + 26, y1 - 2), (x1 - 26, y1 - 2)], fill=G.GOLD_L + (70,), width=1)
    return img


def ident_vertical(s: dict) -> Image.Image:
    """لمحة الهوية في أول 1.5 ثانية: ختم رواق + عنوان الشورت + ترقيمه."""
    img = _veil(214)
    img.alpha_composite(_frame()[0])
    d = ImageDraw.Draw(img)
    lock = G.brand_lockup(300, color=G.PARCH)
    img.alpha_composite(lock, ((W - lock.width) // 2, 470))

    y = 470 + lock.height + 44
    d.line([(W // 2 - 200, y), (W // 2 + 200, y)], fill=G.GOLD_L + (230,), width=2)

    y += 70
    f_hook = G.fit_font(G.AMIRI_B, s["hook"], W - 220, 94, 52)
    G.draw_ar(d, (W // 2, y), s["hook"], f_hook, G.PARCH, anchor="ma",
              stroke=3, stroke_fill=(12, 11, 9))
    y += int(f_hook.size * 1.55)

    G.draw_ar(d, (W // 2, y), s["kicker"], G.font(G.PLEX_M, 42), G.GOLD_L, anchor="ma")
    y += 104
    G.draw_ar(d, (W // 2, y), f"شورت {s['order']} من {D.TOTAL}",
              G.font(G.PLEX_B, 38), (208, 197, 175), anchor="ma")
    y += 78
    G.draw_ar(d, (W // 2, y), D.SERIES, G.font(G.PLEX_R, 32), (150, 141, 120), anchor="ma")
    return img


def endcard_vertical(s: dict) -> Image.Image:
    """بطاقة ختام 3.2 ثانية: هوية + ترقيم + الحلقة الكاملة + دعوة المتابعة."""
    img = Image.new("RGB", (W, H), (9, 8, 7))
    d = ImageDraw.Draw(img)
    for y in range(H):
        k = 1 - (y / H) * 0.45
        d.line([(0, y), (W, y)], fill=(int(30 * k) + 9, int(27 * k) + 8, int(22 * k) + 7))
    fr = _frame()[0]
    img.paste(fr.convert("RGB"), (0, 0), fr)

    lock = G.brand_lockup(300, color=G.PARCH)
    img.paste(lock, ((W - lock.width) // 2, 300), lock)

    y = 300 + lock.height + 40
    d.line([(W // 2 - 210, y), (W // 2 + 210, y)], fill=G.GOLD, width=2)
    y += 56
    G.draw_ar(d, (W // 2, y), D.SERIES, G.font(G.PLEX_M, 34), (186, 175, 150), anchor="ma")

    y += 108
    G.draw_ar(d, (W // 2, y), f"شورت {s['order']} من {D.TOTAL}", G.font(G.AMIRI_B, 58),
              G.GOLD_L, anchor="ma")

    y += 128
    if s.get("ep"):
        G.draw_ar(d, (W // 2, y), "الحلقة الكاملة", G.font(G.PLEX_R, 34), (150, 141, 120), anchor="ma")
        y += 62
        f_ep = G.fit_font(G.AMIRI_B, D.EP_TITLE[s["ep"]], W - 200, 62, 44)
        G.draw_ar(d, (W // 2, y), D.EP_TITLE[s["ep"]], f_ep, G.PARCH, anchor="ma",
                  stroke=2, stroke_fill=(12, 11, 9))
        y += int(f_ep.size * 1.5)
        G.draw_ar(d, (W // 2, y), f"الحلقة {D.EP_ORDER[s['ep']]} من 3 في السلسلة",
                  G.font(G.PLEX_M, 32), G.GOLD_L, anchor="ma")
    else:
        G.draw_ar(d, (W // 2, y), "السلسلة كاملة في القناة", G.font(G.AMIRI_B, 58), G.PARCH, anchor="ma")

    box = [W // 2 - 330, 1580, W // 2 + 330, 1680]
    d.rounded_rectangle(box, radius=50, outline=G.GOLD_L, width=2, fill=(58, 48, 30))
    G.draw_ar(d, (W // 2, (box[1] + box[3]) // 2), "تابع رواق… سلسلة كاملة",
              G.font(G.PLEX_B, 40), G.PARCH, anchor="mm")
    G.draw_ar(d, (W // 2, 1730), D.CHANNEL, G.font(G.PLEX_M, 32), (150, 141, 120), anchor="ma")
    G.draw_ar(d, (W // 2, 1774), "رِواق | تاريخ وتراث", G.font(G.PLEX_R, 28), (143, 133, 112),
              anchor="ma")
    return img


# ------------------------------------------------------------------ assets
def build_assets(s: dict) -> dict:
    key = s["key"]
    a = sdir(key)
    d = f"{OUT}/{key}"
    os.makedirs(d, exist_ok=True)
    dur = probe_dur(D.src(s))

    caption_card().save(f"{a}/card.png")
    ident_vertical(s).save(f"{a}/ident.png")
    endcard_vertical(s).save(f"{a}/endcard.png")
    G.watermark_bug(78).save(f"{a}/bug.png")

    rows = SC.load(key)
    SC.write_srts(rows, d)
    SC.build_ass(rows, f"{a}/captions.ass")
    json.dump(rows, open(f"{a}/rows.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    if not os.path.exists(f"{ASSETS}/MUSIC_BED_series.wav"):
        import music as M
        os.makedirs(ASSETS, exist_ok=True)
        M.write_wav(f"{ASSETS}/MUSIC_INTRO_riwaq.wav", M.intro())
        M.write_wav(f"{ASSETS}/MUSIC_OUTRO_riwaq.wav", M.outro())
        M.write_wav(f"{ASSETS}/MUSIC_BED_series.wav", M.bed(120.0, dbfs=-18.0))

    meta = {"key": key, "order": s["order"], "dur": dur, "total": dur + ENDPAD,
            "rows": len(rows)}
    json.dump(meta, open(f"{a}/assets.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[{key}] assets OK — {dur:.2f}s → {dur + ENDPAD:.2f}s، {len(rows)} كابشن")
    return meta


def wm_enable(dur: float) -> str:
    parts, t = [], 16.0
    while t < dur - 1.5:
        parts.append(f"between(t,{t:.2f},{t + WM_LEN:.2f})")
        t += WM_PERIOD
    return "+".join(parts) if parts else "0"


def vfilter(s: dict, dur: float) -> str:
    a = sdir(s["key"])
    total = dur + ENDPAD
    f = [
        f"[0:v]trim=0:{dur:.3f},setpts=PTS-STARTPTS,fps=25[base]",
        "[1:v]format=rgba,fade=t=in:st=0:d=0.30:alpha=1,"
        f"fade=t=out:st={IDENT_END - 0.40:.2f}:d=0.40:alpha=1[idn]",
        f"[base][idn]overlay=0:0:enable='between(t,0,{IDENT_END:.2f})'[b0]",
        "[4:v]format=rgba[card]",
        f"[b0][card]overlay=0:0:enable='between(t,0,{dur:.3f})'[b1]",
        f"[b1]ass={a}/captions.ass:fontsdir={REPO}/public/fonts[b2]",
        "[2:v]format=rgba[bug]",
        f"[b2][bug]overlay={(W - 171) // 2}:1652:enable='{wm_enable(dur)}'[b3]",
        "[3:v]format=rgba[ec]",
        f"[b3][ec]overlay=0:0:enable='gte(t,{dur:.3f})'[b4]",
        f"[b4]fade=t=in:st=0:d=0.25,fade=t=out:st={total - 0.45:.2f}:d=0.45,"
        "format=yuv420p,setsar=1[vout]",
    ]
    return ";".join(f)


def afilter(dur: float) -> str:
    total = dur + ENDPAD
    f = [
        f"[0:a]atrim=0:{dur:.3f},asetpts=N/SR/TB,aresample=48000,asplit=2[voice][sc]",
        f"[5:a]atrim=0:{dur:.3f},asetpts=N/SR/TB,volume=0.55,aresample=48000[bedraw]",
        "[bedraw][sc]sidechaincompress=threshold=0.03:ratio=9:attack=25:release=420:"
        "makeup=1:level_sc=1[bed]",
        "[6:a]atrim=0:4.4,asetpts=N/SR/TB,volume=0.34,aresample=48000[in]",
        f"[7:a]atrim=0:{ENDPAD + 0.8:.2f},asetpts=N/SR/TB,volume=0.60,"
        f"adelay={int((dur - 0.5) * 1000)}|{int((dur - 0.5) * 1000)},aresample=48000[out]",
        "[voice][bed][in][out]amix=inputs=4:duration=longest:normalize=0[premix]",
        f"[premix]apad=pad_dur={ENDPAD:.2f},atrim=0:{total:.3f},"
        "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,"
        "alimiter=limit=0.89:level=disabled[aout]",
    ]
    return ";".join(f)


def render(s: dict, crf: int = 18, preset: str = "medium") -> str:
    key = s["key"]
    a = sdir(key)
    meta = build_assets(s) if not os.path.exists(f"{a}/assets.json") else json.load(
        open(f"{a}/assets.json", encoding="utf-8"))
    dur = meta["dur"]
    total = dur + ENDPAD
    out = f"{OUT}/{key}/MASTER_FINAL_{key}.mp4"
    cmd = [FF, "-y", "-hide_banner", "-nostdin",
           "-i", D.src(s),
           "-loop", "1", "-i", f"{a}/ident.png",
           "-loop", "1", "-i", f"{a}/bug.png",
           "-loop", "1", "-i", f"{a}/endcard.png",
           "-loop", "1", "-i", f"{a}/card.png",
           "-stream_loop", "-1", "-i", f"{ASSETS}/MUSIC_BED_series.wav",
           "-i", f"{ASSETS}/MUSIC_INTRO_riwaq.wav",
           "-i", f"{ASSETS}/MUSIC_OUTRO_riwaq.wav",
           "-filter_complex", vfilter(s, dur) + ";" + afilter(dur),
           "-map", "[vout]", "-map", "[aout]",
           "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
           "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p", "-r", "25",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-color_range", "tv",
           "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
           "-movflags", "+faststart", "-t", f"{total:.3f}", out]
    sh(cmd)
    print(f"[{key}] master OK — {os.path.getsize(out) / 1e6:.1f} MB / {total:.2f}s")
    return out


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "assets"
    if mode == "assets":
        for s in D.SHORTS:
            build_assets(s)
    elif mode == "render":
        render(D.by_key(sys.argv[2]))
    elif mode == "all":
        for s in D.SHORTS:
            build_assets(s)
            render(s)
