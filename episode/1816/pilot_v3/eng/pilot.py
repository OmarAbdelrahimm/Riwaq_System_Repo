#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
eng/pilot.py — the 0-30 s hook of Chapter 1 (1816), rebuilt as a layered edit.

Every shot is a stack of at least three live layers; the names are recorded from the
same list the compositor consumes, so QA counts what was actually drawn.

Timing is read from vo_timestamps_FINAL.json (measured on the final 626.37 s master),
so a prop lands on the word the word was spoken:
  stamp «يونيو 1816»        2.92  (the year is the word being said)
  tag «نيو إنجلاند …»       6.34  (نيو إنجلاند)
  frost                    15.89 (الصقيع)
  circled frost            16.87 (وهو المفروض غايب)
  thread leaves the frame  20.12 (بعد)
  tag «آلاف الكيلومترات»    21.02 (الكيلومترات)
  brand sting              22.42 (وفي)
  caption «أشهر وحش…»      25.55 (ولادة أشهر وحش)
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from eng.core import (W, H, FPS, COL, hexrgb, ar, font, step, ease, ramp, clamp01,
                      Plate, Particles, Film, Shot, Logo, TextReveal, Frost,
                      draw_thread, draw_circle_annot, draw_arrow, paper_sheet, tape,
                      pin_sprite, stamp_sprite, ink_blot, ruwaq_mark, mark_path,
                      grade_lerp, desaturate, expose, drop_shadow, contrast_ratio, bg_stats,
                      torn_rect)
import eng.maps as maps

ROOT = '/home/user/Riwaq_System_Repo'
SH = '/home/user/work/shots'
BUILD = os.path.join(ROOT, 'episode/1816/build')

FILM = Film(grain=10.0, vig=0.20, seed=3)
LOGO = Logo(size=52, color='parchment', alpha=200)

# the film's one honesty label: AI-built scenes are re-imagined, said once at the head
# of the chapter (and again in the credits), never per scene.
REIMAGINED = 'مشاهد مُعاد تخيّلها'


# ---------------------------------------------------------------- helpers
def canvas(color=COL['ink_deep']):
    return Image.new('RGB', (W, H), hexrgb(color))


class L:
    """a named layer; renderers return [L('plate.parallax', img), ...]"""
    __slots__ = ('name', 'im', 'info')

    def __init__(self, name, im, **info):
        self.name, self.im = name, im
        self.info = info


def grade_cold(im, k):
    return grade_lerp(im, 0.0, 1.0, k)


def sheet_on_frame(sheet, x, y, shadow=True):
    """place a physical sheet at (x, y) with its shadow underneath it"""
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    if shadow:
        lay = maps.shadow_of(sheet, at=(x, y), blur=24, off=(16, 20), size=(W, H))
    lay.alpha_composite(sheet, (x, y))
    return lay


def fade(lay, k):
    if k >= 0.999:
        return lay
    a = np.asarray(lay, np.float32).copy()
    a[..., 3] *= k
    return Image.fromarray(a.astype(np.uint8))


# ---------------------------------------------------------------- props
class Thermometer:
    """paper-collage thermometer: a cut paper strip, brass pin, ink scale, and a red
    column whose meniscus drops in stepped motion (10 fps), not on a smooth tween"""

    def __init__(self, h=430, w=132, seed=4):
        self.h, self.w = h, w
        body = paper_sheet(w, h, seed=seed, tone='parchment2')
        lay = Image.new('RGBA', body.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        cx = w // 2 + 12
        top, bot = 54, h - 62
        d.rounded_rectangle([cx - 13, top, cx + 13, bot], radius=13,
                            outline=(44, 41, 37, 240), width=3)
        d.rounded_rectangle([cx - 6, top + 6, cx + 6, bot - 6], radius=6,
                            outline=(44, 41, 37, 95), width=1)
        f = font('plex', 15)
        for i in range(9):
            yy = top + 10 + i * (bot - top - 20) / 8
            long = (i % 2 == 0)
            d.line([(cx - 44, yy), (cx - (14 if long else 24), yy)],
                   fill=(44, 41, 37, 200 if long else 135), width=2)
            if long:
                d.text((cx - 78, yy - 9), str(80 - i * 10), font=f, fill=(44, 41, 37, 180))
        d.ellipse([cx - 19, bot - 14, cx + 19, bot + 24], outline=(44, 41, 37, 240), width=3)
        body = Image.alpha_composite(body, lay)
        p = pin_sprite(r=10, color='gold')
        body.alpha_composite(p, (int(cx - p.width / 2), 4))
        self.body = drop_shadow(body, blur=18, off=(11, 14), alpha=170)
        self.cx, self.top, self.bot = cx, top, bot

    def layer(self, x, y, k=1.0, drop_from=0.40, drop_to=2.55, t=0.0):
        spr = self.body.copy()
        d = ImageDraw.Draw(spr)
        kk = ease(ramp(step(t, 10.0), drop_from, drop_to))     # stepped 10 fps
        yy = self.bot + (self.top - self.bot) * kk
        d.rounded_rectangle([self.cx - 8, yy, self.cx + 8, self.bot], radius=7,
                            fill=(150, 44, 40, 240))
        d.ellipse([self.cx - 16, self.bot - 10, self.cx + 16, self.bot + 18],
                  fill=(150, 44, 40, 244))
        d.ellipse([self.cx - 16, yy - 6, self.cx + 16, yy + 8], fill=(178, 62, 56, 240))
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        lay.alpha_composite(fade(spr, k), (int(x), int(y)))
        return lay


def tag(text, size=42, tone='parchment2', seed=21):
    """pinned paper tag with a pin through it, and the ink box in sprite coordinates
    (the drop shadow pads the canvas, so the box carries that pad too)"""
    tr = TextReveal(text, size=size, color='ink_deep', fontkey='plex_bold')
    pw, ph = int(tr.tw + 92), int(tr.th + 104)
    sheet = paper_sheet(pw, ph, seed=seed, tone=tone)
    tx, ty = int(46 + (pw - 92 - tr.tw) / 2), 74
    ImageDraw.Draw(sheet).text((tx, ty), ar(text), font=tr.f,
                               fill=hexrgb(COL['ink_deep']) + (246,))
    p = pin_sprite(r=11)
    sheet.alpha_composite(p, (int(pw * 0.5 - p.width / 2), 6))
    pad = int(14 * 2.2)
    return dict(sprite=drop_shadow(sheet, blur=14, off=(8, 10), alpha=155),
                box=(pad + tx + 6, pad + ty + 6, pad + tx + tr.tw + 6, pad + ty + tr.th + 8))


class Caption:
    """A key phrase in dark ink on a torn paper slip. On this chapter's frost/cream
    plates light type cannot hold 4.5:1, so phrases are carried by paper — and the
    slip's own pixels are what QA measures against the ink."""

    def __init__(self, text, size=54, tone='parchment2', seed=88, pad=(46, 34)):
        tr = TextReveal(text, size=size, color='ink_deep', fontkey='plex_bold', max_words=6)
        pw, ph = int(tr.tw + pad[0] * 2), int(tr.th + pad[1] * 2)
        sheet = paper_sheet(pw, ph, seed=seed, tone=tone)
        d = ImageDraw.Draw(sheet)
        d.text((pad[0] - tr.bb[0], pad[1] - tr.bb[1]), ar(text), font=tr.f,
               fill=hexrgb(COL['ink_deep']) + (250,))
        d.line([(pad[0], pad[1] - 18), (pw - pad[0], pad[1] - 18)],
               fill=hexrgb(COL['burgundy']) + (150,), width=2)
        self.sprite = drop_shadow(sheet, blur=16, off=(9, 12), alpha=172)
        self.text = text
        sh_pad = int(16 * 2.2)          # drop_shadow pads the canvas by blur * 2.2
        self.box_in_sprite = (sh_pad + pad[0], sh_pad + pad[1],
                              sh_pad + pad[0] + tr.tw, sh_pad + pad[1] + tr.th)

    def layer(self, k=1.0, xf=0.5, yf=0.79, rise=0):
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        x = int(W * xf - self.sprite.width / 2)
        y = int(H * yf - self.sprite.height / 2 + rise)
        lay.alpha_composite(fade(self.sprite, k), (x, y))
        bx0, by0, bx1, by1 = self.box_in_sprite
        return L('prop.caption', lay, text=self.text, k=k,
                 box=(x + bx0, y + by0, x + bx1, y + by1), fg=hexrgb(COL['ink_deep']))


def paper_label(text, size=24, seed=23, w=None):
    """small dark-ink line on a torn slip — used for the honesty label. Returns the
    sprite plus the ink box in sprite coordinates."""
    f = font('plex', size)
    probe = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
    bb = probe.textbbox((0, 0), ar(text), font=f)
    tw = bb[2] - bb[0]
    pw = w or int(tw + 54)
    ph = int(size + 30)
    sheet = paper_sheet(pw, ph, seed=seed, tone='parchment2')
    tx, ty = (pw - tw) / 2, 13
    ImageDraw.Draw(sheet).text((tx, ty), ar(text), font=f,
                               fill=hexrgb(COL['ink_deep']) + (238,))
    pad = int(10 * 2.2)
    return dict(sprite=drop_shadow(sheet, blur=10, off=(6, 8), alpha=155),
                box=(pad + int(tx) + 2, pad + int(ty) + 3,
                     pad + int(tx) + int(tw) + 2, pad + int(ty) + int(bb[3] - bb[1]) + 6))


# ---------------------------------------------------------------- shots
def build_shots():
    shots = []

    # ================= S1  0.00-3.30  wheat turns from summer to frost ON SCREEN
    p_warm = Plate(os.path.join(SH, 'look01_raw.png'), horizon=0.42)
    p_snow = Plate(os.path.join(SH, 'ch1_wheat_snow_raw.png'), horizon=0.40)
    snow_a = Particles('snow', count=300, seed=11, speed=1.0, wind=0.5, size=(1, 2.6))

    st = stamp_sprite('يونيو 1816', size=46, color='burgundy', pad=20)
    st_paper = paper_sheet(st.width + 46, st.height + 40, seed=17, tone='parchment2')
    st_paper = drop_shadow(st_paper, blur=13, off=(7, 9), alpha=168)
    st_paper.alpha_composite(st, (23, 20))
    disclaimer = paper_label(REIMAGINED, size=23, seed=29)

    def s1(t, fi, suppress=()):
        # two plates cross-dissolved under two seconds, both parallaxing: the season
        # change happens in front of the audience instead of being implied by a grade
        zoom = 1.02 + 0.11 * ease(t / 3.3)
        k = ease(ramp(t, 0.75, 2.55))
        warm = p_warm.frame(zoom=zoom, pan=(0.10, -0.03), parallax=1.0)
        cold = grade_cold(p_snow.frame(zoom=zoom, pan=(0.10, -0.03), parallax=1.0), 0.62)
        base = Image.blend(warm, cold, k)
        out = [L('plate.parallax', base),
               L('particles.snow', snow_a.draw(t, intensity=0.12 + 0.88 * ramp(t, 0.7, 2.0)))]
        if t > 2.55 and 'prop.stamp' not in suppress:
            k2 = ease(ramp(t, 2.65, 2.92))
            sc = 1.5 - 0.5 * k2
            spr = st_paper.rotate(-7, expand=True, resample=Image.BICUBIC)
            spr = spr.resize((max(2, int(spr.width * sc)), max(2, int(spr.height * sc))),
                             Image.BICUBIC)
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            px0, py0 = int(W * 0.60 - spr.width / 2), int(H * 0.17)
            lay.alpha_composite(fade(spr, min(1.0, k2 * 1.6)), (px0, py0))
            bw, bh = st.width + 46, st.height + 40
            box = (px0 + (spr.width - bw) // 2 + 23 + 8,
                   py0 + (spr.height - bh) // 2 + 20 + 8,
                   px0 + (spr.width - bw) // 2 + 23 + st.width - 8,
                   py0 + (spr.height - bh) // 2 + 20 + st.height - 8)
            out.append(L('prop.stamp', lay, text='يونيو 1816', box=box, k=k2,
                         fg=hexrgb(COL['burgundy'])))
        if 0.5 < t < 3.05 and 'prop.text' not in suppress:
            kd = ease(ramp(t, 0.5, 0.82)) * (1.0 - ease(ramp(t, 2.55, 3.05)))
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            px, py = int(W * 0.035), int(H * 0.055)
            lay.alpha_composite(fade(disclaimer['sprite'], kd), (px, py))
            b = disclaimer['box']
            out.append(L('prop.disclaimer', lay, text=REIMAGINED, k=kd,
                         box=(px + b[0], py + b[1], px + b[2], py + b[3]),
                         fg=hexrgb(COL['ink_deep'])))
        return out

    shots.append(Shot('S1_wheat', 0.00, 3.30, [], s1,
                      events=[(2.92, 'stamp «يونيو 1816» lands', 'stamp')], cam='push'))

    # ================= S2  3.30-7.43  boots in the mud, thermometer, pinned tag
    p_boots = Plate(os.path.join(SH, 'ch1_03_legs_raw.png'), horizon=0.30) \
        if os.path.exists(os.path.join(SH, 'ch1_03_legs_raw.png')) else None
    therm = Thermometer()
    tag_geo = tag('نيو إنجلاند · 8 يونيو')
    pinned = tag_geo

    def s2(t, fi, suppress=()):
        zoom = 1.11 - 0.05 * ease(t / 4.13)
        base = grade_cold(p_boots.frame(zoom=zoom, pan=(-0.16 + 0.06 * ease(t / 4.0), 0.0),
                                        parallax=1.0), 0.70)
        out = [L('plate.parallax', base),
               L('particles.rain', Particles('rain', count=210, seed=23, speed=1.9,
                                             wind=0.7, opacity=0.8).draw(t, 0.9)),
               # snow starts on «والتلج» (7.43) and thickens from there
               L('particles.snow', Particles('snow', count=260, seed=27, speed=1.6,
                                             wind=0.9, size=(1, 3.0),
                                             area=(0.0, 0.0, 1.0, 0.85)).draw(
                   t, ramp(t, 3.9, 4.25) * 0.85)),
               L('prop.thermometer', therm.layer(W - 300, 120, k=ease(ramp(t, 0.10, 0.5)),
                                                 t=t))]
        if t > 1.00 and 'prop.text' not in suppress:      # 4.30, as «أمريكا» is named
            kk = ease(ramp(t, 1.00, 1.26))
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            tx, ty = int(W * 0.05), int(H * 0.615 - 46 * (1 - kk))
            lay.alpha_composite(fade(pinned['sprite'], kk), (tx, ty))
            b = pinned['box']
            out.append(L('prop.pinned_tag', lay, text='نيو إنجلاند · 8 يونيو',
                         box=(tx + b[0], ty + b[1], tx + b[2], ty + b[3]), k=kk,
                         fg=hexrgb(COL['ink_deep'])))
        return out

    shots.append(Shot('S2_boots', 3.30, 7.43, [], s2,
                      events=[(3.92, 'thermometer slides onto the frame', 'paper_slide'),
                              (4.35, 'place tag «نيو إنجلاند · 8 يونيو» pinned', 'pin'),
                              (6.20, 'thermometer needle falls to frost', 'needle'),
                              (7.43, 'snow thickens on the field', 'wind')],
                      cam='pull'))

    # ================= S3  7.43-9.97  a farmer in falling snow
    p_shadow = Plate(os.path.join(SH, 'ch1_23_shadow_raw.png'), horizon=0.52)
    snow_b = Particles('snow', count=420, seed=31, speed=1.4, wind=0.35, size=(1, 3.2))
    snow_g = Particles('snow', count=150, seed=33, speed=2.2, wind=0.9, size=(2, 5),
                       opacity=0.35, area=(0.0, 0.55, 1.0, 0.45))

    def s3(t, fi, suppress=()):
        zoom = 1.03 + 0.06 * ease(t / 2.54)
        base = grade_cold(p_shadow.frame(zoom=zoom, pan=(0.05 * math.sin(t * 0.8), 0.0),
                                         parallax=1.15), 0.62)
        # this plate arrived with a warm sun disc in the sky, which breaks the
        # chapter's palette: take the colour out, hold the highlights down
        base = desaturate(base, 0.88, 1.08)
        base = expose(base, 0.86, 0.02)
        return [L('plate.parallax', base),
                L('particles.snow_far', snow_b.draw(t, intensity=ramp(t, 0.15, 1.1))),
                L('particles.snow_ground', snow_g.draw(t, intensity=0.85))]

    shots.append(Shot('S3_silhouette', 7.43, 9.97, [], s3,
                      events=[(8.65, 'snow begins to fall on him', 'wind')], cam='drift'))

    # ================= S4  9.97-15.31  the paper map over Europe, then the drowned field
    p_table = Plate(os.path.join(SH, 'ch1_18_table_raw.png'), horizon=0.40)
    MW, MH = int(W * 0.62), int(W * 0.62 * 0.62)
    paper_map = maps.make_map_sheet(MW, MH, -45, 50, 1.78, seed=44)
    MAP_O = (int(W * 0.165), int(H * 0.145))
    route = [(x + MAP_O[0], y + MAP_O[1]) for x, y in
             maps.route_points([(-71.0, 42.3), (-40, 46), (-5, 49), (10, 50.5), (37.6, 55.75)],
                               'equirect', -45, 50, MW, MH, 1.78)]
    p_flood = Plate(os.path.join(SH, 'ch1_flooded_crops_raw.png'), horizon=0.42) \
        if os.path.exists(os.path.join(SH, 'ch1_19_footprint_raw.png')) else None
    p_flood_ok = os.path.exists('/home/user/work/shots/ch1_flooded_crops_raw.png')

    def table_move(t, dur):
        zoom = 1.16 + 0.04 * ease(t / dur)
        return grade_cold(p_table.frame(zoom=zoom,
                                        pan=(-0.06 + 0.08 * ease(t / dur),
                                             0.22 - 0.03 * ease(t / dur)),
                                        parallax=1.10), 0.62)

    def water_line(t):
        """the standing water climbing the furrows: a soft horizontal band that
        rises across the lower frame, drawn as water, not as a card"""
        k = ease(ramp(t, 4.28, 4.95))
        if k <= 0:
            return None
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        y = int(H * (0.95 - 0.10 * k))
        band = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(band).rectangle([0, y, W, H], fill=(74, 88, 92, 62))
        lay = band.filter(ImageFilter.GaussianBlur(26))
        return lay

    def s4(t, fi, suppress=()):
        if t < 2.35:
            dx = int(16 * math.sin(t * 0.7)); dy = int(9 * math.cos(t * 0.5))
            return [L('plate.table', table_move(t, 2.35)),
                    L('map.sheet_on_plate',
                      sheet_on_frame(paper_map, MAP_O[0] + dx, MAP_O[1] + dy)),
                    L('particles.rain', Particles('rain', count=230, seed=47, speed=2.4,
                                                  wind=0.5, opacity=0.75).draw(
                        t, ramp(t, 0.15, 1.1))),
                    L('annotation.thread', draw_thread(route, ramp(t, 0.85, 2.25), width=6))]
        lt = t - 2.35
        zoom = 1.07 - 0.05 * ease(lt / 2.95)
        base = grade_cold(p_flood.frame(zoom=zoom, pan=(0.10 * ease(lt / 2.95), 0.0),
                                        parallax=1.0), 0.85)
        return [L('plate.parallax', base),
                L('particles.rain', Particles('rain', count=260, seed=51, speed=2.6,
                                              wind=0.45, opacity=0.8).draw(lt, 1.0)),
                L('particles.sleet', Particles('snow', count=180, seed=55, speed=3.4,
                                               wind=0.9, size=(1, 2.2), opacity=0.55).draw(
                    lt, ramp(t, 2.29, 2.62))),
                L('water.rising', water_line(t))]

    shots.append(Shot('S4_map_flood', 9.97, 15.31, [], s4,
                      events=[(11.52, 'rain falls over Europe', 'rain'),
                              (12.26, 'the rain turns to sleet', 'sleet'),
                              (13.65, 'the crops never grew', 'wind'),
                              (14.60, 'the furrows go under water', 'water')], cam='pan'))

    # ================= S5a  15.31-17.50  frost returns: glass, then a frosted blade
    p_win = Plate(os.path.join(SH, 'ch1_20_window_outside_raw.png'), horizon=0.44)
    p_ice = Plate(os.path.join(SH, 'ch1_frost_leaf_raw.png'), horizon=0.42)
    frost = Frost((int(W * 0.30), int(H * 0.16), int(W * 0.52), int(H * 0.64)), seed=77)

    def s5a(t, fi, suppress=()):
        if t < 0.98:
            zoom = 1.05 + 0.05 * ease(t / 0.98)
            base = grade_cold(p_win.frame(zoom=zoom, pan=(0.06 * ease(t / 0.98),
                                                          -0.02 + 0.02 * ease(t / 0.98)),
                                          parallax=1.20), 0.74)
            base = expose(base, 1.55, 0.05)
            return [L('plate.parallax', base),
                    L('particles.snow_far', Particles('snow', count=150, seed=79, speed=1.1,
                                                      wind=0.5, size=(1, 2.4),
                                                      area=(0.0, 0.0, 0.55, 0.62)).draw(t, 0.8)),
                    L('frost.glaze', frost.draw(ease(ramp(t, 0.02, 0.95))))]
        lt = t - 0.98
        zoom = 1.10 - 0.07 * ease(lt / 1.21)
        base = grade_cold(p_ice.frame(zoom=zoom, pan=(-0.05 + 0.05 * ease(lt / 1.2),
                                                      0.02 - 0.02 * ease(lt / 1.2)),
                                      parallax=1.15), 0.72)
        out = [L('plate.parallax', base),
               L('particles.snow_far', Particles('snow', count=120, seed=83, speed=1.3,
                                                 wind=0.6, size=(1, 2.6),
                                                 area=(0.55, 0.0, 0.45, 0.75)).draw(lt, 0.5))]
        if lt > 0.16:
            kc = ease(ramp(lt, 0.16, 0.58))
            out.append(L('annotation.circle',
                         draw_circle_annot(W * 0.50, H * 0.42, int(150 + 34 * kc),
                                           progress=kc, width=5)))
        return out

    shots.append(Shot('S5a_frost', 15.31, 17.50, [], s5a,
                      events=[(15.89, 'frost returns on the window glass', 'wind'),
                              (16.87, 'frost that should not be there: circled',
                               'paper_slide')], cam='push'))

    # ================= S5  17.50-20.36  the map, pulled back; the thread leaves west
    map_s5 = paper_map.copy()
    route_s5 = [(x - 30, y + 6) for x, y in route]
    scrap_west = paper_sheet(232, 98, seed=57, tone='parchment')
    scrap_west = drop_shadow(scrap_west, blur=12, off=(7, 9), alpha=155)
    _sd = ImageDraw.Draw(scrap_west)
    for _i in range(3):
        _sd.line([(30, 42 + _i * 18), (30 + 150 + (_i % 2) * 24, 44 + _i * 18)],
                 fill=(38, 35, 31, 208), width=3)

    def s5(t, fi, suppress=()):
        dx = int(-30 * ease(t / 2.86)); dy = int(6 * ease(t / 2.86))
        out = [L('plate.table', table_move(t + 2.4, 2.86)),
               L('particles.rain', Particles('rain', count=150, seed=53, speed=2.0,
                                             wind=0.4, opacity=0.55).draw(t, ramp(t, 0.2, 1.2))),
               L('map.sheet_on_plate',
                 sheet_on_frame(map_s5, MAP_O[0] + dx, MAP_O[1] + dy)),
               L('annotation.through', draw_thread(route_s5, ramp(t, 0.10, 1.35), width=7))]
        if t > 0.55:
            out.append(L('annotation.arrow', draw_arrow(
                (route_s5[0][0], route_s5[0][1]),
                (route_s5[0][0] - 340, route_s5[0][1] - 70),
                progress=ease(ramp(t, 0.55, 1.35)), width=5)))
        if t > 0.92:
            k2 = ease(ramp(t, 0.92, 1.28))
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            sx, sy = int(W * 0.055), int(H * 0.16 - 26 * (1 - k2))
            lay.alpha_composite(fade(scrap_west, k2), (sx, sy + 8))
            lay.alpha_composite(fade(pin_sprite(r=9, color='burgundy'), k2), (sx + 6, sy))
            out.append(L('prop.pin', lay))
        return out

    shots.append(Shot('S5_thread_exit', 17.50, 20.36, [], s5,
                      events=[(19.04, 'the secret was not in the continents', 'riser'),
                              (20.12, 'the thread leaves frame westward', 'thread_draw')],
                      cam='lateral'))

    # ================= S6  20.36-22.42  Sumbawa, and how far away it is
    p_sumb = Plate(os.path.join(SH, 'ch1_30_sumbawa_raw.png'), horizon=0.46)
    GW, GH = int(W * 0.42), int(H * 0.60)
    route_sheet = maps.make_map_sheet(GW, GH, 6.0, 20.0, 1.55, seed=93)
    SHEET_O = (int(W * 0.515), int(H * 0.115))
    arc_pts = [(x + SHEET_O[0], y + SHEET_O[1]) for x, y in
               maps.route_points([(116.4, -8.2), (100, 4), (79, 20), (60, 30), (33, 37),
                                  (10, 43), (-30, 45), (-62, 43)],
                                 'equirect', 6.0, 20.0, GW, GH, 1.55)]
    _isl = maps.project(116.4, -8.2, 'equirect', 6.0, 20.0, GW, GH, 1.55)
    ISL = (float(_isl[0]) + SHEET_O[0], float(_isl[1]) + SHEET_O[1])
    SUMMIT = (W * 0.615, H * 0.455)                 # the crater, on the photograph
    sky_pts = [(W * 0.615, H * 0.455), (W * 0.545, H * 0.505), (W * 0.455, H * 0.545),
               (W * 0.34, H * 0.575), (W * 0.21, H * 0.600), (W * 0.02, H * 0.628)]
    tag_km = tag('آلاف الكيلومترات', size=38, seed=25)

    def s6(t, fi, suppress=()):
        sheet_k = 1.0 - ease(ramp(t, 1.15, 1.62))
        zoom = 1.03 + 0.07 * ease(t / 2.06)
        base = grade_cold(p_sumb.frame(zoom=zoom, pan=(-0.05 + 0.07 * ease(t / 2.06),
                                                      -0.02 - 0.03 * ease(t / 2.06)),
                                       parallax=1.10), 0.62)
        dx = int(26 * math.sin(t * 0.75)); dy = int(-14 * ease(t / 2.06))
        sheet_lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        sxp = SHEET_O[0] + dx + int(300 * (1 - sheet_k))
        syp = SHEET_O[1] + dy + int(70 * (1 - sheet_k))
        sh = maps.shadow_of(route_sheet, at=(sxp, syp), blur=22, off=(16, 20), size=(W, H))
        sheet_lay.alpha_composite(fade(sh, sheet_k))
        sheet_lay.alpha_composite(fade(route_sheet, sheet_k), (sxp, syp))
        out = [L('plate.parallax', base),
               L('particles.dust', Particles('dust', count=170, seed=59, speed=1.0,
                                             wind=0.3, size=(2, 5), opacity=0.55,
                                             area=(0.55, 0.0, 0.45, 1.0)).draw(t, 0.85)),
               L('map.sheet_on_plate', sheet_lay)]
        kc = ease(ramp(t, 0.02, 0.46))
        mx = ISL[0] + (SUMMIT[0] - ISL[0]) * (1 - sheet_k)
        my = ISL[1] + (SUMMIT[1] - ISL[1]) * (1 - sheet_k)
        out.append(L('annotation.circle',
                     draw_circle_annot(mx, my, int(58 + 12 * kc), progress=kc, width=5)))
        out.append(L('annotation.thread',
                     draw_thread(arc_pts if sheet_k > 0.55 else sky_pts,
                                 ramp(t, 0.34, 1.58), width=6,
                                 alpha=int(235 * (0.45 + 0.55 * sheet_k)))))
        if t > 1.68:
            kp = ease(ramp(t, 1.68, 1.94))
            pl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            pn = pin_sprite(r=9, color='burgundy')
            pl.alpha_composite(fade(pn, kp), (int(mx - pn.width / 2),
                                              int(my - pn.width * 0.62)))
            out.append(L('prop.pin', pl))
        if t > 0.66 and 'prop.text' not in suppress:
            k = ease(ramp(t, 0.66, 0.94))
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            gx, gy = int(W * 0.035), int(H * 0.055)
            lay.alpha_composite(fade(tag_km['sprite'], k), (gx, gy))
            b = tag_km['box']
            out.append(L('prop.pinned_tag', lay, text='آلاف الكيلومترات',
                         box=(gx + b[0], gy + b[1], gx + b[2], gy + b[3]), k=k,
                         fg=hexrgb(COL['ink_deep'])))
        return out

    shots.append(Shot('S6_globe', 20.36, 22.42, [], s6,
                      events=[(20.36, 'thousands of kilometres away', 'pin'),
                              (21.42, 'the line lands on the far side', 'paper_slide')],
                      cam='drift'))

    # ================= S7  22.42-24.00  brand sting: the thread writes the mark
    MARK = 700
    mark_pts = [(x + W / 2 - MARK / 2, y + H / 2 - MARK / 2 - 80)
                for x, y in mark_path(size=MARK)]

    def s7(t, fi, suppress=()):
        out = [L('table.dark', canvas(COL['ink_deep']).convert('RGBA'))]
        tex = paper_sheet(W, H, seed=71, tone='ink_second')
        out.append(L('paper.texture', fade(tex, 0.5)))
        out.append(L('annotation.thread', draw_thread(mark_pts, ramp(t, 0.05, 1.15),
                                                      width=11,
                                                      color='gold' if t < 1.15
                                                      else 'gold_light')))
        if t > 1.02:
            kk = ease(ramp(t, 1.02, 1.40))
            dot = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            cx0 = W / 2
            cy0 = (H / 2 - MARK / 2 - 80) + MARK * 0.31 - MARK * 0.17 * 0.40
            r0 = MARK * 0.040
            ImageDraw.Draw(dot).ellipse([cx0 - r0, cy0 - r0, cx0 + r0, cy0 + r0],
                                        fill=hexrgb(COL['gold_light']) + (int(246 * kk),))
            out.append(L('brand.dot', dot))
        if t > 1.02 and 'prop.text' not in suppress:
            k = ease(ramp(t, 1.02, 1.45))
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(lay)
            f = font('amiri_bold', 92)
            tw = d.textbbox((0, 0), ar('رِواق'), font=f)[2]
            d.text((W / 2 - tw / 2, H / 2 + 250), ar('رِواق'), font=f,
                   fill=hexrgb(COL['parchment']) + (int(252 * k),))
            f2 = font('plex', 34)
            t2 = ar('تَارِيخْ وَتُرَاث')
            tw2 = d.textbbox((0, 0), t2, font=f2)[2]
            d.text((W / 2 - tw2 / 2, H / 2 + 356), t2, font=f2,
                   fill=hexrgb(COL['stone_light']) + (int(230 * k),))
            out.append(L('kinetic.wordmark', lay, text='رِواق',
                         box=(int(W / 2 - tw / 2), int(H / 2 + 258),
                              int(W / 2 + tw / 2), int(H / 2 + 250 + 92)),
                         fg=hexrgb(COL['parchment'])))
        return out

    shots.append(Shot('S7_sting', 22.42, 24.00, [], s7,
                      events=[(22.42, 'brand sting begins', 'sting'),
                              (23.10, 'the thread writes the mark', 'thread_draw')],
                      cam='hold'))

    # ================= S8  24.00-27.85  the most famous monster in literature
    p_mon = Plate(os.path.join(SH, 'ch1_29_alley_raw.png'), horizon=0.45)

    def _make_note():
        rng = np.random.default_rng(63)
        w, h = 330, 250
        sc = paper_sheet(w, h, seed=63, tone='parchment2')
        d = ImageDraw.Draw(sc)
        # a hand that reads as handwriting: wobbled baseline with ascenders
        for (y0, x1) in ((96, 250), (150, 214)):
            x = 34
            while x < x1 - 12:
                wd = int(rng.integers(9, 20))
                hh = int(rng.integers(9, 22)) if rng.random() > 0.45 else int(rng.integers(4, 8))
                wob = int(rng.integers(-3, 4))
                if rng.random() > 0.18:
                    d.line([(x, y0 + wob), (x, y0 - hh + wob)], fill=(44, 41, 36, 212), width=2)
                    d.line([(x, y0 - hh + wob), (x + wd - 3, y0 - hh + 3 + wob)],
                           fill=(44, 41, 36, 188), width=2)
                    d.line([(x + wd - 3, y0 - hh + 3 + wob), (x + wd, y0 - 1 + wob)],
                           fill=(44, 41, 36, 188), width=2)
                x += wd + int(rng.integers(4, 9))
        sc.alpha_composite(ink_blot(22, seed=65, color='burgundy'), (w - 74, h - 92))
        tpe = tape(w=86, h=30, seed=67).rotate(-9, expand=True, resample=Image.BICUBIC)
        sc.alpha_composite(tpe, (int(w * 0.5 - tpe.width / 2), -8))
        pn = pin_sprite(r=10, color='gold')
        sc.alpha_composite(pn, (int(w * 0.5 - pn.width / 2), -2))
        return drop_shadow(sc, blur=15, off=(10, 13), alpha=178)

    note = _make_note()
    mon_cap = Caption('أشهر وحش في الأدب', size=52, seed=91)

    def s8(t, fi, suppress=()):
        zoom = 1.04 + 0.07 * ease(t / 3.85)
        base = grade_cold(p_mon.frame(zoom=zoom, pan=(-0.12, -0.03), parallax=1.05), 0.66)
        out = [L('plate.parallax', base),
               L('particles.fog', Particles('dust', count=200, seed=61, speed=1.2, wind=0.25,
                                            size=(2, 5), opacity=0.5,
                                            area=(0.0, 0.45, 1.0, 0.55)).draw(t, 0.9))]
        if t > 0.3:
            k = ease(ramp(t, 0.30, 0.62))          # lands at 24.62 with the pin hit
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            lay.alpha_composite(fade(note, k),
                                (int(W * 0.545), int(H * 0.40 - 26 * (1 - k))))
            out.append(L('prop.note_scrap', lay))
        if t > 1.50 and 'prop.text' not in suppress:      # 25.50: «ولادة»
            kc = ease(ramp(t, 1.50, 1.86))
            out.append(mon_cap.layer(k=kc, xf=0.42, yf=0.795, rise=int(22 * (1 - kc))))
        return out

    shots.append(Shot('S8_monster', 24.00, 27.85, [], s8,
                      events=[(24.62, 'the note scrap is pinned to the frame', 'pin'),
                              (25.55, 'caption slip lands', 'paper_slide'),
                              (26.28, 'the most famous monster in literature', 'riser')],
                      cam='push'))

    # ================= S9  27.85-30.00  back to the field
    p_snow_m = Plate(os.path.join(SH, 'ch1_wheat_snow_mirror_raw.png'), horizon=0.40)

    def s9(t, fi, suppress=()):
        zoom = 1.16 - 0.07 * ease(t / 2.15)      # a tighter frame, the opposite move
        base = grade_cold(p_snow_m.frame(zoom=zoom, pan=(-0.04, 0.09), parallax=1.10), 0.5)
        return [L('plate.parallax', base),
                L('particles.snow', snow_a.draw(t + 3.3, intensity=0.6))]

    shots.append(Shot('S9_return', 27.85, 30.00, [], s9,
                      events=[(28.97, 'let us begin with', 'wind')], cam='pull'))

    return shots


TEXTS = []          # no light type over photographs: phrases are carried by paper


def events_table(shots):
    rows = []
    for s in shots:
        for (te, label, sfx) in s.events:
            rows.append(dict(t=round(te, 3), shot=s.name, event=label, sfx=sfx,
                             frame=int(round(te * FPS))))
    rows.sort(key=lambda r: r['t'])
    return rows


if __name__ == '__main__':
    for s in build_shots():
        print(f'  {s.name:16s} {s.t0:6.2f}-{s.t1:6.2f} {s.cam}')
    for r in events_table(build_shots()):
        print('  ev', r['t'], r['shot'], r['event'])
