#!/usr/bin/env python3
"""Original music (procedural synthesis) + soft SFX + the mix versions.

Everything here is generated from code: no external samples, no third-party licences.
- Music: Hijaz modal colour on D (D Eb F# G A Bb C). Drone + pad + Karplus-Strong plucks (oud-like)
  + soft frame drum during the siege. Mood: dark-tension until the hypothesis moment, then warm-story,
  per brand.json sound.music_moods. Mood changes only at the hypothesis moment (acts as a chapter card).
- Ducking: −12 dB under speech (brand.json duck_db) from the word timestamps.
- SFX: brand items (impact_soft, riser, page_turn, ui_tick, shimmer, whoosh) synthesized softly.
- Mixes: master (−14 LUFS / TP −1), no-voice (music + SFX), SFX-only.
"""
import json, pathlib, subprocess, sys, re
import numpy as np, soundfile as sf
from scipy.signal import fftconvolve, butter, sosfilt

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
EXP = REPO / "exports" / ROOT.name
AUD = EXP / "audio"
SR = 48000
rng = np.random.default_rng(1258)
FF = "/tmp/ffmpeg"


def hz(midi): return 440.0 * 2 ** ((midi - 69) / 12)

D2, A2, D3 = 38, 45, 50
HIJAZ = [62, 63, 66, 67, 69, 70, 72, 74]          # D4 Eb F# G A Bb C D5
WARM = [62, 64, 66, 67, 69, 71, 73, 74]           # D major (warm-story)


def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, "low", fs=SR, output="sos"), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), x)


def env_adsr(n, a=0.5, r=1.0):
    e = np.ones(n); na = min(n, int(a * SR)); nr = min(n - na, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    if nr > 0: e[-nr:] *= np.linspace(1, 0, nr)
    return e


def ks_pluck(freq, dur=2.6, bright=0.5, decay=0.996):
    n = int(dur * SR); N = max(2, int(SR / freq))
    buf = lp(rng.uniform(-1, 1, N), 1200 + 5000 * bright, 1)
    y = np.zeros(n); y[:N] = buf
    k = N
    while k < n:
        m = min(N, n - k)
        prev = y[k - N:k - N + m + 1]
        if len(prev) < m + 1: prev = np.append(prev, prev[-1])
        y[k:k + m] = decay * 0.5 * (prev[:m] + prev[1:m + 1])
        k += m
    body = lp(y, 2600, 2) + 0.3 * hp(y, 900, 1)       # oud-like body: dark, a bit nasal
    return body * np.exp(-np.arange(n) / (SR * 1.1))


def pad_tone(freqs, n, detune=0.25, bright=900):
    t = np.arange(n) / SR; L = np.zeros(n); R = np.zeros(n)
    for j, f in enumerate(freqs):
        g = 1 / (1 + 0.6 * j)
        for d, ch in ((-detune, L), (detune, R)):
            ph = 2 * np.pi * (f + d) * t + rng.uniform(0, 6.28)
            ch += g * (np.sin(ph) + 0.22 * np.sin(2 * ph) + 0.08 * np.sin(3 * ph))
    trem = 0.88 + 0.12 * np.sin(2 * np.pi * 0.11 * t)
    return lp(L * trem, bright), lp(R * trem, bright)


def frame_drum(n_len=1.2, pitch=72):
    n = int(n_len * SR); t = np.arange(n) / SR
    f = pitch + 40 * np.exp(-t / 0.03)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.28)
    skin = lp(rng.uniform(-1, 1, n), 1800) * np.exp(-t / 0.025) * 0.5
    return np.tanh(1.3 * (body + skin))


def reverb(L, R, seconds=2.8, wet=0.28):
    n = int(seconds * SR); t = np.arange(n) / SR
    irL = rng.standard_normal(n) * np.exp(-t / (seconds / 6.5)); irR = rng.standard_normal(n) * np.exp(-t / (seconds / 6.5))
    irL = lp(irL, 5000); irR = lp(irR, 5000); irL /= np.abs(irL).sum() ** 0.5 * 6; irR /= np.abs(irR).sum() ** 0.5 * 6
    wL = fftconvolve(L, irL)[: len(L)]; wR = fftconvolve(R, irR)[: len(R)]
    return L * (1 - wet) + wL * wet * 3, R * (1 - wet) + wR * wet * 3


def music(duration, sections, drum_spans, shimmer_at, seed_phrase=0):
    """sections: [(t0, t1, mood)]"""
    n = int(duration * SR); L = np.zeros(n); R = np.zeros(n); t = np.arange(n) / SR
    # drone (whole piece) with slow breathing and section-aware level
    dr = np.zeros(n)
    for f, g in ((hz(D2), 0.5), (hz(A2), 0.28), (hz(D3), 0.18)):
        dr += g * (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t))
    dr = lp(dr, 420) * (0.75 + 0.25 * np.sin(2 * np.pi * t / 23.0))
    L += dr * 0.55; R += dr * 0.55
    for (t0, t1, mood) in sections:
        i0, i1 = int(t0 * SR), min(n, int(t1 * SR)); m = i1 - i0
        if m <= 0: continue
        prog = ([[62, 63, 66, 69], [55, 58, 62, 67], [62, 66, 69, 72], [58, 62, 65, 70]] if mood == "tension"
                else [[62, 66, 69, 74], [55, 59, 62, 67], [59, 62, 66, 71], [57, 61, 64, 69]])
        if mood == "suspend": prog = [[62, 69, 74]]
        step = 12.0 if mood != "suspend" else 999
        k = 0; s = i0
        while s < i1:
            e = min(i1, s + int(step * SR)); ln = e - s
            if ln < SR // 4: break
            chord = prog[k % len(prog)]; k += 1
            pl, pr = pad_tone([hz(c - 12) for c in chord], ln, bright=700 if mood == "tension" else 1100)
            ev = env_adsr(ln, 2.5, 2.5)
            g = 0.16 if mood != "suspend" else 0.10
            L[s:e] += pl * ev * g; R[s:e] += pr * ev * g
            s = e
        # plucked phrases
        scale = HIJAZ if mood == "tension" else WARM
        if mood != "suspend":
            tt = t0 + 3.0; ph = 0
            while tt < t1 - 3:
                phrase = [scale[i] for i in ([4, 3, 2, 1, 0] if ph % 2 == 0 else [0, 1, 2, 4, 3, 2])]
                if mood != "tension": phrase = [scale[i] for i in ([2, 4, 5, 4, 2] if ph % 2 == 0 else [4, 5, 7, 5, 4, 2])]
                dt = 0.42 if mood == "tension" else 0.5
                for j, note in enumerate(phrase):
                    p = ks_pluck(hz(note - 12), bright=0.35 + 0.1 * (j % 2))
                    a = int((tt + j * dt + rng.uniform(-0.02, 0.02)) * SR)
                    b = min(n, a + len(p))
                    if a >= n: break
                    pan = 0.5 + 0.25 * np.sin(j)
                    L[a:b] += p[: b - a] * 0.22 * (1 - pan) * 2; R[a:b] += p[: b - a] * 0.22 * pan * 2
                tt += 9.0 + rng.uniform(-1, 2) if mood == "tension" else 8.0 + rng.uniform(-1, 1.5); ph += 1
    # frame drum heartbeat
    for (t0, t1) in drum_spans:
        bt = t0
        while bt < t1:
            for off, g in ((0, 0.35), (0.42, 0.18)):
                d = frame_drum(); a = int((bt + off) * SR); b = min(n, a + len(d))
                if a < n: L[a:b] += d[: b - a] * g; R[a:b] += d[: b - a] * g
            bt += 1.25
    for at in shimmer_at:
        sh = shimmer(2.2); a = int(at * SR); b = min(n, a + len(sh))
        L[a:b] += sh[: b - a] * 0.25; R[a:b] += sh[: b - a] * 0.25
    L, R = reverb(L, R)
    fade = int(3 * SR); L[-fade:] *= np.linspace(1, 0, fade); R[-fade:] *= np.linspace(1, 0, fade)
    f_in = int(1.5 * SR); L[:f_in] *= np.linspace(0, 1, f_in); R[:f_in] *= np.linspace(0, 1, f_in)
    return np.stack([L, R], 1)


# ---------- SFX (soft only) ----------
def bandnoise(n, f0, f1, q=1.0):
    x = rng.uniform(-1, 1, n); out = np.zeros(n); seg = 2048
    for s in range(0, n, seg):
        fc = f0 * (f1 / f0) ** (s / max(1, n)); lo = max(40, fc / (1 + q)); hi = min(SR / 2.2, fc * (1 + q))
        sos = butter(2, [lo, hi], "band", fs=SR, output="sos")
        out[s:s + seg] = sosfilt(sos, x[max(0, s - 512):s + seg])[-len(x[s:s + seg]):]
    return out


def whoosh(d=0.9): n = int(d * SR); return bandnoise(n, 300, 2400) * np.sin(np.pi * np.linspace(0, 1, n)) ** 2


def riser(d=3.0):
    n = int(d * SR); x = np.linspace(0, 1, n)
    tone = np.sin(2 * np.pi * np.cumsum(180 * 4 ** x) / SR) * 0.3
    return (bandnoise(n, 250, 4000, 0.6) + tone) * x ** 2.2 * np.minimum(1, (n - np.arange(n)) / (0.03 * SR))


def impact_soft(d=1.6):
    n = int(d * SR); t = np.arange(n) / SR
    f = 42 + 55 * np.exp(-t / 0.08)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.45) + lp(rng.uniform(-1, 1, n), 900) * np.exp(-t / 0.06) * 1.2
    return np.tanh(1.2 * s)


def page_turn(d=0.7):
    n = int(d * SR); t = np.arange(n) / SR
    rust = bandnoise(n, 2500, 1200, 1.2) * (np.sin(np.pi * t / d) ** 1.5)
    flick = bandnoise(n, 4000, 3000, 0.8) * np.exp(-((t - d * 0.7) / 0.03) ** 2)
    return rust * 0.8 + flick


def ui_tick(f=1500, d=0.06):
    n = int(d * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.012) + rng.uniform(-1, 1, n) * np.exp(-t / 0.0015) * 0.4


def shimmer(d=2.2):
    n = int(d * SR); t = np.arange(n) / SR; out = np.zeros(n)
    for j, m in enumerate([74, 78, 81, 86]):
        f = hz(m); out += np.sin(2 * np.pi * f * t + j) * np.exp(-t / 0.9) * np.minimum(1, t / 0.15) / (1 + 0.4 * j)
        out += 0.15 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.2)
    return out * 0.6


def sonic_logo(d=2.4):
    n = int(d * SR); out = np.zeros(n)
    for j, m in enumerate([62, 63, 66, 69, 74]):
        p = ks_pluck(hz(m - 12), dur=1.8, bright=0.45); a = int(j * 0.16 * SR); b = min(n, a + len(p)); out[a:b] += p[: b - a] * (0.8 if j < 4 else 1.0)
    dr = frame_drum(); out[int(0.64 * SR):int(0.64 * SR) + len(dr)] += dr[: n - int(0.64 * SR)] * 0.5
    return out


SFX = {"impact_soft": impact_soft, "riser": riser, "page_turn": page_turn, "ui_tick": ui_tick, "shimmer": shimmer, "whoosh": whoosh, "SONIC_LOGO": sonic_logo}
GAIN = {"impact_soft": 0.35, "riser": 0.18, "page_turn": 0.30, "ui_tick": 0.22, "shimmer": 0.20, "whoosh": 0.12, "SONIC_LOGO": 0.45}


def place(buf, x, at, g, pan=0.5):
    a = int(at * SR); b = min(len(buf), a + len(x))
    if a < 0 or a >= len(buf): return
    buf[a:b, 0] += x[: b - a] * g * (1 - pan) * 2 ** 0.5; buf[a:b, 1] += x[: b - a] * g * pan * 2 ** 0.5


def sfx_events_long(scenes, meta):
    ev = []
    by = {s["id"]: s for s in scenes}
    for sc in meta["scenes"]:
        t0 = by[sc["id"]]["t_in"]; txt = sc["sfx"]
        if "riser" in txt and "impact" in txt:
            ev.append(("riser", t0 + 0.2)); ev.append(("impact_soft", t0 + 3.2)); continue
        if "SONIC_LOGO" in txt: ev.append(("SONIC_LOGO", t0 + 0.3)); continue
        m = re.search(r"ui_tick\s*[×x]\s*(\d)", txt)
        if m:
            for k in range(int(m.group(1))): ev.append(("ui_tick", t0 + 0.6 + k * 1.6))
            continue
        for key in ("impact_soft", "riser", "page_turn", "ui_tick", "shimmer", "whoosh"):
            if key in txt:
                ev.append((key, t0 + (0.0 if key in ("impact_soft", "page_turn", "whoosh") else 0.3)))
    return ev


def duck_env(words, n, duck_db=-12, attack=0.12, release=0.35):
    active = np.zeros(n, dtype=bool)
    for w in words:
        a, b = int((w["t0"] - 0.08) * SR), int((w["t1"] + 0.1) * SR); active[max(0, a):min(n, b)] = True
    target = np.where(active, 10 ** (duck_db / 20), 1.0)
    # smooth with one-pole in blocks (10 ms) for speed
    hop = SR // 100; tb = target[::hop]; g = np.empty_like(tb); cur = 1.0
    for i, v in enumerate(tb):
        c = 1 - np.exp(-0.01 / (attack if v < cur else release)); cur += (v - cur) * c; g[i] = cur
    return np.repeat(g, hop)[:n]


def ffloud(src, dst, I, TP=-1.0, LRA=11):
    m = subprocess.run([FF, "-hide_banner", "-i", str(src), "-af", f"loudnorm=I={I}:TP={TP}:LRA={LRA}:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    js = json.loads(m[m.rfind("{"): m.rfind("}") + 1])
    af = (f"loudnorm=I={I}:TP={TP}:LRA={LRA}:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}:"
          f"measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
    subprocess.run([FF, "-hide_banner", "-y", "-i", str(src), "-af", af, "-ar", str(SR), "-c:a", "pcm_s24le", str(dst)], check=True, capture_output=True)


def build(kind):
    meta = json.loads((ROOT / "script_scenes.json").read_text(encoding="utf-8"))
    if kind == "long":
        tl = json.loads((ROOT / "timeline.json").read_text(encoding="utf-8")); dur = tl["duration_s"]
        sc = {s["id"]: s for s in tl["scenes"]}
        turn = sc["14"]["t_in"]; close = sc["26"]["t_in"]
        sections = [(0, turn, "tension"), (turn, sc["15"]["t_in"], "suspend"), (sc["15"]["t_in"], close, "warm"), (close, dur, "tension")]
        drums = [(sc["09"]["t_in"], sc["13"]["t_in"])]
        mus = music(dur, sections, drums, shimmer_at=[])
        events = sfx_events_long(tl["scenes"], meta); words = tl["words"]; voice = AUD / "voice_full.wav"; tag = ""
    else:
        tl = json.loads((ROOT / "timeline_short.json").read_text(encoding="utf-8")); dur = tl["duration_s"]; b = tl["beats"]
        sections = [(0, b[4]["t_in"], "tension"), (b[4]["t_in"], b[6]["t_in"], "suspend"), (b[6]["t_in"], dur, "warm")]
        mus = music(dur, sections, [], shimmer_at=[])
        events = [("impact_soft", 0.05), ("shimmer", b[4]["t_in"] + 0.1), ("impact_soft", b[8]["t_in"]), ("ui_tick", b[11]["t_in"] + 0.2), ("SONIC_LOGO", b[-1]["t_in"] + 0.6)]
        words = tl["words"]; voice = AUD / "voice_short.wav"; tag = "_short"
    n = int(dur * SR)
    mus = mus[:n]
    if len(mus) < n: mus = np.pad(mus, ((0, n - len(mus)), (0, 0)))
    mus /= np.max(np.abs(mus)) + 1e-9; mus *= 0.5
    sfx = np.zeros((n, 2))
    for k, (name, at) in enumerate(events):
        place(sfx, SFX[name](), at, GAIN[name], pan=0.5 + (0.12 if k % 2 else -0.12) * (name == "ui_tick"))
    v, _ = sf.read(voice); v = v[:n] if len(v) >= n else np.pad(v, (0, n - len(v)))
    g = duck_env(words, n)
    # music stem ≈ −20 LUFS standalone → ≈ −32 LUFS under speech after the −12 dB duck
    mus_level = 10 ** (-3.5 / 20)
    mix = np.stack([v, v], 1) * 1.0 + mus * mus_level * g[:, None] + sfx
    sf.write(AUD / f"music{tag}.wav", mus * mus_level, SR, subtype="PCM_24")
    sf.write(AUD / f"music_ducked{tag}.wav", mus * mus_level * g[:, None], SR, subtype="PCM_24")
    sf.write(AUD / f"sfx{tag}.wav", sfx, SR, subtype="PCM_24")
    sf.write(EXP / "tmp" / f"mix_raw{tag}.wav", mix, SR, subtype="PCM_24")
    sf.write(EXP / "tmp" / f"nv_raw{tag}.wav", mus * mus_level + sfx, SR, subtype="PCM_24")
    ffloud(EXP / "tmp" / f"mix_raw{tag}.wav", AUD / f"mix_master{tag}.wav", -14, -1.0)
    ffloud(EXP / "tmp" / f"nv_raw{tag}.wav", AUD / f"mix_no_voice{tag}.wav", -16, -1.0)
    pk = np.max(np.abs(sfx)) + 1e-9
    sf.write(AUD / f"mix_sfx_only{tag}.wav", sfx / pk * 10 ** (-3 / 20), SR, subtype="PCM_24")
    json.dump({"events": events, "sections": sections}, open(EXP / "tmp" / f"audio_events{tag}.json", "w"), ensure_ascii=False, indent=1)
    print(kind, "done", round(dur, 2), "s; sfx events", len(events))


if __name__ == "__main__":
    for k in (sys.argv[1:] or ["long", "short"]): build(k)
