"""أغلفة v2 — صورة كاملة (full-bleed) بلا أي طبقة تعتيم أو تدرّج لوني.

كل النصوص والشعار فوق الصورة مباشرة، وتُقرأ عبر ظل ديناميكي متعدّد الطبقات
(ظل واسع ناعم + ظل قريب حاد + هالة ذهبية خفيفة)، فلا يوجد أي مستطيل أو شريط غامق.

الاستخدام:
    python3 scripts/series/covers_v2.py            # كل الحلقات 01–06
    python3 scripts/series/covers_v2.py 03         # حلقة واحدة
"""
from __future__ import annotations

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

import numpy as np  # noqa: E402
import graphics as G  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

REPO = "/home/user/Riwaq_System_Repo"
DRIVE = f"{REPO}/google_drive"
OUT = f"{REPO}/outputs/SERIES_RIWAQ/covers_v2"
FF = os.environ.get(
    "FFMPEG", "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2")

SHADOW = (6, 6, 5)


# ----------------------------------------------------------------------------- لقطات
def grab(master: str, t: float, out: str) -> Image.Image:
    """لقطة من داخل إطار الفيديو فقط (بدون شريط الكابشن أو ترويسة القالب)."""
    subprocess.run([FF, "-v", "error", "-copyts", "-ss", str(t), "-i", master,
                    "-frames:v", "1", "-vf", "crop=1440:808:240:108",
                    "-y", out], check=True)
    return Image.open(out).convert("RGB")


# ----------------------------------------------------------------------------- ظلال
def _blur_mask(mask: Image.Image, radius: float, alpha: float) -> Image.Image:
    m = mask.filter(ImageFilter.GaussianBlur(radius))
    if alpha < 1.0:
        m = m.point(lambda v: int(v * alpha))
    return m


def add_shadowed(canvas: Image.Image, layer: Image.Image,
                 wide=(26, 0.86, (10, 14)), tight=(7, 0.80, (3, 5)),
                 glow: tuple | None = None, core=(12, 0.62, (0, 2)),
                 extra: list | None = None) -> None:
    """يركّب طبقة RGBA بظل ديناميكي متعدّد الطبقات (بلا أي صندوق أو تعبئة)."""
    a = layer.split()[3]
    pad = 96
    W, H = canvas.size

    def place(mask_img: Image.Image, color, offset):
        sh = Image.new("L", (W + 2 * pad, H + 2 * pad), 0)
        sh.paste(mask_img, (pad + offset[0], pad + offset[1]))
        rgba = Image.new("RGBA", sh.size, color + (0,))
        rgba.putalpha(sh)
        canvas.alpha_composite(rgba.crop((pad, pad, pad + W, pad + H)))

    # طبقات إضافية واسعة جدًا = ظل محيط ناعم يفصل النص عن أي خلفية فاتحة
    for radius, alpha, off in (extra or []):
        place(_blur_mask(a, radius, alpha), SHADOW, off)
    if glow:
        g_radius, g_alpha, g_color = glow
        place(_blur_mask(a, g_radius, g_alpha), g_color, (0, 0))
    place(_blur_mask(a, wide[0], wide[1]), SHADOW, wide[2])
    if core:
        place(_blur_mask(a, core[0], core[1]), SHADOW, core[2])
    place(_blur_mask(a, tight[0], tight[1]), SHADOW, tight[2])
    canvas.alpha_composite(layer, (0, 0))


def draw_ar_stroke(d, xy, s, fnt, fill, stroke=3, stroke_fill=(8, 7, 6, 225), anchor="la"):
    """نص عربي بحدّ داكن رقيق + خطوة ظل — يقرأ فوق أي خلفية بلا أي صندوق."""
    d.text(xy, G.ar(s), font=fnt, fill=stroke_fill, anchor=anchor,
           stroke_width=stroke, stroke_fill=stroke_fill)
    d.text(xy, G.ar(s), font=fnt, fill=fill, anchor=anchor)


def text_layer(size: tuple[int, int], painter) -> Image.Image:
    """يرسم نصًّا بدقة مضاعفة ثم يصغّره — حواف عربية ناعمة."""
    ss = 2
    big = Image.new("RGBA", (size[0] * ss, size[1] * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    painter(d, ss)
    return big.resize(size, Image.LANCZOS)


# ----------------------------------------------------------------------------- إطار الصورة
def fill_frame(frame: Image.Image, W: int, H: int, focus: float = 0.5) -> Image.Image:
    """يملأ الكادر كاملًا من نفس اللقطة (قصّ ذكي، بلا أي تعتيم)."""
    scale = max(W / frame.width, H / frame.height)
    f = frame.resize((int(frame.width * scale + 0.5), int(frame.height * scale + 0.5)),
                     Image.LANCZOS)
    left = int((f.width - W) * focus)
    top = int((f.height - H) * 0.5)
    return f.crop((left, top, left + W, top + H))


def _vignette(img: Image.Image, strength: float = 0.16) -> Image.Image:
    """توهين خفيف جدًا لأطراف الكادر فقط — لا يمسّ لون منتصف الصورة."""
    W, H = img.size
    y, x = np.mgrid[0:H, 0:W]
    cx, cy = W / 2, H / 2
    r = np.sqrt(((x - cx) / (W * 0.62)) ** 2 + ((y - cy) / (H * 0.62)) ** 2)
    v = np.clip((r - 0.55) / 0.75, 0, 1) ** 1.6 * strength
    arr = np.asarray(img).astype(np.float32) * (1 - v[..., None])
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


# ----------------------------------------------------------------------------- الغلاف الأفقي
SAFE_BOTTOM = 552      # آخر سطر في الكتلة النصية — فوق سطح الطاولة/الكوب
SAFE_TOP = 206


def cover_h(frame: Image.Image, lines: list[str], kicker: str, out: str,
            name: str = "ياسر الحزيمي", badge: str | None = None,
            focus: float = 0.5, max_w: int = 600) -> str:
    W, H = 1280, 720
    base = _vignette(fill_frame(frame, W, H, focus)).convert("RGBA")

    # ------- الشعار (ظل واسع + ظل قريب + هالة ذهبية خفيفة)
    lock = G.brand_lockup(112, color=G.PARCH)
    logo_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    logo_layer.alpha_composite(lock, (56, 34))
    add_shadowed(base, logo_layer,
                 wide=(18, 0.92, (8, 12)), tight=(5, 0.88, (2, 4)),
                 glow=(16, 0.18, G.GOLD_L))

    # ------- قياس الكتلة النصية: كيكر + عنوان + سطر توقيع واحد (اسم + شارة)
    kick_px, name_px, badge_px, badge_h, row_h = 30, 30, 26, 44, 46
    fixed = 54 + 26 + row_h                      # فاصل الكيكر + فاصل التوقيع + سطر التوقيع
    avail = SAFE_BOTTOM - SAFE_TOP - fixed
    fitted, total, px = [], 0, 92
    while px > 44:
        fitted, total = [], 0
        for line in lines:
            fnt = G.fit_font(G.AMIRI_B, line, max_w, px, 44)
            fitted.append((line, fnt))
            total += int(fnt.size * 1.28)
        if total <= avail:
            break
        px -= 2
    block_h = fixed + total
    y_kick = SAFE_BOTTOM - block_h
    y_title = y_kick + 54
    y_row = y_title + total + 24
    x0 = 66

    def painter(d: ImageDraw.ImageDraw, ss: int) -> None:
        draw_ar_stroke(d, (x0 * ss, y_kick * ss), kicker, G.font(G.PLEX_B, kick_px * ss),
                       G.GOLD_L + (255,), stroke=1 * ss)
        y = y_title
        for line, fnt in fitted:
            draw_ar_stroke(d, (x0 * ss, y * ss), line, G.font(G.AMIRI_B, fnt.size * ss),
                           G.PARCH + (255,), stroke=2 * ss)
            y += int(fnt.size * 1.28)
        # سطر واحد: فاصل ذهبي + الاسم + الشارة
        cy = y_row + row_h / 2
        fn = G.font(G.PLEX_M, name_px * ss)
        nm_w = G.text_w(fn, G.ar(name)) / ss
        draw_ar_stroke(d, (x0 * ss, (cy + 3) * ss), name, fn,
                       (232, 222, 202, 255), stroke=1 * ss, anchor="ls")
        if badge:
            fb = G.font(G.PLEX_B, badge_px * ss)
            bx = x0 + nm_w + 26
            bw = G.text_w(fb, G.ar(badge)) / ss + 34
            d.rounded_rectangle([bx * ss, (cy - badge_h / 2) * ss,
                                 (bx + bw) * ss, (cy + badge_h / 2) * ss],
                                radius=22 * ss, fill=(16, 14, 10, 196),
                                outline=G.GOLD_L + (232,), width=max(2, 2 * ss))
            G.draw_ar(d, ((bx + 17) * ss, cy * ss), badge, fb,
                      G.PARCH + (255,), anchor="lm")

    add_shadowed(base, text_layer((W, H), painter),
                 wide=(26, 1.0, (8, 11)), tight=(5, 1.0, (2, 3)),
                 glow=(11, 0.10, G.GOLD), core=(16, 0.85, (0, 3)),
                 extra=[(56, 0.40, (0, 6)), (34, 0.52, (0, 4))])

    # ------- إطار ذهبي مزدوج رقيق (خطوط فقط، بلا أي تعبئة)
    d = ImageDraw.Draw(base)
    d.rectangle([16, 16, W - 17, H - 17], outline=G.GOLD_L + (225,), width=2)
    d.rectangle([24, 24, W - 25, H - 25], outline=(122, 100, 55, 95), width=1)

    base.convert("RGB").save(out, quality=93, subsampling=1)
    return out


# ----------------------------------------------------------------------------- الغلاف العمودي
def cover_v(frame: Image.Image, lines: list[str], kicker: str, out: str,
            name: str = "ياسر الحزيمي", focus: float = 0.62) -> str:
    W, H = 1080, 1920
    base = _vignette(_fill_v(frame, W, H, focus), 0.20).convert("RGBA")

    lock = G.brand_lockup(146, color=G.PARCH)
    logo_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    logo_layer.alpha_composite(lock, (66, 72))
    add_shadowed(base, logo_layer,
                 wide=(22, 0.92, (8, 12)), tight=(6, 0.88, (2, 4)),
                 glow=(18, 0.18, G.GOLD_L))

    fitted, total = [], 0
    for line in lines:
        fnt = G.fit_font(G.AMIRI_B, line, W - 150, 124, 66)
        fitted.append((line, fnt))
        total += int(fnt.size * 1.26)
    # الكتلة النصية أسفل الكادر — تحت الوجه دائمًا، وفوق منطقة آمنة من واجهة الشورت
    y_kick = H - 436 - total
    y_title = y_kick + 78
    y_sig = y_title + total + 22

    def painter(d: ImageDraw.ImageDraw, ss: int) -> None:
        draw_ar_stroke(d, (66 * ss, y_kick * ss), kicker, G.font(G.PLEX_B, 42 * ss),
                       G.GOLD_L + (255,), stroke=2 * ss)
        y = y_title
        for line, fnt in fitted:
            draw_ar_stroke(d, (66 * ss, y * ss), line, G.font(G.AMIRI_B, fnt.size * ss),
                           G.PARCH + (255,), stroke=3 * ss)
            y += int(fnt.size * 1.26)
        d.line([(66 * ss, (y_sig - 16) * ss), ((66 + 110) * ss, (y_sig - 16) * ss)],
               fill=G.GOLD_L + (225,), width=3 * ss)
        draw_ar_stroke(d, (66 * ss, y_sig * ss), name, G.font(G.PLEX_M, 40 * ss),
                       (228, 218, 198, 255), stroke=2 * ss)

    add_shadowed(base, text_layer((W, H), painter),
                 wide=(34, 1.0, (9, 13)), tight=(6, 1.0, (2, 3)),
                 glow=(16, 0.10, G.GOLD), core=(20, 0.95, (0, 4)),
                 extra=[(72, 0.42, (0, 8)), (48, 0.55, (0, 6))])

    d = ImageDraw.Draw(base)
    d.rectangle([20, 20, W - 21, H - 21], outline=G.GOLD_L + (225,), width=3)
    base.convert("RGB").save(out, quality=93, subsampling=1)
    return out


def _best_band_y(base: Image.Image, band_h: int, lo=0.34, hi=0.90,
                 left=60, right=760) -> int:
    """يختار أنسب شريط عمودي للنص: أقل سطوعًا وأقل ازدحامًا (بحث آلي داخل الكادر)."""
    import numpy as np
    g = np.asarray(base.convert("L").crop((left, 0, right, base.height))).astype(np.float32)
    H = g.shape[0]
    rows = g.mean(axis=1)
    detail = np.abs(np.diff(g, axis=1)).mean(axis=1)      # مقدار التفاصيل/الازدحام
    score = rows + detail * 1.6
    k = np.ones(band_h) / band_h
    smooth = np.convolve(score, k, mode="valid")
    i0, i1 = int(H * lo), min(int(H * hi), H - band_h)
    if i1 <= i0:
        return int(H * lo)
    best = i0 + int(np.argmin(smooth[i0:i1]))
    return best


def _fill_v(frame: Image.Image, W: int, H: int, focus: float) -> Image.Image:
    """ملء عمودي كامل من نفس اللقطة — بلا أي شريط أو لون مضاف.

    focus = موضع الشخص أفقيًا داخل الغلاف (0.30 يسارًا… 0.70 يمينًا).
    """
    scale = H / frame.height
    f = frame.resize((int(frame.width * scale + 0.5), H), Image.LANCZOS)
    face_x = f.width * 0.50
    left = int(face_x - focus * W)
    left = max(0, min(left, f.width - W))
    return f.crop((left, 0, left + W, H))
