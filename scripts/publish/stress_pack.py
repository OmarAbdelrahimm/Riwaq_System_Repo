"""أغلفة حزمة «الضغط النفسي» — A/B أفقي 1280×720 + عمودي 1080×1920.

نفس نظام العلامة المستخدم في حزم أبو سمبل والذكاء الاصطناعي (ظلّ نص متعدّد الطبقات،
إطار ذهبي، علامة رواق أعلى اليسار، والزاوية اليمنى السفلى خالية لشارة المدة)،
لكن بتدرّج دافئ يناسب الرسوم الليلية/الصباحية.

    python3 scripts/publish/stress_pack.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "series"))

import graphics as G  # noqa: E402
from PIL import Image, ImageDraw, ImageEnhance  # noqa: E402

import abu_simbel_pack as P  # noqa: E402

REPO = "/home/user/Riwaq_System_Repo"
OUT = f"{REPO}/outputs/PUBLISH_PACK_STRESS"
ART = f"{OUT}/art"

BG_A = f"{ART}/bg_A.png"   # مكتب ليلاً + نوافذ مفتوحة في الدماغ (مولَّدة)
BG_B = f"{ART}/bg_B.png"   # شروق + نَفَس عميق عند النافذة (مولَّدة)

INK, PARCH, GOLD, GOLD_L = G.INK, G.PARCH, G.GOLD, G.GOLD_L

draw, rtl = P.draw, P.rtl
fit_font, side_shade = P.fit_font, P.side_shade
shadowed, gold_frame, lockup, fit_lines = P.shadowed, P.gold_frame, P.lockup, P.fit_lines

WARM = (58, 40, 22)


def cover(path: str, W: int, H: int, fx=0.5, fy=0.5, zoom=1.0) -> Image.Image:
    """قصّ يغطّي الإطار مع تكبير اختياري (لتشديد الكادر على الوجه وإبعاد التفاصيل)."""
    im = Image.open(path).convert("RGB")
    if zoom != 1.0:
        w, h = int(im.width / zoom), int(im.height / zoom)
        x = int((im.width - w) * fx)
        y = int((im.height - h) * fy)
        im = im.crop((x, y, x + w, y + h))
    scale = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * scale + 0.5), int(im.height * scale + 0.5)), Image.LANCZOS)
    x = int((im.width - W) * fx)
    y = int((im.height - H) * fy)
    return im.crop((x, y, x + W, y + H))


def corner_shade(im: Image.Image, corner="tl", strength=150, radius=0.62) -> Image.Image:
    """تعتيم ناعم في زاوية واحدة (سقوط عدسة طبيعي) — يُقرأ الشعار فوق سماء/نافذة فاتحة."""
    W, H = im.size
    sw, sh = 40, 23
    small = Image.new("L", (sw, sh), 0)
    px = small.load()
    cx = 0.0 if corner in ("tl", "bl") else sw
    cy = 0.0 if corner in ("tl", "tr") else sh
    for y in range(sh):
        for x in range(sw):
            d = (((x - cx) / (radius * sw)) ** 2 + ((y - cy) / (radius * sh)) ** 2) ** 0.5
            px[x, y] = int(min(1.0, max(0.0, 1 - d)) ** 1.4 * strength)
    mask = small.resize((W, H), Image.BICUBIC)
    return Image.composite(Image.new("RGB", (W, H), (10, 8, 6)), im, mask)


def warm_grade(im: Image.Image) -> Image.Image:
    """دفء خفيف + تباين: يبرز الإضاءة الدافئة ويُعمّق الظلال بلا تغيير الهوية اللونية."""
    im = ImageEnhance.Brightness(im).enhance(1.04)
    im = ImageEnhance.Contrast(im).enhance(1.12)
    im = ImageEnhance.Color(im).enhance(1.06)
    lum = im.convert("L")
    mask = lum.point(lambda v: int((1 - v / 255) ** 1.8 * 150))
    return Image.composite(Image.new("RGB", im.size, WARM), im, mask)


def horizontal(src, out, kicker, title, sub, gold_word=None, fx=0.5, fy=0.5,
               zoom=1.0, title_px=104, x_right=1198, y_bottom=560, max_w=520,
               strength=210, width=0.50, corner=None) -> str:
    W, H = 1280, 720
    base = cover(src, W, H, fx, fy, zoom)
    base = warm_grade(base)
    base = P.vignette(base, 0.28)
    base = side_shade(base, "right", strength=strength, width=width, soft=0.55)
    if corner:
        base = corner_shade(base, corner, strength=150, radius=0.55)

    fonts = fit_lines(title, max_w, title_px, 50)
    line_h = [int(f.size * 1.28) for f in fonts]
    y_title = y_bottom - sum(line_h)

    def painter(d):
        draw(d, (x_right, y_title - 48), kicker, G.font(G.PLEX_B, 30), GOLD_L + (255,))
        y = y_title
        for text, f, lh in zip(title, fonts, line_h):
            fill = (GOLD_L if gold_word and gold_word in text else PARCH) + (255,)
            draw(d, (x_right, y), text, f, fill)
            y += lh
        fs = fit_font(G.PLEX_M, sub, max_w + 60, 28, 19)
        draw(d, (x_right, y_bottom + 26), sub, fs, (240, 226, 204, 255))

    shadowed(base, painter, blur=10, offsets=((0, 5), (0, 12), (0, 22)), alpha=236)
    lockup(base, 92, (40, 24))
    gold_frame(base, W, H)

    base.save(out.replace(".jpg", ".png"))
    base.save(out, quality=92, subsampling=1)
    print("cover", out)
    return out


def vertical(src, out, kicker, title, sub, fx=0.5, fy=0.2, band_h=1120,
             zoom=1.0) -> str:
    """1080×1920: صورة أعلى + كتلة نص أسفلها، وآخر 240px خالية."""
    W, H = 1080, 1920
    base = Image.new("RGB", (W, H), INK)
    band = cover(src, W, band_h, fx, fy, zoom)
    band = warm_grade(band)
    band = side_shade(band, "bottom", strength=165, width=0.28, soft=0.8)
    band = corner_shade(band, "tl", strength=185, radius=0.42)
    base.paste(band, (0, 0))

    fade = Image.new("L", (1, band_h), 0)
    for i in range(band_h):
        t = i / (band_h - 1)
        fade.putpixel((0, i), 0 if t < 0.82 else int(((t - 0.82) / 0.18) ** 1.3 * 255))
    base.paste(Image.new("RGB", (W, band_h), INK), (0, 0), fade.resize((W, band_h)))

    sub_f = fit_font(G.PLEX_M, sub, W - 180, 36, 24)
    gap = 48
    start = 146
    while start > 70:
        fonts = fit_lines(title, W - 170, start, 70)
        heights = [int(f.size * 1.32) for f in fonts]
        block = 62 + sum(heights) + gap + 46
        if band_h + 84 + block <= H - 240:
            break
        start -= 6
    y = band_h + 84 + max(0, ((H - 250) - (band_h + 84) - block) // 2)

    def painter(d):
        draw(d, (W - 70, y - 62), kicker, G.font(G.PLEX_B, 40), GOLD_L + (255,))
        yy = y
        for i, (text, f, lh) in enumerate(zip(title, fonts, heights)):
            fill = (GOLD_L if i == len(title) - 1 else PARCH) + (255,)
            draw(d, (W - 70, yy), text, f, fill)
            yy += lh
        draw(d, (W - 70, yy + gap), sub, sub_f, (240, 226, 204, 255))

    shadowed(base, painter, blur=12, offsets=((0, 6), (0, 14)), alpha=205)
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

    # A — المشكلة: الدماغ مش بيقفل (صورة ليلية، أقرب لروح الفيديو)
    horizontal(BG_A, f"{OUT}/THUMB_A_STRESS_1280x720.jpg",
               "الضغط النفسي · مش ضعف",
               ["دماغك لسه", "فاتحة 30 تاب؟"],
               "إشارة إن جسمك طالب مساحة… مش عيب فيك",
               gold_word="فاتحة 30 تاب؟",
               fx=0.42, fy=0.42, zoom=1.18, title_px=104, y_bottom=512,
               strength=228, width=0.58, corner="tl")

    # B — الحل: خطوة واحدة صباحًا (تباين كامل في المزاج واللون)
    horizontal(BG_B, f"{OUT}/THUMB_B_STRESS_1280x720.jpg",
               "حل عملي · النهاردة",
               ["خطوة واحدة", "تكفي"],
               "من غير مهدّئات… ولا تغيير لحياتك كلها",
               gold_word="تكفي",
               fx=0.30, fy=0.46, zoom=1.12, title_px=120, y_bottom=520,
               strength=200, width=0.52, corner="tl")

    # عمودي للشورتس/الكوميونيتي
    vertical(BG_A, f"{OUT}/THUMB_SHORTS_STRESS_1080x1920.jpg",
             "الضغط النفسي",
             ["دماغك لسه", "فاتحة 30 تاب؟"],
             "خطوات عملية تبدأ بيها النهاردة", fx=0.40, fy=0.10, band_h=1120, zoom=1.10)
