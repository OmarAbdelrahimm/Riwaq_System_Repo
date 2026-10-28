"""HARUN v4 — إعادة توقيت الحركة (إصلاح التقطيع الذي رصده صاحب العمل).

المشكلة المقيسة في المصدر 1280×720@30:
  • 61 إطارًا مكرّرًا حرفيًا (تجمّد ثم قفزة) → إحساس «لاج».
  • تباعد الإطارات الحقيقية غير منتظم (1 / 2 / 3 إطارات) ومعدّل المحتوى
    الفعلي يتغيّر بين 12 و24 إطارًا/ثانية حسب المقطع → اهتزاز على فترات مختلفة.

الحل: توزيع الحركة على شبكة منتظمة 30fps بتدفّق بصري (Farneback)، مع حماية
القطعات: عند تغيّر مشهد حقيقي لا يُدمج الإطاران إطلاقًا.

الاستخدام: python scripts/harun_v4_retime.py <t0> <t1> <out.mp4> [crf]
"""
from __future__ import annotations

import subprocess
import sys
import time

import av
import cv2
import numpy as np

SRC = ("/home/user/Riwaq_System_Repo/google_drive/"
       "01-VID-harun-al-rashid-and-the-wise-man-v1.mp4")
FF = ("/home/user/.venv_tools/lib/python3.11/site-packages/imageio_ffmpeg/binaries/"
      "ffmpeg-linux-x86_64-v7.0.2")
FPS = 30
DUP_EPS = 0.35
CUT_EPS = 16.0
DOWN = 2
CHUNK = 8.0


def small(img: np.ndarray, w: int = 160, h: int = 90) -> np.ndarray:
    g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return cv2.resize(g, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32)


def flow(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    h, w = a.shape
    A = cv2.resize(a, (w // DOWN, h // DOWN), interpolation=cv2.INTER_AREA)
    B = cv2.resize(b, (w // DOWN, h // DOWN), interpolation=cv2.INTER_AREA)
    f = cv2.calcOpticalFlowFarneback(A, B, None, 0.5, 4, 17, 4, 7, 1.2, 0)
    f = cv2.resize(f, (w, h), interpolation=cv2.INTER_LINEAR)
    f[..., 0] *= DOWN
    f[..., 1] *= DOWN
    return f


_G: dict = {}


def mesh(w: int, h: int):
    if (w, h) not in _G:
        _G[(w, h)] = np.meshgrid(np.arange(w, dtype=np.float32),
                                 np.arange(h, dtype=np.float32))
    return _G[(w, h)]


def warp(img: np.ndarray, f: np.ndarray) -> np.ndarray:
    h, w = img.shape[:2]
    gx, gy = mesh(w, h)
    return cv2.remap(img, gx + f[..., 0], gy + f[..., 1],
                     interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def blend(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    out = (1.0 - t) * a.astype(np.float32) + t * b.astype(np.float32)
    return np.clip(out + 0.5, 0, 255).astype(np.uint8)


def gather(t0: float, t1: float):
    c = av.open(SRC)
    s = c.streams.video[0]
    frames, prev = [], None
    try:
        for fr in c.decode(s):
            t = float(fr.pts * s.time_base)
            if t < t0 - 1e-6:
                continue
            if t >= t1 - 1e-6:
                break
            arr = np.asarray(fr.to_image().convert("RGB"))
            sm = small(arr)
            if prev is not None and float(np.abs(sm - prev).mean()) < DUP_EPS:
                prev = sm
                continue
            frames.append((t, arr))
            prev = sm
    finally:
        c.close()
    return frames


def main() -> None:
    t_start = time.time()
    t0 = float(sys.argv[1])
    t1 = float(sys.argv[2])
    out = sys.argv[3]
    crf = sys.argv[4] if len(sys.argv) > 4 else "13"

    probe = av.open(SRC)
    W = probe.streams.video[0].codec_context.width
    H = probe.streams.video[0].codec_context.height
    probe.close()

    enc = subprocess.Popen(
        [FF, "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0", "-an",
         "-c:v", "libx264", "-preset", "medium", "-crf", crf,
         "-pix_fmt", "yuv420p", "-x264-params", "keyint=60:min-keyint=30:scenecut=0",
         "-y", out], stdin=subprocess.PIPE)

    stats = {"warped": 0, "held": 0, "cut": 0}
    pos = t0
    while pos < t1 - 1e-6:
        end = min(t1, pos + CHUNK)
        frames = gather(pos, end + 0.05)
        if not frames:
            break
        grays = [cv2.cvtColor(f[1], cv2.COLOR_RGB2GRAY) for f in frames]
        sms = [small(f[1]) for f in frames]
        flows, cuts = [], []
        for i in range(len(frames) - 1):
            d = float(np.abs(sms[i + 1] - sms[i]).mean())
            cut = d > CUT_EPS
            cuts.append(cut)
            flows.append(None if cut else flow(grays[i], grays[i + 1]))

        i = 0
        for k in range(int(round((pos - t0) * FPS)), int(round((end - t0) * FPS))):
            t = t0 + k / FPS
            while i + 1 < len(frames) and frames[i + 1][0] <= t + 1e-9:
                i += 1
            if i + 1 >= len(frames):
                frame = frames[i][1]
                stats["held"] += 1
            else:
                ta, A = frames[i]
                tb, B = frames[i + 1]
                if cuts[i] or flows[i] is None or tb - ta < 1e-6:
                    frame = A if t < (ta + tb) / 2 else B
                    stats["cut"] += 1
                else:
                    fr_ = min(1.0, max(0.0, (t - ta) / (tb - ta)))
                    wa = warp(A, flows[i] * fr_)
                    wb = warp(B, -flows[i] * (1.0 - fr_))
                    frame = blend(wa, wb, fr_)
                    stats["warped"] += 1
            enc.stdin.write(frame.astype(np.uint8).tobytes())
        pos = end
        print(f"  {pos:6.1f}s / {t1:.1f}s  {stats}", flush=True)

    enc.stdin.close()
    enc.wait()
    print("done", out, f"{time.time()-t_start:.0f}s", stats)


if __name__ == "__main__":
    main()
