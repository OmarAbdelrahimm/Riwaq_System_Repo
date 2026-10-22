"""b-roll تفسيري بأسلوب «ڤوكس» ثلاثي الأبعاد — مبني بالكامل داخل المستودع (بلا حقوق خارجية).

الفكرة: مشاهد إيزومترية (مكعبات/ألواح/مسارات) مع إضاءة وظلال وعمق، ونصّ عربي يشرح الفكرة،
تُحرَّك بالتكبير البطيء + مسحة ضوء، فتُستخدم كبطاقات b-roll تُغطّي كامل الإطار بين مقاطع الحوار.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import graphics as G  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

W, H = 1920, 1080
SS = 2  # supersampling
INK0 = (16, 14, 12)
INK1 = (34, 29, 23)
GOLD = G.GOLD
GOLD_L = G.GOLD_L
PARCH = G.PARCH
DARK_OBJ = (46, 40, 33)
RED = (150, 58, 46)
BLUE = (54, 78, 96)
SAND = (128, 108, 78)
GREEN = (72, 92, 70)

ISO_C = math.cos(math.radians(30))
ISO_S = math.sin(math.radians(30))


# ---------------------------------------------------------------- helpers
def _grad_bg(glow_xy=(0.5, 0.42), glow_r=0.55, top=INK1, bottom=INK0) -> Image.Image:
    w, h = W * SS, H * SS
    base = Image.new("RGB", (w, h), top)
    d = ImageDraw.Draw(base)
    for y in range(h):
        k = y / h
        c = tuple(int(top[i] + (bottom[i] - top[i]) * k) for i in range(3))
        d.line([(0, y), (w, y)], fill=c)
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx, cy = glow_xy[0] * w, glow_xy[1] * h
    r = glow_r * w
    for i in range(28, 0, -1):
        rr = r * i / 28
        v = int(26 * (1 - i / 28) ** 1.7)
        gd.ellipse([cx - rr, cy - rr * 0.8, cx + rr, cy + rr * 0.8], fill=(v, int(v * 0.86), int(v * 0.66)))
    glow = glow.filter(ImageFilter.GaussianBlur(60 * SS))
    return Image.blend(base, Image.blend(base, glow, 0.85), 0.55)


def _grid(img: Image.Image, horizon=0.52, color=(70, 60, 46), step=64, alpha=58):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    w, h = img.size
    hz = int(h * horizon)
    # خطوط أفقية متقاربة نحو الأفق
    k = 1.0
    y = h
    while y > hz:
        a = int(alpha * (1 - (y - hz) / (h - hz)) ** 0.6 + 10)
        d.line([(0, y), (w, y)], fill=color + (a,), width=SS)
        y -= step * SS * k
        k *= 0.93
    # خطوط عمودية متباعدة
    n = 16
    for i in range(n + 1):
        x0 = int(w * (i / n))
        cx = w / 2
        x1 = int(cx + (x0 - cx) * 2.6)
        d.line([(x0, h), (x1, hz)], fill=color + (int(alpha * 0.55),), width=SS)
    img.alpha_composite(ov) if img.mode == "RGBA" else img.paste(ov, (0, 0), ov)
    return img


def _iso(x, y, z, s=1.0, ox=W * SS / 2, oy=H * SS * 0.62):
    sx = (x - y) * ISO_C * s + ox
    sy = (x + y) * ISO_S * s - z * s + oy
    return sx, sy


def _shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def box(d: ImageDraw.ImageDraw, x, y, z, w, dp, h, s, color, outline=None, ox=None, oy=None):
    """مكعّب إيزومتري بأوجه مظللة (سفلي/يمين/يسار)."""
    kw = {}
    if ox is not None:
        kw = {"ox": ox, "oy": oy}
    p = lambda dx, dy, dz: _iso(x + dx, y + dy, z + dz, s, **kw)  # noqa: E731
    top = [p(0, 0, h), p(w, 0, h), p(w, dp, h), p(0, dp, h)]
    left = [p(0, dp, h), p(w, dp, h), p(w, dp, 0), p(0, dp, 0)]
    right = [p(w, 0, h), p(w, dp, h), p(w, dp, 0), p(w, 0, 0)]
    d.polygon(left, fill=_shade(color, 0.62), outline=outline)
    d.polygon(right, fill=_shade(color, 0.82), outline=outline)
    d.polygon(top, fill=_shade(color, 1.12), outline=outline)


def shadow(img: Image.Image, xy, w, h, blur=26, alpha=120):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.ellipse([xy[0] - w / 2, xy[1] - h / 2, xy[0] + w / 2, xy[1] + h / 2], fill=(0, 0, 0, alpha))
    ov = ov.filter(ImageFilter.GaussianBlur(blur * SS))
    img.alpha_composite(ov)


def glow_spot(img: Image.Image, xy, r, color=GOLD_L, alpha=70):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for i in range(12, 0, -1):
        rr = r * i / 12
        a = int(alpha * (1 - i / 12) ** 1.6)
        d.ellipse([xy[0] - rr, xy[1] - rr, xy[0] + rr, xy[1] + rr], fill=color + (a,))
    ov = ov.filter(ImageFilter.GaussianBlur(r * 0.06 + 6 * SS))
    img.alpha_composite(ov)


def chip(d: ImageDraw.ImageDraw, anchor, text, target, fnt, side="right", color=GOLD_L):
    """لصيقة نصية بخط قائد يصلها بالمجسم."""
    tw = G.text_w(fnt, G.ar(text))
    pad = 18 * SS
    bw, bh = tw + 2 * pad, int(fnt.size * 1.7)
    ax, ay = anchor
    bx = ax + (34 * SS if side == "right" else -34 * SS - bw)
    by = ay - bh / 2
    d.line([(ax, ay), (bx if side == "right" else bx + bw, by + bh / 2)],
           fill=color + (150,), width=max(1, 2 * SS))
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=bh // 2,
                        fill=(24, 21, 17, 210), outline=color + (170,), width=max(1, 2 * SS))
    G.draw_ar(d, (bx + bw / 2, by + bh / 2), text, fnt, PARCH, anchor="mm")


# ---------------------------------------------------------------- scenes
def scene_house(d, img, s, palette):
    """بيت مفتوح تدخل إليه مكعبات صغيرة داكنة."""
    ox, oy = W * SS * 0.52, H * SS * 0.70
    shadow(img, (ox, oy + 10 * SS), 900 * SS, 150 * SS, blur=20, alpha=110)
    box(d, -3, -3, 0, 6, 6, 4.6, s, palette["wall"], ox=ox, oy=oy)
    # فتحة الباب
    d.polygon([_iso(-0.6, 3.02, 4.2, s, ox, oy), _iso(1.4, 3.02, 4.2, s, ox, oy),
               _iso(1.4, 3.02, 0, s, ox, oy), _iso(-0.6, 3.02, 0, s, ox, oy)],
              fill=(12, 10, 9))
    # مكعبات دخول
    for i, (bx, by, bz, sz) in enumerate([(-4.2, 2.2, 0, 0.9), (-3.4, 4.0, 0, 0.7), (5.0, 1.0, 0, 1.0)]):
        box(d, bx, by, bz, sz, sz, sz, s, DARK_OBJ, ox=ox, oy=oy)
        glow_spot(img, _iso(bx + sz / 2, by + sz / 2, bz + sz / 2, s, ox, oy), 60 * SS, RED, 40)


def scene_conference(d, img, s, palette):
    """طاولة مستديرة وحولها مكعبات — مؤتمر يومي."""
    ox, oy = W * SS * 0.50, H * SS * 0.72
    shadow(img, (ox, oy + 8 * SS), 980 * SS, 170 * SS, blur=22, alpha=120)
    # قاعدة
    box(d, -1.2, -1.2, 0, 2.4, 2.4, 0.9, s, palette["base"], ox=ox, oy=oy)
    # قرص
    top = Image.new("RGBA", img.size, (0, 0, 0, 0))
    td = ImageDraw.Draw(top)
    cx, cy = _iso(0, 0, 2.4, s, ox, oy)
    rw, rh = 2.9 * s * ISO_C * 2.0, 2.9 * s * 0.82
    td.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=palette["table"] + (255,))
    td.ellipse([cx - rw * 0.86, cy - rh * 0.86, cx + rw * 0.86, cy + rh * 0.86],
               fill=_shade(palette["table"], 1.15) + (255,))
    img.alpha_composite(top)
    for a in range(0, 360, 60):
        bx = 1.7 * math.cos(math.radians(a)) - 0.3
        by = 1.7 * math.sin(math.radians(a)) - 0.3
        box(d, bx, by, 2.4, 0.6, 0.6, 0.6, s, DARK_OBJ, ox=ox, oy=oy)
    box(d, -0.45, -0.45, 2.4, 0.9, 0.9, 0.9, s, palette["seats"], ox=ox, oy=oy)


def scene_gap(d, img, s, palette):
    """كتلتان تُفصلان بوتد — التفريق بين اثنين."""
    ox, oy = W * SS * 0.50, H * SS * 0.70
    shadow(img, (ox, oy + 12 * SS), 900 * SS, 150 * SS, blur=20, alpha=110)
    box(d, -4.4, -1.4, 0, 2.6, 2.8, 2.6, s, palette["a"], ox=ox, oy=oy)
    box(d, 1.8, -1.4, 0, 2.6, 2.8, 2.6, s, palette["b"], ox=ox, oy=oy)
    # شظايا بين الكتلتين (أثر التفريق)
    for i, (bx, bz, sz) in enumerate([(-0.9, 2.4, 0.55), (-0.2, 1.2, 0.4), (0.5, 2.9, 0.65), (-0.6, 0.4, 0.3)]):
        box(d, bx, -0.9 + i * 0.35, bz, sz, sz, sz, s, RED, ox=ox, oy=oy)
        glow_spot(img, _iso(bx, -0.7, bz + sz / 2, s, ox, oy), 55 * SS, RED, 45)


def scene_network(d, img, s, palette):
    """عقدة مركزية وحولها عقد — الشبكة/كلام الناس."""
    ox, oy = W * SS * 0.50, H * SS * 0.68
    shadow(img, (ox, oy + 10 * SS), 940 * SS, 160 * SS, blur=22, alpha=110)
    pts = []
    for i in range(8):
        a = math.radians(i * 45)
        x, y = 5.2 * math.cos(a), 5.2 * math.sin(a)
        pts.append((x, y))
    for x, y in pts:
        d.line([_iso(0, 0, 2.2, s, ox, oy), _iso(x, y, 0.9, s, ox, oy)],
               fill=palette["edge"] + (120,), width=max(1, int(2 * SS)))
    for i, (x, y) in enumerate(pts):
        col = palette["seats"] if i % 2 else DARK_OBJ
        box(d, x - 0.5, y - 0.5, 0, 1.0, 1.0, 1.0, s, col, ox=ox, oy=oy)
    box(d, -1.1, -1.1, 0, 2.2, 2.2, 3.0, s, palette["base"], ox=ox, oy=oy)
    glow_spot(img, _iso(0, 0, 3.2, s, ox, oy), 120 * SS, GOLD_L, 60)


def scene_road(d, img, s, palette):
    """طريق إيزومتري + لوحات إرشادية + سيارة."""
    ox, oy = W * SS * 0.62, H * SS * 0.74
    # شريط الطريق
    d.polygon([_iso(-1.6, -9, 0, s, ox, oy), _iso(1.6, -9, 0, s, ox, oy),
               _iso(1.6, 9, 0, s, ox, oy), _iso(-1.6, 9, 0, s, ox, oy)],
              fill=palette["road"])
    for y in range(-8, 9, 2):
        d.polygon([_iso(-0.12, y, 0.02, s, ox, oy), _iso(0.12, y, 0.02, s, ox, oy),
                   _iso(0.12, y + 1.0, 0.02, s, ox, oy), _iso(-0.12, y + 1.0, 0.02, s, ox, oy)],
                  fill=(190, 180, 158))
    # لوحات
    for i, yy in enumerate((-5.0, -0.5)):
        box(d, -3.4, yy, 0, 0.18, 0.18, 1.8, s, (90, 80, 64), ox=ox, oy=oy)
        box(d, -4.3, yy - 0.08, 1.7, 1.9, 0.14, 0.85, s, palette["sign"], ox=ox, oy=oy)
    # سيارة (مكعبان)
    box(d, 0.6, -2.2, 0, 1.5, 2.6, 0.7, s, palette["car"], ox=ox, oy=oy)
    box(d, 0.85, -1.7, 0.7, 1.0, 1.5, 0.6, s, _shade(palette["car"], 1.25), ox=ox, oy=oy)
    glow_spot(img, _iso(1.2, -1.0, 0.8, s, ox, oy), 90 * SS, GOLD_L, 45)


def scene_ropes(d, img, s, palette):
    """حبلان: صاعد إلى السماء ونازل منها."""
    ox, oy = W * SS * 0.50, H * SS * 0.78
    box(d, -5, -1.2, 0, 10, 2.4, 0.5, s, palette["base"], ox=ox, oy=oy)
    for i, (x, col, up) in enumerate(((-2.2, GOLD_L, True), (2.2, BLUE, False))):
        top = _iso(x, 0, 9.5 if up else 0.5, s, ox, oy)
        bot = _iso(x, 0, 0.5 if up else 9.5, s, ox, oy)
        d.line([top, bot], fill=col + (235,), width=max(2, int(4 * SS)))
        for k in range(1, 7):
            t = k / 7
            px = top[0] + (bot[0] - top[0]) * t
            py = top[1] + (bot[1] - top[1]) * t
            r = 5 * SS
            d.ellipse([px - r, py - r, px + r, py + r], fill=col + (255,))
        glow_spot(img, (top[0], top[1]), 110 * SS, col, 55)


def scene_balance(d, img, s, palette):
    """ميزان: كفّتان، إحداهما ترجح — العبادات والتعاملات."""
    ox, oy = W * SS * 0.50, H * SS * 0.72
    shadow(img, (ox, oy + 10 * SS), 820 * SS, 140 * SS, blur=18, alpha=110)
    box(d, -1.5, -1.5, 0, 3.0, 3.0, 0.35, s, _shade(palette["base"], 0.8), ox=ox, oy=oy)
    box(d, -0.45, -0.45, 0.35, 0.9, 0.9, 4.85, s, palette["base"], ox=ox, oy=oy)
    px, py = _iso(0, 0, 5.2, s, ox, oy)

    arm = 5.0 * s * ISO_C
    d.line([(px - arm, py), (px + arm, py)], fill=GOLD_L + (240,), width=max(2, int(3 * SS)))
    for side, col, drop in ((-1, GREEN, 0.0), (1, RED, 1.7)):
        ex = px + side * arm
        ey = py + drop * s * 0.5
        d.line([(ex, py), (ex, ey - 12 * SS)], fill=(150, 138, 116, 220), width=max(1, int(2 * SS)))
        # كفّة: قطع ناقص مزدوج يعطي إحساس الصحن
        rw, rh = 74 * SS, 20 * SS
        d.ellipse([ex - rw, ey - rh, ex + rw, ey + rh], fill=_shade(col, 0.55) + (255,))
        d.ellipse([ex - rw, ey - rh - 9 * SS, ex + rw, ey + rh - 9 * SS], fill=col + (255,))
        d.arc([ex - rw, ey - rh - 9 * SS, ex + rw, ey + rh - 9 * SS], 0, 180,
              fill=_shade(col, 1.35) + (255,), width=max(1, 2 * SS))
        # ثقل فوق الكفّة
        bw = 0.9 if side < 0 else 1.25
        bx = (ex - W * SS * 0.085) / (ISO_C * s) / 1.0
        # نرسم المكعّب بإحداثيات العالم ثم نرفعه فوق الكفّة
        cxx = (ex - ox) / (ISO_C * s) / 2.0 if False else 0
        box(d, -bw / 2 - 0.0, -bw / 2, 0, bw, bw, bw, s, col,
            ox=ex, oy=ey - 14 * SS)


def scene_vessel(d, img, s, palette):
    """شبكة أوعية دموية متفرعة يجري فيها مكعب داكن."""
    ox, oy = W * SS * 0.50, H * SS * 0.60
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    root = _iso(0, 0, 0, s, ox, oy)
    branches = [(-6, -2), (-4, -5), (5, -3), (7, 2), (3, 5), (-3, 6)]
    for bx, by in branches:
        mid = ((root[0] + _iso(bx, by, 0, s, ox, oy)[0]) / 2,
               (root[1] + _iso(bx, by, 0, s, ox, oy)[1]) / 2 - 26 * SS)
        od.line([root, mid], fill=(168, 66, 54, 255), width=max(3, int(9 * SS)), joint="curve")
        od.line([mid, _iso(bx, by, 0, s, ox, oy)], fill=(140, 50, 42, 255), width=max(2, int(6 * SS)), joint="curve")
        for k in (0.35, 0.7):
            px = root[0] + (_iso(bx, by, 0, s, ox, oy)[0] - root[0]) * k
            py = root[1] + (_iso(bx, by, 0, s, ox, oy)[1] - root[1]) * k
            r = 6 * SS
            od.ellipse([px - r, py - r, px + r, py + r], fill=(220, 120, 104, 235))
    ov = ov.filter(ImageFilter.GaussianBlur(1.2 * SS))
    img.alpha_composite(ov)
    glow_spot(img, root, 150 * SS, RED, 70)
    box(d, -0.45, -0.45, 0, 0.9, 0.9, 0.9, s, (22, 20, 18), ox=ox, oy=oy)


def scene_funnel(d, img, s, palette):
    """مصفاة: كثير يدخل، قليل يخرج — رأي/حقيقة أو كلام الناس."""
    ox, oy = W * SS * 0.52, H * SS * 0.66
    for i in range(9):
        a = math.radians(-70 + i * 17)
        x, y = 7.5 * math.cos(a), 7.5 * math.sin(a)
        box(d, x - 0.35, y - 0.35, 2.6 + (i % 3) * 0.5, 0.7, 0.7, 0.7, s, DARK_OBJ, ox=ox, oy=oy)
    box(d, -2.6, -1.2, 0.8, 5.2, 2.4, 0.25, s, palette["base"], ox=ox, oy=oy)
    d.polygon([_iso(-2.6, -1.2, 0.8, s, ox, oy), _iso(2.6, -1.2, 0.8, s, ox, oy),
               _iso(0.8, 1.6, 4.0, s, ox, oy), _iso(-0.8, 1.6, 4.0, s, ox, oy)],
              fill=_shade(palette["base"], 0.8))
    box(d, -0.5, 1.2, 0, 1.0, 1.0, 1.0, s, GOLD_L, ox=ox, oy=oy)
    glow_spot(img, _iso(0, 1.6, 1.2, s, ox, oy), 110 * SS, GOLD_L, 60)


def scene_books(d, img, s, palette):
    """كتب متراكمة وشمعة/قنديل — العلم الذي رفعه الطحاوي."""
    ox, oy = W * SS * 0.50, H * SS * 0.74
    shadow(img, (ox, oy + 8 * SS), 760 * SS, 130 * SS, blur=18, alpha=110)
    for i in range(5):
        col = [SAND, (110, 90, 66), (86, 74, 58), (122, 100, 72), (96, 84, 64)][i]
        box(d, -2.6 + i * 0.16, -1.8 + i * 0.1, i * 0.55, 5.2 - i * 0.32, 3.6 - i * 0.2, 0.55, s, col, ox=ox, oy=oy)
    # قنديل
    lx, ly = _iso(3.6, -1.6, 0.4, s, ox, oy)
    d.line([(lx, ly), (lx, ly - 90 * SS)], fill=(120, 108, 88, 220), width=max(1, 2 * SS))
    d.ellipse([lx - 26 * SS, ly - 96 * SS, lx + 26 * SS, ly - 44 * SS], fill=(226, 190, 120))
    glow_spot(img, (lx, ly - 70 * SS), 150 * SS, GOLD_L, 80)


def scene_compass(d, img, s, palette):
    """بوصلة: إبرة ذهبية على قرص داكن."""
    ox, oy = W * SS * 0.50, H * SS * 0.55
    cx, cy = _iso(0, 0, 0, s, ox, oy)
    rw, rh = 5.6 * s * ISO_C, 5.6 * s * 0.72
    d.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=palette["base"])
    d.ellipse([cx - rw * 0.92, cy - rh * 0.92, cx + rw * 0.92, cy + rh * 0.92],
              outline=GOLD_L + (200,), width=max(2, int(3 * SS)))
    for a in range(0, 360, 30):
        ax = cx + math.cos(math.radians(a)) * rw * 0.8
        ay = cy + math.sin(math.radians(a)) * rh * 0.8
        bx = cx + math.cos(math.radians(a)) * rw * 0.94
        by = cy + math.sin(math.radians(a)) * rh * 0.94
        d.line([(ax, ay), (bx, by)], fill=(200, 186, 158, 180), width=max(1, 2 * SS))
    d.polygon([(cx, cy - rh * 0.66), (cx + 22 * SS, cy), (cx, cy + rh * 0.66), (cx - 22 * SS, cy)],
              fill=GOLD_L)
    glow_spot(img, (cx, cy), 130 * SS, GOLD_L, 55)


SCENES = {
    "house": scene_house,
    "conference": scene_conference,
    "gap": scene_gap,
    "network": scene_network,
    "road": scene_road,
    "ropes": scene_ropes,
    "balance": scene_balance,
    "vessel": scene_vessel,
    "funnel": scene_funnel,
    "books": scene_books,
    "compass": scene_compass,
}

PALETTES = {
    "gold": {"wall": (108, 92, 68), "base": (96, 82, 62), "table": (78, 66, 50),
             "seats": (64, 54, 42), "edge": GOLD_L, "road": (62, 54, 42),
             "sign": (96, 84, 64), "car": (150, 126, 82), "a": (96, 82, 62), "b": (74, 64, 50)},
    "red": {"wall": (120, 62, 52), "base": (92, 56, 48), "table": (84, 52, 44),
            "seats": (58, 40, 36), "edge": (180, 92, 76), "road": (58, 44, 38),
            "sign": (110, 70, 58), "car": (150, 92, 66), "a": (120, 62, 52), "b": (78, 44, 38)},
    "blue": {"wall": (66, 86, 96), "base": (54, 72, 82), "table": (48, 64, 74),
             "seats": (38, 50, 58), "edge": (110, 150, 168), "road": (40, 50, 56),
             "sign": (72, 96, 108), "car": (120, 150, 162), "a": (66, 86, 96), "b": (44, 58, 68)},
}


def make_card(scene: str, headline: list[str], kicker: str, note: str | None = None,
              palette: str = "gold", out: str = "/tmp/card.png", seed: int = 0) -> str:
    """بطاقة b-roll كاملة الإطار (1920×1080)."""
    img = _grad_bg(glow_xy=(0.62, 0.40)).convert("RGBA")
    img = _grid(img, horizon=0.55)
    pal = PALETTES[palette]
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    s = W * SS * 0.036
    SCENES[scene](d, layer, s, pal)
    img.alpha_composite(layer, (int(W * SS * 0.085), int(H * SS * 0.03)))

    # تدرّج داكن يسار الإطار (خلف النص) — قبل رسم النص حتى لا يبهت
    grad = Image.new("L", (img.width, img.height), 0)
    gd = ImageDraw.Draw(grad)
    for xx in range(int(img.width * 0.62)):
        v = int(240 * (1 - xx / (img.width * 0.62)) ** 1.15)
        gd.line([(xx, 0), (xx, img.height)], fill=v)
    img.paste(Image.new("RGBA", img.size, (10, 9, 8, 255)), (0, 0), grad)

    # إطار + شعار
    d2 = ImageDraw.Draw(img)
    d2.rectangle([26 * SS, 26 * SS, img.width - 27 * SS, img.height - 27 * SS],
                 outline=GOLD + (110,), width=max(1, 2 * SS))
    lock = G.brand_lockup(int(120 * SS), color=PARCH)
    img.alpha_composite(lock, (70 * SS, 62 * SS))

    # النص: يسار الإطار
    x0 = int(120 * SS)
    y = int(300 * SS)
    f_k = G.font(G.PLEX_B, int(34 * SS))
    G.draw_ar(d2, (x0, y), kicker, f_k, GOLD_L, stroke=max(1, SS), stroke_fill=(10, 9, 8))
    y += int(72 * SS)
    for line in headline:
        fnt = G.font(G.AMIRI_B, int(88 * SS))
        G.draw_ar(d2, (x0, y), line, fnt, PARCH, stroke=max(2, 3 * SS), stroke_fill=(10, 9, 8))
        y += int(110 * SS)
    # خط ذهبي فاصل
    d2.line([(x0, y + 8 * SS), (x0 + 260 * SS, y + 8 * SS)], fill=GOLD_L + (200,), width=max(1, 3 * SS))
    if note:
        f_n = G.font(G.PLEX_M, int(30 * SS))
        G.draw_ar(d2, (x0, y + 46 * SS), note, f_n, (206, 194, 172))
    # فينييت + حبيبات
    vig = Image.new("L", img.size, 0)
    vd = ImageDraw.Draw(vig)
    for i in range(60):
        pad = -i * 6 * SS
        vd.rectangle([pad, pad, img.width - pad, img.height - pad], outline=8)
    vig = vig.filter(ImageFilter.GaussianBlur(120 * SS))
    img.paste(Image.new("RGBA", img.size, (0, 0, 0, 255)), (0, 0), vig)

    img = img.convert("RGB").resize((W, H), Image.LANCZOS)
    img.save(out, quality=94)
    return out


if __name__ == "__main__":
    import json
    spec = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else []
    os.makedirs("outputs/SERIES_RIWAQ/NEW/cards", exist_ok=True)
    for c in spec:
        p = make_card(c["scene"], c["headline"], c["kicker"], c.get("note"), c.get("palette", "gold"),
                      out=f"outputs/SERIES_RIWAQ/NEW/cards/{c['id']}.png")
        print("card", c["id"], p)
