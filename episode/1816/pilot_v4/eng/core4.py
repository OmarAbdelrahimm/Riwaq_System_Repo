#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eng4/core4.py — real-footage compositor for PILOT v4.

Every shot is built on a supplied AI clip decoded at 1920x1080 (see src/), never on a
procedural plate. Layers are added on top of that footage: snowfall, rain, paper tags,
stamps, pins, the map, the brand mark, grain and vignette.

Particles are ANALYTIC: position is a pure function of time, so any frame can be
rendered on its own and re-rendering a range reproduces it exactly.
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

INK = (28, 24, 20)
PAPER = (243, 235, 219)
PAPER_2 = (237, 230, 214)
BURG = (94, 34, 48)
GOLD = (201, 168, 106)
GOLD_HI = (239, 230, 210)
CREAM = (239, 230, 210)


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
    """crop-and-scale a source image, then know where a source point lands on screen"""

    def __init__(self, zoom=1.0, cx=None, cy=None, pan=(0.0, 0.0), src=(W, H)):
        self.z = zoom
        self.src = src
        self.cx = (cx if cx is not None else src[0] / 2) + pan[0]
        self.cy = (cy if cy is not None else src[1] / 2) + pan[1]

    def crop(self):
        w, h = self.src[0] / self.z, self.src[1] / self.z
        x0 = min(max(0, self.cx - w / 2), self.src[0] - w)
        y0 = min(max(0, self.cy - h / 2), self.src[1] - h)
        return x0, y0, w, h

    def apply(self, im):
        # sub-pixel crop: an integer crop makes consecutive frames land on the SAME
        # pixels when the move is smaller than a pixel a frame, which reads as a
        # stutter (and in the QA as a "static" frame). An affine map keeps the move
        # continuous at any speed.
        x0, y0, w, h = self.crop()
        return im.transform((W, H), Image.AFFINE,
                            (w / W, 0, x0, 0, h / H, y0), resample=Image.BILINEAR)

    def to_screen(self, x, y):
        x0, y0, w, h = self.crop()
        return ((x - x0) * W / w, (y - y0) * H / h)


# ---------------------------------------------------------------- plates

class Plate:
    """a decoded clip: frames on disk at 1920x1080, 30 fps"""

    _cache = {}

    def __init__(self, key, in_point=0.0, loop=True):
        self.key = key
        self.dir = os.path.join(SRC, key)
        self.files = sorted(os.listdir(self.dir))
        self.n = len(self.files)
        self.in_point = in_point
        self.loop = loop

    def idx(self, t):
        i = int(round(self.in_point * FPS + t * FPS))
        if i >= self.n:
            i = (i - self.n) % max(1, self.n - 1) if self.loop else self.n - 1
        return max(0, min(self.n - 1, i))

    def frame(self, t, cam=None):
        i = self.idx(t)
        key = (self.key, i)
        if key not in Plate._cache:
            im = Image.open(os.path.join(self.dir, self.files[i])).convert('RGB')
            if len(Plate._cache) > 48:
                Plate._cache.clear()
            Plate._cache[key] = im
        im = Plate._cache[key]
        return cam.apply(im) if cam else im


# ---------------------------------------------------------------- grade

def grade(im, mul=(1, 1, 1), adds=(0, 0, 0), sat=1.0, lift=0.0, gamma=1.0):
    a = np.asarray(im, np.float32) / 255.0
    lum = a @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    a = lum[..., None] + (a - lum[..., None]) * sat
    if gamma != 1.0:
        a = np.clip(a, 0, 1) ** gamma
    a = a * np.array(mul, np.float32) + np.array(adds, np.float32) / 255.0
    if lift:
        a = a * (1 - lift) + lift
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def flash_curve(t, t0, dur=0.42, peak=0.55):
    """a lightning lift: instant rise, double-decay fall"""
    if t < t0 or t > t0 + dur * 3:
        return 0.0
    u = t - t0
    a = math.exp(-u * 9.0)
    b = 0.45 * math.exp(-((u - 0.13) ** 2) / (2 * 0.035 ** 2))
    return peak * min(1.0, (a + b))


def apply_flash(im, amount):
    if amount <= 0:
        return im
    a = np.asarray(im, np.float32) / 255.0
    a = a + (1.0 - a) * amount * 0.85
    a[..., 2] = np.minimum(1.0, a[..., 2] * (1 + amount * 0.25))
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


# ---------------------------------------------------------------- particles

class Snow:
    """analytic snowfall — position depends only on t, never on call order"""

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
    """analytic rain: streaks, steeper and faster than snow"""

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
        wa = 1 if n == 1 else None
        for i in range(n):
            L = self.ln[i]
            d.line([(x[i] / 2, y[i] / 2), (x[i] / 2 - L * self.sl[i] / 2, y[i] / 2 - L / 2)],
                   fill=int(self.al[i]), width=wa or 1)
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


def paper_tag(text, size=58, fill=INK, paper=PAPER, padx=34, pady=22,
              rotate=0.0, tape=True, seed=3):
    """a pinned paper tag: torn-ish sheet, fibre mottle, tape, ink.

    The ink box is derived by diffing the finished sheet against an identical sheet
    built WITHOUT the glyphs, so tape, mottle and rotation can never move it.
    """
    sp = text_sprite(text, size, fill)

    def build(with_text):
        w, h = sp.width + padx * 2, sp.height + pady * 2
        sheet = Image.new('RGBA', (w, h), paper + (255,))
        rng = np.random.default_rng(seed)
        m = (rng.normal(0, 6, (h // 3, w // 3))).astype(np.float32)
        m = np.asarray(Image.fromarray(((m + 128).clip(0, 255)).astype(np.uint8))
                       .resize((w, h), Image.BILINEAR), np.float32)
        a = np.asarray(sheet, np.float32)
        a[..., :3] = np.clip(a[..., :3] + (m - 128)[..., None] * 0.45, 0, 255)
        sheet = Image.fromarray(a.astype(np.uint8))
        if tape:
            for cx in (int(w * 0.18), int(w * 0.78)):
                tw, th = int(w * 0.26), 26
                tp = Image.new('RGBA', (tw, th), (232, 222, 198, 118))
                ImageDraw.Draw(tp).line([(0, 2), (tw, 2)], fill=(255, 250, 238, 90), width=2)
                sheet.alpha_composite(tp, (cx, -6))
        if with_text:
            sheet.alpha_composite(sp, (padx, pady))
        return sheet

    sheet, bare = build(True), build(False)
    d0 = np.abs(np.asarray(sheet, np.float32)[..., :3] - np.asarray(bare, np.float32)[..., :3]).sum(2)
    d0 = d0 * (np.asarray(sheet, np.float32)[..., 3] > 250)
    ys, xs = np.where(d0 > 24)
    ink_box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1) if len(xs) \
        else (padx, pady, padx + sp.width, pady + sp.height)

    sh, pad = shadow_of(sheet, blur=15, off=(9, 13), alpha=150)
    if rotate:
        sh = sh.rotate(rotate, expand=True, resample=Image.BICUBIC)
        ink_box = _rotate_box(ink_box, sheet.size, rotate, sh.size)
        pad = 0
    ink_box = tuple(int(v + pad) if not rotate else int(v) for v in ink_box)
    return dict(sprite=sh, box=ink_box, pad=pad)


def _rotate_box(box, old, ang, new):
    cx, cy = old[0] / 2.0, old[1] / 2.0
    th = math.radians(ang)
    pts = [(box[0], box[1]), (box[2], box[1]), (box[2], box[3]), (box[0], box[3])]
    out = []
    for x, y in pts:
        dx, dy = x - cx, y - cy
        out.append((dx * math.cos(th) + dy * math.sin(th) + new[0] / 2.0,
                    -dx * math.sin(th) + dy * math.cos(th) + new[1] / 2.0))
    xs = [p[0] for p in out]
    ys = [p[1] for p in out]
    return (min(xs), min(ys), max(xs), max(ys))


def torn_rect(w, h, paper=PAPER, seed=3, edge=7):
    """a paper fragment with a torn edge"""
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


def stamp_sprite(text, size=76, ink=BURG, paper=PAPER_2):
    sp = text_sprite(text, size, ink)
    w, h = sp.width + 76, sp.height + 60
    # a stamp lives on paper: give it a torn document fragment so the burgundy ink
    # always sits on a light ground, never straight on footage
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sheet = torn_rect(w, h, paper=paper, seed=17)
    im.alpha_composite(sheet)
    d = ImageDraw.Draw(im)
    for i in range(3):
        d.rounded_rectangle([16 - i, 14 - i, w - 16 + i, h - 14 + i], radius=8,
                            outline=ink + (170 - i * 45,), width=3)
    im.alpha_composite(sp, (38, 30))
    a = np.asarray(im, np.float32)
    al = a[..., 3]
    noise = np.random.default_rng(9).normal(0, 26, al.shape)
    a[..., 3] = np.clip(al + noise * (al > 0), 0, 255)
    im = Image.fromarray(a.astype(np.uint8))
    sh, pad = shadow_of(im, blur=10, off=(5, 7), alpha=110)
    return dict(sprite=sh, box=(pad + 38, pad + 30, pad + 38 + sp.width, pad + 30 + sp.height))


def pin(dst, x, y, t, t0, r=13, col=GOLD):
    """a brass pin that drops in and settles"""
    if t < t0:
        return dst
    u = min(1.0, (t - t0) / 0.22)
    drop = (1 - u) ** 3 * 34
    a = int(255 * min(1.0, (t - t0) / 0.10))
    lay = Image.new('RGBA', (r * 6, r * 6), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx = cy = r * 3
    d.ellipse([cx - r * 1.4, cy - r * 1.4 + 4, cx + r * 1.4, cy + r * 1.4 + 4], fill=(0, 0, 0, 90))
    d.ellipse([cx - r, cy - r - drop, cx + r, cy + r - drop],
              fill=col + (a,), outline=(255, 248, 232, a), width=2)
    d.ellipse([cx - r * 0.34, cy - r * 0.5 - drop, cx + r * 0.22, cy + r * 0.12 - drop],
              fill=(255, 250, 238, a))
    dst.alpha_composite(lay, (int(x - r * 3), int(y - r * 3)))
    return dst


# ---------------------------------------------------------------- brand

LOGO = None


def logo():
    global LOGO
    if LOGO is None:
        im = Image.open(os.path.join(GD, '01-logo-horizontal-light-bg.png')).convert('RGBA')
        # the supplied lockup ships a real alpha channel: use it, do not re-key it
        im = im.crop(im.split()[3].getbbox())
        a = np.asarray(im, np.float32)
        out = np.zeros_like(a)
        out[..., 0], out[..., 1], out[..., 2] = GOLD_HI
        out[..., 3] = np.clip(a[..., 3] * 1.6, 0, 255)
        LOGO = Image.fromarray(out.astype(np.uint8))
    return LOGO


def place_logo(dst, w=300, x=76, y=H - 150, alpha=1.0, t=None, draw_under=0.0):
    lg = logo()
    s = w / lg.width
    lg = lg.resize((int(lg.width * s), int(lg.height * s)), Image.LANCZOS)
    if alpha < 1.0:
        a = lg.split()[3].point(lambda v: int(v * alpha))
        lg.putalpha(a)
    dst.alpha_composite(lg, (int(x), int(y)))
    if draw_under > 0:
        d = ImageDraw.Draw(dst)
        yl = y + lg.height + 12
        d.line([(x, yl), (x + int(lg.width * draw_under), yl)], fill=GOLD + (220,), width=2)
    return dst


# ---------------------------------------------------------------- finishing

_GRAIN = None
_VIG = None


def grain(i):
    """per-frame film grain, seeded by the frame number.

    A four-frame cycle was not enough: a slow push moves less than a pixel per frame,
    the resample quantises that away, and two frames then differed only by repeated
    grain — which the static detector correctly read as a freeze. Real grain is unique
    on every frame, so the noise floor is unique too.
    """
    global _GRAIN
    if _GRAIN is None:
        _GRAIN = {}
    k = int(i) % 900
    if k not in _GRAIN:
        if len(_GRAIN) > 12:
            _GRAIN.clear()
        base = _GRAIN.get('_base')
        if base is None:
            base = np.random.default_rng(5).normal(0, 5.2, (H, W)).astype(np.float32)
            _GRAIN['_base'] = base
        r = np.random.default_rng(1000 + k)
        oy, ox = r.integers(0, H), r.integers(0, W)
        _GRAIN[k] = np.roll(np.roll(base, oy, 0), ox, 1)
    return _GRAIN[k]


def vignette():
    global _VIG
    if _VIG is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
        _VIG = np.clip(1.0 - 0.42 * np.clip(r - 0.55, 0, 3) ** 1.6, 0.35, 1.0)
    return _VIG


def finish(im, frame_i=0, grain_amt=1.0, vig=1.0):
    a = np.asarray(im.convert('RGB'), np.float32)
    a *= vignette()[..., None] ** vig
    a += grain(frame_i)[..., None] * grain_amt
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def fade_to_black(im, k):
    if k >= 1:
        return im
    a = np.asarray(im, np.float32) * max(0.0, k)
    return Image.fromarray(a.astype(np.uint8))
