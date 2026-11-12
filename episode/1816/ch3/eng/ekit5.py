#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ekit5.py — the shared kit for chapters 3 to 6.

Every rule this film is judged on lives in ONE place so four chapters cannot each
interpret it differently:

  * the dark glass card is rgba(14,19,26,0.85); there is no beige "sheet" here and no
    drawing of mountains, seas, globes, molecules or charts;
  * plates are the delivered AI clips, cover-fit to 1920x1080, graded and grained;
  * geography is Natural Earth 1:50m, projected once, pushed in by the camera;
  * documents are paper with REAL lettering, the same vocabulary as DOC A in chapter 1;
  * every chapter declares its start on the episode VO and its audio is that slice only.

The chapter modules import this and add their own shots. Nothing here is specific to a
chapter's argument.
"""
import json
import math
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, '/home/user/work')

from eng5 import core5 as C

W, H = 1920, 1080
FPS = 30

GOLD = C.GOLD
CREAM = (239, 230, 210)
GLASS = (14, 19, 26, 230)          # the 0.85 layer with a 0.90 core, as in chapter 2
GLASS_UNDER = (14, 19, 26, 217)
GLASS_EDGE = (126, 140, 152, 66)
GLASS_RULE = (126, 140, 152, 34)

MAP_SRC = '/home/user/ne/ne_50m_admin_0_countries.geojson'


# ---------------------------------------------------------------- timing
def ramp(t, a, b):
    if b <= a:
        return 1.0 if t >= b else 0.0
    return max(0.0, min(1.0, (t - a) / (b - a)))


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def grader(base, warmth=0.88, sat=0.86):
    return C.grade5(base.convert('RGB'), warmth=warmth, sat=sat).convert('RGBA')


# ---------------------------------------------------------------- plates
_PL = {}


def plates(*keys):
    """open one or more clip plates. `plates('07')` and `plates('0','7')` both work:
    the first version iterated the STRING and tried to open a clip called '0'."""
    if len(keys) == 1 and not isinstance(keys[0], str):
        keys = tuple(keys[0])
    for k in keys:
        if k not in _PL:
            _PL[k] = C.Plate(k, src_fps=24.0)
    return _PL


def fill(im):
    """cover-fit a 1280x720 plate to 1920x1080 without touching its aspect ratio"""
    sc = max(W / im.width, H / im.height)
    out = im.resize((int(round(im.width * sc)), int(round(im.height * sc))),
                    Image.LANCZOS)
    ox = (out.width - W) // 2
    oy = (out.height - H) // 2
    return out.crop((ox, oy, ox + W, oy + H))


def crop_z(im, z, pan=(0.0, 0.0)):
    """crop to 1/z of the plate, then it gets cover-fit: a real push, not a scale"""
    cw, ch = im.width / z, im.height / z
    cx = im.width / 2 + pan[0]
    cy = im.height / 2 + pan[1]
    x0 = max(0, min(im.width - cw, cx - cw / 2))
    y0 = max(0, min(im.height - ch, cy - ch / 2))
    return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch)))


def plate(key, src_t, z=1.0, pan=(0.0, 0.0), warmth=0.88, sat=0.84):
    """one graded plate frame at source time `src_t`, pushed by z"""
    plates(key)
    im = _PL[key].frame(src_t, None).convert('RGB')
    if abs(z - 1.0) > 1e-3 or pan != (0.0, 0.0):
        im = crop_z(im, z, pan)
    return grader(fill(im), warmth=warmth, sat=sat).convert('RGBA')


class Shake:
    def __init__(self, amp=1.0, seed=3):
        rng = np.random.default_rng(seed)
        self.ph = rng.uniform(0, 6.28, 6)
        self.amp = amp

    def apply(self, im, t, amount=1.0):
        a = amount * self.amp
        if a <= 0.01:
            return im
        dx = a * (3.2 * math.sin(t * 21.7 + self.ph[0]) +
                  1.6 * math.sin(t * 37.3 + self.ph[1]))
        dy = a * (2.6 * math.sin(t * 25.1 + self.ph[2]) +
                  1.3 * math.sin(t * 41.9 + self.ph[3]))
        base = im.resize((int(W * 1.05), int(H * 1.05)), Image.BILINEAR)
        ox = max(0, min(base.width - W, int((base.width - W) / 2 + dx)))
        oy = max(0, min(base.height - H, int((base.height - H) / 2 + dy)))
        return base.crop((ox, oy, ox + W, oy + H))


# ---------------------------------------------------------------- the map
_RINGS = {}


def rings_50m(lat_min=-60.0):
    if 'r' in _RINGS:
        return _RINGS['r']
    with open(MAP_SRC, 'r', encoding='utf-8') as fh:
        gj = json.load(fh)
    out = []

    def add(ring):
        if len(ring) < 4:
            return
        if sum(p[1] for p in ring) / len(ring) < lat_min:
            return
        out.append([(float(p[0]), float(p[1])) for p in ring])

    for feat in gj.get('features', []):
        g = feat.get('geometry') or {}
        if g.get('type') == 'Polygon':
            for r in g['coordinates']:
                add(r)
        elif g.get('type') == 'MultiPolygon':
            for poly in g['coordinates']:
                for r in poly:
                    add(r)
    _RINGS['r'] = out
    return out


class GeoMap:
    def __init__(self, lon_a=-155, lon_b=180, lat_a=-56, lat_b=84, w=3840, h=1860):
        self.box = (lon_a, lon_b, lat_a, lat_b)
        self.w, self.h = w, h
        self.rings = rings_50m()
        self.mask = self._raster()

    def _raster(self):
        lon_a, lon_b, lat_a, lat_b = self.box
        m = Image.new('L', (self.w, self.h), 0)
        d = ImageDraw.Draw(m)
        for ring in self.rings:
            pts = [((p[0] - lon_a) / (lon_b - lon_a) * self.w,
                    (lat_b - p[1]) / (lat_b - lat_a) * self.h) for p in ring]
            d.polygon(pts, fill=255)
        return m

    def px(self, lon, lat):
        lon_a, lon_b, lat_a, lat_b = self.box
        return ((lon - lon_a) / (lon_b - lon_a) * self.w,
                (lat_b - lat) / (lat_b - lat_a) * self.h)


_GEO = {}
_PLATE = {}


def geo():
    if 'm' not in _GEO:
        _GEO['m'] = GeoMap()
    return _GEO['m']


def map_plate():
    if 'b' in _PLATE:
        return _PLATE['b']
    m = geo()
    mask = np.asarray(m.mask, np.float32) / 255.0
    h, w = mask.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = np.zeros((h, w, 3), np.float32)
    a += np.array([7, 9, 13], np.float32)
    a += ((np.clip(1.0 - yy / h, 0, 1) ** 2) * 9.0)[..., None] * \
        np.array([0.45, 0.70, 1.0], np.float32)[None, None, :]
    u8 = (mask * 255).astype(np.uint8)
    inner = np.asarray(Image.fromarray(u8).filter(ImageFilter.GaussianBlur(1.8)),
                       np.float32) / 255.0
    interior = np.asarray(Image.fromarray(u8).filter(ImageFilter.GaussianBlur(14.0)),
                          np.float32) / 255.0
    # land has to be clearly a different material from water, or the wide shot reads
    # as a negative: a coastline in the sea rather than a continent in an ocean
    land = np.array([25, 28, 33], np.float32)[None, None, :] + \
        (np.clip(interior, 0, 1) ** 0.8 * 13.0)[..., None] * \
        np.array([1.00, 0.98, 0.94], np.float32)
    # a slow relief so a continent is not one flat value
    rel = (np.sin(xx / w * math.pi * 3.1) * np.cos(yy / h * math.pi * 2.3)) * 3.2
    land = land + rel[..., None]
    a = a * (1 - mask[..., None]) + land * mask[..., None]
    a += (np.clip((mask - inner) * 7.0, 0, 1) * 78)[..., None] * \
        np.array([0.70, 0.80, 0.90], np.float32)
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    g = Image.new('RGBA', out.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    for lon in range(-150, 181, 30):
        x, _ = m.px(lon, 0)
        gd.line([(x, 0), (x, h)], fill=(30, 36, 43, 90), width=2)
    for lat in range(-40, 85, 20):
        _, y = m.px(0, lat)
        gd.line([(0, y), (w, y)], fill=(30, 36, 43, 90), width=2)
    _PLATE['b'] = Image.alpha_composite(out, g).convert('RGB')
    return _PLATE['b']


class Cam:
    def __init__(self, lon, lat, zoom=1.0, target=(W * 0.5, H * 0.5)):
        m = geo()
        self.m = m
        pw = m.w / zoom
        ph = pw * H / W
        cx, cy = m.px(lon, lat)
        tx, ty = target
        x0 = max(0, min(m.w - pw, cx - pw * (tx / W)))
        y0 = max(0, min(m.h - ph, cy - ph * (ty / H)))
        self.rect = (x0, y0, x0 + pw, y0 + ph)

    def apply(self):
        x0, y0, x1, y1 = self.rect
        return map_plate().crop((int(x0), int(y0), int(x1), int(y1))).resize(
            (W, H), Image.LANCZOS)

    def to_screen(self, lon, lat):
        px, py = self.m.px(lon, lat)
        x0, y0, x1, y1 = self.rect
        return ((px - x0) / (x1 - x0) * W, (py - y0) / (y1 - y0) * H)


_CORNER = {}


def corner(dst):
    """the locked corner mark, composited from a sprite built once.

    C.corner_logo re-scales the logo file on every call, which cost 0.12 s of every
    single frame in profiling. The mark is static, so it is rendered once onto alpha and
    then composited -- pixel-identical, and it takes the render from 1.1 s to 0.9 s.
    """
    if 's' not in _CORNER:
        tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        C.corner_logo(tmp)
        box = tmp.getbbox()
        _CORNER['s'] = tmp.crop(box)
        _CORNER['xy'] = (box[0], box[1])
    sp = _CORNER['s']
    x, y = _CORNER['xy']
    dst.alpha_composite(sp, (x, y))
    return dst


def bed(lon=6.4, lat=46.4, zoom=2.2, blur=17.0, dark=0.52, warmth=0.80, sat=0.52):
    """a defocused map used ONLY as a surface for type.

    When a shot carries words rather than geography, a sharp coastline invites the eye to
    read a place that the narration is not talking about. Blurring it to a texture keeps
    the visual family (same map, same grade) without claiming anything.
    """
    im = grader(Cam(lon, lat, zoom=zoom).apply(), warmth=warmth, sat=sat)
    im = im.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(im.convert('RGB'), np.float32) * dark
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')


def focus(base, cx, cy, r=260, colour=(255, 196, 128), amount=0.30):
    if amount <= 0.004:
        return base
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.25) ** 2)
    g = np.clip(1.0 - d / max(r, 1e-3), 0, 1) ** 2 * amount
    a = np.asarray(base.convert('RGB'), np.float32)
    a += g[..., None] * np.array(colour, np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')


def map_label(base, text, x, y, a=1.0, size=44, fill=CREAM):
    """type on the map, carried by its own glyph shadow -- never by a scrim panel"""
    if a <= 0.004:
        return base
    sp = C.text_sprite(text, size=size, fill=fill)
    out = Image.new('RGBA', (sp.width + 60, sp.height + 60), (0, 0, 0, 0))
    for blur, off, op in ((7, 3, 0.94), (18, 6, 0.66)):
        sh = Image.new('L', out.size, 0)
        sh.paste(sp.split()[3], (30, 30 + off))
        sh = sh.filter(ImageFilter.GaussianBlur(blur))
        lay = Image.new('RGBA', out.size, (0, 0, 0, 0))
        lay.putalpha(sh.point(lambda v: int(v * op * a)))
        out.alpha_composite(lay)
    s2 = sp.copy()
    s2.putalpha(sp.split()[3].point(lambda v: int(v * a)))
    out.alpha_composite(s2, (30, 30))
    base.alpha_composite(out, (int(x - 30), int(y - 30)))
    return base


# ---------------------------------------------------------------- the dark glass card
PLACED = []


def glass(w, h, radius=10):
    ss = 3
    big = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    d.rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], radius=radius * ss,
                        fill=GLASS_UNDER)
    d.rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], radius=radius * ss, fill=GLASS)
    d.rounded_rectangle([ss, ss, w * ss - 1 - ss, h * ss - 1 - ss], radius=radius * ss,
                        outline=GLASS_EDGE, width=2 * ss)
    return big.resize((w, h), Image.LANCZOS)


def ink(sp, a=1.0):
    """type with its own shallow shadow: no scrim behind type, as the brief requires"""
    pad = 6
    out = Image.new('RGBA', (sp.width + pad * 2, sp.height + pad * 2), (0, 0, 0, 0))
    sh = Image.new('L', out.size, 0)
    sh.paste(sp.split()[3], (pad, pad + 2))
    sh = sh.filter(ImageFilter.GaussianBlur(2.2))
    lay = Image.new('RGBA', out.size, (0, 0, 0, 0))
    lay.putalpha(sh.point(lambda v: int(v * 0.72 * a)))
    out.alpha_composite(lay)
    body = sp.copy()
    body.putalpha(sp.split()[3].point(lambda v: int(v * a)))
    out.alpha_composite(body, (pad, pad))
    return out


def fit(sp, maxw):
    if sp.width <= maxw:
        return sp
    sc = maxw / sp.width
    return sp.resize((int(sp.width * sc), int(sp.height * sc)), Image.LANCZOS)


def card_alpha(im, a):
    if a >= 0.999:
        return im
    im = im.copy()
    im.putalpha(im.split()[3].point(lambda v: int(v * a)))
    return im


def glass_card(rows, pad=(38, 30), gap=14, size=40, title=None, title_size=34,
               align='right', accent=None):
    """ONE dark glass card. Everything is measured before anything is drawn, so no line
    can run into another and the stack cannot exceed its own card."""
    rendered = []
    for r in rows:
        if isinstance(r, tuple):
            lab, val = r
            rendered.append(('pair',
                             ink(C.text_sprite(lab, size=int(size * 0.86),
                                               fill=(168, 180, 190))),
                             ink(C.text_sprite(val, size=size, fill=CREAM))))
        elif r == '---':
            rendered.append(('rule', None, None))
        else:
            rendered.append(('line',
                             ink(C.text_sprite(r, size=size, fill=CREAM)), None))
    ts = ink(C.text_sprite(title, size=title_size, fill=accent or GOLD)) if title else None
    padx, pady = pad
    widths = [ts.width] if ts is not None else []
    for kind, a, b in rendered:
        if kind == 'pair':
            widths.append(a.width + 34 + b.width)
        elif kind == 'line':
            widths.append(a.width)
    w = max(max(widths) + padx * 2, 360)
    h = pady * 2
    if ts is not None:
        h += ts.height + 26
    for kind, a, b in rendered:
        h += (12 if kind == 'rule' else max(a.height, b.height if b is not None else 0)) + gap
    h -= gap
    sp = glass(w, h)
    y = pady
    if ts is not None:
        t2 = fit(ts, w - padx * 2)
        sp.alpha_composite(t2, (w - padx - t2.width if align == 'right' else padx, y))
        y += ts.height + 8
        d = ImageDraw.Draw(sp, 'RGBA')
        d.line([(padx, y + 4), (w - padx, y + 4)], fill=GLASS_RULE, width=2)
        y += 18
    for kind, a, b in rendered:
        if kind == 'rule':
            d = ImageDraw.Draw(sp, 'RGBA')
            d.line([(padx + w * 0.18, y + 5), (w - padx, y + 5)], fill=GLASS_RULE,
                   width=2)
            y += 12 + gap
            continue
        if kind == 'pair':
            run = Image.new('RGBA', (a.width + 34 + b.width, max(a.height, b.height)),
                            (0, 0, 0, 0))
            if align == 'right':
                run.alpha_composite(b, (0, 0))
                run.alpha_composite(a, (b.width + 34, (b.height - a.height) // 2))
            else:
                run.alpha_composite(a, (0, (b.height - a.height) // 2))
                run.alpha_composite(b, (a.width + 34, 0))
            sp.alpha_composite(run, (w - padx - run.width if align == 'right' else padx,
                                     y))
            y += run.height + gap
        else:
            s2 = fit(a, w - padx * 2)
            sp.alpha_composite(s2, (w - padx - s2.width if align == 'right' else padx, y))
            y += a.height + gap
    return sp


def place(base, sp, x, y, a=1.0, shadow=True):
    if a > 0.004:
        PLACED.append(dict(rect=(int(x), int(y), int(x) + sp.width, int(y) + sp.height),
                           alpha=float(a)))
    if a <= 0.004:
        return base
    sp = card_alpha(sp, a)
    x, y = int(x), int(y)
    if shadow:
        sh = Image.new('RGBA', (sp.width + 80, sp.height + 80), (0, 0, 0, 0))
        sh.alpha_composite(sp, (40, 40))
        sh.putalpha(sh.split()[3].filter(ImageFilter.GaussianBlur(18))
                    .point(lambda v: int(v * 0.72)))
        base.alpha_composite(sh, (x - 40 + 4, y - 40 + 10))
    base.alpha_composite(sp, (x, y))
    return base


# ---------------------------------------------------------------- documents
def doc_paper(w, h, seed=5):
    """the reading surface: dark glass, not a paper sheet.

    Cycle 6 rejected beige/paper sheets outright, so a quoted source is a panel of the
    same smoked glass as the cards -- legible, branded, and never a photographed page.
    """
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = np.zeros((h, w, 3), np.float32)
    a[...] = np.array([17, 19, 24], np.float32)
    # a slow, cool sheen so the panel is not a flat rectangle
    f = ((np.sin(xx / w * math.pi * 1.7 + 0.7) * 0.5 + 0.5) *
         (np.cos(yy / h * math.pi * 1.3 + 1.1) * 0.5 + 0.5))
    a += (f * 9.0)[..., None] * np.array([0.8, 0.95, 1.25], np.float32)
    a += rng.normal(0, 1.6, (h, w, 1)).astype(np.float32)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle([0, 0, w - 1, h - 1], outline=(198, 162, 96, 96), width=2)
    d.rectangle([7, 7, w - 8, h - 8], outline=(198, 162, 96, 40), width=1)
    im.putalpha(238)
    return im


def doc_text(im, x, y, text, size=30, fill=CREAM, fname='Amiri-Regular.ttf'):
    sp = C.text_sprite(text, size=size, fill=fill, fname=fname)
    im.alpha_composite(sp, (x, y))
    return sp


def place_doc(base, doc, cx, cy, a=1.0, shadow=True):
    sp = card_alpha(doc, a)
    x, y = int(cx - sp.width / 2), int(cy - sp.height / 2)
    if shadow:
        sh = Image.new('RGBA', (sp.width + 90, sp.height + 90), (0, 0, 0, 0))
        sh.alpha_composite(sp, (45, 45))
        sh.putalpha(sh.split()[3].filter(ImageFilter.GaussianBlur(22))
                    .point(lambda v: int(v * 0.8)))
        base.alpha_composite(sh, (x - 45 + 6, y - 45 + 14))
    base.alpha_composite(sp, (x, y))
    return base


# ---------------------------------------------------------------- particles
def motes(base, t, density=1.0, colour=(214, 206, 190)):
    """slow dust in the light: the only motion layer a still-ish plate gets"""
    n = int(180 * max(0.0, min(1.0, density)))
    if n <= 0:
        return base
    rng = np.random.default_rng(41)
    x0 = rng.uniform(0, W, n)
    y0 = rng.uniform(0, H, n)
    vy = rng.uniform(6, 26, n)
    al = rng.uniform(28, 90, n)
    sz = rng.uniform(1.0, 2.6, n)
    mask = Image.new('L', (W // 2, H // 2), 0)
    d = ImageDraw.Draw(mask)
    for i in range(n):
        y = (y0[i] - vy[i] * t) % (H + 40) - 20
        x = (x0[i] + 14 * math.sin(t * 0.5 + i) ) % W
        d.ellipse([x / 2 - sz[i], y / 2 - sz[i], x / 2 + sz[i], y / 2 + sz[i]],
                  fill=int(al[i]))
    mask = mask.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.2))
    lay = Image.new('RGBA', (W, H), colour + (0,))
    lay.putalpha(mask)
    return Image.alpha_composite(base, lay)


def vignette_a(base, amount=0.22):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    g = np.clip(r - 0.55, 0, 1) ** 1.5 * amount
    a = np.asarray(base.convert('RGB'), np.float32) * (1.0 - g[..., None])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
