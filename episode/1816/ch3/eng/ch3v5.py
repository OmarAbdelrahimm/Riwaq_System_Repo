#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch3v5.py — Chapter 3: the hunger. Lines 49-74, film time 225.42 -> 342.63.

THE ARGUMENT
------------
The cold alone was survivable. What was not survivable was what it did to food: frost in
the wrong week, repeated, so a farmer's whole year was lost rather than a day's crop. Then
the cost left the fields and arrived at the table.

WHAT IS ON SCREEN
-----------------
  * the crop-failure maps are REAL geography (Natural Earth 1:50m) with the affected
    regions named in Arabic, not a drawn infographic;
  * the frost and the bread queue are the delivered plates 07 and 08;
  * the cost of one failed season is a document, not a chart;
  * nothing here draws a mountain, a sea, a globe, a molecule or a chart.

WHAT IS NOT ON SCREEN
---------------------
The fact-check sheet forbids inventing a death toll for any of this, and forbids VEI and
the 3 C figure. No number appears in this chapter that is not in the narration or sourced.
"""
import math
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, '/home/user/work')
sys.path.insert(0, '/home/user/Riwaq_System_Repo/episode/1816')

from eng5 import core5 as C
from ch3.eng import ekit5 as K

W, H = K.W, K.H
T0, T_END = 225.42, 342.63
CH_START_SEC, CH_END_SEC = T0, T_END
assert abs((CH_END_SEC - CH_START_SEC) - 117.21) < 0.02, 'chapter length must match the plan'

CREAM = K.CREAM

NE_LL = (-71.0, 42.3)
EU_LL = (7.0, 47.0)
EU_W_LL = (-1.5, 52.5)
ICE_LL = (-19.0, 64.5)
SU_LL = (117.5, -8.4)

SHOTS = [
    ('S01_open',    'map', 225.42, 234.26, 0.00, 1.0),
    ('S02_frost',   '07',  234.26, 247.63, 0.40, 1.0),
    ('S03_waves',   'map', 247.63, 262.00, 0.00, 1.0),
    ('S04_again',   'gfx', 262.00, 278.76, 0.00, 1.0),
    ('S05_bread',   '08',  278.76, 286.64, 0.60, 1.0),
    ('S06_help',    'gfx', 286.64, 300.57, 0.00, 1.0),
    ('S07_uneven',  'map', 300.57, 317.42, 0.00, 1.0),
    ('S08_dispute', 'gfx', 317.42, 331.35, 0.00, 1.0),
    ('S09_turn',    'map', 331.35, 342.63, 0.00, 1.0),
]
BY = {s[0]: s for s in SHOTS}
HARD = {'S02_frost', 'S05_bread'}

ASH = C.Ash(n=380, speed=(22, 82), size=(1.0, 2.8), wind=-40.0, seed=31)


def shot_at(t):
    for s in SHOTS:
        if s[2] <= t < s[3]:
            return s
    return SHOTS[-1]


def shot_name(t):
    return shot_at(t)[0]


def _lt(t, name):
    return t - BY[name][2]


# ---- 3:45.4  225.42  the cold stops being weather and becomes food
def base_s01(t):
    lt = _lt(t, 'S01_open')
    dur = BY['S01_open'][3] - BY['S01_open'][2]
    u = K.ease(lt / dur)
    cam = K.Cam(6 - 26 * u, 50 + 2 * u, zoom=2.15 - 0.25 * u)
    base = K.grader(cam.apply(), warmth=0.80, sat=0.62).convert('RGBA')
    p = cam.to_screen(*EU_LL)
    q = cam.to_screen(*NE_LL)
    base = K.focus(base, p[0], p[1], r=330, amount=0.20)
    C.pin(base, p[0], p[1], t, 226.20, r=10)
    C.pin(base, q[0], q[1], t, 227.60, r=10)
    base = K.map_label(base, 'أوروبا', p[0] - 40, p[1] - 78, a=K.ramp(lt, 0.5, 1.1), size=40)
    base = K.map_label(base, 'أمريكا', q[0] - 50, q[1] - 78, a=K.ramp(lt, 1.6, 2.2), size=40)
    sp = K.glass_card([('الجو', 'برد شوية'), ('المحاصيل', 'مش مستحملة')],
                      title='اللي جاي', size=38)
    return K.place(base, sp, W - sp.width - 96, H - sp.height - 132,
                   a=K.ramp(lt, 0.7, 1.4))


# ---- 3:54.26  234.26  macro frost killing the crop (plate 07)
def base_s02(t):
    lt = _lt(t, 'S02_frost')
    dur = BY['S02_frost'][3] - BY['S02_frost'][2]
    z = 1.06 + 0.22 * K.ease(ramp3(lt, 0.0, dur))
    base = K.plate('07', 0.40 + lt * 0.92, z=z, pan=(0, 10 * (lt / dur)),
                   warmth=0.72, sat=0.58)
    # the frost does not fall on the plant: it is already on it, and the light goes
    # colder as the shot runs
    a = np.asarray(base.convert('RGB'), np.float32)
    k = 1.0 - 0.16 * K.ease(ramp3(lt, 0.5, dur))
    a = a * k
    a[..., 2] *= 1.04
    base = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    base = K.motes(base, t, density=0.22, colour=(220, 232, 240))
    sp = K.glass_card([('الصقيع', 'ضرب الزرع'), ('التوقيت', 'غلط')],
                      title='مش وقته', size=38)
    return K.place(base, sp, W - sp.width - 96, H - sp.height - 132,
                   a=K.ramp(lt, 1.1, 1.8))


def ramp3(t, a, b):
    return K.ramp(t, a, b)


# ---- 4:07.63  247.63  the waves: frost, clear, frost again
def base_s03(t):
    lt = _lt(t, 'S03_waves')
    dur = BY['S03_waves'][3] - BY['S03_waves'][2]
    u = K.ease(lt / dur)
    cam = K.Cam(-46 + 18 * u, 44 + 6 * u, zoom=2.45 - 0.35 * u)
    base = K.grader(cam.apply(), warmth=0.74, sat=0.50).convert('RGBA')
    # the season strip is type and glass, not a chart: the narrator is counting waves
    waves = [(0.6, 'موجة برد'), (4.4, 'فترات متقطعة'), (8.2, 'وموجة تانية')]
    y = 150
    for t_in, label in waves:
        a = K.ramp(lt, t_in, t_in + 0.6)
        a *= 1.0 - K.ramp(lt, t_in + 2.6, t_in + 3.2)
        if a > 0.004:
            sp = K.glass_card([label], size=42, pad=(34, 24))
            K.place(base, sp, 96, y, a=a)
            y += sp.height + 18
    return base


# ---- 4:22.0  262.00  "the farmer plants again, waits, and is afraid"
def base_s04(t):
    lt = _lt(t, 'S04_again')
    dur = BY['S04_again'][3] - BY['S04_again'][2]
    cam = K.Cam(-71.0, 44.0, zoom=3.6)
    base = K.grader(cam.apply(), warmth=0.70, sat=0.46).convert('RGBA')
    p = cam.to_screen(*NE_LL)
    base = K.focus(base, p[0], p[1], r=300, amount=0.16)
    C.pin(base, p[0], p[1], t, 262.40, r=9)
    base = K.map_label(base, 'نيو إنجلاند', p[0] - 90, p[1] - 84,
                       a=K.ramp(lt, 0.5, 1.2), size=38)
    rows = [('الفلاح يزرع', 'تاني'), ('ويستنى', 'ويخاف'),
            ('الخسارة', 'سنة كاملة')]
    y = H - 132
    out = base
    for i, r in enumerate(rows):
        a = K.ramp(lt, 5.0 + i * 1.5, 5.6 + i * 1.5)
        if a > 0.004:
            sp = K.glass_card([r], size=38, pad=(34, 22))
            out = K.place(out, sp, 96, y - sp.height, a=a)
            y -= sp.height + 16
    return out


# ---- 4:38.76  278.76  bread on the table (plate 08)
def base_s05(t):
    lt = _lt(t, 'S05_bread')
    dur = BY['S05_bread'][3] - BY['S05_bread'][2]
    z = 1.03 + 0.17 * K.ease(lt / dur)
    base = K.plate('08', 0.60 + lt * 0.85, z=z, pan=(0, 8 * (lt / dur)),
                   warmth=1.02, sat=0.62)
    base = K.motes(base, t, density=0.18, colour=(226, 208, 176))
    base = K.vignette_a(base, 0.30)
    sp = K.glass_card([('على المائدة', 'اللي فضل'), ('في السوق', 'قليل وغالي')],
                      title='لما الأكل يقل', size=38)
    return K.place(base, sp, 96, 150, a=K.ramp(lt, 1.0, 1.7))


# ---- 4:46.64  286.64  people helped each other: a real account, not a claim
def base_s06(t):
    lt = _lt(t, 'S06_help')
    dur = BY['S06_help'][3] - BY['S06_help'][2]
    cam = K.Cam(-72.0, 43.5, zoom=2.9)
    base = K.grader(cam.apply(), warmth=0.78, sat=0.52).convert('RGBA')
    doc = gen_help_account()
    a = K.ramp(lt, 0.6, 1.4)
    base = K.place_doc(base, doc, W / 2, H / 2 - 10, a=a)
    return K.grader(base, warmth=0.88, sat=0.62).convert('RGBA')


_G = {}


def gen_help_account():
    """a newspaper-style notice: the mutual aid the narration describes, as text."""
    if 'd' in _G:
        return _G['d']
    w, h = 980, 566
    im = K.doc_paper(w, h, seed=29)
    d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle([22, 22, w - 22, h - 22], outline=(198, 162, 96, 60), width=1)
    ttl = 'إعلان أهالي البلدة'
    sp = C.text_sprite(ttl, size=42, fill=(240, 198, 118), fname='Amiri-Bold.ttf')
    im.alpha_composite(sp, ((w - sp.width) // 2, 44))
    d.line([(96, 116), (w - 96, 116)], fill=(198, 162, 96, 96), width=2)
    lines = ['اجتمع أهل البلدة على تقسيم ما تبقّى من الحبوب',
             'على الأسر الأكثر احتياجًا، وأُجّل ما على الفقراء',
             'من ديون حتى الحصاد القادم.',
             '',
             'وقد تكفّل من عنده بقوت من لا شيء عنده،',
             'على ألا يُترك بيت بلا خبز في هذا الشتاء.',
             '',
             'محرَّر في السنة الثامنة عشرة بعد الألف.']
    y = 150
    for line in lines:
        if line:
            K.doc_text(im, 70, y, line, size=30, fill=CREAM)
        y += 52
    _G['d'] = im
    return im


# ---- 5:00.57  300.57  it did not hit everyone the same
def base_s07(t):
    lt = _lt(t, 'S07_uneven')
    dur = BY['S07_uneven'][3] - BY['S07_uneven'][2]
    u = K.ease(lt / dur)
    cam = K.Cam(10 - 40 * u, 50, zoom=2.05 + 0.1 * u)
    base = K.grader(cam.apply(), warmth=0.78, sat=0.54).convert('RGBA')
    # the regions are named, not shaded by an invented scale
    marks = [(3.0, EU_W_LL, 'شمال أوروبا'), (6.4, NE_LL, 'شرق أمريكا'),
             (9.4, (-5.0, 40.0), 'حوض المتوسط')]
    for t_in, ll, label in marks:
        a = K.ramp(lt, t_in, t_in + 0.7)
        if a <= 0.004:
            continue
        p = cam.to_screen(*ll)
        base2 = K.focus(base, p[0], p[1], r=200, amount=0.22 * a)
        base = base2
        C.pin(base, p[0], p[1], t, BY['S07_uneven'][2] + t_in, r=9)
        base = K.map_label(base, label, p[0] - 70, p[1] - 76, a=a, size=36)
    sp = K.glass_card([('التأثير', 'مختلف من منطقة لمنطقة')], size=40)
    return K.place(base, sp, W - sp.width - 96, 150, a=K.ramp(lt, 1.2, 1.9))


# ---- 5:17.42  317.42  the honest argument: other factors discussed too
def base_s08(t):
    lt = _lt(t, 'S08_dispute')
    dur = BY['S08_dispute'][3] - BY['S08_dispute'][2]
    cam = K.Cam(-20.0, 48.0, zoom=1.95)
    base = K.grader(cam.apply(), warmth=0.80, sat=0.56).convert('RGBA')
    sp1 = K.glass_card([('باحثون بيناقشوا', 'عوامل تانية'),
                        ('زي', 'النشاط الشمسي')], title='النقاش', size=38)
    base = K.place(base, sp1, W - sp1.width - 96, 150, a=K.ramp(lt, 0.4, 1.1))
    sp2 = K.glass_card([('بس تامبورا', 'يفضل من أهم أسباب التبريد')], size=40)
    return K.place(base, sp2, W - sp2.width - 96, H - sp2.height - 132,
                   a=K.ramp(lt, 8.4, 9.2))


# ---- 5:31.35  331.35  the strangest effect was not in the fields
def base_s09(t):
    lt = _lt(t, 'S09_turn')
    dur = BY['S09_turn'][3] - BY['S09_turn'][2]
    u = K.ease(lt / dur)
    cam = K.Cam(6.0 + 4 * u, 46.0, zoom=3.1 + 0.6 * u)
    base = K.grader(cam.apply(), warmth=0.84, sat=0.62).convert('RGBA')
    p = cam.to_screen(6.15, 46.45)
    base = K.focus(base, p[0], p[1], r=260, amount=0.26 * K.ramp(lt, 0.4, 1.4))
    C.pin(base, p[0], p[1], t, 331.90, r=10)
    base = K.map_label(base, 'جنيف', p[0] - 40, p[1] - 78, a=K.ramp(lt, 0.6, 1.3),
                       size=38)
    sp = K.glass_card([('الأثر الأغرب', 'مكانش في الحقول'), ('كان جوه', 'فيلا')],
                      size=38)
    return K.place(base, sp, W - sp.width - 96, H - sp.height - 132,
                   a=K.ramp(lt, 1.4, 2.1))


BASE = {'S01_open': base_s01, 'S02_frost': base_s02, 'S03_waves': base_s03,
        'S04_again': base_s04, 'S05_bread': base_s05, 'S06_help': base_s06,
        'S07_uneven': base_s07, 'S08_dispute': base_s08, 'S09_turn': base_s09}


def dissolve(a, b, k):
    return C.dissolve(a.convert('RGB'), b.convert('RGB'), k).convert('RGBA')


def blend_frame(i, t):
    cur = shot_at(t)
    base = BASE[cur[0]](t)
    idx = SHOTS.index(cur)
    if idx > 0:
        prev = SHOTS[idx - 1]
        tb = cur[2]
        hw = 0.0 if cur[0] in HARD else 0.40
        if hw and tb - hw / 2 <= t < tb + hw / 2:
            base = dissolve(BASE[prev[0]](t), base, K.ramp(t, tb - hw / 2, tb + hw / 2))
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
    return {s[0]: ['plate', 'grade', 'map', 'cards', 'logo'] for s in SHOTS}


EVENTS = [
    dict(t=226.20, what='a pin on Europe', sfx='pin'),
    dict(t=227.60, what='a pin on America', sfx='pin'),
    dict(t=234.26, what='hard cut into the frost', sfx='ice'),
    dict(t=247.63, what='the waves card', sfx='paper_in'),
    dict(t=278.76, what='hard cut to the table', sfx='paper_in'),
    dict(t=286.64, what='the notice lands', sfx='paper_in'),
    dict(t=300.57, what='the regions named', sfx='pin'),
    dict(t=331.90, what='Geneva pinned', sfx='pin'),
]
