"""غلافا البث المباشر «رِواق مباشر» — نسختا A/B (1280×720).

نفس لغة أغلفة v2: صورة كاملة بلا تدرّج داكن، والنص بظل ديناميكي متعدّد الطبقات.
الجديد: شارة بث مباشر بنقطة حمراء نابضة + سطر موضوع أسفل العنوان.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import covers_v2 as V  # noqa: E402
import graphics as G  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

REPO = "/home/user/Riwaq_System_Repo"
OUT = f"{REPO}/outputs/SERIES_RIWAQ/LIVE"
SRC = f"{REPO}/google_drive/الفيديو 01 — العلاقات أعمق من التواصل (ماستر).mp4"
LIVE_RED = (214, 62, 54)

SAFE_BOTTOM = 566
SAFE_TOP = 190


def live_pill(d, x, y, ss, label="بث مباشر", px=26):
    """كبسولة شفافة بنقطة حمراء + كلمة «بث مباشر»."""
    fb = G.font(G.PLEX_B, px * ss)
    tw = G.text_w(fb, G.ar(label)) / ss
    pad_l, gap = 20, 13
    dot_r = 7
    w = pad_l + dot_r * 2 + gap + tw + 18
    h = 42
    d.rounded_rectangle([x * ss, y * ss, (x + w) * ss, (y + h) * ss],
                        radius=(h / 2) * ss, fill=(14, 12, 9, 200),
                        outline=(196, 90, 78, 230), width=max(2, 2 * ss))
    cx = x + pad_l + dot_r
    d.ellipse([(cx - dot_r) * ss, (y + h / 2 - dot_r) * ss,
               (cx + dot_r) * ss, (y + h / 2 + dot_r) * ss], fill=LIVE_RED + (255,))
    G.draw_ar(d, ((cx + dot_r + gap) * ss, (y + h / 2) * ss), label, fb,
              (245, 236, 224, 255), anchor="lm")
    return w


def build(frame_t: float, lines: list[str], sub: str, out: str,
          focus: float = 0.5, live="بث مباشر") -> str:
    W, H = 1280, 720
    frame = V.grab(SRC, frame_t, f"/tmp/live_{int(frame_t)}.png")
    base = V._vignette(V.fill_frame(frame, W, H, focus), 0.15).convert("RGBA")

    # ------- الشعار
    lock = G.brand_lockup(112, color=G.PARCH)
    logo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    logo.alpha_composite(lock, (56, 34))
    V.add_shadowed(base, logo, wide=(18, 0.92, (8, 12)), tight=(5, 0.88, (2, 4)),
                   glow=(16, 0.18, G.GOLD_L))

    # شارة «بث مباشر» أعلى اليمين (عربي RTL: يمين الكادر)
    from PIL import Image as _I
    badge_layer = _I.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge_layer)
    ss_b = 2
    tmp = _I.new("RGBA", (W * ss_b, H * ss_b), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    bw = live_pill(td, 0, 0, ss_b, live)
    tmp = tmp.crop((0, 0, int((bw + 4) * ss_b), 46 * ss_b)).resize(
        (int(bw + 4), 46), _I.LANCZOS)
    badge_layer.alpha_composite(tmp, (W - 56 - int(bw) - 4, 40))
    V.add_shadowed(base, badge_layer, wide=(14, 0.95, (0, 6)), tight=(4, 0.9, (0, 2)),
                   glow=(12, 0.16, LIVE_RED))

    # ------- الكتلة النصية: عنوان كبير + سطر موضوع + اسم
    kick_px, name_px, row_h, sub_px = 30, 30, 46, 27
    fixed = 30 + 40 + 30 + 26 + row_h
    avail = SAFE_BOTTOM - SAFE_TOP - fixed
    fitted, total, px = [], 0, 92
    while px > 44:
        fitted, total = [], 0
        for line in lines:
            fnt = G.fit_font(G.AMIRI_B, line, 600, px, 44)
            fitted.append((line, fnt))
            total += int(fnt.size * 1.28)
        if total <= avail:
            break
        px -= 2
    y0 = SAFE_BOTTOM - (fixed + total)
    y_title = y0 + 30
    y_sub = y_title + total + 40
    y_row = y_sub + 40 + 30
    x0 = 66

    def painter(d: ImageDraw.ImageDraw, ss: int) -> None:
        y = y_title
        for line, fnt in fitted:
            V.draw_ar_stroke(d, (x0 * ss, y * ss), line, G.font(G.AMIRI_B, fnt.size * ss),
                             G.PARCH + (255,), stroke=2 * ss)
            y += int(fnt.size * 1.28)
        fs = G.fit_font(G.PLEX_M, sub, 560, sub_px, 20)
        V.draw_ar_stroke(d, (x0 * ss, y_sub * ss), sub, G.font(G.PLEX_M, fs.size * ss),
                         G.GOLD_L + (255,), stroke=1 * ss)
        cy = y_row + row_h / 2
        fn = G.font(G.PLEX_M, name_px * ss)
        nm_w = G.text_w(fn, G.ar("د. ياسر الحزيمي")) / ss
        V.draw_ar_stroke(d, (x0 * ss, (cy + 3) * ss), "د. ياسر الحزيمي", fn,
                         (234, 224, 204, 255), stroke=1 * ss, anchor="ls")
        fb = G.font(G.PLEX_B, 25 * ss)
        bx = x0 + nm_w + 26
        label = "رِواق مباشر"
        bw2 = G.text_w(fb, G.ar(label)) / ss + 32
        d.rounded_rectangle([bx * ss, (cy - 22) * ss, (bx + bw2) * ss, (cy + 22) * ss],
                            radius=21 * ss, fill=(16, 14, 10, 198),
                            outline=G.GOLD_L + (232,), width=max(2, 2 * ss))
        G.draw_ar(d, ((bx + 16) * ss, cy * ss), label, fb, G.PARCH + (255,), anchor="lm")

    V.add_shadowed(base, V.text_layer((W, H), painter),
                   wide=(34, 1.0, (9, 12)), tight=(6, 1.0, (2, 3)),
                   glow=(13, 0.11, G.GOLD), core=(22, 1.0, (0, 4)),
                   extra=[(92, 0.50, (0, 10)), (64, 0.62, (0, 7))])

    d = ImageDraw.Draw(base)
    d.rectangle([16, 16, W - 17, H - 17], outline=G.GOLD_L + (225,), width=2)
    d.rectangle([24, 24, W - 25, H - 25], outline=(122, 100, 55, 95), width=1)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    base.convert("RGB").save(out, quality=93, subsampling=1)
    return out


if __name__ == "__main__":
    build(38, ["كيف تعيش", "بوعي؟"],
          "النهايات · المقارنة · النجاح الحقيقي", f"{OUT}/LIVE_A_1280x720.jpg")
    build(205, ["النجاح", "الحقيقي"],
          "النهايات · المقارنة · النجاح الحقيقي", f"{OUT}/LIVE_B_1280x720.jpg",
          focus=0.52)
    print("OK")
