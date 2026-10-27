"""أغلفة حزمة الشورتس «سر واحد» — A/B عمودي 1080×1920.

الغلاف بملء الإطار، والنص في أعلى الصورة (المنطقة المظلمة طبيعيًا) بعيدًا عن
شريط العنوان أسفل الشورتس وأزرار التفاعل على اليمين.

    python3 scripts/publish/family_pack.py
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
OUT = f"{REPO}/outputs/PUBLISH_PACK_FAMILY"
ART = f"{OUT}/art"

BG_A = f"{ART}/bg_A.png"   # البيت: العائلة على الطربيزة والراجل بالصينية (مولَّد)
BG_B = f"{ART}/bg_B.png"   # الزقاق: واقف في الباب والناس ماشية (مولَّد)

INK, PARCH, GOLD, GOLD_L = G.INK, G.PARCH, G.GOLD, G.GOLD_L
draw, rtl = P.draw, P.rtl
fit_font, side_shade = P.fit_font, P.side_shade
shadowed, gold_frame, lockup, fit_lines = P.shadowed, P.gold_frame, P.lockup, P.fit_lines


def grade(im: Image.Image, contrast=1.14) -> Image.Image:
    im = ImageEnhance.Brightness(im).enhance(1.03)
    im = ImageEnhance.Contrast(im).enhance(contrast)
    im = ImageEnhance.Color(im).enhance(1.06)
    return im


def vertical(src, out, kicker, title, sub, fx=0.5, fy=0.5, top_h=0.44,
             title_px=150, y_kicker=200) -> str:
    W, H = 1080, 1920
    base = P.cover_crop(src, W, H, fx, fy)
    base = grade(base)
    base = P.vignette(base, 0.34)

    # تعتيم متدرّج من الأعلى كي يُقرأ النص فوق الإضاءة الداخلية
    n = 96
    line = Image.new("L", (1, n), 0)
    for i in range(n):
        t = i / (n - 1)
        line.putpixel((0, i), int(max(0.0, 1 - t / top_h) ** 1.15 * 240))
    base.paste(Image.new("RGB", (W, H), (8, 7, 6)), (0, 0), line.resize((W, H), Image.BICUBIC))
    base = side_shade(base, "bottom", strength=155, width=0.24, soft=0.85)

    fonts = fit_lines(title, W - 190, title_px, 92)
    heights = [int(f.size * 1.24) for f in fonts]
    sub_f = fit_font(G.PLEX_M, sub, W - 230, 38, 25)
    y = y_kicker + 76

    def painter(d):
        draw(d, (W - 84, y_kicker), kicker, G.font(G.PLEX_B, 41), GOLD_L + (255,))
        yy = y
        for i, (text, f, lh) in enumerate(zip(title, fonts, heights)):
            fill = (GOLD_L if i == len(title) - 1 else PARCH) + (255,)
            draw(d, (W - 84, yy), text, f, fill)
            yy += lh
        draw(d, (W - 84, yy + 32), sub, sub_f, (234, 222, 200, 255))

    shadowed(base, painter, blur=13, offsets=((0, 6), (0, 16)), alpha=218)

    d = ImageDraw.Draw(base, "RGBA")
    lockup(base, 106, (46, 44))
    d.line([(84, H - 300), (W - 84, H - 300)], fill=GOLD_L + (100,), width=2)
    d.rectangle([16, 16, W - 17, H - 17], outline=GOLD_L + (190,), width=2)

    base.save(out.replace(".jpg", ".png"))
    base.save(out, quality=92, subsampling=1)
    print("cover", out)
    return out


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)

    # A — اللغز: «سر واحد أنقذ عيلة»
    vertical(BG_A, f"{OUT}/THUMB_A_FAMILY_1080x1920.jpg",
             "قصة عمر ويوسف",
             ["سر واحد", "أنقذ عيلة"],
             "عيلة على وشك تفترق… وراجل واحد بس فضل",
             fx=0.50, fy=0.50, top_h=0.40, title_px=154, y_kicker=188)

    # B — الصورة الأقوى: «هو اللي فضل»
    vertical(BG_B, f"{OUT}/THUMB_B_FAMILY_1080x1920.jpg",
             "لما الكل مشي",
             ["هو اللي", "فضل واقف"],
             "الوفاء مش كلام… ده اللي بيفضل في الضلمة",
             fx=0.56, fy=0.52, top_h=0.40, title_px=158, y_kicker=196)
