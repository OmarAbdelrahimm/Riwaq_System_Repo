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


def draw_ink(im: Image.Image, text: str, fnt, right: int, top: int, fill,
             layer: ImageDraw.ImageDraw | None = None) -> int:
    """يرسم النص بحيث تكون **حافة الحبر** اليمنى عند right وأعلاه عند top.

    يُرجع أسفل الحبر — أي أن السطر التالي يبدأ من هنا بالضبط.
    """
    w, h, x0, y0 = ink_size(text, fnt)
    d = layer or ImageDraw.Draw(im, "RGBA")
    d.text((right - (x0 + w), top - y0), G.ar(text), font=fnt, fill=fill, anchor="ls")
    return top + h


_INK_CACHE: dict[tuple, tuple[int, int, int, int]] = {}


def ink_size(text: str, fnt) -> tuple[int, int, int, int]:
    """(العرض، الارتفاع، x0، y0) لحبر النص **المرئي** فعلًا.

    getbbox في Pillow يُرجع أطول ascender/descender في الخط (+40% مع Amiri)،
    لذلك نرسم على قناع ونقيس البكسلات؛ الـx0/y0 إزاحتان من نقطة خط الأساس.
    """
    key = (text, getattr(fnt, "size", 0), getattr(fnt, "path", ""))
    if key in _INK_CACHE:
        return _INK_CACHE[key]
    probe = Image.new("L", (2600, 700), 0)
    ImageDraw.Draw(probe).text((120, 500), G.ar(text), font=fnt, fill=255, anchor="ls")
    box = probe.getbbox()
    res = (0, 0, 0, 0) if box is None else (box[2] - box[0], box[3] - box[1],
                                            box[0] - 120, box[1] - 500)
    _INK_CACHE[key] = res
    return res


def fit_width(text: str, family: str, max_w: int, start_px: int,
              floor_px: int = 18) -> ImageFont.FreeTypeFont:
    """يُصغّر حتى يدخل العرض — يمنع خروج العربية من الإطار على اليسار.

    القياس على النص **المُشكَّل** (بعد reshaper+bidi) وإلا كان القياس خاطئًا.
    """
    px = start_px
    while px > floor_px and G.text_w(font(family, px), G.ar(text)) > max_w:
        px -= 2
    return font(family, px)


def measure(text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int, int]:
    """(العرض، الارتفاع الفعلي للحروف، أعلى الحدّ) — للحروف العربية بعد التشكيل."""
    b = fnt.getbbox(G.ar(text))
    return b[2] - b[0], b[3] - b[1], b[1]


# ---------------------------------------------------------------- الإطار
def frame3(im: Image.Image, scale: float | None = None, *,
           signature: bool = True, bevel: bool = True,
           opaque: bool = True, thick: bool = False) -> Image.Image:
    """الإطار الثلاثي: خارجي ذهبي → شعرة بيضاء → أقواس زوايا.

    bevel=True   ⇒ حدّ فاتح فوق وحدّ داكن تحت على نفس الحافة = عمق 1px بلا أي توهّج.
    opaque=True  ⇒ ألوان صريحة (بلا شفافية) — هي الفرق بين «فخم» و«باهت».
    thick=True   ⇒ سُمك 3px بدل 2px للإطار الخارجي والأقواس (يبقى مقروءًا عند التصغير).
    scale=None   ⇒ يُعاير على الضلع الأقصر مقابل 720 (مرجع 1280×720).
    """
    W, H = im.size
    # ⚠️ المرجع 1280×720 وضلعه الأقصر 720 — القسمة على 1280 كانت تُصغّر الإطار
    # إلى 56% وتُنتج إطارًا باهتًا (خطأ حقيقي اكتُشف بمقارنة البكسل).
    f = TOKENS.scale(scale) if scale is not None else TOKENS.scale(min(W, H) / 720)
    d = ImageDraw.Draw(im, "RGBA")
    k = max(1, round(min(W, H) / 1280))
    ow = (3 if thick else 2) * (1 if min(W, H) >= 1000 else 1)
    bw = (3 if thick else 2) * 1
    hi = (255, 246, 226)          # حدّ الإضاءة (أعلى/يسار)
    lo = (0, 0, 0)                # حدّ الظل (أسفل/يمين)
    gold = COLORS["champagne"] + ((255,) if opaque else (225,))
    gold_soft = COLORS["champagne"] + ((235,) if opaque else (200,))

    def rect(inset: int, width: int, colour):
        d.rectangle([inset, inset, W - 1 - inset, H - 1 - inset],
                    outline=colour, width=width)

    # 1) الإطار الخارجي + bevel: الظل داخل الحافة، الإضاءة خارجها
    if bevel:
        rect(f.outer_inset + ow, 1, lo + (110,))
        rect(f.outer_inset - 1, 1, hi + (120,))
    rect(f.outer_inset, ow, gold)

    # 2) الشعرة البيضاء — أضعف وضوحًا، نسيج لا إشارة
    rect(f.hair_inset, f.hair_w, COLORS["hairline"] + (150,))

    # 3) أقواس الزوايا — زوايا فقط، لا صندوق كامل
    i, arm = f.bracket_inset, f.bracket_arm
    x0, y0, x1, y1 = i, i, W - 1 - i, H - 1 - i
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1),
                             (x0, y1, 1, -1), (x1, y1, -1, -1)):
        if bevel:   # ظل داخلي ثم إضاءة خارجية
            d.line([(cx + sx * 1, cy + sy * 1), (cx + sx * arm, cy + sy * 1)],
                   fill=hi + (110,), width=1)
            d.line([(cx + sx * 1, cy + sy * 1), (cx + sx * 1, cy + sy * arm)],
                   fill=hi + (110,), width=1)
        d.line([(cx, cy), (cx + sx * arm, cy)], fill=gold_soft, width=bw)
        d.line([(cx, cy), (cx, cy + sy * arm)], fill=gold_soft, width=bw)

    # 4) خط التوقيع — أسفل-يسار فقط (يكسر التماثل)
    if signature:
        sx = f.sig_x
        sy = H - f.sig_y_from_bottom
        sw = max(f.sig_w, 2 if thick else f.sig_w)
        d.line([(sx, sy), (sx + f.sig_len, sy)],
               fill=COLORS["gold_rule"] + ((245,) if opaque else (215,)), width=sw)
        if bevel:
            d.line([(sx, sy - 1), (sx + f.sig_len, sy - 1)], fill=hi + (90,), width=1)
    return im


def series_badge(im: Image.Image, text: str, *, corner: str = "tr",
                 px: int = 18, pad: tuple[int, int] = (14, 7)) -> tuple[int, int, int, int]:
    """شارة السلسلة داخل زاوية الإطار (لا في السفل-يمين: يوتيوب يطبع شارة المدة فوقها).

    corner: "tr" أعلى-يمين (الموصى به) · "bl" أسفل-يسار (مكان المرجع الأصلي) · "br" (مخاطرة).
    """
    fnt = font("sans_m", px)
    tw = G.text_w(fnt, G.ar(text))
    w, h = tw + pad[0] * 2, px + pad[1] * 2
    # يُزاح داخل الأقواس: لا يلمس قوس الزاوية ولا الإطار (كان يتقاطع معهما)
    clear = TOKENS.bracket_inset + TOKENS.bracket_arm + 14      # = 74 على 1280×720
    if corner == "tr":
        x1, y1 = im.size[0] - clear, clear
        box = (x1 - w, y1, x1, y1 + h)
    elif corner == "bl":
        x0, y0 = clear, im.size[1] - clear - h
        box = (x0, y0, x0 + w, y0 + h)
    else:   # br — يوتيوب قد يغطّيه بشارة المدة
        x1, y1 = im.size[0] - clear, im.size[1] - clear - h
        box = (x1 - w, y1, x1, y1 + h)
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle(box, radius=h // 2, fill=(8, 7, 6, 170),
                        outline=COLORS["champagne"] + (235,), width=1)
    d.text(((box[0] + box[2]) // 2, (box[1] + box[3]) // 2 - 1), G.ar(text),
           font=fnt, fill=COLORS["champagne"] + (250,), anchor="mm")
    return box


# ---------------------------------------------------------------- الإطار القديم (المعتمد)
# قياسات مأخوذة بالبكسل من الغلاف القديم المعتمد (1280×720):
#   قوس الزاوية : inset 11 · ذراع 27 · 1px · #C1B193  (خارج الإطار — هذه هي لمسة القديم)
#   الإطار      : inset 16 · 2px  · #C1A269  (ذهبي دافئ أغمق من الشامبانيا)
#   الشعرة      : inset 24 · 1px  · #7B623A  (ذهبي باهت، وليس أبيض)
# + خط التوقيع (الإضافة الوحيدة المطلوبة)
CLASSIC = {
    "bracket_inset": 11, "bracket_arm": 27, "bracket_w": 1,
    "gold_inset": 16, "gold_w": 2, "gold": (0xC1, 0xA2, 0x69),
    "hair_inset": 24, "hair_w": 1, "hair": (0x7B, 0x62, 0x3A),
    "bracket": (0xC1, 0xB1, 0x93),
    "sig_x": 52, "sig_len": 91, "sig_from_bottom": 78, "sig_w": 2,
    "sig": (0xBF, 0xAF, 0x8F),
}


def frame_classic(im: Image.Image, *, signature: bool = True,
                  scale: float | None = None) -> Image.Image:
    """الإطار القديم المعتمد حرفيًا + خط التوقيع. لا bevel، لا أقواس داخلية."""
    W, H = im.size
    k = scale if scale is not None else min(W, H) / 720
    q = lambda v: max(1, int(round(v * k)))  # noqa: E731
    c = CLASSIC
    d = ImageDraw.Draw(im, "RGBA")

    def rect(inset, width, colour, alpha=255):
        d.rectangle([inset, inset, W - 1 - inset, H - 1 - inset],
                    outline=colour + (alpha,), width=width)

    # 1) أقواس الزوايا — رفيعة وخارج الإطار (سمة الإطار القديم)
    bi, arm, bw = q(c["bracket_inset"]), q(c["bracket_arm"]), c["bracket_w"]
    for (cx, cy, sx, sy) in ((bi, bi, 1, 1), (W - 1 - bi, bi, -1, 1),
                             (bi, H - 1 - bi, 1, -1), (W - 1 - bi, H - 1 - bi, -1, -1)):
        d.line([(cx, cy), (cx + sx * arm, cy)], fill=c["bracket"] + (235,), width=bw)
        d.line([(cx, cy), (cx, cy + sy * arm)], fill=c["bracket"] + (235,), width=bw)

    # 2) الإطار الذهبي الدافئ
    rect(q(c["gold_inset"]), c["gold_w"], c["gold"], 255)

    # 3) الشعرة الذهبية الباهتة
    rect(q(c["hair_inset"]), c["hair_w"], c["hair"], 200)

    # 4) خط التوقيع — أسفل-يسار فقط
    if signature:
        sx, sy = q(c["sig_x"]), H - q(c["sig_from_bottom"])
        d.line([(sx, sy), (sx + q(c["sig_len"]), sy)],
               fill=c["sig"] + (240,), width=c["sig_w"])
    return im


# ---------------------------------------------------------------- الشارة 3D
def badge3d(im: Image.Image, text: str, centre: tuple[int, int], *,
            px: int | None = None, pad_x: int = 26, pad_y: int = 14,
            radius: int | None = None) -> tuple[int, int, int, int]:
    """شارة النص الثلاثية الأبعاد — «المستوى الثالث» في سلّم الطباعة.

    طبقاتها (من أسفل لأعلى):
      1) ظل ناعم واسع خارجها        → يفصلها عن الصورة
      2) قاعدة داكنة مُزاحة 2px      → سُمك مرئي
      3) حدّ ذهبي خارجي 2px
      4) حدّ ذهبي داخلي 1px @+5px    → «الذهبي ظاهر فوق وتحت»
      5) النص الأبيض
    الزوايا دائرية بنسبة ~45% من الارتفاع (لا حادّة).
    """
    px = px or LADDER.badge
    fnt = font("sans_b", px)
    s_txt = G.ar(text)
    tw = G.text_w(fnt, s_txt)
    h = px + pad_y * 2
    w = tw + pad_x * 2
    r = radius if radius is not None else max(10, int(h * 0.28))
    cx, cy = centre
    box = (cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2)

    # 1) ظل ناعم واسع — يُركّب كطبقة قناع (يعمل مع RGB و RGBA)
    sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle(
        [box[0] + 1, box[1] + 8, box[2] + 1, box[3] + 9], radius=r, fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    im.paste(Image.new("RGB", im.size, (0, 0, 0)), (0, 0), sh)

    # 2) القاعدة الداكنة مُزاحة للأسفل = سُمك 2px
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle([box[0], box[1] + 2, box[2], box[3] + 2],
                        radius=r, fill=(10, 9, 8, 215))
    # 3) الوجه الداخلي
    d.rounded_rectangle(box, radius=r, fill=(12, 11, 9, 140))
    # 4) الحدّ الذهبي الخارجي
    d.rounded_rectangle(box, radius=r, outline=COLORS["champagne"] + (255,), width=2)
    # 5) الحدّ الذهبي الداخلي (يظهر فوق وتحت)
    inset = 5
    d.rounded_rectangle([box[0] + inset, box[1] + inset, box[2] - inset, box[3] - inset],
                        radius=max(2, r - inset),
                        outline=COLORS["champagne"] + (110,), width=1)
    # 6) النص — يُرفع 2% لأن النقاط العربية تنزل تحت خط الأساس
    d.text((cx, cy - int(px * 0.03)), s_txt, font=fnt,
           fill=COLORS["white"] + (255,), anchor="mm")
    return box


def cover_crop(path: str, W: int, H: int, fx: float = 0.5, fy: float = 0.5,
               zoom: float = 1.0) -> Image.Image:
    """قصّ 16:9 مع تحكّم في نقطة التركيز والتكبير.

    zoom=1.0 ⇒ أوسع كادر ممكن. zoom=1.22 ⇒ اقتراب 22% (الوجه أكبر).
    fx/fy نسبيّان في **الفائض** الذي نُزحزح فيه النافذة: 0.5 = المنتصف،
    0.0 = الحافة الأولى، 1.0 = الحافة الأخيرة.
    (المصدر 4:3 أوسع من 16:9 ⇒ الفائض أفقي كبير، والتحكم في fx هو ما يحرّك البطل.)
    """
    im = Image.open(path).convert("RGB")
    base = max(W / im.width, H / im.height)
    s = base * zoom
    im = im.resize((max(1, int(im.width * s + 0.5)),
                    max(1, int(im.height * s + 0.5))), Image.LANCZOS)
    slack_x = max(0, im.width - W)
    slack_y = max(0, im.height - H)
    x = int(slack_x * fx)
    y = int(slack_y * fy)
    return im.crop((x, y, x + W, y + H))


def grade(im: Image.Image, brightness: float = 1.04, contrast: float = 1.10,
          color: float = 0.96) -> Image.Image:
    """تصحيح لوني محافظ: الخلفية تهدأ قليلًا، البطل يبقى حقيقيًا."""
    from PIL import ImageEnhance
    im = ImageEnhance.Brightness(im).enhance(brightness)
    im = ImageEnhance.Contrast(im).enhance(contrast)
    return ImageEnhance.Color(im).enhance(color)


def text_shadow(base: Image.Image, painter, blur: int = 10,
                offsets=((0, 4), (0, 10), (0, 18)), alpha: int = 210) -> None:
    """ظل نصّي متعدّد الطبقات — يضمن القراءة فوق أي خلفية بلا لوح داكن."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    painter(ImageDraw.Draw(layer))
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", base.size, (0, 0, 0, alpha)), (0, 0), layer.split()[-1])
    for dx, dy in offsets:
        b = sh.filter(ImageFilter.GaussianBlur(blur))
        base.paste(Image.new("RGB", base.size, (0, 0, 0)), (dx, dy), b.split()[-1])
    base.paste(layer, (0, 0), layer)


def lockup(im: Image.Image, width: int = 92, xy: tuple[int, int] = (40, 26)) -> None:
    """شعار رواق أعلى-اليسار — موضع ثابت في كل غلاف."""
    lock = G.brand_lockup(width, color=G.PARCH)
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    layer.alpha_composite(lock, xy)
    text_shadow(im, lambda d: d.bitmap((0, 0), layer.split()[-1],
                                       fill=(255, 255, 255, 255)),
                blur=12, offsets=((0, 4),), alpha=190)
    im.paste(layer, (0, 0), layer)


def pill(im: Image.Image, text: str, centre: tuple[int, int], px: int = 20,
         pad_x: int = 16, pad_y: int = 8, right: int | None = None
         ) -> tuple[int, int, int, int]:
    """كبسولة رقيقة (الشارة التصنيفية) — إطار شامبانيا + نص شامبانيا، بلا تعبئة.

    right= ⇒ تُحاذى حافّتها اليمنى على هذا الإحداثي (يمنع خروجها عن عمود النص).
    """
    fnt = font("sans_m", px)
    tw = G.text_w(fnt, text)
    w, h = tw + pad_x * 2, px + pad_y * 2
    cx, cy = centre
    if right is not None:
        cx = right - w // 2
    box = (cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2)
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle(box, radius=h // 2, fill=(0, 0, 0, 120),
                        outline=COLORS["champagne"] + (225,), width=1)
    d.text((cx, cy - 1), G.ar(text), font=fnt,
           fill=COLORS["champagne"] + (250,), anchor="mm")
    return box


def neq(im: Image.Image, centre: tuple[int, int], size: int,
        color: tuple[int, int, int] | None = None, width: int | None = None) -> None:
    """علامة ≠ مرسومة يدويًا (لا تعتمد على وجود الحرف في الخط)."""
    c = (color or COLORS["champagne"]) + (255,)
    w = width or max(4, size // 9)
    x, y = centre
    d = ImageDraw.Draw(im, "RGBA")
    d.line([(x - size // 2, y - size // 4), (x + size // 2, y - size // 4)], fill=c, width=w)
    d.line([(x - size // 2, y + size // 4), (x + size // 2, y + size // 4)], fill=c, width=w)
    d.line([(x - size // 3, y + size // 3), (x + size // 3, y - size // 3)], fill=c, width=w)


def _ar_text(d, xy, text, fnt, fill, anchor="ra"):
    """نص عربي مُشكَّل الاتجاه — نقطة واحدة للرسم في كل السكربتات."""
    d.text(xy, G.ar(text), font=fnt, fill=fill, anchor=anchor)


def arrow_marker(im: Image.Image, tip: tuple[int, int], size: int,
                 direction: str = "up", width: int | None = None) -> None:
    """سهم نظيف كمؤشّر بصري واحد — يُستخدم بدل السهم الملوّن الضخم."""
    c = COLORS["champagne"] + (245,)
    w = width or max(4, size // 7)
    x, y = tip
    d = ImageDraw.Draw(im, "RGBA")
    if direction == "up":
        d.line([(x, y), (x, y + size)], fill=c, width=w)
        d.line([(x, y), (x - size // 2, y + size // 2)], fill=c, width=w)
        d.line([(x, y), (x + size // 2, y + size // 2)], fill=c, width=w)
    else:
        d.line([(x, y), (x, y - size)], fill=c, width=w)
        d.line([(x, y), (x - size // 2, y - size // 2)], fill=c, width=w)
        d.line([(x, y), (x + size // 2, y - size // 2)], fill=c, width=w)


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
