"""HARUN v4 — غلافا يوتيوب A/B (1280×720) بقواعد السيو البصري.

قواعد مطبَّقة:
  • عنوان الغلاف ≤ 4 كلمات، يُقرأ على الهاتف.
  • تباين عالٍ: نص رقّي + حدّ أسود سميك على خلفية داكنة.
  • الوجه في ثلث، والنص في الثلث المقابل.
  • منطقة آمنة: لا شيء في آخر 46px أسفل اليمين (شارة المدة).
  • هوية رواق: الإطار الذهبي + الشعار.
"""
from __future__ import annotations

import os
import subprocess
import sys

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

REPO = "/home/user/Riwaq_System_Repo"
AMIRI_B = f"{REPO}/public/fonts/Amiri-Bold.ttf"
PLEX_B = f"{REPO}/public/fonts/IBMPlexSansArabic-Bold.ttf"
PLEX_M = f"{REPO}/public/fonts/IBMPlexSansArabic-Medium.ttf"
FF = ("/home/user/.venv_tools/lib/python3.11/site-packages/imageio_ffmpeg/binaries/"
      "ffmpeg-linux-x86_64-v7.0.2")

W, H = 1280, 720
INK = (18, 16, 12)
PARCH = (243, 235, 219)
GOLD = (169, 138, 75)
GOLD_L = (205, 176, 116)
STONE = (150, 138, 118)


def ar(t: str) -> str:
    return get_display(arabic_reshaper.reshape(t))


def grab(video: str, t: float) -> Image.Image:
    out = f"/tmp/coverframe_{int(t*100)}.png"
    subprocess.run([FF, "-v", "error", "-ss", str(t), "-i", video,
                    "-frames:v", "1", "-y", out], check=True)
    return Image.open(out).convert("RGB")


def fit(text: str, path: str, max_w: int, start: int, floor: int):
    px = start
    while px > floor:
        f = ImageFont.truetype(path, px)
        b = f.getbbox(ar(text))
        if b[2] - b[0] <= max_w:
            return f
        px -= 2
    return ImageFont.truetype(path, floor)


def kasra_word(d, x_right, y, text, fnt, fill):
    """كلمة تنتهي بكسرة مرسومة تحت آخر حرف (reshaper يُسقط الحركات)."""
    s_ = ar(text)
    w_ = fnt.getlength(s_)
    d.text((x_right - w_, y), s_, font=fnt, fill=fill)
    return w_


def build(video: str, t_face: float, kicker: str, lines: list[str],
          badge: str, out_path: str, zoom: float = 1.0) -> str:
    base = Image.new("RGB", (W, H), INK)
    ph = grab(video, t_face)
    if ph.size == (1920, 1080):          # ماستر نهائي: نافذة الفيديو النظيفة فقط
        ph = ph.crop((249, 94, 1671, 894))
    px0, px1, py0, py1 = 596, 1247, 30, 690
    ph_w, ph_h = px1 - px0, py1 - py0
    scale = max(ph_w / ph.width, ph_h / ph.height) * zoom
    ph2 = ph.resize((int(ph.width*scale + 0.5), int(ph.height*scale + 0.5)), Image.LANCZOS)
    cx = ph2.width // 2
    top = max(0, (ph2.height - ph_h) // 2 - 14)
    base.paste(ph2.crop((cx - ph_w//2, top, cx - ph_w//2 + ph_w, top + ph_h)), (px0, py0))

    # تلاشٍ عريض: لا حدّ رأسي مرئي بين النص والصورة
    grad = Image.new("L", (ph_w, ph_h), 0)
    gd = ImageDraw.Draw(grad)
    for x in range(ph_w):
        gd.line([(x, 0), (x, ph_h)], fill=int(255 * max(0.0, 1 - x/(ph_w*0.92))**0.85))
    base.paste(Image.new("RGB", (ph_w, ph_h), INK), (px0, py0), grad)
    base = Image.alpha_composite(base.convert("RGBA"),
                                 Image.new("RGBA", (W, H), (10, 9, 7, 46))).convert("RGB")

    # سطوع أعلى اليمين لقراءة الشعار على أي صورة
    scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    sd.rounded_rectangle([W - 214, 26, W - 40, 138], radius=12, fill=(12, 11, 8, 132))
    base = Image.alpha_composite(base.convert("RGBA"), scrim).convert("RGB")

    d = ImageDraw.Draw(base)
    d.rectangle([26, 24, W-27, H-25], outline=GOLD, width=2)
    d.rectangle([32, 30, W-33, H-31], outline=(58, 50, 34), width=1)

    d.text((W - 196, 40), ar("رواق"), font=ImageFont.truetype(AMIRI_B, 44), fill=PARCH)
    d.text((W - 196, 98), ar("تاريخ وتراث"),
           font=ImageFont.truetype(PLEX_M, 18), fill=STONE)

    x_right = px0 - 34
    text_max = x_right - 92
    f_k = ImageFont.truetype(PLEX_B, 29)
    kb = f_k.getbbox(ar(kicker))
    d.text((x_right - (kb[2]-kb[0]), 176), ar(kicker), font=f_k, fill=GOLD_L)

    y = 236
    for line in lines:
        f = fit(line, AMIRI_B, text_max, 124 if len(lines) <= 2 else 100, 62)
        s = ar(line)
        b = f.getbbox(s)
        d.text((x_right - (b[2]-b[0]) - b[0], y), s, font=f, fill=PARCH,
               stroke_width=5, stroke_fill=(10, 9, 7))
        y += int((b[3]-b[1]) * 1.20)

    f_b = ImageFont.truetype(PLEX_B, 24)
    bb = f_b.getbbox(ar(badge))
    bw = bb[2]-bb[0] + 40
    by = H - 108
    d.rounded_rectangle([x_right - bw, by, x_right, by+44], radius=22,
                        fill=(38, 32, 22), outline=GOLD, width=2)
    d.text((x_right - bw + 20 - bb[0], by + 8), ar(badge), font=f_b, fill=PARCH)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    base.save(out_path, quality=95, subsampling=0)
    return out_path


def main() -> None:
    video = sys.argv[1] if len(sys.argv) > 1 else "/home/user/work_v4/retimed_full.mp4"
    outdir = sys.argv[2] if len(sys.argv) > 2 else f"{REPO}/exports/HARUN_001/publish"
    print(build(video, 9.8, "حكايات رواق", ["الرجل الحكيم", "و٣ أسئلة"],
                "هارون الرشيد", f"{outdir}/COVER_A_1280x720.jpg"))
    print(build(video, 63.4, "حكايات رواق", ["جمادات", "تكلّمت"],
                "لغز الحكيم", f"{outdir}/COVER_B_1280x720.jpg", zoom=1.16))


if __name__ == "__main__":
    main()
