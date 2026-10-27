#!/usr/bin/env python3
"""فحص الميديا النهائية — الفحوص التي لا يستطيع `qc.py` فعلها بلا ملف MP4.

    python3 scripts/qc_media.py exports/MASTER.mp4 --report reports/QC_MEDIA_ID.md \
        --aspect 9x16 --frames 6

يفحص على **الملف المسلَّم نفسه**:
  1) الحاوية: المدة · الفريمات · الأبعاد · fps · البتريت
  2) الصوت: I (LUFS) · LRA · True Peak  — عبر `ebur128`
  3) أسود غير مقصود — `blackdetect`
  4) تجميد — `freezedetect`
  5) سلامة الفك — `-f null -`
  6) لقطات إطارات للمعاينة البصرية (اختياري)
  7) تقدير تجاوز المنطقة الآمنة للكابشن (سطوع/تباين في شريط الكابشن)

ffmpeg يُبحث عنه بالترتيب: $FFMPEG → imageio_ffmpeg → ffmpeg النظامي.
`ffprobe` غير مطلوب (الميتاداتا تُقرأ من `ffmpeg -i`).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def find_ffmpeg() -> str:
    env = os.environ.get("FFMPEG")
    if env and Path(env).exists():
        return env
    try:
        import imageio_ffmpeg  # type: ignore
        p = imageio_ffmpeg.get_ffmpeg_exe()
        if p and Path(p).exists():
            return p
    except Exception:
        pass
    p = shutil.which("ffmpeg")
    if p:
        return p
    sys.exit("❌ ffmpeg غير متاح — ضع المسار في $FFMPEG أو: pip install imageio-ffmpeg")


def run(cmd: list[str], timeout: int = 1800) -> tuple[str, int]:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return (r.stdout or "") + (r.stderr or ""), r.returncode


# ─────────────────────────── 1) الحاوية ───────────────────────────
def probe(ff: str, f: Path) -> dict:
    out, _ = run([ff, "-hide_banner", "-i", str(f)])

    def grab(pat, cast=float):
        m = re.search(pat, out)
        return cast(m.group(1)) if m else None

    dur = grab(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", str)
    seconds = None
    if dur:
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", out)
        h, mi, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
        seconds = h * 3600 + mi * 60 + s
    v = re.search(r"Stream #\d+:\d+.*?Video:.*?(\d{2,5})x(\d{2,5}).*?(\d+(?:\.\d+)?)\s*fps", out)
    a = re.search(r"Stream #\d+:\d+.*?Audio:\s*([\w\-]+).*?(\d{4,6})\s*Hz.*?(\d+)\s*kb/s", out)
    pix = re.search(r"Video:.*?(yuv\w+|rgb\w+)", out)
    size = f.stat().st_size
    return {
        "duration_s": round(seconds, 3) if seconds else None,
        "width": int(v.group(1)) if v else None,
        "height": int(v.group(2)) if v else None,
        "fps": float(v.group(3)) if v else None,
        "pix_fmt": pix.group(1) if pix else None,
        "audio_codec": a.group(1) if a else None,
        "audio_hz": int(a.group(2)) if a else None,
        "audio_kbps": int(a.group(3)) if a else None,
        "size_mb": round(size / 1_048_576, 2),
        "faststart": None,  # يُقاس بـ moov position أدناه
    }


def has_faststart(f: Path) -> bool | None:
    """moov قبل mdat ⇒ +faststart. قراءة أول 2MB فقط."""
    try:
        head = f.open("rb").read(2_000_000)
    except OSError:
        return None
    moov, mdat = head.find(b"moov"), head.find(b"mdat")
    if moov == -1:
        return None
    if mdat == -1:
        return True
    return moov < mdat


# ─────────────────────────── 2) الصوت ───────────────────────────
def loudness(ff: str, f: Path) -> dict:
    out, _ = run([ff, "-hide_banner", "-nostats", "-i", str(f),
                  "-af", "ebur128=peak=true", "-f", "null", "-"])
    tail = out[out.rfind("Summary:"):] if "Summary:" in out else out[-4000:]
    res = {}
    m = re.search(r"I:\s*(-?[\d.]+)\s*LUFS", tail)
    if m:
        res["lufs_i"] = float(m.group(1))
    m = re.search(r"LRA:\s*(-?[\d.]+)\s*LU", tail)
    if m:
        res["lra"] = float(m.group(1))
    m = re.search(r"Peak:\s*(-?[\d.]+)\s*dBFS", tail)
    if m:
        res["true_peak"] = float(m.group(1))
    return res


# ─────────────────────── 3+4) أسود وتجميد ───────────────────────
def detect(ff: str, f: Path, filt: str) -> list[str]:
    out, _ = run([ff, "-hide_banner", "-nostats", "-i", str(f),
                  "-vf", filt, "-an", "-f", "null", "-"])
    return [ln.strip() for ln in out.splitlines() if "black_start" in ln or "freeze_start" in ln]


# ───────────────────── 5) سلامة الفك ─────────────────────
def decode_ok(ff: str, f: Path) -> tuple[bool, int]:
    out, code = run([ff, "-hide_banner", "-v", "error", "-i", str(f), "-f", "null", "-"])
    errors = len([ln for ln in out.splitlines() if ln.strip()])
    return (code == 0 and errors == 0), errors


# ───────────────────── 6) لقطات الإطارات ─────────────────────
def frames(ff: str, f: Path, n: int, outdir: Path) -> list[Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    dur = probe(ff, f)["duration_s"] or 0
    made = []
    for i in range(n):
        t = max(0.0, dur * (i + 0.5) / n)
        p = outdir / f"frame_{i + 1:02d}_{t:07.2f}s.jpg"
        out, code = run([ff, "-hide_banner", "-nostats", "-ss", f"{t:.2f}", "-i", str(f),
                         "-frames:v", "1", "-q:v", "2", str(p)])
        if p.exists():
            made.append(p)
    return made


# ──────────── 7) تجاوز الكابشن للمنطقة الآمنة (تقدير سطوع) ────────────
def caption_band_luma(ff: str, f: Path, band: tuple[int, int], width: int) -> dict | None:
    """يقيس متوسط سطوع شريط الكابشن على 5 إطارات — مؤشر لا حكم.

    فيلم فاتح جدًا + كابشن ورقي = خطر قراءة. الرقم يساعد، والحكم بصري.
    """
    try:
        import numpy as np
        from PIL import Image
    except Exception:
        return None
    dur = probe(ff, f)["duration_s"] or 0
    vals = []
    with tempfile.TemporaryDirectory() as td:
        for i in range(5):
            t = max(0.0, dur * (i + 0.5) / 5)
            p = Path(td) / f"b{i}.png"
            run([ff, "-hide_banner", "-nostats", "-ss", f"{t:.2f}", "-i", str(f),
                 "-frames:v", "1", "-vf", f"crop={width}:{band[1] - band[0]}:0:{band[0]}", str(p)])
            if p.exists():
                arr = np.asarray(Image.open(p).convert("L"), dtype=float) / 255.0
                vals.append(round(float(np.median(arr)), 3))
    if not vals:
        return None
    return {"median_luma_band": max(vals), "samples": vals,
            "note": "أعلى قيمة مقيسة؛ فوق 0.46 تُشغَّل اللوحة التكيفية"}


# ─────────────────────────── التقرير ───────────────────────────
def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="فحص الميديا النهائية")
    ap.add_argument("video")
    ap.add_argument("--report", help="مسار تقرير md")
    ap.add_argument("--aspect", default="9x16", help="9x16 | 16x9 | 1x1 | 4x5")
    ap.add_argument("--frames", type=int, default=6, help="عدد لقطات المعاينة (0 = بلا)")
    ap.add_argument("--frames-dir", default=None)
    ap.add_argument("--lufs", type=float, default=-14.0)
    ap.add_argument("--tp", type=float, default=-1.0)
    ap.add_argument("--lra", type=float, default=8.0)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    f = Path(a.video)
    if not f.is_file():
        sys.exit(f"❌ الملف غير موجود: {f}")
    ff = find_ffmpeg()

    info = probe(ff, f)
    info["faststart"] = has_faststart(f)
    audio = loudness(ff, f)
    black = detect(ff, f, "blackdetect=d=0.10:pix_th=0.10")
    freeze = detect(ff, f, "freezedetect=n=0.003:d=1.0")
    ok, errs = decode_ok(ff, f)

    band = {"9x16": (1210, 1360), "16x9": (880, 980), "1x1": (820, 910), "4x5": (1010, 1130)}[a.aspect]
    luma = caption_band_luma(ff, f, band, info["width"] or 1080)

    shots = []
    if a.frames:
        outdir = Path(a.frames_dir or (f.parent / "_qc_frames"))
        shots = frames(ff, f, a.frames, outdir)

    # ── الحكم ──
    verdict: list[tuple[str, str, str]] = []   # (PASS/WARN/FAIL, بند, قيمة)

    def add(okv: bool | None, name: str, detail: str) -> None:
        verdict.append(("WARN" if okv is None else ("PASS" if okv else "FAIL"), name, detail))

    d, w, h, fps = info["duration_s"], info["width"], info["height"], info["fps"]
    frames_expected = round(d * fps) if (d and fps) else None
    add(bool(d), "المدة", f"{d}s")
    add(bool(w and h), "الأبعاد", f"{w}×{h}")
    add(bool(fps), "معدل الفريمات", f"{fps}")
    add(info["pix_fmt"] == "yuv420p", "بتريت", str(info["pix_fmt"]))
    add(info["faststart"] is not False, "faststart (moov قبل mdat)",
        "نعم" if info["faststart"] else ("غير معروف" if info["faststart"] is None else "لا — أضف -movflags +faststart"))

    if not info.get("audio_codec"):
        add(False, "مسار الصوت", "لا يوجد مسار صوتي — الماستر صامت")
    if "lufs_i" in audio:
        add(abs(audio["lufs_i"] - a.lufs) <= 1.0, "LUFS", f'{audio["lufs_i"]} (الهدف {a.lufs}±1)')
    if "lra" in audio:
        add(audio["lra"] <= a.lra, "LRA", f'{audio["lra"]} (≤ {a.lra})')
    if info.get("audio_hz"):
        add(None if info["audio_hz"] == 48000 else False,
            "معدل عينة الصوت",
            f'{info["audio_hz"]}Hz' + ("" if info["audio_hz"] == 48000
            else " — loudnorm يرفع إلى 96k؛ أضف -ar 48000 بعده"))
    if "true_peak" in audio:
        add(audio["true_peak"] <= a.tp, "True Peak", f'{audio["true_peak"]} dBFS (≤ {a.tp})')
    add(len(black) == 0, "أسود غير مقصود", f"{len(black)} حدث" if black else "صفر")
    add(len(freeze) == 0, "تجميد", f"{len(freeze)} حدث (راجع إن كان مقصودًا)" if freeze else "صفر")
    add(ok, "سلامة الفك", "سليم" if ok else f"{errs} خطأ")
    if luma:
        hot = luma["median_luma_band"] > 0.46
        add(None if hot else True, "سطوع شريط الكابشن (إرشادي)",
            f'{luma["median_luma_band"]}' + (" — فوق 0.46 ⇒ شغّل اللوحة التكيفية" if hot else " — اللوحة غير لازمة"))

    fails = sum(1 for s, _, _ in verdict if s == "FAIL")
    icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}

    lines = [f"# QC MEDIA — {f.name}", "",
             f"**الحالة:** {'✅ يمر' if fails == 0 else f'❌ {fails} مخالفة'} · **الحجم:** {info['size_mb']}MB",
             "", "| الفحص | النتيجة | القيمة |", "|---|---|---|"]
    lines += [f"| {n} | {icon[s]} {s} | {v} |" for s, n, v in verdict]

    if frames_expected:
        lines += ["", f"**فريمات متوقعة:** {frames_expected} عند {fps}fps"]
    if info.get("audio_codec"):
        lines += [f"**الصوت:** {info['audio_codec']} · {info['audio_hz']}Hz · {info['audio_kbps']}kb/s"]
    if shots:
        lines += ["", "## لقطات المعاينة", ""] + [f"- `{p.name}`" for p in shots]
    if black:
        lines += ["", "## أحداث سوداء", ""] + [f"- `{b}`" for b in black[:10]]
    if freeze:
        lines += ["", "## أحداث تجميد", ""] + [f"- `{b}`" for b in freeze[:10]]

    report = "\n".join(lines) + "\n"
    if a.report:
        Path(a.report).parent.mkdir(parents=True, exist_ok=True)
        Path(a.report).write_text(report, encoding="utf-8")
    print(report)
    if a.json:
        print(json.dumps({"info": info, "audio": audio, "black": black,
                          "freeze": freeze, "luma": luma}, ensure_ascii=False, indent=2))
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
