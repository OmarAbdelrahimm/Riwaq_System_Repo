"""أصول الهوية البصرية لسلسلة رواق (كارت الكابشن، العلامة المائية، بطاقة الختام، الأغلفة)."""
from __future__ import annotations

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_DIR = "/home/user/Riwaq_System_Repo/public/fonts"
AMIRI_B = f"{FONT_DIR}/Amiri-Bold.ttf"
AMIRI_R = f"{FONT_DIR}/Amiri-Regular.ttf"
PLEX_B = f"{FONT_DIR}/IBMPlexSansArabic-Bold.ttf"
PLEX_M = f"{FONT_DIR}/IBMPlexSansArabic-Medium.ttf"
PLEX_R = f"{FONT_DIR}/IBMPlexSansArabic-Regular.ttf"

INK = (28, 25, 21)
INK_CARD = (26, 23, 18)
PARCH = (243, 235, 219)
GOLD = (169, 138, 75)
GOLD_L = (194, 164, 105)
PALE = (239, 230, 210)
STONE = (138, 127, 107)


def font(path: str, px: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, px)


def ar(text: str) -> str:
    return get_display(arabic_reshaper.reshape(text))


def text_w(fnt: ImageFont.FreeTypeFont, s: str) -> int:
    b = fnt.getbbox(s)
    return b[2] - b[0]


def text_h(fnt: ImageFont.FreeTypeFont, s: str = "ا") -> int:
    b = fnt.getbbox(s)
    return b[3] - b[1]


def draw_ar(d: ImageDraw.ImageDraw, xy, s: str, fnt, fill, anchor="la", **kw):
    d.text(xy, ar(s), font=fnt, fill=fill, anchor=anchor, **kw)


def brand_mark(size_px: int, color=GOLD_L, jewel=GOLD_L) -> Image.Image:
    """قوس رواق + الجوهرة — نفس هندسة العلامة الأصلية (إطار 111.48×104.98)."""
    ss = 4
    W = int(size_px * ss)
    H = int(round(size_px * 104.98 / 111.48 * ss))
    k = W / 111.48

    def X(x):
        return (x - 4.26) * k

    def Y(y):
        return (y - 8.76) * k

    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    # القوس الخارجي: ساقان + قبة بيضاوية (72 عرضًا، 42 ارتفاعًا)
    md.rectangle([X(24), Y(37), X(96), Y(104)], fill=255)
    md.ellipse([X(24), Y(16), X(96), Y(58) + (Y(58) - Y(37))], fill=255)
    # تفريغ الباطن
    md.rectangle([X(37), Y(44), X(83), Y(104)], fill=0)
    md.ellipse([X(37), Y(31), X(83), Y(58) + (Y(58) - Y(44))], fill=0)
    # القاعدة
    md.rounded_rectangle([X(14), Y(100.4), X(106), Y(105.6)], radius=2.4 * k, fill=255)
    # الجوهرة (دائرة)
    r = 6.6 * k
    md.ellipse([X(60) - r, Y(66) - r, X(60) + r, Y(66) + r], fill=255)

    # تنعيم الزوايا الداخلية كما في العلامة الأصلية
    mask = mask.filter(ImageFilter.GaussianBlur(radius=max(1.0, k * 1.15)))
    mask = mask.point(lambda v: 255 if v > 110 else 0)
    base = mask.resize((max(1, int(round(W / ss))), max(1, int(round(H / ss)))), Image.LANCZOS)
    out = Image.new("RGBA", base.size, (0, 0, 0, 0))
    out = Image.composite(Image.new("RGBA", base.size, color + (255,)), out, base)
    return out


def brand_lockup(width_px: int, color=PARCH, tagline="تَارِيخْ وَتُرَاث", jewel=GOLD_L) -> Image.Image:
    """الشعار الرأسي: رمز + «رِواق» + «تاريخ وتراث» — بتباعد محسوب من صناديق النص."""
    mark = brand_mark(int(width_px * 0.62), color=color, jewel=jewel)
    f1 = font(AMIRI_B, int(width_px * 0.36))
    f2 = font(AMIRI_R, int(width_px * 0.135))
    b1 = f1.getbbox(ar("رِواق"))
    b2 = f2.getbbox(ar(tagline))
    h1, h2 = b1[3] - b1[1], b2[3] - b2[1]
    w1, w2 = b1[2] - b1[0], b2[2] - b2[0]
    gap1 = int(width_px * 0.02)
    gap2 = int(width_px * 0.012)
    W = max(mark.width, w1, w2)
    H = mark.height + gap1 + h1 + gap2 + h2 + 6
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    img.paste(mark, ((W - mark.width) // 2, 0), mark)
    y = mark.height + gap1
    draw_ar(d, ((W - w1) // 2 - b1[0], y - b1[1]), "رِواق", f1, color + (255,))
    y += h1 + gap2
    draw_ar(d, ((W - w2) // 2 - b2[0], y - b2[1]), tagline, f2, STONE + (255,))
    return img


def caption_card(W=1920, H=1080) -> Image.Image:
    """كارت الكابشن — يغطي كارتهم القديم (فيُخفي نصّهم) بنفس لغة الإطار الذهبي."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 239, 935, 1680, 1052
    d.rounded_rectangle([x0, y0, x1, y1], radius=9, fill=INK_CARD + (255,),
                        outline=GOLD + (120,), width=2)
    d.line([x0 + 22, y0 + 1, x1 - 22, y0 + 1], fill=GOLD_L + (70,), width=1)
    d.line([x0 + 22, y1 - 1, x1 - 22, y1 - 1], fill=GOLD_L + (60,), width=1)
    return img


def watermark_bug(height_px=104, width_px=None) -> Image.Image:
    """علامة مائية صغيرة (شعار + «رواق») منخفضة الوضوح، تُعرض كل 30 ثانية."""
    mark = brand_mark(int(height_px * 0.80), color=PALE, jewel=GOLD_L)
    f = font(AMIRI_B, int(height_px * 0.60))
    word = "رِواق"
    b = f.getbbox(ar(word))
    ww, hh = b[2] - b[0], b[3] - b[1]
    gap = int(height_px * 0.14)
    W = mark.width + gap + ww + 10
    H = max(mark.height, hh) + int(height_px * 0.24)
    core = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(core)
    core.paste(mark, (0, (H - mark.height) // 2), mark)
    draw_ar(d, (mark.width + gap - b[0], (H - hh) // 2 - b[1]), word, f, PALE + (240,))
    # ظل ناعم أسفل العنصر لضمان القراءة فوق الصورة
    pad = 6
    sh = Image.new("RGBA", (W + 2 * pad, H + 2 * pad), (0, 0, 0, 0))
    sh.paste(core, (pad, pad), core)
    sh = sh.filter(ImageFilter.GaussianBlur(4))
    out = Image.new("RGBA", sh.size, (0, 0, 0, 0))
    dark = Image.new("RGBA", sh.size, (8, 7, 6, 160))
    out = Image.composite(dark, out, sh.split()[3])
    out.alpha_composite(core, (pad, pad))
    a = out.split()[3].point(lambda v: int(v * 0.58))
    out.putalpha(a)
    if width_px:
        hh2 = int(out.height * width_px / out.width)
        out = out.resize((width_px, hh2), Image.LANCZOS)
    return out


def ident_lockup(W=1920, H=1080) -> Image.Image:
    """معرّف البداية: تعتيم خفيف لكامل الإطار + شعار رواق في المنتصف (يظهر ~1.6 ثانية)."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    veil = Image.new("RGBA", (W, H), (10, 9, 7, 118))
    img.alpha_composite(veil)
    lock = brand_lockup(300, color=PARCH, tagline="تَارِيخْ وَتُرَاث")
    # ظل ناعم خلف الشعار لضمان القراءة
    sh = Image.new("RGBA", (lock.width + 120, lock.height + 120), (0, 0, 0, 0))
    sh.paste(lock, (60, 60), lock)
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    sh.putalpha(sh.split()[3].point(lambda v: int(v * 0.55)))
    cx, cy = (W - lock.width) // 2, int(H * 0.30)
    img.alpha_composite(sh, (cx - 60, cy - 60))
    img.alpha_composite(lock, (cx, cy))
    d = ImageDraw.Draw(img)
    y = cy + lock.height + 26
    d.line([(W // 2 - 120, y), (W // 2 + 120, y)], fill=GOLD_L + (200,), width=2)
    return img


def endcard(n: int, total: int, next_title: str | None,
            series="مركزية العلاقة مع الله — ياسر الحزيمي",
            channel="@gallery_of_history", W=1920, H=1080) -> Image.Image:
    """بطاقة ختام 4 ثوانٍ: هوية + ترقيم النشر + الحلقة التالية + دعوة اشتراك."""
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    for y in range(H):
        k = 1 - (y / H) * 0.5
        d.line([(0, y), (W, y)], fill=(int(31 * k) + 9, int(28 * k) + 8, int(23 * k) + 7))
    d.rectangle([70, 58, W - 70, H - 58], outline=GOLD, width=2)
    d.rectangle([86, 74, W - 86, H - 74], outline=(120, 99, 54), width=1)

    lock = brand_lockup(250, color=PARCH)
    img.paste(lock, ((W - lock.width) // 2, 120), lock)

    f_series = font(PLEX_M, 32)
    f_lbl = font(PLEX_R, 27)
    f_next = font(AMIRI_B, 54)
    f_cta = font(PLEX_B, 38)
    f_ch = font(PLEX_M, 28)
    f_num = font(AMIRI_B, 36)

    y = 120 + lock.height + 34
    draw_ar(d, (W // 2, y), series, f_series, (186, 175, 150), anchor="ma")
    y += 52
    d.line([(W // 2 - 210, y), (W // 2 + 210, y)], fill=GOLD, width=2)
    y += 26
    draw_ar(d, (W // 2, y), f"الحلقة {n} من {total}", f_num, GOLD_L, anchor="ma")
    y += 58
    if next_title:
        draw_ar(d, (W // 2, y), "الحلقة التالية", f_lbl, (150, 141, 120), anchor="ma")
        y += 40
        draw_ar(d, (W // 2, y), next_title, f_next, PARCH, anchor="ma")
    else:
        draw_ar(d, (W // 2, y), "شاهد بقية السلسلة في القناة", f_next, PARCH, anchor="ma")

    box = [W // 2 - 340, 812, W // 2 + 340, 896]
    d.rounded_rectangle(box, radius=42, outline=GOLD_L, width=2, fill=(58, 48, 30))
    draw_ar(d, (W // 2, (box[1] + box[3]) // 2), "اشترك في القناة وفعّل جرس التنبيه",
            f_cta, PARCH, anchor="mm")
    draw_ar(d, (W // 2, 936), channel, f_ch, (150, 141, 120), anchor="ma")
    draw_ar(d, (W // 2, 968), "رِواق | تاريخ وتراث", font(PLEX_R, 26), (143, 133, 112), anchor="ma")
    return img


def fit_font(path: str, text: str, max_w: int, start_px: int, min_px: int = 24) -> ImageFont.FreeTypeFont:
    px = start_px
    while px > min_px:
        f = font(path, px)
        if text_w(f, ar(text)) <= max_w:
            return f
        px -= 2
    return font(path, min_px)


def wrap_ar(text: str, fnt: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(fnt, ar(t)) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines
