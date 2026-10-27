"""اختبار الإطار فقط — الزاوية بمقاس 4× — القديم / الحالي / المقترح جنبًا إلى جنب.

    python3 scripts/publish/frame_test.py

لا يُنتج أي ملف تسليم: صورة واحدة للمراجعة في outputs/FRAME_TEST/.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import Image, ImageDraw

import cover_system as CS
import ep02_cover as EP

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "outputs" / "FRAME_TEST"
REF = Path("/tmp/arena-coding-uploads/image-1.jpeg")      # الغلاف المرجعي الاحترافي
OLD = REPO / "outputs" / "SERIES_RIWAQ" / "covers_v2" / "02" / "THUMB_A_1280x720.jpg"
CUR = next((REPO / "outputs" / "PUBLISH_PACK_EP02_COVERS").glob("02-CVR-H-A-*.jpg"))

CROP = 132          # مقاس القص (px) — 4× ⇒ 528
ZOOM = 4
GAP = 18
LABEL_H = 40

ROWS = {
    "TL": ((0, 0), "الزاوية العليا-اليسرى"),
    "TR": ((1280 - CROP, 0), "الزاوية العليا-اليمنى — موضع الترقيم المقترح"),
    "BL": ((0, 720 - CROP), "الزاوية السفلى-اليسرى (خط التوقيع)"),
}


def rebuilt(bevel: bool, thick: bool, corner_badge: bool) -> Image.Image:
    """يعيد بناء غلاف A بالإطار المقترح فقط (بدون أي تغيير في النص)."""
    im = EP.cover_a.__wrapped__() if hasattr(EP.cover_a, "__wrapped__") else None
    # نُعيد استخدام البناء نفسه مع تعطيل الإطار ثم نطبّق النسخة المقترحة
    orig = CS.frame3
    CS.frame3 = lambda img, *a, **k: img
    try:
        base = EP.cover_a()
    finally:
        CS.frame3 = orig
    if corner_badge:
        # نص مختصر في اختبار الزاوية فقط — النص الطويل يمتد يسارًا خارج القص
        CS.series_badge(base, "2 من 6", corner="tr", px=18)
    CS.frame3(base, bevel=bevel, thick=thick, opaque=True)
    return base


def panel(im: Image.Image, corner: str) -> Image.Image:
    (x, y), _ = ROWS[corner]
    c = im.crop((x, y, x + CROP, y + CROP)).resize((CROP * ZOOM, CROP * ZOOM), Image.NEAREST)
    return c


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    proposed = rebuilt(bevel=True, thick=True, corner_badge=True)
    progressive = rebuilt(bevel=True, thick=True, corner_badge=False)

    flat = rebuilt(bevel=False, thick=True, corner_badge=False)
    sources = [
        ("REFERENCE", Image.open(REF).convert("RGB"), "المرجع"),
        ("OLD", Image.open(OLD).convert("RGB"), "القديم"),
        ("CURRENT", Image.open(CUR).convert("RGB"), "الحالي v1"),
        ("FLAT", flat, "v2 بلا 3D"),
        ("BEVEL", progressive, "v2 + 3D"),
        ("BEVEL+TAG", proposed, "v2 + 3D + الترقيم في الزاوية"),
    ]

    cols = len(sources)
    pw = CROP * ZOOM
    W = cols * pw + (cols - 1) * GAP + 2 * GAP
    row_lab_h = 30
    row_stride = row_lab_h + pw + GAP
    H = LABEL_H + 8 + len(ROWS) * row_stride + GAP
    canvas = Image.new("RGB", (W, H), (18, 17, 16))
    d = ImageDraw.Draw(canvas)

    f_lab = CS.font("sans_b", 20)
    f_row = CS.font("sans_m", 17)

    # الصور أولًا، ثم كل النصوص فوقها (وإلا اختفت تحت الصور)
    for r, (corner, _) in enumerate(ROWS.items()):
        y0 = LABEL_H + 8 + r * row_stride
        for i, (_, img, _) in enumerate(sources):
            x = GAP + i * (pw + GAP)
            py = y0 + row_lab_h
            canvas.paste(panel(img, corner), (x, py))
            d.rectangle([x - 1, py - 1, x + pw, py + pw], outline=(52, 47, 40), width=1)

    for i, (_, _, label) in enumerate(sources):
        x = GAP + i * (pw + GAP)
        d.text((x + pw // 2, 16), CS.G.ar(label), font=f_lab,
               fill=(226, 214, 190), anchor="ma")

    for r, (corner, (_, row_label)) in enumerate(ROWS.items()):
        y0 = LABEL_H + 8 + r * row_stride
        d.rectangle([GAP, y0 + 2, GAP + 400, y0 + row_lab_h - 4], fill=(18, 17, 16))
        d.text((GAP + 2, y0 + 6), CS.G.ar(row_label), font=f_row,
               fill=(168, 155, 132), anchor="la")

    out = OUT / "frame-corner-test-4x.png"
    canvas.save(out)
    print("out:", out, canvas.size)


if __name__ == "__main__":
    main()
