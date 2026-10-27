"""أغلفة الحلقات الستة (أفقي 1280×720) بنظام الأغلفة المعتمد — A و B لكل حلقة.

    python3 scripts/publish/episodes_covers.py [01 02 ...]

المخرجات: outputs/PUBLISH_PACK_SERIES_COVERS/ — أسماء إنجليزية من naming.py
النظام: docs/COVER_SYSTEM.md
  • إطار: خطوط أفقية خارجية متلاشية + رأسية داخلية أرفع + خط التوقيع (frame_v3)
  • عزل: البطل مضيء، الأطراف تهدأ، بلا ضباب على الوجه (isolate)
  • شارة النص: خمس طبقات عمق (badge3d)
  • الترقيم: شارة صغيرة في زاوية الإطار (corner_number)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import Image, ImageDraw

import cover_system as CS
import graphics as G
import naming

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "outputs" / "PUBLISH_PACK_SERIES_COVERS"
ASSETS = REPO / "public" / "projects" / "TAWASUL_001" / "assets"
PORTRAIT = ASSETS / "sheikh_tawasul.jpg"      # 1152×864 — يد مرفوعة
PORTRAIT2 = ASSETS / "sheikh_f38.jpg"         # 1152×864 — نظرة هادئة

W, H = 1280, 720
X_RIGHT = 520
MAX_W = 448
TOP = 214
BOTTOM = 690

# رقم الحلقة، slug إنجليزي، ونصوص A/B
EPISODES = {
    "01": dict(
        slug="relationships-deeper-than-communication",
        a=dict(h1="العلاقة", h2="أعمق من الكلام",
               badge="مهارات التواصل لا تصنع علاقة",
               bridge="الفرق الذي يغيّر كل شيء",
               src=PORTRAIT, fx=0.55, fy=0.22, zoom=1.18),
        b=dict(h1="الفرق", h2="بين الكلام والعلاقة",
               badge="أغلب خناقاتنا سببها الخلط",
               bridge="لوحة مشتركة بين طرفين",
               src=PORTRAIT2, fx=0.52, fy=0.26, zoom=1.14),
    ),
    "02": dict(
        slug="comparison-is-a-tool-not-a-standard",
        a=dict(h1="المقارنة", h2="أداة لا معيار",
               badge="قارن… ولا تجلد ذاتك",
               bridge="الفرق بين الميزان والمرآة",
               src=PORTRAIT, fx=0.58, fy=0.24, zoom=1.14),
        b=dict(h1="الصاعدة", h2="أم الهابطة؟",
               badge="واحدة ترفعك… وأخرى تكسرك",
               bridge="أنواع المقارنة الأربعة",
               src=PORTRAIT2, fx=0.50, fy=0.22, zoom=1.12),
    ),
    "03": dict(
        slug="endings-in-relationships",
        a=dict(h1="النهايات", h2="موت أم بداية؟",
               badge="كل خروج هو دخول",
               bridge="لا تنهِ قبل أن تعرف إلى أين تدخل",
               src=PORTRAIT2, fx=0.56, fy=0.24, zoom=1.16),
        b=dict(h1="قبل أن تنهي", h2="إلى أين تدخل؟",
               badge="لا تخرج قبل أن تعرف الباب",
               bridge="كل نهاية تفتح بابًا لم تحدّد",
               src=PORTRAIT, fx=0.50, fy=0.20, zoom=1.12),
    ),
    "04": dict(
        slug="shaytan-runs-through-the-blood",
        a=dict(h1="الشيطان", h2="يجري مجرى الدم",
               badge="عدو تسكنه في علاقاتك",
               bridge="لماذا يفرح بتفريقك عن أهلك؟",
               src=PORTRAIT, fx=0.46, fy=0.20, zoom=1.20),
        b=dict(h1="العدو", h2="الذي لا تراه",
               badge="يفرّق بينك وبين أقرب الناس",
               bridge="أخطر معصية: تفريق القلوب",
               src=PORTRAIT2, fx=0.58, fy=0.26, zoom=1.18),
    ),
    "05": dict(
        slug="who-drives-your-car",
        a=dict(h1="من يقود", h2="سيارتك؟",
               badge="خمسة مقاعد في منظومة العلاقات",
               bridge="الوجهة والخريطة والسائق",
               src=PORTRAIT, fx=0.60, fy=0.26, zoom=1.16),
        b=dict(h1="الوجهة", h2="والخريطة والسائق",
               badge="لماذا تهت في الطريق؟",
               bridge="منظومة العلاقات في خمسة مقاعد",
               src=PORTRAIT2, fx=0.48, fy=0.22, zoom=1.14),
    ),
    "06": dict(
        slug="opinion-is-not-the-truth",
        a=dict(h1="الرأي", h2="ليس الحقيقة",
               badge="أنقد ولا تجرح… واقبل ولا تُكسر",
               bridge="كيف تفرّق بين الرأي والحكم؟",
               src=PORTRAIT2, fx=0.54, fy=0.24, zoom=1.16),
        b=dict(h1="«أنت لا تصلح", h2="لشيء»",
               badge="حين يصبح كلام الناس حكمًا",
               bridge="قصة الطحاوي وخاله",
               src=PORTRAIT, fx=0.48, fy=0.20, zoom=1.18),
    ),
}

PLANS = [(1.00, 1.00, (12, 22, 26)), (0.96, 1.00, (11, 20, 24)),
         (0.92, 0.97, (10, 18, 22)), (0.88, 0.94, (9, 16, 20)),
         (0.82, 0.90, (8, 14, 18)), (0.76, 0.86, (6, 12, 16))]


def plan(h1, h2, badge, bridge, name):
    for k, kb, (g1, g2, g3) in PLANS:
        f_h1 = CS.fit_width(h1, "sans_b", MAX_W, int(CS.LADDER.h1 * k), 40)
        f_h2 = CS.fit_width(h2, "display", MAX_W, int(CS.LADDER.h2 * k), 36)
        f_bd = CS.fit_width(badge, "sans_b", MAX_W - 54, int(CS.LADDER.badge * kb), 20)
        f_br = CS.fit_width(bridge, "sans_r", MAX_W, int(CS.LADDER.bridge * kb), 15)
        f_nm = CS.font("sans_m", CS.LADDER.name)
        h1h = CS.ink_size(h1, f_h1)[1]
        h2h = CS.ink_size(h2, f_h2)[1]
        bdh = f_bd.size + 28
        brh = CS.ink_size(bridge, f_br)[1]
        nmh = CS.ink_size(name, f_nm)[1]
        total = h1h + g1 + h2h + g2 + CS.LADDER.rule_h + g3 + bdh + 22 + brh + 22 + nmh
        if TOP + total <= BOTTOM:
            return f_h1, f_h2, f_bd, f_br, f_nm, (g1, g2, g3)
    raise RuntimeError("لا يوجد تدرّج يدخل المساحة")


def build(spec: dict, num: str, variant: str, corner: str | None = None) -> Image.Image:
    im = CS.cover_crop(str(spec["src"]), W, H, fx=spec["fx"], fy=spec["fy"], zoom=spec["zoom"])
    im = CS.isolate(im, strength=0.60)

    h1, h2, badge, bridge = spec["h1"], spec["h2"], spec["badge"], spec["bridge"]
    name = "ياسر الحزيمي"
    f_h1, f_h2, f_bd, f_br, f_nm, (g1, g2, g3) = plan(h1, h2, badge, bridge, name)

    bd_w = CS.ink_size(badge, f_bd)[0] + 54
    bd_h = f_bd.size + 28

    def painter(d):
        y = TOP
        y = CS.draw_ink(im, h1, f_h1, X_RIGHT, y, CS.COLORS["white"] + (255,), d)
        y += g1
        y = CS.draw_ink(im, h2, f_h2, X_RIGHT, y, CS.COLORS["champagne"] + (255,), d)
        y += g2
        rule_y = y
        y += CS.LADDER.rule_h + g3
        badge_cy = y + bd_h // 2
        y += bd_h + 22
        y = CS.draw_ink(im, bridge, f_br, X_RIGHT, y, (250, 247, 238, 248), d)
        y += 22
        y = CS.draw_ink(im, name, f_nm, X_RIGHT, y, CS.COLORS["white"] + (238,), d)
        assert y <= BOTTOM, f"الكتلة تجاوزت {BOTTOM}: {y}"
        return rule_y

    probe = Image.new("RGBA", im.size, (0, 0, 0, 0))
    rule_y = painter(ImageDraw.Draw(probe))
    CS.text_shadow(im, lambda d: painter(d), blur=11,
                   offsets=((0, 4), (0, 11), (0, 20)), alpha=230)
    CS.rule(im, (X_RIGHT, rule_y), length=336)
    CS.badge3d(im, badge, (X_RIGHT - bd_w // 2,
                           rule_y + CS.LADDER.rule_h + g3 + bd_h // 2), px=f_bd.size)
    CS.corner_number(im, corner or f"{num} من 6", corner="tr")
    CS.lockup(im, 84, (44, 26))
    CS.frame_v3(im)
    return im


def main(only: list[str] | None = None) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for num, ep in EPISODES.items():
        if only and num not in only:
            continue
        for tag in ("A", "B"):
            im = build(ep[tag.lower()], num, tag)
            stem = naming.cover_name(num, "CVR-H", "", variant=tag, v=2, en=ep["slug"])
            jpg, png = naming.save_cover(im, stem, OUT)
            CS.qc_thumb(Image.open(jpg), str(OUT / naming.name(
                num, "QC", "", variant=tag, v=2, ext="png", en="thumb-168px")))
            print(f"{num}{tag} -> {jpg.name} {jpg.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main(sys.argv[1:] or None)
