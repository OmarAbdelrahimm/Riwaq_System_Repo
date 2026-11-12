#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chapter 2 — «الغاز اللي برّد الكوكب» : 1:49.48 → 3:45.42 (SRT lines 22–48).

The chapter is built on the same engine, the same plate law and the same QA as Chapter 1.
What is different here is the subject: Tambora, the eruption, and the chemistry that turned
an explosion into a cold summer. Nothing in this chapter may use clips 04 or 05 — they are
spent in Chapter 1 — so the eruption is drawn: a geological section that collapses
4300 m → 2850 m, an archive-plate collage, and VEI / column-height infographics, until clip
06 lands at its literal cue 2:18.21.

Shot map, anchored to the SRT to the second (never an even split):

    L22 103.17  the strongest was not in Europe        S01 bridge      103.17 - 106.27
    L23 106.27  April 1815, Sumbawa, Indonesia         S02 map         106.27 - 112.45
    L24 112.45  Tambora wakes after years of quiet     S03 wake        112.45 - 117.24
    L25 117.24  10 April, the climax                   S04 climax      117.24 - 121.58
    L26 121.58  the largest recorded eruption          S05 vei7        121.58 - 125.80
    L27 125.80  rock, ash and gas thrown up            S06 column      125.80 - 131.15
    L28 131.15  ash buried the islands and the crops   S07 ashfall     131.15 - 138.21
    L29 138.21  near the volcano: houses, crops, people S08 clip06     138.21 - 144.79
    L30 144.79  tens of thousands                      S09 toll        144.79 - 149.62
    L31 149.62  it did not stop at the island          S10 map_out     149.62 - 153.31
    L32 153.31  fine ash rode the winds to the stratosphere S11 loft  153.31 - 158.86
    L33 158.86  something still working out of sight   S12 hidden      158.86 - 163.13
    L34 163.13  something that would change the summer S13 change     163.13 - 166.36
    L35 166.36  what exactly is it?                    S14 question    166.36 - 168.89
    L36 168.89  not fire, gas                          S15 gas         168.89 - 172.78
    L37 172.78  volcanoes mean heat — so how cold?     S16 paradox     172.78 - 179.52
    L38 179.52  it is not only ash blocking the sun    S17 notjust     179.52 - 182.84
    L39 182.84  the eruption released SO2               S18 so2         182.84 - 186.71
    L40 186.71  the gases reached the upper atmosphere  S19 rise        186.71 - 190.57
    L41 190.57  coarse ash falls fast, aerosol stays    S20 split       190.57 - 196.05
    L42 196.05  winds wrapped it around the planet     S21 planet      196.05 - 198.02
    L43 198.02  sulphate particles formed              S22 sulphate    198.02 - 203.30
    L44 203.30  they reflected sunlight into space      S23 reflect     203.30 - 206.46
    L45 206.46  less solar energy reached the ground    S24 energy      206.46 - 210.02
    L46 210.02  cooling that outlasted the eruption     S25 cooling     210.02 - 214.65
    L47 214.65  the same mechanism climate science uses S26 mechanism   214.65 - 217.87
    L48 217.87  but cooling is not the worst part       S27 turn        217.87 - 225.42
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from eng5 import core5 as C
from eng5 import tags5 as TG
from eng5 import world5 as W5

W, H = C.W, C.H

# ---------------------------------------------------------------- plates
# THIS CHAPTER IS ALLOWED CLIP 06 AND NOTHING ELSE. 01 02 03 04 05 are spent in Chapter 1
# and 07 08 belong to Chapter 3.
CH2_PLATES = ('06',)
PL = {k: C.Plate(k, src_fps=24.0) for k in CH2_PLATES}

# Chapter 1's flakes are 3-8 px discs, which in ash weather read as confetti. Chapter 2
# uses fine ash: many more, much smaller, lower alpha and colder, plus a few cinders.
ASH_HVY = C.Ash(n=1500, speed=(55, 140), size=(0.5, 1.5), wind=-72, seed=41,
                alpha=(24, 64), color=(172, 165, 152))
ASH_MID = C.Ash(n=800, speed=(35, 95), size=(0.45, 1.2), wind=-50, seed=17,
                alpha=(18, 48), color=(168, 161, 150))
CINDERS = C.Ash(n=34, speed=(70, 150), size=(1.6, 2.6), wind=-95, seed=63,
                alpha=(60, 110), color=(120, 104, 88))
MOTES = C.Ash(n=260, speed=(12, 34), size=(0.4, 1.0), wind=-8, seed=5,
              alpha=(16, 40), color=(176, 168, 154))

T0, T_END = 103.17, 225.42

SHOTS = [
    ('S01_bridge',   'map', T0,      106.27, 0.00, 1.0000),
    ('S02_map',      'map', 106.27,  112.45, 0.00, 1.0000),
    ('S03_wake',     'gfx', 112.45,  117.24, 0.00, 1.0000),
    ('S04_climax',   'gfx', 117.24,  121.58, 0.00, 1.0000),
    ('S05_vei',      'gfx', 121.58,  125.80, 0.00, 1.0000),
    ('S06_column',   'gfx', 125.80,  131.15, 0.00, 1.0000),
    ('S07_ashfall',  'gfx', 131.15,  138.21, 0.00, 1.0000),
    ('S08_village',  '06',  138.21,  144.79, 0.00, 1.0000),
    ('S09_toll',     'gfx', 144.79,  149.62, 0.00, 1.0000),
    ('S10_map_out',  'map', 149.62,  153.31, 0.00, 1.0000),
    ('S11_loft',     'gfx', 153.31,  158.86, 0.00, 1.0000),
    ('S12_hidden',   'map', 158.86,  163.13, 0.00, 1.0000),
    ('S13_change',   'map', 163.13,  166.36, 0.00, 1.0000),
    ('S14_question', 'map', 166.36,  168.89, 0.00, 1.0000),
    ('S15_gas',      'gfx', 168.89,  172.78, 0.00, 1.0000),
    ('S16_paradox',  'gfx', 172.78,  179.52, 0.00, 1.0000),
    ('S17_notjust',  'gfx', 179.52,  182.84, 0.00, 1.0000),
    ('S18_so2',      'gfx', 182.84,  186.71, 0.00, 1.0000),
    ('S19_rise',     'gfx', 186.71,  190.57, 0.00, 1.0000),
    ('S20_split',    'gfx', 190.57,  196.05, 0.00, 1.0000),
    ('S21_planet',   'map', 196.02,  198.02, 0.00, 1.0000),
    ('S22_sulphate', 'gfx', 198.02,  203.30, 0.00, 1.0000),
    ('S23_reflect',  'gfx', 203.30,  206.46, 0.00, 1.0000),
    ('S24_energy',   'gfx', 206.46,  210.02, 0.00, 1.0000),
    ('S25_cooling',  'gfx', 210.02,  214.65, 0.00, 1.0000),
    ('S26_mechanism', 'gfx', 214.65, 217.87, 0.00, 1.0000),
    ('S27_turn',     'map', 217.87,  225.42, 0.00, 1.0000),
]
BY_NAME = {s[0]: s for s in SHOTS}
MAP_SHOTS = {s[0] for s in SHOTS if s[1] == 'map'}
FORCE_HARD_BEFORE = {'S04_climax', 'S08_village', 'S15_gas', 'S27_turn'}

DUST = {}


def ramp(t, a, b):
    return max(0.0, min(1.0, (t - a) / max(1e-6, b - a)))


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def grader(base):
    return C.grade5(base.convert('RGB'), warmth=0.88, sat=0.86).convert('RGBA')


# ---------------------------------------------------------------- the map
MAP_W, MAP_H = 4315, 2193   # 1.5x, and east to 180E so the island can be centred
C_CW, C_CH = 1280, 720      # clip 06's real pixel size, measured
_MAPBASE = {}


def map_obj():
    if 'm' not in _MAPBASE:
        _MAPBASE['m'] = W5.Map(lon_a=-132, lon_b=180, lat_a=-30, lat_b=80,
                               x0=0, y0=0, w=MAP_W, h=MAP_H, ss=2)
    return _MAPBASE['m']


def map_base():
    """the plate, built once.

    `world5.compose_map` fills land with one flat colour and adds an inner glow that
    speckles at this resolution, which at 1.5x zoom reads as white confetti on the
    continents. Here the land gets its own low-frequency relief and the glow is derived
    from a blurred copy of the coast, so nothing can alias into dots.
    """
    if 'b' not in _MAPBASE:
        m = map_obj()
        mask = np.asarray(m.mask, np.float32) / 255.0
        yy, xx = np.mgrid[0:MAP_H, 0:MAP_W].astype(np.float32)
        a = np.zeros((MAP_H, MAP_W, 3), np.float32)
        # sea: a shallow gradient, colder toward the poles
        a += np.array([9, 12, 16], np.float32)
        a += ((np.clip(1.0 - yy / MAP_H, 0, 1) ** 2) * np.float32(10))[..., None] * \
            np.array([0.5, 0.75, 1.0], np.float32)[None, None, :]
        sea_n = _noise(MAP_W // 2, MAP_H // 2, 3, 3)
        a += np.asarray(Image.fromarray(((sea_n * 40) + 128).clip(0, 255)
                                        .astype(np.uint8)).resize((MAP_W, MAP_H),
                                                                  Image.BILINEAR),
                        np.float32)[..., None] * 0.06 - 3
        # land: charcoal with relief, brighter on the shoulders
        relief = _noise(MAP_W // 2, MAP_H // 2, 4, 12)
        relief = np.asarray(Image.fromarray(((relief * 40) + 128).clip(0, 255)
                                            .astype(np.uint8)).resize((MAP_W, MAP_H),
                                                                      Image.BILINEAR),
                             np.float32) / 40.0
        land = np.array([22, 26, 31], np.float32)
        lc = land[None, None, :] + (relief * 9)[..., None] + \
            (np.float32(6) * np.array([0.35, 0.32, 0.28], np.float32))[None, None, :]
        a = a * (1 - mask[..., None]) + lc * mask[..., None]
        # coast: a hairline just inside the boundary, plus a soft inner glow
        edge = mask - np.asarray(Image.fromarray((mask * 255).astype(np.uint8))
                                 .filter(ImageFilter.GaussianBlur(2.0)), np.float32) / 255.0
        edge = np.clip(edge * 3.4, 0, 1)
        a += (edge * 40)[..., None] * np.array([0.62, 0.72, 0.80], np.float32)
        # inner glow only: eroding the mask keeps every drop of light on the land. The
        # outer halo this used to add lit the whole ocean, so the sea read as mid grey.
        erode = np.asarray(Image.fromarray((mask * 255).astype(np.uint8))
                           .filter(ImageFilter.GaussianBlur(6.0)), np.float32) / 255.0
        inner = np.clip(mask - erode, 0, 1)
        a += (inner * 16)[..., None] * np.array([0.55, 0.68, 0.80], np.float32)
        # graticule at 30 degrees, faint
        g = Image.new('RGBA', (MAP_W, MAP_H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        for lon in range(-120, 151, 30):
            x, _ = m.px(lon, 0)
            gd.line([(x, 0), (x, MAP_H)], fill=(24, 29, 35, 70), width=1)
        for lat in range(-20, 81, 20):
            _, y = m.px(0, lat)
            gd.line([(0, y), (MAP_W, y)], fill=(24, 29, 35, 70), width=1)
        out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
        _MAPBASE['b'] = Image.alpha_composite(out, g).convert('RGB')
    return _MAPBASE['b']


SU_LL = (117.5, -8.4)
ICE_LL = (-16.0, 64.7)
EU_LL = (7.0, 47.0)
NE_LL = (-71.0, 42.3)


def focus(base, cx, cy, r=260, colour=(255, 196, 128), amount=0.30):
    if amount <= 0.004:
        return base
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.25) ** 2)
    g = np.clip(1.0 - d / max(r, 1e-3), 0, 1) ** 2 * amount
    a = np.asarray(base.convert('RGB'), np.float32)
    a += (g[..., None] * np.array(colour, np.float32) * 0.55)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')


# ---------------------------------------------------------------- type
HAND = 'Amiri-Regular.ttf'
HAND_BOLD = 'Amiri-Bold.ttf'
AR = 'IBMPlexSansArabic-Bold.ttf'
AR_R = 'IBMPlexSansArabic-Regular.ttf'
TEXT_LOG = {}
text_off = {'on': False}


def hand_text(im, x, y, text, size=34, fill=(43, 31, 20), font_name=None):
    """type on paper, shaped once. Never one character at a time: that breaks Arabic."""
    name = font_name or HAND
    if text_off['on']:
        return im
    sp = C.text_sprite(text, size=size, fill=fill, fname=name)
    im.alpha_composite(sp, (int(x), int(y)))
    TEXT_LOG[name] = TEXT_LOG.get(name, 0) + len(text)
    TEXT_LOG.setdefault(('path', name), C.font(name, size).path)
    return im


def label(base, text, x, y, t, t_in, t_out, size=48, fill=(226, 218, 200), shadow=True,
          scrim=True):
    """a line of type in the map plates, with its own contrast under it.

    A shadow is not enough over a map: measured against the plate behind the ink, the
    lower thirds came out at 2.4-4.1:1, under the 4.5 floor. The type therefore gets a
    scrim -- a soft, low-alpha ivory-warm panel just under the ink -- which is what raises
    the ratio without putting a card on the map.
    """
    if not (t_in <= t < t_out) or not C.T() or text_off['on']:
        return base
    a = min(ramp(t, t_in, t_in + 0.5), 1.0 - ramp(t, t_out - 0.4, t_out))
    if a <= 0:
        return base
    sp = C.text_sprite(text, size=size, fill=fill)
    if scrim:
        # a tight, heavily blurred shadow layer UNDER the letters only: it darkens the
        # plate where the ink sits, and leaves the rest of the map untouched. (A panel
        # here put a beige-grey box on the map, which the brief rules out.)
        pad = 22
        sc = Image.new('RGBA', (sp.width + pad * 2, sp.height + pad * 2), (0, 0, 0, 0))
        sc.alpha_composite(sp, (pad, pad))
        al = sc.split()[3].filter(ImageFilter.GaussianBlur(11)).point(
            lambda v: int(min(255, v * 3.4) * 0.95))
        dark = Image.new('RGBA', sc.size, (6, 8, 11, 0))
        dark.putalpha(al)
        if a < 1:
            dark.putalpha(al.point(lambda v: int(v * a)))
        base.alpha_composite(dark, (int(x) - pad, int(y) - pad))
    if shadow:
        sh = Image.new('RGBA', (sp.width + 12, sp.height + 12), (0, 0, 0, 0))
        for blur, op in ((7, 0.95), (16, 0.7)):
            a2 = Image.new('L', sh.size, 0)
            a2.paste(sp.split()[3], (6, 8))
            a2 = a2.filter(ImageFilter.GaussianBlur(blur))
            sh2 = Image.new('RGBA', sh.size, (0, 0, 0, 0))
            sh2.putalpha(a2.point(lambda v: int(v * op)))
            sh.alpha_composite(sh2)
        sh.alpha_composite(sp, (6, 6))
        sp = sh
        x, y = x - 6, y - 6
    if a < 1:
        sp = sp.copy()
        sp.putalpha(sp.split()[3].point(lambda v: int(v * a)))
    base.alpha_composite(sp, (int(x), int(y)))
    return base


# ---------------------------------------------------------------- plates for the eruption
# No clip 04 or 05 here: the volcano is drawn. These are the chapter's own graphics.
_BLANK = {}


def _card(w, h, fill, seed=3, edge=1.0):
    """a sheet of stock for a printed plate: warm off-white, with a little tooth.

    The paper is deterministic per (w, h, seed) and cached, because it is the plate's
    substrate: the lettering-off pass in the text test rebuilds the sheet every time, and
    a fresh noise draw would put a pixel of grain under every pad the ink once covered.
    """
    key = (w, h, seed, tuple(fill), edge)
    if key in _BLANK:
        return _BLANK[key].copy()
    rng = np.random.default_rng(seed)
    a = np.zeros((h, w, 3), np.float32)
    a[...] = fill
    # tooth: deterministic per seed, and LOW frequency once resized (bilinear on a
    # smooth field), so it never aliases into speckle
    n = _noise(w, h, 3, seed + 11)
    a += (n * 7.0)[..., None]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    l = 1.02 - 0.30 * np.clip(np.sqrt(((xx - w * 0.30) / w) ** 2 +
                                      ((yy - h * 0.18) / h) ** 2) / 1.05, 0, 1)
    a *= l[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle([0, 0, w - 1, h - 1], outline=(118, 102, 86, int(150 * edge)), width=2)
    _BLANK[key] = im
    return im.copy()


def panel(base, im, cx, cy, tilt=0.0, alpha=1.0, shadow=True):
    """place a printed plate on the frame with a soft shadow"""
    if alpha <= 0.004:
        return base
    sp = im
    if tilt:
        sp = sp.rotate(tilt, expand=True, resample=Image.BICUBIC)
    if alpha < 1.0:
        sp = sp.copy()
        sp.putalpha(sp.split()[3].point(lambda v: int(v * alpha)))
    x, y = int(cx - sp.width / 2), int(cy - sp.height / 2)
    if shadow:
        sh = Image.new('RGBA', (sp.width + 60, sp.height + 60), (0, 0, 0, 0))
        sh.alpha_composite(sp, (30, 30))
        a = sh.split()[3].filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * 0.70))
        sh.putalpha(a)
        base.alpha_composite(sh, (x - 30 + 6, y - 30 + 12))
    base.alpha_composite(sp, (x, y))
    return base


# ---- the geological section: Tambora 4300 m before, 2850 m after
def _section_sheet(w=1180, h=760, collapse=0.0):
    """a cross-section of the mountain, drawn to scale, that loses its summit.

    `collapse` runs 0 -> 1: the summit is cut down from 4300 m to 2850 m and the caldera
    opens. The sea line and the scale bar stay put so the height loss is legible.
    """
    im = _card(w, h, (236, 228, 212), seed=71)
    d = ImageDraw.Draw(im, 'RGBA')
    base_y = int(h * 0.80)
    m_per_px = 4300.0 / (base_y - int(h * 0.14))          # true scale
    d.line([(30, base_y), (w - 30, base_y)], fill=(70, 58, 46, 200), width=3)
    peak_x, peak_top = w * 0.46, base_y - 4300 / m_per_px
    cut_top = base_y - (4300 - 1450 * collapse) / m_per_px
    # the mountain, as a polygon with a summit that steps down
    left, right = w * 0.10, w * 0.86
    pts = [(left, base_y), (peak_x - 250, base_y - 1500 / m_per_px),
           (peak_x - 96, cut_top + 40), (peak_x + 96, cut_top + 40),
           (peak_x + 260, base_y - 1400 / m_per_px), (right, base_y)]
    d.polygon(pts, fill=(70, 62, 54, 255))
    # strata: a few lines that follow the mountain's shoulders
    for k in range(7):
        y = base_y - (400 + k * 420) / m_per_px
        d.line([(left + 40, y + 26), (peak_x, y - 10), (right - 40, y + 22)],
               fill=(96, 86, 74, 90), width=2)
    # the missing summit, ghosted, so the loss has a shape
    if collapse > 0.02:
        ghost = [(peak_x - 96, cut_top + 40), (peak_x, peak_top), (peak_x + 96, cut_top + 40)]
        ov = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(ov).polygon(ghost, fill=(150, 120, 92, int(70 * collapse)))
        im.alpha_composite(ov)
        d = ImageDraw.Draw(im, 'RGBA')
    # the caldera floor once it has opened
    if collapse > 0.35:
        u = ramp(collapse, 0.35, 1.0)
        d.arc([peak_x - 130, cut_top + 10, peak_x + 130, cut_top + 150],
              start=200, end=340, fill=(120, 70, 52, int(200 * u)), width=5)
    # the sea, in front
    d.rectangle([30, base_y + 3, w - 30, base_y + 74], fill=(58, 88, 104, 110))
    # scale bar: 1000 m
    sb_x, sb_y = 60, base_y - 1000 / m_per_px - 10
    d.line([(sb_x, sb_y), (sb_x, base_y - 8)], fill=(60, 48, 38, 220), width=3)
    d.line([(sb_x - 10, sb_y), (sb_x + 10, sb_y)], fill=(60, 48, 38, 220), width=3)
    d.line([(sb_x - 10, base_y - 8), (sb_x + 10, base_y - 8)], fill=(60, 48, 38, 220), width=3)
    hand_text(im, sb_x + 22, int((sb_y + base_y) / 2) - 20, '1000 m', size=26,
              fill=(58, 44, 34))
    # the two heights, lettered on the drawing: the summit's own number, right-aligned
    # above the summit. (A second Arabic numeral used to be stamped here as well and
    # collided with it -- one label per height.)
    hand_text(im, 60, 44, 'Tambora — cross-section', size=38, fill=(52, 38, 26))
    h_now = 4300 - 1450 * collapse
    hs = '%d m' % int(round(h_now / 10.0) * 10)
    sp = C.text_sprite(hs, 44, fill=(120, 60, 40))
    im.alpha_composite(sp, (int(peak_x + 150 - sp.width / 2), int(cut_top) - 74))
    return im


_SECT = {}


def section_sheet(collapse):
    key = round(collapse, 2)
    if key not in _SECT:
        _SECT[key] = _section_sheet(collapse=collapse)
    return _SECT[key]


# ---------------------------------------------------------------- camera safety net
def cam_to(ll, zoom, target=(W * 0.5, H * 0.5), plate=(MAP_W, MAP_H)):
    """a camera framed on a place, not on a guessed zoom.

    `Camera(zoom=)` is relative to the plate, so on a 2600x1462 map a "1.2" shows four
    fifths of the planet: every map shot read as the same wide world, and the pans were
    clamped away, which is why the frames were byte-identical for seconds. Here the zoom
    is derived from the plate and the pan is solved so the subject lands where the
    composition wants it. `zoom >= 1.0` only when the crop really is smaller than the
    frame, so nothing is ever upscaled.
    """
    m = map_obj()
    bx, by = m.px(*ll)
    zmin_frame = (H * (plate[0] / plate[1])) / plate[0]
    z = max(zoom, zmin_frame + 0.004)
    cw, ch = plate[0] / z, plate[1] / z
    x0 = min(max(0.0, bx - target[0] * cw / W), plate[0] - cw)
    y0 = min(max(0.0, by - target[1] * ch / H), plate[1] - ch)
    pan = (x0 + cw / 2 - plate[0] / 2, y0 + ch / 2 - plate[1] / 2)
    return C.Camera(zoom=z, pan=pan)


def safe_cam(zoom, pan=(0.0, 0.0), aspect=MAP_W / MAP_H):
    """kept for the desk shots: a zoom that can never leave a gap."""
    zmin = (H * aspect) / MAP_W
    return C.Camera(zoom=max(zoom, zmin + 0.004), pan=pan)


# ---------------------------------------------------------------- shots
def base_s01(t):
    """«والأقوى ما كانش في أوروبا خالص» (L22): the bridge, Europe falls away east"""
    lt = t - T0
    dur = 106.27 - T0
    u = ease(lt / dur)
    m = map_obj()
    cam = cam_to((62 + 46 * u, 22 - 21 * u), 1.10 - 0.06 * u,
                 target=(W * 0.50, H * 0.48))
    base = cam.apply(map_base()).convert('RGBA')
    d = ImageDraw.Draw(base)
    S = lambda ll: cam.to_screen(*m.px(*ll))
    p = S(EU_LL)
    ps = S(SU_LL)
    base = focus(base, p[0], p[1], r=330, amount=0.26 * (1.0 - ramp(lt, 0.8, 2.4)))
    base = focus(base, ps[0], ps[1], r=300, amount=0.20 * ramp(lt, 0.9, 2.4))
    d = ImageDraw.Draw(base)          # focus() rebinds base: the pen has to follow it
    C.pin(base, p[0], p[1], t, T0, r=11)
    if lt > 0.4:
        W5.dashed_line(d, [S(ll) for ll in (EU_LL, (60, 30), (95, 5), SU_LL)],
                       C.GOLD + (245,), width=5, dash=22, gap=13,
                       upto=ramp(lt, 0.4, 2.6))
    base = label(base, 'الأقوى مكانش في أوروبا', 96, H - 150, t, T0 + 0.30, 106.20,
                 size=50)
    return grader(base)


def base_s02(t):
    """«إبريل 1815 — جزيرة سومباوا» (L23): land on Sumbawa and hold"""
    lt = t - 106.27
    dur = 112.45 - 106.27
    u = ease(lt / dur)
    m = map_obj()
    cam = cam_to(SU_LL, 1.95 - 0.28 * u, target=(W * 0.44, H * 0.46))
    base = cam.apply(map_base()).convert('RGBA')
    p = cam.to_screen(*m.px(*SU_LL))
    base = focus(base, p[0], p[1], r=280, amount=0.26 * ramp(lt, 0.3, 1.4))
    d = ImageDraw.Draw(base)
    if lt > 0.25:
        for k, (r0, ph) in enumerate(((70, 0.0), (110, 0.55), (150, 1.1))):
            q = ((lt / 2.4) + ph) % 1.0
            rr = r0 * (0.70 + 0.50 * q)
            a = int(190 * (1 - q) * ramp(lt, 0.25 + k * 0.2, 0.8 + k * 0.2))
            if a > 4:
                d.ellipse([p[0] - rr, p[1] - rr * 0.62, p[0] + rr, p[1] + rr * 0.62],
                          outline=(224, 186, 120, a), width=3)
    C.pin(base, p[0], p[1], t, 106.60, r=10)
    # the island named, right of the mark
    sp = C.text_sprite('سومباوا', 36, fill=(232, 220, 198))
    a = ramp(lt, 0.55, 1.25)
    sp.putalpha(sp.split()[3].point(lambda v: int(v * a)))
    base.alpha_composite(sp, (int(p[0] - sp.width / 2), int(p[1] - 78)))
    base = label(base, 'إبريل ١٨١٥ — جزيرة سومباوا', 96, H - 150, t, 106.50, 112.40,
                 size=48)
    return grader(base)


def base_s03(t):
    """«تونجّار إندونيسيا، وقت الانفجار» (L24): the sea, going out under the ash"""
    lt = t - 112.45
    dur = 117.24 - 112.45
    base = _beach_backdrop(lt, dur)
    base = ASH_HVY.draw(base, t, density=0.30 + 0.10 * ramp(lt, 0.5, 3.0))
    # the day failing: the frame dims as the column rises out of shot
    a = np.asarray(base.convert('RGB'), np.float32) * (1.0 - 0.16 * ease(lt / dur))
    base = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    base = label(base, 'تونجّار، إندونيسيا', 96, H - 150, t, 112.70, 117.20, size=46)
    return grader(base)


def base_s04(t):
    """«يوم 10 إبريل وصل لذروة الانفجار» (L25): the summit comes down"""
    lt = t - 117.24
    dur = 121.58 - 117.24
    base = _desk_backdrop(lt, dur, seed=81)
    col = ease(ramp(lt, 0.55, 2.85))
    sheet = section_sheet(round(col, 2))
    panel(base, _scaled(sheet, 1.02), W / 2, H / 2 - 30, tilt=-0.6)
    # a dust wave off the collapsing flank
    if 0.6 < lt < 3.2:
        u = ramp(lt, 0.6, 3.2)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W * 0.46) / 520) ** 2 + ((yy - H * 0.62) / 190) ** 2)
        g = np.clip(1 - r, 0, 1) ** 2 * 0.32 * (1 - u)
        a = np.asarray(base.convert('RGB'), np.float32)
        a += g[..., None] * np.array([120, 100, 82], np.float32)
        base = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    return grader(base)


def base_s05(t):
    """«أكبر ثوران مسجّل في التاريخ البشري» (L26): the VEI 7 infographic"""
    lt = t - 121.58
    dur = 125.80 - 121.58
    base = _desk_backdrop(lt, dur, seed=93)
    sheet = _vei_sheet(min(1.0, ramp(lt, 0.35, 2.30)))
    panel(base, sheet, W / 2 - 40, H / 2 - 20, tilt=0.4, alpha=ramp(lt, 0.0, 0.40))
    return grader(base)


def base_s06(t):
    """«صخور ورماد وغازات اندفعت لفوق» (L27): the column"""
    lt = t - 125.80
    dur = 131.15 - 125.80
    base = _desk_backdrop(lt, dur, seed=105)
    sheet = _column_sheet(min(1.0, ramp(lt, 0.30, 3.20)))
    panel(base, sheet, W / 2, H / 2 - 10, tilt=-0.3, alpha=ramp(lt, 0.0, 0.40))
    base = ASH_HVY.draw(base, t, density=0.22 * ramp(lt, 1.2, 3.2))
    return grader(base)


def base_s07(t):
    """«الرماد غطّى الجزر القريبة» (L28): the ash footprint, over Sumbawa"""
    lt = t - 131.15
    dur = 138.21 - 131.15
    u = ease(lt / dur)
    m = map_obj()
    cam = cam_to(SU_LL, 1.68 + 0.18 * u, target=(W * 0.46, H * 0.50))
    base = cam.apply(map_base()).convert('RGBA')
    base = ASH_MID.draw(base, t, density=0.50)
    d = ImageDraw.Draw(base)
    p = cam.to_screen(*m.px(*SU_LL))
    for k in range(4):
        q = ramp(lt, 0.45 + k * 0.62, 2.60 + k * 0.62)
        if q <= 0:
            continue
        rr = min(34 + 120 * ease(q), 84 + 52 * k)
        d.ellipse([p[0] - rr, p[1] - rr * 0.66, p[0] + rr, p[1] + rr * 0.66],
                  outline=(196, 178, 150, int(160 * (1 - 0.55 * q))), width=4)
    C.pin(base, p[0], p[1], t, 131.15, r=10)
    base = label(base, 'الرماد غطّى الجزر', 96, H - 150, t, 131.40, 138.15, size=48)
    return grader(base)


def base_s08(t):
    """«وقرب البركان، الكارثة كانت مباشرة» (L29): clip 06, the buried village.

    `Plate.frame` is driven by the time INSIDE the shot, not the chapter clock: Chapter 1's
    shots handed it a local `lt` and this one was handed `lt` too, but the plate was asked
    for `t`. At 0.8 files per output frame the source index has to move every frame or the
    clip freezes. (The QA run flagged 197 frames on index 0, but that was `plate_src`
    reporting a placeholder index, not the picture; the picture is checked below.)

    No real faces: the frame is cropped to the left 800x450, where the plate shows huts,
    ashfall and figures at distance, and the right third -- where the plate's woman and
    child are -- is thrown away instead of being graded and shown.
    """
    lt = t - 138.21
    dur = 144.79 - 138.21
    plate = PL['06']
    src = plate.frame(lt, None)          # lt: seconds from the cut, and it advances
    # keep only the left 800x450 of the 1280x720 plate: huts, ashfall, figures at a
    # distance. The right third of the plate carries close faces and is discarded
    # outright, so no real-looking face is ever graded up and shown.
    rect = (0, 0, 800, 450)
    base = _plate_crop(src, rect, z=1.06 - 0.05 * ease(lt / dur),
                       pan=(22 * (lt / dur) - 11, -22)).convert('RGBA')
    base = plate_grade(base, warmth=0.78)
    base = ASH_HVY.draw(base, t, density=0.34)
    base = C.grade5(base.convert('RGB'), warmth=0.82, sat=0.78).convert('RGBA')
    return base


def base_s09(t):
    """«عشرات الآلاف» (L30): the toll, as a counted figure on stock"""
    lt = t - 144.79
    dur = 149.62 - 144.79
    base = _desk_backdrop(lt, dur, seed=117)
    sheet = _toll_sheet(min(1.0, ramp(lt, 0.25, 1.85)))
    panel(base, sheet, W / 2, H / 2 - 10, tilt=0.3, alpha=ramp(lt, 0.0, 0.40))
    return grader(base)


def base_s10(t):
    """«لكن الانفجار ما وقفش عند حدود الجزيرة» (L31): pull out along the arc"""
    lt = t - 149.62
    dur = 153.31 - 149.62
    u = ease(lt / dur)
    m = map_obj()
    cam = cam_to((SU_LL[0] - 6 * u, SU_LL[1] + 2 * u), 1.62 - 0.30 * u,
                 target=(W * 0.52, H * 0.50))
    base = cam.apply(map_base()).convert('RGBA')
    base = ASH_MID.draw(base, t, density=0.45)
    d = ImageDraw.Draw(base)
    p = cam.to_screen(*m.px(*SU_LL))
    C.pin(base, p[0], p[1], t, 149.62, r=10)
    for k in range(3):
        q = ramp(lt, 0.35 + k * 0.7, 2.4 + k * 0.7)
        if q <= 0:
            continue
        rr = min(60 + 240 * ease(q), 150 + 110 * k)
        d.ellipse([p[0] - rr, p[1] - rr * 0.70, p[0] + rr, p[1] + rr * 0.70],
                  outline=(190, 172, 148, int(130 * (1 - 0.5 * q))), width=3)
    base = label(base, 'الانفجار ما وقفش عند الجزيرة', 96, H - 150, t, 149.90, 153.25,
                 size=46)
    return grader(base)


def base_s11(t):
    """«الرماد الخفيف اتحمل مع الرياح» (L32): ash into the stratosphere"""
    lt = t - 153.31
    dur = 158.86 - 153.31
    base = _desk_backdrop(lt, dur, seed=129)
    sheet = _loft_sheet(min(1.0, ramp(lt, 0.30, 3.20)))
    panel(base, sheet, W / 2, H / 2 - 10, tilt=0.5, alpha=ramp(lt, 0.0, 0.40))
    return grader(base)


# ---------------------------------------------------------------- the rest of the shots
def base_s12(t):
    """«وكان لسه فيه حاجة شغّالة بعيد عن العيون» (L33): dust on an empty hemisphere"""
    lt = t - 158.86
    dur = 163.13 - 158.86
    m = map_obj()
    cam = cam_to((-70 + 40 * (lt / dur), 52), 1.38 - 0.05 * ease(lt / dur),
                 target=(W * 0.50, H * 0.44))
    base = cam.apply(map_base()).convert('RGBA')
    base = ASH_MID.draw(base, t, density=0.30)
    # a slow band of haze crossing the frame, no label: this is the "out of sight" beat
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    band = np.exp(-((yy - (H * 0.42 + 40 * math.sin(lt * 0.5))) / 190.0) ** 2)
    a = np.asarray(base.convert('RGB'), np.float32)
    a *= (1.0 - 0.10 * band[..., None] * ramp(lt, 0.5, 2.4))
    base = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    base = label(base, 'حاجة شغّالة بعيد عن العيون', 96, H - 150, t, 159.10, 163.05,
                 size=46)
    return grader(base)


def base_s13(t):
    """«حاجة هتغيّر صيف السنة اللي بعدها» (L34): the hemisphere cools by degrees"""
    lt = t - 163.13
    dur = 166.36 - 163.13
    m = map_obj()
    cam = cam_to((-46, 44), 1.26, target=(W * 0.50, H * 0.46))
    base = cam.apply(map_base()).convert('RGBA')
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u = ease(ramp(lt, 0.3, 2.6))
    cool = np.clip(1.0 - np.sqrt(((xx - W * 0.5) / (W * 0.62)) ** 2 +
                                 ((yy - H * 0.45) / (H * 0.62)) ** 2), 0, 1) ** 1.4
    a = np.asarray(base.convert('RGB'), np.float32)
    a += (cool * 46 * u)[..., None] * np.array([-0.55, -0.10, 0.62], np.float32)
    base = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    base = label(base, 'صيف السنة اللي بعدها', 96, H - 150, t, 163.35, 166.30, size=48)
    return grader(base)


def base_s14(t):
    """«إيه هي بالظبط؟» (L35): hold on the question"""
    lt = t - 166.36
    dur = 168.89 - 166.36
    m = map_obj()
    cam = cam_to((-48 - 6 * (lt / dur), 46), 1.20 - 0.03 * (lt / dur),
                 target=(W * 0.50, H * 0.46))
    base = cam.apply(map_base()).convert('RGBA')
    base = focus(base, W / 2, H / 2, r=520, amount=0.14 * ramp(lt, 0.2, 1.4))
    base = label(base, 'إيه هي بالظبط؟', 96, H - 150, t, 166.50, 168.85, size=56)
    return grader(base)


def base_s15(t):
    """«الإجابة مش نار. الإجابة غاز» (L36): the two words, on stock"""
    lt = t - 168.89
    dur = 172.78 - 168.89
    base = _desk_backdrop(lt, dur, seed=141)
    sheet = _fire_gas_sheet(lt)
    panel(base, sheet, W / 2, H / 2 - 10, tilt=-0.4, alpha=ramp(lt, 0.0, 0.40))
    return grader(base)


def base_s16(t):
    """«بركان يعني حرارة... فإزاي يخلّي الأرض تبرد؟» (L37): the paradox"""
    lt = t - 172.78
    dur = 179.52 - 172.78
    base = _desk_backdrop(lt, dur, seed=153)
    sheet = _paradox_sheet(min(1.0, ramp(lt, 0.3, 2.6)))
    panel(base, sheet, W / 2, H / 2 - 10, tilt=0.3, alpha=ramp(lt, 0.0, 0.40))
    return grader(base)


def base_s17(t):
    """«الموضوع مش إن الرماد حجب الشمس وبس» (L38)"""
    lt = t - 179.52
    dur = 182.84 - 179.52
    base = _desk_backdrop(lt, dur, seed=165)
    sheet = _notjust_sheet(min(1.0, ramp(lt, 0.25, 2.2)))
    panel(base, sheet, W / 2, H / 2 - 10, tilt=-0.3, alpha=ramp(lt, 0.0, 0.40))
    return grader(base)


def base_s18(t):
    """«الثوران أطلق غازات، منها ثاني أكسيد الكبريت» (L39): SO2"""
    lt = t - 182.84
    dur = 186.71 - 182.84
    base = _desk_backdrop(lt, dur, seed=177)
    sheet = _so2_sheet(min(1.0, ramp(lt, 0.25, 2.4)))
    panel(base, sheet, W / 2, H / 2 - 10, tilt=0.4, alpha=ramp(lt, 0.0, 0.40))
    return grader(base)


def base_s19(t):
    """«الغازات دي وصلت لطبقات عالية» (L40): the climb"""
    lt = t - 186.71
    dur = 190.57 - 186.71
    base = _desk_backdrop(lt, dur, seed=189)
    sheet = _rise_sheet(min(1.0, ramp(lt, 0.25, 2.6)))
    panel(base, sheet, W / 2, H / 2 - 10, tilt=-0.4, alpha=ramp(lt, 0.0, 0.40))
    return grader(base)


def base_s20(t):
    """«الرماد الخشن بينزل... والهباء بيفضل» (L41): the two speeds, side by side"""
    lt = t - 190.57
    dur = 196.05 - 190.57
    base = _desk_backdrop(lt, dur, seed=201)
    sheet = _split_sheet(lt)
    panel(base, sheet, W / 2, H / 2 - 10, tilt=0.3, alpha=ramp(lt, 0.0, 0.40))
    return grader(base)


def base_s21(t):
    """«الرياح لفته حوالي الكوكب» (L41): the planet, and the veil going round it"""
    lt = t - 196.02
    dur = 198.02 - 196.02
    base = _planet_backdrop()
    d = ImageDraw.Draw(base, 'RGBA')
    cx, cy = W * 0.50, H * 0.52
    rr = 330
    u = ramp(lt, 0.05, 1.85)
    # the veil, a band that starts over the volcano and wraps east with the wind
    for k in range(150):
        f = k / 149.0
        if f > u + 0.02:
            continue
        ang = math.radians(200 + f * 330 * ease(min(1.0, u * 1.15)))
        ax = cx + rr * 1.10 * math.cos(ang)
        ay = cy + rr * 0.44 * math.sin(ang)
        wob = 0.5 + 0.5 * math.cos(ang * 1.4)
        a = int(190 * ramp(f, 0.0, 0.08) * (1 - 0.25 * f))
        d.ellipse([ax - 13, ay - 6 - 5 * wob, ax + 13, ay + 6 + 5 * wob],
                  fill=(232, 214, 182, a))
    # the volcano, a point on the limb, and the wind direction
    vx, vy = cx - rr * 0.55, cy - rr * 0.20
    d.ellipse([vx - 7, vy - 7, vx + 7, vy + 7], fill=(150, 62, 44, 245))
    base = focus(base, cx, cy, r=520, colour=(255, 214, 150), amount=0.10)
    base = label(base, 'الرياح لفته حوالي الكوكب', 96, H - 150, t, 196.20, 197.98,
                 size=46)
    return grader(base)


def base_s22(t):
    """«هناك اتكوّنت جسيمات دقيقة جدًا — هباء الكبريتات» (L43)"""
    lt = t - 198.02
    dur = 203.30 - 198.02
    base = _desk_backdrop(lt, dur, seed=213)
    sheet = _sulphate_sheet(min(1.0, ramp(lt, 0.25, 3.0)))
    panel(base, sheet, W / 2, H / 2 - 10, tilt=-0.3, alpha=ramp(lt, 0.0, 0.40))
    return grader(base)


def base_s23(t):
    """«عكست جزء من ضوء الشمس للفضاء» (L44): the reflection"""
    lt = t - 203.30
    dur = 206.46 - 203.30
    base = _desk_backdrop(lt, dur, seed=225)
    sheet = _reflect_sheet(lt)
    panel(base, sheet, W / 2, H / 2 - 10, tilt=0.3, alpha=ramp(lt, 0.0, 0.40))
    return grader(base)


def base_s24(t):
    """«طاقة شمسية أقل وصلت لسطح الأرض» (L45): the energy budget"""
    lt = t - 206.46
    dur = 210.02 - 206.46
    base = _desk_backdrop(lt, dur, seed=237)
    sheet = _energy_sheet(min(1.0, ramp(lt, 0.25, 2.4)))
    panel(base, sheet, W / 2, H / 2 - 10, tilt=-0.3, alpha=ramp(lt, 0.0, 0.40))
    return grader(base)


def base_s25(t):
    """«تبريد امتد لفترة بعد الانفجار» (L46): the temperature trace"""
    lt = t - 210.02
    dur = 214.65 - 210.02
    base = _desk_backdrop(lt, dur, seed=249)
    sheet = _cooling_sheet(min(1.0, ramp(lt, 0.25, 3.0)))
    panel(base, sheet, W / 2, H / 2 - 10, tilt=0.3, alpha=ramp(lt, 0.0, 0.40))
    return grader(base)


def base_s26(t):
    """«نفس الآلية اللي بتدرسها علوم المناخ» (L47): the mechanism, as a loop"""
    lt = t - 214.65
    dur = 217.87 - 214.65
    base = _desk_backdrop(lt, dur, seed=261)
    sheet = _mechanism_sheet(min(1.0, ramp(lt, 0.25, 2.4)))
    panel(base, sheet, W / 2, H / 2 - 10, tilt=-0.3, alpha=ramp(lt, 0.0, 0.40))
    return grader(base)


def base_s27(t):
    """«بس التبريد لوحده مش أخطر جزء» (L48): the turn into Chapter 3"""
    lt = t - 217.87
    dur = 225.42 - 217.87
    m = map_obj()
    cam = cam_to((-34 + 54 * ease(lt / dur), 40 - 8 * ease(lt / dur)),
                 1.30 - 0.15 * ease(lt / dur), target=(W * 0.50, H * 0.46))
    base = cam.apply(map_base()).convert('RGBA')
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u = ramp(lt, 0.4, 4.2)
    cool = np.clip(1.0 - np.sqrt(((xx - W * 0.5) / (W * 0.60)) ** 2 +
                                 ((yy - H * 0.48) / (H * 0.60)) ** 2), 0, 1) ** 1.6
    # land only: a disc over the whole frame reads as a blue spotlight, not as cold
    m = map_obj()
    land = np.asarray(m.crop_mask(cam), np.float32) / 255.0 if hasattr(m, 'crop_mask') \
        else np.ones((H, W), np.float32)
    a = np.asarray(base.convert('RGB'), np.float32)
    a += (cool * land * 40 * u)[..., None] * np.array([-0.34, 0.02, 0.46], np.float32)
    base = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    base = label(base, 'بس التبريد لوحده مش أخطر حاجة', 96, H - 150, t, 218.30, 225.30,
                 size=46)
    return grader(base)


# ---------------------------------------------------------------- overlays per shot
# Each map/photo shot carries one lower-third line. The graphics shots carry their own
# printed lettering, so they are left alone -- those are checked by the text-presence test
# against the paper rectangle, not against a lower third.
LINES = [
    ('S01_bridge',   103.40, 106.20, 50, 'الأقوى مكانش في أوروبا'),
    ('S02_map',      106.60, 112.40, 48, 'إبريل ١٨١٥ — جزيرة سومباوا'),
    ('S03_wake',     112.70, 117.20, 46, 'تونجّار، إندونيسيا'),
    ('S07_ashfall',  131.40, 138.15, 48, 'الرماد غطّى الجزر'),
    ('S08_village',  143.95, 144.70, 44, 'كارثة مباشرة'),
    ('S10_map_out',  149.90, 153.25, 46, 'الانفجار ما وقفش عند الجزيرة'),
    ('S12_hidden',   159.10, 159.95, 46, 'حاجة شغّالة بعيد عن العيون'),
    ('S13_change',   163.40, 166.25, 46, 'صيف السنة اللي بعدها'),
    ('S14_question', 166.60, 168.80, 46, 'إيه اللي حصل؟'),
    ('S21_planet',   196.20, 197.98, 44, 'الرياح لفته حوالي الكوكب'),
    ('S27_turn',     218.30, 219.45, 46, 'بس التبريد لوحده مش أخطر حاجة'),
]
LINES_BY_SHOT = {}
for _n, _a, _b, _sz, _tx in LINES:
    LINES_BY_SHOT[_n] = (_a, _b, _sz, _tx)


# ---------------------------------------------------------------- the card plan
# (name, slot, cue, hold, text) -- one tag at a time, sequenced by the queue
CARDS = [
    ('c2_vei',      'B', 122.30, 2.30, 'VEI 7 — أكبر تصنيف مسجّل'),
    ('c2_bury',     'C', 139.90, 2.00, 'قرية كاملة تحت الرماد'),
    ('c2_hidden',   'C', 160.45, 1.95, 'غازات… مش رماد'),
    ('c2_so2',      'B', 183.60, 2.10, 'SO₂ في الستراتوسفير'),
    ('c2_verdict',  'D', 191.60, 2.70, 'VERDICT:gas'),
    ('c2_hold',     'C', 219.60, 2.20, 'التبريد مش آخر الفصل'),
]
TAGS, QUEUE = [], None
CORNER = C.CORNER_LOGO_BOX
# test switch: the logo audit renders the same frame with the mark suppressed and
# differences the two, which locates the ink exactly instead of guessing from brightness
logo_off = {'corner': False}


def build_tags():
    """the tag queue. Rebuilt by the text test so it can blank the ink identically."""
    global TAGS, QUEUE
    from eng5 import tags5 as TG
    TAGS = []
    for name, slot, cue, hold, text in CARDS:
        if text.startswith('VERDICT:'):
            sprite = verdict_verdict()
        else:
            sprite = C.paper_tag(text, size=44 if len(text) > 20 else 50,
                                 seed=abs(hash(name)) % 89 + 5)
        TAGS.append(TG.Tag(name, slot, cue, hold, sprite))
    QUEUE = TG.TagLayoutQueue(TAGS, T_END).retime()
    return QUEUE


def verdict_verdict():
    """a two-line verdict card whose marks are drawn strokes, not glyphs"""
    rows = [('الرماد بيّن الكارثة', 'tick'), ('الغازات عملت البرودة', 'tick')]
    size = 34
    sps = [C.text_sprite(t, size, fill=C.INK) for t, _ in rows]
    mw = int(size * 1.5)
    padx, pady, gap = 34, 20, 16
    tw = max(sp.width for sp in sps)
    w = tw + mw + padx * 2 + 22 + C.ACCENT_W
    lh = max(max(sp.height for sp in sps), mw)
    h = lh * len(rows) + gap * (len(rows) - 1) + pady * 2
    ss = 4
    big = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    d.rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], radius=C.CARD_RADIUS * ss,
                        fill=C.PAPER + (255,))
    d.rectangle([w * ss - C.ACCENT_W * ss, 0, w * ss, h * ss], fill=C.ACCENT + (255,))
    sheet = big.resize((w, h), Image.LANCZOS)
    for i, ((_, kind), sp) in enumerate(zip(rows, sps)):
        y = pady + i * (lh + gap)
        # the mark sits on the RIGHT of its line, where an RTL sentence ends
        mx = padx + 12
        my = y + lh // 2
        ink = (52, 38, 26, 255) if kind == 'tick' else (150, 52, 38, 255)
        if kind == 'tick':
            d2 = ImageDraw.Draw(sheet, 'RGBA')
            d2.line([(mx, my + int(size * 0.28)), (mx + int(size * 0.34), my + int(size * 0.62))],
                    fill=ink, width=5)
            d2.line([(mx + int(size * 0.34), my + int(size * 0.62)),
                     (mx + int(size * 1.05), my - int(size * 0.55))], fill=ink, width=5)
        sheet.alpha_composite(sp, (padx + mw + 20, y + (lh - sp.height) // 2))
    sh, pad = C.shadow_of(sheet, blur=18, off=(6, 10), alpha=int(255 * 0.45))
    return dict(sprite=sh,
                box=(pad + padx, pad + pady, pad + padx + sps[-1].width,
                     pad + pady + sps[-1].height),
                card_box=(pad, pad, pad + w, pad + h), pad=pad)


# ---------------------------------------------------------------- the frame
def shot_at(t):
    for s in SHOTS:
        if s[2] <= t < s[3]:
            return s
    return SHOTS[-1]


def shot_name(t):
    return shot_at(t)[0]


def cut_of(t):
    for s in SHOTS:
        if s[2] <= t < s[3]:
            return s[0]
    return SHOTS[-1][0]


def levels():
    """moving layers per shot, for the pacing audit"""
    out = {}
    for name, kind, a, b, ip, r in SHOTS:
        ls = ['plate' if kind == '06' else 'graphic', 'grain', 'camera', 'label']
        out[name] = ls
    return out


def blend_frame(i, t):
    """the base frame at t, with the transition at this boundary"""
    idx = len(SHOTS) - 1
    for k, s in enumerate(SHOTS):
        if s[2] <= t < s[3]:
            idx = k
            break
    cur = SHOTS[idx]
    a_fn = SHOT_FNS[cur[0]]
    base = a_fn(t)
    if idx > 0:
        prev = SHOTS[idx - 1]
        p_fn = SHOT_FNS[prev[0]]
        hw = 0.50
        tb = cur[2]
        hard = cur[0] in FORCE_HARD_BEFORE
        if not hard and tb - hw / 2 <= t < tb + hw / 2:
            k = ramp(t, tb - hw / 2, tb + hw / 2)
            pa = p_fn(t).convert('RGB')
            aa = base.convert('RGB')
            if cur[1] == 'map' and prev[1] != 'map':
                base = C.zoom_blur(aa, (1 - k) * 0.5).convert('RGBA')
                base = C.dissolve(base.convert('RGB'), C.zoom_blur(pa, k * 0.4),
                                  0.35 + 0.5 * k).convert('RGBA')
            elif prev[1] == 'map' and cur[1] != 'map':
                base = C.dissolve(C.zoom_blur(pa, (1 - k) * 0.45).convert('RGB'), aa,
                                  k).convert('RGBA')
            else:
                base = C.dissolve(pa, aa, k).convert('RGBA')
    return base.convert('RGBA')


def card_boxes(t):
    """the ink rectangles of every card on screen at t"""
    out = []
    if QUEUE is None:
        return out
    for tag, st in QUEUE.active(t):
        out.append(tag.sprite_rect())
    return out


def card_busy(t):
    """True while any card owns the screen, entry to exit inclusive."""
    if QUEUE is None:
        return False
    for tg in QUEUE.tags:
        if tg.t_in - 0.15 <= t < tg.t_done + 0.15:
            return True
    return False


def corner_free(t):
    """True when no card occupies the watermark's own corner.

    The mark is at (56,44)-(201,140) and never moves, so this asks the cards -- their ink
    boxes, not their padded sprites -- whether any of them is in that corner.
    """
    bx0, by0, bx1, by1 = CORNER
    for (x0, y0, x1, y1) in card_boxes(t):
        if x0 < bx1 and bx0 < x1 and y0 < by1 and by0 < y1:
            return False
    return True


def frame_at(t):
    """one finished frame. A pure function of t."""
    i = int(round(t * 30))
    base = blend_frame(i, t)

    # one text element per area: if a card is on screen, the lower third gets out of its
    # way entirely rather than sitting under it
    busy = card_busy(t)
    name = shot_name(t)
    ln = LINES_BY_SHOT.get(name)
    if ln is not None and not busy:
        t_in, t_out, size, text = ln
        base = label(base, text, 96, H - 150, t, t_in, t_out, size=size)

    if C.T() and QUEUE is not None:
        base = QUEUE.render(base, t)

    # the corner mark: fixed coordinate, drawnafter everything else, hidden only where a
    # card owns that corner
    if C.T() and not logo_off['corner'] and corner_free(t):
        C.corner_logo(base)

    out = C.finish(base.convert('RGB'), i % 240)
    if t > T_END - 0.55:
        out = C.fade_to_black(out, max(0.0, (T_END - t) / 0.55))
    return out


def plate_src(t):
    """the plate key, the source index the shot is on, and the source length.

    The first version of this returned a literal 0 for the index, so the plate audit saw
    197 frames "held" on frame 0 and reported a frozen clip that was not there. It reads
    the plate now.
    """
    s = shot_at(t)
    if s[1] not in PL:
        return (s[1], -1, 0, 1.0)
    p = PL[s[1]]
    return (s[1], p.idx(t - s[2]), p.n, p.bsf)


EVENTS = [
    # a beat every 1.4-2.0 s: these are the points where the picture changes -- a pin, a
    # ring, a bar growing, a stroke landing, a card, a sting -- not decorative markers.
    # The first draft listed one event per shot (27 across 122 s) and the pacing audit
    # measured a 7 s hole; this is the shot-by-shot beat plan that replaces it.
    dict(t=103.40, what='map: Europe marked', sfx='pin'),
    dict(t=104.30, what='the line starts east', sfx=None),
    dict(t=105.20, what='the line reaches Sumbawa', sfx=None),
    dict(t=106.30, what='Sumbawa named', sfx=None),
    dict(t=106.90, what='land on the island', sfx=None),
    dict(t=107.90, what='rings start', sfx=None),
    dict(t=108.90, what='second ring', sfx=None),
    dict(t=109.90, what='third ring', sfx=None),
    dict(t=110.90, what='label holds', sfx=None),
    dict(t=111.90, what='the map settles', sfx=None),
    dict(t=112.70, what='the sea goes out under ash', sfx='water'),
    dict(t=113.60, what='the island rises on the horizon', sfx=None),
    dict(t=114.50, what='the plume thickens', sfx=None),
    dict(t=115.40, what='the day dims', sfx=None),
    dict(t=116.30, what='ash thickens', sfx=None),
    dict(t=117.20, what='cut to the section', sfx=None),
    dict(t=117.90, what='the sheet lands', sfx=None),
    dict(t=118.60, what='the summit steps down', sfx=None),
    dict(t=119.40, what='the caldera opens', sfx='thunder'),
    dict(t=120.20, what='the ghost summit holds', sfx=None),
    dict(t=121.00, what='the height lands', sfx=None),
    dict(t=121.90, what='VEI card: the bars grow', sfx=None),
    dict(t=122.75, what='bar 3 grows', sfx=None),
    dict(t=123.60, what='the 1815 mark lands on bar 7', sfx=None),
    dict(t=124.45, what='the last bar fills red', sfx=None),
    dict(t=125.30, what='the plate holds', sfx=None),
    dict(t=125.95, what='the column starts', sfx=None),
    dict(t=126.80, what='the plume mushrooms', sfx=None),
    dict(t=127.65, what='ash falls back out', sfx=None),
    dict(t=128.50, what='the scale labels', sfx=None),
    dict(t=129.35, what='the column tops out', sfx=None),
    dict(t=130.20, what='ash across the plate', sfx=None),
    dict(t=131.40, what='ash rings: neighbouring islands', sfx=None),
    dict(t=132.30, what='ring 2', sfx=None),
    dict(t=133.20, what='ring 3', sfx=None),
    dict(t=134.10, what='ring 4', sfx=None),
    dict(t=135.00, what='the pin', sfx='pin'),
    dict(t=135.90, what='the rings hold', sfx=None),
    dict(t=136.80, what='ash drifts left', sfx=None),
    dict(t=137.70, what='cut into the village', sfx=None),
    dict(t=138.45, what='clip 06: the buried village', sfx=None),
    dict(t=139.35, what='the card lands', sfx='paper_in'),
    dict(t=140.25, what='the push continues', sfx=None),
    dict(t=141.15, what='ash over the village', sfx=None),
    dict(t=142.05, what='the grade deepens', sfx=None),
    dict(t=142.95, what='the push holds', sfx=None),
    dict(t=143.85, what='card out', sfx='paper_out'),
    dict(t=144.90, what='the toll counts up', sfx='needle'),
    dict(t=145.80, what='the figure climbs', sfx=None),
    dict(t=146.70, what='the caption lands', sfx=None),
    dict(t=147.60, what='the count slows', sfx=None),
    dict(t=148.50, what='the figure holds', sfx=None),
    dict(t=149.40, what='cut out to the arc', sfx=None),
    dict(t=150.20, what='pull out: the rings widen', sfx='pin'),
    dict(t=151.10, what='ring 2', sfx=None),
    dict(t=152.00, what='the arc holds', sfx=None),
    dict(t=152.90, what='the label lands', sfx=None),
    dict(t=153.40, what='ash into the stratosphere', sfx=None),
    dict(t=154.30, what='the band fills', sfx=None),
    dict(t=155.20, what='the wind arrows', sfx=None),
    dict(t=156.10, what='the column feeds it', sfx=None),
    dict(t=157.00, what='the band drifts', sfx=None),
    dict(t=157.90, what='the sheet holds', sfx=None),
    dict(t=158.95, what='the hidden hemisphere', sfx=None),
    dict(t=159.85, what='the haze band crosses', sfx=None),
    dict(t=160.75, what='the card lands', sfx='paper_in'),
    dict(t=161.65, what='ash thins', sfx=None),
    dict(t=162.55, what='card out', sfx='paper_out'),
    dict(t=163.45, what='the year after', sfx=None),
    dict(t=164.35, what='the map drifts', sfx=None),
    dict(t=165.25, what='the label lands', sfx=None),
    dict(t=166.15, what='the question', sfx=None),
    dict(t=167.05, what='the map holds', sfx=None),
    dict(t=167.95, what='cut to the answer', sfx=None),
    dict(t=168.95, what='not fire', sfx=None),
    dict(t=169.85, what='the answer: gas', sfx=None),
    dict(t=170.75, what='the molecule', sfx=None),
    dict(t=171.65, what='the sheet holds', sfx=None),
    dict(t=172.85, what='heat, and cold', sfx=None),
    dict(t=173.75, what='the arrows leave the planet', sfx=None),
    dict(t=174.65, what='the question mark', sfx=None),
    dict(t=175.55, what='the paradox holds', sfx=None),
    dict(t=176.45, what='the plume off the cone', sfx=None),
    dict(t=177.35, what='the arrows land', sfx=None),
    dict(t=178.25, what='the frame holds', sfx=None),
    dict(t=179.15, what='the verdict of the sheet', sfx=None),
    dict(t=179.60, what='ash alone is not the answer', sfx=None),
    dict(t=180.50, what='the veils thin', sfx=None),
    dict(t=181.40, what='ash settles out', sfx=None),
    dict(t=182.30, what='the caption', sfx=None),
    dict(t=182.90, what='SO2, drawn', sfx=None),
    dict(t=183.80, what='the sulphur lands', sfx=None),
    dict(t=184.70, what='the oxygens land', sfx=None),
    dict(t=185.60, what='the molecule holds', sfx=None),
    dict(t=186.50, what='cut to the rise', sfx=None),
    dict(t=186.80, what='the gas reaches the stratosphere', sfx=None),
    dict(t=187.70, what='the plume climbs', sfx=None),
    dict(t=188.60, what='the strata light', sfx=None),
    dict(t=189.50, what='the arrow tops out', sfx=None),
    dict(t=190.40, what='cut to the hemispheres', sfx=None),
    dict(t=190.60, what='both hemispheres', sfx=None),
    dict(t=191.50, what='the north band fills', sfx=None),
    dict(t=192.40, what='the verdict card', sfx='paper_in'),
    dict(t=193.30, what='the south band fills', sfx=None),
    dict(t=194.20, what='the equator', sfx=None),
    dict(t=195.10, what='card out', sfx='paper_out'),
    dict(t=196.10, what='planet: the veil goes round', sfx='sting'),
    dict(t=196.80, what='the veil starts at the volcano', sfx=None),
    dict(t=197.40, what='the veil wraps east', sfx=None),
    dict(t=198.10, what='the sulphate curtain', sfx=None),
    dict(t=199.00, what='the sun dims', sfx=None),
    dict(t=199.90, what='the veil thickens', sfx=None),
    dict(t=200.80, what='the ground cools', sfx=None),
    dict(t=201.70, what='the curtain holds', sfx=None),
    dict(t=202.60, what='the caption', sfx=None),
    dict(t=203.40, what='light in, heat out', sfx=None),
    dict(t=204.30, what='the light returns', sfx=None),
    dict(t=205.20, what='the heat leaves', sfx=None),
    dict(t=206.10, what='the sheet holds', sfx=None),
    dict(t=206.50, what='the energy that came back', sfx=None),
    dict(t=207.40, what='the incoming bar', sfx=None),
    dict(t=208.30, what='the outgoing bar', sfx=None),
    dict(t=209.20, what='the difference', sfx=None),
    dict(t=210.10, what='the temperature curve', sfx=None),
    dict(t=211.00, what='the line drops', sfx=None),
    dict(t=211.90, what='the dip lands', sfx=None),
    dict(t=212.80, what='the recovery starts', sfx=None),
    dict(t=213.70, what='the curve holds', sfx=None),
    dict(t=214.70, what='the mechanism, step by step', sfx=None),
    dict(t=215.60, what='step 2 lights', sfx=None),
    dict(t=216.50, what='step 4 lights', sfx=None),
    dict(t=217.40, what='step 5 lights', sfx=None),
    dict(t=217.95, what='the turn into Chapter 3', sfx=None),
    dict(t=218.80, what='the cool wash', sfx=None),
    dict(t=219.70, what='the card lands', sfx='paper_in'),
    dict(t=220.60, what='the map pulls back', sfx=None),
    dict(t=221.50, what='the wash deepens', sfx=None),
    dict(t=222.40, what='card out', sfx='paper_out'),
    dict(t=223.30, what='the frame holds', sfx=None),
    dict(t=224.20, what='the last look', sfx=None),
]
EVENTS.sort(key=lambda e: e['t'])

text_off = {'on': False}
TEXT_LOG = {}

build_tags()


SHOT_FNS = {
    'S01_bridge': base_s01, 'S02_map': base_s02, 'S03_wake': base_s03,
    'S04_climax': base_s04, 'S05_vei': base_s05, 'S06_column': base_s06,
    'S07_ashfall': base_s07, 'S08_village': base_s08, 'S09_toll': base_s09,
    'S10_map_out': base_s10, 'S11_loft': base_s11, 'S12_hidden': base_s12,
    'S13_change': base_s13, 'S14_question': base_s14, 'S15_gas': base_s15,
    'S16_paradox': base_s16, 'S17_notjust': base_s17, 'S18_so2': base_s18,
    'S19_rise': base_s19, 'S20_split': base_s20, 'S21_planet': base_s21,
    'S22_sulphate': base_s22, 'S23_reflect': base_s23, 'S24_energy': base_s24,
    'S25_cooling': base_s25, 'S26_mechanism': base_s26, 'S27_turn': base_s27,
}


# ---------------------------------------------------------------- plates & sheet builders
_DESK = {}


def _desk_backdrop(lt, dur, seed=7, w=1920, h=1080):
    """the same desk Chapter 1 established, so Chapter 2 is the same film"""
    if seed not in _DESK:
        rng = np.random.default_rng(seed)
        a = np.zeros((h, w, 3), np.float32)
        a[...] = (58, 50, 42)
        n = rng.normal(0, 1, (h // 3, w // 3)).astype(np.float32)
        n = np.asarray(Image.fromarray(((n * 40) + 128).clip(0, 255).astype(np.uint8))
                       .resize((w, h), Image.BILINEAR), np.float32) - 128
        a += n[..., None] * 0.5
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        l = 1.0 - 0.52 * np.clip(np.sqrt(((xx - w * 0.30) / w) ** 2 +
                                         ((yy - h * 0.22) / h) ** 2) / 0.98, 0, 1)
        a *= l[..., None]
        r = np.sqrt(((xx - w / 2) / (w * 0.5)) ** 2 + ((yy - h / 2) / (h * 0.5)) ** 2)
        a *= (1.0 - 0.16 * np.clip((r / r.max() - 0.30) / 0.70, 0, 1) ** 2)[..., None]
        _DESK[seed] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    base = _DESK[seed]
    ox = int(12 * (0.5 - lt / max(dur, 1e-3)))
    oy = int(8 * (0.5 - lt / max(dur, 1e-3)))
    return Image.fromarray(np.roll(np.asarray(base), (oy, ox), axis=(0, 1))).convert('RGBA')


# ---------------------------------------------------------------- photographic backdrops
_BG = {}


def _noise(w, h, octaves=4, seed=0):
    """fractal value noise in [-1,1], built from octaves of smooth upsampling"""
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, total = 1.0, 0.0
    for o in range(octaves):
        gy, gx = max(2, h >> (7 - o)), max(2, w >> (7 - o))
        g = rng.normal(0, 1, (gy, gx)).astype(np.float32)
        im = Image.fromarray(((g * 48) + 128).clip(0, 255).astype(np.uint8))
        f = np.asarray(im.resize((w, h), Image.BICUBIC), np.float32) - 128
        out += (f / 48.0) * amp
        total += amp
        amp *= 0.5
    return out / total


def _beach_backdrop(lt, dur, seed=11):
    """the sea going out under ash: ripple field, foam, the last light dying.

    Drawn, never grabbed: this is a texture bed under Chapter 2's narration, not a claim
    to archival footage.
    """
    key = ('beach', seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    hz = H * 0.50
    if key not in _BG:
        n = _noise(W // 2, H // 2, 4, seed)
        n = np.asarray(Image.fromarray(((n * 40) + 128).clip(0, 255).astype(np.uint8))
                       .resize((W, H), Image.BICUBIC), np.float32) / 40.0
        cloud = np.asarray(Image.fromarray(((n * 40) + 128).clip(0, 255).astype(np.uint8))
                           .filter(ImageFilter.GaussianBlur(26)), np.float32) / 40.0
        a = np.zeros((H, W, 3), np.float32)
        sky = np.clip((hz - yy) / hz, 0, 1)
        a[...] = np.array([11, 12, 14], np.float32)
        a += (sky ** 1.9)[..., None] * np.array([22, 19, 15], np.float32)
        a += (cloud * sky * 18)[..., None] * np.array([0.62, 0.55, 0.46], np.float32)
        # the water: horizontal streaks, not concentric ripples. Stretching the noise
        # 6:1 vertically is what makes a surface read as water at night; regular rings
        # read as a target.
        sea = (yy >= hz).astype(np.float32)
        n3 = _noise(W // 2, max(8, H // 12), 3, seed + 9)
        streak = np.asarray(Image.fromarray(((n3 * 40) + 128).clip(0, 255).astype(np.uint8))
                            .resize((W, H), Image.BICUBIC), np.float32) / 40.0
        depth = np.clip((yy - hz) / (H * 0.36), 0, 1)
        a += (sea * (1 - depth * 0.7))[..., None] * np.array([6, 9, 13], np.float32)
        glow = np.exp(-((xx - W * 0.60) / 460.0) ** 2 - ((yy - hz) / (H * 0.30)) ** 2)
        a += (sea * np.clip(streak + 0.4, 0, 1) ** 2 * glow * 34)[..., None] * \
            np.array([0.72, 0.80, 0.88], np.float32)
        # wet sand in the bottom fifth, with a sheen
        sand = np.clip((yy - H * 0.845) / (H * 0.03), 0, 1)
        a = a * (1 - sand[..., None]) + sand[..., None] * \
            (np.array([34, 30, 25], np.float32) + (n * 9)[..., None])
        a *= (1.0 - 0.16 * np.clip(np.sqrt(((xx - W / 2) / (W / 2)) ** 2 +
                                          ((yy - H / 2) / (H / 2)) ** 2) - 0.35, 0, 1)
              [..., None] / 0.65)
        _BG[key] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    bg = _BG[key].copy()
    d = ImageDraw.Draw(bg, 'RGBA')
    g = ease(ramp(lt, 0.0, dur))
    cx = W * 0.60
    top = hz - 40 - 54 * g
    # the island on the horizon: a low cone, black against the ash sky
    d.polygon([(cx - 300, hz + 3), (cx - 66, top + 6), (cx - 20, top),
               (cx + 54, top + 9), (cx + 320, hz + 3)], fill=(13, 13, 15, 255))
    # the plume, drifting right and thinning
    pw, ph = 660, 340
    pl = Image.new('RGBA', (pw, ph), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pl)
    rng = np.random.default_rng(23)
    for k in range(110):
        f = rng.uniform(0, 1)
        px = 22 + f * (pw - 90) + g * 30
        py = ph - 60 - f * (ph * 0.62) + rng.normal(0, 16)
        rr = rng.uniform(16, 54) * (1.0 - 0.30 * f)
        pd.ellipse([px - rr, py - rr * 0.72, px + rr, py + rr * 0.72],
                   fill=(56 + int(rng.uniform(0, 22)), 54 + int(rng.uniform(0, 16)), 52,
                         int(rng.uniform(30, 90) * (1 - 0.25 * lt / max(dur, 1e-3)))))
    pl = pl.filter(ImageFilter.GaussianBlur(7))
    bg.alpha_composite(pl, (int(cx - 40), int(top - ph + 16)))
    # foam: short broken dashes near the horizon, never a line right across the frame
    rng2 = np.random.default_rng(31)
    for k in range(46):
        y = hz + 14 + rng2.uniform(0, 1.0) ** 1.5 * (H * 0.845 - hz - 18)
        x = rng2.uniform(0, W)
        ln = rng2.uniform(24, 110)
        a = int(rng2.uniform(12, 34))
        d.line([(x, y), (x + ln, y + rng2.uniform(-1, 1))],
               fill=(148, 162, 176, a), width=2)
    return bg


def _planet_backdrop():
    """the planet from outside: lit crescent, dark side, a veil catching the light"""
    key = 'planet'
    if key not in _BG:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        cx, cy, rr = W * 0.50, H * 0.50, 360
        n = _noise(W, H, 4, 91)
        a = np.zeros((H, W, 3), np.float32) + np.array([5, 7, 10], np.float32)
        dx, dy = (xx - cx) / rr, (yy - cy) / rr
        d = np.sqrt(dx ** 2 + dy ** 2)
        inside = d < 1.0
        # light from the upper left; the terminator is soft, not a hard edge
        lit = np.clip(0.55 - 0.62 * (dx * 0.70 + dy * 0.71), 0, 1) ** 1.15
        ocean = np.array([16, 34, 52], np.float32)
        col = ocean[None, None, :] * (0.16 + 1.05 * lit[..., None])
        col = col + (n * 3.2)[..., None] * (0.4 + lit[..., None])
        # cloud banding, which is what makes a sphere read as a sphere
        band = (0.5 + 0.5 * np.sin(yy * 0.042 + n * 2.2 + 1.1)) ** 2
        col = col + (band * lit * 30)[..., None] * np.array([0.85, 0.92, 1.0], np.float32)
        a = np.where(inside[..., None], col, a)
        # the limb: a bright thread on the lit side only
        rim = np.clip(1.0 - np.abs(d - 1.0) * 55, 0, 1)
        a += (rim * (12 + 150 * lit))[..., None] * np.array([0.78, 0.88, 1.0], np.float32)
        rng = np.random.default_rng(4)
        for _ in range(240):
            sx, sy = int(rng.integers(0, W)), int(rng.integers(0, H))
            if (sx - cx) ** 2 + (sy - cy) ** 2 < (rr * 1.06) ** 2:
                continue
            v = float(rng.uniform(30, 130))
            a[max(0, sy - 1):sy + 1, max(0, sx - 1):sx + 1] += v * 0.22
        a *= (1.0 - 0.15 * np.clip(np.sqrt(((xx - W / 2) / (W / 2)) ** 2 +
                                          ((yy - H / 2) / (H / 2)) ** 2) - 0.35, 0, 1)
              [..., None] / 0.65)
        _BG[key] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    return _BG[key].copy()


def _plate_crop(src, rect, z=1.0, pan=(0.0, 0.0)):
    """a Ken Burns crop that is explicit about which pixels it keeps.

    `Camera` widens a crop that is smaller than the output frame, so on a 1280x720 plate
    it can never crop anything: every "pan" was a no-op and the clip's faces stayed in
    frame. This crops the source rectangle by hand, then scales, so what is excluded
    really is excluded.
    """
    x0, y0, x1, y1 = rect
    w = (x1 - x0) / z
    h = (y1 - y0) / z
    cx = (x0 + x1) / 2.0 + pan[0]
    cy = (y0 + y1) / 2.0 + pan[1]
    bx0 = min(max(x0, cx - w / 2.0), x1 - w)
    by0 = min(max(y0, cy - h / 2.0), y1 - h)
    return src.crop((int(bx0), int(by0), int(bx0 + w), int(by0 + h))).resize(
        (W, H), Image.LANCZOS)


def _scaled(im, z):
    if abs(z - 1.0) < 1e-3:
        return im
    return im.resize((int(im.width * z), int(im.height * z)), Image.LANCZOS)


def plate_grade(base, warmth=0.8):
    return C.grade5(base.convert('RGB'), warmth=warmth, sat=0.82).convert('RGBA')


def _arrow(d, p0, p1, colour, width=5, head=18):
    d.line([p0, p1], fill=colour, width=width)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    for s in (+1, -1):
        a = ang + s * 2.55
        d.line([p1, (p1[0] + head * math.cos(a), p1[1] + head * math.sin(a))],
               fill=colour, width=width)


def _vei_sheet(u):
    """VEI 7, on a log scale, with 1815 marked on the last bar."""
    w, h = 1180, 700
    im = _card(w, h, (238, 230, 214), seed=301)
    d = ImageDraw.Draw(im, 'RGBA')
    hand_text(im, 56, 40, 'Volcanic Explosivity Index', size=36, fill=(52, 38, 26))
    d.line([(56, 104), (w - 56, 104)], fill=(80, 64, 48, 130), width=3)
    base_y = h - 190
    x0, step, bw = 78, 132, 84
    # volume of tephra, in m3, as the log axis the index is actually defined on
    vol = [1e4, 1e5, 1e6, 1e7, 1e8, 1e9, 1e10, 1e11]
    labs = ['10⁴', '10⁵', '10⁶', '10⁷', '10⁸', '10⁹', '10¹⁰', '10¹¹']
    top_y = 190
    for k in range(8):
        x = x0 + k * step
        hh = int((base_y - top_y) * (0.42 + 0.58 * k / 7.0))
        grown = ramp(u, 0.05 + k * 0.07, 0.50 + k * 0.07)
        if grown <= 0:
            continue
        col = (108, 92, 76) if k < 7 else (168, 62, 44)
        d.rectangle([x, base_y - int(hh * grown), x + bw, base_y], fill=col + (238,))
        d.line([(x, base_y), (x + bw, base_y)], fill=(90, 74, 58, 220), width=2)
        sp = C.text_sprite(str(k), 30, fill=(40, 32, 26))
        im.alpha_composite(sp, (x + bw // 2 - sp.width // 2, base_y + 10))
        sp = C.text_sprite(labs[k], 22, fill=(96, 82, 66))
        im.alpha_composite(sp, (x + bw // 2 - sp.width // 2, base_y - int(hh) - 32))
    sp = C.text_sprite('حجم الرماد (م٣)', 24, fill=(96, 82, 66), fname=AR)
    im.alpha_composite(sp, (56, 148))
    # the 1815 mark goes UNDER the axis, on the year's own bar: any label drawn beside
    # bars 6 and 7 lands on a bar, because the last bar is the right edge of the sheet.
    if u > 0.56:
        a = ramp(u, 0.56, 0.90)
        x = x0 + 7 * step + bw // 2
        sp = _num_sprite('١٨١٥', 36, (150, 50, 36))
        sp.putalpha(sp.split()[3].point(lambda v: int(v * a)))
        im.alpha_composite(sp, (x - sp.width // 2, base_y + 54))
    hand_text(im, 56, h - 134, 'تامبورا — أكبر ثوران مسجّل في التاريخ البشري', size=32,
              fill=(64, 48, 36), font_name=AR)
    return im


def _column_sheet(u):
    """rock, ash and gas thrown up: the column, with a height scale beside it."""
    w, h = 1180, 720
    im = _card(w, h, (234, 226, 210), seed=311)
    d = ImageDraw.Draw(im, 'RGBA')
    hand_text(im, 56, 40, 'Eruption column', size=36, fill=(52, 38, 26))
    ground = h - 120
    d.line([(90, ground), (w - 90, ground)], fill=(70, 58, 46, 200), width=3)
    cx = w * 0.52
    # the cone
    d.polygon([(cx - 190, ground), (cx - 70, ground - 78), (cx + 70, ground - 78),
               (cx + 190, ground)], fill=(70, 60, 52, 255))
    top = ground - 78
    # the column: a tapering tower that leans downwind and mushrooms at the top
    hh = int(430 * ease(u))
    if hh > 6:
        nn = 34
        for k in range(nn):
            f = k / float(nn - 1)
            yy = top - int(hh * f)
            lean = 52 * f * f
            rr = int(46 * (1 - f) + 150 * f ** 2.6)
            for j in range(3):
                ox = (j - 1) * rr * 0.62 + lean
                oy = (j % 2) * 10 - 5
                rj = int(rr * (0.72 + 0.10 * j))
                al = int((150 - 60 * f) * (0.85 + 0.15 * math.sin(k * 1.3 + j)))
                d.ellipse([cx + ox - rj, yy + oy - rj * 0.55,
                           cx + ox + rj, yy + oy + rj * 0.55],
                          fill=(92 + int(40 * f), 86 + int(38 * f), 80 + int(34 * f), al))
        # ash falling back out of the umbrella, short diagonal strokes
        for k in range(14):
            fx = (k * 53) % 260 - 130
            fy = top - hh + 40 + (k * 37) % 120
            d.line([(cx + fx, fy), (cx + fx - 12, fy + 26)], fill=(96, 88, 78, 120), width=2)
    # the scale, marked
    for k, lab in enumerate(('١٠ كم', '٢٠ كم', '٣٠ كم', '٤٠ كم')):
        yy = int(top - 100 - k * 96)
        d.line([(90, yy), (108, yy)], fill=(90, 76, 62, 210), width=3)
        sp = C.text_sprite(lab, 24, fill=(88, 74, 60))
        im.alpha_composite(sp, (116, yy - sp.height // 2))
    hand_text(im, 56, h - 62, 'صخور ورماد وغازات لفوق', size=32, fill=(64, 48, 36),
              font_name=AR)
    return im


def _num_sprite(text, size, fill):
    """Arabic-Indic figures with no bidi pass, in the one font that actually has them."""
    f = C.font('Amiri-Bold.ttf', size)
    box = f.getbbox(text)
    im = Image.new('RGBA', (box[2] - box[0] + 16, box[3] - box[1] + 16), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((8 - box[0], 8 - box[1]), text, font=f, fill=fill + (255,))
    return im


def _toll_sheet(u):
    w, h = 1000, 560
    im = _card(w, h, (238, 230, 214), seed=321)
    d = ImageDraw.Draw(im, 'RGBA')
    n = int(round(10000 + 90000 * ease(u)))
    digits = str(int(round(n / 1000.0)) * 1000)
    arabic = '٠١٢٣٤٥٦٧٨٩'
    grp = ''
    for k, ch in enumerate(reversed(digits)):
        if k and k % 3 == 0:
            grp = '،' + grp
        grp = arabic[int(ch)] + grp
    sp = _num_sprite(grp, 168, (150, 52, 38))
    im.alpha_composite(sp, ((w - sp.width) // 2, 108))
    sp2 = C.text_sprite('تقديرات مختلفة لعشرات الآلاف', 36, fill=(60, 46, 34),
                        fname=AR)
    im.alpha_composite(sp2, ((w - sp2.width) // 2, 330))
    d.line([(120, 110), (w - 120, 110)], fill=(150, 120, 90, 120), width=2)
    return im


def _fire_gas_sheet(lt):
    w, h = 1100, 560
    im = _card(w, h, (236, 228, 212), seed=331)
    d = ImageDraw.Draw(im, 'RGBA')
    a1 = ramp(lt, 0.15, 0.55)
    a2 = ramp(lt, 1.15, 1.65)
    sp = C.text_sprite('الإجابة مش نار', 64, fill=(150, 62, 40), fname=AR)
    sp = sp.copy()
    sp.putalpha(sp.split()[3].point(lambda v: int(v * a1)))
    im.alpha_composite(sp, ((w - sp.width) // 2, 120))
    if a1 > 0.9:
        d.line([(int(w * 0.30), 250), (int(w * 0.70), 250)], fill=(120, 96, 74, 200),
               width=4)
    sp = C.text_sprite('الإجابة غاز', 84, fill=(52, 44, 38), fname=AR)
    sp = sp.copy()
    sp.putalpha(sp.split()[3].point(lambda v: int(v * a2)))
    im.alpha_composite(sp, ((w - sp.width) // 2, 300))
    if a2 > 0.4:
        # a small molecule glyph, drawn: sulphur dioxide, one S and two O
        cx, cy = w // 2, 470
        d.ellipse([cx - 96, cy - 26, cx - 44, cy + 26], outline=(120, 104, 86, 220), width=3)
        d.ellipse([cx + 44, cy - 26, cx + 96, cy + 26], outline=(120, 104, 86, 220), width=3)
        d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=(168, 120, 52, int(230 * a2)))
        d.line([(cx - 44, cy), (cx - 24, cy)], fill=(120, 104, 86, 200), width=3)
        d.line([(cx + 24, cy), (cx + 44, cy)], fill=(120, 104, 86, 200), width=3)
    return im


def _paradox_sheet(u):
    w, h = 1160, 640
    im = _card(w, h, (236, 228, 212), seed=341)
    d = ImageDraw.Draw(im, 'RGBA')
    hand_text(im, 56, 40, 'المفارقة', size=40, fill=(150, 52, 38), font_name=AR)
    d.line([(56, 108), (w - 56, 108)], fill=(120, 96, 74, 140), width=3)
    # left: a volcano, and heat going up
    lx, ly = int(w * 0.28), h - 150
    d.polygon([(lx - 150, ly), (lx - 40, ly - 190), (lx + 40, ly - 190), (lx + 150, ly)],
              fill=(74, 62, 52, 255))
    for k in range(3):
        yy = ly - 210 - k * 46
        d.ellipse([lx - 46 + k * 4, yy - 18, lx + 46 - k * 4, yy + 18],
                  outline=(170, 96, 60, int(160 * ramp(u, 0.15 + k * 0.2, 0.7 + k * 0.2))),
                  width=4)
    sp = C.text_sprite('حرارة', 40, fill=(64, 50, 38), fname=AR)
    im.alpha_composite(sp, (lx - sp.width // 2, ly + 14))
    # right: the planet, and light turned away
    rx, ry, rr = int(w * 0.74), int(h * 0.52), 132
    d.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], fill=(46, 62, 78, 255))
    d.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], outline=(120, 140, 158, 200), width=3)
    for k in range(7):
        ang = -0.9 + k * 0.30
        x0 = rx + rr * math.cos(ang)
        y0 = ry + rr * math.sin(ang)
        x1 = x0 + 86 * math.cos(ang)
        y1 = y0 + 86 * math.sin(ang)
        a = int(210 * ramp(u, 0.35 + k * 0.05, 0.9 + k * 0.05))
        if a > 4:
            _arrow(d, (int(x0), int(y0)), (int(x1), int(y1)), (232, 196, 128, a), 4, 14)
    sp = C.text_sprite('برودة', 40, fill=(64, 50, 38), fname=AR)
    im.alpha_composite(sp, (rx - sp.width // 2, ry + rr + 18))
    if u > 0.55:
        a = ramp(u, 0.55, 0.95)
        sp = C.text_sprite('إزاي؟', 62, fill=(150, 52, 38), fname=AR)
        sp = sp.copy()
        sp.putalpha(sp.split()[3].point(lambda v: int(v * a)))
        im.alpha_composite(sp, ((w - sp.width) // 2, 116))
    return im


def _notjust_sheet(u):
    w, h = 1120, 600
    im = _card(w, h, (236, 228, 212), seed=351)
    d = ImageDraw.Draw(im, 'RGBA')
    hand_text(im, 56, 40, 'الرماد لوحده مش التفسير', size=36, fill=(52, 38, 26),
              font_name=AR)
    d.line([(56, 104), (w - 56, 104)], fill=(120, 96, 74, 140), width=3)
    # a sun, a dust veil, and a ground line: ash dims, but it settles out
    sx, sy = int(w * 0.22), 210
    d.ellipse([sx - 54, sy - 54, sx + 54, sy + 54], fill=(214, 176, 104, 235))
    ground = h - 130
    d.line([(60, ground), (w - 60, ground)], fill=(80, 66, 54, 220), width=3)
    for k in range(26):
        x = 200 + k * 34
        yy = 300 + int(60 * math.sin(k * 0.9)) + int(90 * ramp(u, 0.2, 1.6))
        if yy < ground - 8:
            d.ellipse([x - 2, yy - 2, x + 2, yy + 2], fill=(150, 138, 122, 170))
    # the veils, which thin out as the ash falls
    for k, y in enumerate((190, 240, 290)):
        a = int(120 * (1 - 0.5 * ramp(u, 0.3 + k * 0.2, 1.4 + k * 0.2)))
        d.line([(200, y), (w - 80, y + 14)], fill=(168, 154, 136, a), width=16)
    sp = C.text_sprite('الرماد بينزل وبيخلص', 34, fill=(66, 52, 40), fname=AR)
    im.alpha_composite(sp, (200, h - 96))
    return im


def _so2_sheet(u):
    w, h = 1120, 640
    im = _card(w, h, (234, 226, 210), seed=361)
    d = ImageDraw.Draw(im, 'RGBA')
    hand_text(im, 52, 36, 'SO₂ — ثاني أكسيد الكبريت', size=40, fill=(52, 38, 26),
              font_name=AR)
    d.line([(52, 104), (w - 52, 104)], fill=(120, 96, 74, 140), width=3)
    # the molecule alone left two thirds of the sheet blank; give it the reaction it
    # stands for, with the atoms in the same two colours as the diagram
    cx, cy = int(w * 0.30), int(h * 0.47)
    r = 66
    for ang in (-90 - 58, -90 + 58):
        ax = cx + r * 1.5 * math.cos(math.radians(ang))
        ay = cy + r * 1.5 * math.sin(math.radians(ang))
        a = ramp(u, 0.25, 0.8)
        d.ellipse([ax - 40, ay - 40, ax + 40, ay + 40], fill=(196, 78, 58, int(225 * a)))
        sp = C.text_sprite('O', 42, fill=(250, 244, 234)).copy()
        sp.putalpha(sp.split()[3].point(lambda v: int(v * a)))
        im.alpha_composite(sp, (int(ax - sp.width / 2), int(ay - sp.height / 2)))
    a = ramp(u, 0.10, 0.6)
    d.ellipse([cx - 48, cy - 48, cx + 48, cy + 48], fill=(214, 176, 84, int(240 * a)))
    sp = C.text_sprite('S', 48, fill=(60, 46, 30)).copy()
    sp.putalpha(sp.split()[3].point(lambda v: int(v * a)))
    im.alpha_composite(sp, (cx - sp.width // 2, cy - sp.height // 2))

    # the reaction, on the paper to the right of the molecule. Stacked, not arrowed
    # across: an LTR arrow inside an RTL layout reads backwards whichever way it points.
    rx = w - 96
    a = ramp(u, 0.45, 0.90)

    def row(txt, right, y, size, fill, fname=None):
        sp = C.text_sprite(txt, size, fill=fill, **({'fname': fname} if fname else {})).copy()
        sp.putalpha(sp.split()[3].point(lambda v: int(v * a)))
        im.alpha_composite(sp, (int(right - sp.width), int(y)))
        return sp.width

    y0 = int(h * 0.28)
    row('H₂O', rx, y0, 44, (56, 44, 32))
    row('+', rx - 96, y0, 44, (120, 100, 80))
    row('SO₂', rx - 150, y0, 44, (56, 44, 32))
    d.line([(rx - 300, y0 + 78), (rx, y0 + 78)],
           fill=(150, 62, 44, int(190 * a)), width=3)
    d.polygon([(rx - 150, y0 + 92), (rx - 162, y0 + 74), (rx - 138, y0 + 74)],
              fill=(150, 62, 44, int(200 * a)))
    row('H₂SO₄', rx, y0 + 128, 46, (150, 52, 38))
    row('قطرات حمض كبريتيك', rx, y0 + 200, 28, (96, 80, 64), 'Amiri-Regular.ttf')
    sp = C.text_sprite('غاز انطلق مع الثوران وطلع لطبقات عالية', 32, fill=(64, 50, 38),
                       fname=AR)
    im.alpha_composite(sp, ((w - sp.width) // 2, h - 96))
    return im


def _rise_sheet(u):
    w, h = 1080, 700
    im = _card(w, h, (234, 226, 210), seed=371)
    d = ImageDraw.Draw(im, 'RGBA')
    # the atmosphere as four strata, labelled
    bands = [('التروبوسفير', (150, 160, 166)), ('الستراتوسفير', (120, 138, 156)),
             ('الميزوسفير', (96, 112, 132)), ('الثيرموسفير', (74, 86, 106))]
    y0 = 90
    bh = (h - 190) // len(bands)
    for k, (name, col) in enumerate(bands):
        d.rectangle([60, y0 + k * bh, w - 60, y0 + (k + 1) * bh],
                    fill=tuple(int(c * 0.72) for c in col) + (235,))
        d.line([(60, y0 + k * bh), (w - 60, y0 + k * bh)], fill=(96, 82, 68, 120),
               width=2)
        sp = C.text_sprite(name, 27, fill=(232, 222, 204), fname=AR)
        im.alpha_composite(sp, (w - 78 - sp.width, y0 + k * bh + 9))
    # the plume climbing into the stratosphere
    top = y0 + int(bh * 1.15)
    if u > 0:
        yy = int(y0 + (h - 190) - ((h - 190) - (top - y0)) * ease(u))
        for k in range(16):
            y = yy + k * 9
            rr = int(30 + k * 4)
            a = int(150 * (1 - k / 18.0))
            d.ellipse([w // 2 - rr, y - 12, w // 2 + rr, y + 12],
                      fill=(212, 200, 180, a))
        _arrow(d, (w // 2, y0 + h - 210), (w // 2, yy - 20), (232, 196, 128, 230), 5, 20)
    hand_text(im, 56, h - 66, 'الغازات وصلت لطبقات عالية', size=34, fill=(64, 48, 36),
              font_name=AR)
    return im


def _split_sheet(u):
    """one eruption, two hemispheres: the veil closes in the south too."""
    w, h = 1200, 620
    im = _card(w, h, (234, 226, 210), seed=381)
    d = ImageDraw.Draw(im, 'RGBA')
    hand_text(im, 52, 34, 'نص الكرة الشمالي ونصها الجنوبي', size=38, fill=(52, 38, 26),
              font_name=AR)
    d.line([(52, 100), (w - 52, 100)], fill=(120, 96, 74, 140), width=3)
    # a globe on the left: graticule, terminator, equator
    cx, cy, rr = 300, 340, 190
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(30, 46, 60, 255))
    for k in range(1, 7):
        yy = cy - rr + k * (2 * rr / 7.0)
        hw = math.sqrt(max(rr * rr - (yy - cy) ** 2, 0))
        d.line([(cx - hw, yy), (cx + hw, yy)], fill=(78, 106, 128, 110), width=2)
    for k in range(1, 9):
        xx = cx - rr + k * (2 * rr / 9.0)
        hh = math.sqrt(max(rr * rr - (xx - cx) ** 2, 0))
        d.line([(xx, cy - hh), (xx, cy + hh)], fill=(78, 106, 128, 90), width=2)
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(120, 140, 158, 220), width=3)
    d.line([(cx - rr, cy), (cx + rr, cy)], fill=(226, 206, 168, 235), width=4)
    # the veil, closing in the north first and then the south
    for k, (y0, t0, name, den) in enumerate(((cy - rr, 0.10, 'فوق', 156),
                                             (cy, 0.50, 'وتحت', 96))):
        a = ramp(u, t0, t0 + 0.32)
        if a <= 0.02:
            continue
        ov = Image.new('RGBA', im.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        od.rectangle([cx - rr, y0, cx + rr, y0 + rr], fill=(226, 214, 186, int(den * a)))
        mask = Image.new('L', im.size, 0)
        ImageDraw.Draw(mask).ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=255)
        od = Image.composite(ov, Image.new('RGBA', im.size, (0, 0, 0, 0)), mask)
        im.alpha_composite(od)
        sp = C.text_sprite(name, 34, fill=(150, 52, 38), fname=AR)
        sp.putalpha(sp.split()[3].point(lambda v: int(v * a)))
        im.alpha_composite(sp, (cx - rr - sp.width - 24, int(y0 + rr * 0.45) - sp.height // 2))
    # the notes, on the paper to the right of the globe
    tx = cx + rr + 70
    sp = C.text_sprite('الشمال', 34, fill=(56, 44, 32), fname=AR)
    im.alpha_composite(sp, (tx, 170))
    sp = C.text_sprite('الرماد والغازات لفوق', 28, fill=(96, 80, 64), fname=AR)
    im.alpha_composite(sp, (tx, 218))
    sp = C.text_sprite('الجنوب', 34, fill=(56, 44, 32), fname=AR)
    im.alpha_composite(sp, (tx, 330))
    sp = C.text_sprite('برضو اتأثر', 28, fill=(96, 80, 64), fname=AR)
    im.alpha_composite(sp, (tx, 378))
    d.line([(tx, 316), (tx + 180, 316)], fill=(120, 96, 74, 140), width=2)
    if u > 0.80:
        a = ramp(u, 0.80, 1.0)
        sp = C.text_sprite('التأثير مش محصور في نص واحد', 30, fill=(56, 44, 32), fname=AR)
        sp.putalpha(sp.split()[3].point(lambda v: int(v * a)))
        im.alpha_composite(sp, ((w - sp.width) // 2, h - 66))
    return im


def _globe_backdrop(lt, dur):
    """the planet, unlabelled, turning very slowly: this is not a map of anything familiar"""
    w, h = 1400, 1400
    key = 'globe'
    if key not in _DESK:
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im, 'RGBA')
        d.ellipse([40, 40, w - 40, h - 40], fill=(28, 44, 58, 255))
        d.ellipse([40, 40, w - 40, h - 40], outline=(96, 124, 146, 160), width=4)
        r = w / 2 - 40
        cx = cy = w / 2
        for k in range(1, 9):
            y = cy - r + k * (2 * r / 9.0)
            hw = math.sqrt(max(r * r - (y - cy) ** 2, 0))
            d.line([(cx - hw, y), (cx + hw, y)], fill=(78, 106, 128, 90), width=2)
        for k in range(1, 12):
            x = cx - r + k * (2 * r / 12.0)
            hh = math.sqrt(max(r * r - (x - cx) ** 2, 0))
            d.line([(x, cy - hh), (x, cy + hh)], fill=(78, 106, 128, 70), width=2)
        _DESK[key] = im
    g = _DESK[key].copy()
    d = ImageDraw.Draw(g, 'RGBA')
    # the sulphate veil, spreading from a point high in the north
    sx, sy = g.width * 0.56, g.height * 0.34
    a = ramp(lt, 0.2, 1.6)
    for k in range(9):
        rr = int((60 + k * 58) * (0.4 + 0.6 * ease(min(1.0, a))))
        al = int(46 * max(0.0, 1 - k / 9.0) * min(1.0, a))
        if rr > 4 and al > 1:
            d.ellipse([sx - rr, sy - rr * 0.7, sx + rr, sy + rr * 0.7],
                      fill=(226, 214, 186, al))
    sp = C.text_sprite('١٨١٦', 150, fill=(228, 214, 186))
    sp.putalpha(sp.split()[3].point(lambda v: int(v * 0.36)))
    g.alpha_composite(sp, (int(g.width * 0.30), int(g.height * 0.62)))
    return g


def _sulphate_sheet(u):
    w, h = 1140, 600
    im = _card(w, h, (234, 226, 210), seed=391)
    d = ImageDraw.Draw(im, 'RGBA')
    hand_text(im, 52, 36, 'ستارة من الكبريتات', size=38, fill=(52, 38, 26), font_name=AR)
    d.line([(52, 102), (w - 52, 102)], fill=(120, 96, 74, 140), width=3)
    # sun, veil, ground: the veil thickens across u
    sx, sy = int(w * 0.30), 190
    d.ellipse([sx - 52, sy - 52, sx + 52, sy + 52], fill=(222, 184, 108, 240))
    a = ramp(u, 0.05, 0.9)
    for k in range(7):
        y = 250 + k * 26
        al = int(150 * a * (1 - k / 9.0))
        d.line([(80, y), (w - 80, y - 10)], fill=(206, 194, 174, al), width=18)
    ground = h - 130
    d.line([(60, ground), (w - 60, ground)], fill=(80, 66, 54, 220), width=3)
    sp = C.text_sprite('الشمس بقت أضعف', 36, fill=(64, 50, 38), fname=AR)
    sp.putalpha(sp.split()[3].point(lambda v: int(v * ramp(u, 0.3, 0.85))))
    im.alpha_composite(sp, (int(w * 0.46), ground + 22))
    return im


def _reflect_sheet(u):
    w, h = 1140, 620
    im = _card(w, h, (234, 226, 210), seed=401)
    d = ImageDraw.Draw(im, 'RGBA')
    hand_text(im, 52, 36, 'ضوء داخل، حرارة لبرّة', size=38, fill=(52, 38, 26), font_name=AR)
    d.line([(52, 102), (w - 52, 102)], fill=(120, 96, 74, 140), width=3)
    # sun on the left, veil in the middle, ground on the right
    sx = 150
    d.ellipse([sx - 44, 220, sx + 44, 308], fill=(224, 186, 110, 240))
    for k in range(5):
        y = 250 + k * 16
        a = int(210 * ramp(u, 0.05 + k * 0.04, 0.6 + k * 0.04))
        if a > 4:
            d.line([(sx + 60, y), (700, y - 30)], fill=(232, 196, 128, a), width=4)
    vy = 300
    for k in range(6):
        al = int(60 * ramp(u, 0.15, 0.8) * (1 - k / 8.0))
        d.line([(600 + k * 8, 180), (620 + k * 8, 440)], fill=(210, 200, 182, al),
               width=26)
    ground = h - 140
    d.rectangle([700, ground, w - 40, ground + 40], fill=(96, 78, 60, 235))
    sp = C.text_sprite('الضوء اللي رجع', 30, fill=(140, 52, 38), fname=AR)
    sp.putalpha(sp.split()[3].point(lambda v: int(v * ramp(u, 0.45, 0.95))))
    im.alpha_composite(sp, (int(w * 0.60), ground - 44))
    sp = C.text_sprite('حرارة', 30, fill=(64, 50, 38), fname=AR)
    im.alpha_composite(sp, (760, ground + 52))
    return im


def _energy_sheet(u):
    w, h = 1100, 600
    im = _card(w, h, (234, 226, 210), seed=411)
    d = ImageDraw.Draw(im, 'RGBA')
    hand_text(im, 52, 36, 'الطاقة اللي رجعت', size=38, fill=(52, 38, 26), font_name=AR)
    d.line([(52, 102), (w - 52, 102)], fill=(120, 96, 74, 140), width=3)
    # incoming vs outgoing as two measured bars
    for k, (lab, frac, col) in enumerate((('واصل', 1.00, (150, 120, 74)),
                                          ('راجع', 0.86, (168, 92, 62)))):
        y = 200 + k * 150
        sp = C.text_sprite(lab, 32, fill=(60, 46, 34), fname=AR)
        im.alpha_composite(sp, (90, y - 12))
        L = int((w - 380) * frac * ease(ramp(u, 0.1 + k * 0.2, 0.7 + k * 0.2)))
        d.rectangle([220, y, 220 + max(L, 2), y + 54], fill=col + (230,))
        sp = C.text_sprite('%d٪' % int(round(frac * 100)), 30, fill=(60, 46, 34), fname=AR)
        im.alpha_composite(sp, (230 + max(L, 2), y + 8))
    sp = C.text_sprite('الفرق هو اللي بيبرّد', 34, fill=(140, 52, 38), fname=AR)
    sp.putalpha(sp.split()[3].point(lambda v: int(v * ramp(u, 0.5, 0.95))))
    im.alpha_composite(sp, (90, h - 96))
    return im


def _loft_sheet(u):
    """ash lifted into the stratosphere and carried round by the wind."""
    w, h = 1140, 560
    im = _card(w, h, (234, 226, 210), seed=421)
    d = ImageDraw.Draw(im, 'RGBA')
    hand_text(im, 52, 34, 'الرماد على الرياح', size=38, fill=(52, 38, 26), font_name=AR)
    d.line([(52, 100), (w - 52, 100)], fill=(120, 96, 74, 140), width=3)
    ground = h - 86
    d.line([(70, ground), (w - 70, ground)], fill=(96, 80, 64, 170), width=3)
    sp = C.text_sprite('ستراتوسفير', 28, fill=(72, 58, 44), fname=AR)
    im.alpha_composite(sp, (70, 116))
    top = 152
    # no flat fill anywhere on this sheet: a grey rectangle over the band read as a
    # lozenge printing defect, so the layer is drawn as its own grain
    a = ramp(u, 0.05, 0.85)
    if a > 0.02:
        rng = np.random.default_rng(8)
        for _k in range(620):
            fx = float(rng.uniform(0, 1))
            fy = float(rng.uniform(0, 1))
            x = 74 + fx * (w - 148) + 70 * a * 0.35
            y = top + fy * 92 + 8 * math.sin(fx * 6.0 + 1.4)
            rr = float(rng.uniform(0.8, 2.4))
            if x > w - 74:
                continue
            d.ellipse([x - rr, y - rr * 0.62, x + rr, y + rr * 0.62],
                      fill=(118 + int(rng.uniform(0, 26)), 108, 96,
                            int(rng.uniform(60, 150) * a)))
    d.line([(74, top + 96), (w - 74, top + 96)], fill=(120, 100, 78, 150), width=2)
    # the column feeding it: a soft blurred cone rising from the ground into the band
    cw_, chh = 200, ground - (top + 92)
    ch_ = Image.new('RGBA', (cw_, chh), (0, 0, 0, 0))
    cd = ImageDraw.Draw(ch_)
    for k in range(30):
        f = k / 29.0
        y = chh - 6 - f * (chh - 10)
        rr = 34 - f * 16
        cd.ellipse([cw_ / 2 - rr, y - rr * 0.55, cw_ / 2 + rr, y + rr * 0.55],
                   fill=(150, 138, 120, int(140 * (1 - f * 0.35) * ramp(u, 0.0, 0.5))))
    ch_ = ch_.filter(ImageFilter.GaussianBlur(8))
    im.alpha_composite(ch_, (30, top + 92))
    # a mountain under the column, so the sheet says where the ash came from
    d.polygon([(58, ground), (132, ground - 46), (168, ground - 96), (204, ground - 46),
               (278, ground)], fill=(84, 72, 60, 235))
    d.line([(58, ground), (278, ground)], fill=(70, 58, 48, 235), width=2)
    # the wind, drawn as arrows that run with the band
    for k in range(3):
        x0 = 360 + k * 250
        _arrow(d, (x0, top + 140), (x0 + 150, top + 140),
               (150, 122, 82, int(225 * ramp(u, 0.20 + k * 0.10, 0.70 + k * 0.10))),
               4, 14)
    sp = C.text_sprite('رياح شرقية', 28, fill=(60, 48, 36), fname=AR)
    im.alpha_composite(sp, (w - 84 - sp.width, top + 160))
    sp = C.text_sprite('الرماد بيتحرك مع الرياح لأسابيع', 27, fill=(64, 50, 38), fname=AR)
    im.alpha_composite(sp, (w - 72 - sp.width, 122))
    return im


def _cooling_sheet(u):
    """the temperature curve, drawn as a line that drops and creeps back"""
    w, h = 1140, 620
    im = _card(w, h, (234, 226, 210), seed=431)
    d = ImageDraw.Draw(im, 'RGBA')
    hand_text(im, 52, 36, 'درجة الحرارة', size=38, fill=(52, 38, 26), font_name=AR)
    x0, x1 = 100, w - 90
    y0, y1 = 130, h - 150
    d.line([(x0, y1), (x1, y1)], fill=(96, 80, 64, 220), width=3)
    d.line([(x0, y0), (x0, y1)], fill=(96, 80, 64, 220), width=3)
    # baseline (before) and the dip after the eruption, then the slow recovery
    by = y0 + 90
    d.line([(x0, by), (x1, by)], fill=(140, 120, 96, 140), width=2)
    pts = []
    n = 90
    for k in range(n + 1):
        f = k / float(n)
        if f < 0.28:
            y = by + 4 * math.sin(f * 22)
        else:
            drop = 118 * math.exp(-((f - 0.34) / 0.09) ** 2)
            rec = 118 * math.exp(-((f - 0.34) / 0.26) ** 2) * 0.0
            y = by + drop - rec + 3 * math.sin(f * 14)
        pts.append((x0 + (x1 - x0) * f, y))
    cut = int(len(pts) * ease(u))
    if cut > 2:
        d.line(pts[:cut], fill=(150, 62, 44, 240), width=6, joint='curve')
    if u > 0.55:
        a = ramp(u, 0.55, 0.95)
        sp = C.text_sprite('سنة ١٨١٦', 28, fill=(140, 52, 38), fname=AR)
        sp.putalpha(sp.split()[3].point(lambda v: int(v * a)))
        im.alpha_composite(sp, (int(x0 + (x1 - x0) * 0.34) - sp.width // 2, by - 40))
        sp = C.text_sprite('رجعت بالراحة', 30, fill=(64, 50, 38), fname=AR)
        sp.putalpha(sp.split()[3].point(lambda v: int(v * a)))
        im.alpha_composite(sp, (int(x0 + (x1 - x0) * 0.74), y0 + 4))
    return im


def _mechanism_sheet(u):
    w, h = 1120, 640
    im = _card(w, h, (234, 226, 210), seed=441)
    d = ImageDraw.Draw(im, 'RGBA')
    hand_text(im, 52, 36, 'الآلية، خطوة بخطوة', size=38, fill=(52, 38, 26), font_name=AR)
    d.line([(52, 102), (w - 52, 102)], fill=(120, 96, 74, 140), width=3)
    # the chain reads right to left across the card, not down a spine: the five steps
    # only need one line, and a stack left two thirds of the paper empty
    steps = ('ثوران', 'SO₂ لفوق', 'كبريتات', 'شمس أضعف', 'برودة')
    y = 300
    arts, gap = [], 54
    for k, s in enumerate(steps):
        a = ramp(u, 0.13 * k, 0.13 * k + 0.26)
        sp = C.text_sprite(s, 38, fill=(56, 44, 32), fname=AR).copy()
        sp.putalpha(sp.split()[3].point(lambda v: int(v * a)))
        arts.append((sp, a))
    arts = arts[::-1]        # RTL: the first beat of the chain sits at the right edge
    y = 300
    total = sum(a.width for a, _ in arts) + gap * (len(arts) - 1)
    x = (w - total) // 2
    for k, (sp, a) in enumerate(arts):
        im.alpha_composite(sp, (x, y - sp.height // 2))
        if k < len(arts) - 1:
            ax = x + sp.width + 10
            _arrow(d, (ax + gap - 20, y), (ax, y), (150, 62, 44, int(220 * a)), 3, 12)
        x += sp.width + gap
    d.line([(84, y + 96), (w - 84, y + 96)], fill=(120, 96, 74, int(120 * u)), width=2)
    a = ramp(u, 0.5, 0.85)
    sp = C.text_sprite('من الثوران لحد البرودة', 30, fill=(96, 80, 64), fname=AR).copy()
    sp.putalpha(sp.split()[3].point(lambda v: int(v * a)))
    im.alpha_composite(sp, ((w - sp.width) // 2, y + 132))
    return im
