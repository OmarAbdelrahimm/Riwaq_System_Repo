"""حزمة نشر الشورتس: غلافان A/B (1080×1920) + وثيقة SEO + خطة النشر."""
from __future__ import annotations

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

import graphics as G  # noqa: E402
import shorts_data as D  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

REPO = "/home/user/Riwaq_System_Repo"
OUT = f"{REPO}/outputs/SERIES_RIWAQ/SHORTS"
WORK = f"{REPO}/google_drive/work"
FF = os.environ.get("FFMPEG")


def ff() -> str:
    global FF
    if not FF:
        import imageio_ffmpeg
        FF = imageio_ffmpeg.get_ffmpeg_exe()
    return FF


INK = (26, 24, 21)


def grab(path: str, t: float, out: str) -> str:
    subprocess.run([ff(), "-v", "error", "-copyts", "-ss", str(t), "-i", path,
                    "-frames:v", "1", "-y", out], check=True)
    return out


def cover_short(frame: Image.Image, lines: list[str], kicker: str, order: int,
                out: str) -> str:
    W, H = 1080, 1920
    img = Image.new("RGB", (W, H), INK)
    f = frame.convert("RGB")
    # الصورة تملأ الأعلى؛ التدرّج يمزجها في لوحة النص
    top_h = int(H * 0.66)
    scale = max(W / f.width, top_h / f.height)
    f2 = f.resize((int(f.width * scale + 0.5), int(f.height * scale + 0.5)), Image.LANCZOS)
    left = (f2.width - W) // 2
    f2 = f2.crop((left, 0, left + W, top_h))
    img.paste(f2, (0, 0))

    grad = Image.new("L", (1, top_h), 0)
    gd = ImageDraw.Draw(grad)
    for y in range(top_h):
        gd.point((0, y), fill=int(255 * max(0.0, (y / top_h - 0.42) / 0.58) ** 1.25))
    img.paste(Image.new("RGB", (W, top_h), INK), (0, 0), grad.resize((W, top_h)))

    d = ImageDraw.Draw(img)
    d.rectangle([20, 20, W - 21, H - 21], outline=G.GOLD, width=3)

    lock = G.brand_lockup(150, color=G.PARCH)
    img.paste(lock, (60, 62), lock)

    y = top_h - 40
    G.draw_ar(d, (60, y), kicker, G.font(G.PLEX_B, 46), G.GOLD_L)
    y += 76
    for line in lines:
        fnt = G.fit_font(G.AMIRI_B, line, W - 120, 120, 62)
        G.draw_ar(d, (60, y), line, fnt, G.PARCH, stroke=4, stroke_fill=(12, 11, 9))
        y += int(fnt.size * 1.16)

    # شريط سفلي: الترقيم + اسم الشيخ
    d.line([(60, H - 300), (W - 60, H - 300)], fill=G.GOLD + (255,), width=2)
    f_n = G.font(G.AMIRI_B, 62)
    G.draw_ar(d, (60, H - 268), f"شورت {order} من {D.TOTAL}", f_n, G.PARCH)
    G.draw_ar(d, (60, H - 180), "ياسر الحزيمي", G.font(G.PLEX_M, 44), (210, 199, 178))
    G.draw_ar(d, (W - 60, H - 180), D.CHANNEL, G.font(G.PLEX_M, 34),
              (150, 141, 120), anchor="ra")
    img.save(out, quality=92)
    return out


def seo_md(s: dict) -> str:
    ep = ""
    if s.get("ep"):
        ep = (f"- **الحلقة الكاملة داخل السلسلة:** {D.EP_TITLE[s['ep']]} "
              f"(الحلقة {D.EP_ORDER[s['ep']]} من 3)\n")
    return f"""# حزمة نشر الشورت {s['order']} من {D.TOTAL} — {s['hook']}

**الحساب:** رواق | تاريخ وتراث — https://www.youtube.com/@{D.CHANNEL.lstrip('@')}
**المصدر:** مقتطف من سلسلة «{D.SERIES}» — الشيخ ياسر الحزيمي.
{ep}
## اختبار A/B (عنوان + غلاف)
| | العنوان | الغلاف |
|---|---|---|
| **A** | {s['title_a']} | `COVER_A_1080x1920.jpg` |
| **B** | {s['title_b']} | `COVER_B_1080x1920.jpg` |

> القاعدة: A مع A و B مع B. بعد 48–72 ساعة ثبّت الفائز في العنوان وثبّت غلافه.

## الوصف الجاهز (A)
{s['desc']}

شورت {s['order']} من {D.TOTAL} في سلسلة «{D.SERIES}» للشيخ ياسر الحزيمي.

🎬 السلسلة الكاملة على القناة: https://www.youtube.com/@{D.CHANNEL.lstrip('@')}
📚 رواق | تاريخ وتراث — محتوى يهدي ولا يُلهي.

#رواق #ياسر_الحزيمي #تاريخ_وتراث

## الوصف الجاهز (B)
{s['desc']}

نسخة B: ركّز على السؤال في أول سطر لزيادة التوقف عن التمرير، وأبقِ بقية الوصف ووسومه كما هي.

## الوسوم
{s['tags']}, رواق, تاريخ وتراث, ياسر الحزيمي, shorts, مقاطع قصيرة

## ثوابت النشر
- العنوان ≤ 100 حرف، والشورت الأفقي 9:16 — لا تفتح الشورت من رابط الحلقة الكاملة فقط.
- اربط الشورت بالحلقة الكاملة عبر «الفيديو ذي الصلة» في الاستوديو.
- 3 هاشتاقات كحد أقصى في العنوان/الوصف: `#رواق #ياسر_الحزيمي #shorts`.
"""


def build(s: dict) -> None:
    key = s["key"]
    d = f"{OUT}/{key}"
    os.makedirs(d, exist_ok=True)
    src = D.src(s)
    fa = grab(src, s["frames"][0], f"{WORK}/cov_{key}_a.png")
    fb = grab(src, s["frames"][1], f"{WORK}/cov_{key}_b.png")
    cover_short(Image.open(fa), s["lines_a"], s["kicker"], s["order"], f"{d}/COVER_A_1080x1920.jpg")
    cover_short(Image.open(fb), s["lines_b"], s["kicker"], s["order"], f"{d}/COVER_B_1080x1920.jpg")
    open(f"{d}/SEO_{key}.md", "w", encoding="utf-8").write(seo_md(s))
    print(f"[{key}] pack OK — غلافان + SEO")


if __name__ == "__main__":
    args = sys.argv[1:]
    for s in (D.SHORTS if not args else [D.by_key(k) for k in args]):
        build(s)
