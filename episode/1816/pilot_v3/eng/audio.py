#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
eng/audio.py — the pilot mix, built from the three supplied stems.

What the stems actually are (measured, not assumed):
  VO     -16.60 LUFS, full length, 48 kHz
  MUSIC  -28.68 LUFS, full length
  SFX    -44.36 LUFS, a CONTINUOUS bed: onset analysis found no discrete transients, so
         the cue sheet's stamp / pin / thread hits do not exist as material in it.
         Those prop sounds are therefore DESIGNED here and labelled designed in the
         report; everything else comes from the stems.

Music is sidechain-ducked 11 dB under the voice (inside the 10-12 dB brief), the SFX
bed sits under both, and the sum is mastered to -14 LUFS / -1 dBTP.
"""
import json, os, subprocess, sys
import numpy as np

FF = '/home/user/ffmpeg'
GD = '/home/user/Riwaq_System_Repo/google_drive'
OUT = '/home/user/work/out'
SR = 48000
MUSIC_BED_UNDER_VO_DB = 8.0
DUCK_DB = 11.0
SFX_BED_UNDER_VO_DB = 22.0


def decode(path, start=0.0, dur=None, channels=2):
    cmd = [FF, '-v', 'error', '-ss', f'{start:.6f}', '-i', path]
    if dur:
        cmd += ['-t', f'{dur:.6f}']
    cmd += ['-ac', str(channels), '-ar', str(SR), '-f', 'f32le', '-']
    raw = subprocess.run(cmd, capture_output=True).stdout
    a = np.frombuffer(raw, np.float32)
    return a.reshape(-1, channels)


def env_db(x, attack_ms=60, release_ms=380, block=64):
    n = len(x)
    a_att = 1 - np.exp(-block / (SR * attack_ms / 1000))
    a_rel = 1 - np.exp(-block / (SR * release_ms / 1000))
    mono = np.abs(x).max(1) if x.ndim > 1 else np.abs(x)
    nb = n // block
    bm = mono[:nb * block].reshape(nb, block).max(1)
    out = np.zeros(nb, np.float32)
    cur = 1e-6
    for i, v in enumerate(bm):
        a = a_att if v > cur else a_rel
        cur = cur + a * (v - cur)
        out[i] = cur
    return 20 * np.log10(np.maximum(out, 1e-9)), block


def duck_gain(vo, depth_db=-11.0, thresh_db=-40.0, knee_db=8.0):
    db, block = env_db(vo)
    t = np.clip((db - (thresh_db - knee_db)) / (2 * knee_db), 0, 1)
    g_db = depth_db * (t * t * (3 - 2 * t))
    gain = 10 ** (g_db / 20.0)
    idx = np.repeat(gain, block)
    if len(idx) < len(vo):
        idx = np.concatenate([idx, np.full(len(vo) - len(idx), idx[-1] if len(idx) else 1.0)])
    return idx[:len(vo)].astype(np.float32), float(np.min(g_db)) if len(g_db) else 0.0


# ---------------------------------------------------------------- designed SFX
def sfx_stamp(dur=0.42):
    """rubber stamp on paper: a low thud, a paper slap, a brief crinkle"""
    n = int(dur * SR)
    rng = np.random.default_rng(1)
    t = np.arange(n) / SR
    thud = np.sin(2 * np.pi * 92 * t) * np.exp(-t * 26)
    slap = rng.normal(0, 1, n) * np.exp(-t * 55) * 0.55
    cr = rng.normal(0, 1, n) * np.exp(-((t - 0.03) ** 2) / (2 * 0.012 ** 2)) * 0.28
    x = (thud * 0.8 + slap + cr).astype(np.float32)
    return np.stack([x, x], 1) * 0.5


def sfx_pin(dur=0.30):
    """brass pin into paper: a tick, then a small metallic ring"""
    n = int(dur * SR)
    rng = np.random.default_rng(2)
    t = np.arange(n) / SR
    tick = rng.normal(0, 1, n) * np.exp(-t * 300) * 0.7
    ring = (np.sin(2 * np.pi * 2350 * t) * 0.35 +
            np.sin(2 * np.pi * 3170 * t) * 0.2) * np.exp(-t * 18)
    x = (tick + ring).astype(np.float32) * 0.55
    return np.stack([x, x], 1)


def sfx_paper_slide(dur=0.55):
    """paper dragged across a table"""
    n = int(dur * SR)
    rng = np.random.default_rng(3)
    t = np.arange(n) / SR
    nz = rng.normal(0, 1, n)
    b = np.convolve(nz, np.ones(6) / 6, 'same') - np.convolve(nz, np.ones(90) / 90, 'same')
    # a slide is a swell: shape it so it ATTACKS on the cue instead of peaking 140 ms
    # later, or the sound is late against the picture by definition
    e = np.exp(-t * 8.0) * (1 - np.exp(-t * 900.0)) + 0.18 * np.sin(np.pi * t / dur) ** 2
    x = (b * e).astype(np.float32)
    x /= max(1e-6, np.abs(x).max())
    return np.stack([x, x], 1) * 0.34


def sfx_thread(dur=0.9):
    """a taut thread pulled: rising sine with a paper-thin bow"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 420 + 700 * (t / dur) ** 1.6
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = ((np.sin(ph) * 0.35 + np.sin(2 * ph) * 0.12) * np.exp(-t * 1.6)).astype(np.float32)
    return np.stack([x, x], 1) * 0.4


def sfx_sting(dur=1.2):
    """brand sting: a low struck bell plus a paper shimmer"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n, np.float32)
    for k, amp in ((1, 0.5), (2, 0.22), (3, 0.12), (4.2, 0.06)):
        x += amp * np.sin(2 * np.pi * 148.0 * k * t) * np.exp(-t * (2.6 - 0.35 * k))
    rng = np.random.default_rng(5)
    x = (x + rng.normal(0, 1, n) * np.exp(-t * 6) * 0.08).astype(np.float32)
    return np.stack([x, x], 1) * 0.42


def sfx_needle(dur=0.35):
    """a thermometer meniscus dropping: a glass tick and a small falling tone"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    tick = np.random.default_rng(7).normal(0, 1, n) * np.exp(-t * 420) * 0.55
    f = 1900 * np.exp(-t * 6.5)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 13) * 0.30
    x = (tick + tone).astype(np.float32)
    return np.stack([x, x], 1)


def sfx_sleet(dur=0.9):
    """sleet arriving: fine gritty noise that swells then settles"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(11)
    nz = rng.normal(0, 1, n)
    hi = nz - np.convolve(nz, np.ones(8) / 8, 'same')
    e = np.clip(np.sin(np.pi * t / dur), 0, 1) ** 0.8
    x = (hi * e).astype(np.float32)
    x /= max(1e-6, np.abs(x).max())
    return np.stack([x, x], 1) * 0.22


def sfx_water(dur=1.2):
    """water rising across grass: a low wet swell"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(13)
    nz = rng.normal(0, 1, n)
    lo = np.convolve(nz, np.ones(160) / 160, 'same')
    e = np.clip(np.sin(np.pi * t / dur), 0, 1) ** 1.3
    x = (lo * e * 3.2).astype(np.float32)
    x /= max(1e-6, np.abs(x).max())
    return np.stack([x, x], 1) * 0.30


DESIGNED = {'stamp': sfx_stamp, 'needle': sfx_needle, 'sleet': sfx_sleet,
            'water': sfx_water, 'pin': sfx_pin, 'paper_drop': sfx_paper_slide,
            'paper_slide': sfx_paper_slide, 'thread_draw': sfx_thread, 'sting': sfx_sting}


def place(buf, clip, t, gain=1.0):
    i0 = int(round(t * SR))
    if i0 >= len(buf):
        return
    n = min(len(clip), len(buf) - i0)
    buf[i0:i0 + n] += clip[:n] * gain


def lufs(x):
    """integrated loudness via ffmpeg's meter — never estimated"""
    import tempfile, wave
    p = tempfile.mktemp(suffix='.wav')
    with wave.open(p, 'wb') as w:
        w.setnchannels(x.shape[1]); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    r = subprocess.run([FF, '-hide_banner', '-nostats', '-i', p, '-af',
                        'loudnorm=print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True)
    os.unlink(p)
    e = r.stderr
    return float(json.loads(e[e.rindex('{'):e.rindex('}') + 1])['input_i'])


def build(t_end=30.0, events=None, tag='pilot', vo_gain_db=2.4):
    os.makedirs(OUT, exist_ok=True)
    vo = decode(os.path.join(GD, '1816_OMAR_VO_FULL_MIX_48k.flac'), 0, t_end)
    mus = decode(os.path.join(GD, '1816_ORIGINAL_MUSIC_BED_48k.flac'), 0, t_end)
    sfx = decode(os.path.join(GD, '1816_ORIGINAL_SFX_STEM_48k.flac'), 0, t_end)
    n = min(len(vo), len(mus), len(sfx))
    vo, mus, sfx = vo[:n], mus[:n], sfx[:n]

    vo_lufs = lufs(vo)
    mus_lufs = lufs(mus)
    bed_trim_db = (vo_lufs - MUSIC_BED_UNDER_VO_DB) - mus_lufs
    music_bed = mus * (10 ** (bed_trim_db / 20.0))
    gain, deepest = duck_gain(vo, depth_db=-DUCK_DB)
    mus_ducked = music_bed * gain[:, None]
    sfx_lufs = lufs(sfx)
    sfx_trim_db = (vo_lufs - SFX_BED_UNDER_VO_DB) - sfx_lufs
    sfx = sfx * (10 ** (sfx_trim_db / 20.0))

    props = np.zeros_like(vo)
    placed = []
    for ev in (events or []):
        kind = ev.get('sfx')
        if kind in DESIGNED:
            place(props, DESIGNED[kind](), ev['t'], gain=1.0)
            placed.append(dict(t=ev['t'], kind=kind))

    mix = vo * (10 ** (vo_gain_db / 20.0)) + mus_ducked + sfx + props * 0.55
    peak = np.abs(mix).max()
    mix = np.tanh(mix / max(peak, 1e-6) * 1.35) / np.tanh(1.35) * 0.94
    wav = os.path.join(OUT, f'{tag}_mix_raw.wav')
    import wave
    with wave.open(wav, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
    stems = {}
    for name, arr in (('vo', vo * (10 ** (vo_gain_db / 20.0))), ('music_ducked', mus_ducked),
                      ('sfx_stem', sfx), ('sfx_designed', props)):
        p = os.path.join(OUT, f'{tag}_stem_{name}.wav')
        with wave.open(p, 'wb') as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((np.clip(arr, -1, 1) * 32767).astype(np.int16).tobytes())
        stems[name] = p
    return wav, stems, dict(duck_depth_db=deepest, placed=placed, samples=n,
                           bed_trim_db=bed_trim_db, sfx_trim_db=sfx_trim_db,
                           vo_lufs=vo_lufs, mus_lufs=mus_lufs, sfx_lufs=sfx_lufs)


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
    sys.path.insert(0, '/home/user/work')
    import eng.pilot as P
    shots = P.build_shots()
    evs = [dict(t=r['t'], sfx=r['sfx'], shot=r['shot']) for r in P.events_table(shots)]
    wav, stems, meta = build(30.0, evs, 'pilot')
    print('raw mix', wav, 'duck depth', round(meta['duck_depth_db'], 2), 'dB')
    j = master(wav, os.path.join(OUT, 'PILOT_mix_master.wav'))
    print('pre-master measured:', {k: j[k] for k in ('input_i', 'input_tp', 'input_lra')})
