#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch5v5.py — Chapter 5: the two monsters. Lines 93-113, film time 437.12 -> 524.78.

THE ARGUMENT
------------
One rainy night, one challenge, and two monsters walked out of it. Polidori wrote the
vampire. Mary wrote the name. Only one of them is still on everything.

WHAT IS ON SCREEN
-----------------
  * Polidori's street is plate 13 and the volcano on the page is plate 14;
  * the title page of 1818 is set as type on dark glass, not a photographed paper;
  * the chain of causes is a sequence of measured lines on glass -- a sentence spoken one
    link at a time, not a diagram.
"""
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, '/home/user/work')
sys.path.insert(0, '/home/user/Riwaq_System_Repo/episode/1816')

from eng5 import core5 as C
from ch3.eng import ekit5 as K

W, H = K.W, K.H
T0, T_END = 437.12, 524.78
CH_START_SEC, CH_END_SEC = T0, T_END
assert abs((CH_END_SEC - CH_START_SEC) - 87.66) < 0.05, 'chapter length must match the plan'

CREAM = K.CREAM
SU_LL = (115.5, -8.3)
CHAIN_LL = (-30.0, 40.0)

SHOTS = [
    ('S01_vampire', '13',  437.12, 455.56, 0.50, 1.0),
    ('S02_two',     'gfx', 455.56, 465.60, 0.00, 1.0),  # 'the name that won'
    ('S03_title',   'gfx', 465.60, 482.74, 0.00, 1.0),
    ('S04_name',    'gfx', 482.74, 496.00, 0.00, 1.0),
    ('S05_chain',   'map', 496.00, 508.35, 0.00, 1.0),
    ('S06_volcano', '14',  508.35, 511.67, 0.50, 1.0),
    ('S07_sub',     'gfx', 511.67, 524.78, 0.00, 1.0),
]
BY = {s[0]: s for s in SHOTS}
HARD = {'S01_vampire', 'S06_volcano'}

ASH = C.Ash(n=320, speed=(20, 70), size=(1.0, 2.6), wind=-34.0, seed=57)


def shot_at(t):
    for s in SHOTS:
        if s[2] <= t < s[3]:
            return s
    return SHOTS[-1]


def shot_name(t):
    return shot_at(t)[0]


def _lt(t, name):
    return t - BY[name][2]


# ---- 7:17.12  437.12  Polidori's street (plate 13)
def base_s01(t):
    lt = _lt(t, 'S01_vampire')
    dur = BY['S01_vampire'][3] - BY['S01_vampire'][2]
    z = 1.04 + 0.20 * K.ease(lt / dur)
    base = K.plate('13', 0.50 + lt * 0.78, z=z, pan=(0, 8 * (lt / dur)),
                   warmth=0.70, sat=0.54)
    base = K.motes(base, t, density=0.20, colour=(206, 216, 232))
    base = K.vignette_a(base, 0.34)
    a = np.asarray(base.convert('RGB'), np.float32)
    a *= 1.0 - 0.10 * K.ramp(lt, 2.0, dur)
    base = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    sp = K.glass_card([('ذا فامباير', '١٨١٩'), ('البطل', 'مصاص دم')],
                      title='بوليدوري', size=38)
    return K.place(base, sp, W - sp.width - 96, H - sp.height - 132,
                   a=K.ramp(lt, 0.8, 1.5))


# ---- 7:35.56  455.56  two monsters, one night
def base_s02(t):
    lt = _lt(t, 'S02_two')
    dur = BY['S02_two'][3] - BY['S02_two'][2]
    base = K.bed(6.4, 46.4, zoom=2.30 + 0.35 * K.ease(lt / dur), blur=13.0, dark=0.90)
    base = K.vignette_a(base, 0.30)
    sp = K.glass_card([('التحدي', 'خلّف وحشين'), ('مش', 'وحش واحد')],
                      title='النتيجة', size=40)
    return K.place(base, sp, (W - sp.width) // 2, H - sp.height - 140,
                   a=K.ramp(lt, 0.5, 1.2))


# ---- 7:45.60  465.60  the title page of 1818
def base_s03(t):
    lt = _lt(t, 'S03_title')
    dur = BY['S03_title'][3] - BY['S03_title'][2]
    base = K.bed(6.4, 46.4, zoom=2.10, blur=15.0, dark=0.86)
    base = K.vignette_a(base, 0.38)
    doc = gen_title_page()
    a = K.ramp(lt, 0.3, 1.1)
    # a slow drift so the page is not a pasted still
    dy = int(round(8 * K.ease(lt / dur)))
    return K.place_doc(base, doc, W / 2, H / 2 - 6 + dy, a=a)


# ---- 8:02.74  482.74  the name is the scientist's
def base_s04(t):
    lt = _lt(t, 'S04_name')
    dur = BY['S04_name'][3] - BY['S04_name'][2]
    base = K.bed(6.4, 46.4, zoom=2.05, blur=14.0, dark=0.88)
    base = K.vignette_a(base, 0.34)
    sp1 = K.glass_card([('اكتشاف', 'آخرون'), ('الاسم', 'في الرواية اسم العالِم')],
                       title='لكن', size=38)
    base = K.place(base, sp1, W - sp1.width - 96, 150, a=K.ramp(lt, 6.4, 7.2))
    sp2 = K.glass_card([('فرانكنشتاين', 'العالِم'), ('الكائن', 'من غير اسم')],
                       size=40)
    base = K.place(base, sp2, 96, H - sp2.height - 132, a=K.ramp(lt, 0.6, 1.3))
    sp3 = K.glass_card([('حلقاته', '١٨١٨')], size=38)
    return K.place(base, sp3, 96, 150, a=K.ramp(lt, 9.6, 10.3))


# ---- 8:16.00  496.00  the chain, one link at a time
def base_s05(t):
    lt = _lt(t, 'S05_chain')
    dur = BY['S05_chain'][3] - BY['S05_chain'][2]
    base = K.bed(18.0, 34.0, zoom=1.55, blur=18.0, dark=0.78)
    base = K.vignette_a(base, 0.30)
    # timed to the spoken chain: 491.38 explosion -> 496.39 cold summer, then the
    # rain / the house / the challenge / the vision in line 110
    links = [
        (0.0, 'انفجار', 'طبقة هباء'),
        (4.4, 'صيف بارد', ''),
        (5.3, 'مطر', 'وحبس في البيت'),
        (7.2, 'تحدي', 'ورؤية'),
    ]
    out = base
    y = 150
    for t_in, a_, b_ in links:
        al = K.ramp(lt, t_in, t_in + 0.55)
        if al > 0.004:
            sp = K.glass_card([(a_, b_)] if b_ else [a_], size=38)
            out = K.place(out, sp, 96, y, a=al)
            y += sp.height + 16
    sp = K.glass_card([('مش كل الحلقات', 'بنفس درجة اليقين'),
                       ('الخيط العام', 'موثّق')], title='بس', size=38)
    return K.place(out, sp, W - sp.width - 96, H - sp.height - 132,
                   a=K.ramp(lt, 8.4, 9.2))


# ---- 8:28.35  508.35  volcano in Indonesia (plate 14)
def base_s06(t):
    lt = _lt(t, 'S06_volcano')
    dur = BY['S06_volcano'][3] - BY['S06_volcano'][2]
    z = 1.05 + 0.14 * K.ease(lt / dur)
    base = K.plate('14', 0.50 + lt * 0.90, z=z, warmth=0.80, sat=0.60)
    base = ASH.draw(base, t, density=0.42)
    base = K.vignette_a(base, 0.30)
    sp = K.glass_card([('بركان', 'في إندونيسيا'), ('ووحش', 'على ورقة')],
                      size=40)
    return K.place(base, sp, W - sp.width - 96, H - sp.height - 132,
                   a=K.ramp(lt, 0.3, 0.9))


# ---- 8:31.67  511.67  the subscribe break
def base_s07(t):
    lt = _lt(t, 'S07_sub')
    dur = BY['S07_sub'][3] - BY['S07_sub'][2]
    base = K.bed(6.4, 46.4, zoom=2.20 + 0.5 * K.ease(lt / dur), blur=13.0,
                 dark=0.88)
    base = K.vignette_a(base, 0.44)
    sp = K.glass_card([('لو الحكاية دي', 'فتحت لك سؤال'),
                       ('اشترك', 'دلوقتي')], title='رِواق', size=44)
    return K.place(base, sp, (W - sp.width) // 2, (H - sp.height) // 2,
                   a=K.ramp(lt, 0.5, 1.2))


_G = {}


def gen_title_page():
    """1818 title page as type on smoked glass."""
    if 'd' in _G:
        return _G['d']
    w, h = 900, 700
    im = K.doc_paper(w, h, seed=71)
    d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle([30, 30, w - 30, h - 30], outline=(198, 162, 96, 70), width=1)
    lines = [
        ('فرانكنشتاين', 58, (240, 198, 118), 'Amiri-Bold.ttf'),
        ('أو', 40, (196, 206, 214), 'Amiri-Regular.ttf'),
        ('بروميثيوس الحديث', 48, (240, 232, 214), 'Amiri-Regular.ttf'),
        ('', 30, None, None),
        ('نُشرت أول مرة سنة ١٨١٨', 34, (196, 206, 214), 'Amiri-Regular.ttf'),
        ('', 26, None, None),
        ('والاسم اسم العالِم', 36, CREAM, 'Amiri-Bold.ttf'),
        ('مش اسم الكائن', 44, (240, 198, 118), 'Amiri-Bold.ttf'),
    ]
    y = 90
    for text, size, fill, fname in lines:
        if text:
            sp = C.text_sprite(text, size=size, fill=fill, fname=fname)
            im.alpha_composite(sp, ((w - sp.width) // 2, y))
        y += int(size * 1.55)
    _G['d'] = im
    return im


BASE = {'S01_vampire': base_s01, 'S02_two': base_s02, 'S03_title': base_s03,
        'S04_name': base_s04, 'S05_chain': base_s05, 'S06_volcano': base_s06,
        'S07_sub': base_s07}


def blend_frame(i, t):
    cur = shot_at(t)
    base = BASE[cur[0]](t)
    idx = SHOTS.index(cur)
    if idx > 0:
        prev = SHOTS[idx - 1]
        tb = cur[2]
        hw = 0.0 if cur[0] in HARD else 0.42
        if hw and tb - hw / 2 <= t < tb + hw / 2:
            base = C.dissolve(BASE[prev[0]](t).convert('RGB'), base.convert('RGB'),
                              K.ramp(t, tb - hw / 2, tb + hw / 2)).convert('RGBA')
    return base.convert('RGBA')


def frame_at(t):
    i = int(round(t * 30))
    K.PLACED.clear()
    base = blend_frame(i, t)
    if C.T():
        K.corner(base)
    out = C.finish(base.convert('RGB'), i % 240)
    if t > T_END - 0.55:
        out = C.fade_to_black(out, max(0.0, (T_END - t) / 0.55))
    return out


def plate_src(t):
    s = shot_at(t)
    name, key, t0, t1, ip, rate = s
    if key in ('map', 'gfx'):
        return (key, int(round((t - t0) * 30)), 0, 0.0)
    K.plates(key)
    p = K._PL[key]
    return (key, p.idx(ip + (t - t0) * rate), p.n, p.bsf)


def levels():
    return {s[0]: ['plate', 'grade', 'cards', 'logo'] for s in SHOTS}


EVENTS = [
    dict(t=437.12, what='hard cut to Polidori street', sfx='sting'),
    dict(t=465.60, what='the title page', sfx='paper_in'),
    dict(t=496.00, what='the chain begins', sfx='pin'),
    dict(t=508.35, what='the volcano', sfx='thunder'),
    dict(t=511.67, what='the subscribe card', sfx='sting'),
]
