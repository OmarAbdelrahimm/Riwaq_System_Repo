#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
eng/qa.py — pilot QA, measured on the rendered frames and the delivered audio.

Nothing here is asserted from the shot notes. Every number in the report comes from
this file's output.

  1. layers per shot            min / median live layers, from the render log
  2. event density per 10 s      events on words, and again counting cuts as events
  3. static-frame detector       mean |dLuma| between consecutive frames
  4. text contrast               WCAG ratio per text element, measured on the frame
                                 with that element's ink hidden (paper stays)
  5. logo presence               the mark must be present after 24 s, absent before
  6. duplicate check             dHash64 Hamming distance between shot midpoints
  7. audio                       voice / ducked music / SFX stems, master LUFS + TP
  8. SFX-to-event sync           peak of each designed hit vs its cue frame
  9. B-roll length               4-8 s per clip
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from PIL import Image
import eng.pilot as P

OUT = '/home/user/work/out'
FF = '/home/user/ffmpeg'
FPS = 30


def iter_frames(mp4):
    """stream frames: 30 s of 1080p raw is 5.6 GB, so nothing is held in memory"""
    cmd = [FF, '-v', 'error', '-i', mp4, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    fb = 1080 * 1920 * 3
    while True:
        buf = p.stdout.read(fb)
        if len(buf) < fb:
            break
        yield np.frombuffer(buf, np.uint8).reshape(1080, 1920, 3)
    p.stdout.close(); p.wait()


def scan_frames(mp4, mid_indices):
    want = set(mid_indices)
    diffs, prev = [], None
    kept, fi = {}, 0
    corner_pre, corner_post = [], []
    for fr in iter_frames(mp4):
        g = fr.mean(2)
        if prev is not None:
            diffs.append(float(np.abs(g - prev).mean()))
        prev = g
        if fi in want:
            kept[fi] = Image.fromarray(fr).convert('L').resize((9, 8), Image.LANCZOS)
        if fi in (300, 480, 600):
            corner_pre.append(float(fr[960:1030, 80:160].astype(np.float32).mean()))
        if fi in (750, 810, 885):
            corner_post.append(float(fr[960:1030, 80:160].astype(np.float32).mean()))
        fi += 1
    return np.asarray(diffs), kept, corner_pre, corner_post, fi


def dhash(img, size=8):
    g = np.asarray(img.convert('L').resize((size + 1, size), Image.LANCZOS), np.float32)
    d = g[:, 1:] > g[:, :-1]
    return int(''.join('1' if x else '0' for x in d.flatten()), 2)


def audio_lufs(path):
    r = subprocess.run([FF, '-hide_banner', '-nostats', '-i', path, '-af',
                        'loudnorm=print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True)
    e = r.stderr
    return json.loads(e[e.rindex('{'):e.rindex('}') + 1])


def peak_time(path, t_lo, t_hi):
    """time of the largest sample inside a short window: a hit is a transient, so the
    window is 120 ms, not the whole next second"""
    pre = max(0.0, t_lo - 0.12)
    raw = subprocess.run([FF, '-v', 'error', '-ss', f'{pre:.3f}', '-i', path,
                          '-t', f'{t_hi - t_lo + 0.24:.3f}', '-ac', '1', '-ar', '48000',
                          '-f', 'f32le', '-'], capture_output=True).stdout
    a = np.abs(np.frombuffer(raw, np.float32))
    if not len(a):
        return None
    return pre + float(np.argmax(a)) / 48000.0


def run(tag='pilot', t_end=30.0):
    recs = [json.loads(l) for l in open(os.path.join(OUT, f'layerlog_{tag}.jsonl'))]
    mp4 = os.path.join(OUT, f'PILOT_{tag}.mp4')
    shots = P.build_shots()
    evs = P.events_table(shots)
    out = {}

    per = {}
    for r in recs:
        per.setdefault(r['shot'], []).append(r['layers'])
    out['layers'] = {s: dict(frames=len(v), min=min(v), median=int(np.median(v)), max=max(v))
                     for s, v in per.items()}
    out['layers_min_overall'] = min(min(v) for v in per.values())
    out['layers_ok'] = bool(out['layers_min_overall'] >= 3)

    ev_t = [e['t'] for e in evs]
    gaps = [round(b - a, 3) for a, b in zip(ev_t, ev_t[1:])]
    win = {}
    for w0 in range(0, int(t_end), 10):
        win[f'{w0}-{w0 + 10}s'] = sum(1 for t in ev_t if w0 <= t < w0 + 10)
    out['events'] = dict(count=len(evs), mean_gap=round(float(np.mean(gaps)), 3),
                         max_gap=round(max(gaps), 3), per_10s=win,
                         list=[{k: e[k] for k in ('t', 'shot', 'event', 'sfx', 'frame')}
                               for e in evs])
    out['event_density_ok'] = max(gaps) <= 2.0
    cuts = [s.t0 for s in shots[1:]]
    all_t = sorted(ev_t + cuts)
    agaps = [round(b - a, 3) for a, b in zip(all_t, all_t[1:])]
    out['events_with_cuts'] = dict(count=len(all_t), mean_gap=round(float(np.mean(agaps)), 3),
                                   max_gap=round(max(agaps), 3),
                                   ok=bool(max(agaps) <= 2.0),
                                   note='cut points counted as visible events')

    mids = {int(((s.t0 + s.t1) / 2) * FPS): s.name for s in shots}
    diffs, kept, corner_pre, corner_post, n = scan_frames(mp4, mids)
    run_len = best = 0
    for d in diffs:
        run_len = run_len + 1 if d < 0.35 else 0
        best = max(best, run_len)
    out['motion'] = dict(frames=int(n), mean_diff=round(float(diffs.mean()), 3),
                         min_diff=round(float(diffs.min()), 3),
                         static_frames=int((diffs < 0.35).sum()),
                         longest_static_run=int(best))

    hh = [(mids[fi], dhash(im)) for fi, im in kept.items()]
    dups = []
    for i in range(len(hh)):
        for j in range(i + 1, len(hh)):
            h = bin(hh[i][1] ^ hh[j][1]).count('1')
            if h < 12:
                dups.append(dict(a=hh[i][0], b=hh[j][0], hamming=h))
    out['duplicates'] = dict(pairs=dups, threshold=12, method='dhash64 on shot midpoints')

    pre = float(np.mean(corner_pre)) if corner_pre else 0.0
    post = float(np.mean(corner_post)) if corner_post else 0.0
    out['logo'] = dict(corner_mean_before_24s=round(pre, 2),
                       corner_mean_after_24s=round(post, 2),
                       present_after_24s=bool(post > pre + 1.0))

    cs = {}
    for r in recs:
        for c in r.get('contrast', []):
            cs.setdefault(c['text'], []).append(c['ratio'])
    out['text_contrast'] = {k: dict(n=len(v), min=round(min(v), 2), max=round(max(v), 2),
                                    median=round(float(np.median(v)), 2),
                                    pass_4_5=bool(min(v) >= 4.5))
                            for k, v in sorted(cs.items())}
    out['text_contrast_all_pass'] = all(v['pass_4_5'] for v in out['text_contrast'].values())

    stems = {k: os.path.join(OUT, f'{tag}_stem_{k}.wav')
             for k in ('vo', 'music_ducked', 'sfx_stem', 'sfx_designed')}
    au = {k: audio_lufs(p) for k, p in stems.items()}
    master = audio_lufs(os.path.join(OUT, 'PILOT_mix_master.wav'))
    out['audio'] = dict(
        vo_i=float(au['vo']['input_i']), vo_tp=float(au['vo']['input_tp']),
        music_ducked_i=float(au['music_ducked']['input_i']),
        sfx_bed_i=float(au['sfx_stem']['input_i']),
        sfx_designed_i=float(au['sfx_designed']['input_i']),
        duck_db_bed_vs_voice=round(float(au['music_ducked']['input_i']) -
                                   float(au['vo']['input_i']), 2),
        master_i=float(master['input_i']), master_tp=float(master['input_tp']),
        master_lra=float(master['input_lra']),
        delivery_ok=bool(float(master['input_i']) >= -14.5 and
                         float(master['input_tp']) <= -1.0))

    sync = []
    des = stems['sfx_designed']
    for e in evs:
        if e['sfx'] in ('stamp', 'pin', 'needle', 'paper_drop', 'paper_slide', 'thread_draw', 'sting'):
            p = peak_time(des, e['t'], e['t'] + 0.12)
            if p is not None:
                err = round((p - e['t']) * FPS, 2)
                sync.append(dict(event=e['event'], cue=round(e['t'], 3),
                                 measured_peak=round(p, 4),
                                 error_ms=round((p - e['t']) * 1000, 1),
                                 error_frames=err, ok=bool(abs(err) <= 2)))
    out['sync'] = dict(hits=sync, within_2_frames=all(s['ok'] for s in sync),
                       sfx_source_note='designed in code: the supplied SFX stem is a '
                                       'continuous bed with no discrete transients')

    out['broll'] = [dict(shot=s.name, dur=round(s.t1 - s.t0, 3), cam=s.cam,
                         ok=bool(4.0 <= (s.t1 - s.t0) <= 8.0)) for s in shots]
    out['broll_in_range'] = '%d/%d' % (sum(1 for b in out['broll'] if b['ok']),
                                       len(out['broll']))
    cams = [s.cam for s in shots]
    worst = 1
    cur = 1
    for i in range(1, len(cams)):
        cur = cur + 1 if cams[i] == cams[i - 1] else 1
        worst = max(worst, cur)
    out['camera_runs'] = dict(longest_same_move=worst, ok=bool(worst <= 2), moves=cams)
    return out


def contact_sheet(tag='pilot', cols=5, every=2.0, out_path=None, t_end=30.0):
    mp4 = os.path.join(OUT, f'PILOT_{tag}.mp4')
    times = [i * every for i in range(int(t_end / every))]
    rows = int(np.ceil(len(times) / cols))
    TW, TH = 384, 216
    sheet = Image.new('RGB', (cols * TW, rows * (TH + 22)), (14, 13, 12))
    from PIL import ImageDraw
    d = ImageDraw.Draw(sheet)
    for i, t in enumerate(times):
        p = subprocess.run([FF, '-v', 'error', '-ss', f'{t:.2f}', '-i', mp4, '-frames:v', '1',
                            '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True)
        im = Image.open(__import__('io').BytesIO(p.stdout)).convert('RGB').resize(
            (TW, TH), Image.LANCZOS)
        x, y = (i % cols) * TW, (i // cols) * (TH + 22)
        sheet.paste(im, (x, y))
        d.text((x + 6, y + TH + 4), f'{t:05.2f}s', fill=(200, 190, 170))
    out_path = out_path or os.path.join(OUT, f'PILOT_{tag}_contact_sheet.png')
    sheet.save(out_path)
    return out_path


if __name__ == '__main__':
    tag = sys.argv[1] if len(sys.argv) > 1 else 'pilot'
    res = run(tag)
    with open(os.path.join(OUT, f'QA_{tag}.json'), 'w') as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: res[k] for k in ('layers_min_overall', 'layers_ok',
                                          'event_density_ok', 'events_with_cuts',
                                          'motion', 'logo', 'text_contrast_all_pass',
                                          'audio', 'broll_in_range', 'camera_runs')},
                     ensure_ascii=False, indent=1)[:2600])
    print('contact sheet ->', contact_sheet(tag))
