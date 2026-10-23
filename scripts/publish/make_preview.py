"""لوحة معاينة أي حزمة A/B: كل غلاف تحته شريط يوضّح الحرف + العنوان المقابِل له.

    python scripts/publish/make_preview.py OUT_DIR "A|file.png|العنوان" "B|file.png|العنوان"

الحروف والعناوين تُطبع فوق خلفية حبر، فتبقى قاعدة الاقتران A↔A / B↔B واضحة
ولا يختلط الاختبار على أحد.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "series"))

from PIL import Image, ImageDraw  # noqa: E402

import graphics as G  # noqa: E402

W = 1280
BAR_H = 58
GAP = 6
INK = G.INK
PARCH = G.PARCH
GOLD_L = G.GOLD_L


def fit_font(path, text, max_w, start, floor=16):
    px = start
    while px > floor:
        f = G.font(path, px)
        if G.text_w(f, G.ar(text)) <= max_w:
            return f
        px -= 2
    return G.font(path, floor)


def bar(letter: str, title: str) -> Image.Image:
    im = Image.new("RGB", (W, BAR_H), INK)
    d = ImageDraw.Draw(im, "RGBA")
    s = 38
    x0, y0 = W - 40 - s, (BAR_H - s) // 2
    d.rounded_rectangle([x0, y0, x0 + s, y0 + s], radius=6, fill=GOLD_L + (255,))
    d.text((x0 + s / 2, y0 + s / 2 - 2), letter, font=G.font(G.PLEX_B, 26),
           fill=INK + (255,), anchor="mm")
    f = fit_font(G.PLEX_M, title, W - 40 - s - 34 - 40, 30)
    d.text((x0 - 20, BAR_H // 2), G.ar(title), font=f, fill=PARCH + (255,), anchor="rm")
    return im


def main(argv: list[str]) -> None:
    out_dir = argv[1]
    items = [a.split("|", 2) for a in argv[2:]]
    covers = [Image.open(os.path.join(out_dir, f)).convert("RGB") for _, f, _ in items]
    cw, ch = covers[0].size
    assert all(c.size == (cw, ch) for c in covers), "كل الأغلفة لازم تكون بنفس المقاس"

    H = len(items) * (BAR_H + ch) + GAP * (len(items) - 1)
    sheet = Image.new("RGB", (cw, H), (0, 0, 0))
    y = 0
    for (letter, _, title), c in zip(items, covers):
        sheet.paste(bar(letter, title).resize((cw, BAR_H), Image.LANCZOS), (0, y))
        y += BAR_H
        sheet.paste(c, (0, y))
        y += ch + GAP

    out = os.path.join(out_dir, "AB_PREVIEW.png")
    sheet.save(out)
    print("preview", out, sheet.size)


if __name__ == "__main__":
    main(sys.argv)
