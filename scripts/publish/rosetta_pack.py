"""أغلفة حزمة الشورتس «حجر رشيد» — A/B عمودي 1080×1920 (+ نسختان أفقيتان 1280×720).

الغلاف العمودي بملء الإطار (الصورة 9:16 أصلًا)، والنص في أعلى الإطار حيث الظلام
الطبيعي للصورة — بعيدًا عن شريط العنوان في أسفل الشورتس وأزرار التفاعل على اليمين.

    python3 scripts/publish/rosetta_pack.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "series"))

import graphics as G  # noqa: E402
from PIL import Image, ImageDraw, ImageEnhance  # noqa: E402

import abu_simbel_pack as P  # noqa: E402
import stress_pack as S  # noqa: E402

REPO = "/home/user/Riwaq_System_Repo"
OUT = f"{REPO}/outputs/PUBLISH_PACK_ROSETTA"
ART = f"{OUT}/art"

BG_A = f"{ART}/bg_A.png"   # حجر منقوش في ظلام متحفي (مولَّد)
BG_B = f"{ART}/bg_B.png"   # مكتب عالم 1820 على ضوء شمعة (مولَّد)

INK, PARCH, GOLD, GOLD_L = G.INK, G.PARCH, G.GOLD, G.GOLD_L
draw, rtl = P.draw, P.rtl
fit_font, side_shade = P.fit_font, P.side_shade
shadowed, gold_frame, lockup, fit_lines = P.shadowed, P.gold_frame, P.lockup, P.fit_lines


def grade(im: Image.Image, contrast=1.16, bright=1.02) -> Image.Image:
    im = ImageEnhance.Brightness(im).enhance(bright)
    im = ImageEnhance.Contrast(im).enhance(contrast)
    im = ImageEnhance.Color(im).enhance(1.05)
    return im


def vertical(src, out, kicker, title, sub, fx=0.5, fy=0.5, top_h=0.46,
             title_px=150, y_kicker=250) -> str:
    """1080×1920 بملء الإطار: تعتيم علوي للنص، إطار ذهبي، وشعار أعلى اليسار."""
    W, H = 1080, 1920
    base = P.cover_crop(src, W, H, fx, fy)
    base = grade(base)
    base = P.vignette(base, 0.30)

    # تعتيم متدرّج من الأعلى (ظلام طبيعي فوق الحجر) — بلا لوح ظاهر
    n = 96
    line = Image.new("L", (1, n), 0)
    for i in range(n):
        t = i / (n - 1)
        v = int(max(0.0, 1 - t / top_h) ** 1.15 * 235)
        line.putpixel((0, i), v)
    mask = line.resize((W, H), Image.BICUBIC)
    base.paste(Image.new("RGB", (W, H), (8, 7, 6)), (0, 0), mask)
    base = side_shade(base, "bottom", strength=150, width=0.26, soft=0.85)

    # كتلة النص: من أعلى الإطار للنصف تقريبًا
    fonts = fit_lines(title, W - 200, title_px, 96)
    heights = [int(f.size * 1.26) for f in fonts]
    y = y_kicker + 74
    sub_f = fit_font(G.PLEX_M, sub, W - 230, 38, 26)

    def painter(d):
        draw(d, (W - 84, y_kicker), kicker, G.font(G.PLEX_B, 42), GOLD_L + (255,))
        yy = y
        for i, (text, f, lh) in enumerate(zip(title, fonts, heights)):
            fill = (GOLD_L if i == len(title) - 1 else PARCH) + (255,)
            draw(d, (W - 84, yy), text, f, fill)
            yy += lh
        draw(d, (W - 84, yy + 34), sub, sub_f, (232, 220, 198, 255))

    shadowed(base, painter, blur=13, offsets=((0, 6), (0, 16)), alpha=215)

    d = ImageDraw.Draw(base, "RGBA")
    lockup(base, 108, (46, 44))
    d.line([(84, H - 300), (W - 84, H - 300)], fill=GOLD_L + (105,), width=2)
    d.rectangle([16, 16, W - 17, H - 17], outline=GOLD_L + (195,), width=2)

    base.save(out.replace(".jpg", ".png"))
    base.save(out, quality=92, subsampling=1)
    print("cover", out)
    return out


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)

    # A — الحجر نفسه: «حجر واحد فكّ 3000 سنة»
    vertical(BG_A, f"{OUT}/THUMB_A_ROSETTA_1080x1920.jpg",
             "اللغة اللي صمتت سنة 394",
             ["حجر واحد", "فكّ 3000 سنة"],
             "٣ خطوط… ولغة واحدة اختفت",
             fx=0.50, fy=0.50, top_h=0.50, title_px=150, y_kicker=196)

    # B — شامبليون: «20 سنة عشان يفكّها»
    vertical(BG_B, f"{OUT}/THUMB_B_ROSETTA_1080x1920.jpg",
             "من 1799 لـ 1822",
             ["23 سنة", "عشان يفكّها"],
             "وفقد الوعي لما فهم أول اسم",
             fx=0.50, fy=0.42, top_h=0.40, title_px=162, y_kicker=206)
