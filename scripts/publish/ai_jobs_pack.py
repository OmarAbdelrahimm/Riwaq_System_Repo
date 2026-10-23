"""أغلفة حزمة «الذكاء الاصطناعي والوظائف» — A/B أفقي 1280×720 + عمودي 1080×1920.

يعيد استخدام أدوات abu_simbel_pack (قصّ، تعتيم متدرّج، ظلّ نص متعدّد الطبقات،
إطار ذهبي، علامة رواق) ويضيف تدرّجًا باردًا يناسب موضوع الذكاء الاصطناعي.

    /tmp/venv/bin/python scripts/publish/ai_jobs_pack.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "series"))

import graphics as G  # noqa: E402
from PIL import Image, ImageDraw, ImageEnhance  # noqa: E402

import abu_simbel_pack as P  # noqa: E402  (نفس أدوات العلامة)

REPO = "/home/user/Riwaq_System_Repo"
OUT = f"{REPO}/outputs/PUBLISH_PACK_AI_JOBS"
ART = f"{OUT}/art"

BG_A = f"{ART}/bg_A.png"   # موظف ليلًا + ظلّ إنسان آلي خلفه (مولَّدة)
BG_B = f"{ART}/bg_B.png"   # يد بشرية تلمس يدًا آلية (مولَّدة)

INK, PARCH, GOLD, GOLD_L = G.INK, G.PARCH, G.GOLD, G.GOLD_L

draw = P.draw
rtl = P.rtl
fit_font = P.fit_font
cover_crop = P.cover_crop
side_shade = P.side_shade
shadowed = P.shadowed
gold_frame = P.gold_frame
lockup = P.lockup
fit_lines = P.fit_lines

# أزرق بارد في الظلال يخدم موضوع الذكاء الاصطناعي بلا كسر هوية العلامة
COOL = (26, 44, 62)


def cool_grade(im: Image.Image, strength: float = 0.30) -> Image.Image:
    """تدرّج بارد: يبرّد الظلال فقط ويترك الإضاءة الدافئة على الوجه/اليد."""
    im = ImageEnhance.Brightness(im).enhance(1.06)
    im = ImageEnhance.Contrast(im).enhance(1.14)
    im = ImageEnhance.Color(im).enhance(1.10)
    lum = im.convert("L")
    # قناع للظلال: أقوى عند الأسود، يختفي عند الإضاءة
    mask = lum.point(lambda v: int((1 - v / 255) ** 1.6 * 255 * strength))
    tint = Image.new("RGB", im.size, COOL)
    return Image.composite(tint, im, mask)


def horizontal(src, out, kicker, title, sub, gold_word=None, fx=0.5, fy=0.5,
               title_px=104, x_right=1198, y_bottom=566, max_w=520,
               shade=("right", 215, 0.48)) -> str:
    W, H = 1280, 720
    base = cover_crop(src, W, H, fx, fy)
    base = cool_grade(base)
    base = P.vignette(base, 0.30)
    base = side_shade(base, shade[0], strength=shade[1], width=shade[2], soft=0.55)

    fonts = fit_lines(title, max_w, title_px, 52)
    line_h = [int(f.size * 1.30) for f in fonts]
    y_title = y_bottom - sum(line_h)

    def painter(d):
        fk = G.font(G.PLEX_B, 29)
        draw(d, (x_right, y_title - 46), kicker, fk, GOLD_L + (255,))
        y = y_title
        for text, f, lh in zip(title, fonts, line_h):
            fill = (GOLD_L if gold_word and gold_word in text else PARCH) + (255,)
            draw(d, (x_right, y), text, f, fill)
            y += lh
        fs = fit_font(G.PLEX_M, sub, max_w + 40, 28, 19)
        draw(d, (x_right, y_bottom + 26), sub, fs, (223, 230, 236, 255))

    shadowed(base, painter, blur=10, offsets=((0, 5), (0, 12), (0, 22)), alpha=236)
    lockup(base, 92, (40, 24))
    gold_frame(base, W, H)

    base.save(out.replace(".jpg", ".png"))
    base.save(out, quality=92, subsampling=1)
    print("cover", out)
    return out


def vertical(src, out, kicker, title, sub, fx=0.5, fy=0.3, band_h=1160) -> str:
    """1080×1920: صورة أعلى + كتلة نص أسفلها، وآخر 240px خالية (واجهة الشورتس)."""
    W, H = 1080, 1920
    base = Image.new("RGB", (W, H), INK)
    band = cover_crop(src, W, band_h, fx, fy)
    band = cool_grade(band)
    band = side_shade(band, "bottom", strength=160, width=0.30, soft=0.8)
    base.paste(band, (0, 0))

    fade = Image.new("L", (1, band_h), 0)
    for i in range(band_h):
        t = i / (band_h - 1)
        fade.putpixel((0, i), 0 if t < 0.82 else int(((t - 0.82) / 0.18) ** 1.3 * 255))
    base.paste(Image.new("RGB", (W, band_h), INK), (0, 0), fade.resize((W, band_h)))

    # كتلة النص: تُوسَّط رأسيًا بين أسفل الشريط وحدّ 250px السفلي، وتتقلّص إن لزم
    sub_f = fit_font(G.PLEX_M, sub, W - 180, 36, 25)
    gap = 50                                  # فاصل بين العنوان وسطر الشرح
    start = 146
    while start > 70:
        fonts = fit_lines(title, W - 170, start, 70)
        heights = [int(f.size * 1.32) for f in fonts]
        block = 62 + sum(heights) + gap + 46   # kicker + سطور + فاصل + شرح
        if band_h + 84 + block <= H - 240:
            break
        start -= 6
    y = band_h + 84 + max(0, ((H - 250) - (band_h + 84) - block) // 2)

    def painter(d):
        draw(d, (W - 70, y - 62), kicker, G.font(G.PLEX_B, 40), GOLD_L + (255,))
        yy = y
        for text, f, lh in zip(title, fonts, heights):
            draw(d, (W - 70, yy), text, f, PARCH + (255,))
            yy += lh
        draw(d, (W - 70, yy + gap), sub, sub_f, (223, 230, 236, 255))

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

    # A — الخطر الحاضر: «هو واقف وراك» (الموظف + ظلّ الآلة)
    horizontal(BG_A, f"{OUT}/THUMB_A_AI_JOBS_1280x720.jpg",
               "في مكتبك… دلوقتي",
               ["هو واقف وراك", "وانت مش واخد بالك"],
               "80% بتدرّب فريقها… 40% بس بتقلّل",
               gold_word="وانت مش واخد بالك",
               fx=0.44, fy=0.50, title_px=96, y_bottom=520, max_w=560)

    # B — إعادة التأطير: «مش بديلك… شريكك» (اليد تلمس اليد)
    horizontal(BG_B, f"{OUT}/THUMB_B_AI_JOBS_1280x720.jpg",
               "اللي محدش بيقوله",
               ["مش بديلك", "شريكك"],
               "اللي بيتعلّم بيكسب… مش اللي بيخاف",
               gold_word="شريكك",
               fx=0.40, fy=0.50, title_px=118, y_bottom=540, max_w=560,
               shade=("right", 205, 0.44))

    # عمودي للشورتس/الكوميونيتي
    vertical(BG_A, f"{OUT}/THUMB_SHORTS_AI_JOBS_1080x1920.jpg",
             "الذكاء الاصطناعي وشغلك",
             ["هو واقف وراك", "وانت مش واخد بالك"],
             "الأرقام الحقيقية… مش الإشاعات", fx=0.46, fy=0.12, band_h=1080)
