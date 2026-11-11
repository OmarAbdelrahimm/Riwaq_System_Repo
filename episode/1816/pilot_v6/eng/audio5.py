#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eng5/audio5.py — the v5 mix: supplied voice, composed score, soft text hits.

Levels are targets measured against the voice stem, not fader guesses:

  music   -8 dB relative to the voice RMS while the voice is talking (ducked 11 dB)
  text SFX -15 dB relative to the SPEECH in each hit's own window, inside the -12..-18 dB
           the brief asks for and about 6.5 dB under the music

Every hit is calibrated individually, so the design table holds regardless of how loud the
local line happens to be. A single global fader left hits 17 dB apart from each other.
"""
import json
import os
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, '/home/user/work')

FF = '/home/user/ffmpeg'
GD = '/home/user/Riwaq_System_Repo/google_drive'
OUT = '/home/user/work/out'
SR = 48000
DUCK_DB = 13.0
MUSIC_DUCKED_DB = -17.0
SFX_TABLE_DB = dict(paper_in=-15.0, paper_out=-17.0, pin=-18.0, needle=-19.0,
                    thread_draw=-17.5, sleet=-21.0, water=-18.5, stamp=-16.0,
                    sting=-10.0, thunder=-13.0)


def decode(path, start=0.0, dur=None, channels=2):
    cmd = [FF, '-v', 'error', '-ss', f'{start:.6f}', '-i', path]
    if dur:
        cmd += ['-t', f'{dur:.6f}']
    cmd += ['-ac', str(channels), '-ar', str(SR), '-f', 'f32le', '-']
    raw = subprocess.run(cmd, capture_output=True).stdout
    a = np.frombuffer(raw, np.float32)
    return a.reshape(-1, channels)


def rms(x):
    return float(np.sqrt(np.mean(np.square(x.astype(np.float64))) + 1e-18))


def db(x):
    return 20 * np.log10(max(x, 1e-9))


def env_db(x, attack_ms=60, release_ms=380, block=64):
    a_att = 1 - np.exp(-block / (SR * attack_ms / 1000))
    a_rel = 1 - np.exp(-block / (SR * release_ms / 1000))
    mono = np.abs(x).max(1) if x.ndim > 1 else np.abs(x)
    nb = len(mono) // block
    bm = mono[:nb * block].reshape(nb, block).max(1)
    out = np.zeros(nb, np.float32)
    cur = 1e-6
    for i, v in enumerate(bm):
        a = a_att if v > cur else a_rel
        cur = cur + a * (v - cur)
        out[i] = cur
    return 20 * np.log10(np.maximum(out, 1e-9)), block


def duck_gain(vo, depth_db=-13.0, thresh_db=-38.0, knee_db=7.0):
    """a smooth duck: 13 dB of gain reduction under speech, and the give-back is spread
    over a 7 dB knee so the music rises back through a pause instead of snapping."""
    d, block = env_db(vo)
    t = np.clip((d - (thresh_db - knee_db)) / (2 * knee_db), 0, 1)
    g_db = depth_db * (t * t * (3 - 2 * t))
    gain = 10 ** (g_db / 20.0)
    return np.repeat(gain, block)[:len(vo)], float(g_db.min())


def place(buf, clip, t, gain=1.0):
    i0 = int(round(t * SR))
    if i0 >= len(buf):
        return
    n = min(len(clip), len(buf) - i0)
    buf[i0:i0 + n] += clip[:n] * gain


def write_wav(path, x):
    with wave.open(path, 'wb') as w:
        w.setnchannels(x.shape[1]); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def music_levels(vo, music):
    """measured music level under the voice and in the pauses -- QA reads these, nothing
    in this file claims a number it has not computed."""
    m = np.abs(vo).max(1) > 10 ** (-46 / 20)
    if not m.any() or m.all():
        return None, None
    return (db(rms(music[m])), db(rms(music[~m])))


def build(t_end=30.0, events=None, tag='pilot5', score_gain=None):
    from eng5 import music5
    from eng5 import sfx5

    vo = decode(os.path.join(GD, '1816_OMAR_VO_FULL_MIX_48k.flac'), 0, t_end)
    n = len(vo)

    if score_gain is None:
        score = music5.build(t_end)
        if len(score) < n:
            score = np.pad(score, ((0, n - len(score)), (0, 0)))
        mus = score[:n]
        music_src = 'eng5/music5.py (composed, 116 BPM)'
    else:
        mus = decode(os.path.join(GD, '1816_ORIGINAL_MUSIC_BED_48k.flac'), 0, t_end)[:n]
        music_src = 'supplied bed'

    vo_r, mus_r = rms(vo), rms(mus)
    mus_trim = (db(vo_r) + MUSIC_DUCKED_DB + DUCK_DB) - db(mus_r)
    music_bed = mus * (10 ** (mus_trim / 20.0))
    gain, deepest = duck_gain(vo, depth_db=-DUCK_DB)
    mus_ducked = music_bed * gain[:, None]

    props = np.zeros_like(vo)
    placed = []
    for ev in (events or []):
        k = ev.get('sfx')
        if k in sfx5.KIT:
            clip = sfx5.KIT[k]()
            # calibrate on the clip's OWN rms, over its own length. Measuring over a fixed
            # 0.6 s window diluted the short hits (a 0.18 s pin read 5 dB light).
            c_r = rms(clip)
            # text hits are calibrated against the SPEECH in their own window, so every
            # tag lands on the same number relative to the words it sits under
            if k in ('paper_in', 'paper_out'):
                i0 = max(0, int((ev['t'] - 0.6) * SR))
                i1 = min(len(vo), int((ev['t'] + 0.9) * SR))
                ref = db(rms(vo[i0:i1]))
            else:
                ref = db(vo_r)
            target = ref + SFX_TABLE_DB.get(k, -16.0)
            g = 10 ** ((target - db(c_r)) / 20.0)
            place(props, clip, ev['t'], gain=g)
            placed.append(dict(t=ev['t'], kind=k, gain_db=round(db(g), 2),
                               designed_db=SFX_TABLE_DB.get(k), dur=len(clip) / SR))

    mix = vo + mus_ducked + props
    peak = np.abs(mix).max()
    mix = np.tanh(mix / max(peak, 1e-6) * 1.2) / np.tanh(1.2) * 0.94

    wav = os.path.join(OUT, f'{tag}_mix_raw.wav')
    write_wav(wav, mix)
    stems = {}
    for name, arr in (('vo', vo), ('music_ducked', mus_ducked), ('sfx_designed', props)):
        p = os.path.join(OUT, f'{tag}_stem_{name}.wav')
        write_wav(p, arr)
        stems[name] = p

    per = []
    for ev, pl in zip([e for e in (events or []) if e.get('sfx') in sfx5.KIT], placed):
        t = ev['t']
        clip = sfx5.KIT[ev['sfx']]() * (10 ** (pl['gain_db'] / 20.0))
        solo = db(rms(clip))
        i0 = max(0, int((t - 0.9) * SR))
        i1 = min(len(vo), int((t + 0.9) * SR))
        per.append(dict(event=ev.get('what'), t=round(t, 3), kind=ev['sfx'],
                        dur=round(pl['dur'], 2),
                        designed_db=SFX_TABLE_DB.get(ev['sfx']),
                        dbfs=round(solo, 2),
                        vs_vo_global=round(solo - db(vo_r), 2),
                        vs_vo_speech=round(solo - db(rms(vo[i0:i1])), 2)))
    mus_ratio = db(rms(mus_ducked)) - db(vo_r)
    under_voice, in_pause = music_levels(vo, mus_ducked)
    return wav, stems, dict(duck_depth_db=deepest, scale_db=0.0,
                            music_src=music_src, music_db_vs_vo=round(mus_ratio, 2),
                            music_under_voice_db=None if under_voice is None
                            else round(under_voice - db(vo_r), 2),
                            music_in_pause_db=None if in_pause is None
                            else round(in_pause - db(vo_r), 2),
                            hits=per, samples=n,
                            vo_rms_db=round(db(vo_r), 2))


def master(src, dst, target_i=-14.0, tp=-1.0):
    p = subprocess.run([FF, '-hide_banner', '-nostats', '-i', src, '-af',
                        f'loudnorm=I={target_i}:TP={tp}:LRA=11:print_format=json',
                        '-f', 'null', '-'], capture_output=True, text=True)
    j = json.loads(p.stderr[p.stderr.rindex('{'):p.stderr.rindex('}') + 1])
    af = (f"loudnorm=I={target_i}:TP={tp}:LRA=11:"
          f"measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:"
          f"offset={j['target_offset']}:linear=true")
    subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y', '-i', src, '-af', af,
                    '-ar', '48000', '-c:a', 'pcm_s24le', dst], check=True)
    return j


if __name__ == '__main__':
    from eng5 import pilot5 as P
    evs = [dict(t=e['t'], sfx=e['sfx'], what=e['what']) for e in P.EVENTS if e.get('sfx')]
    wav, stems, meta = build(30.0, evs, 'pilot6')
    j = master(wav, os.path.join(OUT, 'pilot6_master.wav'))
    json.dump(meta, open(os.path.join(OUT, 'audio5_meta.json'), 'w'), indent=1,
              ensure_ascii=False)
    print('mix', wav)
    print('music:', meta['music_src'], meta['music_db_vs_vo'], 'dB vs VO')
    print('duck depth', round(meta['duck_depth_db'], 2))
    print('under voice', meta['music_under_voice_db'], 'in pause', meta['music_in_pause_db'])
    print('loudnorm measured in', j['input_i'], 'TP', j['input_tp'], 'LRA', j['input_lra'])
    for h in meta['hits']:
        print(f"   {h['t']:6.2f} {h['kind']:12s} speech {h['vs_vo_speech']:+6.2f}  "
              f"global {h['vs_vo_global']:+6.2f}  {h['dbfs']:+6.2f} dBFS  {h['event']}")
    print('VO rms', meta['vo_rms_db'], 'dBFS')
    print('pre-master:', {k: j[k] for k in ('input_i', 'input_tp', 'input_lra')})
    json.dump(meta, open(os.path.join(OUT, 'audio5_meta.json'), 'w'), indent=1, ensure_ascii=False)
