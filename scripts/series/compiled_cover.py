"""غلافا الحلقة المجمّعة (A/B) — 1280×720 بنفس لغة أغلفة v2.

صورة كاملة بلا تدرّج داكن + ظل ديناميكي متعدّد الطبقات + شارة مدة الحلقة.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import covers_v2 as V  # noqa: E402
import graphics as G  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

REPO = "/home/user/Riwaq_System_Repo"
OUT = f"{REPO}/outputs/SERIES_RIWAQ/COMPILED"
SRC = f"{REPO}/google_drive/الفيديو 01 — العلاقات أعمق من التواصل (ماستر).mp4"
SRC6 = f"{REPO}/google_drive/الفيديو 06 — الرأي ليس الحقيقة النقد بلا جرح (ماستر).mp4"

SAFE_BOTTOM = 566
SAFE_TOP = 190


def chip(d, x, y, ss, text, px=25, accent=None):
    """كبسولة معلومات (مدة/عدد الحلقات) بنفس لغة الشارة الذهبية."""
    fb = G.font(G.PLEX_B, px * ss)
    tw = G.text_w(fb, G.ar(text)) / ss
    w, h = tw + 34, 42
    d.rounded_rectangle([x * ss, y * ss, (x + w) * ss, (y + h) * ss],
                        radius=(h / 2) * ss, fill=(15, 13, 9, 200),
                        outline=(accent or G.GOLD_L) + (232,), width=max(2, 2 * ss))
    G.draw_ar(d, ((x + 17) * ss, (y + h / 2) * ss), text, fb, G.PARCH + (255,), anchor="lm")
    return w


def build(frame_t: float, lines: list[str], kicker: str, sub: str, out: str,
          duration="26:42", focus: float = 0.5, src: str | None = None) -> str:
    W, H = 1280, 720
    frame = V.grab(src or SRC, frame_t, f"/tmp/cmp_{abs(hash((src, frame_t))) % 10**8}.png")
    base = V._vignette(V.fill_frame(frame, W, H, focus), 0.15).convert("RGBA")

    # ------- الشعار
    lock = G.brand_lockup(112, color=G.PARCH)
    logo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    logo.alpha_composite(lock, (56, 34))
    V.add_shadowed(base, logo, wide=(18, 0.92, (8, 12)), tight=(5, 0.88, (2, 4)),
                   glow=(16, 0.18, G.GOLD_L))

    # ------- شارة المدة أعلى اليمين
    chip_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ss_b = 2
    tmp = Image.new("RGBA", (W * ss_b, 120 * ss_b), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    cw = chip(td, 0, 0, ss_b, duration)
    tmp = tmp.crop((0, 0, int((cw + 4) * ss_b), 46 * ss_b)).resize((int(cw + 4), 46), Image.LANCZOS)
    chip_layer.alpha_composite(tmp, (W - 56 - int(cw) - 4, 40))
    V.add_shadowed(base, chip_layer, wide=(14, 0.95, (0, 6)), tight=(4, 0.9, (0, 2)),
                   glow=(12, 0.14, G.GOLD_L))

    # ------- الكتلة النصية
    kick_px, sub_px, name_px, row_h = 30, 27, 30, 46
    gap_k = 52
    fixed = gap_k + 44 + 34 + 26 + row_h
    avail = SAFE_BOTTOM - SAFE_TOP - fixed
    fitted, total, px = [], 0, 92
    while px > 44:
        fitted, total = [], 0
        for line in lines:
            fnt = G.fit_font(G.AMIRI_B, line, 560, px, 42)
            fitted.append((line, fnt))
            total += int(fnt.size * 1.28)
        if total <= avail:
            break
        px -= 2
    y0 = SAFE_BOTTOM - (fixed + total)
    y_kick = y0
    y_title = y_kick + gap_k
    y_sub = y_title + total + 30
    y_row = y_sub + 44 + 26
    x0 = 66

    def painter(d: ImageDraw.ImageDraw, ss: int) -> None:
        V.draw_ar_stroke(d, (x0 * ss, y_kick * ss), kicker, G.font(G.PLEX_B, kick_px * ss),
                         G.GOLD_L + (255,), stroke=1 * ss)
        y = y_title
        for line, fnt in fitted:
            V.draw_ar_stroke(d, (x0 * ss, y * ss), line, G.font(G.AMIRI_B, fnt.size * ss),
                             G.PARCH + (255,), stroke=2 * ss)
            y += int(fnt.size * 1.28)
        fs = G.fit_font(G.PLEX_M, sub, 560, sub_px, 20)
        V.draw_ar_stroke(d, (x0 * ss, y_sub * ss), sub, G.font(G.PLEX_M, fs.size * ss),
                         (214, 204, 182, 255), stroke=1 * ss)
        cy = y_row + row_h / 2
        fn = G.font(G.PLEX_M, name_px * ss)
        nm_w = G.text_w(fn, G.ar("د. ياسر الحزيمي")) / ss
        V.draw_ar_stroke(d, (x0 * ss, (cy + 3) * ss), "د. ياسر الحزيمي", fn,
                         (234, 224, 204, 255), stroke=1 * ss, anchor="ls")
        fb = G.font(G.PLEX_B, 25 * ss)
        label = "رِواق"
        bw2 = G.text_w(fb, G.ar(label)) / ss + 32
        bx = x0 + nm_w + 26
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
    # A — العنوان الرئيسي (الفكرة): العلاقة التي تُصلح كل العلاقات
    build(60, ["العلاقة التي", "تُصلح كل العلاقات"], "بودكاست بدون ورق",
          "مع الله، ومع النفس، ومع الناس",
          f"{OUT}/COMPILED_A_1280x720.jpg", focus=0.46)
    # B — الزاوية الثانية: علاقاتك كلها تبدأ من علاقتك بالله
    build(95, ["علاقاتك كلها تبدأ", "من علاقتك بالله"], "رحلة في منظومة العلاقات",
          "من الفرد… إلى الأسرة… إلى العالم",
          f"{OUT}/COMPILED_B_1280x720.jpg", focus=0.52, src=SRC6)
    print("OK")
