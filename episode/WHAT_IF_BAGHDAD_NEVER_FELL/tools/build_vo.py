#!/usr/bin/env python3
"""Assemble and finish the VO for the long video and the Short.

- Per clip: atrim (leading/trailing silence) + atempo (pitch preserved), then placement on the timeline from timeline.json.
- Short: keep the vo_keep_segments_src_s segments, then the same tempo.
- Finish chain (ffmpeg): HPF + light EQ + compression + two-pass loudnorm → -16 LUFS / TP -1.5.
Outputs to exports/<EP>/audio/: voice_full.wav, voice_short.wav (48 kHz, mono, 24-bit).
"""
import json, subprocess, pathlib, os, re, sys
import numpy as np, soundfile as sf

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
EXP = REPO / "exports" / ROOT.name
FFD = REPO / "node_modules" / "@remotion" / "compositor-linux-x64-gnu"
def _ffbin():
    try:
        import imageio_ffmpeg  # full static ffmpeg from PyPI (the Remotion build lacks audio filters)
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return str(FFD / "ffmpeg")
FF = _ffbin()
ENV = dict(os.environ)
SR = 48000


def ff(*args):
    r = subprocess.run([FF, "-hide_banner", "-y", *args], env=ENV, capture_output=True, text=True)
    if r.returncode: sys.exit(r.stderr[-2000:])
    return r.stderr


def tempo_clip(src, a, b, tempo, dst):
    ff("-i", str(src), "-af", f"atrim={a}:{b},asetpts=PTS-STARTPTS,atempo={tempo}", "-ar", str(SR), "-ac", "1", str(dst))
    x, _ = sf.read(dst); return x


def finish(raw_path, out_path, chain, target=-16.0, tp=-1.5):
    pre = chain.split(",loudnorm")[0]
    m = ff("-i", str(raw_path), "-af", f"{pre},loudnorm=I={target}:TP={tp}:LRA=7:print_format=json", "-f", "null", "-")
    js = json.loads(m[m.rfind("{"): m.rfind("}") + 1])
    ln = (f"loudnorm=I={target}:TP={tp}:LRA=7:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
    ff("-i", str(raw_path), "-af", f"{pre},{ln}", "-ar", str(SR), "-c:a", "pcm_s24le", str(out_path))
    return js


def main():
    cfg = json.loads((ROOT / "tools" / "audio_cfg.json").read_text(encoding="utf-8"))
    tl = json.loads((ROOT / "timeline.json").read_text(encoding="utf-8"))
    meta = json.loads((ROOT / "script_scenes.json").read_text(encoding="utf-8"))
    tempo = cfg["tempo"]; tmp = EXP / "tmp"; tmp.mkdir(parents=True, exist_ok=True)
    out = EXP / "audio"; out.mkdir(parents=True, exist_ok=True)
    # long
    buf = np.zeros(int(tl["duration_s"] * SR) + SR)
    for c in tl["clips"]:
        x = tempo_clip(EXP / "vo" / c["file"], c["src_in"], c["src_out"], tempo, tmp / f"t_{c['file']}")
        i0 = int(round(c["t_in"] * SR)); buf[i0:i0 + len(x)] += x
    buf = buf[: int(tl["duration_s"] * SR)]
    sf.write(tmp / "vo_long_raw.wav", buf, SR, subtype="PCM_24")
    j1 = finish(tmp / "vo_long_raw.wav", out / "voice_full.wav", cfg["vo_chain"])
    # short
    parts = []
    for k, (a, b) in enumerate(meta["short"]["vo_keep_segments_src_s"]):
        x = tempo_clip(EXP / "vo" / "SHORT.wav", a, b, tempo, tmp / f"s_{k}.wav")
        f = int(0.012 * SR); x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)  # click-free edits
        parts.append(x); parts.append(np.zeros(int(0.06 * SR)))
    sh = np.concatenate([np.zeros(int(0.3 * SR))] + parts[:-1] + [np.zeros(int(1.6 * SR))])
    sf.write(tmp / "vo_short_raw.wav", sh, SR, subtype="PCM_24")
    sf.write(tmp / "vo_short_edit_only.wav", np.concatenate(parts[:-1]), SR)
    j2 = finish(tmp / "vo_short_raw.wav", out / "voice_short.wav", cfg["vo_chain"], target=-15.0)
    print("long", round(len(buf) / SR, 2), "s in_I", j1["input_i"], "| short", round(len(sh) / SR, 2), "s in_I", j2["input_i"])


if __name__ == "__main__":
    main()
