#!/usr/bin/env python3
"""extract_frames.py — يسحب إطارات من فيديو عند ثواني معينة (بدون فلاتر ffmpeg)."""
import subprocess, sys, os

FF = "node_modules/@remotion/compositor-linux-x64-gnu/ffmpeg"


def grab(video, times, outdir="/tmp/frames", width=460):
    os.makedirs(outdir, exist_ok=True)
    paths = []
    for t in times:
        out = os.path.join(outdir, f"t{str(t).replace('.', '_')}.png")
        # -ss قبل -i = سريع ودقيق
        r = subprocess.run(
            [FF, "-y", "-ss", str(t), "-i", video, "-frames:v", "1",
             "-vf", f"scale={width}:-1", out],
            capture_output=True)
        if os.path.exists(out) and os.path.getsize(out) > 1000:
            paths.append(out)
            print(f"  ✅ {t}s")
        else:
            print(f"  ❌ {t}s — {r.stderr.decode()[-200:]}")
    return paths


if __name__ == "__main__":
    v = sys.argv[1]
    ts = [float(x) for x in sys.argv[2].split(",")]
    grab(v, ts)
