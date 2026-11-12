#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch6v5.py — Chapter 6: three myths and what if it happened again. Lines 114-137,
film time 524.78 -> 626.37.

THE ARGUMENT
------------
Correction is not a hedge. Three sentences people repeat about 1816 are each wrong in a
specific way, and the difference between "probably" and "certainly" is what keeps the
story trustworthy. Then the same eruption, placed in a world that ships its food.

WHAT IS ON SCREEN
-----------------
  * the myths are SET TYPE, corrected line by line, with the correction labelled as the
    fact it is;
  * the world of today is real geography -- no globe, no network, no arrows;
  * the end card is the supplied logo, used as-is, never a redrawn word or arch.
"""
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, '/home/user/work')
sys.path.insert(0, '/home/user/Riwaq_System_Repo/episode/1816')

from eng5 import core5 as C
from ch3.eng import ekit5 as K

W, H = K.W, K.H
T0, T_END = 524.78, 626.37
CH_START_SEC, CH_END_SEC = T0, T_END
assert abs((CH_END_SEC - CH_START_SEC) - 101.59) < 0.05, 'chapter length must match the plan'

CREAM = K.CREAM
SU_LL = (115.5, -8.3)
WORLD_LL = (-20.0, 34.0)
HERO_IN, HERO_OUT = 616.69, 623.34

SHOTS = [
    ('S01_myths',  'gfx', 524.78, 559.00, 0.00, 1.0),
    ('S02_world',  'map', 559.00, 572.10, 0.00, 1.0),
    ('S03_linked', 'map', 572.10, 590.98, 0.00, 1.0),
    ('S04_watch',  'gfx', 590.98, 602.71, 0.00, 1.0),
    ('S05_ask',    'map', 602.71, 611.77, 0.00, 1.0),
    ('S06_hero',   'logo', 611.77, 624.05, 0.00, 1.0),
    ('S07_tease',  'map', 624.05, 626.37, 0.00, 1.0),
]
BY = {s[0]: s for s in SHOTS}
HARD = set()

ASH = C.Ash(n=300, speed=(18, 60), size=(1.0, 2.4), wind=-30.0, seed=83)


def shot_at(t):
    for s in SHOTS:
        if s[2] <= t < s[3]:
            return s
    return SHOTS[-1]


def shot_name(t):
    return shot_at(t)[0]


def _lt(t, name):
    return t - BY[name][2]


MYTHS = [
    # (myth in, fact in) -- each pair lands on its own spoken line
    (0.40, 4.40, ('خرافة أولانية', 'الصيف اختفى من كل الدنيا'),
     ('الحقيقة', 'اضطرابات كبيرة في مناطق')),
    (8.60, 13.20, ('خرافة تانية', 'كل يوم كان متجمّد'),
     ('الحقيقة', 'فترات متقطعة')),
    (17.90, 22.00, ('خرافة تالتة', 'بركان واحد هو السبب الوحيد'),
     ('الحقيقة', 'أكتر من عامل ساهم')),
]


def base_s01(t):
    """the three myths: each one rises like a page being turned, and is corrected in
    place. The card never sits under the corner lockup (y >= 196) and never leaves the
    frame while it is still being read."""
    lt = _lt(t, 'S01_myths')
    dur = BY['S01_myths'][3] - BY['S01_myths'][2]
    base = K.bed(6.4, 46.4, zoom=2.05 + 0.10 * K.ease(lt / dur), blur=12.0, dark=0.74)
    base = K.motes(base, t, density=0.10, colour=(198, 208, 220))
    base = K.vignette_a(base, 0.34)
    out = base
    _facts = []
    for i, (m_in, f_in, myth, fact) in enumerate(MYTHS):
        am = K.ramp(lt, m_in, m_in + 0.55)
        am *= 1.0 - K.ramp(lt, m_in + 3.2, m_in + 3.8)
        if am > 0.004:
            sp = K.glass_card([myth], size=40, accent=(226, 128, 112))
            rise = int(round(16 * (1.0 - K.ease(K.ramp(lt, m_in, m_in + 0.55)))))
            out = K.place(out, sp, 96, 196 + rise, a=am)
        # the correction does NOT leave: the three of them accumulate on the right, so
        # by the end of the sequence the frame holds the whole corrected picture
        af = K.ramp(lt, f_in, f_in + 0.55)
        if af > 0.004:
            newest = (i == max(j for j, m in enumerate(MYTHS) if lt >= m[1]))
            sp = K.glass_card([fact], size=40, accent=(150, 206, 168))
            _facts.append((i, sp, af * (1.0 if newest or lt < f_in + 0.9 else 0.62)))
    y_bot = H - 176
    for i, sp, a_ in sorted(_facts, key=lambda r: r[0]):
        y = y_bot - sp.height
        out = K.place(out, sp, W - sp.width - 96, y, a=a_)
        y_bot = y - 14
    sp = K.glass_card([('يُرجَّح', 'بدل أكيد'),
                       ('الفرق بسيط', 'بس هو اللي بيحفظ الثقة')],
                      title='علشان كده', size=38)
    return K.place(out, sp, 96, H - sp.height - 176,
                   a=K.ramp(lt, 27.1, 27.9) * (1 - K.ramp(lt, 31.0, 31.6)))


def base_s02(t):
    lt = _lt(t, 'S02_world')
    dur = BY['S02_world'][3] - BY['S02_world'][2]
    cam = K.Cam(-8.0, 30.0, zoom=2.05 + 0.45 * K.ease(lt / dur))
    base = K.grader(cam.apply(), warmth=0.80, sat=0.56).convert('RGBA')
    base = K.vignette_a(base, 0.26)
    sp = K.glass_card([('تقديرات', 'مش موعد'), ('ومش', 'نبوءة')],
                      title='حجم الخطر', size=38)
    return K.place(base, sp, W - sp.width - 96, 196, a=K.ramp(lt, 5.4, 6.2))


def base_s03(t):
    lt = _lt(t, 'S03_linked')
    dur = BY['S03_linked'][3] - BY['S03_linked'][2]
    cam = K.Cam(-10.0, 32.0, zoom=1.85 + 0.30 * K.ease(lt / dur))
    base = K.grader(cam.apply(), warmth=0.80, sat=0.54).convert('RGBA')
    base = K.vignette_a(base, 0.26)
    marks = [(0.5, (-60.0, 42.0), 'الأكل بيعبر قارات'),
             (8.4, (6.4, 46.4), 'والسما ممر')]
    out = base
    for t_in, ll, label in marks:
        a = K.ramp(lt, t_in, t_in + 0.7)
        if a <= 0.004:
            continue
        p = cam.to_screen(*ll)
        out = K.focus(out, p[0], p[1], r=230, amount=0.22 * a)
        C.pin(out, p[0], p[1], t, BY['S03_linked'][2] + t_in, r=9)
        out = K.map_label(out, label, p[0] - 90, p[1] - 78, a=a, size=36)
    sp = K.glass_card([('الطيران', 'وسلاسل الإمداد')], size=38)
    return K.place(out, sp, W - sp.width - 96, H - sp.height - 150,
                   a=K.ramp(lt, 3.2, 4.0))


def base_s04(t):
    lt = _lt(t, 'S04_watch')
    dur = BY['S04_watch'][3] - BY['S04_watch'][2]
    base = K.bed(6.4, 46.4, zoom=1.95 + 0.35 * K.ease(lt / dur), blur=15.0, dark=0.82)
    base = K.vignette_a(base, 0.32)
    out = base
    sp = K.glass_card([('إحنا النهارده', 'بنعرف نراقب السما')], title='الفرق',
                      size=40)
    out = K.place(out, sp, (W - sp.width) // 2, 196, a=K.ramp(lt, 4.1, 4.9))
    sp = K.glass_card([('الميعاد', 'محدش يعرفه'), ('الاستعداد', 'ده اللي في إيدنا')],
                      size=38)
    return K.place(out, sp, (W - sp.width) // 2, H - sp.height - 150,
                   a=K.ramp(lt, 8.2, 9.0))


def base_s05(t):
    lt = _lt(t, 'S05_ask')
    base = K.bed(-6.0, 34.0, zoom=1.85, blur=19.0, dark=0.74)
    base = K.vignette_a(base, 0.34)
    sp = K.glass_card([('لو حصل بكرة', 'إيه أول حاجة هتتأثر؟')], title='سؤال',
                      size=44)
    out = K.place(base, sp, (W - sp.width) // 2, 210, a=K.ramp(lt, 0.4, 1.1))
    sp2 = K.glass_card([('الأكل؟', 'الطيران؟'), ('الإنترنت؟', '')], size=42)
    return K.place(out, sp2, (W - sp2.width) // 2, H - sp2.height - 170,
                   a=K.ramp(lt, 5.0, 5.8))


def base_s06(t):
    """the end card: the supplied logo as-is, no redrawn word, no arch."""
    lt = _lt(t, 'S06_hero')
    dur = BY['S06_hero'][3] - BY['S06_hero'][2]
    base = K.bed(-6.0, 34.0, zoom=1.9, blur=22.0, dark=0.55)
    base = K.vignette_a(base, 0.44)
    a = min(K.ramp(lt, 0.10, 0.55), 1.0 - K.ramp(lt, dur - 0.55, dur))
    sc = 0.96 + 0.04 * K.ease(min(1.0, max(0.0, lt / 0.7)))
    out = C.hero_logo(base, 960, 470, width=420, scale=sc, alpha=a,
                      dim=0.45 * K.ramp(lt, 0.0, 0.6))
    sp = K.glass_card([('الحلقة الجاية', 'ثوران بلا اسم')], size=38)
    return K.place(out, sp, (W - sp.width) // 2, H - sp.height - 150,
                   a=K.ramp(lt, 2.6, 3.3))


def base_s07(t):
    lt = _lt(t, 'S07_tease')
    base = K.bed(-6.0, 34.0, zoom=2.0, blur=20.0, dark=0.42)
    base = K.vignette_a(base, 0.46)
    sp = K.glass_card([('اشترك', 'عشان يوصلك')], size=44)
    return K.place(base, sp, (W - sp.width) // 2, (H - sp.height) // 2,
                   a=K.ramp(lt, 0.0, 0.5))


BASE = {'S01_myths': base_s01, 'S02_world': base_s02, 'S03_linked': base_s03,
        'S04_watch': base_s04, 'S05_ask': base_s05, 'S06_hero': base_s06,
        'S07_tease': base_s07}


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
    if C.T() and not (HERO_IN - 0.6 <= t < HERO_OUT + 0.6):
        K.corner(base)
    out = C.finish(base.convert('RGB'), i % 240)
    if t > T_END - 0.75:
        out = C.fade_to_black(out, max(0.0, (T_END - t) / 0.75))
    return out


def plate_src(t):
    s = shot_at(t)
    name, key, t0, t1, ip, rate = s
    return (key, int(round((t - t0) * 30)), 0, 0.0)


def levels():
    return {s[0]: ['plate', 'grade', 'mine', 'cards', 'logo'] for s in SHOTS}


EVENTS = [
    dict(t=529.20, what='the first correction', sfx='paper_in'),
    dict(t=533.34, what='myth two', sfx='paper_in'),
    dict(t=542.61, what='myth three', sfx='paper_in'),
    dict(t=559.00, what="today's world", sfx='sting'),
    dict(t=602.71, what='the question', sfx='paper_in'),
    dict(t=616.69, what='the end card', sfx='sting'),
]
