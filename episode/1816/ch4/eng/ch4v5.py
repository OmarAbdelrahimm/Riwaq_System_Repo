#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch4v5.py — Chapter 4: the villa by the lake. Lines 75-92, film time 342.63 -> 437.12.

THE ARGUMENT
------------
The strangest consequence of the cold was not in a field. It was in a room: rain that kept
four writers indoors, a challenge to pass the time, and a vision a girl had with her eyes
closed.

WHAT IS ON SCREEN
-----------------
  * Lake Geneva is real geography; the villa is the delivered plate 09, and the writers at
    the table are plate 10;
  * Mary's and Byron's own words are DOCUMENTS -- paper with real lettering, not a card
    quoting a paragraph;
  * the blank page is plate 11, the laboratory vision is plate 12.
"""
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, '/home/user/work')
sys.path.insert(0, '/home/user/Riwaq_System_Repo/episode/1816')

from eng5 import core5 as C
from ch3.eng import ekit5 as K

W, H = K.W, K.H
T0, T_END = 342.63, 437.12
CH_START_SEC, CH_END_SEC = T0, T_END

CREAM = K.CREAM
LAKE_LL = (6.55, 46.45)

SHOTS = [
    ('S01_lake',    'map', 342.63, 352.20, 0.00, 1.0),
    ('S02_villa',   '09',  352.20, 363.75, 0.60, 1.0),
    ('S03_writers', '10',  363.75, 382.21, 0.50, 1.0),
    ('S04_quote',   'gfx', 382.21, 395.00, 0.00, 1.0),
    ('S05_challenge', 'gfx', 395.00, 411.25, 0.00, 1.0),
    ('S06_page',    '11',  411.25, 417.78, 0.40, 1.0),
    ('S07_vision',  '12',  417.78, 427.33, 0.50, 1.0),
    ('S08_name',    'gfx', 427.33, 437.12, 0.00, 1.0),
]
BY = {s[0]: s for s in SHOTS}
HARD = {'S02_villa', 'S06_page', 'S07_vision'}

RAIN = C.Rain(n=420, speed=(1200, 1900), length=(30, 66), slant=0.22, seed=9,
              alpha=(46, 120))


def shot_at(t):
    for s in SHOTS:
        if s[2] <= t < s[3]:
            return s
    return SHOTS[-1]


def shot_name(t):
    return shot_at(t)[0]


def _lt(t, name):
    return t - BY[name][2]


# ---- 5:42.63  342.63  the lake, and the villa on its shore
def base_s01(t):
    lt = _lt(t, 'S01_lake')
    dur = BY['S01_lake'][3] - BY['S01_lake'][2]
    u = K.ease(lt / dur)
    cam = K.Cam(LAKE_LL[0] + 6 - 6 * u, LAKE_LL[1] + 4 - 4 * u, zoom=5.2 + 2.4 * u)
    base = K.grader(cam.apply(), warmth=0.82, sat=0.60).convert('RGBA')
    p = cam.to_screen(*LAKE_LL)
    base = K.focus(base, p[0], p[1], r=250, amount=0.24 * K.ramp(lt, 0.3, 1.5))
    C.pin(base, p[0], p[1], t, 343.20, r=10)
    base = K.map_label(base, 'بحيرة جنيف', p[0] - 80, p[1] - 84,
                       a=K.ramp(lt, 0.5, 1.2), size=38)
    sp = K.glass_card([('سويسرا', '١٨١٦')], title='الصيف', size=40)
    return K.place(base, sp, W - sp.width - 96, 150, a=K.ramp(lt, 1.0, 1.7))


# ---- 5:52.20  352.20  Villa Diodati in the storm (plate 09)
def base_s02(t):
    lt = _lt(t, 'S02_villa')
    dur = BY['S02_villa'][3] - BY['S02_villa'][2]
    z = 1.02 + 0.16 * K.ease(lt / dur)
    base = K.plate('09', 0.60 + lt * 0.88, z=z, warmth=0.74, sat=0.58)
    base = RAIN.draw(base, t, density=0.30 + 0.20 * K.ramp(lt, 0.5, dur))
    base = K.vignette_a(base, 0.30)
    sp = K.glass_card([('فيلا ديوداتي', 'كولوني — جنيف'),
                       ('الجو', 'مطر وشبورة')], title='المكان', size=36)
    return K.place(base, sp, 96, H - sp.height - 132, a=K.ramp(lt, 1.2, 1.9))


# ---- 6:03.75  363.75  the writers round the candles (plate 10)
def base_s03(t):
    lt = _lt(t, 'S03_writers')
    dur = BY['S03_writers'][3] - BY['S03_writers'][2]
    z = 1.03 + 0.12 * K.ease(lt / dur)
    base = K.plate('10', 0.50 + lt * 0.80, z=z, pan=(0, 6 * (lt / dur)),
                   warmth=1.10, sat=0.72)
    base = K.motes(base, t, density=0.16, colour=(240, 214, 168))
    base = K.vignette_a(base, 0.26)
    sp = K.glass_card([('بايرون', 'وماري'), ('بيرسي شيلي', 'وبوليدوري')],
                      title='اللي قاعدين', size=36)
    return K.place(base, sp, W - sp.width - 96, H - sp.height - 132,
                   a=K.ramp(lt, 1.4, 2.1))


# ---- 6:22.21  382.21  their own words, on paper
def base_s04(t):
    lt = _lt(t, 'S04_quote')
    base = K.grader(K.Cam(6.5, 46.4, zoom=2.4).apply(), warmth=0.84, sat=0.56)
    base = base.convert('RGBA')
    base = K.vignette_a(base, 0.34)
    doc = gen_quotes()
    return K.place_doc(base, doc, W / 2, H / 2 - 6, a=K.ramp(lt, 0.3, 1.1))


# ---- 6:35.00  395.00  the challenge: one ghost story each
def base_s05(t):
    lt = _lt(t, 'S05_challenge')
    dur = BY['S05_challenge'][3] - BY['S05_challenge'][2]
    base = K.grader(K.Cam(6.5, 46.4, zoom=2.05).apply(), warmth=0.86, sat=0.58)
    base = base.convert('RGBA')
    rows = [(0.4, [('التحدي', 'حكاية رعب من كل واحد')]),
            (3.2, [('القراءة', 'حكايات ألمانية مترجمة')]),
            (6.6, [('ماري', 'لسه ما لقيتش فكرة')]),
            (10.0, [('المقدمة', 'كتبتها سنة ١٨٣١')])]
    out = base
    y = 150
    for t_in, rows_ in rows:
        a = K.ramp(lt, t_in, t_in + 0.6)
        a *= 1.0 - K.ramp(lt, t_in + 3.4, t_in + 4.0)
        if a > 0.004:
            sp = K.glass_card(rows_, size=38)
            out = K.place(out, sp, W - sp.width - 96, y, a=a)
            y += sp.height + 20
    return out


# ---- 6:51.25  411.25  the blank page (plate 11)
def base_s06(t):
    lt = _lt(t, 'S06_page')
    dur = BY['S06_page'][3] - BY['S06_page'][2]
    z = 1.04 + 0.14 * K.ease(lt / dur)
    base = K.plate('11', 0.40 + lt * 0.86, z=z, pan=(-14 * (lt / dur), 0),
                   warmth=1.02, sat=0.66)
    base = K.motes(base, t, density=0.14, colour=(236, 214, 176))
    base = K.vignette_a(base, 0.28)
    sp = K.glass_card([('ماري شيلي', 'والورقة البيضاء')], size=38)
    return K.place(base, sp, 96, H - sp.height - 132, a=K.ramp(lt, 0.9, 1.6))


# ---- 6:57.78  417.78  the vision: the pale student (plate 12)
def base_s07(t):
    lt = _lt(t, 'S07_vision')
    dur = BY['S07_vision'][3] - BY['S07_vision'][2]
    z = 1.05 + 0.16 * K.ease(lt / dur)
    base = K.plate('12', 0.50 + lt * 0.82, z=z, warmth=0.72, sat=0.50)
    base = K.vignette_a(base, 0.38)
    sp = K.glass_card([('طالب شاحب', 'بيدرس علوم غريبة'),
                       ('والحاجة', 'بدأت تتحرك')], title='الرؤية', size=36)
    return K.place(base, sp, W - sp.width - 96, 150, a=K.ramp(lt, 1.2, 1.9))


# ---- 7:07.33  427.33  the name
def base_s08(t):
    lt = _lt(t, 'S08_name')
    dur = BY['S08_name'][3] - BY['S08_name'][2]
    u = K.ease(lt / dur)
    base = K.grader(K.Cam(6.6, 46.5, zoom=3.0 + 1.2 * u).apply(), warmth=0.80,
                    sat=0.50).convert('RGBA')
    base = K.vignette_a(base, 0.36)
    sp = K.glass_card([('اسم العالِم', 'فرانكنشتاين'), ('مش', 'الكائن')],
                      title='فرانكنشتاين', size=42)
    return K.place(base, sp, (W - sp.width) // 2, H - sp.height - 140,
                   a=K.ramp(lt, 1.0, 1.8))


_G = {}


def gen_quotes():
    if 'd' in _G:
        return _G['d']
    w, h = 1180, 646
    im = K.doc_paper(w, h, seed=53)
    d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle([22, 22, w - 22, h - 22], outline=(198, 162, 96, 60), width=1)
    sp = C.text_sprite('من مقدمة ماري شيلي — ١٨٣١', size=38, fill=(240, 198, 118),
                       fname='Amiri-Bold.ttf')
    im.alpha_composite(sp, ((w - sp.width) // 2, 40))
    d.line([(96, 110), (w - 96, 110)], fill=(198, 162, 96, 96), width=2)
    lines = ['«كان صيفًا مبلولًا ومش لطيف،',
             'والمطر المتواصل حبسنا في البيت أيام.»',
             '',
             'وكتب بايرون عن الجو:',
             '«شبورة، وضباب، ومطر.»',
             '',
             'وفي يوم قال جملة واحدة:',
             '«كل واحد يكتب حكاية.»']
    y = 150
    for line in lines:
        if line:
            K.doc_text(im, 80, y, line, size=32, fill=CREAM)
        y += 58
    _G['d'] = im
    return im


BASE = {'S01_lake': base_s01, 'S02_villa': base_s02, 'S03_writers': base_s03,
        'S04_quote': base_s04, 'S05_challenge': base_s05, 'S06_page': base_s06,
        'S07_vision': base_s07, 'S08_name': base_s08}


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
    return {s[0]: ['plate', 'grade', 'rain', 'cards', 'logo'] for s in SHOTS}


EVENTS = [
    dict(t=343.20, what='Geneva pinned', sfx='pin'),
    dict(t=352.20, what='hard cut to the villa storm', sfx='thunder'),
    dict(t=363.75, what='the table', sfx='paper_in'),
    dict(t=382.21, what='their words on paper', sfx='paper_in'),
    dict(t=411.25, what='the blank page', sfx='paper_in'),
    dict(t=417.78, what='the vision', sfx='sting'),
]
