#!/usr/bin/env python3
"""خريطة اللوحة التكيفية للكابشن — قرار «لوحة أم لا» لكل مشهد، لا لكل كادر.

    python3 scripts/scrim_map.py SRC.mp4 --aspect 9x16 \
        --out data/projects/<ID>/scrim_map.json

المنطق المعتمد (v2): لوحة مسطّحة تُشغَّل لما **وسط سطوع شريط الكابشن** يعدّي 0.46،
وتُطفأ تلقائيًا تحت العتبة. القرار على مستوى **المشهد** (حدود من `scdet`)، لأن:
  • التغيّر لكل كادر يعني وميض اللوحة = أسوأ من غيابها.
  • القطع على المشهد هو المكان الذي يتغيّر فيه الخلفية فعلًا.

العتبة والنطاقات في `data/brand.json` إن وُجدت (`captions.scrim`)، وإلا الافتراضيات هنا.
المخرج JSON تقرأه طبقة الكابشن (`scrim: true|false` لكل نطاق زمني).
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

DEFAULTS = {
    "threshold": 0.46,
    "scrim_color": "rgba(15,14,12,ALPHA)",
    "scrim_opacity": 0.55,
    "min_shot_s": 0.6,          # مشاهد أقصر من كده تُدمج في الجار
}

# نطاق شريط الكابشن (y0,y1) لكل مقاس — يجب أن يطابق قالب الكابشن
BANDS = {
    "9x16": (1210, 1360),
    "16x9": (880, 980),
    "4x5": (1010, 1130),
    "1x1": (820, 910),
}


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
    sys.exit("❌ ffmpeg غير متاح — $FFMPEG أو: pip install imageio-ffmpeg")


def run(cmd: list[str], timeout: int = 1800) -> str:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return (r.stdout or "") + (r.stderr or "")


def dims(ff: str, f: Path) -> tuple[int, int, float]:
    out = run([ff, "-hide_banner", "-i", str(f)])
    m = re.search(r"Video:.*?(\d{2,5})x(\d{2,5}).*?(\d+(?:\.\d+)?)\s*fps", out)
    if not m:
        sys.exit("❌ لم أقرأ أبعاد الفيديو — تأكد أن الملف فيديو سليم")
    d = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", out)
    dur = int(d.group(1)) * 3600 + int(d.group(2)) * 60 + float(d.group(3)) if d else 0.0
    return int(m.group(1)), int(m.group(2)), dur


def scenes(ff: str, f: Path, thresh: float) -> list[float]:
    """حدود المشاهد (ثوانٍ) عبر `scdet`."""
    out = run([ff, "-hide_banner", "-nostats", "-i", str(f),
               "-vf", f"select='gt(scene,{thresh})',metadata=print:file=-",
               "-an", "-f", "null", "-"])
    pts = []
    for ln in out.splitlines():
        m = re.search(r"pts_time:([\d.]+)", ln)
        if m:
            pts.append(round(float(m.group(1)), 3))
    return sorted(set(pts))


def band_luma(ff: str, f: Path, y0: int, y1: int, w: int, dur: float,
              samples: int) -> list[tuple[float, float]]:
    """تسلسل (زمن, سطوع) لعيّنات منتظمة من شريط الكابشن.

    السطوع = الوسيط (median) لا المتوسط: الوسيط يقاوم بقعة نار/لمعة واحدة،
    والمتوسط كان سيعطي قرارًا خاطئًا في مشهد فيه وجه فاتح على نصف الشريط.
    """
    try:
        import numpy as np
        from PIL import Image
    except Exception:
        sys.exit("❌ المطلوب: pip install numpy pillow (لقياس السطوع)")

    rows: list[tuple[float, float]] = []
    h = y1 - y0
    with tempfile.TemporaryDirectory() as td:
        for i in range(samples):
            t = dur * (i + 0.5) / samples
            p = Path(td) / f"s{i}.png"
            run([ff, "-hide_banner", "-nostats", "-ss", f"{t:.3f}", "-i", str(f),
                 "-frames:v", "1", "-vf", f"crop={w}:{h}:0:{y0},scale=64:-1", str(p)])
            if p.exists():
                arr = np.asarray(Image.open(p).convert("L"), dtype=float) / 255.0
                rows.append((round(t, 3), round(float(np.median(arr)), 4)))
    return rows


def build(src: Path, aspect: str, samples: int, scene_thresh: float,
          threshold: float, min_shot: float) -> dict:
    ff = find_ffmpeg()
    w, hh, dur = dims(ff, src)
    y0, y1 = BANDS[aspect]
    y1 = min(y1, hh - 1)

    cuts = [0.0] + [c for c in scenes(ff, src, scene_thresh) if 0.1 < c < dur - 0.1] + [dur]
    # دمج المشاهد القصيرة
    merged = [cuts[0]]
    for c in cuts[1:]:
        if c - merged[-1] < min_shot and c != cuts[-1]:
            continue
        merged.append(c)
    if merged[-1] != dur:
        merged.append(dur)

    lum = band_luma(ff, src, y0, y1, w, dur, samples)

    shots = []
    for a, b in zip(merged, merged[1:]):
        inside = [v for t, v in lum if a <= t < b]
        if not inside:
            # مشهد أقصر من المسافة بين عيّنتين → نأخذ الجار الأقرب زمنيًا
            nearest = min(lum, key=lambda tv: abs(tv[0] - (a + b) / 2)) if lum else (0, 0.0)
            inside = [nearest[1]]
        lum_max = max(inside)
        shots.append({
            "start": round(a, 3),
            "end": round(b, 3),
            "luma_max": lum_max,
            "scrim": bool(lum_max > threshold),
            "samples": len(inside),
        })

    on = sum(1 for s in shots if s["scrim"])
    return {
        "source": src.name,
        "aspect": aspect,
        "width": w,
        "height": hh,
        "duration_s": round(dur, 3),
        "band": {"y0": y0, "y1": y1},
        "threshold": threshold,
        "metric": "median luma of caption band, max over shot",
        "method": "scdet scene cuts + sampled median luma; decision per shot",
        "shot_count": len(shots),
        "scrim_on_shots": on,
        "scrim_on_ratio": round(on / len(shots), 3) if shots else 0.0,
        "shots": shots,
        "note": "luma_max يقاوم اللمعات المفردة؛ فوق العتبة ⇒ لوحة مسطّحة فقط (لا تدرّج)",
    }


def apply_to(captions: list[dict], shots: list[dict]) -> int:
    """يحقن `luma` في كل سطر كابشن حسب المشهد الذي يقع فيه.

    الوسيط يُقصد به هنا: نأخذ **أعلى** سطوع في المشهد (`luma_max`) لا أوسطه،
    لأن الكابشن يبقى ثانية أو ثانيتين فوق خلفية متغيّرة — أسوأ لحظة هي التي تحكم.
    """
    n = 0
    for c in captions:
        try:
            mid = (float(c["t_in"]) + float(c["t_out"])) / 2
        except (KeyError, TypeError, ValueError):
            continue
        for sh in shots:
            if sh["start"] <= mid < sh["end"]:
                c["luma"] = sh["luma_max"]
                n += 1
                break
    return n


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="خريطة اللوحة التكيفية للكابشن")
    ap.add_argument("source")
    ap.add_argument("--aspect", default="9x16", choices=sorted(BANDS))
    ap.add_argument("--samples", type=int, default=120, help="عدد العيّنات على طول الفيديو")
    ap.add_argument("--scene-thresh", type=float, default=0.30)
    ap.add_argument("--threshold", type=float, default=None)
    ap.add_argument("--min-shot", type=float, default=None)
    ap.add_argument("--brand", default="data/brand.json")
    ap.add_argument("--out", default=None)
    ap.add_argument("--apply", default=None,
                    help="ملف كابشن JSON (قائمة فيها t_in/t_out) — يُحقن فيه luma لكل سطر")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    cfg = dict(DEFAULTS)
    bp = Path(a.brand)
    if bp.is_file():
        try:
            brand = json.loads(bp.read_text(encoding="utf-8"))
            cfg.update((brand.get("captions", {}) or {}).get("scrim", {}) or {})
        except Exception:
            pass
    thresh = a.threshold if a.threshold is not None else float(cfg["threshold"])
    min_shot = a.min_shot if a.min_shot is not None else float(cfg["min_shot_s"])

    src = Path(a.source)
    if not src.is_file():
        sys.exit(f"❌ الملف غير موجود: {src}")

    data = build(src, a.aspect, a.samples, a.scene_thresh, thresh, min_shot)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
    touched = None
    if a.apply:
        ap_path = Path(a.apply)
        if not ap_path.is_file():
            sys.exit(f"❌ ملف الكابشن غير موجود: {ap_path}")
        raw = json.loads(ap_path.read_text(encoding="utf-8"))
        # نقبل الشكلين: قائمة مباشرة، أو {data: [...]}
        holder = raw if isinstance(raw, list) else raw.get("data")
        if not isinstance(holder, list) or not holder:
            sys.exit("❌ ملف الكابشن لازم قائمة أسطر فيها t_in/t_out (أو {data: [...]})")
        touched = apply_to(holder, data["shots"])
        out_apply = Path(a.out).with_name(ap_path.name) if a.out else ap_path
        out_apply.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if not a.quiet:
            print(f"\n→ حُقن `luma` في {touched} سطر كابشن داخل {out_apply}")

    if not a.quiet:
        print(f"# SCRIM MAP — {data['source']}  ({data['width']}×{data['height']} · {data['duration_s']}s)")
        print(f"العتبة {data['threshold']} · مشاهد {data['shot_count']} · لوحة على {data['scrim_on_shots']} "
              f"({data['scrim_on_ratio'] * 100:.0f}%)")
        print()
        print("| # | من | إلى | وسيط السطوع | لوحة |")
        print("|---|---|---|---|---|")
        for i, s in enumerate(data["shots"], 1):
            print(f"| {i} | {s['start']:.2f} | {s['end']:.2f} | {s['luma_max']:.3f} | "
                  f"{'نعم' if s['scrim'] else 'لا'} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
