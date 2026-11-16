"""Measured QC for the EP13 0-6 s proof.

    .venv/bin/python tools/ep13/qc.py --frames render/ep13/frames_v2 \
        --control render/ep13/frames_v2_nocam --out render/ep13/QC_REPORT.json

What it measures (nothing here is asserted by eye only):
  * motion   : mean |delta RGB| between consecutive frames inside named regions
  * control  : the same regions with the camera push disabled, so a region that
               moves only because of the camera is not counted as animation
  * freeze   : frames where nothing at all changed (a frozen pair)
  * legibility: p95-p5 luminance spread inside the type boxes, and the same
               after a 360 px downsample (phone-size check)
  * frame    : mean luminance of the four border strips (nothing black-clipped)
  * palette  : share of pixels inside the approved + pending brand ranges
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

# regions in output pixels (1280x720)
REGIONS = {
    "fish_body": (250, 425, 425, 505),
    "fish_tail": (185, 420, 250, 520),
    "glass_milk": (855, 400, 955, 505),
    "claim_card": (620, 400, 960, 570),
    "headline": (330, 165, 860, 225),
    "bg_dust_control": (60, 210, 170, 270),
}
TYPE_BOXES = {
    "headline": (338, 160, 950, 235),
    "kicker": (594, 116, 676, 136),
    "gold_word": (478, 158, 537, 235),
}
PHASES = {"S1a_fish": (0, 22), "S1b_settle": (22, 54), "S2_break": (54, 91), "S3_claim": (91, 180)}


def load(folder: Path, idx: int, box) -> np.ndarray:
    im = Image.open(folder / f"{idx:04d}.png").convert("RGB")
    x0, y0, x1, y1 = box
    return np.asarray(im.crop((x0, y0, x1, y1)), dtype=np.float32)


def region_stats(folder: Path, total: int) -> dict:
    out = {}
    prev = {k: load(folder, 0, b) for k, b in REGIONS.items()}
    deltas = {k: np.zeros(total - 1, dtype=np.float32) for k in REGIONS}
    lum = np.zeros(total, dtype=np.float32)
    lum[0] = np.asarray(Image.open(folder / "0000.png").convert("L")).mean()
    for i in range(1, total):
        for k, b in REGIONS.items():
            cur = load(folder, i, b)
            deltas[k][i - 1] = np.abs(cur - prev[k]).mean()
            prev[k] = cur
        lum[i] = np.asarray(Image.open(folder / f"{i:04d}.png").convert("L")).mean()
    for k, d in deltas.items():
        phases = {}
        for name, (a, b) in PHASES.items():
            seg = d[max(0, a - 1):b - 1]
            phases[name] = round(float(seg.mean()), 3) if seg.size else 0.0
        out[k] = {
            "mean_delta": round(float(d.mean()), 3),
            "max_delta": round(float(d.max()), 3),
            "max_at_frame": int(d.argmax()) + 1,
            "moving_frames": int((d > 0.05).sum()),
            "phase_mean_delta": phases,
        }
    out["_frame_luminance"] = {"min": round(float(lum.min()), 2),
                               "max": round(float(lum.max()), 2)}
    return out


def freeze_report(folder: Path, total: int) -> list[int]:
    frozen = []
    prev = np.asarray(Image.open(folder / "0000.png").convert("RGB"), dtype=np.int16)
    for i in range(1, total):
        cur = np.asarray(Image.open(folder / f"{i:04d}.png").convert("RGB"), dtype=np.int16)
        if np.abs(cur - prev).max() == 0:
            frozen.append(i)
        prev = cur
    return frozen


def legibility(folder: Path, frame: int) -> dict:
    im = Image.open(folder / f"{frame:04d}.png").convert("L")
    res = {}
    for name, box in TYPE_BOXES.items():
        if box[2] <= box[0]:
            continue
        crop = im.crop(box)
        a = np.asarray(crop, dtype=np.float32)
        p5, p95 = np.percentile(a, [5, 95])
        small = np.asarray(crop.resize((max(1, crop.width // 4), max(1, crop.height // 4)),
                                       Image.LANCZOS), dtype=np.float32)
        sp5, sp95 = np.percentile(small, [5, 95])
        res[name] = {"full_spread": round(float(p95 - p5), 1),
                     "at_25pct_scale_spread": round(float(sp95 - sp5), 1)}
    return res


def border_report(folder: Path, frame: int) -> dict:
    a = np.asarray(Image.open(folder / f"{frame:04d}.png").convert("L"), dtype=np.float32)
    h, w = a.shape
    return {"top": round(float(a[:3].mean()), 1), "bottom": round(float(a[-3:].mean()), 1),
            "left": round(float(a[:, :3].mean()), 1), "right": round(float(a[:, -3:].mean()), 1)}


def palette_share(folder: Path, frame: int) -> dict:
    a = np.asarray(Image.open(folder / f"{frame:04d}.png").convert("RGB"), dtype=np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    gold = (r > g) & (g > b) & (b < 150) & (r > 90)
    cyan = (b > r) & (b > 30) & (g > r)
    coral = (r > b) & (r > 60) & (g < r * 0.92)
    total = a.shape[0] * a.shape[1]
    return {"gold_pct": round(float(gold.sum()) / total * 100, 2),
            "cyan_pct": round(float(cyan.sum()) / total * 100, 2),
            "coral_pct": round(float(coral.sum()) / total * 100, 2)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", required=True)
    ap.add_argument("--control", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--total", type=int, default=180)
    a = ap.parse_args()

    main_dir, ctrl_dir = Path(a.frames), Path(a.control)
    report = {
        "frames": a.total,
        "fps": 30,
        "duration_s": a.total / 30,
        "resolution": "1280x720",
        "camera_on": region_stats(main_dir, a.total),
        "camera_off": region_stats(ctrl_dir, a.total),
        "frozen_pairs_camera_on": freeze_report(main_dir, a.total),
        "frozen_pairs_camera_off": freeze_report(ctrl_dir, a.total),
        "legibility": {str(f): legibility(main_dir, f) for f in (0, 20, 54, 70, 120, 179)},
        "borders": {str(f): border_report(main_dir, f) for f in (0, 54, 90, 179)},
        "palette_share": {str(f): palette_share(main_dir, f) for f in (20, 54, 120, 179)},
    }
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(report, indent=2))

    hdr = f"{'region':<16}{'cam-on':>8}{'cam-off':>9}{'move':>6}" + "".join(f"{p:>11}" for p in PHASES)
    print(hdr)
    for k in REGIONS:
        on, off = report["camera_on"][k], report["camera_off"][k]
        row = f"{k:<16}{on['mean_delta']:>8.2f}{off['mean_delta']:>9.2f}{on['moving_frames']:>6}"
        row += "".join(f"{v:>11.2f}" for v in on["phase_mean_delta"].values())
        print(row)
    print("frozen pairs (cam on):", len(report["frozen_pairs_camera_on"]),
          report["frozen_pairs_camera_on"][:6])
    print("wrote", a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
