"""لوحة معاينة حزمة «أبو سمبل»: الغلاف A فوق الغلاف B، كل واحد بشريط يوضّح
الحرف والعنوان المقابِل له (A↔A / B↔B) كي لا يختلط الاختبار على أحد.

    /tmp/venv/bin/python scripts/publish/make_preview.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image, ImageDraw  # noqa: E402

import abu_simbel_pack as P  # noqa: E402
import graphics as G  # noqa: E402

OUT = P.OUT
W = 1280
COVER_H = 720
BAR_H = 58
GAP = 6

ITEMS = [
    ("A", "THUMB_A_ABU_SIMBEL_1280x720.png",
     "كيف رفعوا معبد أبو سمبل 65 مترًا؟ | معجزة إنقاذ اليونسكو"),
    ("B", "THUMB_B_ABU_SIMBEL_1280x720.png",
     "أنقذوه قبل الغرق: كيف نُقل معبد أبو سمبل قطعة قطعة؟"),
]


def bar(letter: str, title: str) -> Image.Image:
    im = Image.new("RGB", (W, BAR_H), P.INK)
    d = ImageDraw.Draw(im, "RGBA")
    # مربّع الحرف في أقصى اليمين
    s = 38
    x0, y0 = W - 40 - s, (BAR_H - s) // 2
    d.rounded_rectangle([x0, y0, x0 + s, y0 + s], radius=6, fill=P.GOLD_L + (255,))
    f_letter = G.font(G.PLEX_B, 26)
    d.text((x0 + s / 2, y0 + s / 2 - 2), letter, font=f_letter, fill=P.INK + (255,), anchor="mm")
    # العنوان
    f = P.fit_font(G.PLEX_M, title, W - 40 - s - 34 - 40, 30, 18)
    P.draw(d, (x0 - 20, BAR_H // 2), title, f, P.PARCH + (255,), anchor="rm")
    return im


def main() -> None:
    blocks = [bar(l, t) for l, _, t in ITEMS]
    covers = [Image.open(os.path.join(OUT, f)).convert("RGB") for _, f, _ in ITEMS]

    H = len(ITEMS) * (BAR_H + COVER_H) + GAP * (len(ITEMS) - 1)
    sheet = Image.new("RGB", (W, H), (0, 0, 0))
    y = 0
    for b, c in zip(blocks, covers):
        sheet.paste(b, (0, y))
        y += BAR_H
        sheet.paste(c, (0, y))
        y += COVER_H + GAP

    out = os.path.join(OUT, "AB_PREVIEW.png")
    sheet.save(out)
    print("preview", out, sheet.size)


if __name__ == "__main__":
    main()
