#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gfx.py — the motion-layer graphics for RUWAQ | 1816, drawn in code.

Everything is a full-frame RGBA overlay at the delivery resolution, so FFmpeg only
has to composite, not design. Brand values are read from 05_Template_Kit/brand.json
where they exist; nothing is invented.

Layers produced here:
  paper(size)            aged paper field with fibres and damp stains
  rule(...)              the thin gold rule
  thread(points)         the golden thread motif
  title / kicker / end   Amiri + Plex Arabic, shaped and bidi-ordered in code
"""
import json, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import arabic_reshaper
from bidi.algorithm import get_display

BRAND = json.load(open('/home/user/Riwaq_System_Repo/05_Template_Kit/brand.json'))
C = {k: v['hex'] for k, v in BRAND['theme']['colors'].items()}
FONTS = {
    'amiri': '/home/user/Riwaq_System_Repo/public/fonts/Amiri-Regular.ttf',
    'amiri_bold': '/home/user/Riwaq_System_Repo/public/fonts/Amiri-Bold.ttf',
    'plex': '/home/user/Riwaq_System_Repo/public/fonts/IBMPlexSansArabic-Regular.ttf',
    'plex_med': '/home/user/Riwaq_System_Repo/public/fonts/IBMPlexSansArabic-Medium.ttf',
    'plex_bold': '/home/user/Riwaq_System_Repo/public/fonts/IBMPlexSansArabic-Bold.ttf',
}
W, H = 2560, 1440


def hexrgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def ar(text):
    """Shape and reorder Arabic for Pillow's simple text layout."""
    return get_display(arabic_reshaper.reshape(text))


def font(kind, px):
    return ImageFont.truetype(FONTS[kind], px)


# ------------------------------------------------------------------ paper
def paper(size=(W, H), seed=1816, tone='dark'):
    """Aged paper: base tone, long fibres, a few damp blooms, soft vignette."""
    rng = np.random.default_rng(seed)
    w, h = size
    base = hexrgb(C['parchment2'] if tone == 'light' else C['ink_deep'])
    a = np.ones((h, w, 3), np.float32) * np.array(base, np.float32)
    # coarse mottling: low-frequency noise, upscaled
    small = rng.normal(0, 1, (h // 24, w // 24)).astype(np.float32)
    mot = np.array(Image.fromarray(((small - small.min()) / (np.ptp(small) + 1e-6) * 255)
                                   .astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32)
    mot = (mot / 255.0 - 0.5)[..., None]
    strength = 14 if tone == 'dark' else 9
    a += mot * strength
    # fibres: thin random strokes
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    fibre = hexrgb(C['stone_light'])
    for _ in range(w // 12):
        x, y = rng.integers(0, w), rng.integers(0, h)
        ln = rng.integers(6, 46); ang = rng.normal(0, .35)
        d.line([(x, y), (x + ln * math.cos(ang), y + ln * math.sin(ang))],
               fill=fibre, width=1)
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    # damp blooms
    bl = Image.new('RGB', (w, h), base)
    bd = ImageDraw.Draw(bl)
    for _ in range(5):
        cx, cy = rng.integers(0, w), rng.integers(0, h)
        r = rng.integers(h // 8, h // 3)
        bd.ellipse([cx - r, cy - r, cx + r, cy + r],
                   fill=tuple(int(c * 1.12) for c in base))
    bl = bl.filter(ImageFilter.GaussianBlur(90))
    img = Image.blend(img, bl, 0.55)
    # vignette
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    vig = np.clip(1 - BRAND['theme']['look']['vignette'] * (r ** 2.2), 0, 1)[..., None]
    arr = np.asarray(img, np.float32) * vig
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
    return out


# ------------------------------------------------------------------ rules and thread
def rule(size=(W, H), inset=90, y=None, color=None, thickness=3, alpha=210):
    w, h = size
    lay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    y = h - inset if y is None else y
    d.line([(inset, y), (w - inset, y)], fill=hexrgb(color or C['gold']) + (alpha,), width=thickness)
    return lay


def thread(size=(W, H), pts=None, color=None, width=4, alpha=235, glow=True):
    """Golden thread as a smooth catmull-rom through control points."""
    w, h = size
    if pts is None:
        pts = [(-0.05, .62), (.22, .48), (.48, .58), (.74, .44), (1.05, .55)]
    P = [(x * w, y * h) for x, y in pts]

    def cr(p0, p1, p2, p3, t):
        t2, t3 = t * t, t * t * t
        return (0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t +
                       (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3),
                0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t +
                       (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3))

    curve = []
    ext = [P[0]] + P + [P[-1]]
    for i in range(len(ext) - 3):
        for s in range(24):
            curve.append(cr(*ext[i:i + 4], s / 24))
    lay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    col = hexrgb(color or C['gold_light'])
    if glow:
        g = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(g).line(curve, fill=col + (60,), width=width * 5, joint='curve')
        g = g.filter(ImageFilter.GaussianBlur(10))
        lay = Image.alpha_composite(lay, g)
    d = ImageDraw.Draw(lay)
    d.line(curve, fill=col + (alpha,), width=width, joint='curve')
    return lay


# ------------------------------------------------------------------ type
def text_layer(txt, kind='amiri_bold', px=78, color=None, pos='center',
               size=(W, H), align='center', max_width=None, line_gap=18, opacity=255):
    w, h = size
    lay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    f = font(kind, px)
    col = hexrgb(color or C['parchment']) + (opacity,)
    s = ar(txt)
    lines = s.split('\n')
    widths = [d.textlength(ln, font=f) for ln in lines]
    asc, desc = f.getmetrics()
    lh = asc + desc
    total = lh * len(lines) + line_gap * (len(lines) - 1)
    y = (h - total) / 2 if pos == 'center' else pos
    for ln, wd in zip(lines, widths):
        if align == 'center':
            x = (w - wd) / 2
        elif align == 'right':
            x = w - wd - 90
        else:
            x = 90
        d.text((x, y), ln, font=f, fill=col)
        y += lh + line_gap
    return lay


def card_title(kicker, title, size=(W, H)):
    """Chapter card: kicker, gold rule, two-line Amiri title."""
    w, h = size
    lay = paper(size, tone='dark').point(lambda v: v)
    k = text_layer(kicker, 'plex_med', 40, C['stone'], pos=h // 2 - 190, size=size)
    r = rule(size, inset=w // 2 - 260, y=h // 2 - 108, thickness=2)
    t = text_layer(title, 'amiri_bold', 118, C['parchment'], pos=h // 2 - 60, size=size, line_gap=26)
    for L in (k, r, t):
        lay = Image.alpha_composite(lay, L)
    return lay


def end_card(title, tagline, size=(W, H)):
    w, h = size
    lay = paper(size, tone='dark')
    t = text_layer(title, 'amiri_bold', 150, C['parchment'], pos=h // 2 - 120, size=size)
    s = text_layer(tagline, 'plex', 42, C['gold_light'], pos=h // 2 + 60, size=size)
    r = rule(size, inset=w // 2 - 220, y=h // 2 + 20, thickness=2)
    for L in (t, r, s):
        lay = Image.alpha_composite(lay, L)
    return lay


if __name__ == '__main__':
    card_title('الفصل الأول', 'الصيف اللي\nمكانش').save('/tmp/card.png')
    print('ok')
