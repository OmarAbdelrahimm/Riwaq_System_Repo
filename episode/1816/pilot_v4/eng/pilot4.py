#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eng4/pilot4.py — PILOT v4 (0:00-0:30) built on the supplied AI footage.

Six segments, cut to the measured voice:

  S1 0.00- 4.35  COLD OPEN     09_Line_075_Villa_Diodati_Exterior_Storm
  S2 4.35- 9.97  FARMERS       01_Line_002_Farmers_Snow_America
  S3 9.97-15.96  EUROPE        02_Line_003_Europe_Rain_Mud
  S4 15.96-22.42 MAP           Natural Earth, dark mode
  S5 22.42-28.97 MONSTER       03_Line_006_Hook_Frankenstein_Silhouette
  S6 28.97-30.00 RETURN        01_Line_002 (push in, corner logo)

Every overlay sits ON footage; no shot is a procedural plate.
"""
import math

import numpy as np
from PIL import Image, ImageDraw

from . import core4 as C
from . import world

W, H = C.W, C.H
HIDE_TEXT = [False]


def T():
    return not HIDE_TEXT[0]

# ---------------------------------------------------------------- assets
P09 = C.Plate('09')
P01 = C.Plate('01')
P02 = C.Plate('02')
P03 = C.Plate('03')


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def ramp(t, a, b):
    return max(0.0, min(1.0, (t - a) / max(1e-6, b - a)))


def slide_in(t, t0, dur=0.45, dist=90):
    """paper travelling into frame: returns (offset, alpha)"""
    u = ramp(t, t0, t0 + dur)
    e = 1 - (1 - u) ** 3
    return (1 - e) * dist, min(1.0, u * 2.2)


def put(dst, prop, x, y, alpha=1.0, dy=0.0):
    sp = prop['sprite']
    if alpha < 1.0:
        sp = sp.copy()
        sp.putalpha(sp.split()[3].point(lambda v: int(v * alpha)))
    # x,y is the ink top-left; the sprite carries shadow pad
    pad = prop.get('pad', 0)
    bx, by = prop['box'][0], prop['box'][1]
    dst.alpha_composite(sp, (int(x - bx), int(y - by + dy)))
    return dst


# ---------------------------------------------------------------- the map

MAP = None
MAP_W, MAP_H = 2600, 1462


def map_obj():
    global MAP
    if MAP is None:
        # the plate is built LARGER than the frame on purpose: a frame-sized plate
        # leaves the camera nothing to pan across, and a map that cannot pan reads as
        # a still no matter how the zoom eases
        MAP = world.Map(lon_a=-132, lon_b=150, lat_a=-30, lat_b=80,
                        x0=0, y0=0, w=MAP_W, h=MAP_H, ss=3)
    return MAP


def map_base():
    m = map_obj()
    bg = Image.new('RGB', (MAP_W, MAP_H), (8, 10, 13)).convert('RGBA')
    return Image.alpha_composite(bg, world.compose_map(bg, m, 0)).convert('RGB')


def haversine(a, b):
    R = 6371.0
    p1, p2 = math.radians(a[1]), math.radians(b[1])
    dp = p2 - p1
    dl = math.radians(b[0] - a[0])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


ROUTE_LL = [(-71.0, 42.3), (-58, 45.5), (-38, 50.0), (-14, 52.5), (8, 52.0),
            (28, 47.0), (44, 34.0), (58, 20.0), (74, 8.0), (92, -1.5),
            (108, -6.0), (117.5, -8.4)]
NE_LL = (-71.0, 42.3)
EU_LL = (10.0, 49.0)
SU_LL = (117.5, -8.4)


def thermometer(h=250, w=54, frac=0.78, seed=23):
    """a paper thermometer with a mercury column at `frac`"""
    pad = 26
    im = Image.new('RGBA', (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sheet = C.torn_rect(w + pad * 2, h + pad * 2, paper=C.PAPER_2, seed=seed, edge=6)
    im.alpha_composite(sheet)
    d = ImageDraw.Draw(im)
    x0, y0 = pad + 14, pad + 16
    x1, y1 = x0 + w - 28, y0 + h - 40
    d.rounded_rectangle([x0, y0, x1, y1], radius=(x1 - x0) // 2, outline=(120, 112, 98, 255), width=3)
    bulb = (x0 + x1) / 2
    d.ellipse([bulb - 17, y1 - 6, bulb + 17, y1 + 28], fill=C.BURG + (255,))
    top = y0 + 14 + (1 - frac) * (y1 - y0 - 28)
    d.rounded_rectangle([bulb - 7, top, bulb + 7, y1 + 6], radius=7, fill=C.BURG + (255,))
    for k in range(6):
        yy = y0 + 22 + k * (y1 - y0 - 44) / 5
        d.line([(x1 - 16, yy), (x1 - 4, yy)], fill=(96, 90, 78, 255), width=2)
    sh, spad = C.shadow_of(im, blur=13, off=(8, 11), alpha=145)
    return dict(sprite=sh, box=(spad + x0, spad + y0, spad + x1, spad + y1 + 30), pad=spad)


# ---------------------------------------------------------------- the mark

def mark(dst, width=260, cx=None, cy=None, prog=1.0, alpha=1.0, col=C.GOLD_HI):
    """the Riwaq portico, drawn as ink: jambs, lintel, pediment, keystone dot.

    `width` is the flat span between the jambs, so the mark can be sized by how
    much frame it should occupy instead of by an abstract multiplier.
    """
    cx = W / 2 if cx is None else cx
    cy = H / 2 if cy is None else cy
    half = width / 2.0
    jamb_h = width * 0.52
    ped_h = width * 0.30
    # local coordinates around (0,0): the anchor is applied once, at composite time
    base_y = jamb_h * 0.62
    top_y = base_y - jamb_h
    apex_y = top_y - ped_h
    stroke = max(4, int(width * 0.045))

    lay = Image.new('RGBA', (int(width * 3), int(width * 3)), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    ox, oy = width * 1.5, width * 1.5

    segs = [
        [(-half, base_y), (-half, top_y)],          # left jamb
        [(half, top_y), (half, base_y)],            # right jamb
        [(-half - stroke, top_y), (half + stroke, top_y)],   # lintel
        [(-half - stroke, top_y), (0, apex_y)],     # left pediment
        [(half + stroke, top_y), (0, apex_y)],      # right pediment
    ]
    tot = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in segs)
    want = tot * max(0.0, min(1.0, prog))
    col_a = col + (int(255 * max(0.0, min(1.0, alpha))),)
    for a, b in segs:
        if want <= 0:
            break
        L = max(1e-6, math.hypot(b[0] - a[0], b[1] - a[1]))
        f = min(1.0, want / L)
        d.line([(ox + a[0], oy + a[1]),
                (ox + a[0] + (b[0] - a[0]) * f, oy + a[1] + (b[1] - a[1]) * f)],
               fill=col_a, width=stroke)
        want -= L * f
    if prog > 0.95:
        dr = stroke * 0.95
        d.ellipse([ox - dr, oy + apex_y - dr, ox + dr, oy + apex_y + dr], fill=col_a)

    out = dst.copy()
    out.alpha_composite(lay, (int(cx - ox), int(cy - oy)))
    return out


# ---------------------------------------------------------------- shots

class Shot:
    def __init__(self, name, t0, t1, fn, layers=3):
        self.name, self.t0, self.t1, self.fn, self.layers = name, t0, t1, fn, layers


SNOW_FG = C.Snow(n=46, speed=(240, 380), size=(1.6, 3.2), wind=-40, seed=21, alpha=(40, 80))
SNOW_MID = C.Snow(n=300, speed=(90, 200), size=(0.9, 2.2), wind=-26, seed=7, alpha=(60, 140))
RAIN = C.Rain(n=430, seed=11, alpha=(22, 62))
ASH = C.Snow(n=150, speed=(14, 34), size=(1.0, 2.2), wind=7, seed=31, alpha=(30, 74))


def s1_cold_open(t):
    """black -> storm over the lake; the year stamps in; the grade turns cold"""
    u = ramp(t, 0.0, 2.0)
    cam = C.Camera(zoom=1.30 - 0.14 * ease(min(1.0, t / 4.35)), pan=(0, -20))
    base = P09.frame(t, cam)
    # warm -> cold inside the first two seconds
    warm = (1.14, 1.02, 0.86)
    cold = (0.86, 0.94, 1.10)
    mul = tuple(warm[i] + (cold[i] - warm[i]) * ease(u) for i in range(3))
    base = C.grade(base, mul=mul, sat=0.55 + 0.5 * ease(u), lift=0.01).convert('RGBA')

    # snow starts as the grade turns cold
    d = ramp(t, 1.0, 2.6)
    if d > 0:
        base = SNOW_MID.draw(base, t, density=0.35 * d)

    # label: once, at the start — "re-imagined", never per scene
    if 0.55 < t < 4.2 and T():
        a = min(1.0, (t - 0.55) / 0.4) * min(1.0, (4.2 - t) / 0.5)
        lab = C.paper_tag('مشاهد مُعاد تخيّلها', size=34, padx=22, pady=12, tape=False, seed=4)
        put(base, lab, 96, H - 150, alpha=0.92 * a)

    # the year, stamped on paper, landing on the word
    if t >= 2.92 and T():
        off, a = slide_in(t, 2.92, 0.42, 70)
        st = C.stamp_sprite('يونيو 1816', size=88)
        x = W - 700 + off
        y = 300
        base.alpha_composite(st['sprite'], (int(x - st['box'][0]), int(y - st['box'][1])))

    base = C.finish(base, int(t * 30), grain_amt=1.0)
    # hard cut in from black
    return C.fade_to_black(base, min(1.0, t / 0.18))


def s2_farmers(t):
    """the supplied farmers plate, slow push, snow thickening on the word"""
    lt = t - 4.35
    cam = C.Camera(zoom=1.04 + 0.09 * ease(lt / 5.62), pan=(10, 0), src=(1344, 768))
    base = P01.frame(t, cam)
    base = C.grade(base, mul=(0.90, 0.97, 1.08), sat=0.78, lift=0.012).convert('RGBA')

    d1 = 0.55 + 0.30 * ramp(t, 7.43, 8.65)
    base = SNOW_MID.draw(base, t, density=d1)
    base = SNOW_FG.draw(base, t, density=0.6, blur=1.6)

    if t >= 5.05 and T():
        off, a = slide_in(t, 5.05, 0.5, 80)
        tag = C.paper_tag('فلاحين · أمريكا', size=56, rotate=-1.6, seed=5)
        put(base, tag, 120 - off, 120, alpha=a)
        if T():
            C.pin(base, 146 - off, 106, t, 5.05)

    if t >= 6.25:
        frac = 0.80 - 0.42 * ease(ramp(t, 6.25, 7.10))
        th = thermometer(frac=frac)
        put(base, th, 150, 470, alpha=0.96)
    if t >= 7.43 and T():
        off, a = slide_in(t, 7.43, 0.5, 80)
        tag = C.paper_tag('والتلج بينزل عليه', size=52, rotate=1.4, seed=6)
        put(base, tag, W - 640 - off, H - 260, alpha=a)
        if T():
            C.pin(base, W - 614 - off, H - 274, t, 7.43)

    return C.finish(base, int(t * 30))


def s3_europe(t):
    """rain and mud; the ruined crop is called out on a torn paper strip"""
    lt = t - 9.97
    cam = C.Camera(zoom=1.16 - 0.10 * ease(lt / 5.99), pan=(-8, 0), src=(1280, 720))
    base = P02.frame(t, cam)
    base = C.grade(base, mul=(0.84, 0.93, 1.04), sat=0.72, lift=0.008).convert('RGBA')

    base = RAIN.draw(base, t, density=0.30 + 0.55 * ramp(t, 10.6, 11.9))
    base = SNOW_FG.draw(base, t, density=0.22, blur=1.8)

    if t >= 10.23 and T():
        off, a = slide_in(t, 10.23, 0.5, 80)
        tag = C.paper_tag('أوروبا · مطر وبرد', size=54, rotate=1.2, seed=8)
        put(base, tag, 110 - off, 116, alpha=a)
        if T():
            C.pin(base, 136 - off, 102, t, 10.23)

    if t >= 14.78 and T():
        off, a = slide_in(t, 14.78, 0.45, 70)
        tag = C.paper_tag('برد وتراب', size=46, rotate=1.8, seed=14)
        put(base, tag, 120 - off, 150, alpha=a)
        if T():
            C.pin(base, 146 - off, 136, t, 14.78)
    if t >= 13.65 and T():
        off, a = slide_in(t, 13.65, 0.55, 120)
        tag = C.paper_tag('المحاصيل ما كبرتش', size=50, rotate=-1.1, seed=9)
        put(base, tag, W - 700 - off, H - 250, alpha=a)

    return C.finish(base, int(t * 30))


def s4_map(t):
    """the continent push, the thread, the distance counter"""
    lt = t - 15.96
    m = map_obj()
    # a slow, constant drift on top of the push: the plate is never dead-still, and the
    # drift keeps every frame of the hold moving even where the map itself is empty
    # constant-speed drift plus a slow push: the coastlines move a full pixel or more
    # on every frame, so no frame pair can quantise onto the same picture
    cam = C.Camera(zoom=1.34 - 0.08 * (0.6 * ease(lt / 6.46) + 0.4 * (lt / 6.46)),
                   pan=(-120 + 200 * (lt / 6.46) + 9 * math.sin(lt * 0.7),
                        -40 + 70 * (lt / 6.46)),
                   src=(MAP_W, MAP_H))
    base = cam.apply(map_base()).convert('RGBA')
    # drifting ash over the map: slow, sparse, analytic
    base = ASH.draw(base, t, density=0.8)
    # a slow lamp sweep across the plate. The map is mostly flat dark, so without a
    # moving highlight a hold reads as a still frame no matter how the camera drifts.
    base = lamplight(base, t)

    def S(lonlat):
        x, y = m.px(*lonlat)
        return cam.to_screen(x, y)

    d = ImageDraw.Draw(base)

    # scrims for the type: a top band for the label, a bottom band for the counter.
    # alpha ramps smoothly and the colour is the map's own near-black, so the land
    # reads slightly brighter than the scrim and the map never looks washed out.
    base.alpha_composite(scrim(0, 200, 150, 0, invert=False), (0, 0))
    base.alpha_composite(scrim(H - 300, H, 0, 175, invert=False), (0, H - 300))

    # New England is pinned when the voice says the secret was not in these continents
    if t >= 16.53:
        p = S(NE_LL)
        C.pin(base, p[0], p[1], t, 16.53, r=11)
        if t >= 16.53:
            a = ramp(t, 16.6, 17.1)
            ring = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            rd = ImageDraw.Draw(ring)
            rr = 26 + 10 * a
            rd.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr],
                       outline=C.GOLD_HI + (int(200 * a),), width=2)
            base.alpha_composite(ring)

    # the thread: first a short leg (Europe), then the whole route on "thousands of km"
    pts = [S(ll) for ll in ROUTE_LL]
    if t >= 17.35:
        seg = pts[:5]
        u1 = ramp(t, 17.35, 19.04)
        world.dashed_line(d, seg, C.GOLD + (240,), width=4, dash=20, gap=14, upto=u1)
    if t >= 19.04:
        p = S(EU_LL)
        C.pin(base, p[0], p[1], t, 19.04, r=9)
    if t >= 19.72:
        u2 = ramp(t, 19.72, 21.46)
        world.dashed_line(d, pts, C.GOLD + (245,), width=5, dash=22, gap=15, upto=u2)
        p = S(EU_LL)
        C.pin(base, p[0], p[1], t, 19.72, r=9)
    if t >= 21.02:
        p = S(SU_LL)
        C.pin(base, p[0], p[1], t, 21.02, r=12)

    # distance counter, ink on the dark map: gold type on a dark scrim
    if t >= 20.36 and T():
        u = ramp(t, 20.36, 21.46)
        val = int(round(15000 * (u ** 0.75)))
        a = min(1.0, ramp(t, 20.36, 20.6))
        sp = C.text_sprite(f'+{val:,} كم'.replace(',', '٬'), size=116, fill=C.GOLD_HI)
        x0 = W - sp.width - 120
        y0 = H - sp.height - 110
        if a < 1:
            sp = sp.copy()
            sp.putalpha(sp.split()[3].point(lambda v: int(v * a)))
        base.alpha_composite(sp, (x0, y0))

    if t >= 15.96 and T():
        a = ramp(t, 16.0, 16.6)
        lab = C.text_sprite('السر مش في القارات', size=52, fill=C.GOLD_HI)
        let = 0.75 + 0.25 * a
        lab2 = lab.resize((int(lab.width * let), int(lab.height * let)), Image.LANCZOS)
        base.alpha_composite(lab2, (96, 74))

    return C.finish(base, int(t * 30))


def s5_monster(t):
    """the supplied silhouette plate, retimed so its lightning lands on the reveal"""
    lt = t - 22.42
    src_t = 0.30 + 0.44 * lt
    cam = C.Camera(zoom=1.10 - 0.06 * ease(lt / 6.55), pan=(0, 0), src=(1280, 720))
    base = P03.frame(src_t, cam)
    base = C.grade(base, mul=(1.02, 1.05, 1.16), sat=0.62, lift=0.012).convert('RGBA')

    # punch the plate's own flash: peaks measured at src 2.4 s and 2.8 s
    f = 0.0
    for peak in (2.40, 2.80):
        d = src_t - peak
        if -0.05 < d < 0.55:
            f = max(f, 0.20 * math.exp(-max(0.0, d) * 7.0))
    base = C.apply_flash(base, f)

    # the brand sting: a two-frame step back, then the mark draws itself
    if t >= 22.42:
        k = min(1.0, (t - 22.42) / 0.10)
        base = C.fade_to_black(base, 0.35 + 0.65 * k)
    if 23.10 <= t <= 25.70:
        prog = ramp(t, 23.10, 24.30)
        fade = 1.0 if t < 25.10 else max(0.0, (25.70 - t) / 0.60)
        if prog > 0.95 and 24.30 <= t <= 24.52:
            # the keystone dot lands: a short, visible emphasis on the resolve
            base = C.apply_flash(base, 0.06 * (1 - abs(t - 24.36) / 0.12))
        # hold the footage back while the mark is up so the sting reads as a title beat
        base = C.fade_to_black(base, 0.42 + 0.58 * min(1.0, ramp(t, 23.1, 23.4)))
        base = mark(base, width=300, cx=W / 2, cy=H / 2 - 40, prog=prog,
                    alpha=min(1.0, 0.96 * fade))

    if t >= 26.28 and T():
        off, a = slide_in(t, 26.28, 0.5, 80)
        tag = C.paper_tag('أشهر وحش في الأدب', size=54, rotate=-1.3, seed=12)
        put(base, tag, 104, H - 268 - off * 0.2, alpha=a)
        if T():
            C.pin(base, 130, H - 282, t, 26.28)

    return C.finish(base, int(t * 30))


def s6_return(t):
    """back to what people saw; the corner logo takes over from the sting"""
    lt = t - 28.97
    cam = C.Camera(zoom=1.30 + 0.06 * ease(lt / 1.03), pan=(-70, -46), src=(1344, 768))
    base = P01.frame(9.2 + lt, cam)
    base = C.grade(base, mul=(0.88, 0.95, 1.07), sat=0.72).convert('RGBA')
    base = SNOW_MID.draw(base, t, density=0.5)
    if t >= 28.97:
        C.place_logo(base, w=300, alpha=min(1.0, ramp(t, 28.97, 29.25)))
    return C.finish(C.fade_to_black(base, max(0.0, (30.0 - t) / 0.35)), int(t * 30))


SHOTS = [
    Shot('S1_cold_open', 0.00, 4.35, s1_cold_open, 4),
    Shot('S2_farmers', 4.35, 9.97, s2_farmers, 5),
    Shot('S3_europe', 9.97, 15.96, s3_europe, 4),
    Shot('S4_map', 15.96, 22.42, s4_map, 5),
    Shot('S5_monster', 22.42, 28.97, s5_monster, 5),
    Shot('S6_return', 28.97, 30.00, s6_return, 3),
]


def lamplight(base, t, amp=44):
    """a soft radial highlight drifting over the map: low amplitude, large area"""
    cx = W * (0.30 + 0.16 * math.sin(t * 0.55))
    cy = H * (0.42 + 0.10 * math.cos(t * 0.43))
    yy, xx = np.mgrid[0:H:4, 0:W:4].astype(np.float32)
    r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (W * 0.62)
    g = np.clip(1.0 - r, 0, 1) ** 2 * amp
    g = np.asarray(Image.fromarray(g.astype(np.uint8)).resize((W, H), Image.BILINEAR),
                   np.float32)
    a = np.asarray(base.convert('RGB'), np.float32) + g[..., None]
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    out.putalpha(base.split()[3])
    return out


def scrim(y0, y1, a_top, a_bot, invert=False, col=(8, 10, 13)):
    h = max(1, y1 - y0)
    g = Image.new('L', (1, h))
    gd = ImageDraw.Draw(g)
    for i in range(h):
        f = i / (h - 1)
        gd.point((0, i), fill=int(a_top + (a_bot - a_top) * f))
    g = g.resize((W, h), Image.BILINEAR)
    lay = Image.new('RGBA', (W, h), col + (0,))
    lay.putalpha(g)
    return lay


def shot_at(t):
    for s in SHOTS:
        if s.t0 <= t < s.t1:
            return s
    return SHOTS[-1]


# events: t, what becomes visible, and the cue the mixer places
EVENTS = [
    dict(t=2.92, what='stamp «يونيو 1816»', sfx='stamp', shot='S1'),
    dict(t=4.02, what='cold grade completes, snow thickens', sfx='sleet', shot='S1'),
    dict(t=5.05, what='tag فلاحين · أمريكا', sfx='pin', shot='S2'),
    dict(t=6.25, what='thermometer needle drops on زرعهم', sfx='needle', shot='S2'),
    dict(t=7.43, what='tag والتلج بينزل + snow thickens', sfx='pin', shot='S2'),
    dict(t=8.65, what='snow begins (design hit)', sfx='sleet', shot='S2'),
    dict(t=10.23, what='tag أوروبا · مطر وبرد', sfx='pin', shot='S3'),
    dict(t=11.02, what='rain doubles on «مطر»', sfx='sleet', shot='S3'),
    dict(t=11.52, what='rain hammering at full weight', sfx='water', shot='S3'),
    dict(t=12.26, what='sleet layer in', sfx='sleet', shot='S3'),
    dict(t=14.78, what='strip برد pinned على تكبر', sfx='paper_slide', shot='S3'),
    dict(t=13.65, what='strip المحاصيل ما كبرتش', sfx='paper_slide', shot='S3'),
    dict(t=16.53, what='New England pinned', sfx='pin', shot='S4'),
    dict(t=17.35, what='thread leg 1 draws', sfx='thread_draw', shot='S4'),
    dict(t=19.04, what='thread lands on Europe', sfx='pin', shot='S4'),
    dict(t=19.72, what='thread turns for Sumbawa', sfx='thread_draw', shot='S4'),

    dict(t=21.02, what='Sumbawa pinned + counter lands', sfx='pin', shot='S4'),

    dict(t=22.42, what='brand sting + dip', sfx='sting', shot='S5'),
    dict(t=23.10, what='mark draws', sfx='thread_draw', shot='S5'),
    dict(t=24.30, what='mark resolved (keystone dot)', sfx='thread_draw', shot='S5'),
    dict(t=25.60, what='mark clears, plate returns', sfx='paper_slide', shot='S5'),
    dict(t=26.28, what='tag أشهر وحش في الأدب', sfx='pin', shot='S5'),
    dict(t=27.19, what='plate lightning across the window', sfx='thunder', shot='S5'),
    dict(t=28.97, what='corner logo + return', sfx=None, shot='S6'),
]

EVENTS.sort(key=lambda e: e['t'])

# text elements for contrast measurement: (label, shot, t, rect on screen)
TEXTS = [
    ('disclaimer', 'S1', 2.20, (96, H - 150, 250, 44), 'ink on paper'),
    ('stamp 1816', 'S1', 3.60, (W - 700, 300, 470, 130), 'ink on paper'),
    ('tag USA', 'S2', 6.00, (120, 120, 430, 96), 'ink on paper'),
    ('tag snow', 'S2', 8.40, (W - 640, H - 260, 500, 90), 'ink on paper'),
    ('tag Europe', 'S3', 11.00, (110, 116, 470, 94), 'ink on paper'),
    ('tag crops', 'S3', 14.40, (W - 700, H - 250, 520, 86), 'ink on paper'),
    ('map counter', 'S4', 21.30, (W - 700, H - 230, 600, 170), 'gold on dark'),
    ('tag monster', 'S5', 27.00, (104, H - 268, 470, 92), 'ink on paper'),
]
