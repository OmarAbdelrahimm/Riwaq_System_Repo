#!/usr/bin/env python3
"""Analyze a reference video: cuts, motion, palette, audio, optional ASR.

Usage: ref_analyze.py <video> <outdir>
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

VIDEO = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def probe(path):
    r = run(["ffprobe", "-v", "error", "-print_format", "json",
             "-show_format", "-show_streams", str(path)])
    return json.loads(r.stdout)


def fmt_t(t):
    m, s = divmod(t, 60)
    return f"{int(m):02d}:{s:05.2f}"


# ---------------------------------------------------------------- probe
info = probe(VIDEO)
vdur = float(info["format"]["duration"])
vstream = next(s for s in info["streams"] if s["codec_type"] == "video")
astream = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
W, H = vstream["width"], vstream["height"]
FPS = eval(vstream["r_frame_rate"]) if "/" in vstream["r_frame_rate"] else float(vstream["r_frame_rate"])

report = {
    "file": VIDEO.name,
    "duration_s": round(vdur, 2),
    "size_mb": round(int(info["format"]["size"]) / 1048576, 2),
    "resolution": [W, H],
    "aspect": round(W / H, 3),
    "orientation": "vertical" if H > W else ("square" if H == W else "horizontal"),
    "fps": round(FPS, 2),
    "vcodec": vstream.get("codec_name"),
    "bitrate_kbps": round(int(info["format"]["bit_rate"]) / 1000),
    "audio": None if not astream else {
        "codec": astream.get("codec_name"),
        "channels": astream.get("channels"),
        "sample_rate": astream.get("sample_rate"),
        "bitrate_kbps": round(int(astream.get("bit_rate", 0)) / 1000) if astream.get("bit_rate") else None,
    },
}

# ---------------------------------------------------------------- scene cuts
r = run(["ffmpeg", "-hide_banner", "-i", str(VIDEO),
         "-vf", "select='gt(scene,0.22)',showinfo", "-an", "-f", "null", "-"])
cuts = [round(float(m), 2) for m in re.findall(r"pts_time:([0-9.]+)", r.stderr)]
cuts = sorted(set(cuts))
boundaries = [0.0] + cuts + [round(vdur, 2)]
shots = []
for i in range(len(boundaries) - 1):
    shots.append({"index": i + 1, "start": boundaries[i], "end": boundaries[i + 1],
                  "dur": round(boundaries[i + 1] - boundaries[i], 2)})
report["cut_count"] = len(cuts)
report["cuts_s"] = cuts
report["avg_shot_s"] = round(sum(s["dur"] for s in shots) / len(shots), 2)
report["shots"] = shots

# ---------------------------------------------------------------- frame decode (small, for motion+palette)
SMALL_W = 192
r = run(["ffmpeg", "-hide_banner", "-i", str(VIDEO),
         "-vf", f"scale={SMALL_W}:-2", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"])
raw = r.stdout
if isinstance(raw, str):
    raw = raw.encode("latin-1")
frame_size = SMALL_W * (H * SMALL_W // W // 2 * 2) * 3
# compute actual height from ffmpeg auto: safer to re-decode with explicit size
h_small = int(round(H * SMALL_W / W / 2) * 2)
frame_size = SMALL_W * h_small * 3
n_frames = len(raw) // frame_size
frames = np.frombuffer(raw[: n_frames * frame_size], dtype=np.uint8).reshape(n_frames, h_small, SMALL_W, 3)

gray = frames.mean(axis=3).astype(np.float32)
diffs = np.abs(np.diff(gray, axis=0)).mean(axis=(1, 2))
fps_eff = n_frames / vdur if vdur else FPS
per_sec_motion = []
for s in range(int(np.ceil(vdur))):
    a, b = int(s * fps_eff), int((s + 1) * fps_eff)
    seg = diffs[a:b]
    per_sec_motion.append(round(float(seg.mean()), 2) if len(seg) else 0.0)
report["motion_energy_per_s"] = per_sec_motion
report["motion_mean"] = round(float(diffs.mean()), 2)
report["motion_max"] = round(float(diffs.max()), 2)
report["static_ratio"] = round(float((diffs < 1.0).mean()), 3)

# per-shot colour palette + brightness
palette_rows = []
for sh in shots:
    a = int(sh["start"] * fps_eff)
    b = max(a + 1, int(sh["end"] * fps_eff))
    seg = frames[a:b]
    if len(seg) == 0:
        continue
    sample = seg[:: max(1, len(seg) // 6)]
    px = sample.reshape(-1, 3)
    img = Image.fromarray(px.reshape(1, -1, 3).astype(np.uint8))
    q = img.quantize(colors=5, method=Image.MEDIANCUT).convert("RGB")
    cols = np.array(q).reshape(-1, 3)
    uniq, cnt = np.unique(cols, axis=0, return_counts=True)
    order = np.argsort(-cnt)
    hexes = ["#%02X%02X%02X" % tuple(uniq[i]) for i in order][:5]
    pct = [round(float(cnt[i] / cnt.sum() * 100), 1) for i in order][:5]
    palette_rows.append({
        "shot": sh["index"], "start": sh["start"], "end": sh["end"],
        "brightness": round(float(seg.mean()), 1),
        "contrast": round(float(seg.std()), 1),
        "palette": hexes, "palette_pct": pct,
        "motion": round(float(diffs[max(0, a):b].mean()), 2) if b > a else 0,
    })
report["shots_detail"] = palette_rows

# ---------------------------------------------------------------- contact sheets at native res
def sheet(times, cols, path, label_prefix=""):
    thumbs = []
    for t in times:
        p = OUT / f"_f_{t:.2f}.png"
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}",
             "-i", str(VIDEO), "-frames:v", "1", "-y", str(p)])
        if p.exists():
            thumbs.append((t, Image.open(p).convert("RGB").copy()))
            p.unlink()
    if not thumbs:
        return
    tw, th = thumbs[0][1].size
    scale = min(1.0, 760 / tw)
    tw, th = int(tw * scale), int(th * scale)
    rows = (len(thumbs) + cols - 1) // cols
    pad, lab = 6, 26
    sh = Image.new("RGB", (cols * tw + (cols + 1) * pad, rows * (th + lab) + (rows + 1) * pad), (18, 18, 18))
    d = ImageDraw.Draw(sh)
    try:
        f = ImageFont.truetype(FONT, 18)
    except Exception:
        f = ImageFont.load_default()
    for i, (t, im) in enumerate(thumbs):
        c, rw = i % cols, i // cols
        x = pad + c * (tw + pad)
        y = pad + rw * (th + lab + pad)
        sh.paste(im.resize((tw, th)), (x, y + lab))
        d.text((x + 2, y + 3), f"{label_prefix}{t:.2f}s", fill=(255, 220, 120), font=f)
    sh.save(path, quality=90)
    report.setdefault("sheets", []).append(path.name)


step = max(0.75, vdur / 28)
times = [round(min(vdur - 0.05, i * step), 2) for i in range(int(vdur / step) + 1)]
sheet(times[:15], 3, OUT / "sheet_A.jpg")
if len(times) > 15:
    sheet(times[15:], 3, OUT / "sheet_B.jpg")

# hero frames: first + last + one per shot (max 6)
hero = [0.15] + [round((s["start"] + s["end"]) / 2, 2) for s in shots][:5] + [vdur - 0.3]
for i, t in enumerate(hero):
    p = OUT / f"hero_{i:02d}_{t:.2f}s.png"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(VIDEO),
         "-frames:v", "1", "-y", str(p)])

# strip: vertical slice of frames to show motion (every 0.25s for first 3s)
sheet([round(i * 0.25, 2) for i in range(12)], 4, OUT / "sheet_open.jpg", "open ")

# ---------------------------------------------------------------- audio analysis
if astream:
    loud = run(["ffmpeg", "-hide_banner", "-i", str(VIDEO), "-af",
                "loudnorm=print_format=json", "-f", "null", "-"])
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", loud.stderr, re.S)
    if m:
        report["audio_loudness"] = json.loads(m.group(0))

    sil = run(["ffmpeg", "-hide_banner", "-i", str(VIDEO), "-af",
               "silencedetect=noise=-38dB:d=0.35", "-f", "null", "-"])
    report["silences"] = [tuple(round(float(x), 2) for x in pair)
                          for pair in re.findall(r"silence_start: ([0-9.]+).*?silence_end: ([0-9.]+)", sil.stderr, re.S)]

    wav = OUT / "audio_16k_mono.wav"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(VIDEO),
         "-ac", "1", "-ar", "16000", "-y", str(wav)])
    r = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(wav),
             "-f", "s16le", "-acodec", "pcm_s16le", "-"])
    a = np.frombuffer(r.stdout.encode("latin-1"), dtype=np.int16).astype(np.float32) / 32768.0
    sr = 16000
    segs = []
    win = sr  # 1s
    for i in range(0, len(a) - win, win):
        seg = a[i:i + win]
        rms = float(np.sqrt((seg ** 2).mean()))
        spec = np.abs(np.fft.rfft(seg)) + 1e-9
        flat = float(np.exp(np.log(spec).mean()) / spec.mean())
        zcr = float((np.diff(np.signbit(seg).astype(int)) != 0).mean())
        centroid = float((np.arange(len(spec)) * spec).sum() / spec.sum() * sr / len(spec))
        segs.append({"t": i // sr, "rms_db": round(20 * np.log10(max(rms, 1e-6)), 1),
                     "flatness": round(flat, 4), "zcr": round(zcr, 3),
                     "centroid_hz": round(centroid)})
    report["audio_per_sec"] = segs
    # tempo guess from onset envelope
    env = np.array([10 ** (s["rms_db"] / 20) for s in segs])
    if len(env) > 4:
        flux = np.diff(env)
        report["audio_dynamic_range_db"] = round(float(env.max() - env.min()), 2)

    asr = None
    if os.environ.get("ASR") == "1":
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "faster-whisper"],
                           check=True, capture_output=True)
            from faster_whisper import WhisperModel
            model = WhisperModel("small", device="cpu", compute_type="int8")
            segments, info2 = model.transcribe(str(wav), language=None, vad_filter=True)
            asr = {"detected_language": info2.language,
                   "prob": round(info2.language_probability, 3),
                   "segments": [{"start": round(s.start, 2), "end": round(s.end, 2),
                                 "text": s.text.strip()} for s in segments]}
        except Exception as e:  # noqa
            asr = {"error": str(e)[:400]}
    report["asr"] = asr

# ---------------------------------------------------------------- write
(OUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

md = [f"# Reference analysis — {VIDEO.name}", ""]
md.append(f"- duration **{report['duration_s']}s** · {W}×{H} ({report['orientation']}, AR {report['aspect']}) · {report['fps']} fps · {report['bitrate_kbps']} kbps")
md.append(f"- cuts: **{report['cut_count']}** · avg shot **{report['avg_shot_s']}s**")
md.append(f"- motion mean {report['motion_mean']} · max {report['motion_max']} · static ratio {report['static_ratio']}")
if astream:
    md.append(f"- audio: {astream.get('codec_name')} {astream.get('channels')}ch @ {astream.get('sample_rate')}")
    if "audio_loudness" in report:
        L = report["audio_loudness"]
        md.append(f"- loudness: I {L.get('input_i')} LUFS · LRA {L.get('input_lra')} · TP {L.get('input_tp')} dBTP")
    if report.get("audio_per_sec"):
        rms = [s["rms_db"] for s in report["audio_per_sec"]]
        md.append(f"- audio RMS per second (dB): {rms}")
    if report.get("silences"):
        md.append(f"- silences: {report['silences']}")
    if report.get("asr") and not report["asr"].get("error"):
        A = report["asr"]
        md.append(f"\n## Transcript (lang={A['detected_language']} p={A['prob']})\n")
        for s in A["segments"]:
            md.append(f"- [{fmt_t(s['start'])}] {s['text']}")
    elif report.get("asr", {}).get("error"):
        md.append(f"- ASR error: {report['asr']['error']}")
md.append("\n## Shots\n")
md.append("| # | start | end | dur | brightness | contrast | motion | palette |")
md.append("|---|---|---|---|---|---|---|---|")
for s in report["shots_detail"]:
    md.append(f"| {s['shot']} | {fmt_t(s['start'])} | {fmt_t(s['end'])} | {s['dur']}s | {s['brightness']} | {s['contrast']} | {s['motion']} | {' '.join(s['palette'][:4])} |")
(OUT / "REPORT.md").write_text("\n".join(md), encoding="utf-8")
print("\n".join(md)[:6000])
