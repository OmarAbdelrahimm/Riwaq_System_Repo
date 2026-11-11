#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eng5/core5.py — v5 compositor: real footage, one grade, one grain, one logo.

Changes from v4, all driven by the review:

  * THE LOGO IS THE SUPPLIED FILE, NOT A DRAWING. v4 drew a procedural portico for the
    sting, which read as a plain house outline. The sting now animates the supplied
    wordmark (02-logo-horizontal-dark-bg.png, ivory ink, native 1600x1063, clean alpha)
    and the corner watermark is the same file. Aspect ratio is never altered.
  * ONE GRADE. Every plate, the map and every prop pass through `grade5()` with the same
    transfer, so the film is one look rather than three.
  * ONE GRAIN. Per-frame grain, same amplitude everywhere, applied last.
  * DISSOLVES. `dissolve()` cross-fades two rendered frames, so transitions are real
    blends rather than hard cuts with a flash.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

W, H = 1920, 1080
FPS = 30
SRC = '/home/user/work/src'
FONTS = '/home/user/Riwaq_System_Repo/public/fonts'
GD = '/home/user/Riwaq_System_Repo/google_drive'

INK = (26, 22, 18)
PAPER = (243, 235, 219)
PAPER_2 = (237, 230, 214)
BURG = (94, 34, 48)
GOLD = (201, 168, 106)
GOLD_HI = (239, 230, 210)
CREAM = (239, 230, 210)

HIDE_TEXT = [False]


def T():
    return not HIDE_TEXT[0]


# ---------------------------------------------------------------- text

def ar(text):
    return get_display(arabic_reshaper.reshape(text))


_fc = {}


def font(name, size):
    key = (name, size)
    if key not in _fc:
        _fc[key] = ImageFont.truetype(os.path.join(FONTS, name), size)
    return _fc[key]


def text_sprite(text, size=64, fill=INK, fname='IBMPlexSansArabic-Bold.ttf', pad=8):
    f = font(fname, size)
    s = ar(text)
    box = f.getbbox(s)
    w = box[2] - box[0] + pad * 2
    h = box[3] - box[1] + pad * 2
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - box[0], pad - box[1]), s, font=f, fill=fill + (255,))
    return im


# ---------------------------------------------------------------- camera

class Camera:
    """sub-pixel crop, always derived from the image actually passed in.

    v5 built this with src=(1280,720) -- the source file's size -- while the plate frames
    on disk were already 1920x1080. The crop therefore took a 1103x621 window out of the
    1080p frame and scaled it back up to 1920: a 1.74x upscale stacked on the 1.5x the
    decoder had done, 2.6x in total, which is what made the farmer's face blocky at
    0:11. `src` is gone; the transform reads im.size, so a mismatch cannot happen again.
    """

    def __init__(self, zoom=1.0, cx=None, cy=None, pan=(0.0, 0.0), src=None):
        self.z = zoom
        self.src = src          # kept only for callers that still pass it; ignored
        self._c = None
        self.off = pan

    def _centre(self, sw, sh):
        return (sw / 2 + self.off[0], sh / 2 + self.off[1])

    def crop_for(self, sw, sh):
        w, h = sw / self.z, sh / self.z
        cx, cy = self._centre(sw, sh)
        x0 = min(max(0, cx - w / 2), sw - w)
        y0 = min(max(0, cy - h / 2), sh - h)
        return x0, y0, w, h

    def apply(self, im):
        sw, sh = im.size
        x0, y0, w, h = self.crop_for(sw, sh)
        # never upscale: if the window is smaller than the frame, widen it instead
        if w < W or h < H:
            w, h = max(w, W), max(h, H)
            w, h = min(w, sw), min(h, sh)
            x0 = min(max(0, x0), sw - w)
            y0 = min(max(0, y0), sh - h)
        self._c = (x0, y0, w, h)
        return im.transform((W, H), Image.AFFINE,
                            (w / W, 0, x0, 0, h / H, y0), resample=Image.BICUBIC)

    def to_screen(self, x, y):
        if self._c is None:
            raise RuntimeError('camera has no crop yet')
        x0, y0, w, h = self._c
        return ((x - x0) * W / w, (y - y0) * H / h)


class Plate:
    _cache = {}

    def __init__(self, key, in_point=0.0, loop=True, src_fps=24.0):
        self.key = key
        self.dir = os.path.join(SRC, key)
        self.files = sorted(os.listdir(self.dir))
        self.n = len(self.files)
        self.in_point = in_point
        self.loop = loop
        # the clip was decoded 1:1, so one file is one source frame; at 24 fps a 30 fps
        # timeline must step 0.8 files per frame or the action runs 25 % fast
        # 24 fps source on a 30 fps timeline -> 0.8 source frames per output frame
        self.ratio = src_fps / FPS
        self.bsf = src_fps / FPS          # decoded files consumed per output frame
        self.seconds = self.n / src_fps

    def idx(self, t):
        i = int(round(self.in_point * FPS + t * FPS * self.ratio))
        if i >= self.n:
            # hold the last frame rather than wrap: wrapping replays the clip from the
            # top inside the same shot, which reads as a jump cut
            i = self.n - 1
        return max(0, min(self.n - 1, i))

    def frame(self, t, cam=None):
        i = self.idx(t)
        key = (self.key, i)
        if key not in Plate._cache:
            if len(Plate._cache) > 10:
                Plate._cache.clear()
            Plate._cache[key] = Image.open(os.path.join(self.dir, self.files[i])).convert('RGB')
        im = Plate._cache[key]
        return cam.apply(im) if cam else im


# ---------------------------------------------------------------- the one grade

def grade5(im, warmth=1.0, contrast=1.06, lift=0.008, sat=0.86):
    """the film's single look: cool, slightly desaturated, lifted blacks, warm highlights.

    Every plate and the map go through this, so nothing looks like a different film.
    `warmth` is the only per-shot knob: <1 cooler, >1 warmer.
    """
    a = np.asarray(im.convert('RGB'), np.float32) / 255.0
    lum = a @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    a = lum[..., None] + (a - lum[..., None]) * sat
    a = np.clip((a - 0.46) * contrast + 0.46, 0, 1)
    sh = np.clip(1.0 - lum * 1.6, 0, 1)[..., None]
    hi = np.clip(lum * 1.35 - 0.35, 0, 1)[..., None]
    a = a + sh * np.array([-0.012, 0.004, 0.030], np.float32) * warmth
    a = a + hi * np.array([0.028, 0.012, -0.014], np.float32)
    a = a * (1 - lift) + lift
    a = np.clip(a * np.array([1.0 + (warmth - 1) * 0.05, 1.0, 1.0 - (warmth - 1) * 0.05],
                             np.float32), 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8))


def apply_flash(im, amount):
    if amount <= 0:
        return im
    a = np.asarray(im, np.float32) / 255.0
    a = a + (1.0 - a) * amount * 0.85
    a[..., 2] = np.minimum(1.0, a[..., 2] * (1 + amount * 0.25))
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


# ---------------------------------------------------------------- particles

class Snow:
    def __init__(self, n=420, speed=(70, 190), size=(1.2, 3.4), wind=-26.0, seed=7,
                 alpha=(90, 210)):
        rng = np.random.default_rng(seed)
        self.n = n
        self.x0 = rng.uniform(-200, W + 200, n)
        self.y0 = rng.uniform(0, H + 400, n)
        self.vy = rng.uniform(*speed, n)
        self.vx = rng.uniform(-14, 14, n) + wind
        self.sz = rng.uniform(*size, n)
        self.al = rng.uniform(*alpha, n)
        self.ph = rng.uniform(0, 6.28, n)
        self.fq = rng.uniform(0.4, 1.3, n)

    def draw(self, dst, t, density=1.0, blur=0.0):
        n = int(self.n * max(0.0, min(1.0, density)))
        if n <= 0:
            return dst
        mask = Image.new('L', (W // 2, H // 2), 0)
        d = ImageDraw.Draw(mask)
        y = (self.y0[:n] + self.vy[:n] * t) % (H + 400) - 200
        x = (self.x0[:n] + self.vx[:n] * t + 18 * np.sin(self.fq[:n] * t + self.ph[:n])) % (W + 400) - 200
        for i in range(n):
            r = self.sz[i]
            d.ellipse([x[i] / 2 - r, y[i] / 2 - r, x[i] / 2 + r, y[i] / 2 + r],
                      fill=int(self.al[i]))
        mask = mask.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(0.9))
        if blur:
            mask = mask.filter(ImageFilter.GaussianBlur(blur))
        flake = Image.new('RGBA', (W, H), (248, 252, 255, 0))
        flake.putalpha(mask)
        return Image.alpha_composite(dst, flake)


class Rain:
    def __init__(self, n=520, speed=(1500, 2300), length=(28, 74), slant=0.20, seed=11,
                 alpha=(40, 110)):
        rng = np.random.default_rng(seed)
        self.n = n
        self.x0 = rng.uniform(-200, W + 200, n)
        self.y0 = rng.uniform(0, H + 300, n)
        self.vy = rng.uniform(*speed, n)
        self.ln = rng.uniform(*length, n)
        self.sl = slant * rng.uniform(0.8, 1.2, n)
        self.al = rng.uniform(*alpha, n)

    def draw(self, dst, t, density=1.0):
        n = int(self.n * max(0.0, min(1.0, density)))
        if n <= 0:
            return dst
        mask = Image.new('L', (W // 2, H // 2), 0)
        d = ImageDraw.Draw(mask)
        y = (self.y0[:n] + self.vy[:n] * t) % (H + 300) - 150
        x = (self.x0[:n] + self.vy[:n] * self.sl[:n] * t) % (W + 400) - 200
        for i in range(n):
            L = self.ln[i]
            d.line([(x[i] / 2, y[i] / 2), (x[i] / 2 - L * self.sl[i] / 2, y[i] / 2 - L / 2)],
                   fill=int(self.al[i]), width=1)
        mask = mask.resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(0.4))
        wet = Image.new('RGBA', (W, H), (222, 236, 244, 0))
        wet.putalpha(mask)
        return Image.alpha_composite(dst, wet)


# ---------------------------------------------------------------- paper props

def shadow_of(im, blur=16, off=(10, 14), alpha=140):
    pad = int(blur * 2.2)
    big = Image.new('RGBA', (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    big.alpha_composite(im, (pad, pad))
    sh = Image.new('RGBA', big.size, (0, 0, 0, 0))
    a = big.split()[3].filter(ImageFilter.GaussianBlur(blur))
    sh.putalpha(a.point(lambda v: int(v * alpha / 255)))
    out = Image.new('RGBA', big.size, (0, 0, 0, 0))
    out.alpha_composite(sh, (off[0], off[1]))
    out.alpha_composite(big, (0, 0))
    return out, pad


def torn_rect(w, h, paper=PAPER, seed=3, edge=7):
    rng = np.random.default_rng(seed)
    mask = Image.new('L', (w, h), 255)
    d = ImageDraw.Draw(mask)
    for side in range(4):
        if side == 0:
            pts = [(i, rng.integers(0, edge)) for i in range(w)]
        elif side == 1:
            pts = [(w - 1 - rng.integers(0, edge), i) for i in range(h)]
        elif side == 2:
            pts = [(i, h - 1 - rng.integers(0, edge)) for i in range(w)]
        else:
            pts = [(rng.integers(0, edge), i) for i in range(h)]
        d.line(pts, fill=0, width=1)
    sheet = Image.new('RGBA', (w, h), paper + (255,))
    sheet.putalpha(mask)
    return sheet


CARD_RADIUS = 4
ACCENT_W = 5
ACCENT = BURG          # #5E2230, the burgundy in the brand kit


def card(text, size=54, fill=INK, paper=PAPER, padx=40, pady=26, accent=ACCENT,
         accent_w=ACCENT_W, radius=CARD_RADIUS, shadow=(18, 0.45), seed=3):
    """a broadcast-grade information card.

    Not a flat beige rectangle: 4 px corners, a 5 px burgundy accent bar on the RIGHT edge
    (where Arabic reading starts), and a soft 18 px shadow at 45 % that lets the card sit
    in the scene lighting instead of on top of it.

    All shapes are drawn at 4x and downsampled, so the corners and the accent bar are
    genuinely anti-aliased rather than aliased staircases -- the v5 "noisy border" was
    exactly this: rounded_rectangle drawn at 1x.
    """
    ss = 4
    sp = text_sprite(text, size, fill)
    w = sp.width + padx * 2 + (accent_w if accent else 0)
    h = sp.height + pady * 2
    big = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    r = radius * ss
    d.rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], radius=r, fill=paper + (255,))
    if accent:
        bar = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0))
        ImageDraw.Draw(bar).rectangle([w * ss - accent_w * ss, 0, w * ss, h * ss],
                                      fill=accent + (255,))
        mask = Image.new('L', (w * ss, h * ss), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], radius=r,
                                              fill=255)
        big.paste(bar, (0, 0), Image.composite(bar.split()[3], mask, mask))
    sheet = big.resize((w, h), Image.LANCZOS)

    rng = np.random.default_rng(seed)
    tooth = np.asarray(Image.fromarray(((rng.normal(0, 4, (max(1, h // 2), max(1, w // 2)))
                                         + 128).clip(0, 255)).astype(np.uint8))
                       .resize((w, h), Image.BILINEAR), np.float32)
    a = np.asarray(sheet, np.float32)
    a[..., :3] = np.clip(a[..., :3] + (tooth - 128)[..., None] * 0.16, 0, 255)
    sheet = Image.fromarray(a.astype(np.uint8))
    sheet.alpha_composite(sp, (padx, pady))

    blur, op = shadow
    sh, pad = shadow_of(sheet, blur=blur, off=(6, 10), alpha=int(255 * op))
    return dict(sprite=sh,
                box=(pad + padx, pad + pady, pad + padx + sp.width, pad + pady + sp.height),
                pad=pad)


def paper_tag(text, **kw):
    """kept as the name pilot5 calls; it is a cinematically styled card now."""
    return card(text, **kw)


def floating_line(text, size=40, fill=CREAM, alpha=0.65, shadow=True):
    """a small cinematic line with no plate behind it: ivory at 65 % with a soft shadow.

    The brief for v6: the "re-imagined scenes" notice must not be a paper box, because a
    paper box makes it a second card competing with the year card.
    """
    sp = text_sprite(text, size, fill)
    out = Image.new('RGBA', (sp.width + 48, sp.height + 48), (0, 0, 0, 0))
    if shadow:
        # the fill is held at 65 % because that is the brief; legibility comes from the
        # shadow, drawn twice (tight and wide) so the type separates from a busy forest
        # without becoming a plate.
        for blur, off, op in ((4, 2, 0.95), (11, 3, 0.55)):
            a = Image.new('L', out.size, 0)
            a.paste(sp.split()[3], (24, 24 + off))
            a = a.filter(ImageFilter.GaussianBlur(blur))
            sh = Image.new('RGBA', out.size, (0, 0, 0, 0))
            sh.putalpha(a.point(lambda v: int(v * op)))
            out.alpha_composite(sh)
    sp2 = sp.copy()
    sp2.putalpha(sp2.split()[3].point(lambda v: int(v * alpha)))
    out.alpha_composite(sp2, (24, 24))
    return dict(sprite=out, box=(24, 24, 24 + sp.width, 24 + sp.height), pad=24)


def stamp_sprite(text, size=86, ink=BURG, paper=PAPER_2, shadow=(18, 0.45)):
    """the year card: a clean double hairline rule drawn at 4x, so the frame is a smooth
    vector line. In v5 three 3 px rounded_rectangles were drawn at 1x and read as a
    dithered/noisy border."""
    ss = 4
    sp = text_sprite(text, size, ink)
    w, h = sp.width + 96, sp.height + 74
    big = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    d.rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], radius=CARD_RADIUS * ss,
                        fill=paper + (255,))
    for inset, width, alpha in ((13, 2, 205), (21, 1, 120)):
        d.rounded_rectangle([inset * ss, (inset - 2) * ss,
                             (w - inset) * ss, (h - inset + 2) * ss],
                            radius=(CARD_RADIUS + 2) * ss,
                            outline=ink + (alpha,), width=int(width * ss))
    im = big.resize((w, h), Image.LANCZOS)
    im.alpha_composite(sp, (48, 37))
    sh, pad = shadow_of(im, blur=shadow[0], off=(6, 10), alpha=int(255 * shadow[1]))
    return dict(sprite=sh, box=(pad + 48, pad + 37, pad + 48 + sp.width, pad + 37 + sp.height))


def pin(dst, x, y, t, t0, r=13, col=GOLD):
    if t < t0:
        return dst
    u = min(1.0, (t - t0) / 0.22)
    drop = (1 - u) ** 3 * 30
    a = int(255 * min(1.0, (t - t0) / 0.10))
    lay = Image.new('RGBA', (r * 6, r * 6), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx = cy = r * 3
    d.ellipse([cx - r * 1.3, cy - r * 1.3 + 4, cx + r * 1.3, cy + r * 1.3 + 4], fill=(0, 0, 0, 80))
    d.ellipse([cx - r, cy - r - drop, cx + r, cy + r - drop],
              fill=col + (a,), outline=(255, 248, 232, a), width=2)
    d.ellipse([cx - r * 0.32, cy - r * 0.5 - drop, cx + r * 0.2, cy + r * 0.1 - drop],
              fill=(255, 250, 238, a))
    dst.alpha_composite(lay, (int(x - r * 3), int(y - r * 3)))
    return dst


# ---------------------------------------------------------------- the supplied logo

LOGO = {}


def logo_info():
    """open the supplied file once and report what it actually is"""
    if 'info' not in LOGO:
        p = os.path.join(GD, '02-logo-horizontal-dark-bg.png')
        im = Image.open(p)
        LOGO['file'] = p
        LOGO['native'] = im.size
        LOGO['mode'] = im.mode
        im = im.convert('RGBA')
        al = np.asarray(im)[..., 3]
        ys, xs = np.where(al > 8)
        LOGO['alpha_bbox'] = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
        LOGO['image'] = im
    return LOGO


def logo_scaled(width):
    """scale the supplied lockup to `width`, preserving its aspect ratio exactly"""
    li = logo_info()
    im = li['image']
    s = width / im.width
    return im.resize((max(1, int(round(im.width * s))), max(1, int(round(im.height * s)))),
                     Image.LANCZOS), s


def reveal_r2l(lg, u, feather=0.18):
    """write the wordmark on from the right, the direction Arabic reads.

    A hard vertical crop cut through letters and read as a glitch; the reveal is now a
    soft-edged mask sweeping right to left.
    """
    u = max(0.0, min(1.0, u))
    w, h = lg.size
    span = int(w * (1.0 + feather))
    edge = int(span * u)
    m = np.zeros((h, w), np.float32)
    fw = max(1, int(w * feather))
    for x in range(w):
        d = (w - 1 - x)
        m[:, x] = np.clip((edge - d) / fw, 0, 1)
    a = np.asarray(lg, np.float32)
    a[..., 3] *= m
    return Image.fromarray(a.astype(np.uint8))


def place_logo(dst, x, y, width=330, alpha=1.0, shadow=True):
    """place the supplied mark. A feathered drop shadow (not a box) keeps the ivory
    wordmark legible over a bright plate: on the button frame it measured 3.71:1, which
    is below the 4.5:1 the brief requires for text."""
    lg, s = logo_scaled(width)
    if alpha < 1.0:
        lg = lg.copy()
        lg.putalpha(lg.split()[3].point(lambda v: int(v * alpha)))
    if shadow:
        pad = 26
        gl = Image.new('RGBA', (lg.width + pad * 2, lg.height + pad * 2), (0, 0, 0, 0))
        gl.alpha_composite(lg, (pad, pad))
        a = gl.split()[3].filter(ImageFilter.GaussianBlur(14))
        sh = Image.new('RGBA', gl.size, (0, 0, 0, 0))
        sh.putalpha(a.point(lambda v: int(v * 0.62)))
        for dx, dy in ((0, 0), (2, 3)):
            dst.alpha_composite(sh, (int(x) - pad + dx, int(y) - pad + dy))
    dst.alpha_composite(lg, (int(x), int(y)))
    return dst, lg.size, s


# ---------------------------------------------------------------- transitions

def dissolve(a, b, k):
    """cross-fade two finished frames; k=0 is a, k=1 is b"""
    k = max(0.0, min(1.0, k))
    if k <= 0:
        return a
    if k >= 1:
        return b
    aa = np.asarray(a.convert('RGB'), np.float32)
    bb = np.asarray(b.convert('RGB'), np.float32)
    return Image.fromarray((aa * (1 - k) + bb * k).astype(np.uint8))


def whip(a, b, k, strength=0.42):
    """a whip pan: the outgoing frame smears off to one side, the incoming arrives.

    A cross-dissolve between two shots of similar content (two men, two fields) ghosts
    the faces together and reads as a mistake. A directional smear hides the change,
    which is why the brief asks for a whip pan specifically on the America->Europe cut.
    """
    k = max(0.0, min(1.0, k))
    off = strength * W
    canvas = Image.new('RGB', (W, H), (6, 7, 9))
    ax = int(-k * off)
    bx = int((1 - k) * off)
    blur = max(0.0, (1 - abs(k - 0.5) * 2) * off * 0.30)
    A = a.convert('RGB')
    B = b.convert('RGB')
    if blur > 0.5:
        A = A.filter(ImageFilter.GaussianBlur(blur * 0.35))
        B = B.filter(ImageFilter.GaussianBlur(blur * 0.35))
    canvas.paste(A, (ax, 0))
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).rectangle([max(0, bx), 0, W, H], fill=255)
    canvas.paste(B, (bx, 0), m)
    if blur > 0.5:
        canvas = canvas.filter(ImageFilter.GaussianBlur(min(14.0, blur * 0.5)))
    return canvas


def zoom_blur(im, amount):
    """a radial smear: the map's in/out transition"""
    if amount <= 0.01:
        return im.convert('RGB')
    acc = np.zeros((H, W, 3), np.float32)
    wsum = 0.0
    for i, s in enumerate((1.0, 1.02, 1.045, 1.075, 1.11)):
        z = 1.0 + (s - 1.0) * amount * 2.4
        cw, ch = W / z, H / z
        x0, y0 = (W - cw) / 2, (H - ch) / 2
        sm = im.transform((W, H), Image.AFFINE, (cw / W, 0, x0, 0, ch / H, y0),
                          resample=Image.BILINEAR)
        wgt = 1.0 / (1 + i)
        acc += np.asarray(sm, np.float32) * wgt
        wsum += wgt
    out = acc / wsum
    base = np.asarray(im.convert('RGB'), np.float32)
    mix = (1 - amount) * base + amount * out
    return Image.fromarray(np.clip(mix, 0, 255).astype(np.uint8))


# ---------------------------------------------------------------- finishing

_GRAIN = {}


def grain(i, amt=5.0):
    """per-frame grain, unique on every frame (a cycle repeats and reads as a freeze).

    One base tile is kept and rolled per frame. Caching a rolled copy per frame cost
    7 GB (900 frames x 8 MB) and got the render OOM-killed on a 4 GB box.
    """
    if '_base' not in _GRAIN:
        _GRAIN['_base'] = np.random.default_rng(5).normal(0, 1.0, (H, W)).astype(np.float32)
    r = np.random.default_rng(1000 + (int(i) % 900))
    b = _GRAIN['_base']
    return np.roll(b, (int(r.integers(0, H)), int(r.integers(0, W))), (0, 1)) * amt


_VIG = None


def vignette(depth=0.14):
    """a soft cinematic vignette: `depth` is how much light is lost at the corners.

    v6 asks for 12-15 % at the edges, so the default is 0.14 and the falloff starts well
    inside the frame -- a vignette that only touches the last few pixels is invisible,
    one that starts too early looks like a lens fault.
    """
    global _VIG
    if _VIG is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W * 0.5)) ** 2 + ((yy - H / 2) / (H * 0.5)) ** 2)
        r = r / r.max()
        v = 1.0 - depth * np.clip((r - 0.32) / 0.68, 0, 1) ** 2.0
        _VIG = v.astype(np.float32)
    return _VIG


def finish(im, frame_i=0, grain_amt=1.0, vig=1.0):
    a = np.asarray(im.convert('RGB'), np.float32)
    a *= (vignette() ** vig)[..., None]
    a += grain(frame_i)[..., None] * grain_amt
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def fade_to_black(im, k):
    if k >= 1:
        return im
    a = np.asarray(im, np.float32) * max(0.0, k)
    return Image.fromarray(a.astype(np.uint8))
