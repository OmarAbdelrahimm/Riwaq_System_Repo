#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
assemble.py — Chapter 1 paper cut, built on the absolute frame timeline.

Two things a naive concat gets wrong, both handled here:
 1. SHOT_LIST_v2.2 leaves intentional gaps between shots (narration pauses,
    0.36-1.38 s, 14.70 s total). Concatenating shot durations collapses them and
    the picture runs ahead of the voice. So the cut is built as frames:
    F(t) = round(t * 30) and every segment owns [F(t_in), F(t_end)).
 2. Segment lengths are quantised to whole frames, so the total is exact and the
    audio trim is the same frame boundary.

In-scene gaps are absorbed by letting the shot's move keep running (the screen
never freezes on a stale frame). Scene-change gaps are held as black, and the
next scene fades up over 200 ms, which is the only fade brand.json allows.
"""
import csv, os, subprocess
import numpy as np
from PIL import Image, ImageFilter
import gfx, cards
from gfx import W, H, C, hexrgb, text_layer, thread, rule

FF = '/home/user/.local/bin/ffmpeg'
EP = '/home/user/Riwaq_System_Repo/episode/1816'
PL = '/home/user/work/plates'
GD = '/home/user/Riwaq_System_Repo/google_drive'
CUT = '/home/user/work/cut'
FPS = 30
OUTW, OUTH = 1920, 1080
os.makedirs(f'{CUT}/seg', exist_ok=True)
os.makedirs(f'{CUT}/lay', exist_ok=True)


def F(t):
    return int(round(float(t) * FPS))


PLATE = {
    '1':  f'{GD}/LOOK01_field_dawn_graded_2560x1440.png',
    '2':  f'{PL}/ch1_02_farmland_raw.png',
    '3':  f'{PL}/ch1_03_legs_raw.png',
    '4':  f'{PL}/ch1_04_rain_raw.png',
    '5':  f'{PL}/ch1_05_sprouts_raw.png',
    '8':  f'{PL}/ch1_08_nib_raw.png',
    '9':  f'{PL}/ch1_09_handwriting_raw.png',
    '10': f'{PL}/ch1_10_market_raw.png',
    '12': f'{PL}/ch1_12_frost_window_raw.png',
    '13': f'{PL}/ch1_13_frost_fence_raw.png',
    '17': f'{PL}/ch1_17_road_raw.png',
    '18': f'{PL}/ch1_10_market_raw.png',
    '19': f'{PL}/ch1_02_farmland_raw.png',
    '20': f'{GD}/LOOK01_field_dawn_graded_2560x1440.png',
    '23': f'{PL}/ch1_03_legs_raw.png',
    '29': f'{PL}/ch1_17_road_raw.png',
    '30': f'{GD}/LOOK02_sulfate_haze_graded_2560x1440.png',
    '32': f'{PL}/ch1_12_frost_window_raw.png',
}
# shots that reuse an earlier image instead of a plate made for them, and the
# re-framing each one gets so the reuse is not visible as a repeat
STAND_IN = {'18': ('10', 'tight'), '19': ('2', 'low'), '20': ('1 LOOK01', 'right'),
            '23': ('3', 'left'), '29': ('17', 'low'), '30': ('LOOK02', 'tight'),
            '32': ('12', 'high')}
VARIANT = {k: v[1] for k, v in STAND_IN.items()}
# small colour separation per scene so the archive never feels like one grade
TEMP = {'1': 1.00, '2': 0.97, '3': 1.03}

# 'مشاهد مُعاد تخيّلها' is a factual label, not a caption: it marks every shot whose
# image was generated. v2.2 flags it on shot 4; as production lead I also mark the
# first generated shot of each of the three scenes (2, 10, 17) so a viewer who joins
# mid-chapter still sees it. Quiet corner treatment, not a title.
QUIET = {'2', '4', '10', '17'}
END_TITLE = '34'
TEXT = {
    '2':  'مشاهد مُعاد تخيّلها',
    '10': 'مشاهد مُعاد تخيّلها',
    '17': 'مشاهد مُعاد تخيّلها',
    '4':  'مشاهد مُعاد تخيّلها',
    '8':  'أشهر وحش في الأدب',
    '12': 'الصقيع رجع',
    '14': 'نيو إنجلاند · 8 يونيو',
    '19': 'اختفى من الحقول',
    '22': 'ثلاثة مشتبهين',
    '25': 'فترة دالتون',
    '30': 'سومباوا',
    '30': 'سومباوا',
    '33': 'أقوى تأثير',
}

# surfaces alternate: full-bleed sheet, inset document, stamped page, so no two
# consecutive inserts use the same device.
# Rhythm across the 16 inserts: inset document / full-bleed page / stamped page,
# three paper tones, alternating tilt. Scale >1 crops the sheet so the page fills
# the frame and the cut edge disappears.
CARDS = {
    # three surfaces only, alternating: inset sheet (document on the table),
    # full-bleed sheet (the page is the frame), and one purpose-built insert.
    '6':  lambda: cards.card_thread(seed=61, bleed=True, tone=1,
                                    path=[(.02, .30), (.36, .46), (.70, .34), (1.02, .48)]),
    '7':  lambda: cards.card_map(seed=71, label='آلاف الكيلومترات', scale=0.84, rot=-0.7, tone=0),
    '11': lambda: cards.card_thread(seed=81, bleed=True, tone=2,
                                    path=[(-.02, .18), (.30, .30), (.62, .52), (.98, .66)]),
    '14': lambda: cards.card_ledger(seed=91, scale=0.84, rot=-0.6, tone=0),
    '15': lambda: cards.card_ledger(seed=92, bleed=True, tone=2, pointer=4),
    '16': lambda: cards.card_ledger(seed=93, scale=0.70, rot=1.1, tone=1),
    '21': lambda: cards.card_folder(seed=101, tone=2),
    '22': lambda: cards.card_pins(seed=102, tone=0, scale=0.84, rot=0.5),
    '24': lambda: cards.card_data(seed=111, sun=False, scale=0.80, rot=-0.9, tone=1),
    '25': lambda: cards.card_data(seed=112, sun=True, scale=0.88, rot=0.4, tone=0),
    '26': lambda: cards.card_map(seed=121, arc=False, stamp='غير محدد', scale=0.84, rot=0.7, tone=2),
    '27': lambda: cards.card_blank(seed=103, tone=1, scale=0.58, rot=-1.4, stamp='بلا اسم'),
    '28': lambda: cards.card_cloud(seed=122, tone=2, scale=0.80, rot=-1.0),
    '31': lambda: cards.card_thread(seed=131, bleed=True, tone=0,
                                    path=[(-.02, .60), (.30, .40), (.62, .46), (.88, .40)]),
    '33': lambda: cards.card_thread(seed=104, bleed=True, tone=1, beats=3, emphasis=True,
                                    path=[(.06, .64), (.34, .44), (.66, .56), (.94, .38)]),
    '34': lambda: cards.card_plain(seed=141, tone=2),
}


def prep(path, w=2560, h=1440, seed=5, variant='center'):
    """Cover-crop to 16:9, then take a *different crop of the same source* when a
    shot is a declared stand-in, so the same plate never reads twice at the same
    framing. Variants are re-framings, not new photographs, and the report says so."""
    im = Image.open(path).convert('RGB')
    sw, sh = im.size
    tr = w / h
    if sw / sh > tr:
        nw = int(sh * tr); x = (sw - nw) // 2
        im = im.crop((x, 0, x + nw, sh))
    else:
        nh = int(sw / tr); y = (sh - nh) // 2
        im = im.crop((0, y, sw, y + nh))
    if variant != 'center':
        cw, ch = im.size
        # re-frame then re-cover: 62-82% of the frame, pushed to one side
        f = {'low': (0.74, 0.50, 0.50, 0.72), 'high': (0.74, 0.50, 0.50, 0.28),
             'left': (0.72, 0.72, 0.32, 0.50), 'right': (0.72, 0.72, 0.68, 0.50),
             'tight': (0.62, 0.62, 0.50, 0.46)}[variant]
        fw, fh = int(cw * f[0]), int(ch * f[1])
        cx, cy = int(cw * f[2]), int(ch * f[3])
        x0 = max(0, min(cw - fw, cx - fw // 2)); y0 = max(0, min(ch - fh, cy - fh // 2))
        im = im.crop((x0, y0, x0 + fw, y0 + fh)).resize((cw, ch), Image.LANCZOS)
    im = im.resize((w, h), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32) / 255.0
    TOE, SHO, BL, WR = 0.10, 0.90, 0.035, 0.93

    def f(v):
        out = v.copy()
        lo = v < TOE
        t = v[lo] / TOE
        out[lo] = BL + (TOE - BL) * (t * t * (3 - 2 * t))
        hi = v > SHO
        t2 = (v[hi] - SHO) / (1 - SHO)
        out[hi] = SHO + (WR - SHO) * (t2 * (2 - t2))
        return out
    for c in range(3):
        a[..., c] = f(a[..., c])
    if seed is not None:
        rng = np.random.default_rng(seed)
        g = rng.normal(0, 6.0, (h, w, 1)).astype(np.float32)
        a = a * 255.0 + g
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def _fit(lay, path):
    """overlays are authored on the 2560x1440 design canvas, the frame is 1920x1080;
    without this the marks land off-centre and corner marks fall outside the frame."""
    lay.resize((OUTW, OUTH), Image.LANCZOS).save(path)
    return path


def end_title():
    """chapter card at the tail of shot 34: the frame empties to paper and the
    title settles, then holds. 380 ms in, no out."""
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    lay = Image.alpha_composite(lay, text_layer('الفصل الأول', 'plex_med', 46,
                                                C['stone'], pos=int(H * .40)))
    lay = Image.alpha_composite(lay, rule((W, H), inset=int(W * .30), y=int(H * .455),
                                          thickness=2, alpha=200))
    lay = Image.alpha_composite(lay, text_layer('الصيف اللي مكانش', 'amiri_bold', 132,
                                                C['ink_deep'], pos=int(H * .50)))
    return _fit(lay, f'{CUT}/lay/end_title.png')


def overlay_png(shot, main):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    if shot in QUIET:
        # bottom-right, inside the 120 px bottom safe area, low contrast
        from PIL import ImageDraw as _ID
        from gfx import ar, font
        f = font('plex_med', 40)
        d = _ID.Draw(lay)
        tw = d.textbbox((0, 0), ar(main), font=f)[2]
        d.text((W - 96 - tw, H - 150), ar(main), font=f,
               fill=hexrgb(C['parchment']) + (176,))
        return _fit(lay, f'{CUT}/lay/txt_{shot}.png')
    px = 96 if len(main) < 22 else 80
    lay = Image.alpha_composite(lay, text_layer(main, 'amiri_bold', px, C['parchment'],
                                                pos=int(H * .745)))
    lay = Image.alpha_composite(lay, rule((W, H), inset=int(W * .34), y=int(H * .712),
                                          thickness=2, alpha=190))
    return _fit(lay, f'{CUT}/lay/txt_{shot}.png')


def motion(shot, n, scene_start, scene_end):
    """Calm, alternating push / pull with a whisper of drift.
    brand: ken_burns 1.0 -> 1.06; no whip, spin, bounce, punch."""
    s = int(shot)
    push = (s % 4) in (1, 2)
    z0, z1 = (1.0, 1.06) if push else (1.06, 1.0)
    dz = (z1 - z0) / max(n - 1, 1)
    z = f"{z0:.4f}+{dz:.6f}*on"
    drift = 0.0018 * (1 if s % 2 else -1)
    x = f"iw/2-(iw/zoom/2)+({drift:.5f}*on*iw/zoom)"
    y = "ih/2-(ih/zoom/2)"
    vf = (f"zoompan=z='{z}':x='{x}':y='{y}'"
          f":d=1:s={OUTW}x{OUTH}:fps={FPS}")
    # zoompan on a still: feed one frame, let d=1 + loop handle the rest
    if scene_start:
        vf += ",fade=t=in:st=0:d=0.2"
    if scene_end:
        vf += f",fade=t=out:st={max(n / FPS - 0.20, 0):.3f}:d=0.2"
    return vf


def build(rows):
    """rows -> [shot, f0, f1, row, tail_fade] on the absolute timeline.

    In-scene narration pauses: the shot's move keeps running to the next t_in, so
    the screen never freezes and no frames are lost.
    Scene-change pauses: the last shot of the scene owns them and fades to black
    over 200 ms (brand allows hard cut or 200 ms fade; those pauses are 0.47-1.38 s,
    so they read as a held breath, not a flicker)."""
    plan = []
    for i, r in enumerate(rows):
        s = int(r['shot'])
        nxt = rows[i + 1] if i + 1 < len(rows) else None
        f0, f1 = F(r['t_in']), F(r['t_out'])
        tail = False
        if nxt is not None:
            if nxt['scene'] == r['scene']:
                f1 = F(nxt['t_in'])
            else:
                f1 = F(nxt['t_in'])
                tail = True
        plan.append([s, f0, f1, r, tail])
    return plan


def main():
    rows = list(csv.DictReader(open(f'{EP}/SHOT_LIST_v2.2.csv', encoding='utf-8-sig')))
    rows = [r for r in rows if r['chapter'] == '1']
    plan = build(rows)
    total_f = plan[-1][2] - plan[0][1]
    print(f'shots {len(rows)}  frames {total_f}  = {total_f/FPS:.3f}s')
    print(f'audio in-point {plan[0][1]/FPS:.4f}s  out {plan[-1][2]/FPS:.4f}s')
    print('stand-ins:', STAND_IN)

    segs = []
    print('frames owned by shots:', sum(p[2] - p[1] for p in plan))
    for idx, (shot, f0, f1, r, tail) in enumerate(plan, 1):
        n = f1 - f0
        shot = str(shot)
        if shot in CARDS:
            src = CARDS[shot]().convert('RGB')
        else:
            src = prep(PLATE[str(shot)], seed=int(shot) * 13,
                       variant=VARIANT.get(str(shot), 'center'))
            t = TEMP.get(r['scene'], 1.0)
            if abs(t - 1.0) > 1e-3:
                a = np.asarray(src, np.float32)
                a[..., 2] *= t
                a[..., 0] *= (2.0 - t)
                src = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        base = f'{CUT}/seg/base_{shot}.png'
        src.resize((OUTW * 2, OUTH * 2), Image.LANCZOS).save(base) if False else src.save(base)

        first_of_scene = (idx == 1) or (plan[idx - 2][3]['scene'] != r['scene'])
        vf = motion(shot, n, first_of_scene, tail)
        inputs = ['-loop', '1', '-framerate', str(FPS), '-i', base]
        fc = f'[0:v]{vf}'
        if str(shot) == END_TITLE:
            # the thread leaves the frame, then the chapter title settles on bare paper
            plain = cards.card_plain(seed=141, tone=2).convert('RGB')
            plain.save('/tmp/_plain_141_2.png')
            th = cards.thread_layer(seed=141, tone=2,
                                    path=[(.10, .52), (.40, .50), (.66, .54), (1.06, .44)])
            tp = f'{CUT}/lay/thread_34.png'
            th.resize((OUTW, OUTH), Image.LANCZOS).save(tp)
            tt = end_title()
            inputs += ['-loop', '1', '-framerate', str(FPS), '-i', tp,
                       '-loop', '1', '-framerate', str(FPS), '-i', tt]
            fc += (f"[bg];[1:v]format=rgba,fade=t=out:st=1.5:d=1.0:alpha=1[t];"
                   f"[bg][t]overlay=0:0[b1];"
                   f"[2:v]format=rgba,fade=t=in:st=2.6:d=0.38:alpha=1[ti];"
                   f"[b1][ti]overlay=0:0")
        elif str(shot) in TEXT:
            ov = overlay_png(str(shot), TEXT[str(shot)])
            inputs += ['-loop', '1', '-framerate', str(FPS), '-i', ov]
            fc += f"[bg];[1:v]format=rgba,fade=t=in:st=0.28:d=0.38:alpha=1," \
                  f"fade=t=out:st={max(n/FPS-0.55,0.5):.3f}:d=0.28:alpha=1[ov];[bg][ov]overlay=0:0"
        out = f'{CUT}/seg/seg_{shot}.mp4'
        cmd = [FF, '-hide_banner', '-loglevel', 'error', '-y', *inputs,
               '-filter_complex', fc, '-frames:v', str(n), '-r', str(FPS),
               '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17',
               '-pix_fmt', 'yuv420p', '-g', '60', out]
        subprocess.run(cmd, check=True)
        segs.append(out)
        print(f'  [{idx:02d}] shot {shot:>2} {n:>4}f {n/FPS:6.2f}s  scene{r["scene"]}'
              f'{"  <fade-in" if first_of_scene else ""}{"  fade-out>" if tail else ""}  {r["shot_type"]}')

    with open(f'{CUT}/concat.txt', 'w') as f:
        for p in segs:
            f.write(f"file '{p}'\n")
    print('rendered', len(segs), 'segments')


if __name__ == '__main__':
    main()
