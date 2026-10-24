"""ورقة مراجعة v2 — إطار القديم مع خط التوقيع + شارة النص 4× + خيارا الترقيم.

    /tmp/venv/bin/python scripts/publish/review_v2.py
الناتج: outputs/FRAME_TEST/REVIEW-v2-frame-textbadge-numbering.png
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
OLD = REPO / "outputs" / "SERIES_RIWAQ" / "covers_v2" / "02" / "THUMB_A_1280x720.jpg"
NEW = next((REPO / "outputs" / "PUBLISH_PACK_EP02_COVERS").glob("02-CVR-H-A-*.jpg"))

BG = (16, 15, 14)
INK = (235, 224, 202)
SUB = (146, 134, 114)
PAD = 26


def crop(im: Image.Image, box, zoom: int = 4) -> Image.Image:
    c = im.crop(box)
    return c.resize((c.width * zoom, c.height * zoom), Image.NEAREST)


def ar(d, xy, text, fnt, fill=SUB, anchor="la"):
    d.text(xy, CS.G.ar(text), font=fnt, fill=fill, anchor=anchor)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    old = Image.open(OLD).convert("RGB")
    new = Image.open(NEW).convert("RGB")
    corner_opt = new.copy()
    CS.series_badge(corner_opt, "2 من 6", corner="tr", px=18)

    f_h = CS.font("sans_b", 24)
    f_l = CS.font("sans_m", 17)

    TL = (0, 0, 118, 118)
    other = {"أعلى-يمين": (1162, 0, 1280, 118),
             "أسفل-يسار": (0, 602, 118, 720),
             "أسفل-يمين": (1162, 602, 1280, 720)}

    z_old = crop(old, TL)
    z_new = crop(new, TL)
    small = {k: crop(new, b).resize((z_new.width // 2, z_new.height // 2), Image.LANCZOS)
             for k, b in other.items()}

    # ---- صف 1: زاوية أعلى-يسار (قديم/جديد) + الزوايا الثلاثة
    y1 = PAD
    hdr1_h = 34
    row1_h = hdr1_h + z_new.height + 26
    x_old, x_new = PAD, PAD + z_new.width + PAD
    x_small = x_new + z_new.width + PAD
    sw = z_new.width // 2

    # ---- صف 2: الشارة
    badge = crop(new, (92, 444, 566, 578), 4)
    notes = ["ظل ناعم واسع يفصلها عن الصورة",
             "قاعدة داكنة مُزاحة 2px = سُّمك مرئي",
             "حدّ ذهبي خارجي 2px",
             "حدّ ذهبي داخلي 1px — يظهر فوق وتحت",
             "زوايا دائرية، ليست حادّة"]
    hdr2_h = 34
    row2_h = hdr2_h + badge.height + 16 + len(notes) * 26

    # ---- صف 3: الترقيم
    opt_a = crop(new, (292, 92, 540, 146), 4)          # كبسولة أعلى الكتلة
    opt_b = crop(corner_opt, (1140, 92, 1272, 146), 4)  # شارة زاوية الإطار
    hdr3_h = 34
    row3_h = hdr3_h + opt_a.height + 30

    notes_w = max(CS.G.text_w(f_l, CS.G.ar("•  " + n)) for n in notes)
    W = max(x_small + 3 * (sw + PAD) + PAD,
            PAD + badge.width + PAD + notes_w + PAD,
            PAD + opt_a.width + PAD + opt_b.width + PAD) + PAD
    H = PAD + row1_h + PAD + row2_h + PAD + row3_h + PAD
    canvas = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(canvas)

    # ===== صف 1
    y = y1
    ar(d, (PAD, y), "١) الإطار: القديم (يسار) مقابل المعتمد الجديد (يمين) — زاوية أعلى-يسار، تكبير ٤×", f_h, INK)
    y += hdr1_h
    canvas.paste(z_old, (x_old, y))
    canvas.paste(z_new, (x_new, y))
    ar(d, (x_old, y + z_new.height + 5), "القديم", f_l)
    ar(d, (x_new, y + z_new.height + 5), "الجديد = القديم + خط التوقيع", f_l)
    for i, (name, img) in enumerate(small.items()):
        sx = x_small + i * (sw + PAD)
        canvas.paste(img, (sx, y))
        ar(d, (sx, y + img.height + 4), name, f_l)

    # ===== صف 2
    y = PAD + row1_h + PAD
    ar(d, (PAD, y), "٢) إطار النص (المستوى الثالث) — طبقات العمق — تكبير ٤×", f_h, INK)
    y += hdr2_h
    canvas.paste(badge, (PAD, y))
    for i, n in enumerate(notes):
        ar(d, (PAD + badge.width + PAD, y + 10 + i * 26), "•  " + n, f_l)

    # ===== صف 3
    y = PAD + row1_h + PAD + row2_h + PAD
    ar(d, (PAD, y), "٣) الترقيم — أي الخيارين؟ (تكبير ٤×)", f_h, INK)
    y += hdr3_h
    canvas.paste(opt_a, (PAD, y))
    ar(d, (PAD, y + opt_a.height + 6), "أ) كبسولة أعلى الكتلة النصية", f_l)
    xb = PAD + opt_a.width + PAD
    canvas.paste(opt_b, (xb, y))
    ar(d, (xb, y + opt_b.height + 6), "ب) شارة صغيرة داخل زاوية الإطار", f_l)

    out = OUT / "REVIEW-v2-frame-textbadge-numbering.png"
    canvas.save(out)
    print("out:", out, canvas.size)


if __name__ == "__main__":
    main()
