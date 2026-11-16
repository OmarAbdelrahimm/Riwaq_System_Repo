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

VIDEO = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
OUT.mkdir(parents=True, exist_ok=True)

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def log(*a):
    print(*a, flush=True)


def run(cmd, binary=False):
    return subprocess.run(cmd, capture_output=binary or True,
                          text=not binary, errors=None if binary else "replace")


def fmt_t(t):
    m, s = divmod(float(t), 60)
    return f"{int(m):02d}:{s:05.2f}"


def ffprobe(path):
    r = run(["ffprobe", "-v", "error", "-print_format", "json",
             "-show_format", "-show_streams", str(path)])
    return json.loads(r.stdout)


# ---------------------------------------------------------------- probe
info = ffprobe(VIDEO)
vdur = float(info["format"]["duration"])
vstream = next(s for s in info["streams"] if s["codec_type"] == "video")
astream = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
W, H = int(vstream["width"]), int(vstream["height"])
num, den = vstream["r_frame_rate"].split("/")
FPS = float(num) / float(den)

report = {
    "file": VIDEO.name,
    "duration_s": round(vdur, 2),
    "size_mb": round(int(info["format"]["size"]) / 1048576, 2),
    "resolution": [W, H],
    "aspect": round(W / H, 3),
    "orientation": "vertical" if H > W else ("square" if H == W else "horizontal"),
    "fps": round(FPS, 2),
    "vcodec": vstream.get("codec_name"),
    "pix_fmt": vstream.get("pix_fmt"),
    "bitrate_kbps": round(int(info["format"]["bit_rate"]) / 1000),
    "audio": None if not astream else {
        "codec": astream.get("codec_name"),
        "channels": astream.get("channels"),
        "sample_rate": astream.get("sample_rate"),
        "bitrate_kbps": round(int(astream.get("bit_rate", 0)) / 1000) if astream.get("bit_rate") else None,
    },
}
log(f"[probe] {W}x{H} {FPS}fps {vdur}s audio={bool(astream)}")

# ---------------------------------------------------------------- scene cuts
r = run(["ffmpeg", "-hide_banner", "-i", str(VIDEO),
         "-vf", "select='gt(scene,0.20)',showinfo", "-an", "-f", "null", "-"])
cuts = sorted({round(float(m), 2) for m in re.findall(r"pts_time:([0-9.]+)", r.stderr)})
boundaries = [0.0] + cuts + [round(vdur, 2)]
shots = [{"index": i + 1, "start": boundaries[i], "end": boundaries[i + 1],
          "dur": round(boundaries[i + 1] - boundaries[i], 2)}
         for i in range(len(boundaries) - 1)]
report["cut_count"] = len(cuts)
report["cuts_s"] = cuts
report["avg_shot_s"] = round(sum(s["dur"] for s in shots) / len(shots), 2)
report["shots"] = shots
log(f"[cuts] {len(cuts)} cuts")

# ---------------------------------------------------------------- decode tiny frames
SMALL_W = 160
SMALL_H = int(round(H * SMALL_W / W / 2) * 2)
raw = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(VIDEO),
           "-vf", f"scale={SMALL_W}:{SMALL_H}", "-pix_fmt", "rgb24",
           "-f", "rawvideo", "-"], binary=True).stdout
fsz = SMALL_W * SMALL_H * 3
n_frames = len(raw) // fsz
frames = np.frombuffer(raw[: n_frames * fsz], dtype=np.uint8).reshape(n_frames, SMALL_H, SMALL_W, 3)
fps_eff = n_frames / vdur
log(f"[frames] {n_frames} tiny frames @ {fps_eff:.2f}/s")

gray = frames.mean(axis=3).astype(np.float32)
diffs = np.abs(np.diff(gray, axis=0)).mean(axis=(1, 2))
if len(diffs) == 0:
    diffs = np.zeros(1)
report["motion_mean"] = round(float(diffs.mean()), 2)
report["motion_max"] = round(float(diffs.max()), 2)
report["static_ratio"] = round(float((diffs < 1.0).mean()), 3)
per_sec = []
for s in range(int(np.ceil(vdur))):
    a, b = int(s * fps_eff), int((s + 1) * fps_eff)
    seg = diffs[a:b]
    per_sec.append(round(float(seg.mean()), 2) if len(seg) else 0.0)
report["motion_energy_per_s"] = per_sec

# ---------------------------------------------------------------- per-shot palette
shots_detail = []
for sh in shots:
    a = int(sh["start"] * fps_eff)
    b = max(a + 1, int(sh["end"] * fps_eff))
    seg = frames[a:b]
    if len(seg) == 0:
        continue
    sample = seg[:: max(1, len(seg) // 6)]
    px = sample.reshape(-1, 3)
    q = Image.fromarray(px.reshape(1, -1, 3).astype(np.uint8)).quantize(colors=5, method=Image.MEDIANCUT).convert("RGB")
    cols = np.array(q).reshape(-1, 3)
    uniq, cnt = np.unique(cols, axis=0, return_counts=True)
    order = np.argsort(-cnt)
    shots_detail.append({
        "shot": sh["index"], "start": sh["start"], "end": sh["end"], "dur": sh["dur"],
        "brightness": round(float(seg.mean()), 1),
        "contrast": round(float(seg.std()), 1),
        "palette": ["#%02X%02X%02X" % tuple(uniq[i]) for i in order][:5],
        "palette_pct": [round(float(cnt[i] / cnt.sum() * 100), 1) for i in order][:5],
        "motion": round(float(diffs[a:b].mean()), 2) if b <= len(diffs) else 0,
    })
report["shots_detail"] = shots_detail

# ---------------------------------------------------------------- contact sheets
def grab(t):
    p = OUT / f"_g_{t:.2f}.png"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}",
         "-i", str(VIDEO), "-frames:v", "1", "-update", "1", "-y", str(p)])
    if p.exists():
        try:
            im = Image.open(p).convert("RGB").copy()
        except Exception:
            im = None
        p.unlink(missing_ok=True)
        return im
    return None


def sheet(times, cols, path, prefix=""):
    thumbs = [(t, im) for t in times for im in [grab(t)] if im is not None]
    if not thumbs:
        return
    tw0, th0 = thumbs[0][1].size
    scale = min(1.0, 620 / tw0)
    tw, th = int(tw0 * scale), int(th0 * scale)
    rows = (len(thumbs) + cols - 1) // cols
    pad, lab = 6, 24
    sh = Image.new("RGB", (cols * tw + (cols + 1) * pad,
                           rows * (th + lab) + (rows + 1) * pad), (16, 16, 16))
    d = ImageDraw.Draw(sh)
    f = None
    for fp in FONT_CANDIDATES:
        if os.path.exists(fp):
            f = ImageFont.truetype(fp, 17)
            break
    f = f or ImageFont.load_default()
    for i, (t, im) in enumerate(thumbs):
        c, rw = i % cols, i // cols
        x = pad + c * (tw + pad)
        y = pad + rw * (th + lab + pad)
        sh.paste(im.resize((tw, th)), (x, y + lab))
        d.text((x + 2, y + 3), f"{prefix}{t:.2f}s", fill=(255, 214, 110), font=f)
    sh.save(path, quality=88)
    report.setdefault("sheets", []).append(path.name)


step = max(0.8, vdur / 24)
times = [round(min(vdur - 0.05, i * step), 2) for i in range(int(vdur / step) + 1)]
sheet(times[:12], 3, OUT / "sheet_A.jpg")
sheet(times[12:], 3, OUT / "sheet_B.jpg")
sheet([round(i * 0.35, 2) for i in range(10)], 5, OUT / "sheet_open.jpg", "t")
sheet([round(vdur - 3 + i * 0.35, 2) for i in range(10)], 5, OUT / "sheet_end.jpg", "t")

# hero frames (native res)
hero_t = [0.2] + [round((s["start"] + s["end"]) / 2, 2) for s in shots][:6] + [round(vdur - 0.35, 2)]
for i, t in enumerate(dict.fromkeys(hero_t)):
    im = grab(t)
    if im:
        im.save(OUT / f"hero_{i:02d}_{t:.2f}s.png")
log("[sheets] done")

# ---------------------------------------------------------------- audio
if astream:
    loud = run(["ffmpeg", "-hide_banner", "-i", str(VIDEO), "-af", "loudnorm=print_format=json", "-f", "null", "-"])
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", loud.stderr, re.S)
    if m:
        report["audio_loudness"] = json.loads(m.group(0))

    sil = run(["ffmpeg", "-hide_banner", "-i", str(VIDEO), "-af",
               "silencedetect=noise=-38dB:d=0.30", "-f", "null", "-"])
    report["silences"] = [
        {"start": float(a), "end": float(b)}
        for a, b in re.findall(r"silence_start: ([0-9.]+).*?silence_end: ([0-9.]+)", sil.stderr, re.S)]

    wav = OUT / "audio_16k_mono.wav"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(VIDEO),
         "-ac", "1", "-ar", "16000", "-y", str(wav)])
    rawa = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(wav),
                "-f", "s16le", "-acodec", "pcm_s16le", "-"], binary=True).stdout
    a = np.frombuffer(rawa, dtype=np.int16).astype(np.float32) / 32768.0
    sr = 16000
    segs = []
    win = sr
    for i in range(0, max(1, len(a) - win), win):
        seg = a[i:i + win]
        rms = float(np.sqrt((seg ** 2).mean()))
        spec = np.abs(np.fft.rfft(seg)) + 1e-9
        flat = float(np.exp(np.log(spec).mean()) / spec.mean())
        zcr = float((np.signbit(seg[1:]) != np.signbit(seg[:-1])).mean())
        centroid = float((np.arange(len(spec)) * spec).sum() / spec.sum() * sr / len(spec))
        segs.append({"t": i // sr,
                     "rms_db": round(20 * np.log10(max(rms, 1e-6)), 1),
                     "flatness": round(flat, 4), "zcr": round(zcr, 3),
                     "centroid_hz": round(centroid)})
    report["audio_per_sec"] = segs
    if segs:
        rms = [s["rms_db"] for s in segs]
        report["audio_rms_range_db"] = [min(rms), max(rms)]

    if os.environ.get("ASR", "0") == "1":
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "faster-whisper"],
                           check=True, capture_output=True)
            from faster_whisper import WhisperModel
            model = WhisperModel("small", device="cpu", compute_type="int8")
            seg_iter, i2 = model.transcribe(str(wav), vad_filter=True)
            report["asr"] = {
                "detected_language": i2.language,
                "prob": round(i2.language_probability, 3),
                "segments": [{"start": round(s.start, 2), "end": round(s.end, 2),
                              "text": s.text.strip()} for s in seg_iter],
            }
        except Exception as e:  # noqa: BLE001
            report["asr"] = {"error": f"{type(e).__name__}: {e}"[:500]}
log("[audio] done")

# ---------------------------------------------------------------- write
(OUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

md = [f"# تحليل الفيديو المرجعي — {VIDEO.name}", ""]
md.append(f"- المدة **{report['duration_s']}s** · {W}×{H} ({report['orientation']}, AR {report['aspect']}) · {report['fps']} fps · {report['bitrate_kbps']} kbps · {report['size_mb']} MB")
md.append(f"- عدد القطعات: **{report['cut_count']}** · متوسط طول اللقطة **{report['avg_shot_s']}s**")
md.append(f"- حركة: متوسط {report['motion_mean']} · أقصى {report['motion_max']} · نسبة السكون {report['static_ratio']}")
md.append(f"- طاقة الحركة لكل ثانية: {report['motion_energy_per_s']}")
if astream:
    md.append(f"- صوت: {astream.get('codec_name')} · {astream.get('channels')}ch · {astream.get('sample_rate')}Hz")
    if "audio_loudness" in report:
        L = report["audio_loudness"]
        md.append(f"- لودنس: I {L.get('input_i')} LUFS · LRA {L.get('input_lra')} · TP {L.get('input_tp')} dBTP · thresh {L.get('input_thresh')}")
    if report.get("audio_per_sec"):
        md.append(f"- RMS لكل ثانية: {[s['rms_db'] for s in report['audio_per_sec']]}")
        md.append(f"- سنترويد الطيف (Hz) لكل ثانية: {[s['centroid_hz'] for s in report['audio_per_sec']]}")
        md.append(f"- zcr لكل ثانية: {[s['zcr'] for s in report['audio_per_sec']]}")
        md.append(f"- flatness: {[s['flatness'] for s in report['audio_per_sec']]}")
    if report.get("silences"):
        md.append(f"- فراغات صامتة (≥0.3s @ -38dB): {report['silences']}")
    if report.get("asr", {}).get("error"):
        md.append(f"- ASR error: {report['asr']['error']}")
    if report.get("asr") and report["asr"].get("segments") is not None:
        A = report["asr"]
        md.append(f"\n## النص المسموع (لغة: {A['detected_language']} · ثقة {A['prob']})\n")
        for s in A["segments"]:
            md.append(f"- [{fmt_t(s['start'])} → {fmt_t(s['end'])}] {s['text']}")

md.append("\n## اللقطات\n")
md.append("| # | بداية | نهاية | مدة | سطوع | تباين | حركة | لوحة |")
md.append("|---|---|---|---|---|---|---|---|")
for s in shots_detail:
    md.append(f"| {s['shot']} | {fmt_t(s['start'])} | {fmt_t(s['end'])} | {s['dur']}s | {s['brightness']} | {s['contrast']} | {s['motion']} | {' '.join(s['palette'][:4])} |")
(OUT / "REPORT.md").write_text("\n".join(md), encoding="utf-8")
log("\n".join(md))
