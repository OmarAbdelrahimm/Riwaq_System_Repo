"""أغلفة «التواصل ليس علاقة» — نسختان تنفيذًا لملاحظات vidIQ.

ملاحظات الأداة الثلاثة على الغلاف القديم:
  1) «قصّ أقرب على الوجه أو استبدل الخلفية بخلفية أنظف».
  2) «أضف سهمًا أو إشارة بصرية تدلّ على العنصر الأساسي».
  3) «استخدم تخطيطًا نظيفًا للمقارنة جنبًا إلى جنب أو نصف/نصف».

  A = تخطيط نصف/نصف (التواصل ≠ العلاقة) مع علامة ≠ ذهبية بينهما.
  B = وجه مكبّر مع سهم ذهبي يشير إلى الضيف.

    /tmp/venv/bin/python scripts/publish/tawasul_v2.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "series"))

import graphics as G  # noqa: E402
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter  # noqa: E402

import abu_simbel_pack as P  # noqa: E402

REPO = "/home/user/Riwaq_System_Repo"
OUT = f"{REPO}/outputs/PUBLISH_PACK_TAWASUL"
SRC = f"{REPO}/public/projects/TAWASUL_001/assets/sheikh_tawasul.jpg"

INK, PARCH, GOLD, GOLD_L, STONE = G.INK, G.PARCH, G.GOLD, G.GOLD_L, G.STONE

draw, rtl = P.draw, P.rtl
shadowed, gold_frame, lockup = P.shadowed, P.gold_frame, P.lockup
fit_font, fit_lines = P.fit_font, P.fit_lines


def load(fx=0.5, fy=0.5, zoom=1.0) -> Image.Image:
    im = Image.open(SRC).convert("RGB")
    if zoom != 1.0:
        w, h = int(im.width / zoom), int(im.height / zoom)
        x, y = int((im.width - w) * fx), int((im.height - h) * fy)
        im = im.crop((x, y, x + w, y + h))
    return im


def resize_cover(im: Image.Image, W: int, H: int, fx=0.5, fy=0.5) -> Image.Image:
    s = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * s + 0.5), int(im.height * s + 0.5)), Image.LANCZOS)
    x, y = int((im.width - W) * fx), int((im.height - H) * fy)
    return im.crop((x, y, x + W, y + H))


def clean_bg(im: Image.Image, amount=0.55) -> Image.Image:
    """«خلفية أنظف»: تفتيح التفاصيل المشتّتة (لمبات/ستارة) بضباب خفيف على الأطراف فقط."""
    W, H = im.size
    blurred = im.filter(ImageFilter.GaussianBlur(int(W * 0.012)))
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([W * 0.34, -H * 0.22, W * 1.24, H * 1.22], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(W // 9))
    mask = mask.point(lambda v: int(v * amount))
    return Image.composite(im, blurred, mask)


def grade(im: Image.Image) -> Image.Image:
    im = ImageEnhance.Brightness(im).enhance(1.05)
    im = ImageEnhance.Contrast(im).enhance(1.12)
    im = ImageEnhance.Color(im).enhance(0.94)      # ستارة أقل إشباعًا = خلفية أهدأ
    return im


def shadowed_shapes(base: Image.Image, painter, blur=14, offsets=((0, 5), (0, 14)), alpha=210):
    """ظل ناعم لأي رسم (سهم/دائرة) بنفس منطق ظلّ النص."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    painter(ImageDraw.Draw(layer, "RGBA"))
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", base.size, (0, 0, 0, alpha)), (0, 0), layer.split()[-1])
    for dx, dy in offsets:
        b = sh.filter(ImageFilter.GaussianBlur(blur))
        base.paste(Image.new("RGB", base.size, (0, 0, 0)), (dx, dy), b.split()[-1])
    base.paste(layer, (0, 0), layer)


# ------------------------------------------------------------------ A: نصف/نصف
def cover_a(out: str) -> str:
    W, H = 1280, 720
    SPLIT = 628

    # لوح اليمين: الضيف مقصوص أقرب (وجه أكبر، خلفية أنظف)
    right = resize_cover(clean_bg(load(zoom=1.14)), W - SPLIT, H, fx=0.62, fy=0.30)
    right = grade(right)

    # لوح اليسار: حبر بارد قليلًا للتفريق البصري بين المفهومين
    left = Image.new("RGB", (SPLIT, H), INK)
    grad = Image.new("L", (1, H), 0)
    for i in range(H):
        grad.putpixel((0, i), int(18 + 26 * (i / (H - 1))))
    left.paste(Image.new("RGB", (SPLIT, H), (34, 38, 42)), (0, 0), grad.resize((SPLIT, H)))

    base = Image.new("RGB", (W, H), INK)
    base.paste(left, (0, 0))
    base.paste(right, (SPLIT, 0))
    base = P.vignette(base, 0.30)

    # العنوانان على مستوى واحد للمقارنة المباشرة
    y_word = 196
    f_word = G.font(G.AMIRI_B, 92)

    def painter(d):
        # يسار اللوحة: التواصل
        d.text((SPLIT - 62, y_word), G.ar("التواصل"), font=f_word,
               fill=(226, 219, 205, 255), anchor="ra")
        d.text((SPLIT - 62, y_word + 118), G.ar("كلام · رسائل · إقناع"),
               font=G.font(G.PLEX_M, 27), fill=(158, 150, 136, 255), anchor="ra")
        d.text((SPLIT - 62, 96), G.ar("الفرق اللي بيغيّر كل حاجة"),
               font=G.font(G.PLEX_B, 26), fill=GOLD_L + (255,), anchor="ra")

        # يمين اللوحة: العلاقة في أعلى الكادر (منطقة الستارة الداكنة، فوق الوجه)
        d.text((SPLIT + 62, 96), G.ar("العلاقة"), font=f_word,
               fill=GOLD_L + (255,), anchor="la")
        d.text((SPLIT + 62, 96 + 118), G.ar("وقت · أمان · وفاء"),
               font=G.font(G.PLEX_M, 27), fill=(232, 220, 198, 255), anchor="la")

        # تسمية كل مفهوم
        f_l = G.font(G.PLEX_M, 24)
        d.text((SPLIT - 62, 372), G.ar("مهارة تتعلّمها"), font=f_l,
               fill=(150, 143, 130, 255), anchor="ra")
        d.text((SPLIT + 62, 372), G.ar("اختيار كل يوم"), font=f_l,
               fill=(214, 200, 178, 255), anchor="la")

        # خلاصة أسفل اليسار
        f_c = G.font(G.AMIRI_B, 44)
        d.text((SPLIT - 62, 556), G.ar("العلاقة مش نتيجة الكلام"),
               font=f_c, fill=PARCH + (255,), anchor="ra")
        d.text((SPLIT - 62, 618), G.ar("الكلام نتيجة العلاقة"), font=f_c,
               fill=GOLD_L + (255,), anchor="ra")
        d.text((SPLIT + 62, 652), G.ar("ياسر الحزيمي · بدون ورق"),
               font=G.font(G.PLEX_B, 23), fill=(216, 207, 192, 255), anchor="la")

    shadowed(base, painter, blur=11, offsets=((0, 5), (0, 14), (0, 24)), alpha=232)

    # علامة ≠ ذهبية على خط الفصل — الإشارة البصرية التي طلبتها الأداة
    def badge(d):
        cx, cy, r = SPLIT, y_word + 74, 40
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(24, 21, 17, 245),
                  outline=GOLD_L + (235,), width=3)
        d.line([(cx - 15, cy - 15), (cx + 15, cy + 15)], fill=GOLD_L + (255,), width=6)
        d.line([(cx + 15, cy - 15), (cx - 15, cy + 15)], fill=GOLD_L + (255,), width=6)

    shadowed_shapes(base, badge, blur=16, offsets=((0, 6),), alpha=190)

    d = ImageDraw.Draw(base, "RGBA")
    d.line([(SPLIT, 0), (SPLIT, H)], fill=GOLD_L + (150,), width=2)
    lockup(base, 88, (36, 26))
    gold_frame(base, W, H, inset=16)

    base.save(out.replace(".jpg", ".png"))
    base.save(out, quality=93, subsampling=1)
    print("cover", out)
    return out


# ------------------------------------------------------------------ B: وجه مكبّر + سهم
def cover_b(out: str) -> str:
    W, H = 1280, 720
    # قصّ أقرب مع ترك الضيف في يمين الكادر، ثم تعتيم قوي على اليسار للنص
    base = resize_cover(clean_bg(load(zoom=1.22), amount=0.65), W, H, fx=0.86, fy=0.20)
    base = grade(base)
    base = P.vignette(base, 0.32)
    base = P.side_shade(base, "left", strength=248, width=0.62, soft=0.46)

    x = 392                                   # حدّ النص من اليمين للشمال
    maxw = x - 74                             # هامش أيسر مضمون داخل الإطار

    def fit_amiri(text, start, floor=48):
        px = start
        while px > floor:
            f = G.font(G.AMIRI_B, px)
            if G.text_w(f, G.ar(text)) <= maxw:
                return f
            px -= 2
        return G.font(G.AMIRI_B, floor)

    f1 = fit_amiri("التواصل", 92)
    f2 = fit_amiri("ليس علاقة!", 112)

    def painter(d):
        d.text((x, 92), G.ar("بودكاست بدون ورق"), font=G.font(G.PLEX_B, 25),
               fill=GOLD_L + (255,), anchor="ra")
        d.text((x, 128), G.ar("التواصل"), font=f1, fill=PARCH + (255,), anchor="ra")
        d.text((x, 262), G.ar("ليس علاقة!"), font=f2, fill=GOLD_L + (255,), anchor="ra")
        d.line([(x - 300, 400), (x, 400)], fill=GOLD + (135,), width=2)
        d.text((x, 418), G.ar("أغلب خناقاتنا"), font=G.font(G.PLEX_B, 30),
               fill=(230, 220, 202, 255), anchor="ra")
        d.text((x, 460), G.ar("سببها الخلط بينهم"), font=G.font(G.PLEX_M, 28),
               fill=(212, 202, 184, 255), anchor="ra")
        d.text((x, 640), G.ar("ياسر الحزيمي · بدون ورق"),
               font=G.font(G.PLEX_B, 24), fill=(202, 193, 178, 255), anchor="ra")

    shadowed(base, painter, blur=12, offsets=((0, 6), (0, 16), (0, 26)), alpha=240)

    # سهم ذهبي يشير من النص إلى وجه الضيف (العنصر الأساسي)
    def arrow(d):
        y = 540
        x0, x1 = x - 300, x + 26
        d.line([(x0, y), (x1, y)], fill=GOLD_L + (225,), width=6)
        d.polygon([(x1 - 30, y), (x1 + 2, y - 16), (x1 + 2, y + 16)], fill=GOLD_L + (225,))

    shadowed_shapes(base, arrow, blur=12, offsets=((0, 5),), alpha=175)

    d = ImageDraw.Draw(base, "RGBA")
    lockup(base, 88, (36, 26))
    gold_frame(base, W, H, inset=16)

    base.save(out.replace(".jpg", ".png"))
    base.save(out, quality=93, subsampling=1)
    print("cover", out)
    return out


if __name__ == "__main__":
    os.makedirs(f"{OUT}/V2", exist_ok=True)
    cover_a(f"{OUT}/V2/THUMB_TAWASUL_V2_A_SPLIT_1280x720.jpg")
    cover_b(f"{OUT}/V2/THUMB_TAWASUL_V2_B_FACE_1280x720.jpg")
