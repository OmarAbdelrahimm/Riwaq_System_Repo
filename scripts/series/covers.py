"""أغلفة يوتيوب A/B (1280×720 + 1080×1920) بأسلوب رواق، من لقطات حقيقية للشيخ في الماستر."""
from __future__ import annotations

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

import graphics as G  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

FF = "/tmp/venv/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
INK = (26, 24, 21)


def grab(master: str, t: float, out: str = "/tmp/grab.png", inset: bool = True) -> str:
    """لقطة من الفيديو — افتراضيًا من داخل الإطار فقط (بدون شريط الكابشن أو ترويسة القالب)."""
    vf = "crop=1440:808:240:108,scale=1920:1080:flags=lanczos" if inset else "scale=1920:1080"
    subprocess.run([FF, "-v", "error", "-copyts", "-ss", str(t), "-i", master,
                    "-frames:v", "1", "-vf", vf, "-y", out], check=True)
    return out


def cover_h(title_lines: list[str], kicker: str, frame: Image.Image, out: str,
            name: str = "ياسر الحزيمي", badge: str | None = None) -> str:
    """غلاف أفقي: نصف صورة + نصف نص، بالهوية الذهبية."""
    W, H = 1280, 720
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    # الصورة على اليمين مع قصّ ذكي (يمين الإطار = تجاه الشيخ)
    ph_h = H
    ph_w = int(W * 0.50)
    f = frame.convert("RGB")
    scale = max(ph_w / f.width, ph_h / f.height)
    f2 = f.resize((int(f.width * scale + 0.5), int(f.height * scale + 0.5)), Image.LANCZOS)
    left = int(f2.width * 0.42)
    top = int((f2.height - ph_h) * 0.30)
    f2 = f2.crop((left, top, left + ph_w, top + ph_h))
    img.paste(f2, (W - ph_w, 0))
    # تدرّج داكن يسار الصورة لينصهر مع خلفية النص
    grad = Image.new("L", (ph_w, ph_h), 0)
    gd = ImageDraw.Draw(grad)
    for x in range(ph_w):
        v = 255 * max(0.0, 1 - x / (ph_w * 0.62)) ** 1.25
        gd.line([(x, 0), (x, ph_h)], fill=int(min(255, v)))
    img.paste(Image.new("RGB", (ph_w, ph_h), INK), (W - ph_w, 0), grad)

    # إطار ذهبي
    d.rectangle([16, 16, W - 17, H - 17], outline=G.GOLD, width=2)
    # الشعار أعلى اليسار
    lock = G.brand_lockup(120, color=G.PARCH)
    img.paste(lock, (52, 44), lock)

    # النص
    text_w_max = W - ph_w - 96
    x0 = 62
    y = 232
    f_k = G.font(G.PLEX_B, 30)
    G.draw_ar(d, (x0, y), kicker, f_k, G.GOLD_L)
    y += 56
    for line in title_lines:
        fnt = G.fit_font(G.AMIRI_B, line, text_w_max, 92, 44)
        G.draw_ar(d, (x0, y), line, fnt, G.PARCH,
                  stroke=3, stroke_fill=(14, 13, 11))
        y += int(fnt.size * 1.34)
    # توقيع الشيخ أعلى الشارة، مثبّت على قاعدة ثابتة أسفل الغلاف
    badge_top = H - 92
    f_n = G.font(G.PLEX_M, 30)
    sig_y = badge_top - 34
    G.draw_ar(d, (x0, sig_y), name, f_n, (210, 199, 178), anchor="ls")
    if badge:
        f_b = G.font(G.PLEX_B, 26)
        bw = G.text_w(f_b, G.ar(badge)) + 34
        d.rounded_rectangle([x0, badge_top, x0 + bw, badge_top + 46], radius=23,
                            fill=(58, 48, 30), outline=G.GOLD_L, width=2)
        G.draw_ar(d, (x0 + 17, badge_top + 23), badge, f_b, G.PARCH, anchor="lm")
    img.save(out, quality=92)
    return out


def cover_vertical(title_lines: list[str], kicker: str, frame: Image.Image, out: str,
                   name: str = "ياسر الحزيمي") -> str:
    W, H = 1080, 1920
    img = Image.new("RGB", (W, H), INK)
    f = frame.convert("RGB")
    scale = max(W / f.width, (H * 0.70) / f.height)
    f2 = f.resize((int(f.width * scale + 0.5), int(f.height * scale + 0.5)), Image.LANCZOS)
    left = (f2.width - W) // 2
    f2 = f2.crop((left, int((f2.height - H * 0.70) * 0.22), left + W, int((f2.height - H * 0.70) * 0.22 + H * 0.70)))
    img.paste(f2, (0, 0))
    # تدرّج داكن لأسفل
    oy = int(H * 0.70)
    grad = Image.new("L", (1, oy), 0)
    gd = ImageDraw.Draw(grad)
    for y in range(oy):
        gd.point((0, y), fill=int(255 * (y / oy) ** 1.6))
    img.paste(Image.new("RGB", (W, oy), INK), (0, 0),
              grad.resize((W, oy)))
    d = ImageDraw.Draw(img)
    d.rectangle([20, 20, W - 21, H - 21], outline=G.GOLD, width=3)
    lock = G.brand_lockup(140, color=G.PARCH)
    img.paste(lock, (60, 70), lock)
    y = oy - 150
    f_k = G.font(G.PLEX_B, 44)
    G.draw_ar(d, (60, y), kicker, f_k, G.GOLD_L)
    y += 70
    for line in title_lines:
        fnt = G.fit_font(G.AMIRI_B, line, W - 120, 132, 62)
        G.draw_ar(d, (60, y), line, fnt, G.PARCH, stroke=4, stroke_fill=(14, 13, 11))
        y += int(fnt.size * 1.0)
    # مساحة آمنة سفلية (لا نضع شيئًا في آخر 240px)
    f_n = G.font(G.PLEX_M, 42)
    G.draw_ar(d, (60, H - 300), name, f_n, (210, 199, 178))
    img.save(out, quality=92)
    return out
