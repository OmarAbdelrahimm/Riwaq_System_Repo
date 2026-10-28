"""HARUN v4 — بناء طبقات الإطار من الماستر المعتمد v3 (قياس بكسل ببكسل).

التعديلات المطلوبة من صاحب العمل:
  1) حذف «الحلقة ١» من السطر العلوي وإبقاء «حكايات رِواق» + كسرة تحت الراء.
  2) كارت الكابشن بلا نص (النص يُحرَّق بـ libass لضمان اتجاه RTL صحيح).

المخرجات → public/projects/HARUN_001/frame_v4/
"""
from __future__ import annotations

import av
import arabic_reshaper
import numpy as np
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

REPO = "/home/user/Riwaq_System_Repo"
OUT = f"{REPO}/public/projects/HARUN_001/frame_v4"
V3 = f"{REPO}/google_drive/04-VID-harun-master-v3-1920x1080-frame.mp4"
FONT = f"{REPO}/public/fonts"
AMIRI_B = f"{FONT}/Amiri-Bold.ttf"
PLEX_M = f"{FONT}/IBMPlexSansArabic-Medium.ttf"

W, H = 1920, 1080
VX, VY, VW, VH = 249, 94, 1422, 800
CAP = (249, 902, 1671, 986)
TOP_GAP = (640, 1280)

INK = (20, 18, 14)
CARD = (24, 22, 16)
PARCH = (243, 235, 219)
GOLD = (169, 138, 75)
GOLD_L = (194, 164, 105)
STONE = (138, 127, 107)

SERIES_HI = "حكايات"
SERIES_LO = "رواق"
KASRA = "\u0650"
TITLE = "هارون الرشيد والرجل الحكيم"


def ar(t: str) -> str:
    return get_display(arabic_reshaper.reshape(t))


def series_line(d, cx, ink_top, fnt, fill):
    """«حكايات رواق» + كسرة مرسومة يدويًا تحت الراء (reshaper يُسقط الحركات)."""
    hi, lo = ar(SERIES_HI), ar(SERIES_LO)
    gap = fnt.getlength(" ") * 1.15
    w1, w2 = fnt.getlength(hi), fnt.getlength(lo)
    x = cx - (w1 + gap + w2) / 2
    y = ink_top - fnt.getbbox(hi)[1]
    d.text((x, y), hi, font=fnt, fill=fill)
    x2 = x + w1 + gap
    d.text((x2, y), lo, font=fnt, fill=fill)
    rx = x2 + fnt.getlength(lo[:-1])
    rb = fnt.getbbox(lo[-1])
    mb = fnt.getbbox(KASRA)
    kx = rx + (rb[0] + rb[2]) / 2 - (mb[0] + mb[2]) / 2
    ky = y + rb[3] - 2 - mb[1]
    d.text((kx, ky), KASRA, font=fnt, fill=fill)
    return (x, x + w1 + gap + w2)


def centered(d, cx, y, text, fnt, fill):
    s = ar(text)
    b = fnt.getbbox(s)
    d.text((cx - (b[2] - b[0]) / 2 - b[0], y), s, font=fnt, fill=fill)


def median_plate() -> Image.Image:
    """وسيط عشرات الإطارات: يثبّت الإطار ويُلغي الفيديو المتحرك والكابشن المتغيّر."""
    c = av.open(V3)
    s = c.streams.video[0]
    times = [5, 9, 13, 17, 21, 25, 29, 33, 41, 45, 49, 53, 57, 61, 65, 69, 73,
             77, 81, 85, 89, 93, 97, 101, 105, 109, 113, 117, 121, 125, 129,
             133, 137, 141, 145, 149, 153, 155]
    want = {int(round(t * 30)) for t in times}
    buf = []
    for i, fr in enumerate(c.decode(s)):
        if i in want:
            buf.append(np.asarray(fr.to_image().convert("RGB")))
        if i > max(want):
            break
    c.close()
    return Image.fromarray(np.median(np.stack(buf), axis=0).astype(np.uint8))


def build() -> Image.Image:
    base = median_plate().convert("RGB")
    d = ImageDraw.Draw(base)

    # 1) محو الرأس القديم (بين نهايتي خط الإطار العلوي)
    d.rectangle([TOP_GAP[0] + 1, 6, TOP_GAP[1] - 1, 93], fill=INK)
    # 2) محو الكارت القديم
    d.rectangle(list(CAP), fill=CARD)

    # 3) العنوان الجديد
    f1 = ImageFont.truetype(PLEX_M, 27)
    series_line(d, 960, 12, f1, (152, 141, 117))
    f2 = ImageFont.truetype(AMIRI_B, 40)
    centered(d, 960, 34 - f2.getbbox(ar(TITLE))[1], TITLE, f2, PARCH)

    # 4) كارت الكابشن
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle(list(CAP), radius=9, outline=GOLD + (135,), width=2)
    cd.line([CAP[0] + 20, CAP[1] + 3, CAP[2] - 20, CAP[1] + 3], fill=GOLD_L + (60,))
    cd.line([CAP[0] + 20, CAP[3] - 3, CAP[2] - 20, CAP[3] - 3], fill=GOLD_L + (50,))
    out = Image.alpha_composite(base.convert("RGBA"), card)

    # 5) تفريغ نافذة الفيديو
    px = out.load()
    for y in range(VY, VY + VH):
        for x in range(VX, VX + VW):
            px[x, y] = (0, 0, 0, 0)
    return out


def riddle() -> Image.Image:
    w, h = 700, 240
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=14,
                        fill=(24, 22, 16, 246), outline=GOLD + (200,), width=2)
    d.rounded_rectangle([9, 9, w - 10, h - 10], radius=8, outline=GOLD_L + (70,), width=1)
    for yy in (26, h - 27):
        d.line([w // 2 - 90, yy, w // 2 + 90, yy], fill=GOLD_L + (90,))
        d.ellipse([w // 2 - 3, yy - 3, w // 2 + 3, yy + 3], fill=GOLD_L + (200,))
    centered(d, w // 2, 52, "اللغز", ImageFont.truetype(AMIRI_B, 82), GOLD_L)
    centered(d, w // 2, 168, "فكّر معنا قبل أن تسمع الجواب",
             ImageFont.truetype(PLEX_M, 27), PARCH)
    return img


def ident() -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    centered(d, 960, 424, "رواق", ImageFont.truetype(AMIRI_B, 96), PARCH)
    d.line([760, 552, 1160, 552], fill=GOLD + (160,))
    centered(d, 960, 566, "تاريخ وتراث", ImageFont.truetype(PLEX_M, 34), GOLD_L)
    return img


def sweep() -> Image.Image:
    w, h = 520, 1400
    img = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(img)
    for i in range(w):
        d.line([(i, 0), (i, h)], fill=int(255 * (1 - abs(i - w / 2) / (w / 2)) ** 2.1))
    img = img.rotate(-18, expand=False, resample=Image.BICUBIC)
    rgba = Image.new("RGBA", (w, h), (255, 246, 224, 0))
    rgba.putalpha(img.point(lambda v: int(v * 0.34)))
    return rgba


def main() -> None:
    import os
    os.makedirs(OUT, exist_ok=True)
    build().save(f"{OUT}/FRAME_plate.png")
    riddle().save(f"{OUT}/CARD_riddle.png")
    ident().save(f"{OUT}/OVERLAY_ident.png")
    Image.new("RGBA", (W, H), (8, 7, 5, 150)).save(f"{OUT}/veil.png")
    sweep().save(f"{OUT}/sweep.png")
    print("frame layers OK ->", OUT)


if __name__ == "__main__":
    main()
