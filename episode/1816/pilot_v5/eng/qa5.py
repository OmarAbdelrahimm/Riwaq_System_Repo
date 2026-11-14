#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eng5/qa5.py — measure the v5 pilot. Nothing here is asserted from the design; it reads
the rendered MP4, the frame log and the mix, and reports what it finds.

  1  tag overlap            from the tag queue + the frame log
  2  logo                  from the file actually composited
  3  text SFX level        from the mix, per hit, against the voice
  4  music tempo           from the delivered score, autocorrelated
  5  transitions / pacing  from the frame log: dissolves, cuts, static frames, event gaps
"""
import json
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, '/home/user/work')
FF = '/home/user/ffmpeg'
OUT = '/home/user/work/out'


def log_rows(tag='pilot5'):
    return [json.loads(l) for l in open(os.path.join(OUT, f'layerlog_{tag}.jsonl'))]


def tempo_of(path):
    raw = subprocess.run([FF, '-v', 'error', '-i', path, '-ac', '1', '-ar', '48000',
                          '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    hop = 240
    env = np.abs(x[:len(x) // hop * hop]).reshape(-1, hop).max(1)
    d = np.diff(env)
    d = d - d.mean()
    ac = np.correlate(d, d, 'full')[len(d) - 1:]
    ac /= ac[0]
    lo, hi = int(0.34 / (hop / 48000)), int(0.90 / (hop / 48000))
    lag = int(np.argmax(ac[lo:hi])) + lo
    return 60.0 / (lag * hop / 48000), float(ac[lag])


def band_energy(path):
    raw = subprocess.run([FF, '-v', 'error', '-i', path, '-ac', '1', '-ar', '48000',
                          '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    X = np.abs(np.fft.rfft(x))
    fr = np.fft.rfftfreq(len(x), 1 / 48000)
    tot = (X ** 2).sum()
    bands = [(20, 80), (80, 200), (200, 600), (600, 2000), (2000, 6000), (6000, 20000)]
    return {f'{a}-{b}': round(100 * float((X[(fr >= a) & (fr < b)] ** 2).sum() / tot), 1)
            for a, b in bands}


def loudness(path):
    p = subprocess.run([FF, '-hide_banner', '-nostats', '-i', path, '-af',
                        'loudnorm=print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True)
    e = p.stderr
    j = json.loads(e[e.rindex('{'):e.rindex('}') + 1])
    return dict(I=float(j['input_i']), TP=float(j['input_tp']), LRA=float(j['input_lra']))


def main():
    from eng5 import pilot5 as P

    rows = log_rows('pilot5')
    res = {}

    # ---- 1 tags
    audit = P.QUEUE.audit()
    res['tags'] = dict(
        audit=audit, max_tags_in_any_frame=max(len(r['tags']) for r in rows),
        timeline=dict(entries=P.QUEUE.enters(), exits=P.QUEUE.exits()),
        min_gap_between_exit_and_entry=round(min(
            [b[0] - a[0] for a, b in zip(P.QUEUE.exits(), P.QUEUE.enters()[1:])] or [0]), 3),
        slots_used=sorted({tg.slot for tg in P.QUEUE.tags}))

    # ---- 2 logo
    rep = P.logo_report()

    def corner_luma(t, box=(40, 40, 400, 200)):
        """count ivory pixels in the corner the mark occupies, at a time with no tag.

        The first version of this check sampled t=20 with a box wide enough to include the
        bright map label, so it reported "logo not visible" on a frame where the mark was
        plainly there. Count bright pixels at 29.0 and compare with the same corner at
        23.0, before the watermark's fade-in at 26.27.
        """
        subprocess.run([FF, '-v', 'error', '-y', '-ss', f'{t}', '-i',
                        os.path.join(OUT, 'pilot5.mp4'), '-frames:v', '1', '/tmp/_c.png'],
                       check=True)
        from PIL import Image
        a = np.asarray(Image.open('/tmp/_c.png').convert('RGB'), np.float32)
        x0, y0, x1, y1 = box
        reg = a[y0:y1, x0:x1].reshape(-1, 3)
        return int((reg.min(1) > 170).sum())
    before = corner_luma(23.00)
    after = corner_luma(29.00)
    res['logo'] = dict(file=rep['file'], native=list(rep['native']), mode=rep['mode'],
                       drawn_width_px=rep['drawn_width'],
                       aspect_native=round(rep['native'][0] / rep['native'][1], 4),
                       ivory_px_corner_23_0s=before,
                       ivory_px_corner_29_0s=after,
                       visible_after_26_3=bool(after > 2000 and after > before * 3))

    # ---- 3 text sfx
    meta = json.load(open(os.path.join(OUT, 'audio5_meta.json')))
    paper = [h for h in meta['hits'] if h['kind'] in ('paper_in', 'paper_out')]
    res['audio'] = dict(
        music_db_vs_vo=meta['music_db_vs_vo'], duck_depth_db=meta['duck_depth_db'],
        music_source=meta['music_src'],
        paper_hits=[dict(t=h['t'], db_vs_speech=h['vs_vo_speech'], dbfs=h['dbfs'])
                    for h in paper],
        paper_range_dB=[min(h['vs_vo_speech'] for h in paper),
                        max(h['vs_vo_speech'] for h in paper)],
        text_hits_in_band_12_18=bool(all(-18.0 <= h['vs_vo_speech'] <= -12.0
                                         for h in paper)),
        paper_under_music_dB=round(abs(meta['music_db_vs_vo']) -
                                   abs(np.mean([h['vs_vo_speech'] for h in paper])), 2),
        all_hits=meta['hits'])

    bpm, conf = tempo_of(os.path.join(OUT, 'pilot5_stem_music_ducked.wav'))
    res['music'] = dict(source='eng5/music5.py', bpm=round(bpm, 1),
                        autocorr=round(conf, 3),
                        bands_pct=band_energy(os.path.join(OUT, 'pilot5_stem_music_ducked.wav')),
                        in_95_120=bool(95 <= bpm <= 120))

    # ---- 5 pacing
    d = np.array([r['diff'] for r in rows[1:]], np.float32)
    ts = np.array([r['t'] for r in rows[1:]], np.float32)
    static = np.where(d < 0.30)[0]
    shots = {}
    for r in rows:
        shots.setdefault(r['shot'], []).append(r['t'])
    ev = sorted([e['t'] for e in P.EVENTS])
    gaps = [round(b - a, 2) for a, b in zip(ev, ev[1:])]
    res['pacing'] = dict(
        frames=len(rows), motion_mean=round(float(d.mean()), 3),
        motion_min=round(float(d.min()), 3), static_frames=int(len(static)),
        static_at=[round(float(ts[i]), 3) for i in static[:12]],
        cuts=[round(r['t'], 3) for r in rows if r['cut']],
        shot_lengths={k: round(max(v) - min(v) + 1 / 30, 2) for k, v in shots.items()},
        longest_shot_s=max(round(max(v) - min(v) + 1 / 30, 2) for v in shots.values()),
        layers_min=int(min(r['layers'] for r in rows)),
        events=len(ev), max_event_gap_s=max(gaps), gaps=gaps)

    res['transitions'] = {}
    for name, t in (('S2 dissolve', P.S2), ('S3 whip', P.S3), ('S4 in', P.S4),
                    ('S5 hard cut', P.S5), ('S6 hard cut', P.S6)):
        w = [i for i, x in enumerate(ts) if abs(x - t) < 0.45]
        if w:
            res['transitions'][name] = dict(peak_jump=round(float(d[w].max()), 2),
                                            mean_jump=round(float(d[w].mean()), 2))

    res['loudness'] = loudness(os.path.join(OUT, 'PILOT_CH1_00-30s_v5.mp4'))

    json.dump(res, open(os.path.join(OUT, 'QA_pilot5.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in res.items() if k != 'audio'}, indent=1,
                     ensure_ascii=False)[:3500])
    print('--- audio ---')
    print(json.dumps({k: v for k, v in res['audio'].items() if k != 'all_hits'}, indent=1,
                     ensure_ascii=False))
    return res


if __name__ == '__main__':
    main()
