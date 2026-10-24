"""Riwaq Cover System v1 — القواعد المقيسة لأغلفة القناة.

المرجع النصي: docs/COVER_SYSTEM.md
كل رقم هنا مقيس بالبكسل من غلاف مرجعي احترافي 1280×720، وليس تقديرًا.

الاستخدام:
    from cover_system import TOKENS, COLORS, frame3, badge3d, signature_rule
    frame3(base)                     # إطار ثلاثي + أقواس + خط توقيع
    badge3d(base, box, "نص")         # شارة ثلاثية الأبعاد

لا تُضبّب الوجه. لا تُضف عنصرًا دون حذف آخر.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

_HERE = Path(__file__).resolve().parent
_FONTS = _HERE.parent.parent / "public" / "fonts"

sys.path.insert(0, str(_HERE.parent / "series"))
import graphics as G  # noqa: E402


# ---------------------------------------------------------------- الألوان
COLORS = {
    "champagne": (0xC2, 0xAF, 0x8F),   # #C2AF8F  الإطار · H2 · الشارات · المساطر
    "white": (0xFF, 0xFD, 0xF5),       # #FFFDF5  H1 · نص الشارة · الجسر · الاسم
    "hairline": (0xCB, 0xC7, 0xC6),    # #CBC7C6  الشعرة الوسطى فقط
    "gold_rule": (0xC3, 0xAD, 0x86),   # #C3AD86  مسطرة العنوان + خط التوقيع
    "ink": (0x14, 0x12, 0x0F),         # ظل الشارة (طبقة القاعدة)
}
# ممنوع الذهبي المشبع (#C9A961) على البطل — يُستخدم الشامبانيا فقط.


# ---------------------------------------------------------------- الهندسة
@dataclass(frozen=True)
class Frame:
    """مواضع الإطار الثلاثي، مُعايَرة على 1280×720 ثم تُقاس نسبيًا."""

    outer_inset: int = 16
    outer_w: int = 2
    hair_inset: int = 24
    hair_w: int = 1
    bracket_inset: int = 30
    bracket_arm: int = 30
    bracket_w: int = 2
    sig_x: int = 52
    sig_len: int = 91
    sig_y_from_bottom: int = 78
    sig_w: int = 2

    def scale(self, k: float) -> "Frame":
        """مقياس للنسخة العمودية 1080×1920 (k = 1.5) أو أي مقاس آخر."""
        f = lambda v: max(1, int(round(v * k)))  # noqa: E731
        return Frame(
            outer_inset=f(self.outer_inset), outer_w=max(1, f(self.outer_w)),
            hair_inset=f(self.hair_inset), hair_w=1,
            bracket_inset=f(self.bracket_inset), bracket_arm=f(self.bracket_arm),
            bracket_w=max(1, f(self.bracket_w)),
            sig_x=f(self.sig_x), sig_len=f(self.sig_len),
            sig_y_from_bottom=f(self.sig_y_from_bottom), sig_w=max(1, f(self.sig_w)),
        )


# ---------------------------------------------------------------- سلّم الطباعة
@dataclass(frozen=True)
class Ladder:
    """ستة مستويات. H1:H2 ≈ 1.13، وكل مستوى ≈ 42% من الذي قبله."""

    h1: int = 104        # الكلمة الرئيسية — أبيض دافئ
    h2: int = 92         # السطر الثاني — شامبانيا، Amiri Bold
    badge: int = 44      # الشارة 3D — الادعاء القابل للاقتباس
    bridge: int = 26     # الجسر — Plex Regular (خط مختلف)
    name: int = 30       # اسم الشيخ
    kicker: int = 20     # شارة التصنيف أعلى
    series: int = 18     # شارة السلسلة أسفل-يمين
    logo: int = 46

    rule_w: int = 336    # المسطرة = 80–85% من عرض السطر الأعلى
    rule_h: int = 4

    def scale(self, k: float) -> "Ladder":
        f = lambda v: int(round(v * k))  # noqa: E731
        return Ladder(h1=f(self.h1), h2=f(self.h2), badge=f(self.badge),
                      bridge=f(self.bridge), name=f(self.name),
                      kicker=f(self.kicker), series=f(self.series),
                      logo=f(self.logo),
                      rule_w=f(self.rule_w), rule_h=max(2, f(self.rule_h)))


TOKENS = Frame()
LADDER = Ladder()

# مناطق آمنة: تُحجب بالنص الحرج (شارة المدة وشريط التقدم)
SAFE_EXCLUDE = {
    "top_right": (0.80, 1.0, 0.0, 0.20),
    "bottom_right": (0.75, 1.0, 0.75, 1.0),
}


# ---------------------------------------------------------------- الخطوط
def font(family: str, px: int) -> ImageFont.FreeTypeFont:
    """'display' = Amiri Bold (نسخي) · 'sans_b' · 'sans_m' · 'sans_r'."""
    path = {
        "display": _FONTS / "Amiri-Bold.ttf",
        "sans_b": _FONTS / "IBMPlexSansArabic-Bold.ttf",
        "sans_m": _FONTS / "IBMPlexSansArabic-Medium.ttf",
        "sans_r": _FONTS / "IBMPlexSansArabic-Regular.ttf",
    }[family]
    return G.font(str(path), px)


def ladder_fonts(k: float = 1.0) -> dict[str, ImageFont.FreeTypeFont]:
    L = LADDER.scale(k)
    return {
        "h1": font("sans_b", L.h1),
        "h2": font("display", L.h2),
        "badge": font("sans_b", L.badge),
        "bridge": font("sans_r", L.bridge),
        "name": font("sans_m", L.name),
        "kicker": font("sans_m", L.kicker),
        "series": font("sans_m", L.series),
    }


def fit_width(text: str, family: str, max_w: int, start_px: int,
              floor_px: int = 18) -> ImageFont.FreeTypeFont:
    """يُصغّر حتى يدخل العرض — يمنع خروج العربية من الإطار على اليسار."""
    px = start_px
    while px > floor_px and G.text_w(font(family, px), text) > max_w:
        px -= 2
    return font(family, px)


# ---------------------------------------------------------------- الإطار
def frame3(im: Image.Image, scale: float | None = None, *,
           signature: bool = True) -> Image.Image:
    """الإطار الثلاثي: خارجي ذهبي → شعرة بيضاء → أقواس زوايا.

    scale=None ⇒ يُعاير على الضلع الأقصر (1280) تلقائيًا.
    """
    W, H = im.size
    f = TOKENS.scale(scale) if scale is not None else TOKENS.scale(min(W, H) / 1280)
    d = ImageDraw.Draw(im, "RGBA")

    # 1) الإطار الخارجي — سميك نسبيًا، هو الوحيد الذي ينجو عند 168px
    d.rectangle([f.outer_inset, f.outer_inset,
                 W - 1 - f.outer_inset, H - 1 - f.outer_inset],
                outline=COLORS["champagne"] + (225,), width=f.outer_w)

    # 2) الشعرة البيضاء — أضعف وضوحًا، نسيج لا إشارة
    d.rectangle([f.hair_inset, f.hair_inset,
                 W - 1 - f.hair_inset, H - 1 - f.hair_inset],
                outline=COLORS["hairline"] + (150,), width=f.hair_w)

    # 3) أقواس الزوايا — زوايا فقط، لا صندوق كامل
    i, arm, bw = f.bracket_inset, f.bracket_arm, f.bracket_w
    c = COLORS["champagne"] + (245,)
    x0, y0, x1, y1 = i, i, W - 1 - i, H - 1 - i
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1),
                             (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([(cx, cy), (cx + sx * arm, cy)], fill=c, width=bw)
        d.line([(cx, cy), (cx, cy + sy * arm)], fill=c, width=bw)

    # 4) خط التوقيع — أسفل-يسار فقط (يكسر التماثل)
    if signature:
        sx = f.sig_x
        sy = H - f.sig_y_from_bottom
        d.line([(sx, sy), (sx + f.sig_len, sy)],
               fill=COLORS["gold_rule"] + (215,), width=f.sig_w)
    return im


# ---------------------------------------------------------------- الشارة 3D
def badge3d(im: Image.Image, text: str, centre: tuple[int, int], *,
            px: int | None = None, pad_x: int = 22, pad_y: int = 12,
            radius: int = 12) -> tuple[int, int, int, int]:
    """شارة مستطيلة «ثلاثية الأبعاد»: قاعدة داكنة مُزاحة + إطار ذهبي + ظل ناعم.

    الظل على طبقة منفصلة ⇒ لا يلمس الوجه. تُعيد الـbox للاستخدام كمرجع.
    """
    px = px or LADDER.badge
    fnt = font("sans_b", px)
    s = G.ar(text)
    tw, th = G.text_w(fnt, text), px
    w, h = tw + pad_x * 2, th + pad_y * 2
    cx, cy = centre
    box = (cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2)

    # ظل ناعم
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(
        [box[0], box[1] + 6, box[2], box[3] + 6], radius=radius,
        fill=(0, 0, 0, 115))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12))) if im.mode == "RGBA" \
        else im.paste(Image.new("RGB", im.size, (0, 0, 0)), (0, 0),
                      sh.filter(ImageFilter.GaussianBlur(12)).split()[-1])

    d = ImageDraw.Draw(im, "RGBA")
    # طبقة القاعدة (أسود مُزاح 2.5px للأسفل)
    d.rounded_rectangle([box[0], box[1] + 2, box[2], box[3] + 2],
                        radius=radius, fill=COLORS["ink"] + (205,))
    # الوجه الذهبي فوقها
    d.rounded_rectangle(box, radius=radius, outline=COLORS["champagne"] + (240,),
                        width=2)
    d.rounded_rectangle([box[0] + 4, box[1] + 4, box[2] - 4, box[3] - 4],
                        radius=max(2, radius - 4), outline=COLORS["champagne"] + (90,),
                        width=1)
    # النص — يُرفع قليلًا حتى لا تلمس النقاط (ي) الحدّ السفلي
    d.text((cx, cy - int(px * 0.06)), s, font=fnt,
           fill=COLORS["white"] + (255,), anchor="mm")
    return box


def rule(im: Image.Image, xy: tuple[int, int], *, length: int | None = None,
         thickness: int | None = None) -> None:
    """مسطرة عنوان — أقصر من الكلمتين، وتُكمل خط النظر نحو الشارة."""
    a = LADDER
    length = length or a.rule_w
    thickness = thickness or a.rule_h
    x, y = xy
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([x - length, y, x, y + thickness],
                fill=COLORS["gold_rule"] + (235,))


# ---------------------------------------------------------------- الخلفية
def protect_face_box(size: tuple[int, int], box: tuple[float, float, float, float]
                     ) -> Image.Image:
    """قناع: أبيض = اسمح بالتعتيم، أسود = احمِ الوجه. box نسبية (l,t,r,b)."""
    W, H = size
    l, t, r, b = (int(box[0] * W), int(box[1] * H), int(box[2] * W), int(box[3] * H))
    m = Image.new("L", size, 255)
    ImageDraw.Draw(m).rectangle([l, t, r, b], fill=0)
    return m.filter(ImageFilter.GaussianBlur(60))


def shade_away_from_face(im: Image.Image, side: str, strength: int,
                         face_box: tuple[float, float, float, float]) -> Image.Image:
    """تعريض اتجاهي على الخلفية مع حماية مستطيل الوجه (لا ضباب على الوجه)."""
    W, H = im.size
    ramp = Image.new("L", (W, H), 0)
    px = ramp.load()
    for x in range(W):
        t = x / (W - 1)
        v = (1 - t) if side == "left" else t
        v = max(0.0, min(1.0, (v - 0.35) / 0.65))
        for y in range(H):
            px[x, y] = int(strength * v * v)
    mask = Image.composite(ramp, Image.new("L", (W, H), 0), protect_face_box((W, H), face_box))
    dark = Image.new("RGB", (W, H), (10, 9, 8))
    return Image.composite(dark, im, mask.point(lambda v: int(v * 0.92)))


def qc_thumb(im: Image.Image, out: str | None = None) -> Image.Image | None:
    """اختبار الإبهام: 168px ثم تكبير — الحكم على نقطة التركيز الواحدة."""
    small = im.resize((168, int(168 * im.height / im.width)), Image.LANCZOS)
    big = small.resize(im.size, Image.NEAREST)
    if out:
        big.save(out)
    return big


if __name__ == "__main__":
    print("champagne", "#%02X%02X%02X" % COLORS["champagne"])
    print("frame(1280)", TOKENS)
    print("ladder 1080x1920", LADDER.scale(1.5))
