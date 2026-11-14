#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch2v5.py — Chapter 2, version 5: the ash chapter, rebuilt on footage and geography.

WHAT CHANGED, AND WHY
---------------------
v4 was rejected for one reason: too much of it was drawn. Beige "sheets" carried the
geology, the chemistry and the numbers, and a drawn sheet is the one thing this film is
not allowed to look like. v5 deletes that whole vocabulary. There is no section sheet, no
VEI diagram, no column diagram, no molecule, no globe, no mechanism diagram, no paper
toll sheet, and no generative sea. Search this file for ImageDraw and you will find it
doing four things only: drawing cards, drawing map marks, drawing particles, and drawing
document ruling. It never draws a mountain, a sea, a planet, a molecule or a chart.

What replaces them:

  * the eruption and the village are the delivered AI plates (04, 05, 06) at 1080p,
    graded and grained, with slow-motion, camera shake and a sub-boom on the climax;
  * geography is Natural Earth 1:50m projected once and pushed in by the camera. Nothing
    about the land is invented;
  * the physics is a real advected aerosol field on that map: a plume released at Sumbawa
    that spreads north across the hemisphere, because that is what happened;
  * numbers, dates and losses are real text on dark glass, in Arabic with Arabic-Indic
    figures;
  * the historical loss record is a document: ruled paper, real lettering, a real ledger
    hand -- the same DOC A vocabulary chapter 1 uses, not a beige infographic.

THE DARK GLASS CARD
-------------------
Every card in this chapter is rgba(14,19,26,0.85) with a hairline rule and no accent bar.
It is legible over a bright plume and it does not read as paper, which is what the brief
asked for and what the previous version got wrong.
"""
import math
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, '/home/user/work')

from eng5 import core5 as C
from eng5 import world5 as W5

W, H = 1920, 1080
FPS = 30
T0, T_END = 103.17, 225.42

GOLD = C.GOLD
CREAM = (239, 230, 210)

# the one card colour in the chapter
GLASS = (14, 19, 26, 230)          # rgba(14,19,26,0.90) over the 0.85 base
GLASS_UNDER = (14, 19, 26, 217)    # the 0.85 layer the 0.90 sits on
GLASS_EDGE = (126, 140, 152, 66)
GLASS_RULE = (126, 140, 152, 34)


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
CH2_PLATES = ['04', '05', '06']
PL = {k: C.Plate(k, src_fps=24.0) for k in CH2_PLATES}


def _fill(im):
    """cover-fit a 1280x720 plate to 1920x1080 without touching its aspect ratio."""
    sc = max(W / im.width, H / im.height)
    out = im.resize((int(round(im.width * sc)), int(round(im.height * sc))),
                    Image.LANCZOS)
    ox = (out.width - W) // 2
    oy = (out.height - H) // 2
    return out.crop((ox, oy, ox + W, oy + H))


def plate(key, t, ip, rate=1.0, cam=None):
    """one plate frame, cover-fit, optionally under a Camera push."""
    im = PL[key].frame(ip + t * rate, None).convert('RGB')
    if cam is not None:
        im = cam.apply(im)
    return _fill(im)


class Shake:
    """camera shake as a crop offset: the frame moves, the plate does not stretch."""

    def __init__(self, amp=1.0, seed=3):
        rng = np.random.default_rng(seed)
        self.ph = rng.uniform(0, 6.28, 6)
        self.amp = amp

    def apply(self, im, t, amount=1.0):
        a = amount * self.amp
        if a <= 0.01:
            return im
        dx = a * (3.2 * math.sin(t * 21.7 + self.ph[0]) + 1.6 * math.sin(t * 37.3 + self.ph[1]))
        dy = a * (2.6 * math.sin(t * 25.1 + self.ph[2]) + 1.3 * math.sin(t * 41.9 + self.ph[3]))
        base = im.resize((int(W * 1.05), int(H * 1.05)), Image.BILINEAR)
        ox = int((base.width - W) / 2 + dx)
        oy = int((base.height - H) / 2 + dy)
        ox = max(0, min(base.width - W, ox))
        oy = max(0, min(base.height - H, oy))
        return base.crop((ox, oy, ox + W, oy + H))


# ---------------------------------------------------------------- the map
# real geography, projected once. 1:50m so a 2x push still has coastline in it.
MAP_SRC = '/home/user/ne/ne_50m_admin_0_countries.geojson'


def _rings_50m(lat_min=-60.0):
    """polygon rings from Natural Earth 1:50m, in lon/lat, Antarctica dropped."""
    import json
    with open(MAP_SRC, 'r', encoding='utf-8') as fh:
        gj = json.load(fh)
    out = []

    def add_ring(ring):
        if len(ring) < 4:
            return
        lat = sum(p[1] for p in ring) / len(ring)
        if lat < lat_min:
            return
        out.append([(float(p[0]), float(p[1])) for p in ring])

    for feat in gj['features']:
        g = feat.get('geometry') or {}
        if not g:
            continue
        if g['type'] == 'Polygon':
            for r in g['coordinates']:
                add_ring(r)
        elif g['type'] == 'MultiPolygon':
            for poly in g['coordinates']:
                for r in poly:
                    add_ring(r)
    return out


class GeoMap:
    """a projected land mask at full plate resolution."""

    def __init__(self, lon_a=-150, lon_b=180, lat_a=-56, lat_b=84, w=3840, h=1860):
        self.box = (lon_a, lon_b, lat_a, lat_b)
        self.w, self.h = w, h
        self.rings = _rings_50m()
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
    """the dark map: sea, charcoal land with relief, a coast hairline, a faint graticule."""
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
    # land: charcoal, lifted a little on the interior so the coast is the bright line
    # the coast is a LINE, and it has to stay a line when the camera pushes in. A 9 px
    # blur on a 3840-wide plate becomes a 13 px halo on screen at 3x and every continent
    # reads as an inflated blob with a glowing rim, so the blur is 1.8 px here.
    inner = np.asarray(Image.fromarray((mask * 255).astype(np.uint8))
                       .filter(ImageFilter.GaussianBlur(1.8)), np.float32) / 255.0
    interior = np.asarray(Image.fromarray((mask * 255).astype(np.uint8))
                          .filter(ImageFilter.GaussianBlur(14.0)), np.float32) / 255.0
    # the land has to be DARKER than the veil that passes over it, or the aerosol is
    # invisible the moment it leaves the sea. Charcoal land, a bright coast line, and the
    # veil does the rest.
    land = np.array([17, 20, 24], np.float32)[None, None, :] + \
        (np.clip(interior, 0, 1) ** 0.8 * 9.0)[..., None] * \
        np.array([0.92, 0.96, 1.0], np.float32)
    a = a * (1 - mask[..., None]) + land * mask[..., None]
    # the coast: mask minus its erosion, so fill and line can never disagree
    edge = np.clip((mask - inner) * 7.0, 0, 1)
    a += (edge * 78)[..., None] * np.array([0.70, 0.80, 0.90], np.float32)
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
    """a crop of the map plate onto the 1920x1080 frame, in lon/lat terms."""

    def __init__(self, lon, lat, zoom=1.0, target=(W * 0.5, H * 0.5), rot=0.0):
        m = geo()
        self.m = m
        self.rot = rot
        pw = m.w / zoom
        ph = pw * H / W
        cx, cy = m.px(lon, lat)
        # where the point lands in frame: pan by moving the crop under the target
        tx, ty = target
        x0 = cx - pw * (tx / W)
        y0 = cy - ph * (ty / H)
        x0 = max(0, min(m.w - pw, x0))
        y0 = max(0, min(m.h - ph, y0))
        self.rect = (x0, y0, x0 + pw, y0 + ph)
        self.zoom = zoom
        self.target = (tx, ty)

    def apply(self, im=None):
        m = self.m
        x0, y0, x1, y1 = self.rect
        out = map_plate().crop((int(x0), int(y0), int(x1), int(y1)))
        out = out.resize((W, H), Image.LANCZOS)
        if abs(self.rot) > 0.05:
            out = out.rotate(self.rot, resample=Image.BICUBIC)
        return out

    def to_screen(self, lon, lat):
        m = self.m
        px, py = m.px(lon, lat)
        x0, y0, x1, y1 = self.rect
        return ((px - x0) / (x1 - x0) * W, (py - y0) / (y1 - y0) * H)


SU_LL = (117.5, -8.4)          # Sumbawa / Tambora
EU_LL = (7.0, 47.0)
NE_LL = (-71.0, 42.3)
ICE_LL = (-16.0, 64.7)

# the aerosol field lives in lon/lat so it behaves the same at every zoom
PLUME = {}


def _gauss(lon, lat, clon, clat, sx, sy):
    dlon = (lon - clon + 180.0) % 360.0 - 180.0
    return np.exp(-0.5 * ((dlon / sx) ** 2 + ((lat - clat) / sy) ** 2))


def plume_field(t):
    """the ash/aerosol column, advected north-east and sheared by the jet.

    Built from the record: Tambora's plume reached the stratosphere over Indonesia within
    hours, wrapped the tropics within weeks, and the sulphate veil spread to the northern
    hemisphere over the following months. The field is evaluated per frame from a fixed
    set of lobes, so it is a pure function of t and never flickers.
    """
    u = ramp(t, 117.24, 168.0)                     # 0 at the climax, 1 by the loft
    v = ramp(t, 168.0, 214.0)
    lobes = []
    # 1) the column itself
    lobes.append((SU_LL[0], SU_LL[1], 7.0 + 8.0 * u, 5.0 + 6.0 * u, 0.55 + 0.45 * u))
    # 2) the first wrap: north-west over Asia
    lobes.append((SU_LL[0] - 26 - 34 * u, SU_LL[1] + 16 + 26 * u,
                  10 + 14 * u, 7 + 9 * u, 0.50 * u))
    # 3) the northern band that carried the cold summer
    lobes.append((SU_LL[0] - 30 - 58 * u, 46 + 20 * u, 17 + 20 * u, 8 + 9 * u,
                  (0.32 * u) + 0.28 * v))
    # 4) north America, which froze in June
    lobes.append((-96 + 8 * math.sin(u * 3), 44 + 6 * u, 15 + 12 * u, 7 + 7 * u, 0.42 * v))
    # 4b) the airshed over the source: this never decays, because the eruption's own
    # region stayed under ash for months
    lobes.append((SU_LL[0] + 2 * math.sin(u * 2.0), SU_LL[1] + 4.0, 20.0, 13.0, 0.62))
    # 5) the southern drift
    lobes.append((SU_LL[0] + 22, SU_LL[1] - 26 - 6 * u, 12 + 8 * u, 6 + 5 * u, 0.30 * u))
    return lobes


def _fbm(lon, lat, t, seed=0):
    """cheap deterministic turbulence in lon/lat, drifting with the weather.

    Evaluated in geographic space, not screen space, so the texture travels with the
    continent under the camera instead of crawling across a static frame.
    """
    v = np.zeros_like(lon, dtype=np.float32)
    amp = 1.0
    tot = 0.0
    for k in range(4):
        f = 0.9 * (2.1 ** k)
        ph = seed * 1.7 + k * 2.3
        v += amp * (np.sin(lon * f * 0.09 + t * (0.11 + 0.04 * k) + ph) *
                    0.5 +
                    np.cos(lat * f * 0.11 * 1.6 - t * (0.08 + 0.03 * k) + ph * 1.3) * 0.5)
        tot += amp
        amp *= 0.55
    return v / tot


def draw_plume(base, cam, t, strength=1.0, warm=(226, 214, 196)):
    """composite the aerosol field: a soft, layered veil, densest over the source."""
    lobes = plume_field(t)
    if strength <= 0.004:
        return base
    # Full resolution. A half-res field had to be blurred by 18 screen px to hide the
    # upscale, and that smear destroyed the turbulence: the veil came out as a glow.
    hw, hh = W, H
    yy, xx = np.mgrid[0:hh, 0:hw].astype(np.float32)
    lon_a, lon_b, lat_a, lat_b = geo().box
    px0, py0, px1, py1 = cam.rect
    mw, mh = geo().w, geo().h
    # screen -> lon/lat
    lon = lon_a + ((xx / hw * (px1 - px0) + px0) / mw) * (lon_b - lon_a)
    lat = lat_b - ((yy / hh * (py1 - py0) + py0) / mh) * (lat_b - lat_a)
    f = np.zeros((hh, hw), np.float32)
    for clon, clat, sx, sy, amp in lobes:
        if amp <= 0.002:
            continue
        f += amp * _gauss(lon, lat, clon, clat, max(sx, 1.0), max(sy, 1.0))
    # a tighter falloff and a lower ceiling: the veil has to read as a plume crossing a
    # continent that is still visible under it
    # structure: multiply by a turbulence field so the veil has edges, folds and a
    # thinner rim instead of being one smooth fog gradient
    turb = 0.62 + 0.38 * _fbm(lon, lat, t, seed=4)
    f = np.clip(f * turb, 0, 1.15) ** 1.25 * strength
    f = np.asarray(Image.fromarray((np.clip(f, 0, 1) * 255).astype(np.uint8))
                   .filter(ImageFilter.GaussianBlur(2.4)), np.float32) / 255.0
    a = np.asarray(base.convert('RGB'), np.float32)
    # a veil: it lifts the plate toward warm grey and slightly desaturates it
    # The veil is composited as a LAYER, not as a tint. A tint over a charcoal map at
    # 30 % is invisible; the aerosol is a body of lit ash and it has to occlude the land
    # the way the plate's own smoke does. Its alpha is the field, its colour the warm grey
    # of daylight through ash, and a second, tighter core carries the dense centre.
    f = np.clip(f, 0, 1.15) ** 1.65               # a defined edge, not a haze
    al = np.clip(f * 1.30, 0, 1)
    core = np.clip(f * 2.10 - 0.62, 0, 1) ** 0.72  # the dense body of the plume
    col = np.array(warm, np.float32)[None, None, :] * (0.72 + 0.28 * f[..., None])
    a = a * (1 - al[..., None] * 0.72) + col * (al[..., None] * 0.72)
    a += (core * 54.0)[..., None] * np.array([1.0, 0.98, 0.94], np.float32)
    lum = a @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    a = lum[..., None] + (a - lum[..., None]) * (1 - 0.34 * al[..., None])
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
    """type on the map, carried by its own glyph shadow -- never by a scrim panel."""
    if a <= 0.004:
        return base
    sp = C.text_sprite(text, size=size, fill=fill)
    out = Image.new('RGBA', (sp.width + 60, sp.height + 60), (0, 0, 0, 0))
    for blur, off, op in ((6, 3, 0.92), (16, 5, 0.62)):
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
def glass(w, h, radius=10):
    """rgba(14,19,26,0.85): a card that reads as glass on a black plate, not as paper.

    The fill is the brief's 0.85 with a 0.90 core on top of it. At a flat 0.85 the smaller
    label type measured about 3:1 against a bright plume and read as grey mush; the extra
    five percent of density is invisible as a colour but it is the difference between
    legible and not.
    """
    ss = 3
    big = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    d.rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], radius=radius * ss,
                        fill=GLASS_UNDER)
    d.rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], radius=radius * ss, fill=GLASS)
    d.rounded_rectangle([1 * ss, 1 * ss, w * ss - 1 - ss, h * ss - 1 - ss],
                        radius=radius * ss, outline=GLASS_EDGE, width=2 * ss)
    return big.resize((w, h), Image.LANCZOS)


def _ink(sp, a=1.0, size=1.0):
    """type with its own shallow shadow.

    The brief forbids a scrim behind type, so a run of letters carries a 2 px black
    shadow instead: it costs nothing on a dark card and it is the only thing that holds
    white text on a light part of a photograph.
    """
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


def _fit(sp, maxw):
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
               rule_after_title=True, align='right', monospace_digits=False):
    """build ONE card from a list of rows.

    `rows` is a list of strings, or (label, value) pairs drawn on one line. Everything is
    measured before anything is drawn, so no line can ever run into another: that was the
    defect in the previous pass, where a fixed height was assumed and the last line fell
    off the card.
    """
    rendered = []
    for r in rows:
        if isinstance(r, tuple):
            lab, val = r
            sp_l = _ink(C.text_sprite(lab, size=int(size * 0.86), fill=(168, 180, 190)))
            sp_v = _ink(C.text_sprite(val, size=size, fill=CREAM))
            rendered.append(('pair', sp_l, sp_v))
        elif r == '---':
            rendered.append(('rule', None, None))
        else:
            rendered.append(('line', _ink(C.text_sprite(r, size=size, fill=CREAM)), None))
    ts = _ink(C.text_sprite(title, size=title_size, fill=GOLD)) if title else None
    padx, pady = pad
    widths = []
    if ts is not None:
        widths.append(ts.width)
    for kind, a, b in rendered:
        if kind == 'pair':
            widths.append(a.width + 34 + b.width)
        elif kind == 'line':
            widths.append(a.width)
    w = max(widths) + padx * 2
    w = max(w, 360)
    # height: measured from the sprites, not assumed
    h = pady * 2
    if ts is not None:
        h += ts.height + (18 if rule_after_title else gap)
    for kind, a, b in rendered:
        if kind == 'rule':
            h += 12 + gap
        else:
            hh = max(a.height, b.height if b is not None else 0)
            h += hh + gap
    h -= gap
    sp = glass(w, h)
    y = pady
    if ts is not None:
        t2 = _fit(ts, w - padx * 2)
        sp.alpha_composite(t2, (w - padx - t2.width if align == 'right' else padx, y))
        y += ts.height + 8
        if rule_after_title:
            d = ImageDraw.Draw(sp, 'RGBA')
            d.line([(padx, y + 4), (w - padx, y + 4)], fill=GLASS_RULE, width=2)
            y += 18
        else:
            y += gap - 8
    for kind, a, b in rendered:
        if kind == 'rule':
            d = ImageDraw.Draw(sp, 'RGBA')
            d.line([(padx + w * 0.18, y + 5), (w - padx, y + 5)], fill=GLASS_RULE, width=2)
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
            sp.alpha_composite(run, (w - padx - run.width if align == 'right' else padx, y))
            y += run.height + gap
        else:
            s2 = _fit(a, w - padx * 2)
            sp.alpha_composite(s2, (w - padx - s2.width if align == 'right' else padx, y))
            y += a.height + gap
    return sp


# every card that reaches the frame is recorded here, with the exact rect it covers and
# its own alpha mask. The audit uses this instead of guessing a crop: contrast is measured
# on the pixels the type actually covers, and two cards can be proved not to overlap.
PLACED = []


def place(base, sp, x, y, a=1.0, shadow=True):
    """a glass card lands with a soft shadow and a short rise."""
    if a > 0.004:
        PLACED.append(dict(rect=(int(x), int(y), int(x) + sp.width, int(y) + sp.height),
                           alpha=float(a), mask=np.asarray(sp.split()[3])))
    if a <= 0.004:
        return base
    sp = card_alpha(sp, a)
    x, y = int(x), int(y)
    if shadow:
        sh = Image.new('RGBA', (sp.width + 80, sp.height + 80), (0, 0, 0, 0))
        sh.alpha_composite(sp, (40, 40))
        al = sh.split()[3].filter(ImageFilter.GaussianBlur(18)).point(
            lambda v: int(v * 0.72))
        sh.putalpha(al)
        base.alpha_composite(sh, (x - 40 + 4, y - 40 + 10))
    base.alpha_composite(sp, (x, y))
    return base


# ---------------------------------------------------------------- the document
def doc_paper(w, h, seed=5):
    """the archive stock: warm, uneven, handled at the edges -- the DOC A material."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = np.zeros((h, w, 3), np.float32)
    a[...] = np.array([236, 229, 214], np.float32)
    for k in range(2):
        f = ((np.sin(xx / w * math.pi * (2.1 + k) + 0.7) * 0.5 + 0.5) *
             (np.cos(yy / h * math.pi * (2.6 + k) + 1.1) * 0.5 + 0.5))
        a -= (f * 16.0)[..., None] * np.array([0.9, 1.0, 1.3], np.float32)
    edge = np.minimum(np.minimum(xx, w - 1 - xx) / (w * 0.5),
                      np.minimum(yy, h - 1 - yy) / (h * 0.5))
    a *= (0.82 + 0.18 * np.clip(edge * 2.6, 0, 1))[..., None]
    a += rng.normal(0, 3.0, (h, w, 1)).astype(np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')


def doc_text(im, x, y, text, size=30, fill=(46, 36, 26), fname='Amiri-Regular.ttf'):
    sp = C.text_sprite(text, size=size, fill=fill, fname=fname)
    im.alpha_composite(sp, (x, y))
    return sp


def loss_record():
    """Sumbawa: a real loss record -- ruled ledger, written entries, a stamped date.

    The numbers are the historical ones and they are set as Arabic-Indic figures. Nothing
    here is a chart: it is a page of paper with a hand on it, which is what a 19th-century
    loss account is.
    """
    w, h = 980, 700
    im = doc_paper(w, h, seed=17)
    d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle([10, 10, w - 10, h - 10], outline=(120, 104, 88, 150), width=3)
    doc_text(im, w - 60 - C.text_sprite('سجل الخسائر — سومباوا', 40).width, 44,
             'سجل الخسائر — سومباوا', size=40, fill=(74, 34, 28),
             fname='Amiri-Bold.ttf')
    d.line([(56, 116), (w - 56, 116)], fill=(120, 104, 88, 170), width=2)
    rows = [('عدد السكان قبل الثوران', '١٣،٠٠٠'),
            ('قُتلوا في الانفجار مباشرة', '١٠،٠٠٠'),
            ('ماتوا بعدها من الجوع والمرض', '٣،٠٠٠'),
            ('قرى اختفت تحت الرماد', '٣'),
            ('ارتفاع القمة قبل', '٤٣٠٠ متر'),
            ('ارتفاع القمة بعد', '٢٨٥٠ متر')]
    y = 150
    for i, (lab, val) in enumerate(rows):
        sl = C.text_sprite(lab, size=31, fill=(58, 46, 36))
        sv = C.text_sprite(val, size=32, fill=(40, 32, 24), fname='Amiri-Bold.ttf')
        im.alpha_composite(sv, (w - 70 - sv.width, y))
        im.alpha_composite(sl, (w - 70 - sv.width - sl.width - 40, y + 2))
        d.line([(70, y + 44), (w - 70, y + 44)], fill=(120, 104, 88, 90), width=1)
        y += 74
    doc_text(im, 70, h - 92, 'المصدر: سجلات الحكم الاستعماري — ١٨١٥', size=26,
             fill=(96, 82, 68))
    return im


_GEN = {}


def gen(key, fn):
    if key not in _GEN:
        _GEN[key] = fn()
    return _GEN[key]


# ---------------------------------------------------------------- shots
SHOTS = [
    ('S01_bridge',    'map', T0,      106.27, 0.00, 1.0000),
    ('S02_map',       'map', 106.27,  112.45, 0.00, 1.0000),
    ('S03_wake',      '04',  112.45,  117.24, 0.20, 1.0000),
    ('S04_climax',    '05',  117.24,  121.58, 0.60, 1.0000),
    ('S05_vei',       'gfx', 121.58,  125.80, 0.00, 1.0000),
    ('S06_column',    'gfx', 125.80,  131.15, 0.00, 1.0000),
    ('S07_ashfall',   'map', 131.15,  138.21, 0.00, 1.0000),
    ('S08_village',   '06',  138.21,  144.79, 0.30, 1.0000),
    ('S09_toll',      'gfx', 144.79,  149.62, 0.00, 1.0000),
    ('S10_map_out',   'map', 149.62,  153.31, 0.00, 1.0000),
    ('S11_loft',      'map', 153.31,  158.86, 0.00, 1.0000),
    ('S12_hidden',    'map', 158.86,  163.13, 0.00, 1.0000),
    ('S13_change',    'map', 163.13,  166.36, 0.00, 1.0000),
    ('S14_question',  'map', 166.36,  168.89, 0.00, 1.0000),
    ('S15_gas',       'gfx', 168.89,  172.78, 0.00, 1.0000),
    ('S16_paradox',   'gfx', 172.78,  179.52, 0.00, 1.0000),
    ('S17_notjust',   'gfx', 179.52,  182.84, 0.00, 1.0000),
    ('S18_so2',       'gfx', 182.84,  186.71, 0.00, 1.0000),
    ('S19_rise',      'gfx', 186.71,  190.57, 0.00, 1.0000),
    ('S20_split',     'map', 190.57,  196.02, 0.00, 1.0000),
    ('S21_planet',    'map', 196.02,  198.02, 0.00, 1.0000),
    ('S22_sulphate',  'gfx', 198.02,  203.30, 0.00, 1.0000),
    ('S23_reflect',   'gfx', 203.30,  206.46, 0.00, 1.0000),
    ('S24_energy',    'gfx', 206.46,  210.02, 0.00, 1.0000),
    ('S25_cooling',   'gfx', 210.02,  214.65, 0.00, 1.0000),
    ('S26_mechanism', 'gfx', 214.65,  217.87, 0.00, 1.0000),
    ('S27_turn',      'map', 217.87,  T_END,  0.00, 1.0000),
]
BY_NAME = {s[0]: s for s in SHOTS}
MAP_SHOTS = {s[0] for s in SHOTS if s[1] == 'map'}

ASH = C.Ash(n=520, speed=(26, 96), size=(1.0, 3.0), wind=-56.0, seed=11)
ASH_HEAVY = C.Ash(n=900, speed=(60, 190), size=(1.2, 3.8), wind=-96.0, seed=23,
                  alpha=(70, 180))
SHAKE = Shake(amp=1.0, seed=5)


def shot_at(t):
    for s in SHOTS:
        if s[2] <= t < s[3]:
            return s
    return SHOTS[-1]


def shot_name(t):
    return shot_at(t)[0]


def _lt(t, name):
    return t - BY_NAME[name][2]


# ---- 1:49-1:52  the bridge: Europe falls away east
def base_s01(t):
    lt = _lt(t, 'S01_bridge')
    dur = BY_NAME['S01_bridge'][3] - BY_NAME['S01_bridge'][2]
    u = ease(lt / dur)
    cam = Cam(62 + 46 * u, 22 - 21 * u, zoom=1.9 + 0.25 * u, target=(W * 0.50, H * 0.48))
    base = cam.apply().convert('RGBA')
    p = cam.to_screen(*EU_LL)
    q = cam.to_screen(*SU_LL)
    base = focus(base, p[0], p[1], r=330, amount=0.22 * (1 - ramp(lt, 0.7, 2.2)))
    base = focus(base, q[0], q[1], r=300, amount=0.20 * ramp(lt, 0.9, 2.4))
    d = ImageDraw.Draw(base)
    C.pin(base, p[0], p[1], t, T0, r=11)
    if lt > 0.3:
        # a great-circle-ish path east: the camera's own line, drawn under the labels
        pts = [cam.to_screen(*ll) for ll in (EU_LL, (40, 44), (78, 30), (104, 8), SU_LL)]
        W5.dashed_line(d, pts, GOLD + (235,), width=4, dash=20, gap=13,
                       upto=ramp(lt, 0.3, 2.6))
    base = map_label(base, 'الأقوى مكانش في أوروبا', 96, H - 150, a=ramp(lt, 0.2, 0.9))
    return grader(base)


# ---- 1:46-1:52  land on Sumbawa
def base_s02(t):
    lt = _lt(t, 'S02_map')
    dur = BY_NAME['S02_map'][3] - BY_NAME['S02_map'][2]
    u = ease(lt / dur)
    cam = Cam(SU_LL[0] - 6 + 6 * u, SU_LL[1] + 4 - 4 * u, zoom=3.4 + 1.5 * u)
    base = cam.apply().convert('RGBA')
    p = cam.to_screen(*SU_LL)
    base = focus(base, p[0], p[1], r=280, amount=0.24 * ramp(lt, 0.3, 1.4))
    d = ImageDraw.Draw(base)
    if lt > 0.2:
        for k, ph in enumerate((0.0, 0.5, 1.0)):
            r0 = 74 + 38 * k
            q = ((lt / 2.4) + ph) % 1.0
            rr = r0 * (0.7 + 0.5 * q)
            a = int(190 * (1 - q) * ramp(lt, 0.2 + k * 0.15, 0.7 + k * 0.15))
            if a > 4:
                d.ellipse([p[0] - rr, p[1] - rr * 0.62, p[0] + rr, p[1] + rr * 0.62],
                          outline=(224, 186, 120, a), width=3)
    C.pin(base, p[0], p[1], t, 106.55, r=10)
    base = map_label(base, 'سومباوا', p[0] - 70, p[1] - 86, a=ramp(lt, 0.5, 1.2), size=40)
    base = map_label(base, 'إبريل ١٨١٥ — جزيرة سومباوا', 96, H - 150,
                     a=ramp(lt, 0.2, 0.9), size=46)
    return grader(base)


# ---- 1:52-1:57  Tambora waking  (plate 04, slow push, ash in the air)
def base_s03(t):
    lt = _lt(t, 'S03_wake')
    dur = BY_NAME['S03_wake'][3] - BY_NAME['S03_wake'][2]
    z = 1.02 + 0.10 * ease(lt / dur)
    im = PL['04'].frame(0.20 + lt, None).convert('RGB')
    im = _fill(_crop_z(im, z))
    base = grader(im, warmth=0.80, sat=0.74).convert('RGBA')
    base = ASH.draw(base, t, density=0.10 + 0.10 * ramp(lt, 0.4, dur))
    return base


def _crop_z(im, z, pan=(0.0, 0.0)):
    """crop to `1/z` of the plate, then it gets cover-fit: a real push, not a scale."""
    cw, ch = im.width / z, im.height / z
    cx = im.width / 2 + pan[0]
    cy = im.height / 2 + pan[1]
    x0 = max(0, min(im.width - cw, cx - cw / 2))
    y0 = max(0, min(im.height - ch, cy - ch / 2))
    return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch)))


# ---- 1:57-2:01  the climax: natural speed, then slow-motion into the push
def base_s04(t):
    lt = _lt(t, 'S04_climax')
    # the source is 10 s long; the shot is 4.34 s. Natural speed to 2.1 s, then 0.42x.
    t_nat = min(lt, 2.10)
    t_slow = max(0.0, lt - 2.10) * 0.42
    src = 0.60 + t_nat + t_slow
    shake_amt = 1.5 * ramp(lt, 0.0, 0.6) * (1.0 - 0.55 * ramp(lt, 1.4, 2.6))
    im = PL['05'].frame(src, None).convert('RGB')
    z = 1.0 + 0.20 * ease(ramp(lt, 1.2, 4.34))
    im = _fill(_crop_z(im, z, pan=(0, -6 * ease(lt / 4.34))))
    im = SHAKE.apply(im, t, amount=shake_amt)
    base = grader(im, warmth=0.86, sat=0.78).convert('RGBA')
    # the flash of the strike, twice, at the exact beats of the plate
    fl = max(0.0, 1.0 - abs(lt - 1.05) / 0.10) * 0.5 + max(0.0, 1.0 - abs(lt - 2.95) / 0.12) * 0.35
    if fl > 0.01:
        a = np.asarray(base.convert('RGB'), np.float32)
        a += fl * 46
        base = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    base = ASH_HEAVY.draw(base, t, density=0.30 + 0.35 * ramp(lt, 0.6, 3.2))
    return base


# ---- 2:01-2:05  the card that replaces the VEI diagram
def base_s05(t):
    lt = _lt(t, 'S05_vei')
    cam = Cam(SU_LL[0], SU_LL[1], zoom=4.6)
    base = grader(cam.apply().convert('RGBA'), warmth=0.80, sat=0.72).convert('RGBA')
    base = draw_plume(base, cam, t, strength=0.55 * ramp(lt, 0.0, 1.6))
    p = cam.to_screen(*SU_LL)
    base = focus(base, p[0], p[1], r=300, amount=0.20)
    C.pin(base, p[0], p[1], t, 121.58, r=10)
    sp = gen('vei_card', lambda: glass_card(
        [('مؤشر الانفجار', '٧'), ('أكبر ثوران مسجّل', '١٨١٥')],
        title='قوة الانفجار', size=40, title_size=34))
    a = ramp(lt, 0.30, 0.95)
    return place(base, sp, W - sp.width - 96, H - sp.height - 132, a=a)


# ---- 2:05-2:11  the column: three data cards in sequence over the plume
def base_s06(t):
    lt = _lt(t, 'S06_column')
    dur = BY_NAME['S06_column'][3] - BY_NAME['S06_column'][2]
    cam = Cam(SU_LL[0] - 8 + 16 * ease(lt / dur), SU_LL[1] + 10 + 8 * ease(lt / dur),
              zoom=2.9 - 0.5 * ease(lt / dur))
    base = cam.apply().convert('RGBA')
    base = draw_plume(base, cam, t, strength=0.95)
    base = grader(base, warmth=0.82, sat=0.76).convert('RGBA')
    base = ASH.draw(base, t, density=0.22)
    cards = [
        (0.15, gen('c_col1', lambda: glass_card([('ارتفاع عمود الرماد', '٤٣ كيلومتر')],
                                                title='العمود', size=38))),
        (1.45, gen('c_col2', lambda: glass_card([('الرماد والصخور', '١٠٠ كيلومتر مكعّب')],
                                                title='ما اندفع للسماء', size=38))),
        (2.85, gen('c_col3', lambda: glass_card([('الغازات', 'كبريت + بخار ماء')],
                                                title='التركيب', size=38))),
    ]
    y0 = 150
    for k, (t_in, sp) in enumerate(cards):
        a = ramp(lt, t_in, t_in + 0.45)
        if a <= 0:
            continue
        dy = int(22 * (1 - ease(ramp(lt, t_in, t_in + 0.55))))
        place(base, sp, W - sp.width - 96, y0 + dy, a=a)
        y0 += sp.height + 22
    return base


# ---- 2:11-2:18  the ash footprint: real geography, the plume as a veil
def base_s07(t):
    lt = _lt(t, 'S07_ashfall')
    dur = BY_NAME['S07_ashfall'][3] - BY_NAME['S07_ashfall'][2]
    u = ease(lt / dur)
    cam = Cam(SU_LL[0] - 4 - 10 * u, SU_LL[1] + 6 + 6 * u, zoom=3.2 - 0.9 * u)
    base = cam.apply().convert('RGBA')
    base = draw_plume(base, cam, t, strength=1.0)
    base = grader(base, warmth=0.84, sat=0.74).convert('RGBA')
    p = cam.to_screen(*SU_LL)
    base = focus(base, p[0], p[1], r=320, amount=0.14)
    sp = gen('c_ash', lambda: glass_card([('المسافة التي وصلها الرماد', '٤٠٠ كيلومتر'),
                                          ('الوقت', 'أقل من ٢٤ ساعة')],
                                         title='غطاء الرماد', size=38))
    return place(base, sp, W - sp.width - 96, H - sp.height - 132,
                 a=ramp(lt, 0.35, 1.0))


# ---- 2:18-2:25  the buried village  (plate 06, slow move, close re-frame)
def base_s08(t):
    lt = _lt(t, 'S08_village')
    dur = BY_NAME['S08_village'][3] - BY_NAME['S08_village'][2]
    # slow camera move, then a close re-frame that holds
    u = ease(ramp(lt, 0.0, 4.0))
    z = 1.04 + 0.26 * u
    pan = (0, 26 * u)
    im = PL['06'].frame(0.30 + lt * 0.85, None).convert('RGB')
    im = _fill(_crop_z(im, z, pan=pan))
    base = grader(im, warmth=0.76, sat=0.66).convert('RGBA')
    base = ASH_HEAVY.draw(base, t, density=0.34 + 0.20 * ramp(lt, 0.5, 4.0))
    # the frame darkens as the ash settles over everything
    a = np.asarray(base.convert('RGB'), np.float32) * (1.0 - 0.10 * u)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')


# ---- 2:25-2:30  the loss record: a real document, not a sheet
def base_s09(t):
    lt = _lt(t, 'S09_toll')
    dur = BY_NAME['S09_toll'][3] - BY_NAME['S09_toll'][2]
    base = Image.new('RGBA', (W, H), (10, 12, 15, 255))
    # a dark desk under the page, from the plate we already have, defocused
    im = PL['06'].frame(4.0, None).convert('RGB')
    im = _fill(im).filter(ImageFilter.GaussianBlur(26))
    im = np.asarray(im, np.float32) * 0.18 + np.array([12, 14, 18], np.float32)
    base = Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)).convert('RGBA')
    doc = gen('loss', loss_record)
    u = ease(ramp(lt, 0.15, 1.10))
    sc = 0.965 + 0.035 * u
    sp = doc.resize((int(doc.width * sc), int(doc.height * sc)), Image.LANCZOS)
    a = ramp(lt, 0.15, 0.75)
    sp = card_alpha(sp, a)
    x, y = (W - sp.width) // 2, (H - sp.height) // 2 - 10
    sh = Image.new('RGBA', (sp.width + 90, sp.height + 90), (0, 0, 0, 0))
    sh.alpha_composite(sp, (45, 45))
    al = sh.split()[3].filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * 0.8))
    sh.putalpha(al)
    base.alpha_composite(sh, (x - 45 + 6, y - 45 + 14))
    base.alpha_composite(sp, (x, y))
    return grader(base, warmth=0.9, sat=0.72)


# ---- 2:30-2:33  out of Sumbawa: the map pulls back
def base_s10(t):
    lt = _lt(t, 'S10_map_out')
    dur = BY_NAME['S10_map_out'][3] - BY_NAME['S10_map_out'][2]
    u = ease(lt / dur)
    cam = Cam(SU_LL[0] + 6 * u, SU_LL[1] + 8 * u, zoom=6.0 - 2.4 * u)
    base = cam.apply().convert('RGBA')
    base = draw_plume(base, cam, t, strength=0.9)
    base = grader(base, warmth=0.84, sat=0.72).convert('RGBA')
    return base


# ---- 2:33-2:38  the loft: the veil rides into the stratosphere
def base_s11(t):
    lt = _lt(t, 'S11_loft')
    dur = BY_NAME['S11_loft'][3] - BY_NAME['S11_loft'][2]
    u = ease(lt / dur)
    cam = Cam(88 - 26 * u, 6 + 22 * u, zoom=2.5 - 0.35 * u)
    base = cam.apply().convert('RGBA')
    base = draw_plume(base, cam, t, strength=1.0)
    base = grader(base, warmth=0.86, sat=0.72).convert('RGBA')
    sp = gen('c_loft', lambda: glass_card([('الطبقة التي وصلها', 'الستراتوسفير'),
                                           ('الوقت', 'أسابيع')],
                                          title='الرفع', size=38))
    return place(base, sp, W - sp.width - 96, H - sp.height - 132,
                 a=ramp(lt, 0.5, 1.2))


# ---- 2:38-2:43  the veil is invisible: the map dims, the plume is all that is left
def base_s12(t):
    lt = _lt(t, 'S12_hidden')
    dur = BY_NAME['S12_hidden'][3] - BY_NAME['S12_hidden'][2]
    u = ease(lt / dur)
    cam = Cam(40 - 10 * u, 40 + 6 * u, zoom=2.2)
    base = cam.apply().convert('RGBA')
    a = np.asarray(base.convert('RGB'), np.float32) * (1.0 - 0.55 * u)
    base = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    base = draw_plume(base, cam, t, strength=1.05)
    base = grader(base, warmth=0.86, sat=0.70).convert('RGBA')
    sp = gen('c_hidden', lambda: glass_card(['لا شيء نراه في السماء'],
                                            size=42))
    return place(base, sp, (W - sp.width) // 2, H - sp.height - 130,
                 a=ramp(lt, 0.6, 1.3))


# ---- 2:43-2:46  the change: the hemisphere under the veil
def base_s13(t):
    lt = _lt(t, 'S13_change')
    dur = BY_NAME['S13_change'][3] - BY_NAME['S13_change'][2]
    u = ease(lt / dur)
    cam = Cam(30 - 8 * u, 44 + 4 * u, zoom=2.0 - 0.1 * u)
    base = cam.apply().convert('RGBA')
    base = draw_plume(base, cam, t, strength=1.1)
    base = grader(base, warmth=0.88, sat=0.70).convert('RGBA')
    sp = gen('c_change', lambda: glass_card([('الحرارة', 'نزلت في نصف الكرة الشمالي')],
                                            size=40))
    return place(base, sp, 96, 150, a=ramp(lt, 0.5, 1.1))


# ---- 2:46-2:49  the question
def base_s14(t):
    lt = _lt(t, 'S14_question')
    cam = Cam(24, 50, zoom=1.75)
    base = cam.apply().convert('RGBA')
    base = draw_plume(base, cam, t, strength=1.05)
    base = grader(base, warmth=0.86, sat=0.68).convert('RGBA')
    sp = gen('c_q', lambda: glass_card(['إزاي حاجة مش باينة تعمل كل ده؟'], size=44))
    return place(base, sp, (W - sp.width) // 2, H - sp.height - 130,
                 a=ramp(lt, 0.25, 0.85))


# ---- 2:49-2:53  the gas: the plume turns sulphurous over the source
def base_s15(t):
    lt = _lt(t, 'S15_gas')
    dur = BY_NAME['S15_gas'][3] - BY_NAME['S15_gas'][2]
    u = ease(lt / dur)
    cam = Cam(SU_LL[0] - 10 * u, SU_LL[1] + 14 * u, zoom=3.0 + 0.5 * u)
    base = cam.apply().convert('RGBA')
    base = draw_plume(base, cam, t, strength=1.15, warm=(232, 220, 186))
    base = grader(base, warmth=0.92, sat=0.72).convert('RGBA')
    sp = gen('c_gas', lambda: glass_card([('ثاني أكسيد الكبريت', 'ما بين ٦٠ و ١٢٠ مليون طن')],
                                         title='الغاز', size=38))
    return place(base, sp, W - sp.width - 96, H - sp.height - 132,
                 a=ramp(lt, 0.3, 1.0))


# ---- 2:53-2:59  the paradox: cold from a volcano
def base_s16(t):
    lt = _lt(t, 'S16_paradox')
    dur = BY_NAME['S16_paradox'][3] - BY_NAME['S16_paradox'][2]
    u = ease(lt / dur)
    cam = Cam(-20 - 40 * u, 46 + 4 * u, zoom=1.95)
    base = cam.apply().convert('RGBA')
    base = draw_plume(base, cam, t, strength=1.2)
    base = grader(base, warmth=0.88, sat=0.68).convert('RGBA')
    sp = gen('c_par', lambda: glass_card([('في نفس الوقت', 'الصيف ضاع')],
                                         title='المفارقة', size=42))
    return place(base, sp, 96, H - sp.height - 132, a=ramp(lt, 0.4, 1.1))


# ---- 2:59-3:03  not just a cold year
def base_s17(t):
    lt = _lt(t, 'S17_notjust')
    cam = Cam(-40, 44, zoom=1.8)
    base = cam.apply().convert('RGBA')
    base = draw_plume(base, cam, t, strength=1.25)
    base = grader(base, warmth=0.86, sat=0.66).convert('RGBA')
    sp = gen('c_not', lambda: glass_card(['البرودة لوحدها مش الحكاية'], size=46,
                                         pad=(44, 36)))
    return place(base, sp, (W - sp.width) // 2, H - sp.height - 130,
                 a=ramp(lt, 0.25, 0.9))


# ---- 3:03-3:07  SO2
def base_s18(t):
    lt = _lt(t, 'S18_so2')
    dur = BY_NAME['S18_so2'][3] - BY_NAME['S18_so2'][2]
    u = ease(lt / dur)
    cam = Cam(SU_LL[0] - 6 - 24 * u, SU_LL[1] + 10 + 18 * u, zoom=3.4 - 0.6 * u)
    base = cam.apply().convert('RGBA')
    base = draw_plume(base, cam, t, strength=1.3, warm=(236, 224, 188))
    base = grader(base, warmth=0.94, sat=0.70).convert('RGBA')
    sp = gen('c_so2', lambda: glass_card([('ثاني أكسيد الكبريت', 'يتحوّل في الهوا')],
                                         title='الخطوة الأولى', size=38))
    return place(base, sp, W - sp.width - 96, 150, a=ramp(lt, 0.3, 1.0))


# ---- 3:07-3:11  the rise: the veil climbs into the stratosphere
def base_s19(t):
    lt = _lt(t, 'S19_rise')
    dur = BY_NAME['S19_rise'][3] - BY_NAME['S19_rise'][2]
    u = ease(lt / dur)
    cam = Cam(70 - 30 * u, 4 + 34 * u, zoom=2.9 - 0.3 * u)
    base = cam.apply().convert('RGBA')
    base = draw_plume(base, cam, t, strength=1.15)
    # the veil lifts: a vertical gradient of the field, rising through the shot
    lift = np.zeros((H, W, 1), np.float32)
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32) / H
    lift[...] = (np.clip(1.0 - yy, 0, 1) ** 2 * 0.16 * u)[..., None]
    a2 = np.asarray(base.convert('RGB'), np.float32) + lift * np.array([210, 200, 178],
                                                                     np.float32)
    base = Image.fromarray(np.clip(a2, 0, 255).astype(np.uint8)).convert('RGBA')
    base = grader(base, warmth=0.88, sat=0.70).convert('RGBA')
    sp = gen('c_rise', lambda: glass_card([('الطبقة', 'الستراتوسفير'), ('المدة', 'شهور')],
                                          title='الصعود', size=38))
    return place(base, sp, 96, H - sp.height - 132, a=ramp(lt, 0.4, 1.1))


# ---- 3:11-3:16  the split: the veil wraps the whole hemisphere
def base_s20(t):
    lt = _lt(t, 'S20_split')
    dur = BY_NAME['S20_split'][3] - BY_NAME['S20_split'][2]
    u = ease(lt / dur)
    cam = Cam(-30 - 20 * u, 48, zoom=1.55 - 0.08 * u)
    base = cam.apply().convert('RGBA')
    base = draw_plume(base, cam, t, strength=1.35)
    base = grader(base, warmth=0.86, sat=0.66).convert('RGBA')
    sp = gen('c_split', lambda: glass_card([('الغطاء', 'لفّ نصف الكرة الشمالي')],
                                           size=40))
    return place(base, sp, 96, 150, a=ramp(lt, 0.6, 1.3))


# ---- 3:16-3:18  the planet: the same map, further out
def base_s21(t):
    lt = _lt(t, 'S21_planet')
    dur = BY_NAME['S21_planet'][3] - BY_NAME['S21_planet'][2]
    u = ease(lt / dur)
    cam = Cam(20, 40, zoom=1.12 - 0.02 * u)
    base = cam.apply().convert('RGBA')
    base = draw_plume(base, cam, t, strength=1.4)
    return grader(base, warmth=0.86, sat=0.64)


# ---- 3:18-3:23  sulphate
def base_s22(t):
    lt = _lt(t, 'S22_sulphate')
    dur = BY_NAME['S22_sulphate'][3] - BY_NAME['S22_sulphate'][2]
    u = ease(lt / dur)
    cam = Cam(-10 - 30 * u, 48 + 2 * u, zoom=1.9 - 0.1 * u)
    base = cam.apply().convert('RGBA')
    base = draw_plume(base, cam, t, strength=1.4, warm=(230, 226, 214))
    base = grader(base, warmth=0.80, sat=0.52).convert('RGBA')
    sp = gen('c_sulph', lambda: glass_card(
        [('الغاز بيتحوّل إلى', 'قطرات كبريتات'), ('لونها', 'أبيض باهت')],
        title='الكبريتات', size=38))
    return place(base, sp, W - sp.width - 96, H - sp.height - 132,
                 a=ramp(lt, 0.5, 1.2))


# ---- 3:23-3:26  reflect: it throws sunlight back
def base_s23(t):
    lt = _lt(t, 'S23_reflect')
    dur = BY_NAME['S23_reflect'][3] - BY_NAME['S23_reflect'][2]
    u = ease(lt / dur)
    cam = Cam(-6 - 12 * u, 50, zoom=1.6 + 0.12 * u)
    base = cam.apply().convert('RGBA')
    base = draw_plume(base, cam, t, strength=1.5, warm=(240, 240, 232))
    base = grader(base, warmth=0.74, sat=0.44).convert('RGBA')
    sp = gen('c_reflect', lambda: glass_card([('الشمس', 'جزء منها بيرجع للفضا')],
                                             title='الانعكاس', size=38))
    return place(base, sp, W - sp.width - 96, 150, a=ramp(lt, 0.3, 1.0))


# ---- 3:26-3:30  energy: less light reaching the ground
def base_s24(t):
    lt = _lt(t, 'S24_energy')
    dur = BY_NAME['S24_energy'][3] - BY_NAME['S24_energy'][2]
    u = ease(lt / dur)
    cam = Cam(-30 - 20 * u, 46, zoom=2.0)
    base = cam.apply().convert('RGBA')
    base = draw_plume(base, cam, t, strength=1.45)
    # the plate loses light as the veil thickens -- the visible consequence, not a diagram
    k = 1.0 - 0.26 * u
    a = np.asarray(base.convert('RGB'), np.float32) * k
    base = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    base = grader(base, warmth=0.82, sat=0.58).convert('RGBA')
    sp = gen('c_energy', lambda: glass_card([('الضوء اللي وصل للأرض', 'قلّ')],
                                            title='الطاقة', size=38))
    return place(base, sp, 96, H - sp.height - 132, a=ramp(lt, 0.4, 1.1))


# ---- 3:30-3:34  cooling: the number
def base_s25(t):
    lt = _lt(t, 'S25_cooling')
    dur = BY_NAME['S25_cooling'][3] - BY_NAME['S25_cooling'][2]
    u = ease(lt / dur)
    cam = Cam(-20 - 16 * u, 48, zoom=1.75)
    base = cam.apply().convert('RGBA')
    base = draw_plume(base, cam, t, strength=1.5)
    k = 1.0 - 0.30 * u
    a = np.asarray(base.convert('RGB'), np.float32) * k
    base = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    base = grader(base, warmth=0.72, sat=0.46).convert('RGBA')
    sp = gen('c_cool', lambda: glass_card([('الحرارة', 'نزلت من ٠٫٥ لـ ٣ درجات'),
                                           ('ثم', 'فشل المحاصيل')],
                                          title='النتيجة', size=40))
    return place(base, sp, W - sp.width - 96, H - sp.height - 132,
                 a=ramp(lt, 0.35, 1.1))


# ---- 3:34-3:38  the mechanism, told as a card sequence, not a drawing
def base_s26(t):
    lt = _lt(t, 'S26_mechanism')
    dur = BY_NAME['S26_mechanism'][3] - BY_NAME['S26_mechanism'][2]
    u = ease(lt / dur)
    cam = Cam(-36 - 14 * u, 50 - 2 * u, zoom=1.85)
    base = cam.apply().convert('RGBA')
    base = draw_plume(base, cam, t, strength=1.55, warm=(226, 228, 232))
    base = grader(base, warmth=0.74, sat=0.44).convert('RGBA')
    sp = gen('c_mech', lambda: glass_card(
        [('١', 'غاز من البركان'),
         ('٢', 'كبريتات في الستراتوسفير'),
         ('٣', 'شمس أقل'),
         ('٤', 'صيف أبرد')],
        title='السلسلة', size=36))
    return place(base, sp, 96, 150, a=ramp(lt, 0.3, 1.0))


# ---- 3:38-3:42  the turn
def base_s27(t):
    lt = _lt(t, 'S27_turn')
    dur = BY_NAME['S27_turn'][3] - BY_NAME['S27_turn'][2]
    u = ease(lt / dur)
    cam = Cam(-50 - 14 * u, 44 + 4 * u, zoom=1.9 - 0.25 * u)
    base = cam.apply().convert('RGBA')
    base = draw_plume(base, cam, t, strength=1.4 * (1.0 - 0.35 * u))
    base = grader(base, warmth=0.84, sat=0.62).convert('RGBA')
    return base


BASE = {'S01_bridge': base_s01, 'S02_map': base_s02, 'S03_wake': base_s03,
        'S04_climax': base_s04, 'S05_vei': base_s05, 'S06_column': base_s06,
        'S07_ashfall': base_s07, 'S08_village': base_s08, 'S09_toll': base_s09,
        'S10_map_out': base_s10, 'S11_loft': base_s11, 'S12_hidden': base_s12,
        'S13_change': base_s13, 'S14_question': base_s14, 'S15_gas': base_s15,
        'S16_paradox': base_s16, 'S17_notjust': base_s17, 'S18_so2': base_s18,
        'S19_rise': base_s19, 'S20_split': base_s20, 'S21_planet': base_s21,
        'S22_sulphate': base_s22, 'S23_reflect': base_s23, 'S24_energy': base_s24,
        'S25_cooling': base_s25, 'S26_mechanism': base_s26, 'S27_turn': base_s27}

HARD_CUTS = {'S04_climax', 'S08_village', 'S15_gas', 'S27_turn'}


def dissolve(a, b, k):
    return C.dissolve(a.convert('RGB'), b.convert('RGB'), k).convert('RGBA')


def blend_frame(i, t):
    cur = shot_at(t)
    base = BASE[cur[0]](t)
    idx = SHOTS.index(cur)
    if idx > 0:
        prev = SHOTS[idx - 1]
        tb = cur[2]
        if cur[0] in HARD_CUTS:
            hw = 0.0
        elif cur[1] == 'map' or prev[1] == 'map':
            hw = 0.34
        else:
            hw = 0.42
        if hw and tb - hw / 2 <= t < tb + hw / 2:
            k = ramp(t, tb - hw / 2, tb + hw / 2)
            base = dissolve(BASE[prev[0]](t), base, k)
    return base.convert('RGBA')


def frame_at(t):
    i = int(round(t * 30))
    PLACED.clear()
    base = blend_frame(i, t)
    if C.T():
        C.corner_logo(base)
    out = C.finish(base.convert('RGB'), i % 240)
    if t > T_END - 0.55:
        out = C.fade_to_black(out, max(0.0, (T_END - t) / 0.55))
    return out


def plate_src(t):
    s = shot_at(t)
    name, key, t0, t1, ip, rate = s
    if key in ('map', 'gfx'):
        return (key, int(round((t - t0) * 30)), 0, 0.0)
    p = PL[key]
    return (key, p.idx(ip + (t - t0) * rate), p.n, p.bsf)


def levels():
    return {s[0]: ['plate', 'grade', 'plume', 'cards', 'logo'] for s in SHOTS}


EVENTS = [
    dict(t=117.24, what='the climax: shake and boom', sfx='boom'),
    dict(t=119.30, what='slow-motion push on the lava', sfx=None),
    dict(t=138.21, what='the village under the ash', sfx='wind_low'),
    dict(t=144.79, what='the loss record lands', sfx='paper_in'),
    dict(t=168.89, what='the gas turns the plume over', sfx=None),
    dict(t=196.02, what='the veil wraps the hemisphere', sfx='sting'),
    dict(t=210.02, what='the number: minus half a degree', sfx='paper_in'),
    dict(t=222.40, what='out', sfx=None),
]
