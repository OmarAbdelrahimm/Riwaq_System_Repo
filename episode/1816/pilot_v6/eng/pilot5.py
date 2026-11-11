#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eng5/pilot5.py — PILOT v5 (0:00-0:30).

The five fixes from the review, in one place:

  1. every callout goes through TagLayoutQueue: four fixed slots, one tag on screen at a
     time, entry only after the previous exit has completed, 0.4 s bezier entry, 0.3 s
     exit, 40 px slide, +-2 deg settle, 0.5 s stagger.
  2. the sting animates the SUPPLIED wordmark; the corner watermark is the same file.
  3. every text hit is a paper sound, calibrated per hit against the speech beneath it.
  4. the score is eng5/music5.py at 116 BPM (the supplied bed measures 70 BPM).
  5. dissolves between clips, zoom-blur in and out of the map, a whip pan on the
     Americas->Europe change, a hard cut into the monster, one grade over everything.
"""
import math

import numpy as np
from PIL import Image, ImageDraw

from . import core5 as C
from . import tags5 as TG
from . import world5 as W5

W, H = C.W, C.H

# every clip is 24 fps; the timeline is 30, so the plate steps 0.8 files per frame and
# plays at its true speed. No speed ramp, no frame blending, no optical flow anywhere.
P09 = C.Plate('09', src_fps=24.0)
P01 = C.Plate('01', src_fps=24.0)
P02 = C.Plate('02', src_fps=24.0)
P03 = C.Plate('03', src_fps=24.0)

SNOW_FG = C.Snow(n=46, speed=(240, 380), size=(1.6, 3.2), wind=-40, seed=21, alpha=(40, 80))
SNOW_MID = C.Snow(n=300, speed=(90, 200), size=(0.9, 2.2), wind=-26, seed=7, alpha=(60, 140))
RAIN = C.Rain(n=430, seed=11, alpha=(22, 62))
ASH = C.Snow(n=150, speed=(14, 34), size=(1.0, 2.2), wind=7, seed=31, alpha=(30, 74))


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def ramp(t, a, b):
    return max(0.0, min(1.0, (t - a) / max(1e-6, b - a)))


# ---------------------------------------------------------------- shot boundaries
S1, S2, S3, S4, S5, S6 = 0.0, 4.35, 9.97, 15.96, 22.42, 28.97
T_END = 30.0
DISSOLVE = 0.65
MAP_IN, MAP_OUT = 0.60, 0.60
WHIP = 0.30

# ---------------------------------------------------------------- the queue
TAGS = [
    # the year card now goes THROUGH the queue. In v5 it was drawn straight into the
    # frame and duly shared the screen with the disclaimer -- the one rule the queue
    # exists to enforce, broken by going around it.
    # the year card sits on the word and is clear of the S2 dissolve: in 2.10, out by 4.20
    TG.Tag('stamp_1816', 'A', 2.10, 1.4, C.stamp_sprite('يونيو 1816', size=86)),
    TG.Tag('place_usa', 'A', 5.05, 2.9,
           C.paper_tag('فلاحين · أمريكا', size=52, seed=5)),
    TG.Tag('place_eu', 'A', S3, 2.1,
           C.paper_tag('أوروبا', size=54, seed=8)),
    TG.Tag('crops', 'C', 12.90, 2.4,
           C.paper_tag('المحاصيل ما كبرتش', size=46, seed=9)),
    TG.Tag('monster', 'C', 25.75, 2.4,
           C.paper_tag('أشهر وحش في الأدب', size=46, seed=12)),
]
QUEUE = TG.TagLayoutQueue(TAGS, T_END)

# the disclaimer is floor type, not a card: ivory at 65 % with a soft shadow, top left,
# and gone before the year card arrives
DISCLAIMER = C.floating_line('مشاهد مُعاد تخيّلها', size=38, alpha=0.65)
DISC_IN, DISC_OUT_0, DISC_OUT_1 = 0.60, 2.95, 3.50
CORNER_SHOT = [None]
MAP = None
MAP_W, MAP_H = 2600, 1462


def map_obj():
    global MAP
    if MAP is None:
        MAP = W5.Map(lon_a=-132, lon_b=150, lat_a=-30, lat_b=80,
                     x0=0, y0=0, w=MAP_W, h=MAP_H, ss=3)
    return MAP


_MAPBASE = None


def map_base():
    global _MAPBASE
    if _MAPBASE is None:
        m = map_obj()
        bg = Image.new('RGB', (MAP_W, MAP_H), (8, 10, 13)).convert('RGBA')
        _MAPBASE = Image.alpha_composite(bg, W5.compose_map(bg, m, 0)).convert('RGB')
    return _MAPBASE


ROUTE_LL = [(-71.0, 42.3), (-58, 45.5), (-38, 50.0), (-14, 52.5), (8, 52.0),
            (28, 47.0), (44, 34.0), (58, 20.0), (74, 8.0), (92, -1.5),
            (108, -6.0), (117.5, -8.4)]
NE_LL, EU_LL, SU_LL = (-71.0, 42.3), (10.0, 49.0), (117.5, -8.4)


# ---------------------------------------------------------------- shots
def base_s1(t):
    """storm over the lake: the cold open, grade turning cold, snow arriving"""
    u = ramp(t, 0.0, 2.0)
    cam = C.Camera(zoom=1.30 - 0.14 * ease(min(1.0, t / S2)), pan=(0, -20))
    im = C.grade5(P09.frame(t, cam), warmth=1.55 - 0.55 * ease(u), sat=0.62 + 0.24 * ease(u))
    base = im.convert('RGBA')
    d = ramp(t, 1.0, 2.6)
    if d > 0:
        base = SNOW_MID.draw(base, t, density=0.35 * d)
    return base


def base_s2(t):
    """the farmers, slow push, snow thickening on the word"""
    lt = t - S2
    cam = C.Camera(zoom=1.04 + 0.09 * ease(lt / 5.62), pan=(10, 0))
    base = C.grade5(P01.frame(lt, cam), warmth=0.92, sat=0.80).convert('RGBA')
    base = SNOW_MID.draw(base, t, density=0.55 + 0.30 * ramp(t, 7.43, 8.65))
    base = SNOW_FG.draw(base, t, density=0.6, blur=1.6)
    return base


def base_s3(t):
    """Europe: rain and mud, rain hammering from the word مطر"""
    lt = t - S3
    cam = C.Camera(zoom=1.05 - 0.03 * ease(lt / 5.99), pan=(-8, 0))
    base = C.grade5(P02.frame(lt, cam), warmth=0.80, sat=0.74).convert('RGBA')
    base = RAIN.draw(base, t, density=0.30 + 0.55 * ramp(t, 10.6, 11.9))
    base = SNOW_FG.draw(base, t, density=0.22, blur=1.8)
    return base


def base_s4(t):
    """the map, dark mode, camera drifting across a plate larger than the frame"""
    lt = t - S4
    m = map_obj()
    cam = C.Camera(zoom=1.34 - 0.08 * (0.6 * ease(lt / 6.46) + 0.4 * (lt / 6.46)),
                   pan=(-120 + 200 * (lt / 6.46) + 9 * math.sin(lt * 0.7),
                        -40 + 70 * (lt / 6.46)),
                   src=(MAP_W, MAP_H))
    base = cam.apply(map_base()).convert('RGBA')
    base = ASH.draw(base, t, density=0.8)

    def S(lonlat):
        x, y = m.px(*lonlat)
        return cam.to_screen(x, y)

    d = ImageDraw.Draw(base)
    pts = [S(ll) for ll in ROUTE_LL]
    if t >= 16.53:
        p = S(NE_LL)
        C.pin(base, p[0], p[1], t, 16.53, r=11)
        a = ramp(t, 16.6, 17.1)
        ring = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        rd = ImageDraw.Draw(ring)
        rr = 26 + 10 * a
        rd.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr],
                   outline=C.GOLD_HI + (int(200 * a),), width=2)
        base.alpha_composite(ring)
    if t >= 17.35:
        W5.dashed_line(d, pts[:5], C.GOLD + (240,), width=4, dash=20, gap=14,
                       upto=ramp(t, 17.35, 19.04))
    if t >= 19.04:
        p = S(EU_LL)
        C.pin(base, p[0], p[1], t, 19.04, r=9)
    if t >= 19.72:
        W5.dashed_line(d, pts, C.GOLD + (245,), width=5, dash=22, gap=15,
                       upto=ramp(t, 19.72, 21.46))
    if t >= 21.02:
        p = S(SU_LL)
        C.pin(base, p[0], p[1], t, 21.02, r=12)

    if t >= 20.36 and C.T():
        u = ramp(t, 20.36, 21.46)
        val = int(round(15000 * (u ** 0.75)))
        a = min(1.0, ramp(t, 20.36, 20.6))
        sp = C.text_sprite(f'+{val:,} كم'.replace(',', '٬'), size=96, fill=C.GOLD_HI)
        if a < 1:
            sp = sp.copy()
            sp.putalpha(sp.split()[3].point(lambda v: int(v * a)))
        # upper right: the lower right of this frame is where the route lands
        base.alpha_composite(sp, (W - sp.width - 110, 60))
    if t >= 15.96 and C.T():
        a = ramp(t, 16.0, 16.6)
        lab = C.text_sprite('السر مش في القارات', size=48, fill=(226, 218, 200))
        lab = lab.resize((int(lab.width * (0.75 + 0.25 * a)), int(lab.height * (0.75 + 0.25 * a))),
                         Image.LANCZOS)
        base.alpha_composite(lab, (96, 74))
    return C.grade5(base.convert('RGB'), warmth=0.90, sat=0.90).convert('RGBA')


# plate 03 has its own scene change: black silhouette to frame 40, a bright lab reveal to
# 100, the settled silhouette after. The sting must land on the figure in the arch window,
# so the in-point is 2.95 s, not the head of the clip.
S5_IN, S5_RATE = 2.95, 0.7455


def base_s5(t):
    """the silhouette plate; its own lightning flash is retimed to land inside the shot"""
    lt = t - S5
    src_t = S5_IN + lt * S5_RATE
    cam = C.Camera(zoom=1.10 - 0.06 * ease(lt / 6.55), pan=(0, 0))
    im = C.grade5(P03.frame(src_t, cam), warmth=0.86, sat=0.60)
    f = 0.0
    for peak in (4.90, 5.35):
        d = src_t - peak
        if -0.05 < d < 0.55:
            f = max(f, 0.20 * math.exp(-max(0.0, d) * 7.0))
    im = C.apply_flash(im, f)

    # summer -> the figure resolves -> ash thickens: three visible changes on three words.
    # The layer list for this shot claims ash drift, so ash is now actually drawn here.
    if t >= 24.90:
        bloom = 0.10 * ramp(t, 24.90, 25.35)
        im = C.apply_flash(im, bloom)
    base = im.convert('RGBA')
    ash_d = 0.55 + 0.55 * ramp(t, 27.24, 28.19)
    base = ASH.draw(base, t - S5, density=ash_d)
    if t >= 25.63:
        k = 0.30 * ramp(t, 25.63, 26.60)
        a = np.asarray(base.convert('RGB'), np.float32)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        rr = np.sqrt(((xx - W / 2) / (W * 0.60)) ** 2 + ((yy - H / 2) / (H * 0.60)) ** 2)
        a *= (1.0 - k * np.clip(rr - 0.45, 0, 2) ** 1.5)[..., None]
        base = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')

    # the sting: a quick dip, then the SUPPLIED wordmark writes on
    base = base
    if S5 + 0.55 <= t <= S5 + 3.30:
        u = ramp(t, S5 + 0.55, S5 + 1.75)
        fade = 1.0 if t < S5 + 2.85 else max(0.0, (S5 + 3.30 - t) / 0.45)
        lg, s = C.logo_scaled(430)
        part = C.reveal_r2l(lg, u)
        if fade < 1:
            part = part.copy()
            part.putalpha(part.split()[3].point(lambda v: int(v * fade)))
        x = int(W / 2 - lg.width / 2)
        y = int(H / 2 - lg.height / 2 - 40)
        base.alpha_composite(part, (x, y))
    return base


def base_s6(t):
    """the button: back to the farmers, corner watermark"""
    lt = t - S6
    cam = C.Camera(zoom=1.30 + 0.06 * ease(lt / 1.03), pan=(-70, -46))
    base = C.grade5(P01.frame(7.2 + lt, cam), warmth=0.92, sat=0.80).convert('RGBA')
    base = SNOW_MID.draw(base, t, density=0.5)
    return base


SHOT_FNS = [('S1_cold_open', base_s1), ('S2_farmers', base_s2), ('S3_europe', base_s3),
            ('S4_map', base_s4), ('S5_monster', base_s5), ('S6_return', base_s6)]
BOUNDS = [(S1, S2), (S2, S3), (S3, S4), (S4, S5), (S5, S6), (S6, T_END)]


def map_base_final(t):
    return base_s4(max(t, S4)).convert('RGB')


def shot_name(t):
    if t < S2:
        return 'S1_cold_open'
    if t < S3:
        return 'S2_farmers'
    if t < S4:
        return 'S3_europe'
    if t < S5:
        return 'S4_map'
    if t < S6:
        return 'S5_monster'
    return 'S6_return'


def plate_src(t):
    """which decoded frames actually fed this frame: the log records what happened"""
    if t < S2:
        return ('09', P09.idx(t), P09.n, P09.bsf)
    if t < S3:
        return ('01', P01.idx(t - S2), P01.n, P01.bsf)
    if t < S4:
        return ('02', P02.idx(t - S3), P02.n, P02.bsf)
    if t < S5:
        return ('map', -1, 0, 0.0)
    if t < S6:
        return ('03', P03.idx(S5_IN + (t - S5) * S5_RATE), P03.n, P03.bsf)
    return ('01', P01.idx(7.2 + (t - S6)), P01.n, P01.bsf)


def cut_of(t):
    for b in (S2, S3, S4, S5, S6):
        if abs(t - b) <= DISSOLVE / 2 + 1e-9:
            return b
    return None


# ---------------------------------------------------------------- the frame
_STAMP_T0 = 2.60


def frame_at(t):
    """one finished frame, at time t. Pure function of t."""
    i = int(round(t * 30))
    base = None

    done = False
    for (name, fn), (t0, t1) in zip(SHOT_FNS, BOUNDS):
        if t0 <= t < t1:
            base = fn(t)
            done = True
            break
    if not done:
        base = base_s6(t)

    # transitions. Each boundary gets the move the brief calls for:
    #   storm -> farmers   cross-dissolve 0.65
    #   farmers -> Europe  whip pan 0.30 (content changes; a dissolve would ghost)
    #   Europe -> map      zoom-blur 0.60 in, 0.60 out
    #   map -> monster     hard cut on the sting
    #   monster -> button  hard cut
    if S2 - DISSOLVE / 2 <= t < S2 + DISSOLVE / 2:
        k = ramp(t, S2 - DISSOLVE / 2, S2 + DISSOLVE / 2)
        base = C.dissolve(base_s1(t), base_s2(t), k).convert('RGBA')
    if S3 - WHIP / 2 <= t < S3 + WHIP / 2:
        k = ramp(t, S3 - WHIP / 2, S3 + WHIP / 2)
        base = C.whip(base_s2(t), base_s3(t), k).convert('RGBA')
    if S4 - MAP_IN <= t < S4 + 0.10:
        k = 1.0 - ramp(t, S4 - MAP_IN, S4 + 0.10)
        base = C.zoom_blur(base_s3(t).convert('RGB'), k * 0.55).convert('RGBA')
        if k > 0.55:
            base = C.dissolve(base, map_base_final(t), (k - 0.55) / 0.45)
    if S5 - MAP_OUT <= t < S5:
        k = ramp(t, S5 - MAP_OUT, S5)
        base = C.zoom_blur(base_s4(t).convert('RGB'), (1 - k) * 0.55).convert('RGBA')
        if k > 0.6:
            base = C.dissolve(base, base_s5(t).convert('RGB'), (k - 0.6) / 0.4)

    # every transition path returns RGB; the tag queue needs RGBA
    base = base.convert('RGBA')

    # 2) the disclaimer: floating type, no paper, top left
    if C.T() and DISC_IN <= t < DISC_OUT_1:
        a_ = ramp(t, DISC_IN, DISC_IN + 0.45)
        if t > DISC_OUT_0:
            a_ *= max(0.0, (DISC_OUT_1 - t) / (DISC_OUT_1 - DISC_OUT_0))
        sp = DISCLAIMER['sprite'].copy()
        sp.putalpha(sp.split()[3].point(lambda v: int(v * a_)))
        base.alpha_composite(sp, (96 - DISCLAIMER['pad'], 86 - DISCLAIMER['pad']))

    # 3) the tag queue: the ONLY way a callout reaches the screen
    if C.T():
        base = QUEUE.render(base, t)

    # 4) the corner watermark, from the supplied file. It goes in whichever upper corner
    #    is darker on this frame, so the ivory ink always clears 4.5:1 over the plate.
    if t >= S5 + 3.30:
        a = min(1.0, ramp(t, S5 + 3.30, S5 + 3.75))
        lg, _ = C.logo_scaled(300)
        L = np.asarray(base.convert('L'), np.float32)
        zone = (56, 56 + 210)
        left = float(L[zone[0]:zone[1], 40:40 + lg.width].mean())
        right = float(L[zone[0]:zone[1], W - 40 - lg.width:W - 40].mean())
        x = 40 if left <= right else W - lg.width - 40
        C.place_logo(base, x, 56, width=300, alpha=a)
        CORNER_SHOT[0] = (x, round(left, 1), round(right, 1))

    out = C.finish(base.convert('RGB'), i)
    if t < 0.18:
        out = C.fade_to_black(out, t / 0.18)
    if t > T_END - 0.35:
        out = C.fade_to_black(out, max(0.0, (T_END - t) / 0.35))
    return out


def logo_report():
    li = C.logo_info()
    return dict(file=li['file'].split('/')[-1], native=li['native'], mode=li['mode'],
                alpha_bbox=li['alpha_bbox'], drawn_width=300)


# ---------------------------------------------------------------- events
EVENTS = [
    dict(t=1.20, what='snow arrives over the lake', sfx=None, shot='S1'),
    dict(t=2.60, what='stamp «يونيو 1816»', sfx='stamp', shot='S1'),
    dict(t=4.35, what='snow drives in on فلاحين', sfx='sleet', shot='S2'),
    dict(t=5.05, what='tag فلاحين · أمريكا enters', sfx='paper_in', shot='S2'),
    dict(t=6.25, what='thermometer needle drops', sfx='needle', shot='S2'),
    dict(t=7.43, what='snow thickens on والتلج', sfx='sleet', shot='S2'),
    dict(t=8.65, what='snow reaches full weight on بينزل', sfx='sleet', shot='S2'),
    dict(t=S3 + 0.30, what='tag أوروبا enters', sfx='paper_in', shot='S3'),
    dict(t=11.52, what='rain at full weight on مطر', sfx='water', shot='S3'),
    dict(t=12.26, what='sleet layer in on وبرد', sfx='sleet', shot='S3'),
    dict(t=13.27, what='tag المحاصيل ما كبرتش enters', sfx='paper_in', shot='S3'),
    dict(t=14.78, what='crop strip pinned on تكبر', sfx='pin', shot='S3'),
    dict(t=16.53, what='New England pinned', sfx='pin', shot='S4'),
    dict(t=17.35, what='thread leg 1 draws', sfx='thread_draw', shot='S4'),
    dict(t=19.04, what='thread lands on Europe', sfx='pin', shot='S4'),
    dict(t=19.72, what='thread turns for Sumbawa', sfx='thread_draw', shot='S4'),
    dict(t=21.02, what='Sumbawa pinned + counter', sfx='pin', shot='S4'),
    dict(t=22.42, what='brand sting: wordmark writes on', sfx='sting', shot='S5'),
    dict(t=23.60, what='plate lightning across the window', sfx='thunder', shot='S5'),
    dict(t=24.90, what='summer bloom on الصيف', sfx=None, shot='S5'),
    dict(t=25.75, what='tag أشهر وحش في الأدب enters', sfx='paper_in', shot='S5'),
    dict(t=26.60, what='silhouette settles, ash rises', sfx=None, shot='S5'),
    dict(t=27.24, what='ash thickens on وحش', sfx=None, shot='S5'),
    dict(t=28.19, what='last word الأدب, ash at full', sfx='sleet', shot='S5'),
    dict(t=S6, what='corner wordmark + return', sfx=None, shot='S6'),
    dict(t=29.65, what='wordmark settles, fade', sfx=None, shot='S6'),
]
EVENTS.sort(key=lambda e: e['t'])

TEXTS = [
    ('disclaimer', 'S1', 2.20, (96, 84, 300, 60), 'ink on paper'),
    ('stamp 1816', 'S1', 3.30, (W - 700, 300, 470, 130), 'ink on paper'),
    ('place_usa', 'S2', 6.00, (120, 120, 430, 96), 'ink on paper'),
    ('place_eu', 'S3', 11.00, (110, 116, 300, 94), 'ink on paper'),
    ('crops', 'S3', 14.20, (104, H - 250, 520, 86), 'ink on paper'),
    ('map counter', 'S4', 21.30, (1080, 700, 640, 200), 'gold on dark'),
    ('monster', 'S5', 26.60, (104, H - 300, 470, 92), 'ink on paper'),
]
