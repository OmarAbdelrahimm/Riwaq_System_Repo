"""Render the RUWAQ EP13 0-6 s proof.

Commands (from the repo root):
  .venv/bin/python tools/ep13/render.py frames --out render/ep13/frames_v2
  .venv/bin/python tools/ep13/render.py video  --frames render/ep13/frames_v2 --out render/ep13/PROOF_0_6_v2.mp4
  .venv/bin/python tools/ep13/render.py still  --frame 54 --size 1920x1080 --out render/ep13/STYLEFRAME_A.png
  .venv/bin/python tools/ep13/render.py contact --frames render/ep13/frames_v2 --out render/ep13/PROOF_CONTACT.jpg

The proof MP4 carries the original S01 take (0-6.00 s), trimmed, never stretched.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ep13.scene import Renderer  # noqa: E402
from ep13.timeline import FRAMES  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def ffmpeg() -> str:
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def cmd_frames(args) -> int:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    r = Renderer(args.width, args.height)
    for f in range(args.start, args.end):
        if args.camera_off and not (args.start <= f < args.end):
            continue
        img = r.render(f, camera=not args.camera_off)
        img.save(out / f"{f:04d}.png", compress_level=1)
        if f % 20 == 0:
            print(f"frame {f}/{args.end}", flush=True)
    print("frames done:", out)
    return 0


def cmd_still(args) -> int:
    w, h = (int(v) for v in args.size.lower().split("x"))
    r = Renderer(w, h, ss=2)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    r.render(args.frame).save(args.out)
    print("still:", args.out, (w, h))
    return 0


def cmd_video(args) -> int:
    frames = Path(args.frames)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    audio_src = ROOT / "public/ep13/audio/chapter01.mp3"
    silent = out.with_name(out.stem + "_silent.mp4")
    subprocess.run([
        ffmpeg(), "-v", "error", "-y", "-framerate", "30", "-start_number", "0",
        "-i", str(frames / "%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "slow",
        "-movflags", "+faststart", str(silent),
    ], check=True)
    subprocess.run([
        ffmpeg(), "-v", "error", "-y", "-i", str(silent), "-ss", "0", "-t", "6.000",
        "-i", str(audio_src), "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out),
    ], check=True)
    silent.unlink(missing_ok=True)
    print("video:", out)
    return 0


def cmd_contact(args) -> int:
    from PIL import Image, ImageDraw

    frames = Path(args.frames)
    picks = [0, 20, 40, 60, 90, 120, 150, 179]
    ims = [Image.open(frames / f"{p:04d}.png").convert("RGB") for p in picks]
    cols, rows = 4, 2
    tw, th = ims[0].width // 2, ims[0].height // 2
    pad, label_h = 12, 26
    sheet = Image.new("RGB", (cols * tw + pad * (cols + 1), rows * (th + label_h) + pad * (rows + 1)),
                      (13, 14, 18))
    d = ImageDraw.Draw(sheet)
    for i, (p, im) in enumerate(zip(picks, ims)):
        c, r_ = i % cols, i // cols
        x = pad + c * (tw + pad)
        y = pad + r_ * (th + label_h + pad)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
        d.text((x + 2, y + th + 6), f"frame {p}  ({(p / 30):.2f}s)", fill=(210, 196, 168))
    sheet.save(args.out, quality=92)
    print("contact:", args.out)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("frames")
    f.add_argument("--out", required=True)
    f.add_argument("--start", type=int, default=0)
    f.add_argument("--end", type=int, default=FRAMES)
    f.add_argument("--width", type=int, default=1280)
    f.add_argument("--height", type=int, default=720)
    f.add_argument("--camera-off", action="store_true")
    f.set_defaults(func=cmd_frames)

    s = sub.add_parser("still")
    s.add_argument("--frame", type=int, required=True)
    s.add_argument("--size", default="1920x1080")
    s.add_argument("--out", required=True)
    s.set_defaults(func=cmd_still)

    v = sub.add_parser("video")
    v.add_argument("--frames", required=True)
    v.add_argument("--out", required=True)
    v.set_defaults(func=cmd_video)

    c = sub.add_parser("contact")
    c.add_argument("--frames", required=True)
    c.add_argument("--out", required=True)
    c.set_defaults(func=cmd_contact)

    a = ap.parse_args()
    return a.func(a)


if __name__ == "__main__":
    raise SystemExit(main())
