"""أغلفة الحلقة 02 — «المقارنة أداة لا معيار» — أول تطبيق لنظام الأغلفة v1.

    python3 scripts/publish/ep02_cover.py

التخطيط **من أعلى لأسفل بقياسات حبر حقيقية** (CS.draw_ink): كل سطر يبدأ حيث
انتهى الحبر السابق، فلا يمكن أن يتصادم سطران ولا أن يُدفن نص تحت الشارة.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import Image, ImageDraw

import cover_system as CS
import naming

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "outputs" / "PUBLISH_PACK_EP02_COVERS"
ASSETS = REPO / "public" / "projects" / "TAWASUL_001" / "assets"

SRC_A = ASSETS / "sheikh_tawasul.jpg"    # يد مرفوعة — طاقة وبيان
SRC_B = ASSETS / "sheikh_f38.jpg"        # نظرة هادئة حاسمة — سؤال

W, H = 1280, 720
X_RIGHT = 520                 # حافة عمود النص (مقيسة من الغلاف المرجعي)
MAX_W = 448                   # أقصى عرض للعناصر
TOP = 214                     # بداية كتلة النص
BOTTOM = 664                  # آخر سطر مسموح (خط التوقيع تحته)


PLANS = [   # (معامل H1/H2, معامل الشارة/الجسر, الفواصل: H1→H2, H2→مسطرة, مسطرة→شارة)
    (1.00, 1.00, (12, 22, 26)),
    (0.96, 1.00, (11, 20, 24)),
    (0.92, 0.97, (10, 18, 22)),
    (0.88, 0.94, (9, 16, 20)),
    (0.82, 0.90, (8, 14, 18)),
]


def plan(h1, h2, badge, bridge, name):
    """يختار أكبر تدرّج يدخل المساحة — قياسات حبر حقيقية لا تقديرات."""
    for k, kb, (g1, g2, g3) in PLANS:
        f_h1 = CS.fit_width(h1, "sans_b", MAX_W, int(CS.LADDER.h1 * k), 40)
        f_h2 = CS.fit_width(h2, "display", MAX_W, int(CS.LADDER.h2 * k), 36)
        f_bd = CS.fit_width(badge, "sans_b", MAX_W - 44, int(CS.LADDER.badge * kb), 20)
        f_br = CS.fit_width(bridge, "sans_r", MAX_W, int(CS.LADDER.bridge * kb), 15)
        f_nm = CS.font("sans_m", CS.LADDER.name)

        h1h = CS.ink_size(h1, f_h1)[1]
        h2h = CS.ink_size(h2, f_h2)[1]
        bdh = f_bd.size + 22
        brh = CS.ink_size(bridge, f_br)[1]
        nmh = CS.ink_size(name, f_nm)[1]
        total = (h1h + g1 + h2h + g2 + CS.LADDER.rule_h + g3 + bdh
                 + 22 + brh + 22 + nmh)
        if TOP + total <= BOTTOM:
            return f_h1, f_h2, f_bd, f_br, f_nm, (g1, g2, g3)
    raise RuntimeError("لا يوجد تدرّج يدخل المساحة — راجع TOP/BOTTOM")


def build(im, pill_txt, h1, h2, badge, bridge, name, rule_len=336):
    f_h1, f_h2, f_bd, f_br, f_nm, (g1, g2, g3) = plan(h1, h2, badge, bridge, name)

    for label, txt, f, lim in (("H1", h1, f_h1, MAX_W), ("H2", h2, f_h2, MAX_W),
                               ("badge", badge, f_bd, MAX_W - 44),
                               ("bridge", bridge, f_br, MAX_W)):
        w = CS.ink_size(txt, f)[0]
        assert w <= lim, f"{label} أعرض من العمود: {w} > {lim}"

    bd_w = CS.ink_size(badge, f_bd)[0] + 44
    bd_h = f_bd.size + 22

    def painter(d):
        y = TOP
        y = CS.draw_ink(im, h1, f_h1, X_RIGHT, y, CS.COLORS["white"] + (255,), d)
        y += g1
        y = CS.draw_ink(im, h2, f_h2, X_RIGHT, y, CS.COLORS["champagne"] + (255,), d)
        y += g2
        yield_rule = y
        y += CS.LADDER.rule_h + g3
        badge_cy = y + bd_h // 2
        y += bd_h + 22
        y = CS.draw_ink(im, bridge, f_br, X_RIGHT, y, (250, 247, 238, 248), d)
        y += 22
        y = CS.draw_ink(im, name, f_nm, X_RIGHT, y, CS.COLORS["white"] + (238,), d)
        assert y <= BOTTOM + 2, f"الكتلة تجاوزت {BOTTOM}: {y}"
        return yield_rule

    probe = Image.new("RGBA", im.size, (0, 0, 0, 0))
    rule_y = painter(ImageDraw.Draw(probe))

    CS.text_shadow(im, lambda d: painter(d), blur=11,
                   offsets=((0, 4), (0, 11), (0, 20)), alpha=228)
    CS.rule(im, (X_RIGHT, rule_y), length=min(rule_len, MAX_W))
    CS.badge3d(im, badge, (X_RIGHT - bd_w // 2,
                           rule_y + CS.LADDER.rule_h + g3 + bd_h // 2), px=f_bd.size)
    CS.pill(im, pill_txt, (0, 118), px=19, right=X_RIGHT)
    CS.lockup(im, 92, (40, 26))
    CS.frame_classic(im)      # الإطار القديم المعتمد + خط التوقيع
    return im


def cover_a() -> Image.Image:
    im = CS.cover_crop(str(SRC_A), W, H, fx=0.56, fy=0.24, zoom=1.14)
    im = CS.grade(im, brightness=1.03, contrast=1.10, color=0.93)
    im = CS.shade_away_from_face(im, "left", 205, (0.40, 0.04, 0.84, 0.68))
    return build(im,
                 pill_txt="الحلقة 2 من 6 · تطوير الذات",
                 h1="المقارنة",
                 h2="أداة لا معيار",
                 badge="قارن… ولا تجلد ذاتك",
                 bridge="الفرق بين الميزان والمرآة",
                 name="ياسر الحزيمي")


def cover_b() -> Image.Image:
    im = CS.cover_crop(str(SRC_B), W, H, fx=0.50, fy=0.22, zoom=1.12)
    im = CS.grade(im, brightness=1.02, contrast=1.12, color=0.92)
    im = CS.shade_away_from_face(im, "left", 212, (0.34, 0.02, 0.82, 0.70))
    return build(im,
                 pill_txt="الحلقة 2 من 6 · تطوير الذات",
                 h1="الصاعدة",
                 h2="أم الهابطة؟",
                 badge="واحدة ترفعك… وأخرى تكسرك",
                 bridge="أنواع المقارنة الأربعة",
                 name="ياسر الحزيمي",
                 rule_len=300)


EN = {   # اسم إنجليزي مقصود لكل نسخة (لا ترجمة آلية في أسماء التسليم)
    "A": "comparison-is-a-tool-not-a-standard",
    "B": "upward-or-downward-comparison",
}


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for old in list(OUT.glob("*.jpg")) + list(OUT.glob("*.png")):
        old.unlink()                      # مجلد التسليم يحتوي النسخة الحالية فقط
    for tag, im, note in (("A", cover_a(), "بيان"), ("B", cover_b(), "سؤال")):
        stem = naming.cover_name("02", "CVR-H", "المقارنة أداة لا معيار",
                                 variant=tag, v=1, en=EN[tag])
        jpg, png = naming.save_cover(im, stem, OUT)
        print(f"{tag} ({note}) -> {jpg.name} · {jpg.stat().st_size // 1024} KB")
        CS.qc_thumb(Image.open(jpg), str(OUT / naming.name("02", "QC", "", variant=tag, v=1,
                                                          ext="png", en="thumb-168px")))
    print("done")
