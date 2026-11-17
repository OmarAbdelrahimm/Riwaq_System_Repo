#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""analyze_reference.py — قياس فيديو مرجعي بدلًا من وصفه بالانطباع.

Usage:
    python scripts/analyze_reference.py <video> <outdir> [--scene 0.20] [--no-audio]

Outputs (in <outdir>): REPORT.md · report.json · sheet_*.jpg · hero_*.png

يعتمد على ffmpeg/ffprobe في الـPATH. لا يتصل بأي خدمة خارجية.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# ------------------------------------------------------------------ dependencies
def _fail(msg: str) -> None:
    print(f"[analyze_reference] {msg}", file=sys.stderr)
    raise SystemExit(2)


try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
except ModuleNotFoundError as exc:  # pragma: no cover
    _fail(f"مكتبة ناقصة: {exc.name}. شغّل: pip install -r scripts/requirements-analyze.txt")

FFMPEG = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
FFPROBE = shutil.which("ffprobe") or shutil.which("ffprobe.exe")
if not FFMPEG:
    _fail("ffmpeg غير موجود في PATH. ويندوز: winget install Gyan.FFmpeg")

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
]


# ------------------------------------------------------------------ helpers
def run(cmd: list[str], binary: bool = False) -> subprocess.CompletedProcess:
    if cmd and cmd[0] == "ffmpeg" and FFMPEG != "ffmpeg":
        cmd = [FFMPEG] + cmd[1:]
    elif cmd and cmd[0] == "ffprobe":
        cmd = [FFPROBE or FFMPEG] + cmd[1:]
    return subprocess.run(cmd, capture_output=True, text=not binary)


def fmt_t(t: float) -> str:
    m, s = divmod(float(t), 60)
    return f"{int(m):02d}:{s:05.2f}"


def probe(path: Path) -> dict:
    """يفضّل ffprobe؛ وإن غاب يُستخرج الحد الأدنى من ffmpeg نفسه."""
    if FFPROBE:
        out = run(["ffprobe", "-v", "error", "-print_format", "json",
                   "-show_format", "-show_streams", str(path)]).stdout
        try:
            return json.loads(out)
        except json.JSONDecodeError:
            pass  # ffprobe غير صالح (stub) → السقوط إلى ffmpeg -i
    txt = run(["ffmpeg", "-hide_banner", "-i", str(path)]).stderr
    v = re.search(r"Stream #\d+:\d+.*?: Video: (\w+).*?, (\d+)x(\d+).*?, ([0-9.]+) fps", txt)
    a = re.search(r"Stream #\d+:\d+.*?: Audio: (\w+).*?, (\d+) Hz, (stereo|mono)", txt)
    d = re.search(r"Duration: (\d+):(\d+):([0-9.]+)", txt)
    b = re.search(r"bitrate: (\d+) kb/s", txt)
    if not (v and d):
        _fail("تعذّر قراءة بيانات الفيديو. ثبّت ffprobe (يأتي مع ffmpeg).")
    dur = int(d.group(1)) * 3600 + int(d.group(2)) * 60 + float(d.group(3))
    streams = [{"codec_type": "video", "codec_name": v.group(1),
                "width": v.group(2), "height": v.group(3), "r_frame_rate": "0/1"}]
    if a:
        streams.append({"codec_type": "audio", "codec_name": a.group(1),
                        "sample_rate": a.group(2),
                        "channels": 2 if a.group(3) == "stereo" else 1})
    return {"format": {"duration": str(dur),
                       "size": str(path.stat().st_size),
                       "bit_rate": str(int(b.group(1)) * 1000 if b else 0)},
            "streams": streams}


# ------------------------------------------------------------------ main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("outdir")
    ap.add_argument("--scene", type=float, default=0.20, help="عتبة كشف القطعة (افتراضي 0.20)")
    ap.add_argument("--no-audio", action="store_true")
    args = ap.parse_args()

    video = Path(args.video).expanduser().resolve()
    if not video.exists():
        _fail(f"الملف غير موجود: {video}")
    out = Path(args.outdir).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)

    info = probe(video)
    dur = float(info["format"]["duration"])
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a_stream = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    W, H = int(v["width"]), int(v["height"])
    rfr = v.get("r_frame_rate", "0/1")
    try:
        num, den = rfr.split("/")
        fps = float(num) / float(den) if float(den) else 30.0
    except (ValueError, ZeroDivisionError):
        fps = 30.0

    rep: dict = {
        "file": video.name,
        "duration_s": round(dur, 2),
        "size_mb": round(int(info["format"]["size"]) / 1048576, 2),
        "resolution": [W, H],
        "aspect": round(W / H, 3),
        "orientation": "vertical" if H > W else ("square" if H == W else "horizontal"),
        "fps": round(fps, 2),
        "vcodec": v.get("codec_name"),
        "bitrate_kbps": round(int(info["format"]["bit_rate"]) / 1000),
        "audio": None if not a_stream else {
            "codec": a_stream.get("codec_name"),
            "channels": a_stream.get("channels"),
            "sample_rate": a_stream.get("sample_rate"),
        },
    }
    print(f"[probe] {W}x{H} {fps:.2f}fps {dur:.2f}s")

    # ---------------------------------------------------------- cuts
    r = run(["ffmpeg", "-hide_banner", "-i", str(video),
             "-vf", f"select='gt(scene,{args.scene})',showinfo", "-an", "-f", "null", "-"])
    cuts = sorted({round(float(m), 2) for m in re.findall(r"pts_time:([0-9.]+)", r.stderr)})
    bounds = [0.0] + cuts + [round(dur, 2)]
    shots = [{"index": i + 1, "start": bounds[i], "end": bounds[i + 1],
              "dur": round(bounds[i + 1] - bounds[i], 2)} for i in range(len(bounds) - 1)]
    rep |= {"cut_count": len(cuts), "cuts_s": cuts, "shots": shots,
            "avg_shot_s": round(sum(s["dur"] for s in shots) / len(shots), 2)}

    # ---------------------------------------------------------- tiny frames
    SW = 160
    SH = max(2, int(round(H * SW / W / 2) * 2))
    raw = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(video),
               "-vf", f"scale={SW}:{SH}", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"],
              binary=True).stdout
    fsz = SW * SH * 3
    n = len(raw) // fsz
    frames = np.frombuffer(raw[: n * fsz], dtype=np.uint8).reshape(n, SH, SW, 3)
    eff = n / dur if dur else fps
    if fps < 1:                     # ffmpeg -i fallback did not report fps → use real decode rate
        fps = eff
        rep["fps"] = round(fps, 2)

    diffs = np.abs(np.diff(frames.mean(axis=3).astype(np.float32), axis=0)).mean(axis=(1, 2)) \
        if n > 1 else np.zeros(1)
    rep |= {
        "motion_mean": round(float(diffs.mean()), 2),
        "motion_max": round(float(diffs.max()), 2),
        "static_ratio": round(float((diffs < 1.0).mean()), 3),
        "motion_energy_per_s": [
            round(float(diffs[int(s * eff):int((s + 1) * eff)].mean()), 2)
            if len(diffs[int(s * eff):int((s + 1) * eff)]) else 0.0
            for s in range(int(np.ceil(dur)))
        ],
    }

    detail = []
    for sh in shots:
        i0, i1 = int(sh["start"] * eff), max(int(sh["start"] * eff) + 1, int(sh["end"] * eff))
        seg = frames[i0:i1]
        if not len(seg):
            continue
        px = seg[:: max(1, len(seg) // 6)].reshape(-1, 3)
        q = Image.fromarray(px.reshape(1, -1, 3).astype(np.uint8))
        q = q.quantize(colors=5, method=Image.MEDIANCUT).convert("RGB")
        cols = np.array(q).reshape(-1, 3)
        uniq, cnt = np.unique(cols, axis=0, return_counts=True)
        order = np.argsort(-cnt)
        detail.append({
            **{k: sh[k] for k in ("index", "start", "end", "dur")},
            "brightness": round(float(seg.mean()), 1),
            "contrast": round(float(seg.std()), 1),
            "palette": ["#%02X%02X%02X" % tuple(uniq[i]) for i in order][:5],
            "palette_pct": [round(float(cnt[i] / cnt.sum() * 100), 1) for i in order][:5],
            "motion": round(float(diffs[i0:i1].mean()), 2) if i1 <= len(diffs) else 0.0,
        })
    rep["shots_detail"] = detail

    # ---------------------------------------------------------- sheets
    def grab(t: float):
        p = out / f"_g_{t:.2f}.png"
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(video),
             "-frames:v", "1", "-update", "1", "-y", str(p)])
        try:
            return Image.open(p).convert("RGB").copy()
        except Exception:
            return None
        finally:
            p.unlink(missing_ok=True)

    font = next((ImageFont.truetype(f, 17) for f in FONT_CANDIDATES if os.path.exists(f)),
                ImageFont.load_default())

    def sheet(times, cols, name, prefix=""):
        thumbs = [(t, im) for t in times for im in [grab(t)] if im is not None]
        if not thumbs:
            return
        tw0, th0 = thumbs[0][1].size
        k = min(1.0, 620 / tw0)
        tw, th = int(tw0 * k), int(th0 * k)
        rows = (len(thumbs) + cols - 1) // cols
        pad, lab = 6, 24
        sh = Image.new("RGB", (cols * tw + (cols + 1) * pad,
                               rows * (th + lab) + (rows + 1) * pad), (16, 16, 16))
        d = ImageDraw.Draw(sh)
        for i, (t, im) in enumerate(thumbs):
            c, rw = i % cols, i // cols
            x, y = pad + c * (tw + pad), pad + rw * (th + lab + pad)
            sh.paste(im.resize((tw, th)), (x, y + lab))
            d.text((x + 2, y + 3), f"{prefix}{t:.2f}s", fill=(255, 214, 110), font=font)
        sh.save(out / name, quality=88)
        rep.setdefault("sheets", []).append(name)

    step = max(0.8, dur / 24)
    ticks = [round(min(dur - 0.05, i * step), 2) for i in range(int(dur / step) + 1)]
    sheet(ticks[:12], 3, "sheet_A.jpg")
    sheet(ticks[12:], 3, "sheet_B.jpg")
    sheet([round(i * 0.35, 2) for i in range(10)], 5, "sheet_open.jpg", "t")
    sheet([round(max(0, dur - 3 + i * 0.35), 2) for i in range(10)], 5, "sheet_end.jpg", "t")

    hero = [0.2] + [round((s["start"] + s["end"]) / 2, 3) for s in shots][:6] + [round(dur - 0.35, 2)]
    for i, t in enumerate(dict.fromkeys(hero)):
        im = grab(t)
        if im:
            im.save(out / f"hero_{i:02d}_{t:.2f}s.png")

    # ---------------------------------------------------------- audio
    if a_stream and not args.no_audio:
        loud = run(["ffmpeg", "-hide_banner", "-i", str(video),
                    "-af", "loudnorm=print_format=json", "-f", "null", "-"])
        m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", loud.stderr, re.S)
        if m:
            rep["audio_loudness"] = json.loads(m.group(0))

        sil = run(["ffmpeg", "-hide_banner", "-i", str(video),
                   "-af", "silencedetect=noise=-38dB:d=0.30", "-f", "null", "-"])
        rep["silences"] = [{"start": float(x), "end": float(y)} for x, y in
                           re.findall(r"silence_start: ([0-9.]+)[\s\S]*?silence_end: ([0-9.]+)",
                                      sil.stderr)]

        wav = out / "audio_16k_mono.wav"
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(video),
             "-ac", "1", "-ar", "16000", "-y", str(wav)])
        pcm = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(wav),
                   "-f", "s16le", "-acodec", "pcm_s16le", "-"], binary=True).stdout
        sig = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
        sr, win = 16000, 16000
        rows = []
        for i in range(0, max(1, len(sig) - win), win):
            s = sig[i:i + win]
            spec = np.abs(np.fft.rfft(s)) + 1e-9
            freq = np.fft.rfftfreq(len(s), 1 / sr)
            lo = float((spec[freq < 300] ** 2).sum())
            sp = float((spec[(freq >= 300) & (freq < 3400)] ** 2).sum())
            hi = float((spec[freq > 5000] ** 2).sum())
            tot = lo + sp + hi + 1e-12
            rows.append({"t": i // sr,
                         "rms_db": round(float(20 * np.log10(max(float(np.sqrt((s ** 2).mean())), 1e-6))), 1),
                         "low_share": round(float(lo / tot), 3),
                         "speech_share": round(float(sp / tot), 3),
                         "high_share": round(float(hi / tot), 3)})
        rep["audio_per_sec"] = rows
        if rows:
            rep["audio_rms_range_db"] = [min(r["rms_db"] for r in rows),
                                         max(r["rms_db"] for r in rows)]

        # syllabic modulation — هل يوجد طابع كلام/بصمة بشرية؟
        body = sig[: int(max(0, (dur - 2) * sr))]
        if len(body) > sr:
            k = sr // 100
            env = np.convolve(np.abs(body), np.ones(k) / k, mode="same")[::k]
            E = np.abs(np.fft.rfft(env - env.mean()))
            F = np.fft.rfftfreq(len(env), 1 / 100)
            band = (F >= 1.5) & (F <= 8)
            low = (F >= 0.05) & (F <= 8)
            rep["syllabic_modulation"] = {
                "ratio": round(float(E[band].sum() / max(E[low].sum(), 1e-9)), 3),
                "peak_hz": round(float(F[band][np.argmax(E[band])]), 2),
            }
        wav.unlink(missing_ok=True)

    # ---------------------------------------------------------- write
    (out / "report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=2),
                                     encoding="utf-8")
    L = rep.get("audio_loudness", {})
    md = [f"# تحليل مرجعي — {video.name}", "",
          f"- **{rep['duration_s']}s** · {W}×{H} ({rep['orientation']} · AR {rep['aspect']})"
          f" · {rep['fps']} fps · {rep['bitrate_kbps']} kbps",
          f"- قطعات: **{rep['cut_count']}** · متوسط اللقطة **{rep['avg_shot_s']}s**",
          f"- حركة: متوسط {rep['motion_mean']} · أقصى {rep['motion_max']}"
          f" · نسبة السكون {rep['static_ratio']}",
          f"- طاقة الحركة/ثانية: {rep['motion_energy_per_s']}"]
    if L:
        md.append(f"- لودنس: I {L.get('input_i')} LUFS · LRA {L.get('input_lra')}"
                  f" · TP {L.get('input_tp')} dBTP")
    if rep.get("audio_per_sec"):
        md.append(f"- RMS/ثانية: {[r['rms_db'] for r in rep['audio_per_sec']]}")
        md.append(f"- نسبة الباس (<300Hz): {[r['low_share'] for r in rep['audio_per_sec']]}")
    if rep.get("syllabic_modulation"):
        sm = rep["syllabic_modulation"]
        md.append(f"- طابع مقطعي: نسبة {sm['ratio']} · ذروة {sm['peak_hz']} Hz")
    if rep.get("silences"):
        md.append(f"- صمت (≥0.3s @ −38dB): {rep['silences']}")
    md += ["", "| # | بداية | نهاية | مدة | سطوع | تباين | حركة | لوحة |",
           "|---|---|---|---|---|---|---|---|"]
    for s in detail:
        md.append(f"| {s['index']} | {fmt_t(s['start'])} | {fmt_t(s['end'])} | {s['dur']}s |"
                  f" {s['brightness']} | {s['contrast']} | {s['motion']} |"
                  f" {' '.join(s['palette'][:4])} |")
    (out / "REPORT.md").write_text("\n".join(md), encoding="utf-8")

    print(f"[done] {out}")
    print("\n".join(md[:12]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
