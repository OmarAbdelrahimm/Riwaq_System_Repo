#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
eng/core.py — drawing primitives for the 1816 Chapter 1 rebuild.

Nothing in here decides a shot; it only knows how to draw a thing honestly:
paper, ink, brass, thread, frost, grain. Every random element is seeded at build
time so a QA re-render lands on identical pixels.
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = '/home/user/Riwaq_System_Repo'
FONTS = os.path.join(ROOT, 'public/fonts')
W, H, FPS = 1920, 1080, 30

COL = dict(
    ink_deep='#1C1B19', ink_second='#242218', parchment='#F3EBDB', parchment2='#EDE6D6',
    gold='#A98A4B', gold_light='#C2A469', gold_pale='#EFE6D2', burgundy='#5E2230',
    stone='#8A7F6B', stone_light='#B9AE94',
)

_FONT_FILES = {
    'amiri': 'Amiri-Regular.ttf', 'amiri_bold': 'Amiri-Bold.ttf',
    'plex': 'IBMPlexSansArabic-Regular.ttf',
    'plex_med': 'IBMPlexSansArabic-Medium.ttf',
    'plex_bold': 'IBMPlexSansArabic-Bold.ttf',
}
_CACHE = {}


def font(key, size):
    k = (key, size)
    if k not in _CACHE:
        _CACHE[k] = ImageFont.truetype(os.path.join(FONTS, _FONT_FILES[key]), size)
    return _CACHE[k]


def ar(text):
    """Arabic shaping + bidi. A Latin/number run inside an Arabic sentence gets an
    explicit LTR isolate (U+2066 … U+2069) only when the bidi engine can carry it,
    so a date never reorders the words around it."""
    import arabic_reshaper
    from bidi.algorithm import get_display
    words = text.split(' ')
    shaped = []
    for w in words:
        if any('\u0600' <= ch <= '\u06FF' for ch in w):
            shaped.append(arabic_reshaper.reshape(w))
        else:
            shaped.append('\u202a' + w + '\u202c' if w else w)
    s = ' '.join(shaped)
    try:
        return get_display(s)
    except AssertionError:
        # the pure-python bidi implementation cannot nest isolates; fall back to
        # shaping alone, which is correct for RTL-primary lines
        return ' '.join(shaped)


def hexrgb(h):
    h = COL.get(h, h).lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ---------------------------------------------------------------- motion
def clamp01(x):
    return 0.0 if x < 0 else (1.0 if x > 1 else x)


def ramp(t, a, b):
    if b <= a:
        return 1.0 if t >= b else 0.0
    return clamp01((t - a) / (b - a))


def ease(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def step(x, fps=10.0):
    """stepped motion: paper collage moves on 8-12 fps, never continuously"""
    return math.floor(x * fps) / fps


# ---------------------------------------------------------------- contrast
def rel_lum(rgb):
    def f(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = [f(x) for x in rgb[:3]]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg, bg):
    a, b = rel_lum(fg), rel_lum(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def bg_stats(frame_rgb, box, percentile=85):
    x0, y0, x1, y1 = [int(v) for v in box]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(W, x1), min(H, y1)
    if x1 <= x0 or y1 <= y0:
        return (0, 0, 0)
    crop = np.asarray(frame_rgb.crop((x0, y0, x1, y1)), np.float32).reshape(-1, 3)
    lum = crop @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    idx = int(np.argsort(lum)[min(len(lum) - 1, int(len(lum) * percentile / 100.0))])
    return tuple(crop[idx].astype(int).tolist())


# ---------------------------------------------------------------- plate
def depth_proxy(im, horizon=0.46):
    """No monocular depth model is reachable in this sandbox, so the near/far mask
    is a disclosed proxy: a vertical gradient anchored to the plate's horizon line,
    softened, with a little low-frequency variation. It is not a depth map."""
    w, h = im.size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    g = np.clip((yy / h - (horizon - 0.22)) / 0.6, 0, 1)
    small = np.asarray(im.convert('L').resize((24, 14), Image.BILINEAR), np.float32) / 255.0
    low = np.asarray(Image.fromarray((small * 255).astype(np.uint8)).resize((w, h),
                                                                           Image.BICUBIC),
                     np.float32) / 255.0
    d = 0.72 * g + 0.28 * (low - 0.5) + 0.16
    return np.clip(d, 0, 1)


class Plate:
    """Photographic plate with a parallax split driven by the depth proxy.

    Rendered as two shifted planes (near / far) composited through a soft mask, so a
    push or pan gives differential motion instead of a flat zoom.
    """

    def __init__(self, path, oversample=1.30, horizon=0.46, depth=None):
        im = Image.open(path).convert('RGB')
        self.ov = oversample
        self.horizon = horizon
        self.proxy = depth if depth is not None else depth_proxy(im, horizon)
        self.buf = im.resize((int(W * oversample), int(H * oversample)), Image.BICUBIC)
        self.mask = Image.fromarray(((self.proxy) * 255).astype(np.uint8)).resize(
            (W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.2))

    def frame(self, zoom=1.06, pan=(0.0, 0.0), parallax=1.0, rotate=0.0):
        z = max(zoom, 1e-3)
        bw, bh = self.buf.size
        cw, ch = bw / z, bh / z
        cx = bw / 2 + pan[0] * bw * 0.25
        cy = bh / 2 + pan[1] * bh * 0.25
        x0 = min(max(cx - cw / 2, 0), bw - cw)
        y0 = min(max(cy - ch / 2, 0), bh - ch)
        far = self.buf.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize(
            (W, H), Image.BILINEAR)
        dx = pan[0] * 34.0 * parallax
        dy = pan[1] * 20.0 * parallax
        if abs(dx) + abs(dy) > 1.2:
            nx = min(max(x0 + dx * self.ov, 0), bw - cw)
            ny = min(max(y0 + dy * self.ov, 0), bh - ch)
            near = self.buf.crop((int(nx), int(ny), int(nx + cw), int(ny + ch)))
            near = near.resize((W, H), Image.BILINEAR)
            far = Image.composite(near, far, self.mask)
        if rotate:
            far = far.rotate(rotate, resample=Image.BICUBIC)
        return far


def grade_lerp(im, warm_k, cold_k, k):
    """the chapter's colour law: everything is pushed toward the cold slate end"""
    a = np.asarray(im.convert('RGB'), np.float32) / 255.0
    lum = a @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    a = lum[..., None] + (a - lum[..., None]) * (0.72 + 0.12 * k)
    a[..., 2] = np.clip(a[..., 2] * (1.0 + 0.10 * k) + 0.012 * k, 0, 1)
    a[..., 0] = np.clip(a[..., 0] * (1.0 - 0.07 * k), 0, 1)
    a = np.clip((a - 0.5) * (1.02 - 0.05 * k) + 0.5, 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8))


def expose(im, k=1.0, lift=0.0):
    """photographic exposure for a plate that arrived too dark or too bright; `lift`
    raises the toe so a night plate keeps detail instead of crushing to black"""
    a = np.asarray(im.convert('RGB'), np.float32) / 255.0
    a = np.clip(a * k + lift * (1.0 - a), 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8))


def desaturate(im, k=0.7, cool=1.0):
    a = np.asarray(im.convert('RGB'), np.float32) / 255.0
    lum = a @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    a = lum[..., None] + (a - lum[..., None]) * (1 - k)
    a[..., 2] = np.clip(a[..., 2] * cool, 0, 1)
    a[..., 0] = np.clip(a[..., 0] * ((2.0 - cool) * 0.5 + 0.5), 0, 1)
    return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))


# ---------------------------------------------------------------- particles
class Particles:
    def __init__(self, kind='snow', count=260, seed=7, speed=1.0, wind=0.35,
                 size=(1, 3), opacity=0.75, area=None):
        rng = np.random.default_rng(seed)
        self.kind, self.n = kind, count
        self.p = np.stack([rng.random(count), rng.random(count), rng.random(count)], 1)
        self.speed, self.wind, self.size = speed, wind, size
        self.opacity = opacity
        self.area = area or (0.0, 0.0, 1.0, 1.0)

    def draw(self, t, intensity=1.0, gust=0.0):
        if intensity <= 0.01:
            return None
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        ax, ay, aw, ah = self.area
        n = int(self.n * min(intensity, 1.0))
        for i in range(n):
            px, py, ph = self.p[i]
            if self.kind == 'rain':
                y = (py + t * self.speed) % 1.0
                x = (px + t * self.wind * 0.12 + gust * 0.05) % 1.0
                ln = 26 + 34 * ph
                d.line([(ax * W + x * aw * W, ay * H + y * ah * H),
                        (ax * W + (x - 0.006) * aw * W, ay * H + (y - ln / H) * ah * H)],
                       fill=(214, 226, 235, int(120 * self.opacity * intensity)), width=2)
            elif self.kind == 'snow':
                y = (py + t * self.speed * 0.12) % 1.0
                x = (px + math.sin(t * 0.6 + ph * 6.28) * 0.012 + t * self.wind * 0.02) % 1.0
                r = self.size[0] + (self.size[1] - self.size[0]) * ph
                d.ellipse([ax * W + x * aw * W - r, ay * H + y * ah * H - r,
                           ax * W + x * aw * W + r, ay * H + y * ah * H + r],
                          fill=(246, 248, 252, int(210 * self.opacity * intensity)))
            elif self.kind == 'ash':
                y = (py + t * self.speed * 0.06) % 1.0
                x = (px + math.sin(t * 0.35 + ph * 5.0) * 0.02) % 1.0
                r = self.size[0] + (self.size[1] - self.size[0]) * ph
                d.ellipse([ax * W + x * aw * W - r, ay * H + y * ah * H - r,
                           ax * W + x * aw * W + r, ay * H + y * ah * H + r],
                          fill=(120, 116, 108, int(150 * self.opacity * intensity)))
            else:                                     # dust motes
                y = (py + t * self.speed * 0.03) % 1.0
                x = (px + t * self.wind * 0.004) % 1.0
                r = self.size[0] + (self.size[1] - self.size[0]) * ph
                d.ellipse([ax * W + x * aw * W - r, ay * H + y * ah * H - r,
                           ax * W + x * aw * W + r, ay * H + y * ah * H + r],
                          fill=(236, 228, 210, int(90 * self.opacity * intensity)))
        if self.kind in ('snow', 'ash', 'dust'):
            lay = lay.filter(ImageFilter.GaussianBlur(0.6))
        return lay


# ---------------------------------------------------------------- paper
def torn_rect(w, h, seed=3, jitter=6, inset=3):
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    rng = np.random.default_rng(seed)
    steps = max(10, w // 18)
    pts = []
    for i in range(steps + 1):
        pts.append((w * i / steps, inset + rng.uniform(-jitter, jitter)))
    s2 = max(8, h // 18)
    for i in range(s2 + 1):
        pts.append((w - inset + rng.uniform(-jitter, jitter), h * i / s2))
    for i in range(steps + 1):
        pts.append((w - w * i / steps, h - inset + rng.uniform(-jitter, jitter)))
    for i in range(s2 + 1):
        pts.append((inset + rng.uniform(-jitter, jitter), h - h * i / s2))
    d.polygon(pts, fill=255)
    return m.filter(ImageFilter.GaussianBlur(0.8))


def paper_sheet(w, h, seed=3, tone='parchment2'):
    rng = np.random.default_rng(seed)
    base = np.zeros((h, w, 3), np.float32)
    c = np.array(hexrgb(COL[tone]), np.float32)
    small = rng.random((max(2, h // 40), max(2, w // 40))).astype(np.float32)
    grain = np.asarray(Image.fromarray((small * 255).astype(np.uint8)).resize((w, h),
                                                                             Image.BICUBIC),
                       np.float32) / 255.0
    fine = rng.random((h, w)).astype(np.float32)
    n = (grain - 0.5) * 16 + (fine - 0.5) * 9
    for i in range(3):
        base[..., i] = c[i] + n
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    base *= (1.04 - 0.16 * (xx / w * 0.5 + yy / h * 0.5))[..., None]
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert('RGBA')
    im.putalpha(torn_rect(w, h, seed=seed, jitter=max(2, w // 60)))
    return im


def drop_shadow(sprite, blur=26, off=(18, 22), alpha=170):
    pad = int(blur * 2.2)
    canvas = Image.new('RGBA', (sprite.width + pad * 2, sprite.height + pad * 2),
                       (0, 0, 0, 0))
    sh = Image.new('RGBA', sprite.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, alpha), (0, 0), sprite.split()[-1])
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(sh, (pad + off[0], pad + off[1]))
    canvas.alpha_composite(sprite, (pad, pad))
    return canvas


def tape(w=150, h=44, seed=5, tone='gold_pale'):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(seed)
    c = hexrgb(COL[tone])
    for i in range(h):
        a = 96 + int(28 * rng.random())
        d.line([(0, i), (w, i)], fill=c + (a,))
    for x in range(0, w, 7):                 # a faint weave
        d.line([(x, 0), (x + 6, h)], fill=(255, 255, 255, 18))
    return im.filter(ImageFilter.GaussianBlur(0.7))


def pin_sprite(r=13, color='burgundy'):
    s = r * 5
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = cy = s // 2
    d.ellipse([cx - r * 1.9, cy - r * 1.9 + r, cx + r * 1.9, cy + r * 1.9 + r],
              fill=(0, 0, 0, 78))
    c = hexrgb(COL[color])
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c + (250,))
    d.ellipse([cx - r * 0.55, cy - r * 0.62, cx + r * 0.18, cy - r * 0.05],
              fill=(255, 246, 236, 150))     # specular, so it reads as brass
    return im


def stamp_sprite(text, size=64, color='burgundy', pad=26, box=True):
    f = font('plex_bold', size)
    probe = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
    s = ar(text)
    bb = probe.textbbox((0, 0), s, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    im = Image.new('RGBA', (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if box:
        d.rounded_rectangle([2, 2, im.width - 3, im.height - 3], radius=3,
                            outline=hexrgb(COL[color]) + (235,), width=5)
    d.text((pad - bb[0], pad - bb[1]), s, font=f, fill=hexrgb(COL[color]) + (240,))
    a = np.asarray(im, np.float32).copy()
    rng = np.random.default_rng(11)
    n = rng.random((im.height, im.width)).astype(np.float32)
    n = np.asarray(Image.fromarray((n * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(2)), np.float32) / 255.0
    a[..., 3] *= (0.55 + 0.75 * n)          # rubber, not vector
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def ink_blot(r=40, seed=9, color='ink_deep'):
    im = Image.new('RGBA', (r * 3, r * 3), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(seed)
    c = hexrgb(COL[color])
    cx = cy = r * 1.5
    for i in range(9):
        a = rng.uniform(0, 6.28)
        rr = r * rng.uniform(0.55, 0.95)
        ox, oy = math.cos(a) * r * 0.42, math.sin(a) * r * 0.42
        d.ellipse([cx + ox - rr, cy + oy - rr, cx + ox + rr, cy + oy + rr],
                  fill=c + (int(140 + 70 * rng.random()),))
    return im.filter(ImageFilter.GaussianBlur(1.4))


# ---------------------------------------------------------------- drawn marks
def thread_points(pts):
    dense = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        n = max(2, int(math.dist(a, b) / 5))
        for s in range(n):
            t = s / n
            dense.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    dense.append(tuple(pts[-1]))
    return dense


def draw_thread(pts, progress=1.0, width=7, alpha=235, glow=True, dash=None,
                color='gold_light', core=(255, 248, 232, 150)):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    if len(pts) < 2 or progress <= 0:
        return lay
    dense = thread_points(pts)
    seg = dense[:max(2, int(len(dense) * clamp01(progress)))]
    if dash:
        seg = [p for i, p in enumerate(seg) if (i // dash) % 2 == 0]
        if len(seg) < 2:
            return lay
    d = ImageDraw.Draw(lay)
    if glow:
        g = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(g).line(seg, fill=hexrgb(COL[color]) + (34,),
                               width=width * 3, joint='curve')
        lay = Image.alpha_composite(lay, g.filter(ImageFilter.GaussianBlur(width * 1.5)))
        d = ImageDraw.Draw(lay)
    d.line(seg, fill=hexrgb(COL[color]) + (alpha,), width=width, joint='curve')
    d.line(seg, fill=core, width=max(2, width // 3), joint='curve')
    if progress < 0.999:
        x, y = seg[-1]
        d.ellipse([x - width * 1.1, y - width * 1.1, x + width * 1.1, y + width * 1.1],
                  fill=(255, 250, 236, 235))
    return lay


def draw_circle_annot(cx, cy, r, progress=1.0, width=6, color='gold_light', alpha=230):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    if progress <= 0:
        return lay
    d = ImageDraw.Draw(lay)
    d.arc([cx - r, cy - r, cx + r, cy + r], -96, -96 + 372 * clamp01(progress),
          fill=hexrgb(COL[color]) + (alpha,), width=width)
    return lay


def draw_arrow(p0, p1, progress=1.0, width=5, color='gold_light', alpha=235):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    if progress <= 0:
        return lay
    x1 = p0[0] + (p1[0] - p0[0]) * clamp01(progress)
    y1 = p0[1] + (p1[1] - p0[1]) * clamp01(progress)
    d = ImageDraw.Draw(lay)
    c = hexrgb(COL[color]) + (alpha,)
    d.line([p0, (x1, y1)], fill=c, width=width)
    if progress > 0.82:
        a = math.atan2(y1 - p0[1], x1 - p0[0])
        for s in (-0.5, 0.5):
            d.line([(x1, y1), (x1 - 26 * math.cos(a + s), y1 - 26 * math.sin(a + s))],
                   fill=c, width=width)
    return lay


# ---------------------------------------------------------------- brand mark
def ruwaq_mark(size=210, color='parchment', weight=None, dot=True):
    """The رِواق mark, drawn: a portico — a semicircular arch on two slim columns,
    capitals where the arch springs, a plinth, and a gold dot under the arch.
    No logo file exists in the repo, so the mark is drawn here and nowhere else.
    The capitals are what make it read as architecture instead of a light bulb."""
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = hexrgb(COL[color])
    cx = size / 2
    r = size * 0.17
    spring = size * 0.31
    base = size * 0.86
    lw = max(2, int(weight if weight else size * 0.017))
    d.arc([cx - r, spring - r, cx + r, spring + r], 180, 360, fill=c + (244,), width=lw)
    d.line([(cx - r, spring), (cx - r, base)], fill=c + (244,), width=lw)
    d.line([(cx + r, spring), (cx + r, base)], fill=c + (244,), width=lw)
    d.line([(cx - r * 1.34, spring), (cx - r * 0.62, spring)], fill=c + (244,), width=lw)
    d.line([(cx + r * 0.62, spring), (cx + r * 1.34, spring)], fill=c + (244,), width=lw)
    d.line([(cx - r * 1.34, base), (cx + r * 1.34, base)], fill=c + (244,), width=lw)
    if dot:
        rr = size * 0.040
        d.ellipse([cx - rr, spring - r * 0.40 - rr, cx + rr, spring - r * 0.40 + rr],
                  fill=hexrgb(COL['gold_light']) + (246,))
    return im


def mark_path(size=210, samples=6):
    """one continuous thread: up the left column, across its capital, over the arch,
    across the right capital, down the right column."""
    cx = size / 2
    r = size * 0.17
    spring = size * 0.31
    base = size * 0.86
    pts = [(cx - r * 1.34, base), (cx - r * 1.34, spring), (cx - r * 0.62, spring),
           (cx - r, spring)]
    for a in range(180, 361, samples):
        rad = math.radians(a)
        pts.append((cx + r * math.cos(rad), spring + r * math.sin(rad)))
    pts += [(cx + r, spring), (cx + r * 0.62, spring), (cx + r * 1.34, spring),
            (cx + r * 1.34, base)]
    return pts


class Logo:
    """small transparent corner mark — never on a rectangle"""

    def __init__(self, size=54, color='parchment', alpha=190):
        self.sprite = ruwaq_mark(size=size, color=color, weight=2)
        a = np.asarray(self.sprite, np.float32)
        a[..., 3] *= alpha / 255.0
        self.sprite = Image.fromarray(a.astype(np.uint8))

    def pos(self, corner='bl'):
        m = 92
        if corner == 'bl':
            return (m, H - m - self.sprite.height)
        return (W - m - self.sprite.width, H - m - self.sprite.height)

    def draw(self, alpha=1.0, corner='bl'):
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        s = self.sprite
        if alpha < 1.0:
            a = np.asarray(s, np.float32).copy()
            a[..., 3] *= alpha
            s = Image.fromarray(a.astype(np.uint8))
        lay.alpha_composite(s, self.pos(corner))
        return lay


# ---------------------------------------------------------------- frost
class Frost:
    """Frost growing on glass, drawn as a layer. Deterministic."""

    def __init__(self, box, seed=77, crystals=150, max_len=190, color=(236, 244, 250)):
        self.box, self.color = box, color
        rng = np.random.default_rng(seed)
        x0, y0, x1, y1 = box
        self.cr = []
        for i in range(crystals):
            cx, cy = rng.uniform(x0, x1), rng.uniform(y0, y1)
            ang = rng.uniform(-math.pi, math.pi)
            ln = rng.uniform(26, max_len) * (0.5 + 0.5 * rng.random())
            order = rng.random()
            branches = []
            nb = int(rng.integers(3, 7))
            for b in range(nb):
                f = (b + 0.6) / (nb + 0.4)
                bang = ang + (1 if b % 2 else -1) * rng.uniform(0.5, 1.1)
                barbl = ln * (0.30 + 0.28 * rng.random()) * (1 - 0.5 * f)
                branches.append((cx + math.cos(ang) * ln * f, cy + math.sin(ang) * ln * f,
                                 bang, barbl * f))
            self.cr.append((cx, cy, ang, ln, order, branches))
        small = rng.random((max(2, (y1 - y0) // 26), max(2, (x1 - x0) // 26))).astype(np.float32)
        haze = Image.fromarray((small * 255).astype(np.uint8)).resize(
            (max(2, x1 - x0), max(2, y1 - y0)), Image.BICUBIC)
        hz = np.asarray(haze, np.float32) / 255.0
        self.haze = np.clip((hz - 0.42) * 2.6, 0, 1) ** 1.5

    def draw(self, progress=1.0):
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        if progress <= 0.001:
            return lay
        p = clamp01(progress)
        d = ImageDraw.Draw(lay)
        c = self.color
        x0, y0, x1, y1 = self.box
        hz = self.haze * (0.55 * p)
        patch = np.zeros((max(2, y1 - y0), max(2, x1 - x0), 4), np.uint8)
        for i in range(3):
            patch[..., i] = c[i]
        patch[..., 3] = (hz * 150).astype(np.uint8)
        lay.alpha_composite(Image.fromarray(patch, 'RGBA'), (x0, y0))
        for (cx, cy, ang, ln, order, branches) in self.cr:
            k = clamp01((p - order * 0.45) / 0.55)
            if k <= 0.01:
                continue
            a = int(215 * min(1.0, 0.35 + p))
            d.line([(cx, cy), (cx + math.cos(ang) * ln * k, cy + math.sin(ang) * ln * k)],
                   fill=c + (a,), width=2)
            for (bx, by, bang, barbl) in branches:
                if k < 0.35:
                    continue
                kb = clamp01((k - 0.35) / 0.65)
                d.line([(bx, by), (bx + math.cos(bang) * barbl * kb,
                                   by + math.sin(bang) * barbl * kb)],
                       fill=c + (int(a * 0.8),), width=1)
        return lay.filter(ImageFilter.GaussianBlur(0.5))


# ---------------------------------------------------------------- film
class Film:
    """grain + light leak + vignette, all precomputed, offset per frame"""

    def __init__(self, grain=10.0, vig=0.20, seed=3):
        rng = np.random.default_rng(seed)
        self.grain = rng.normal(0, grain, (H, W, 1)).astype(np.float32)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        self.vig = (1.0 - vig * np.clip((r - 0.35) / 0.85, 0, 1) ** 1.4)[..., None]
        self.leak = np.exp(-(((xx - W * 0.86) ** 2) / (W * 0.30) ** 2 +
                             ((yy - H * 0.10) ** 2) / (H * 0.34) ** 2)).astype(np.float32)
        self.leak_col = np.array([255, 238, 205], np.float32)

    def apply(self, im, fi=0, leak=0.0):
        a = np.asarray(im if im.mode == 'RGB' else im.convert('RGB'), np.float32)
        if leak > 0:
            ox = int((fi * 3) % 260) - 130
            a = a + np.roll(self.leak, ox, axis=1)[..., None] * self.leak_col * leak
        a = a * self.vig
        flat = self.grain.reshape(-1)
        g = np.roll(flat, (fi * 7919) % len(flat)).reshape(H, W, 1)
        return Image.fromarray(np.clip(a + g, 0, 255).astype(np.uint8))


# ---------------------------------------------------------------- text
class TextReveal:
    """ink-write text. Dark ink on paper by default; a scrim is available but the
    chapter does not use light type over photographs."""

    def __init__(self, text, size=64, color='ink_deep', pos='lower', fontkey='plex_bold',
                 align='center', max_words=6, scrim=0.0, scrim_color='ink_deep'):
        self.text = text
        assert len(text.split()) <= max_words, f'max {max_words} words: {text!r}'
        self.f = font(fontkey, size)
        self.color = color
        self.pos, self.align = pos, align
        self.scrim, self.scrim_color = scrim, scrim_color
        probe = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
        s = ar(text)
        bb = probe.textbbox((0, 0), s, font=self.f)
        self.tw, self.th = bb[2] - bb[0], bb[3] - bb[1]
        self.bb = bb

    def anchor(self, y=None, x=None):
        ax = W // 2 if (x is None and self.align == 'center') else (x if x is not None else 150)
        if y is None:
            y = int(H * 0.78) if self.pos == 'lower' else int(H * 0.46)
        x0 = ax - self.tw / 2 if self.align == 'center' else ax
        return x0, y

    def draw(self, progress=1.0, y=None, x=None, alpha=255):
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        if progress <= 0:
            return lay
        x0, yy = self.anchor(y, x)
        if self.scrim > 0:
            pad = 34
            sc = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(sc).rounded_rectangle(
                [x0 - pad, yy - pad, x0 + self.tw + pad, yy + self.th + pad + 6],
                radius=8, fill=hexrgb(COL[self.scrim_color]) + (int(200 * self.scrim),))
            lay = Image.alpha_composite(lay, sc.filter(ImageFilter.GaussianBlur(14)))
        txt = Image.new('RGBA', (int(self.tw) + 8, int(self.th) + 12), (0, 0, 0, 0))
        ImageDraw.Draw(txt).text((4 - self.bb[0], 6 - self.bb[1]), ar(self.text),
                                 font=self.f, fill=hexrgb(COL[self.color]) + (alpha,))
        if progress < 0.999:
            txt = txt.crop((0, 0, max(2, int(txt.width * progress) + 6), txt.height))
        lay.alpha_composite(txt, (int(x0) - 4, int(yy) - 6))
        return lay


# ---------------------------------------------------------------- shot model
class Shot:
    def __init__(self, name, t0, t1, layers, render, events=None, cam='push'):
        self.name = name
        self.t0, self.t1 = t0, t1
        self.layers = layers
        self.render = render
        self.events = events or []
        self.cam = cam
