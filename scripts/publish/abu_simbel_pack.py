"""أغلفة حزمة «أبو سمبل» — A/B أفقي 1280×720 + عمودي 1080×1920.

الصور من مصادر حرة (Public Domain / CC0) — انظر assets/LICENSES.md.
كل النصوص مطبوعة فوق الصورة بظلّ متعدّد الطبقات، والزاوية السفلية اليمنى خالية
كي لا تتعارض مع شارة المدة في يوتيوب.

    python3 scripts/publish/abu_simbel_pack.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "series"))

import graphics as G  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

REPO = "/home/user/Riwaq_System_Repo"
OUT = f"{REPO}/outputs/PUBLISH_PACK_ABU_SIMBEL"
ASSETS = f"{OUT}/assets"

FACADE = f"{ASSETS}/abu_simbel_facade_2007_PD.jpg"      # Public Domain
DUCAMP = f"{ASSETS}/abu_simbel_ducamp_1850_PD.jpg"      # Public Domain

INK = G.INK
PARCH = G.PARCH
GOLD = G.GOLD
GOLD_L = G.GOLD_L


# ------------------------------------------------------------------ أدوات
import re

_NUM = re.compile(r"[0-9\u0660-\u0669][0-9\u0660-\u0669\s,.\u2013\u2014:\/-]*[0-9\u0660-\u0669]")


def rtl(text: str) -> str:
    """يُغلّف كل رقم/تاريخ عربي داخل النص بعلامات LTR كي لا ينقلب ترتيبه."""
    return _NUM.sub(lambda m: "\u202a" + m.group(0) + "\u202c", text)


def draw(d, xy, text, fnt, fill, anchor="ra"):
    G.draw_ar(d, xy, rtl(text), fnt, fill, anchor=anchor)


def fit_font(path, text, max_w, start, floor=24):
    px = start
    while px > floor:
        f = G.font(path, px)
        if G.text_w(f, G.ar(rtl(text))) <= max_w:
            return f
        px -= 2
    return G.font(path, floor)


def cover_crop(path: str, W: int, H: int, fx: float = 0.5, fy: float = 0.5) -> Image.Image:
    im = Image.open(path).convert("RGB")
    if im.width < W:
        im = im.resize((int(im.width * W / im.width), int(im.height * W / im.width)), Image.LANCZOS)
    scale = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * scale + 0.5), int(im.height * scale + 0.5)), Image.LANCZOS)
    x = int((im.width - W) * fx)
    y = int((im.height - H) * fy)
    return im.crop((x, y, x + W, y + H))


def side_shade(im: Image.Image, side="right", strength=200, width=0.52,
               soft=0.62) -> Image.Image:
    """تعتيم متدرّج من حافة واحدة — يمنح النص أرضية قراءة بلا لوح ظاهر."""
    W, H = im.size
    horiz = side in ("right", "left")
    n = 96
    line = Image.new("L", (n, 1) if horiz else (1, n), 0)
    edge = 1.0 - width
    for i in range(n):
        t = i / (n - 1)
        k = t if side in ("right", "bottom") else 1 - t   # 1 = الجانب المظلم
        v = ((k - edge) / (1 - edge)) ** soft if k > edge else 0.0
        line.putpixel((i, 0) if horiz else (0, i), int(v * strength))
    mask = line.resize((W, H), Image.BICUBIC)
    return Image.composite(Image.new("RGB", (W, H), (12, 9, 7)), im, mask)


def soft_shade(size: tuple[int, int], centre=(0.0, 1.0), radius=1.0, strength=215) -> Image.Image:
    """تعتيم ناعم بلا حواف (ليس لوحًا) — يرفع قراءة النص فوق الحجر الفاتح."""
    W, H = size
    sw, sh = 48, 27
    small = Image.new("L", (sw, sh), 0)
    px = small.load()
    cx, cy = centre[0] * sw, centre[1] * sh
    for y in range(sh):
        for x in range(sw):
            d = (((x - cx) / (radius * sw)) ** 2 + ((y - cy) / (radius * sh * 1.6)) ** 2) ** 0.5
            v = max(0.0, 1.0 - d)
            px[x, y] = int((v ** 1.25) * strength)
    mask = small.resize((W, H), Image.BICUBIC)
    return Image.composite(Image.new("RGB", (W, H), (10, 8, 6)), Image.new("RGB", (W, H), (0, 0, 0)), mask)


def grade(im: Image.Image) -> Image.Image:
    """تصحيح لوني: رفع الظلال، مزيد من التباين، دفء حجري."""
    from PIL import ImageEnhance
    im = ImageEnhance.Brightness(im).enhance(1.12)
    im = ImageEnhance.Contrast(im).enhance(1.16)
    im = ImageEnhance.Color(im).enhance(1.12)
    return im


def vignette(im: Image.Image, strength: float = 0.55) -> Image.Image:
    W, H = im.size
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([-W * 0.25, -H * 0.35, W * 1.25, H * 1.35], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(W // 12))
    dark = Image.new("RGB", (W, H), (8, 7, 6))
    return Image.composite(im, Image.blend(im, dark, strength), mask)


def shadowed(base: Image.Image, painter, blur=9, offsets=((0, 5), (0, 11), (0, 20)), alpha=225):
    """يرسم طبقة نص ثم يضعها بظلّ ناعم متعدّد الطبقات."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    painter(ImageDraw.Draw(layer))
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", base.size, (0, 0, 0, alpha)), (0, 0), layer.split()[-1])
    for dx, dy in offsets:
        b = sh.filter(ImageFilter.GaussianBlur(blur))
        base.paste(Image.new("RGB", base.size, (0, 0, 0)), (dx, dy), b.split()[-1])
    base.paste(layer, (0, 0), layer)


def fit_lines(lines: list[str], max_w: int, start: int, floor: int):
    px = start
    while px > floor:
        fonts = [G.font(G.AMIRI_B, px) for _ in lines]
        if all(G.text_w(f, G.ar(rtl(t))) <= max_w for f, t in zip(fonts, lines)):
            return fonts
        px -= 2
    return [G.font(G.AMIRI_B, floor) for _ in lines]


def gold_frame(base: Image.Image, W: int, H: int, inset: int = 18) -> None:
    d = ImageDraw.Draw(base, "RGBA")
    d.rectangle([inset, inset, W - 1 - inset, H - 1 - inset], outline=GOLD_L + (215,), width=2)
    d.rectangle([inset + 7, inset + 7, W - 8 - inset, H - 8 - inset], outline=(GOLD[0], GOLD[1], GOLD[2], 90), width=1)


def lockup(base: Image.Image, width=94, xy=(40, 26)) -> None:
    lock = G.brand_lockup(width, color=PARCH)
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer.alpha_composite(lock, xy)
    shadowed(base, lambda d: d.bitmap((0, 0), layer.split()[-1], fill=(255, 255, 255, 255)),
             blur=12, offsets=((0, 4),), alpha=190)
    base.paste(layer, (0, 0), layer)


# ------------------------------------------------------------------ أفقي
def horizontal(src: str, out: str, kicker: str, title: list[str], sub: str,
               gold_word: str | None = None, fx=0.5, fy=0.5, shade_centre=(0.16, 0.86),
               vintage=False, title_px=104) -> str:
    W, H = 1280, 720
    base = cover_crop(src, W, H, fx, fy)
    if vintage:
        base = base.convert("L").convert("RGB")
        warm = Image.new("RGB", (W, H), (36, 26, 18))
        base = Image.blend(base, warm, 0.34)
    base = grade(base)
    base = Image.blend(base, vignette(base, 0.26), 0.4)
    base = side_shade(base, "right", strength=215, width=0.46, soft=0.55)

    x_right = W - 82
    y_title_bottom = 566

    fonts = fit_lines(title, 520, title_px, 56)
    line_h = [int(f.size * 1.31) for f in fonts]
    block_h = sum(line_h)
    y_title = y_title_bottom - block_h

    def painter(d):
        # سطر تمهيدي
        fk = G.font(G.PLEX_B, 30)
        draw(d, (x_right, y_title - 46), kicker, fk, GOLD_L + (255,))
        # العنوان
        y = y_title
        for text, f, lh in zip(title, fonts, line_h):
            fill = (GOLD_L if gold_word and gold_word in text else PARCH) + (255,)
            draw(d, (x_right, y), text, f, fill)
            y += lh
        # سطر سفلي
        fs = fit_font(G.PLEX_M, sub, 560, 29, 21)
        draw(d, (x_right, y_title_bottom + 28), sub, fs, (226, 215, 193, 255))

    shadowed(base, painter, blur=10, offsets=((0, 5), (0, 12), (0, 22)), alpha=232)
    lockup(base, 92, (40, 24))
    gold_frame(base, W, H)

    base.save(out.replace(".jpg", ".png"))
    base.save(out, quality=92, subsampling=1)
    print("cover", out)
    return out


# ------------------------------------------------------------------ عمودي
def vertical(src: str, out: str, kicker: str, title: list[str], sub: str,
             fx=0.5, fy=0.30, band_h=1150) -> str:
    """عمودي 1080×1920: صورة كبيرة أعلى + كتلة نص في الأسفل، وآخر 240px خالية."""
    W, H = 1080, 1920
    base = Image.new("RGB", (W, H), G.INK)
    band = cover_crop(src, W, band_h, fx, fy)
    band = grade(band)
    band = side_shade(band, "bottom", strength=150, width=0.3, soft=0.8)
    base.paste(band, (0, 0))

    # انتقال ناعم من الصورة إلى الحبر
    fade = Image.new("L", (1, band_h), 0)
    for i in range(band_h):
        t = i / (band_h - 1)
        v = 0 if t < 0.82 else int(((t - 0.82) / 0.18) ** 1.3 * 255)
        fade.putpixel((0, i), v)
    base.paste(Image.new("RGB", (W, band_h), G.INK), (0, 0), fade.resize((W, band_h)))

    fonts = fit_lines(title, W - 160, 152, 88)
    heights = [int(f.size * 1.32) for f in fonts]
    total = sum(heights)
    span_top, span_bottom = band_h + 70, H - 250
    y = span_top + max(20, ((span_bottom - span_top) - (total + 210)) // 2) + 120

    def painter(d):
        draw(d, (W - 70, y - 58), kicker, G.font(G.PLEX_B, 42), G.GOLD_L + (255,))
        yy = y
        for text, f, lh in zip(title, fonts, heights):
            draw(d, (W - 70, yy), text, f, PARCH + (255,))
            yy += lh
        fs = fit_font(G.PLEX_M, sub, W - 170, 38, 26)
        draw(d, (W - 70, yy + 34), sub, fs, (228, 217, 195, 255))

    shadowed(base, painter, blur=12, offsets=((0, 6), (0, 14)), alpha=200)

    d = ImageDraw.Draw(base, "RGBA")
    d.line([(70, band_h - 46), (W - 70, band_h - 46)], fill=GOLD_L + (110,), width=2)
    lockup(base, 116, (44, 48))
    d.rectangle([18, 18, W - 19, H - 19], outline=GOLD_L + (200,), width=2)

    base.save(out.replace(".jpg", ".png"))
    base.save(out, quality=92, subsampling=1)
    print("cover", out)
    return out


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    # A — الرقم الذي يجاوب على سؤال العنوان: 65 مترًا (صورة أرشيفية 1850)
    horizontal(DUCAMP, f"{OUT}/THUMB_A_ABU_SIMBEL_1280x720.jpg",
               "حملة اليونسكو · 1964 – 1968",
               ["رفعوه", "65 مترًا"],
               "معبد كامل… نقله العمال حجرًا حجرًا",
               gold_word="65 مترًا", fx=0.26, fy=0.62, vintage=True, title_px=112)
    # B — الصدمة: أنقذوه قبل أن يبتلعه الماء (لقطة ملوّنة للواجهة)
    horizontal(FACADE, f"{OUT}/THUMB_B_ABU_SIMBEL_1280x720.jpg",
               "أعظم إنقاذ أثري في التاريخ",
               ["أنقذوه", "قبل الغرق"],
               "1,036 قطعة أعادوا تركيبها كما كانت",
               gold_word="قبل الغرق", fx=0.34, fy=0.55)
    # عمودي للشورتس/الكوميونيتي
    vertical(FACADE, f"{OUT}/THUMB_SHORTS_ABU_SIMBEL_1080x1920.jpg",
             "قصة إنقاذ أبو سمبل",
             ["أنقذوه", "قبل الغرق"],
             "1,036 قطعة… أُعيد تركيبها", fx=0.30, fy=0.10, band_h=1150)
