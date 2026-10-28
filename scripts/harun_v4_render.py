"""HARUN v4 — التجميع النهائي: فيديو معاد توقيته + الإطار + الكابشن + المؤثرات.

ffmpeg واحد، صورة واحدة لكل إطار:
  المصدر (1280×720@30 محسّن الحركة) → lanczos إلى 1422×800 → pad 1920×1080 عند (249,94)
  → طبقة الإطار (نافذة شفافة) → الكابشن (ass) → تغميقان ناعمان + شريط ضوء
  → بطاقة «اللغز» → معرّف البداية → تلاشي عام
  → صوت: VO + موسيقى + مؤثرات → loudnorm −16 LUFS

الاستخدام:
  python scripts/harun_v4_render.py --out <path> [--preview 30] [--crf 17]
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

REPO = "/home/user/Riwaq_System_Repo"
FF = ("/home/user/.venv_tools/lib/python3.11/site-packages/imageio_ffmpeg/binaries/"
      "ffmpeg-linux-x86_64-v7.0.2")
FRAME = f"{REPO}/public/projects/HARUN_001/frame_v4"
AUDIO = f"{REPO}/public/projects/HARUN_001/audio_v4"
ASS = (f"{REPO}/data/projects/HARUN_001/captions_v4.ass"
       if os.path.exists(f"{REPO}/data/projects/HARUN_001/captions_v4.ass")
       else "/tmp/harun_v4.ass")
VO = f"{REPO}/google_drive/‎⁨الصوت قصة هارون الرشيد والرجل الحكيم 2⁩.wav"
SRC = "/home/user/work_v4/retimed_full.mp4"
FONTCONF = "/home/user/work_v4/fc/fonts.conf"

VX, VY, VW, VH = 249, 94, 1422, 800
DIP1 = (37.85, 38.45)
DIP2 = (126.10, 126.70)
RIDDLE = (131.48, 135.10)
IDENT_END = 1.70
DUR = 159.25


def graph() -> str:
    d1s, d1e = DIP1[0] - 0.28, DIP1[1] + 0.28
    d2s, d2e = DIP2[0] - 0.28, DIP2[1] + 0.28
    sw1, sw2 = DIP1[0] - 0.10, DIP2[0] - 0.10
    rs, re_ = RIDDLE
    v = []
    # دفعة (push-in) ناعمة ٤.٥٪ على مدى الحلقة: تمنع «اللاج» لأن كل إطار
    # يتغيّر ولو بكسر بكسel — المصدر المولَّد يحتوي ٢١ ث من الإطارات المتطابقة.
    z = 0.045 / (DUR * 30)
    v.append(f"[0:v]scale=2048:1152:flags=lanczos,setsar=1,"
             f"zoompan=z='1+{z:.8f}*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
             f":d=1:s={VW}x{VH}:fps=30,unsharp=5:5:0.07:5:5:0,setsar=1,"
             f"pad=1920:1080:{VX}:{VY}:color=black@0[win]")
    v.append("[win][1:v]overlay=0:0:format=auto:eof_action=pass[framed]")
    v.append(f"[framed]ass={ASS}[cap]")
    v.append(f"[3:v]format=rgba,scale=1920:1080,loop=loop=-1:size=1:start=0,"
             f"fade=in:st={d1s}:d=0.30:alpha=1,fade=out:st={d1e}:d=0.34:alpha=1[v1]")
    v.append(f"[4:v]format=rgba,scale=1920:1080,loop=loop=-1:size=1:start=0,"
             f"fade=in:st={d2s}:d=0.30:alpha=1,fade=out:st={d2e}:d=0.34:alpha=1[v2]")
    v.append("[5:v]format=rgba,loop=loop=-1:size=1:start=0[swraw]")
    v.append("[swraw]split=2[sw1][sw2]")
    v.append(f"[cap][v1]overlay=0:0:format=auto:eof_action=pass:"
             f"enable='between(t,{d1s},{d1e+0.34})'[o1]")
    v.append(f"[o1][v2]overlay=0:0:format=auto:eof_action=pass:"
             f"enable='between(t,{d2s},{d2e+0.34})'[o2]")
    v.append(f"[o2][sw1]overlay=x='-620+2520*(t-{sw1})/1.0':y=0:format=auto:eof_action=pass:"
             f"enable='between(t,{sw1},{sw1+1.0})'[o3]")
    v.append(f"[o3][sw2]overlay=x='-620+2520*(t-{sw2})/1.0':y=0:format=auto:eof_action=pass:"
             f"enable='between(t,{sw2},{sw2+1.0})'[o4]")
    v.append(f"[6:v]format=rgba,loop=loop=-1:size=1:start=0,"
             f"fade=in:st={rs}:d=0.45:alpha=1,fade=out:st={re_-0.55}:d=0.55:alpha=1[rid]")
    v.append(f"[o4][rid]overlay=x=(W-w)/2:y=430:format=auto:eof_action=pass:"
             f"enable='between(t,{rs},{re_})'[o5]")
    v.append(f"[7:v]format=rgba,loop=loop=-1:size=1:start=0,"
             f"fade=in:st=0.25:d=0.30:alpha=1,fade=out:st={IDENT_END-0.45}:d=0.45:alpha=1[ident]")
    v.append(f"[o5][ident]overlay=0:0:format=auto:eof_action=pass:"
             f"enable='between(t,0.25,{IDENT_END})'[o6]")
    v.append(f"[o6]fade=in:st=0:d=0.40,fade=out:st={DUR-0.95}:d=0.95,"
             f"format=yuv420p,setsar=1[vout]")
    # صوت
    a = (f"[8:a]aresample=48000,aformat=channel_layouts=stereo,"
         f"loudnorm=I=-16:TP=-2.2:LRA=11,volume=-1.9dB[vo];"
         f"[9:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.135[bed];"
         f"[10:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.80[sfx];"
         f"[vo][bed][sfx]amix=inputs=3:duration=first:dropout_transition=0:normalize=0[mix];"
         f"[mix]alimiter=limit=0.891,afade=in:st=0:d=0.30,"
         f"afade=out:st={DUR-1.1}:d=1.1[aout]")
    return ";".join(v) + ";" + a


def build(out: str, crf: int, preset: str, preview: float | None) -> list[str]:
    return [FF, "-v", "warning", "-stats",
            "-i", SRC,
            "-loop", "1", "-i", f"{FRAME}/FRAME_plate.png",
            "-loop", "1", "-i", f"{FRAME}/CARD_riddle.png",
            "-loop", "1", "-i", f"{FRAME}/veil.png",
            "-loop", "1", "-i", f"{FRAME}/veil.png",
            "-loop", "1", "-i", f"{FRAME}/sweep.png",
            "-loop", "1", "-i", f"{FRAME}/CARD_riddle.png",
            "-loop", "1", "-i", f"{FRAME}/OVERLAY_ident.png",
            "-i", VO,
            "-i", f"{AUDIO}/bed.wav",
            "-i", f"{AUDIO}/sfx.wav",
            "-filter_complex", graph(),
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
            "-profile:v", "high", "-level", "4.1", "-pix_fmt", "yuv420p",
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
            "-x264-params", "keyint=60:min-keyint=30",
            "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
            "-movflags", "+faststart",
            "-t", str(preview if preview else DUR), "-y", out]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=f"{REPO}/exports/HARUN_001/HARUN_001_v4_1920x1080.mp4")
    ap.add_argument("--crf", type=int, default=17)
    ap.add_argument("--preset", default="slow")
    ap.add_argument("--preview", type=float, default=None)
    a = ap.parse_args()

    for need, hint in ((ASS, "harun_v4_captions.py"), (SRC, "harun_v4_retime.py"),
                       (f"{AUDIO}/bed.wav", "harun_v4_audio.py")):
        if not os.path.exists(need):
            sys.exit(f"missing {need} — run scripts/{hint} first")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    env = dict(os.environ, FONTCONFIG_FILE=FONTCONF)
    subprocess.run(build(a.out, a.crf, a.preset, a.preview), check=True, env=env)
    print("wrote", a.out, os.path.getsize(a.out) / 1e6, "MB")


if __name__ == "__main__":
    main()
