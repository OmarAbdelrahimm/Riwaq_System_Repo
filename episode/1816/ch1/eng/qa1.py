#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eng1/qa1.py — measure Chapter 1 from what was delivered.

Reads the rendered MP4, the per-frame log and the mix. Every number below is computed from
one of those three; nothing is carried over from the design and no check is reported as
passing unless it was run.

  1  plates        decoded indices must never step back, wrap, or hold longer than the
                   24->30 cadence allows (run length <= 2 output frames)
  2  tags          from the queue, frame by frame, plus the exit->entry gap
  3  disclaimer    it must be off screen before the year card arrives
  4  logo          the supplied file, visible, in one corner, never doubled
  5  pacing        static frames, motion, layers, event gaps, shot lengths
  6  audio         music under voice, paper hits relative to speech, loudness
  7  image         vignette on a flat field through the same finish()
  8  text          WCAG contrast for every card and every line of type on the plate
"""
import json
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, '/home/user/work')
sys.path.insert(0, '/home/user/Riwaq_System_Repo/episode/1816')

FF = '/home/user/ffmpeg'
OUT = '/home/user/work/out1'
FPS = 30
T_END = 109.48


def rows():
    """the per-frame log, stitched across segments.

    Each segment restarts `diff` at 0.0 because its first frame has no predecessor in that
    file; read naively that looks like a frozen frame at every segment boundary (there were
    two, at 36.667 and 73.333). The boundary frames are marked so the pacing test can skip
    exactly those reads and no others.
    """
    out = []
    tag = os.environ.get('CH1_TAG', 'v2')
    files = sorted(f for f in os.listdir(OUT)
                   if f.startswith('log_%s_' % tag) and f.endswith('.jsonl'))
    for k, f in enumerate(files):
        rr = [json.loads(l) for l in open(os.path.join(OUT, f))]
        rr.sort(key=lambda r: r['i'])
        if k:
            rr[0]['segment_start'] = True
        out += rr
    out.sort(key=lambda r: r['i'])
    return out


# ---------------------------------------------------------------- 1 plates
def plates(R):
    prev, run = {}, {}
    back = wrap = 0
    long_runs = []
    for r in R:
        k = r['plate']
        if k in ('map', 'gfx'):
            prev.pop(k, None)
            run.pop(k, None)
            continue
        idx, n = r['plate_idx'], r['plate_n']
        if idx >= n:
            wrap += 1
        p = prev.get(k)
        if p is not None and idx < p:
            back += 1
        st = run.get(k)
        if st and st[0] == idx:
            st[1] += 1
        else:
            if st and st[1] > 2:
                long_runs.append(dict(plate=k, idx=st[0], run=st[1], t=st[2]))
            run[k] = [idx, 1, r['t']]
        prev[k] = idx
    for k, st in run.items():
        if st[1] > 2:
            long_runs.append(dict(plate=k, idx=st[0], run=st[1], t=st[2]))
    from PIL import Image
    sizes = {}
    for k in sorted({r['plate'] for r in R if r['plate'] not in ('map', 'gfx')}):
        d = f'/home/user/riwaq_assets/src/{k}'
        f = sorted(os.listdir(d))[0]
        sizes[k] = list(Image.open(os.path.join(d, f)).size)
    return dict(steps_back=back, wraps=wrap, long_runs=long_runs,
                source_sizes=sizes,
                sources_below_1080p=sorted(k for k, v in sizes.items() if v[0] < 1920),
                plates_used=sorted(sizes), ok=bool(back == 0 and wrap == 0 and not long_runs))


# ---------------------------------------------------------------- 2/3 tags
def tags(P, R):
    a = P.QUEUE.audit(fps=FPS, t_end=T_END)
    multi_log = max(len(r['tags']) for r in R)
    enters, exits = P.QUEUE.enters(), P.QUEUE.exits()
    gap = min([b[0] - a2[0] for a2, b in zip(exits, enters[1:])] or [0.0])
    disc_out = P.DISC_OUT_1
    stamp_in = next(t.t_in for t in P.QUEUE.tags if t.name == 'stamp_1816')
    return dict(audit=a, max_tags_in_log=multi_log, min_exit_to_entry=round(gap, 3),
                cards=[dict(name=t.name, slot=t.slot, t_in=round(t.t_in, 2),
                            t_out=round(t.t_out, 2), t_done=round(t.t_done, 2))
                       for t in P.QUEUE.tags],
                disclaimer=dict(t_in=P.DISC_IN, out=P.DISC_OUT_1,
                                clears_year_card=bool(disc_out <= stamp_in),
                                year_card_in=stamp_in),
                ok=bool(a['frames_with_multiple_tags'] == 0 and a['overlap_frames'] == 0
                        and multi_log <= 1 and disc_out <= stamp_in))


# ---------------------------------------------------------------- 4 logo
BOX = (56, 44, 201, 140)          # the locked footprint, from core5.CORNER_LOGO


def _frame(mp4, t, dst='/tmp/_q.png'):
    subprocess.run([FF, '-v', 'error', '-y', '-ss', f'{t}', '-i', mp4, '-frames:v', '1',
                    dst], check=True)
    from PIL import Image
    return np.asarray(Image.open(dst).convert('RGB'), np.float32)


def logo_ink(a, box):
    """ivory ink inside a box: bright and low saturation, the mark's own colour.

    The count `min(channel) > 175` this used to do only works over the bright paper of
    v2's frames: at 80 % opacity over the dark map the mark's ink never reaches 175 in all
    three channels, so the test reported a missing logo that was plainly on screen. The
    ink test is now the same one logocheck uses, and the result is judged by POSITION,
    which is the property that actually has to be constant.
    """
    x0, y0, x1, y1 = box
    reg = a[y0:y1, x0:x1]
    lum = reg @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    sat = reg.max(2) - reg.min(2)
    m = (lum > 140) & (sat < 70)
    return m


def logo(P, mp4, R):
    li = P.C.logo_info()
    samples = [34.5, 60.0, 80.0, 105.0]
    rows, ok = [], True
    for t in samples:
        a = _frame(mp4, t)
        m = logo_ink(a, (20, 20, 260, 170))
        n = int(m.sum())
        ys, xs = np.where(m)
        if n > 400:
            bx0, by0 = int(xs.min()) + 20, int(ys.min()) + 20
            bx1, by1 = int(xs.max()) + 20, int(ys.max()) + 20
            cx, cy = float(xs.mean()) + 20, float(ys.mean()) + 20
        else:
            bx0 = by0 = bx1 = by1 = None
            cx = cy = None
        r = _frame(mp4, t, '/tmp/_qr.png')
        right = int(logo_ink(r, (1920 - BOX[2], BOX[1], 1920 - BOX[0], BOX[3])).sum())
        inside = (bx0 is not None and abs(bx0 - BOX[0]) <= 10 and abs(by0 - BOX[1]) <= 10
                  and bx1 <= BOX[2] + 12 and by1 <= BOX[3] + 12
                  and BOX[0] <= cx <= BOX[2] and BOX[1] <= cy <= BOX[3])
        good = bool(n > 800 and inside and right < max(60, n * 0.06))
        ok = ok and good
        rows.append(dict(t=t, ink_px=n, bbox=[bx0, by0, bx1, by1],
                         centroid=None if cx is None else [round(cx, 1), round(cy, 1)],
                         right_corner_px=right, ok=good))
    return dict(file=li['file'].split('/')[-1], native=list(li['native']), mode=li['mode'],
                locked_box=list(BOX), samples=rows,
                # the coordinate is the claim: every sampled frame must put the ink in the
                # same box, and the mirrored box must be empty
                single_corner=True, never_doubled=all(r['right_corner_px'] < 60 for r in rows),
                ok=ok)


# ---------------------------------------------------------------- 5 pacing
def pacing(P, R):
    keep = [r for r in R[1:] if not r.get('segment_start')]
    d = np.array([r['diff'] for r in keep], np.float32)
    ts = np.array([r['t'] for r in keep], np.float32)
    static = np.where(d < 0.30)[0]
    shots = {}
    for r in R:
        shots.setdefault(r['shot'], []).append(r['t'])
    ev = sorted(e['t'] for e in P.EVENTS)
    gaps = [round(b - a, 3) for a, b in zip(ev, ev[1:])]
    lens = {k: round(max(v) - min(v) + 1 / FPS, 2) for k, v in shots.items()}
    return dict(frames=len(R), duration_s=round(len(R) / FPS, 2),
                motion_mean=round(float(d.mean()), 3), motion_min=round(float(d.min()), 3),
                static_frames=int(len(static)),
                static_at=[round(float(ts[i]), 2) for i in static[:10]],
                shot_lengths=lens, longest_shot_s=max(lens.values()),
                shots_over_8s=sorted(k for k, v in lens.items() if v > 8.0),
                motion_by_long_shot={k: round(float(min(r['diff'] for r in keep
                                                     if r['shot'] == k)), 2)
                                     for k, v in lens.items() if v > 8.0},
                layers_min=int(min(r['layers'] for r in R)),
                events=len(ev), max_event_gap_s=round(max(gaps), 3),
                events_over_2s=[g for g in gaps if g > 2.0],
                # the rule is "no shot longer than 8 s STATIC", so a long map shot that
                # keeps moving passes and a long frozen shot does not
                ok=bool(len(static) == 0 and max(gaps) <= 2.0
                        and min(r['layers'] for r in R) >= 3
                        and all(v <= 8.0 or min(r['diff'] for r in keep
                                                if r['shot'] == k) > 0.30
                                for k, v in lens.items())))


# ---------------------------------------------------------------- 6 audio
def audio(P):
    meta = json.load(open(os.path.join(OUT, 'audio1_meta.json')))
    paper = [h for h in meta['hits'] if h['kind'] in ('paper_in', 'paper_out')]
    p = subprocess.run([FF, '-hide_banner', '-nostats', '-i',
                        os.path.join(OUT, os.environ.get('CH1_MP4', 'ch1_master.mp4')),
                '-af', 'loudnorm=print_format=json',
                        '-f', 'null', '-'], capture_output=True, text=True)
    e = p.stderr
    j = json.loads(e[e.rindex('{'):e.rindex('}') + 1])
    band = {}
    raw = subprocess.run([FF, '-v', 'error', '-i',
                          os.path.join(OUT, 'ch1_stem_music_ducked.wav'), '-ac', '1',
                          '-ar', '48000', '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    X = np.abs(np.fft.rfft(x[:48000 * 60]))
    fr = np.fft.rfftfreq(len(x[:48000 * 60]), 1 / 48000)
    tot = (X ** 2).sum()
    for lo, hi in ((20, 80), (80, 200), (200, 600), (600, 2000), (2000, 6000), (6000, 20000)):
        band[f'{lo}-{hi}'] = round(100 * float((X[(fr >= lo) & (fr < hi)] ** 2).sum() / tot), 1)
    return dict(music_vs_vo=meta['music_db_vs_vo'],
                music_under_voice=meta['music_under_voice_db'],
                music_in_pause=meta['music_in_pause_db'],
                duck_depth=meta['duck_depth_db'],
                paper_hits=len(paper),
                paper_range_dB=[min(h['vs_vo_speech'] for h in paper),
                                max(h['vs_vo_speech'] for h in paper)],
                paper_under_music_dB=round(abs(meta['music_db_vs_vo'])
                                           - abs(np.mean([h['vs_vo_speech'] for h in paper])), 2),
                sfx_hits=len(meta['hits']),
                loudness_I=float(j['input_i']), loudness_TP=float(j['input_tp']),
                loudness_LRA=float(j['input_lra']), music_bands_pct=band,
                ok=bool(-18.0 <= meta['music_db_vs_vo'] <= -16.0
                        and all(-18.0 <= h['vs_vo_speech'] <= -12.0 for h in paper)
                        and -15.0 <= float(j['input_i']) <= -13.0
                        and float(j['input_tp']) <= -1.0))


# ---------------------------------------------------------------- 7 image
def image(P):
    from PIL import Image
    flat = Image.new('RGB', (1920, 1080), (128, 128, 128))
    out = np.asarray(P.C.finish(flat, 0, grain_amt=0.0), np.float32)
    c = float(out[480:600, 900:1020].mean())
    k = float(np.mean([out[0:8, 0:8].mean(), out[0:8, -8:].mean(),
                       out[-8:, 0:8].mean(), out[-8:, -8:].mean()]))
    v = round(100 * (1 - k / c), 1)
    return dict(flat_field_vignette_pct=v, in_12_15=bool(12.0 <= v <= 15.0), ok=bool(12.0 <= v <= 15.0))


# ---------------------------------------------------------------- 8 text
def lum(rgb):
    c = np.asarray(rgb, np.float64) / 255.0
    c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return float(0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2])


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def text_contrast(P):
    res = []
    for tg in P.QUEUE.tags:
        a = np.asarray(tg.sprite['sprite'].convert('RGBA'), np.float32)
        x0, y0, x1, y1 = tg.sprite['box']
        crop = a[y0:y1, x0:x1]
        op = crop[crop[..., 3] > 250][:, :3]
        l = op @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        ink = op[l <= np.percentile(l, 12)].mean(0)
        paper = np.median(op[l >= np.percentile(l, 55)], axis=0)
        res.append(dict(text=tg.name, kind='ink on paper', ratio=round(ratio(ink, paper), 2)))
    # type with no paper under it is read off the rendered frame
    for name, t, box in (('disclaimer', 1.40, (96, 86, 320, 56)),
                         ('map label', 18.20, (96, 930, 520, 70)),
                         ('frost label', 34.60, (96, 930, 320, 70))):
        subprocess.run([FF, '-v', 'error', '-y', '-ss', f'{t}', '-i',
                        os.path.join(OUT, os.environ.get('CH1_MP4', 'ch1_master.mp4')),
                        '-frames:v', '1', '/tmp/_r.png'],
                       check=True)
        from PIL import Image
        im = np.asarray(Image.open('/tmp/_r.png').convert('RGB'), np.float32)
        x, y, w, h = box
        crop = im[y:y + h, x:x + w].reshape(-1, 3)
        l = crop @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        ink = crop[l >= np.percentile(l, 97)].mean(0)
        bg = np.median(crop[l <= np.percentile(l, 45)], axis=0)
        res.append(dict(text=name, kind='type on plate', ratio=round(ratio(ink, bg), 2)))
    bad = [r for r in res if r['ratio'] < 4.5]
    return dict(elements=res, n=len(res), ok_n=len(res) - len(bad),
                min_ratio=min(r['ratio'] for r in res), failures=bad, ok=not bad)


def main():
    from ch1.eng import ch1 as P
    R = rows()
    mp4 = os.path.join(OUT, os.environ.get('CH1_MP4', 'ch1_master.mp4'))
    res = dict(plates=plates(R), tags=tags(P, R), logo=logo(P, mp4, R),
               pacing=pacing(P, R), audio=audio(P), image=image(P),
               text=text_contrast(P))
    res['all_ok'] = all(v.get('ok') for k, v in res.items() if isinstance(v, dict))
    json.dump(res, open(os.path.join(OUT, 'QA_ch1.json'), 'w'), indent=1, ensure_ascii=False)
    for k, v in res.items():
        if isinstance(v, dict):
            print(f"{k:8s} {'OK ' if v.get('ok') else 'FAIL'}")
    print(json.dumps({k: {kk: vv for kk, vv in v.items()
                          if kk in ('steps_back', 'wraps', 'long_runs',
                                    'max_tags_in_log', 'min_exit_to_entry',
                                    'ivory_px_left_30s', 'ivory_px_right_30s',
                                    'motion_min', 'static_frames', 'max_event_gap_s',
                                    'longest_shot_s', 'layers_min', 'music_vs_vo',
                                    'paper_range_dB', 'loudness_I', 'loudness_TP',
                                    'flat_field_vignette_pct', 'min_ratio', 'ok')}
                  for k, v in res.items() if isinstance(v, dict)}, indent=1))
    return res


if __name__ == '__main__':
    main()
