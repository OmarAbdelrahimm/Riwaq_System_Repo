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
from PIL import Image, ImageDraw

from eng5 import core5 as C
from eng5 import tags5 as TG
from eng5 import world5 as W5

W, H = C.W, C.H

# ---------------------------------------------------------------- plates
# every clip is 24 fps and the timeline is 30, so a plate steps 0.8 files per frame
PL = {k: C.Plate(k, src_fps=24.0) for k in
      ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14')}

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
    ('S01_house',     '09',   0.00,   4.35, 0.00, 1.0000),
    ('S02_farmers',   '01',   4.35,   9.97, 0.00, 1.0000),
    ('S03_europe',    '02',   9.97,  15.96, 0.00, 1.0000),
    ('S04_map',       'map', 15.96,  22.42, 0.00, 1.0000),
    ('S05_monster',   '03',  22.42,  28.97, 2.95, 0.7455),
    ('S06_return',    '01',  28.97,  33.14, 2.60, 1.0000),
    ('S07_village',   '06',  33.14,  38.58, 0.00, 0.8000),
    ('S08_frost',     '07',  38.58,  46.22, 0.00, 1.0000),
    ('S09_map_frost', 'map', 46.22,  51.31, 0.00, 1.0000),
    ('S10_rain_wide', '02',  51.31,  57.20, 0.00, 1.0000),
    ('S11_famine',    '08',  57.20,  64.31, 0.00, 0.8800),
    ('S12_board',     'map', 64.31,  71.92, 0.00, 1.0000),
    ('S13_sun',       'map', 71.92,  79.25, 0.00, 1.0000),
    ('S14_1809',      'map', 79.25,  88.89, 0.00, 1.0000),
    ('S15_sumbawa',   '04',  88.89,  96.11, 0.20, 1.0000),
    ('S16_eruption',  '05',  96.11, 102.60, 1.90, 0.8700),
    ('S17_reckoning', 'map', 102.60, 109.48, 0.00, 1.0000),
]
T_END = 109.48
BY_NAME = {s[0]: s for s in SHOTS}
MAP_SHOTS = {'S04_map', 'S09_map_frost', 'S12_board', 'S13_sun', 'S14_1809', 'S17_reckoning'}

# transitions: a dissolve between live plates, the map's zoom-blur in/out, and three
# hard cuts where a dissolve would blunt the edit
FORCE_HARD_BEFORE = {'S05_monster', 'S12_board', 'S16_eruption'}


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
    if key == 'map':
        return ('map', int(round((t - t0) * 30)), 0, 0.0)
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


def label(base, text, x, y, t, t_in, t_out, size=48, fill=(226, 218, 200)):
    """a line of type that grows in and is gone by t_out; used inside the map plates"""
    if not (t_in <= t < t_out) or not C.T():
        return base
    a = min(ramp(t, t_in, t_in + 0.5), 1.0 - ramp(t, t_out - 0.4, t_out))
    if a <= 0:
        return base
    sp = C.text_sprite(text, size=size, fill=fill)
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
    """back to the farmers: «وفي آخر الحلقة هتعرف…»"""
    lt = t - 28.97
    cam = C.Camera(zoom=1.30 + 0.06 * ease(lt / 4.17), pan=(-70, -46))
    base = C.grade5(PL['01'].frame(2.6 + lt, cam), warmth=0.92, sat=0.80).convert('RGBA')
    return SNOW_MID.draw(base, t, density=0.5)


def base_s07(t):
    """«خلّينا نبدأ باللي شافوه الناس» — an ash-buried village, people still standing"""
    lt = t - 33.14
    cam = C.Camera(zoom=1.06 - 0.035 * ease(lt / 5.44), pan=(14 * (0.5 - lt / 5.44), 2))
    base = C.grade5(PL['06'].frame(lt * 0.800, cam), warmth=0.88, sat=0.58).convert('RGBA')
    base = ASH_HVY.draw(base, t, density=0.55)
    return MOTE.draw(base, t, density=0.5)


def base_s08(t):
    """the frost came back when it was supposed to be gone: macro on a living leaf"""
    lt = t - 38.58
    cam = C.Camera(zoom=1.05 - 0.045 * ease(lt / 7.64), pan=(-10 * (0.5 - lt / 7.64), 0))
    base = C.grade5(PL['07'].frame(lt, cam), warmth=0.82, sat=0.74).convert('RGBA')
    base = SNOW_FG.draw(base, t, density=0.30, blur=1.4)
    return MOTE.draw(base, t, density=0.6)


def base_s09(t):
    """the frost map: it came back when it was supposed to be gone"""
    lt = t - 46.22
    dur = 5.09
    m = map_obj()
    cam = C.Camera(zoom=1.30 - 0.07 * (0.5 * ease(lt / dur) + 0.5 * (lt / dur)),
                   pan=(-40 + 60 * (lt / dur), -10 + 40 * (lt / dur)), src=(MAP_W, MAP_H))
    base = cam.apply(map_base()).convert('RGBA')
    base = SNOW_MID.draw(base, t, density=0.40)
    d = ImageDraw.Draw(base)
    S = lambda ll: cam.to_screen(*m.px(*ll))
    # the frost is drawn as a cold shroud over the north-east: concentric dashed rings
    # that pulse outward, so the frame has a moving layer that is not the camera
    p = S(NE_LL)
    for k, (r0, ph) in enumerate(((90, 0.0), (150, 0.55), (210, 1.1))):
        u = ((lt / 2.2) + ph) % 1.0
        rr = r0 * (0.75 + 0.45 * u)
        a = int(190 * (1 - u) * ramp(lt, 0.2 + k * 0.25, 0.9 + k * 0.25))
        if a > 4:
            d.ellipse([p[0] - rr, p[1] - rr * 0.62, p[0] + rr, p[1] + rr * 0.62],
                      outline=(196, 224, 245, a), width=3)
    C.pin(base, p[0], p[1], t, 46.22, r=10)
    base = label(base, 'الصقيع رجع', 96, H - 150, t, 46.30, 50.6, size=52)
    return grader(base)


def base_s10(t):
    """rain over the whole European summer: the same fields, a different part of the storm"""
    lt = t - 51.31
    cam = C.Camera(zoom=1.20 - 0.06 * ease(lt / 5.89), pan=(-16 * (0.5 - lt / 5.89), 8))
    base = C.grade5(PL['02'].frame(lt, cam), warmth=0.78, sat=0.70).convert('RGBA')
    base = RAIN.draw(base, t, density=0.55)
    return SNOW_FG.draw(base, t, density=0.20, blur=1.9)


def base_s11(t):
    """«الصيف ما اختفاش من التقويم، اختفى من الحقول» — a family at a bare table"""
    lt = t - 57.20
    cam = C.Camera(zoom=1.06 - 0.04 * ease(lt / 7.11), pan=(6 * (0.5 - lt / 7.11), -4))
    base = C.grade5(PL['08'].frame(lt * 0.880, cam), warmth=0.94, sat=0.68).convert('RGBA')
    return MOTE.draw(base, t, density=0.55)


def base_s12(t):
    """the case opens: three suspects, three pins, one table"""
    lt = t - 64.31
    dur = 7.61
    m = map_obj()
    cam = C.Camera(zoom=1.62 - 0.16 * ease(lt / dur), pan=(0, 0), src=(MAP_W, MAP_H))
    base = cam.apply(map_base()).convert('RGBA')
    base = MOTE.draw(base, t, density=0.7)
    d = ImageDraw.Draw(base)
    S = lambda ll: cam.to_screen(*m.px(*ll))
    # three pins, one per suspect, landing on the beat
    pts = []
    for k, (ll, t_in) in enumerate(((EU_LL, 64.80), (ICE_LL, 66.40), (SU_LL, 68.00))):
        if t >= t_in:
            p = S(ll)
            C.pin(base, p[0], p[1], t, t_in, r=11)
            pts.append(p)
            base = focus(base, p[0], p[1], r=190, amount=0.16 * ramp(t, t_in, t_in + 0.5))
    if len(pts) > 1:
        d.line(pts, fill=C.GOLD + (170,), width=2)
    base = label(base, 'ملف التحقيق', 96, H - 150, t, 64.31, 71.4, size=54)
    return grader(base)


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
    'S04_map': base_s04, 'S05_monster': base_s05, 'S06_return': base_s06,
    'S07_village': base_s07, 'S08_frost': base_s08, 'S09_map_frost': base_s09,
    'S10_rain_wide': base_s10, 'S11_famine': base_s11, 'S12_board': base_s12,
    'S13_sun': base_s13, 'S14_1809': base_s14, 'S15_sumbawa': base_s15,
    'S16_eruption': base_s16, 'S17_reckoning': base_s17,
}


# ---------------------------------------------------------------- the card plan
# (name, slot, cue, hold, text) -- the layout queue retires one card before the next
CARDS = [
    ('stamp_1816', 'A', 2.10, 1.40, 'stamp'),
    ('place_usa', 'A', 5.05, 2.90, 'فلاحين · أمريكا'),
    ('place_eu', 'A', 9.97, 2.10, 'أوروبا'),
    ('crops', 'C', 12.90, 2.40, 'المحاصيل ما لحقتش تكبر'),
    ('map_km', 'C', 20.36, 1.60, '+15٬000 كم'),
    ('summer', 'C', 56.10, 2.40, 'الصيف اختفى من الحقول'),
    ('dalton', 'A', 74.59, 2.40, 'المشتبه 1 · شمس ضعيفة'),
    ('burst1809', 'A', 81.20, 2.30, 'المشتبه 2 · ثوران مجهول'),
    ('sumbawa_tag', 'A', 90.30, 2.40, 'المشتبه 3 · سومباوا'),
    ('dalt_band', 'C', 74.59, 1.00, None),
]

TAGS = []
for name, slot, cue, hold, text in CARDS:
    if text is None:
        continue
    if text == 'stamp':
        sprite = C.stamp_sprite('يونيو 1816', size=86)
    else:
        sprite = C.paper_tag(text, size=46 if len(text) > 18 else 52,
                             seed=abs(hash(name)) % 97 + 3)
    TAGS.append(TG.Tag(name, slot, cue, hold, sprite))
QUEUE = TG.TagLayoutQueue(TAGS, T_END).retime()

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
    if t >= 28.97:
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
    dict(t=30.20, what='the market: empty carts over the fields', sfx='sleet', shot='S07'),
    dict(t=32.10, what='the carts settle, ash drifting', sfx=None, shot='S07'),
    dict(t=33.80, what='candle lit on a bare table', sfx='thunder', shot='S08'),
    dict(t=35.60, what='the family leans in', sfx=None, shot='S08'),
    dict(t=37.40, what='the smallest child looks up', sfx='needle', shot='S08'),
    dict(t=39.20, what='the frost crosses the north-east', sfx='sleet', shot='S08'),
    dict(t=40.20, what='the shroud crosses the map', sfx=None, shot='S09'),
    dict(t=41.50, what='a second ring breaks', sfx=None, shot='S09'),
    dict(t=43.00, what='frost settles over the coast', sfx='water', shot='S09'),
    dict(t=44.60, what='the map goes cold', sfx=None, shot='S09'),
    dict(t=45.60, what='rain finds the frame', sfx='water', shot='S10'),
    dict(t=47.40, what='rain at full weight', sfx=None, shot='S10'),

    dict(t=48.40, what='rain at full weight', sfx='water', shot='S10'),
    dict(t=50.20, what='the horizon greys out', sfx=None, shot='S10'),
    dict(t=52.00, what='boats on the grey water', sfx='water', shot='S11'),
    dict(t=53.60, what='the swell lifts the hulls', sfx=None, shot='S11'),
    dict(t=55.10, what='spray over the gunwale', sfx='water', shot='S11'),
    dict(t=56.10, what='tag الصيف اختفى من الحقول enters', sfx='paper_in', shot='S11'),
    dict(t=57.20, what='hard cut: the street at night', sfx=None, shot='S12'),
    dict(t=58.60, what='a top hat crosses under the lamp', sfx='stamp', shot='S12'),
    dict(t=60.10, what='the lamp post flares', sfx=None, shot='S12'),
    dict(t=61.70, what='the figure turns the corner', sfx=None, shot='S12'),
    dict(t=63.20, what='the street recedes', sfx=None, shot='S12'),
    dict(t=64.80, what='the file opens: first pin', sfx='pin', shot='S12'),
    dict(t=66.40, what='second pin', sfx='pin', shot='S12'),
    dict(t=68.00, what='third pin', sfx='pin', shot='S12'),
    dict(t=69.60, what='the case is open: three suspects', sfx=None, shot='S12'),
    dict(t=71.30, what='the page turns to the first suspect', sfx=None, shot='S13'),
    dict(t=73.00, what='the sun dims', sfx='thread_draw', shot='S13'),
    dict(t=74.59, what='tag المشتبه 1 enters', sfx='paper_in', shot='S13'),
    dict(t=76.40, what='the inner ring pulls in', sfx='thread_draw', shot='S13'),
    dict(t=78.40, what='the light goes out', sfx=None, shot='S13'),
    dict(t=80.34, what='second suspect: a smear with no centre', sfx='thunder', shot='S14'),
    dict(t=82.20, what='the smear breathes', sfx=None, shot='S14'),
    dict(t=84.00, what='ash over the map', sfx='sleet', shot='S14'),
    dict(t=85.80, what='the smear drifts north', sfx=None, shot='S14'),
    dict(t=87.60, what='the plume leans west', sfx='sleet', shot='S14'),
    dict(t=88.89, what='Sumbawa from the air', sfx='thunder', shot='S15'),
    dict(t=90.30, what='tag المشتبه 3 enters', sfx='paper_in', shot='S15'),
    dict(t=92.20, what='ash plume thickens', sfx='sleet', shot='S15'),
    dict(t=94.10, what='the island disappears', sfx=None, shot='S15'),
    dict(t=95.10, what='the island goes dark', sfx=None, shot='S15'),
    dict(t=96.11, what='the eruption', sfx='sting', shot='S16'),

    dict(t=97.60, what='lava and lightning', sfx='thunder', shot='S16'),
    dict(t=99.40, what='embers rise', sfx=None, shot='S16'),
    dict(t=101.00, what='the column leans east', sfx='sleet', shot='S16'),
    dict(t=102.60, what='hard cut: the frame empties east', sfx=None, shot='S17'),
    dict(t=104.10, what='the map slides east', sfx='thread_draw', shot='S17'),
    dict(t=105.80, what='the ring closes on Sumbawa', sfx=None, shot='S17'),
    dict(t=107.50, what='the strongest was not in Europe', sfx=None, shot='S17'),
    dict(t=108.90, what='fade on the answer', sfx=None, shot='S17'),
]
EVENTS.sort(key=lambda e: e['t'])


def levels():
    """three moving layers in every shot, reported so QA can check it rather than trust it"""
    return {
        'S01_house': ['plate 09 + camera', 'snow mid', 'grade drift'],
        'S02_farmers': ['plate 01 + push', 'snow mid', 'snow fg'],
        'S03_europe': ['plate 02 + push', 'rain', 'snow fg'],
        'S04_map': ['map plate + drift', 'route + pins', 'ash drift'],
        'S05_monster': ['plate 03 + camera', 'lightning flash', 'ash drift'],
        'S06_return': ['plate 01 + push', 'snow mid', 'corner wordmark'],
        'S07_village': ['plate 06 + push', 'ash heavy', 'motes'],
        'S08_frost': ['plate 07 + push', 'snow fg', 'motes'],
        'S09_map_frost': ['map plate + drift', 'frost rings', 'snow mid'],
        'S10_rain_wide': ['plate 02 + push', 'rain', 'snow fg'],
        'S11_famine': ['plate 08 + push', 'candle glow', 'motes'],
        'S12_board': ['map plate + push', 'pins', 'motes'],
        'S13_sun': ['map plate + drift', 'sun rings', 'motes'],
        'S14_1809': ['map plate + drift', 'smear rings', 'ash drift'],
        'S15_sumbawa': ['plate 04 + push', 'ash drift', 'plume'],
        'S16_eruption': ['plate 05 + push', 'ash heavy', 'embers'],
        'S17_reckoning': ['map plate + push', 'ring + pin', 'ash drift'],
    }
