#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chapter 1 — «الصيف اللي مجاش» : 0:00.00 → 1:49.48 (3285 frames).

Built on the v6 pilot engine, which is the approved look. Shots 1-9 of this chapter ARE
the pilot, with the same numbers; everything after it is new. Where this chapter and the
pilot differ, the difference is a rule, not a taste:

  * plates are decoded at their native rate and the camera NEVER upscales. 01, 02, 03,
    04, 05, 06, 07, 08, 10 and 12 are 720p sources: they are cropped 16:9 at 1:1 and then
    widened (never pushed in) until the crop is at least 1920 wide, so the only resampling
    left is one bilinear 1280→1920 pass. There is no second generation.
  * a shot that needs more seconds than its plate has is slowed by a CONSTANT factor --
    a clean setpts resample. Never held, never wrapped, never flow-interpolated.
  * the director's 34 shots are edited to 27 screen shots: where two adjacent shots are
    the same clip doing the same thing, splicing them would read as a jump cut, so they
    become one continuous move. Every VO line is still covered.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from eng5 import core5 as C
from eng5 import tags5 as TG
from eng5 import world5 as W5

W, H = C.W, C.H

# ---------------------------------------------------------------- plates
# every clip is 24 fps and the timeline is 30, so a plate steps 0.8 files per frame
# only the clips this chapter is allowed to use: 01 02 03 09 (America / Europe / hook)
# and 04 05 (Sumbawa and the eruption, which its own narration names). 06 07 08 belong to
# chapters 2 and 3 and are not opened here at all -- loading them is how they got burned.
CH1_PLATES = ('01', '02', '03', '04', '05', '09')
PL = {k: C.Plate(k, src_fps=24.0) for k in CH1_PLATES}

SNOW_FG = C.Snow(n=46, speed=(240, 380), size=(1.6, 3.2), wind=-40, seed=21, alpha=(40, 80))
SNOW_MID = C.Snow(n=300, speed=(90, 200), size=(0.9, 2.2), wind=-26, seed=7, alpha=(60, 140))
RAIN = C.Rain(n=430, seed=11, alpha=(22, 62))
ASH = C.Snow(n=150, speed=(14, 34), size=(1.0, 2.2), wind=7, seed=31, alpha=(30, 74))
ASH_HVY = C.Snow(n=260, speed=(20, 52), size=(1.2, 2.8), wind=11, seed=43, alpha=(40, 96))
EMBERS = C.Snow(n=90, speed=(-180, -90), size=(1.2, 2.6), wind=16, seed=57, alpha=(60, 150),
                color=(255, 176, 96))
MOTE = C.Snow(n=70, speed=(-22, -8), size=(1.0, 2.4), wind=6, seed=63, alpha=(24, 62))


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def ramp(t, a, b):
    return max(0.0, min(1.0, (t - a) / max(1e-6, b - a)))


# ---------------------------------------------------------------- shot map
# (name, plate, t_in, t_out, in-point, rate) -- rate < 1 is a constant slow-down
SHOTS = [
    # CHAPTER 1 OWNS THE FOUR AMERICA / EUROPE / HOOK CLIPS AND NOTHING ELSE.
    # The AI clips are for the dramatic beats spread across the ten minutes, not for
    # filling a chapter. Everything else in this chapter is documentary motion graphics:
    # the map and its plates, the case board, the sun, the archive and the collage.
    ('S01_house',     '09',   0.00,   4.35, 0.00, 1.0000),
    ('S02_farmers',   '01',   4.35,   9.97, 0.00, 1.0000),
    ('S03_europe',    '02',   9.97,  15.96, 0.00, 1.0000),
    ('S04_map',       'map', 15.96,  22.42, 0.00, 1.0000),
    ('S05_monster',   '03',  22.42,  28.97, 2.95, 0.7455),
    # 0:29-1:04 is cut to the narration lines, not to an even split:
    #   L7 28.97  what people saw           L10 46.96 a table of readings
    #   L8 33.51  frost, New England        L11 51.76 a harvest under threat
    #   L9 39.27  the 8 June ledger         L12 55.81 the summer left the fields
    #   L13 59.95 who could do this
    ('S06_map_arc',   'map', 28.97,  33.51, 0.00, 1.0000),
    ('S07_frost',     'map', 33.51,  39.27, 0.00, 1.0000),
    ('S08_ledger',    'gfx', 39.27,  46.22, 0.00, 1.0000),
    ('S09_table',     'gfx', 46.22,  51.31, 0.00, 1.0000),
    ('S10_strip',     'gfx', 51.31,  59.11, 0.00, 1.0000),
    ('S11_question',  'map', 59.11,  64.31, 0.00, 1.0000),
    ('S12_board',     'gfx', 64.31,  91.50, 0.00, 1.0000),
    ('S15_sumbawa',   '04',  91.50,  96.11, 2.40, 0.8800),
    ('S16_eruption',  '05',  96.11, 102.60, 1.90, 0.8700),
    ('S17_reckoning', 'map', 102.60, 109.48, 0.00, 1.0000),
]
T_END = 109.48
BY_NAME = {s[0]: s for s in SHOTS}
MAP_SHOTS = {'S04_map', 'S06_map_arc', 'S07_frost', 'S11_question', 'S17_reckoning'}

# transitions: a dissolve between live plates, the map's zoom-blur in/out, and three
# hard cuts where a dissolve would blunt the edit
FORCE_HARD_BEFORE = {'S05_monster', 'S12_board', 'S15_sumbawa', 'S16_eruption'}


def shot_at(t):
    for s in SHOTS:
        if s[2] <= t < s[3]:
            return s
    return SHOTS[-1]


def neighbours(i):
    return SHOTS[i - 1], SHOTS[i]


def trans_window(a, b, t):
    """(kind, progress, half-width) for the boundary between shots a and b, or None"""
    tb = b[2]
    if b[0] in FORCE_HARD_BEFORE:
        return None
    if a[1] == 'map' or b[1] == 'map':
        hw = 0.60
        return ('map', t, hw)
    hw = 0.65
    return ('dissolve', t, hw)


def cut_of(t):
    for i, s in enumerate(SHOTS):
        if i == 0:
            continue
        a = SHOTS[i - 1]
        tw = trans_window(a, s, t)
        if tw is None:
            continue
        kind, _, hw = tw
        if abs(t - s[2]) <= hw / 2 + 1e-9:
            return s[2]
    return None


def plate_src(t):
    """exactly which decoded file fed this frame; the QA reads this, not a claim"""
    s = shot_at(t)
    name, key, t0, t1, ip, rate = s
    if key in ('map', 'gfx'):
        # graphics plates are generated per frame, so there is no clip frame to report
        return (key, int(round((t - t0) * 30)), 0, 0.0)
    p = PL[key]
    return (key, p.idx(ip + (t - t0) * rate), p.n, p.bsf)


def shot_name(t):
    return shot_at(t)[0]


# ---------------------------------------------------------------- the map
MAP_W, MAP_H = 2600, 1462
_MAPBASE = {}


def map_obj():
    if 'm' not in _MAPBASE:
        _MAPBASE['m'] = W5.Map(lon_a=-132, lon_b=150, lat_a=-30, lat_b=80,
                               x0=0, y0=0, w=MAP_W, h=MAP_H, ss=3)
    return _MAPBASE['m']


def map_base():
    """the dark coastline plate, built once and reused by every map shot"""
    if 'b' not in _MAPBASE:
        m = map_obj()
        bg = Image.new('RGB', (MAP_W, MAP_H), (8, 10, 13)).convert('RGBA')
        _MAPBASE['b'] = Image.alpha_composite(bg, W5.compose_map(bg, m, 0)).convert('RGB')
    return _MAPBASE['b']


def grader(base):
    return C.grade5(base.convert('RGB'), warmth=0.90, sat=0.90).convert('RGBA')


def focus(base, cx, cy, r=260, colour=(255, 196, 128), amount=0.30):
    """a soft light on the point the beat is about. Without it a ring over dark ocean
    reads as a stray hairline rather than as the thing the narrator is pointing at."""
    if amount <= 0.004:
        return base
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.25) ** 2)
    g = np.clip(1.0 - d / max(r, 1e-3), 0, 1) ** 2 * amount
    a = np.asarray(base.convert('RGB'), np.float32)
    a += g[..., None] * np.array(colour, np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')


ARCHIVE_TINT = (238, 231, 216)


def archive_sheet(w, h, seed=0, age=0.55):
    """a sheet of paper that is allowed to look old, drawn rather than photographed.

    Public-domain archive scans are the right source for real documents; this is the
    frame's paper STOCK, and it says nothing historically. What makes it read as held
    paper is the uneven age staining and a slightly torn edge, so both are generated from
    a seed and are identical every frame.
    """
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    base = np.zeros((h, w, 3), np.float32)
    base[...] = np.array(ARCHIVE_TINT, np.float32)
    # broad staining: two low-frequency fields, so the paper is not evenly yellow
    for k in range(2):
        fy = rng.uniform(1.5, 3.5, 4)
        fx = rng.uniform(1.5, 3.5, 4)
        f = (np.sin(xx / w * math.pi * fy[0] + 0.7 * k) * 0.5 + 0.5) *             (np.cos(yy / h * math.pi * fx[1] + 1.1 * k) * 0.5 + 0.5)
        base -= (f * 14.0 * age)[..., None] * np.array([0.9, 1.0, 1.3], np.float32)
    # edge darkening, like a page that has been handled for two hundred years
    edge = np.minimum(np.minimum(xx, w - 1 - xx) / (w * 0.5),
                      np.minimum(yy, h - 1 - yy) / (h * 0.5))
    base *= (0.80 + 0.20 * np.clip(edge * 2.6, 0, 1))[..., None]
    base += rng.normal(0, 3.2, (h, w, 1)).astype(np.float32)
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert('RGBA')


def ruled_lines(im, x0, x1, y0, dy, n, colour=(92, 84, 72), alpha=54, wobble=0.0, seed=0):
    """the ruled lines of a ledger page -- the ruling only; the words are real glyphs now."""
    rng = np.random.default_rng(seed)
    d = ImageDraw.Draw(im, 'RGBA')
    for k in range(n):
        y = y0 + k * dy + (rng.normal(0, wobble) if wobble else 0)
        d.line([(x0, y), (x1, y + (rng.normal(0, 1.2) if wobble else 0))],
               fill=colour + (alpha,), width=2)
    return im


# the writing hands. Amiri carries the Arabic cards; for the English ledger there is no
# cursive face in the repo, so the hand is Amiri italic-slanted -- a period-appropriate
# script hand would be better and is on the list to licence.
HAND = 'Amiri-Regular.ttf'
HAND_BOLD = 'Amiri-Bold.ttf'


def hand_text(im, x, y, text, size=34, fill=(43, 31, 20), font_name=None, track=0):
    """type on paper.

    Arabic is written ONCE as a shaped string through ar(): drawing it one character at a
    time breaks every joining form and produced reversed, disconnected letters on the case
    board. Latin is drawn the same way. `track` is applied by spacing the whole string.
    """
    name = font_name or HAND
    if text_off['on']:
        return im
    shaped = C.ar(text) if any('\u0600' <= ch <= '\u06ff' for ch in text) else text
    if track:
        f = C.font(name, size)
        d = ImageDraw.Draw(im, 'RGBA')
        # letter-spacing: draw the shaped string and then widen it by resampling, which
        # keeps the joins intact
        sp = C.text_sprite(text, size=size, fill=fill, fname=name)
        sp = sp.resize((int(sp.width + track * len(text)), sp.height), Image.LANCZOS)
        im.alpha_composite(sp, (x, y))
        TEXT_LOG[name] = TEXT_LOG.get(name, 0) + len(text)
        return im
    sp = C.text_sprite(text, size=size, fill=fill, fname=name)
    im.alpha_composite(sp, (x, y))
    TEXT_LOG[name] = TEXT_LOG.get(name, 0) + len(text)
    TEXT_LOG.setdefault(('path', name), C.font(name, size).path)
    return im


TEXT_LOG = {}
# a switch the text-presence test flips: when True every lettering call is skipped, so the
# same document can be rendered twice and the two frames differenced inside the paper
text_off = {'on': False}


def handwritten_lines(im, x, y, lines, size=34, dy=46, fill=(43, 31, 20), font_name=None):
    """a page of real handwriting: every line is drawn as glyphs, never as a bar.

    The previous version drew grey lozenges for "text", which read as redaction and carried
    no content. This draws the actual sentences the shot is about, and the QA counts the
    ink it produced so a silent fallback cannot pass again.
    """
    for k, line in enumerate(lines):
        hand_text(im, x, y + k * dy, line, size=size,
                  fill=fill, font_name=font_name or HAND)
    return im


def label(base, text, x, y, t, t_in, t_out, size=48, fill=(226, 218, 200), shadow=False):
    """a line of type that grows in and is gone by t_out; used inside the map plates

    `shadow` adds a soft dark drop under the type. Ivory on a pale field measured 1.77:1
    on the frost map, so bare type over the plates now carries its own contrast.
    """
    if not (t_in <= t < t_out) or not C.T():
        return base
    a = min(ramp(t, t_in, t_in + 0.5), 1.0 - ramp(t, t_out - 0.4, t_out))
    if a <= 0:
        return base
    sp = C.text_sprite(text, size=size, fill=fill)
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
    sc = 0.86 + 0.14 * ease(ramp(t, t_in, t_in + 0.55))
    if sc < 0.999:
        sp = sp.resize((int(sp.width * sc), int(sp.height * sc)), Image.LANCZOS)
    if a < 1:
        sp = sp.copy()
        sp.putalpha(sp.split()[3].point(lambda v: int(v * a)))
    base.alpha_composite(sp, (x, y))
    return base


# places used by the chapter's maps
NE_LL = (-71.0, 42.3)          # New England
EU_LL = (7.0, 47.0)            # central Europe
SU_LL = (117.5, -8.4)          # Sumbawa
ICE_LL = (-16.0, 64.7)         # Iceland: the glacial burst of 1810
ROUTE_LL = [(-71.0, 42.3), (-52.0, 46.5), (-30.0, 50.0), (-12.0, 51.5), (5.0, 50.5),
            (24.0, 47.5), (50.0, 42.5), (78.0, 32.0), (102.0, 10.0), (117.5, -8.4)]


def base_s01(t):
    """June 1816 over Lake Geneva: the cold open"""
    u = ramp(t, 0.0, 2.0)
    cam = C.Camera(zoom=1.30 - 0.14 * ease(min(1.0, t / 4.35)), pan=(0, -20))
    im = C.grade5(PL['09'].frame(t, cam), warmth=1.55 - 0.55 * ease(u),
                  sat=0.62 + 0.24 * ease(u))
    base = im.convert('RGBA')
    d = ramp(t, 1.0, 2.6)
    if d > 0:
        base = SNOW_MID.draw(base, t, density=0.35 * d)
    return base


def base_s02(t):
    """the farmers look up, snow thickening on the word"""
    lt = t - 4.35
    cam = C.Camera(zoom=1.04 + 0.09 * ease(lt / 5.62), pan=(10, 0))
    base = C.grade5(PL['01'].frame(lt, cam), warmth=0.92, sat=0.80).convert('RGBA')
    base = SNOW_MID.draw(base, t, density=0.55 + 0.30 * ramp(t, 7.43, 8.65))
    return SNOW_FG.draw(base, t, density=0.6, blur=1.6)


def base_s03(t):
    """Europe: rain and mud, hammering from the word مطر"""
    lt = t - 9.97
    cam = C.Camera(zoom=1.05 - 0.03 * ease(lt / 5.99), pan=(-8, 0))
    base = C.grade5(PL['02'].frame(lt, cam), warmth=0.80, sat=0.74).convert('RGBA')
    base = RAIN.draw(base, t, density=0.30 + 0.55 * ramp(t, 10.6, 11.9))
    return SNOW_FG.draw(base, t, density=0.22, blur=1.8)


def base_s04(t):
    """the secret is not in these continents: the route draws out of frame"""
    lt = t - 15.96
    dur = 6.46
    m = map_obj()
    cam = C.Camera(zoom=1.34 - 0.08 * (0.6 * ease(lt / dur) + 0.4 * (lt / dur)),
                   pan=(-120 + 200 * (lt / dur) + 9 * math.sin(lt * 0.7),
                        -40 + 70 * (lt / dur)), src=(MAP_W, MAP_H))
    base = cam.apply(map_base()).convert('RGBA')
    base = ASH.draw(base, t, density=0.8)
    d = ImageDraw.Draw(base)
    S = lambda ll: cam.to_screen(*m.px(*ll))
    if t >= 16.53:
        p = S(NE_LL)
        C.pin(base, p[0], p[1], t, 16.53, r=11)
    if t >= 17.35:
        W5.dashed_line(d, [S(ll) for ll in ROUTE_LL[:5]], C.GOLD + (240,), width=4,
                       dash=20, gap=14, upto=ramp(t, 17.35, 19.04))
    if t >= 19.04:
        p = S(EU_LL)
        C.pin(base, p[0], p[1], t, 19.04, r=9)
    if t >= 19.72:
        W5.dashed_line(d, [S(ll) for ll in ROUTE_LL], C.GOLD + (245,), width=5,
                       dash=22, gap=15, upto=ramp(t, 19.72, 21.46))
    if t >= 21.02:
        p = S(SU_LL)
        C.pin(base, p[0], p[1], t, 21.02, r=12)
    if t >= 20.36:
        u = ramp(t, 20.36, 21.46)
        val = f'+{int(round(15000 * (u ** 0.75))):,} كم'.replace(',', '٬')
        a = min(1.0, ramp(t, 20.36, 20.6))
        if C.T():
            sp = C.text_sprite(val, size=96, fill=C.GOLD_HI)
            if a < 1:
                sp = sp.copy()
                sp.putalpha(sp.split()[3].point(lambda v: int(v * a)))
            base.alpha_composite(sp, (W - sp.width - 110, 60))
    base = label(base, 'السر مش في القارات', 96, H - 150, t, 16.70, 19.20, size=48)
    return grader(base)


def base_s05(t):
    """the monster in the arch window"""
    lt = t - 22.42
    cam = C.Camera(zoom=1.10 - 0.06 * ease(lt / 6.55), pan=(0, 0))
    src_t = 2.95 + lt * 0.7455
    base = C.grade5(PL['03'].frame(src_t, cam), warmth=0.86, sat=0.60).convert('RGBA')
    for peak in (4.90, 5.35):
        d = src_t - peak
        if -0.55 < d < 0.28:
            base = C.apply_flash(base.convert('RGB'), 0.42 * max(0.0, 1 - abs(d + 0.13) / 0.55) ** 1.5)
            base = base.convert('RGBA')
    return ASH.draw(base, t, density=0.42)


def base_s06(t):
    """«خلّينا نبدأ باللي شافوه الناس» — the arc from America to the whole north-east"""
    lt = t - 28.97
    dur = 4.54
    m = map_obj()
    cam = C.Camera(zoom=1.30 - 0.06 * ease(lt / dur), pan=(10 * (0.5 - lt / dur), 0),
                   src=(MAP_W, MAP_H))
    base = cam.apply(map_base()).convert('RGBA')
    base = SNOW_MID.draw(base, t, density=0.45)
    d = ImageDraw.Draw(base)
    S = lambda ll: cam.to_screen(*m.px(*ll))
    p = S(NE_LL)
    C.pin(base, p[0], p[1], t, 28.97, r=11)
    if lt > 0.4:
        W5.dashed_line(d, [S(ll) for ll in ((-71.0, 42.3), (-73.4, 43.6), (-70.8, 45.2),
                                            (-68.2, 44.6), (-67.0, 46.0))],
                       C.GOLD + (220,), width=4, dash=16, gap=12, upto=ramp(lt, 0.4, 2.6))
    base = focus(base, p[0], p[1], r=260, amount=0.14 * ramp(lt, 0.2, 1.2))
    base = label(base, 'نيو إنجلاند · شرق أمريكا', 96, H - 150, t, 29.30, 33.0, size=46)
    return grader(base)


_DESK = {}
_DESK_SHEET = {}


def _desk(seed, rot, w=1300, h=880):
    """the desk plate: background + aged sheet, built once per (seed, rotation)"""
    key = (seed, rot)
    if key not in _DESK:
        base = archive_sheet(1920, 1080, seed=seed + 100, age=0.9).convert('RGBA')
        base = C.grade5(base.convert('RGB'), warmth=0.55, sat=0.55).convert('RGBA')
        s = _sheet(seed, rot, w, h)
        a = np.asarray(s, np.float32)
        a[..., :3] *= 0.86
        s = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        base.alpha_composite(s, ((1920 - s.width) // 2, (1080 - s.height) // 2))
        _DESK[key] = base
    return _DESK[key]


def _sheet(seed, rot, w=1300, h=880):
    key = (seed, rot, w, h)
    if key not in _DESK_SHEET:
        _DESK_SHEET[key] = archive_sheet(w, h, seed=seed).rotate(rot, expand=True,
                                                                resample=Image.BICUBIC)
    return _DESK_SHEET[key]


def _archive_stage(lt, dur, cam_zoom=1.03, drift=(14, 6), rot=-0.9, seed=7):
    """the desk: a paper sheet in the frame, the camera drifting over it"""
    z = cam_zoom - 0.02 * ease(lt / dur)
    # the sheet is the brightest thing in the frame; on a 0-255 scale it was landing at
    # 240 and reading as a lightbox, so it is held back and let the grade sit on top.
    # Both the paper and the stains are cached: they are identical every frame.
    base = _desk(seed, rot)
    ox = int(drift[0] * (0.5 - lt / dur))
    oy = int(drift[1] * (0.5 - lt / dur))
    if ox or oy:
        base = Image.fromarray(np.roll(np.asarray(base), (oy, ox), axis=(0, 1)))
    base = base.resize((int(1920 * z), int(1080 * z)), Image.BICUBIC)
    ox, oy = int((base.width - 1920) * 0.5), int((base.height - 1080) * 0.5)
    out = base.crop((ox, oy, ox + 1920, oy + 1080)).convert('RGBA')
    return C.grade5(out.convert('RGB'), warmth=0.72, sat=0.62, lift=0.012).convert('RGBA')


LEDGER = ['June 5th — Fair, warm.',
          'June 6th — Wind N.W., very cold.',
          'June 7th — Frost this morning.',
          'June 8th — Cold, and some snow.',
          'June 9th — Ice on the water.']

_DOC_A = {}


def _doc_a_sheet():
    """the ledger page, lettered once and cached: real sentences, real ruling, real ink"""
    if 's' in _DOC_A:
        return _DOC_A['s']
    sheet = archive_sheet(1300, 880, seed=7)
    sheet = ruled_lines(sheet, 96, 1210, 196, 74, 6, alpha=44, wobble=0.0, seed=3)
    # a heading in the same hand, larger
    hand_text(sheet, 96, 96, 'June 1816', size=46, fill=(52, 38, 26))
    hand_text(sheet, 330, 100, '— New England', size=30, fill=(70, 54, 40))
    handwritten_lines(sheet, 96, 196, LEDGER, size=34, dy=74)
    # the shading pen sweeps the June 8th line right to left over 0.6 s at 0:41.5
    _DOC_A['s'] = sheet
    _DOC_A['hl_y'] = 196 + 3 * 74 - 10
    return _DOC_A['s']


def base_s08(t):
    """«سطر بتاريخ 8 يونيو» (L9): the ledger, and the June 8th line shaded as it is read"""
    lt = t - 39.27                      # shot starts at 39.27 (see SHOTS)
    dur = 6.95
    base = _archive_stage(lt, dur, seed=7, cam_zoom=1.00)
    sheet = _doc_a_sheet()
    if lt > 1.0:
        # the shading pen: a translucent yellow wash that sweeps right-to-left
        u = ramp(lt, 2.23, 2.83)
        if u > 0:
            sheet = sheet.copy()
            y = _DOC_A['hl_y']
            x1 = 742
            x0 = int(x1 - (x1 - 82) * u)
            wash = Image.new('RGBA', (max(2, x1 - x0), 38), (255, 220, 80, 112))
            sheet.alpha_composite(wash, (x0, y))
    # slow push from 1.00 to 1.12, tilting toward the shaded line
    z = 1.00 + 0.12 * ease(lt / dur)
    s_img = sheet.rotate(-2.0, expand=True, resample=Image.BICUBIC)
    a = np.asarray(s_img, np.float32)
    a[..., :3] *= 0.92
    s_img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    tw, th = int(1920 * z), int(1080 * z)
    canvas = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
    canvas.alpha_composite(base.resize((tw, th), Image.BICUBIC))
    cx = (tw - s_img.width) // 2
    cy = int((th - s_img.height) // 2 + 40 * ease(lt / dur))   # tilt down to the line
    canvas.alpha_composite(s_img, (cx, cy))
    ox, oy = (tw - 1920) // 2, (th - 1080) // 2
    out = canvas.crop((ox, oy, ox + 1920, oy + 1080)).convert('RGBA')
    return out


def _ch1_card(base, t):
    return base


TEMP_ROWS = [('June 5', '39°F', '52°F'), ('June 6', '34°F', '45°F'),
             ('June 7', '31°F', '44°F'), ('June 8', '30°F', '41°F'),
             ('June 9', '29°F', '40°F'), ('June 10', '33°F', '47°F'),
             ('June 11', '35°F', '49°F'), ('June 12', '32°F', '43°F')]

_DOC_B = {}


def _doc_b_sheet():
    """a temperature table with actual readings, ruled and lettered once"""
    if 's' in _DOC_B:
        return _DOC_B['s']
    sheet = archive_sheet(1240, 900, seed=19)
    d = ImageDraw.Draw(sheet, 'RGBA')
    hand_text(sheet, 70, 60, 'Thermometer — 1816', size=40, fill=(52, 38, 26))
    cols = [(70, 'Date'), (470, 'Morning'), (800, 'Noon')]
    for x, name in cols:
        hand_text(sheet, x, 140, name, size=34, fill=(58, 42, 30))
    d.line([(70, 190), (1170, 190)], fill=(70, 54, 40, 150), width=3)
    for k, row in enumerate(TEMP_ROWS):
        y = 212 + k * 74
        for (x, _), val in zip(cols, row):
            hand_text(sheet, x, y, val, size=32, fill=(48, 34, 24))
        d.line([(70, y + 58), (1170, y + 58)], fill=(90, 74, 58, 46), width=2)
    _DOC_B['s'] = sheet
    return sheet


def base_s09(t):
    """«وفي سجل طقس قديم» (L9): the 8-row readings table — 46.22-51.31"""
    lt = t - 46.22
    dur = 5.09
    base = _archive_stage(lt, dur, seed=19, cam_zoom=1.00, drift=(-6, 4))
    sheet = _doc_b_sheet()
    z = 1.00 + 0.10 * ease(lt / dur)
    s_img = sheet.rotate(-1.4, expand=True, resample=Image.BICUBIC)
    a = np.asarray(s_img, np.float32)
    a[..., :3] *= 0.92
    s_img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    tw, th = int(1920 * z), int(1080 * z)
    canvas = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
    # the desk plate slides with the entry; the sheet slides faster -> parallax
    pe = 1.0 - ease(ramp(lt, 0.0, 0.90))
    canvas.alpha_composite(base.resize((tw, th), Image.BICUBIC), (int(-70 * pe), 0))
    canvas.alpha_composite(s_img, ((tw - s_img.width) // 2 + int(340 * pe),
                                   (th - s_img.height) // 2))
    ox, oy = (tw - 1920) // 2, (th - 1080) // 2
    return canvas.crop((ox, oy, ox + 1920, oy + 1080)).convert('RGBA')


def base_s07(t):
    """«الصقيع رجع وهو المفروض غايب» (L8): frost over New England — 33.51-39.27"""
    lt = t - 33.51
    dur = 5.76
    m = map_obj()
    cam = C.Camera(zoom=1.30 - 0.07 * (0.5 * ease(lt / dur) + 0.5 * (lt / dur)),
                   pan=(-40 + 60 * (lt / dur), -10 + 40 * (lt / dur)), src=(MAP_W, MAP_H))
    base = cam.apply(map_base()).convert('RGBA')
    base = SNOW_MID.draw(base, t, density=0.40)
    d = ImageDraw.Draw(base)
    S = lambda ll: cam.to_screen(*m.px(*ll))
    p = S(NE_LL)
    base = focus(base, p[0], p[1], r=280, amount=0.20 * ramp(lt, 0.2, 1.4))
    for k, (r0, ph) in enumerate(((90, 0.0), (150, 0.55), (210, 1.1))):
        u = ((lt / 2.2) + ph) % 1.0
        rr = r0 * (0.75 + 0.45 * u)
        a = int(190 * (1 - u) * ramp(lt, 0.2 + k * 0.25, 0.9 + k * 0.25))
        if a > 4:
            d.ellipse([p[0] - rr, p[1] - rr * 0.62, p[0] + rr, p[1] + rr * 0.62],
                      outline=(196, 224, 245, a), width=3)
    C.pin(base, p[0], p[1], t, 33.51, r=10)
    base = label(base, 'الصقيع رجع', 96, H - 150, t, 33.70, 38.90, size=52, shadow=True)
    return grader(base)


_DOC_C = {}


def mark_sprite(kind, size=62, ink=None):
    """a ✔ or ✘ drawn as vector strokes.

    U+2714 and U+274C are absent from the Arabic faces, so drawing the characters as text
    produced empty boxes. These are real strokes, anti-aliased at 4x.
    """
    ink = ink or ((94, 122, 62) if kind == 'tick' else (168, 52, 46))
    ss = 4
    w = h = int(size * 1.05)
    big = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    lw = int(size * 0.13 * ss)
    if kind == 'tick':
        pts = [(0.10 * w * ss, 0.56 * h * ss), (0.38 * w * ss, 0.84 * h * ss),
               (0.92 * w * ss, 0.16 * h * ss)]
        d.line(pts, fill=ink + (255,), width=lw, joint='curve')
    else:
        d.line([(0.10 * w * ss, 0.10 * h * ss), (0.90 * w * ss, 0.90 * h * ss)],
               fill=ink + (255,), width=lw)
        d.line([(0.90 * w * ss, 0.10 * h * ss), (0.10 * w * ss, 0.90 * h * ss)],
               fill=ink + (255,), width=lw)
    sp = big.resize((w, h), Image.LANCZOS)
    sh, pad = C.shadow_of(sp, blur=8, off=(3, 5), alpha=90)
    return dict(sprite=sh, box=(pad, pad, pad + w, pad + h),
                card_box=(pad, pad, pad + w, pad + h), pad=pad)


def verdict_card(rows, size=36, seed=11):
    """a card whose marks are strokes, not codepoints: [(text, 'tick'|'cross'), ...]"""
    marks = [mark_sprite(kind, size=int(size * 1.45)) for _, kind in rows]
    sps = [C.text_sprite(t, size, fill=C.INK) for t, _ in rows]
    padx, pady = 34, 20
    gap = 16
    mw = max(m['sprite'].width - 2 * m['pad'] for m in marks)
    tw = max(sp.width for sp in sps)
    w = tw + mw + padx * 2 + 24 + C.ACCENT_W
    lh = max(max(sp.height for sp in sps), mw)
    h = lh * len(rows) + gap * (len(rows) - 1) + pady * 2
    ss = 4
    big = Image.new('RGBA', (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    d.rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], radius=C.CARD_RADIUS * ss,
                        fill=C.PAPER + (255,))
    d.rectangle([w * ss - C.ACCENT_W * ss, 0, w * ss, h * ss], fill=C.ACCENT + (255,))
    sheet = big.resize((w, h), Image.LANCZOS)
    for i, (mk, sp) in enumerate(zip(marks, sps)):
        y = pady + i * (lh + gap)
        # the mark sits on the RIGHT of its line, where an RTL sentence ends
        sheet.alpha_composite(mk['sprite'], (padx - mk['pad'], y + (lh - mk['sprite'].height) // 2))
        sheet.alpha_composite(sp, (padx + mw + 20, y + (lh - sp.height) // 2))
    sh, pad = C.shadow_of(sheet, blur=18, off=(6, 10), alpha=int(255 * 0.45))
    return dict(sprite=sh, box=(pad + padx, pad + pady, pad + padx + sp.width, pad + pady + sp.height),
                card_box=(pad, pad, pad + w, pad + h), pad=pad)


def _fit_sprite(sp, w_max):
    if sp.width > w_max:
        sc = w_max / sp.width
        sp = sp.resize((int(sp.width * sc), int(sp.height * sc)), Image.LANCZOS)
    return sp


def _doc_c_sheet():
    """the season strip: three cells that flip from field green to summer blue on the beat"""
    if 's' in _DOC_C:
        return _DOC_C['s']
    w, h = 1180, 620
    sheet = archive_sheet(w, h, seed=44)
    d = ImageDraw.Draw(sheet, 'RGBA')
    hand_text(sheet, 60, 48, 'الصيف في التقويم — ١٨١٦', size=34, fill=(52, 38, 26),
              font_name='IBMPlexSansArabic-Bold.ttf')
    d.line([(60, 108), (w - 60, 108)], fill=(80, 64, 48, 120), width=3)
    _DOC_C['cells'] = [(60 + k * 360, 150, 320, 400) for k in range(3)]
    _DOC_C['s'] = sheet
    return sheet


_DOC_C_MONTHS = [('يونيو', 0), ('يوليو', 1), ('أغسطس', 2)]


def _doc_c_frame(lt):
    """the strip with its three cells filled to the state they are in at local time lt"""
    sheet = _doc_c_sheet().copy()
    d = ImageDraw.Draw(sheet, 'RGBA')
    for (x, y, cw, ch), (name, k) in zip(_DOC_C['cells'], _DOC_C_MONTHS):
        # each cell flips on its own beat, 0.55 s, green -> blue
        u = ramp(lt, 1.35 + k * 1.10, 1.95 + k * 1.10)
        d.rectangle([x, y, x + cw, y + ch], outline=(92, 74, 58, 150), width=3)
        # the cell interior: the field, then the cold
        col = [int(94 + (159 - 94) * u), int(122 + (183 - 122) * u), int(74 + (201 - 74) * u)]
        d.rectangle([x + 5, y + 5, x + cw - 5, y + ch - 5], fill=tuple(col) + (238,))
        sp = _fit_sprite(C.text_sprite(name, 44, fill=(250, 246, 238)), cw - 24)
        sheet.alpha_composite(sp, (x + (cw - sp.width) // 2, y + ch // 2 - sp.height // 2))
        # a tick under the cell once it has flipped
        if lt >= 1.95 + k * 1.10:
            tx = x + cw // 2
            d.line([(tx - 16, y + ch + 26), (tx - 4, y + ch + 40)], fill=(92, 116, 74, 255), width=5)
            d.line([(tx - 4, y + ch + 40), (tx + 20, y + ch + 6)], fill=(92, 116, 74, 255), width=5)
    return sheet


def base_s10(t):
    """«الصيف ما اختفاش من التقويم» (L12): the season strip — 51.31-59.11"""
    lt = t - 51.31
    dur = 7.80
    base = _archive_stage(lt, dur, seed=31, drift=(6, 8), rot=0.6)
    sheet = _doc_c_frame(lt).rotate(-1.1, expand=True, resample=Image.BICUBIC)
    z = 1.00 + 0.06 * ease(lt / dur)
    tw, th = int(1920 * z), int(1080 * z)
    canvas = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
    canvas.alpha_composite(base.resize((tw, th), Image.BICUBIC))
    canvas.alpha_composite(sheet, ((tw - sheet.width) // 2, (th - sheet.height) // 2 - 30))
    ox, oy = (tw - 1920) // 2, (th - 1080) // 2
    base = canvas.crop((ox, oy, ox + 1920, oy + 1080)).convert('RGBA')
    return base


def base_s11(t):
    """«طيب مين اللي قدر يوصّل الدنيا للدرجة دي؟» (L13): the map — 59.11-64.31"""
    lt = t - 59.11
    dur = 5.20
    m = map_obj()
    cam = C.Camera(zoom=1.22 - 0.10 * (0.4 * ease(lt / dur) + 0.6 * (lt / dur)),
                   pan=(-24 * (0.5 - lt / dur), 12 * (0.5 - lt / dur)), src=(MAP_W, MAP_H))
    base = cam.apply(map_base()).convert('RGBA')
    base = RAIN.draw(base, t, density=0.42)
    d = ImageDraw.Draw(base)
    S = lambda ll: cam.to_screen(*m.px(*ll))
    # the harvest belt, dimming month by month: four contours that fade out of the frame
    # the harvest belt cools band by band: a soft wash that retreats north, not a set of
    # empty rectangles floating on the ocean
    for k, (lat0, lat1) in enumerate(((-6, 16), (16, 34), (34, 50), (50, 62))):
        u = ramp(lt, 0.8 + k * 0.85, 2.4 + k * 0.85)
        if u <= 0:
            continue
        p0, p1 = S((-22, lat0)), S((62, lat1))
        x0, y0 = min(p0[0], p1[0]), min(p0[1], p1[1])
        x1, y1 = max(p0[0], p1[0]), max(p0[1], p1[1])
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        band = ((xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)).astype(np.float32)
        if band.sum() < 100:
            continue
        band = np.asarray(Image.fromarray((band * 255).astype(np.uint8))
                          .filter(ImageFilter.GaussianBlur(26)), np.float32) / 255.0
        a = np.asarray(base.convert('RGB'), np.float32)
        a += (band * 26 * u)[..., None] * np.array([-0.35, -0.05, 0.30], np.float32)
        base = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
        d = ImageDraw.Draw(base)
    base = label(base, 'مين السبب؟', 96, H - 150, t, 59.55, 63.9, size=52, shadow=True)
    return grader(base)


# ---------------------------------------------------------------- the case board
BOARD_T0 = 64.78          # the file drops
BOARD_END = 91.50         # the match cut into the live clip 04


def cork_board():
    """a dark pinboard: cork grain, a top-left key light, an 18 % vignette"""
    key = 'cork'
    if key in _DESK:
        return _DESK[key]
    rng = np.random.default_rng(41)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.zeros((H, W, 3), np.float32)
    base[...] = (74, 56, 40)
    # cork is a warm, fine speckle with a horizontal fibre -- not white noise. The first
    # pass used +-128 noise at full weight and read as television static.
    for block, amp in ((2, 16.0), (4, 11.0), (11, 7.0)):
        n = rng.normal(0, 1, (H // block + 2, W // block + 2)).astype(np.float32)
        n = np.asarray(Image.fromarray(((n * 60) + 128).clip(0, 255).astype(np.uint8))
                       .resize((W, H), Image.BILINEAR), np.float32) - 126
        base += n[..., None] * amp / 60.0
    fibre = rng.normal(0, 1, (H // 3, 3)).astype(np.float32)
    fibre = np.asarray(Image.fromarray(((fibre * 40) + 128).clip(0, 255).astype(np.uint8))
                       .resize((W, H), Image.BILINEAR), np.float32) - 128
    base += fibre[..., None] * 0.09
    light = 1.0 - 0.55 * np.clip(np.sqrt(((xx - W * 0.22) / W) ** 2 +
                                         ((yy - H * 0.16) / H) ** 2) / 0.95, 0, 1)
    base *= light[..., None]
    r = np.sqrt(((xx - W / 2) / (W * 0.5)) ** 2 + ((yy - H / 2) / (H * 0.5)) ** 2)
    base *= (1.0 - 0.18 * np.clip((r / r.max() - 0.32) / 0.68, 0, 1) ** 2)[..., None]
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert('RGBA')
    _DESK[key] = im
    return im


def spring_drop(lt, t_drop, settle=0.55):
    """the offset a thing falls through, with a small overshoot"""
    if lt < t_drop:
        return None
    u = min(1.0, (lt - t_drop) / settle)
    # 1 -> 0 with a bounce: -(1-u)^2 * cos(3.2u)
    k = -(1 - u) ** 2 * math.cos(3.4 * u)
    return k


def paper_card(w, h, kind, rng_seed=0, title=None, lines=(), tilt=0.0, fill=(246, 240, 228)):
    """a card on the board: its own paper, a pin, and real lettering"""
    key = ('card', kind, w, h, title, tuple(lines), tilt, fill)
    if key in _DESK_SHEET:
        return _DESK_SHEET[key]
    card = archive_sheet(w, h, seed=rng_seed + 3)
    # a card is opaque stock: the first pass composited the aged paper at 46 % over the
    # board and every card came out translucent and muddy
    aged = np.asarray(card.convert('RGB'), np.float32)
    solid = np.asarray(Image.new('RGB', (w, h), fill), np.float32)
    card = Image.fromarray(np.clip(aged * 0.34 + solid * 0.66, 0, 255).astype(np.uint8)).convert('RGBA')
    d = ImageDraw.Draw(card, 'RGBA')
    # the printed block at the top of a case card
    ih = int(h * 0.60) if kind == 'island' else int(h * 0.52)
    if kind == 'sun':
        cx, cy = w // 2, int(h * 0.26)
        # a faded sun, printed in ochre: soft halo, disc, and short rays
        halo = Image.new('RGBA', (w, ih), (0, 0, 0, 0))
        dh = ImageDraw.Draw(halo)
        dh.ellipse([cx - 74, cy - 74, cx + 74, cy + 74], fill=(206, 146, 64, 90))
        halo = halo.filter(ImageFilter.GaussianBlur(16))
        card.alpha_composite(halo.convert('RGBA'), (0, 0))
        d = ImageDraw.Draw(card, 'RGBA')
        for k in range(24):
            ang = 2 * math.pi * k / 24
            r1, r2 = 44, 64 + 8 * math.sin(k * 2.1)
            d.line([(cx + r1 * math.cos(ang), cy + r1 * math.sin(ang)),
                    (cx + r2 * math.cos(ang), cy + r2 * math.sin(ang))],
                   fill=(190, 126, 58, 120), width=3)
        d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=(203, 140, 60, 175))
        d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], outline=(150, 96, 40, 120), width=2)
    elif kind == 'volcano':
        d.rectangle([0, 0, w, ih], fill=(38, 36, 34, 255))
        d.polygon([(w * 0.18, ih * 0.92), (w * 0.50, ih * 0.16), (w * 0.82, ih * 0.92)],
                  fill=(14, 14, 16, 255))
        f = C.font('IBMPlexSansArabic-Bold.ttf', 76)
        d.text((w * 0.40, ih * 0.30), '؟', font=f, fill=(255, 255, 255, 230))
        # a small ice core beside it
        d.rectangle([w - 74, ih * 0.58, w - 30, ih * 0.94], fill=(206, 220, 228, 235))
        d.rectangle([w - 74, ih * 0.58, w - 30, ih * 0.62], fill=(150, 176, 190, 235))
    elif kind == 'island':
        fr = _island_frame()
        sc = max(w / fr.width, ih / fr.height)
        fr = fr.resize((int(fr.width * sc + 0.5), int(fr.height * sc + 0.5)), Image.LANCZOS)
        ox = (fr.width - w) // 2
        oy = int((fr.height - ih) * 0.42)
        fr = fr.crop((ox, oy, ox + w, oy + ih))
        if fr.mode != 'RGBA':
            fr = fr.convert('RGBA')
        card.paste(fr.convert('RGB'), (0, 0))
    else:
        d.rectangle([0, 0, w, ih], fill=(44, 40, 36, 255))

    ty = ih + 16
    if title:
        sp = C.text_sprite(title, size=30, fill=(30, 24, 20))
        card.alpha_composite(sp, ((w - sp.width) // 2, ty))
        ty += sp.height + 6
    for line in lines:
        sp = C.text_sprite(line, size=24, fill=(52, 44, 36))
        if sp.width > w - 20:
            sc = (w - 20) / sp.width
            sp = sp.resize((int(sp.width * sc), int(sp.height * sc)), Image.LANCZOS)
        card.alpha_composite(sp, ((w - sp.width) // 2, ty))
        ty += sp.height + 4
    d = ImageDraw.Draw(card, 'RGBA')
    d.rectangle([0, 0, w - 1, h - 1], outline=(120, 104, 88, 160), width=2)
    out = card.rotate(tilt, expand=True, resample=Image.BICUBIC)
    # the centre of the CARD inside the rotated (expanded) sprite: the pin goes here, and
    # the top edge of the card is card_c[1] - h/2 from it
    card_c = (out.width / 2.0, out.height / 2.0)
    _DESK_SHEET[key] = (out, card_c)
    return out, card_c


_ISL = {}


def _island_frame():
    """a frozen frame of clip 04: the subject of the third card, and the match cut's target"""
    if 'f' not in _ISL:
        p = PL['04']
        im = p.frame(0.20 + 2.2, None).convert('RGB')
        _ISL['f'] = im
    return _ISL['f']


def draw_pin(im, x, y, t, t_in, r=9, shadow=True):
    """a pin head: 18 px, #C8302A, a white highlight up-left, a soft shadow"""
    u = ramp(t, t_in, t_in + 0.22)
    if u <= 0:
        return im
    sc = 0.55 + 0.45 * (1 - (1 - u) ** 3)
    rr = r * sc
    layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if shadow:
        d.ellipse([x - rr + 2, y - rr + 7, x + rr + 2, y + rr + 7], fill=(0, 0, 0, 90))
        layer = layer.filter(ImageFilter.GaussianBlur(3))
        im.alpha_composite(layer)
        layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
    d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(200, 48, 42, 255))
    d.ellipse([x - rr * 0.42, y - rr * 0.55, x + rr * 0.10, y - rr * 0.10],
              fill=(255, 236, 230, 210))
    im.alpha_composite(layer)
    return im


def thread(im, p0, p1, t, t_in, dur=0.7, sag=26, colour=(179, 38, 30)):
    """the red thread between two pins, drawn as a slack bezier over `dur`"""
    u = ramp(t, t_in, t_in + dur)
    if u <= 0:
        return im
    layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pts = []
    steps = 40
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + sag
    for k in range(steps + 1):
        a = k / steps
        bx = (1 - a) ** 2 * p0[0] + 2 * (1 - a) * a * mx + a ** 2 * p1[0]
        by = (1 - a) ** 2 * p0[1] + 2 * (1 - a) * a * my + a ** 2 * p1[1]
        pts.append((bx, by))
    n = max(2, int(len(pts) * u))
    d.line(pts[:n], fill=colour + (235,), width=3, joint='curve')
    im.alpha_composite(layer)
    return im


# the three suspect cards: 300x360, laid out on the 1920x1080 board
_CARD_POS = dict(c1=(420, 446), c2=(960, 432), c3=(1500, 446))
CARD_W, CARD_H = 300, 360


def base_s12(t):
    """the case board: a file drops, opens, and three suspects get pinned"""
    lt = t - 64.31
    base = Image.fromarray(np.roll(np.asarray(cork_board()), (0, int(-3 * ease(lt / 7.61))),
                                   axis=1))
    base = base.convert('RGBA')
    d = ImageDraw.Draw(base)

    # 1) the file drops onto the board with a spring landing
    k = spring_drop(lt, 0.47, 0.55)
    if k is not None:
        fw, fh = 620, 440
        if 'file' not in _DESK_SHEET:
            card = archive_sheet(fw, fh, seed=61)
            aged = np.asarray(card.convert('RGB'), np.float32)
            solid = np.asarray(Image.new('RGB', (fw, fh), (232, 222, 202)), np.float32)
            card = Image.fromarray(np.clip(aged * 0.3 + solid * 0.7, 0, 255)
                                   .astype(np.uint8)).convert('RGBA')
            d2 = ImageDraw.Draw(card, 'RGBA')
            d2.rectangle([6, 6, fw - 6, fh - 6], outline=(120, 104, 88, 170), width=3)
            stamp = C.text_sprite('ملف تحقيق — قضية ١٨١٦', size=34, fill=(150, 34, 30))
            stamp.rotate(-8, expand=True, resample=Image.BICUBIC)
            stamp = C.text_sprite('ملف تحقيق — قضية ١٨١٦', size=34, fill=(150, 34, 30))
            stamp = stamp.rotate(-7, expand=True, resample=Image.BICUBIC)
            card.alpha_composite(stamp, (38, 58))
            # a folder tab on the top edge and a typed case form under the stamp
            d2 = ImageDraw.Draw(card, 'RGBA')
            d2.rectangle([40, -2, 250, 26], fill=(214, 200, 176, 255))
            d2.rectangle([40, -2, 250, 26], outline=(140, 122, 102, 190), width=2)
            for i, (lab, val) in enumerate((('التاريخ', '١٨١٦'), ('المكان', '—'))):
                yy = 160 + i * 62
                sp = C.text_sprite(lab, size=26, fill=(96, 80, 64))
                card.alpha_composite(sp, (fw - 50 - sp.width, yy))
                v = C.text_sprite(val, size=28, fill=(48, 40, 32))
                card.alpha_composite(v, (fw - 50 - sp.width - v.width - 24, yy))
                d2.line([(60, yy + 40), (fw - 50 - sp.width - v.width - 40, yy + 40)],
                        fill=(150, 134, 116, 150), width=2)
            tab = C.text_sprite('١٨١٦', size=50, fill=(60, 48, 38))
            card.alpha_composite(tab, (fw - tab.width - 40, fh - tab.height - 22))
            _DESK_SHEET['file'] = card
        fi = _DESK_SHEET['file']
        fx = (W - fw) // 2
        # bottom centre: the suspect cards own the top of the board. It leaves downward
        # after the graph has been read, so the board is clear for the three cards.
        fy = int(562 + 440 * k + 206 * ease(ramp(lt, 9.3, 10.3)))
        if fy < H - 24:
            base.alpha_composite(fi, (fx, fy))

    # 2) the file opens and a temperature graph slides out of it
    if 2.82 <= lt:
        g = ramp(lt, 2.82, 4.2)
        gw, gh = 620, 250
        if 'graph' not in _DESK_SHEET:
            gs = archive_sheet(gw, gh, seed=73)
            dg = ImageDraw.Draw(gs, 'RGBA')
            hand_text(gs, 26, 16, 'نهاية العصر الجليدي الصغير', size=36, fill=(52, 38, 26),
                      font_name='IBMPlexSansArabic-Bold.ttf')
            # a slow oscillation that breaks downward after 1815: the curve the narrator
            # is describing, not a decorative wave
            pts = [(30 + i * (gw - 60) / 34,
                    min(232, 104 + 46 * math.sin(i * 0.30) + 1.6 * i + 6 * math.sin(i * 0.9)))
                   for i in range(35)]
            _DESK_SHEET['graph'] = (gs, pts)
        gs, pts = _DESK_SHEET['graph']
        gg = gs.copy()
        dgg = ImageDraw.Draw(gg, 'RGBA')
        n = max(2, int(len(pts) * ramp(lt, 3.35, 4.55)))
        dgg.line(pts[:n], fill=(58, 50, 42, 235), width=5, joint='curve')
        # the sheet sits in the clear band the cards will later claim, then clears out
        # upward so card 1 can enter without ever sharing the frame with it
        gy = 640 - 400 * g - 780 * ramp(lt, 9.15, 9.95)
        if gy > -gh:
            sh = Image.new('RGBA', gg.size, (0, 0, 0, 0))
            ImageDraw.Draw(sh).rectangle([0, 0, gw, gh], fill=(0, 0, 0, 110))
            base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)),
                                 (int(W / 2 - gw / 2) + 5, int(gy) + 12))
            base.alpha_composite(gg, (int(W / 2 - gw / 2), int(gy)))

    # 3) three suspect cards, pinned
    cards = [('c1', 10.19, 'sun', 'المشتبه الأول',
              ['فترة دالتون', 'نشاط شمسي منخفض'], 3),
             ('c2', 15.99, 'volcano', 'المشتبه الثاني',
              ['ثوران مجهول — حوالي ١٨٠٩', 'المكان: غير معروف'], -2),
             ('c3', 25.39, 'island', 'المشتبه الثالث',
              ['جزيرة سومباوا', 'إبريل ١٨١٥'], 2)]

    placed = {}
    for name, t_at, kind, title, lines, tilt in cards:
        if lt < t_at:
            continue
        kk = spring_drop(lt, t_at, 0.5)
        card, cc = paper_card(CARD_W, CARD_H, kind, rng_seed=hash(name) % 50,
                              title=title, lines=lines, tilt=tilt)
        x, y = _CARD_POS[name]
        hover = int(-90 * kk)
        dim = 1.0
        if name != 'c3' and lt >= 25.39:
            dim = 1.0 - 0.70 * ramp(lt, 25.39, 26.09)
        im2 = card
        if dim < 1.0:
            im2 = card.copy()
            a = im2.split()[3].point(lambda v: int(v * dim))
            im2.putalpha(a)
        ox_ = int(x - cc[0])
        oy_ = int(y - cc[1] + hover)
        base.alpha_composite(im2, (ox_, oy_))
        # the pin, and therefore the thread's anchor: 10 px inside the card's top edge,
        # measured on the card, so a 2-3 deg tilt cannot leave the pin floating on cork
        placed[name] = (ox_ + cc[0] + CARD_W * 0.5 * math.tan(math.radians(tilt)) * 0.0,
                        oy_ + cc[1] - CARD_H / 2 + 12)

    # the card 3 glow, then everything else dims
    if lt >= 25.39 and 'c3' in placed:
        cx, cy = placed['c3']
        base = focus(base, cx, cy, r=260, amount=0.34 * ramp(lt, 25.39, 26.39))

    # 4) red thread: pin 1 -> pin 2, then 2 -> 3
    if 'c1' in placed and 'c2' in placed:
        base = thread(base, placed['c1'], placed['c2'], lt, 18.15, 0.7, sag=34)
    if 'c2' in placed and 'c3' in placed:
        base = thread(base, placed['c2'], placed['c3'], lt, 26.25, 0.7, sag=30)

    # 5) the pins go in last so they sit on top of every thread
    for name, (x, y) in placed.items():
        t_at = {'c1': 10.19, 'c2': 15.99, 'c3': 25.39}[name]
        base = draw_pin(base, x, y, lt, t_at, r=9)

    # 6) the match cut: push into card 3 until its frame is the whole screen
    if lt >= 26.29:
        # push in on card 3's photograph, then hand off to the live clip of the same
        # subject on a hard cut. A 7.5x push simply enlarged a 330 px crop and every
        # frame went to mush -- 2.4x keeps the push legible and lets the plate land sharp.
        u = ramp(lt, 26.29, 27.19)
        c3 = _CARD_POS['c3']
        cx, cy = c3[0], c3[1] - CARD_H // 2 + int(CARD_H * 0.30)
        z = 1.0 + 1.42 * (u ** 2)
        nw, nh = int(W * z), int(H * z)
        big = base.resize((nw, nh), Image.BICUBIC)
        ox = int(np.clip(cx * z - W / 2, 0, nw - W))
        oy = int(np.clip(cy * z - H / 2, 0, nh - H))
        base = big.crop((ox, oy, ox + W, oy + H)).convert('RGBA')
        if u > 0.55:
            base = C.zoom_blur(base.convert('RGB'), (u - 0.62) * 1.9).convert('RGBA')

    return C.grade5(base.convert('RGB'), warmth=0.82, sat=0.78).convert('RGBA')


def base_s13(t):
    """the first suspect: a dim sun, the Dalton minimum"""
    lt = t - 71.92
    dur = 7.33
    m = map_obj()
    cam = C.Camera(zoom=1.26 - 0.06 * (0.5 * ease(lt / dur) + 0.5 * (lt / dur)),
                   pan=(20 - 40 * (lt / dur), 0), src=(MAP_W, MAP_H))
    base = cam.apply(map_base()).convert('RGBA')
    d = ImageDraw.Draw(base)
    S = lambda ll: cam.to_screen(*m.px(*ll))
    # the sun is placed where the chapter has been standing for a minute -- over Europe --
    # and it loses its own light while we watch
    p = S(EU_LL)
    u = ramp(lt, 0.4, 5.6)
    base = focus(base, p[0], p[1], r=300, amount=0.42 * (1 - 0.75 * u))
    for k, (r0, al) in enumerate(((150, 210), (108, 160), (66, 130))):
        a = int(al * (1 - 0.62 * u) * ramp(lt, 0.3 + 0.25 * k, 1.1 + 0.25 * k))
        if a > 4:
            d.ellipse([p[0] - r0, p[1] - r0, p[0] + r0, p[1] + r0],
                      outline=(255, 214, 140, a), width=3)
    base = MOTE.draw(base, t, density=0.5)
    return grader(base)


def base_s14(t):
    """the second suspect: an eruption nobody can place"""
    lt = t - 79.25
    dur = 9.64
    m = map_obj()
    cam = C.Camera(zoom=1.20 - 0.06 * (0.55 * ease(lt / dur) + 0.45 * (lt / dur)),
                   pan=(0, 14 * (0.5 - lt / dur)), src=(MAP_W, MAP_H))
    base = cam.apply(map_base()).convert('RGBA')
    base = ASH.draw(base, t, density=0.45)
    d = ImageDraw.Draw(base)
    S = lambda ll: cam.to_screen(*m.px(*ll))
    # a grey smear with no centre: the 1809 eruption's location is unknown, and the graphic
    # says so by breathing instead of resolving
    for k, (lon, lat) in enumerate(((-78, 4), (-40, -6), (10, 6), (58, 12), (100, 2))):
        p = S((lon, lat))
        u = ((lt / 3.1) + k * 0.21) % 1.0
        rr = 54 + 130 * u
        a = int(165 * (1 - u) * ramp(lt, 0.6 + 0.3 * k, 1.6 + 0.3 * k))
        if a > 4:
            d.ellipse([p[0] - rr, p[1] - rr * 0.7, p[0] + rr, p[1] + rr * 0.7],
                      outline=(216, 220, 226, a), width=3)
        if k == 2:
            base = focus(base, p[0], p[1], r=340, amount=0.10 * ramp(lt, 0.6, 2.4))
    return grader(base)


def base_s15(t):
    """Sumbawa: a volcano in a grey-blue sea"""
    lt = t - 88.89
    cam = C.Camera(zoom=1.06 - 0.03 * ease(lt / 7.22), pan=(6 * (0.5 - lt / 7.22), 0))
    base = C.grade5(PL['04'].frame(0.20 + lt, cam), warmth=0.86, sat=0.68).convert('RGBA')
    return ASH.draw(base, t, density=0.55)


def base_s16(t):
    """the eruption: the chapter's loudest frame"""
    lt = t - 96.11
    cam = C.Camera(zoom=1.12 - 0.09 * ease(lt / 6.49), pan=(0, 6 * (0.5 - lt / 6.49)))
    base = C.grade5(PL['05'].frame(1.90 + lt * 0.870, cam), warmth=0.80, sat=0.74).convert('RGBA')
    for peak in (0.9, 3.4, 5.1):
        d = lt - peak
        if -0.45 < d < 0.30:
            amt = max(0.0, 1.0 - abs(d + 0.10) / 0.45) ** 1.4
            base = C.apply_flash(base.convert('RGB'), 0.30 * amt).convert('RGBA')
    base = ASH_HVY.draw(base, t, density=0.85)
    return EMBERS.draw(base, t, density=0.55, blur=1.2)


def base_s17(t):
    """«والأقوى ما كانش في أوروبا خالص» — the frame empties eastward"""
    lt = t - 102.60
    dur = 6.88
    u = ease(lt / dur)
    m = map_obj()
    # the push is aimed at Sumbawa: the pan is derived from where the island sits on the
    # plate, so the chapter can close on it instead of on the frame edge
    fx, fy = m.px(*SU_LL)
    cam = C.Camera(zoom=1.58 - 0.50 * u, pan=((fx - MAP_W / 2) * 0.55 * u,
                                              (fy - MAP_H / 2) * 0.55 * u), src=(MAP_W, MAP_H))
    base = cam.apply(map_base()).convert('RGBA')
    base = ASH.draw(base, t, density=0.35)
    d = ImageDraw.Draw(base)
    S = lambda ll: cam.to_screen(*m.px(*ll))
    # only Eurasia stays lit; the Americas fall into the vignette as we push east
    p = S(SU_LL)
    u2 = ramp(lt, 0.8, 4.2)
    if u2 > 0:
        rr = 120 + 260 * u2
        a = int(180 * min(1.0, u2 * 1.6))
        d.ellipse([p[0] - rr, p[1] - rr * 0.8, p[0] + rr, p[1] + rr * 0.8],
                  outline=(255, 190, 120, a), width=4)
    C.pin(base, p[0], p[1], t, 102.60, r=12)
    base = focus(base, p[0], p[1], r=320, amount=0.26 * u2)
    base = label(base, 'الأقوى كان هنا', 96, H - 150, t, 103.4, 109.1, size=50)
    return grader(base)


SHOT_FNS = {
    'S01_house': base_s01, 'S02_farmers': base_s02, 'S03_europe': base_s03,
    'S04_map': base_s04, 'S05_monster': base_s05,
    'S06_map_arc': base_s06, 'S07_frost': base_s07, 'S08_ledger': base_s08,
    'S09_table': base_s09, 'S10_strip': base_s10, 'S11_question': base_s11,
    'S12_board': base_s12,
    'S13_sun': base_s13, 'S14_1809': base_s14, 'S15_sumbawa': base_s15,
    'S16_eruption': base_s16, 'S17_reckoning': base_s17,
}


# ---------------------------------------------------------------- the card plan
# (name, slot, cue, hold, text) -- the layout queue retires one card before the next
CARDS = [
    ('stamp_1816', 'A', 2.10, 1.40, 'stamp'),
    ('place_usa', 'A', 5.05, 2.90, 'فلاحين · أمريكا'),
    ('place_eu', 'A', 9.97, 2.10, 'أوروبا'),
    ('archive_1816', 'C', 39.60, 3.20, 'سجل طقس نيو إنجلاند — ٨ يونيو ١٨١٦: برد وشوية تلج'),
    ('europe_table', 'C', 46.60, 2.60, 'أوروبا وأمريكا — مطر وبرد طالوا الصيف كله'),
    ('crops', 'C', 12.90, 2.40, 'المحاصيل ما لحقتش تكبر'),
    ('map_km', 'C', 20.36, 1.60, '+15٬000 كم'),
    ('summer', 'C', 52.60, 3.90, 'VERDICT:summer'),
    ('dalton', 'A', 74.59, 2.40, 'المشتبه 1 · شمس ضعيفة'),
    ('burst1809', 'A', 81.20, 2.30, 'المشتبه 2 · ثوران مجهول'),
    ('sumbawa_tag', 'A', 97.50, 4.60, 'ثلاثة مشتبه بهم… والدراسات بتشاور على واحد'),
    ('dalt_band', 'C', 74.59, 1.00, None),
]

def build_tags():
    """build the tag sprite queue. Called at import, and again by the text-presence test so
    it can rebuild every card with the ink blanked out."""
    global TAGS, QUEUE
    TAGS = []
    for name, slot, cue, hold, text in CARDS:
        if text is None:
            continue
        if text == 'stamp':
            sprite = C.stamp_sprite('يونيو 1816', size=86)
        elif text.startswith('VERDICT:'):
            sprite = verdict_card([('الصيف موجود في التقويم', 'tick'),
                                   ('مختفي من الحقول', 'cross')],
                                  size=36, seed=abs(hash(name)) % 97 + 3)
        elif name == 'sumbawa_tag':
            # the gold card for the payoff line: same size as the case-card lettering it
            # sits beside, and drawn plain, so it clears the board's ink on its entry
            sprite = C.paper_tag(text, size=34, padx=30, pady=18,
                                 seed=abs(hash(name)) % 97 + 3)
        else:
            sprite = C.paper_tag(text, size=46 if len(text) > 18 else 52,
                                 seed=abs(hash(name)) % 97 + 3)
        TAGS.append(TG.Tag(name, slot, cue, hold, sprite))
    QUEUE = TG.TagLayoutQueue(TAGS, T_END).retime()
    return QUEUE


build_tags()
DISCLAIMER = C.floating_line('مشاهد مُعاد تخيّلها', size=38, alpha=0.65)
DISC_IN, DISC_OUT_0, DISC_OUT_1 = 0.60, 1.72, 2.05


# ---------------------------------------------------------------- transitions
def _both(t, shot, fn):
    return fn(t)


def blend_frame(i, t):
    """the finished base frame at time t, including the transition at this boundary"""
    idx = None
    for k, s in enumerate(SHOTS):
        if s[2] <= t < s[3]:
            idx = k
            break
    if idx is None:
        idx = len(SHOTS) - 1
    cur = SHOTS[idx]
    a_fn = SHOT_FNS[cur[0]]
    base = a_fn(t)

    if idx > 0:
        prev = SHOTS[idx - 1]
        tw = trans_window(prev, cur, t)
        if tw:
            kind, _, hw = tw
            tb = cur[2]
            if tb - hw / 2 <= t < tb + hw / 2:
                k = ramp(t, tb - hw / 2, tb + hw / 2)
                p_fn = SHOT_FNS[prev[0]]
                if kind == 'dissolve':
                    base = C.dissolve(p_fn(t).convert('RGB'), a_fn(t).convert('RGB'),
                                      k).convert('RGBA')
                else:
                    # into a map: the outgoing plate blurs its zoom while the map resolves
                    if cur[1] == 'map':
                        kk = 1.0 - k
                        base = C.zoom_blur(a_fn(t).convert('RGB'), kk * 0.55).convert('RGBA')
                        if kk > 0.55:
                            base = C.dissolve(base, C.zoom_blur(p_fn(t).convert('RGB'),
                                                                (kk - 0.55) * 0.9).convert('RGB'),
                                              (kk - 0.55) / 0.45).convert('RGBA')
                    else:
                        kk = k
                        base = C.zoom_blur(p_fn(t).convert('RGB'), kk * 0.55).convert('RGBA')
                        if kk > 0.55:
                            base = C.dissolve(base, a_fn(t).convert('RGB'),
                                              (kk - 0.55) / 0.45).convert('RGBA')
    return base.convert('RGBA')


def frame_at(t):
    """one finished frame at time t. A pure function of t."""
    i = int(round(t * 30))
    base = blend_frame(i, t)

    # 1) the tag queue: the ONLY way a card reaches the screen
    if C.T():
        base = QUEUE.render(base, t)

    # 2) the corner watermark is present for the whole chapter after the button
    if 28.97 <= t < 64.31:
        a = min(1.0, ramp(t, 28.97, 29.42))
        lg, _ = C.logo_scaled(300)
        L = np.asarray(base.convert('L'), np.float32)
        zy = (56, 56 + 210)
        left = float(L[zy[0]:zy[1], 40:40 + lg.width].mean())
        right = float(L[zy[0]:zy[1], W - 40 - lg.width:W - 40].mean())
        x = 40 if left <= right else W - lg.width - 40
        C.place_logo(base, x, 56, width=300, alpha=a)
    if t >= 64.31:
        a = min(1.0, ramp(t, 64.31, 64.76))
        C.place_logo(base, W - 340, 56, width=300, alpha=a)

    # 3) the disclaimer goes on before anything can share its corner, and leaves first
    if C.T() and DISC_IN <= t < DISC_OUT_1:
        a_ = ramp(t, DISC_IN, DISC_IN + 0.45)
        if t > DISC_OUT_0:
            a_ *= max(0.0, (DISC_OUT_1 - t) / (DISC_OUT_1 - DISC_OUT_0))
        sp = DISCLAIMER['sprite'].copy()
        sp.putalpha(sp.split()[3].point(lambda v: int(v * a_)))
        base.alpha_composite(sp, (96 - DISCLAIMER['pad'], 86 - DISCLAIMER['pad']))

    out = C.finish(base.convert('RGB'), i % 240)
    if t < 0.18:
        out = C.fade_to_black(out, t / 0.18)
    if t > T_END - 0.55:
        out = C.fade_to_black(out, max(0.0, (T_END - t) / 0.55))
    return out


# ---------------------------------------------------------------- events
EVENTS = [
    # a beat every 1.4-2.0 s. These are the points the picture actually changes --
    # a card, a pin, a ring, a flash, a light -- not a decorative marker per shot.
    dict(t=1.20, what='snow arrives over the lake', sfx=None, shot='S01'),
    dict(t=2.10, what='stamp «يونيو 1816»', sfx='stamp', shot='S01'),
    dict(t=4.05, what='snow brightens as the house falls away', sfx=None, shot='S01'),
    dict(t=4.35, what='snow drives in on فلاحين', sfx='sleet', shot='S02'),
    dict(t=5.05, what='tag فلاحين · أمريكا enters', sfx='paper_in', shot='S02'),
    dict(t=6.25, what='thermometer needle drops', sfx='needle', shot='S02'),
    dict(t=7.43, what='snow thickens on والتلج', sfx='sleet', shot='S02'),
    dict(t=8.65, what='snow reaches full weight on بينزل', sfx='sleet', shot='S02'),
    dict(t=9.97, what='tag أوروبا enters', sfx='paper_in', shot='S03'),
    dict(t=11.52, what='rain at full weight on مطر', sfx='water', shot='S03'),
    dict(t=12.90, what='tag المحاصيل enters', sfx='paper_in', shot='S03'),
    dict(t=14.78, what='crop strip pinned on تكبر', sfx='pin', shot='S03'),
    dict(t=16.53, what='New England pinned', sfx='pin', shot='S04'),
    dict(t=17.35, what='thread leg 1 draws', sfx='thread_draw', shot='S04'),
    dict(t=19.04, what='thread lands on Europe', sfx='pin', shot='S04'),
    dict(t=19.72, what='thread turns for Sumbawa', sfx='thread_draw', shot='S04'),
    dict(t=20.36, what='+15,000 km counter runs', sfx=None, shot='S04'),
    dict(t=21.02, what='Sumbawa pinned', sfx='pin', shot='S04'),
    dict(t=22.42, what='brand sting: wordmark writes on', sfx='sting', shot='S05'),
    dict(t=23.60, what='plate lightning across the window', sfx='thunder', shot='S05'),
    dict(t=24.70, what='the silhouette steps into the window light', sfx=None, shot='S05'),
    dict(t=25.75, what='tag أشهر وحش في الأدب enters', sfx='paper_in', shot='S05'),
    dict(t=27.24, what='ash thickens on وحش', sfx=None, shot='S05'),
    dict(t=28.97, what='back to the farmers, corner wordmark', sfx='sleet', shot='S06'),
    # 0:29-1:04, re-cut to the narration lines (L7-L13). One event every 1.4-2.0 s.
    dict(t=30.20, what='«خلّينا نبدأ باللي شافوه الناس»: the arc opens', sfx='sleet', shot='S06'),
    dict(t=31.80, what='New England pinned on the arc', sfx='pin', shot='S06'),
    dict(t=33.10, what='the frost band spreads south', sfx=None, shot='S06'),
    dict(t=33.70, what='L8: tag الصقيع رجع', sfx='paper_in', shot='S07'),
    dict(t=35.10, what='frost rings pulse over New England', sfx='sleet', shot='S07'),
    dict(t=36.40, what='the field layer greys out', sfx=None, shot='S07'),
    dict(t=37.70, what='frost reaches the coast', sfx=None, shot='S07'),
    dict(t=39.30, what='hard cut: the ledger on the desk', sfx='paper_in', shot='S08'),
    dict(t=40.60, what='the camera pushes toward the 8 June line', sfx=None, shot='S08'),
    dict(t=41.50, what='the yellow pen sweeps the June 8th line', sfx='thread_draw', shot='S08'),
    dict(t=43.00, what='the shaded line holds', sfx=None, shot='S08'),
    dict(t=44.40, what='the card سجل طقس نيو إنجلاند is read', sfx=None, shot='S08'),
    dict(t=45.60, what='the page settles', sfx=None, shot='S08'),
    dict(t=46.30, what='L10: the readings table slides in from the right', sfx='paper_in', shot='S09'),
    dict(t=47.60, what='the columns line up under parallax', sfx=None, shot='S09'),
    dict(t=48.90, what='the 30F morning reading lands', sfx=None, shot='S09'),
    dict(t=50.20, what='the table settles, card أوروبا وأمريكا', sfx=None, shot='S09'),
    dict(t=51.40, what='L11: the season strip, first cell flips', sfx='paper_in', shot='S10'),
    dict(t=52.70, what='يونيو turns cold', sfx=None, shot='S10'),
    dict(t=53.80, what='يوليو turns cold', sfx=None, shot='S10'),
    dict(t=54.90, what='أغسطس turns cold', sfx=None, shot='S10'),
    dict(t=56.10, what='L12: the verdict card: present on the calendar, gone from the fields', sfx='paper_in', shot='S10'),
    dict(t=57.60, what='the strip holds under the verdict', sfx=None, shot='S10'),
    dict(t=59.15, what='L13: cut back to the map: who could do this?', sfx=None, shot='S11'),
    dict(t=60.60, what='the harvest belt cools northward', sfx=None, shot='S11'),
    dict(t=62.00, what='rain crosses Europe', sfx='water', shot='S11'),
    dict(t=63.40, what='the question holds', sfx=None, shot='S11'),
    # 1:04.78 the case board: the file, the sheet, three pins, two threads
    dict(t=64.78, what='the file drops onto the board', sfx='paper_in', shot='S12'),
    dict(t=65.60, what='the file lands with a paper thud', sfx='stamp', shot='S12'),
    dict(t=67.60, what='the file opens: the temperature sheet rises', sfx='paper_out', shot='S12'),
    dict(t=70.40, what='the curve draws across the sheet', sfx='thread_draw', shot='S12'),
    dict(t=72.20, what='the curve breaks downward after 1815', sfx=None, shot='S12'),
    dict(t=73.40, what='the sheet settles: نهاية العصر الجليدي الصغير', sfx=None, shot='S12'),
    dict(t=74.50, what='suspect 1 pinned: فترة دالتون', sfx='pin', shot='S12'),
    dict(t=75.50, what='the paper settles under the pin', sfx=None, shot='S12'),
    dict(t=76.60, what='the faded sun disc prints', sfx=None, shot='S12'),
    dict(t=77.70, what='the case file slides down out of the way', sfx=None, shot='S12'),
    dict(t=78.90, what='suspect 1 settles', sfx=None, shot='S12'),
    dict(t=80.30, what='suspect 2 pinned: ثوران مجهول', sfx='pin', shot='S12'),
    dict(t=82.20, what='the volcano triangle and the question mark', sfx=None, shot='S12'),
    dict(t=84.00, what='the ice core drops in beside it', sfx=None, shot='S12'),
    dict(t=85.60, what='the first red thread draws pin to pin', sfx='thread_draw', shot='S12'),
    dict(t=87.40, what='the thread goes slack', sfx=None, shot='S12'),
    dict(t=88.30, what='the board is still: two suspects, one thread', sfx=None, shot='S12'),
    dict(t=89.70, what='suspect 3 pinned: جزيرة سومباوا, إبريل 1815', sfx='pin', shot='S12'),
    dict(t=91.00, what='the second thread draws to Sumbawa', sfx='thread_draw', shot='S12'),
    dict(t=64.80, what='the file opens: first pin', sfx='pin', shot='S12'),
    dict(t=66.40, what='second pin', sfx='pin', shot='S12'),
    dict(t=68.00, what='third pin', sfx='pin', shot='S12'),
    dict(t=69.60, what='the case is open: three suspects', sfx=None, shot='S12'),
    dict(t=92.90, what='push-in on the third card begins', sfx=None, shot='S12'),
    dict(t=93.60, what='zoom-blur into the photograph', sfx=None, shot='S12'),
    dict(t=94.30, what='match cut: the live island, first birds', sfx='sleet', shot='S15'),
    dict(t=96.11, what='the eruption', sfx='sting', shot='S16'),
    dict(t=97.60, what='L21: three suspects, the studies point at one', sfx='paper_in', shot='S16'),
    dict(t=99.40, what='lava and lightning', sfx='thunder', shot='S16'),
    dict(t=101.00, what='the column leans east', sfx='sleet', shot='S16'),
    dict(t=102.60, what='hard cut: the frame empties east', sfx=None, shot='S17'),
    dict(t=104.10, what='the map slides east', sfx='thread_draw', shot='S17'),
    dict(t=105.80, what='the ring closes on Sumbawa', sfx=None, shot='S17'),
    dict(t=107.50, what='the strongest was not in Europe', sfx=None, shot='S17'),
    dict(t=108.90, what='fade on the answer', sfx=None, shot='S17'),
]
EVENTS.sort(key=lambda e: e['t'])


def levels():
    """three moving layers in every shot, reported so QA can check it not trust it"""
    return {
        'S01_house': ['plate 09 + camera', 'snow mid', 'grade drift'],
        'S02_farmers': ['plate 01 + push', 'snow mid', 'snow fg'],
        'S03_europe': ['plate 02 + push', 'rain', 'snow fg'],
        'S04_map': ['map plate + drift', 'route + pins', 'ash drift'],
        'S05_monster': ['plate 03 + camera', 'lightning flash', 'ash drift'],
        'S06_map_arc': ['map plate + push', 'pin + route', 'snow mid'],
        'S07_frost': ['map plate + drift', 'frost rings', 'snow mid'],
        'S08_ledger': ['paper sheet + drift', 'hand lettering', 'yellow pen'],
        'S09_table': ['paper sheet + parallax entry', 'readings', 'ruling'],
        'S10_strip': ['paper sheet + drift', 'season cells', 'ticks'],
        'S11_question': ['map plate + push', 'harvest contours', 'rain'],
        'S12_board': ['cork board + drift', 'file, sheet, cards', 'pins + thread'],
        'S15_sumbawa': ['plate 04 + push', 'ash drift', 'plume'],
        'S16_eruption': ['plate 05 + push', 'ash heavy', 'embers'],
        'S17_reckoning': ['map plate + push', 'ring + pin', 'ash drift'],
    }
