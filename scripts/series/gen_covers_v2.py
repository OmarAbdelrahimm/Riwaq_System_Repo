"""مولّد أغلفة v2 لكل الحلقات: A/B أفقي (1280×720) + عمودي (1080×1920)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import covers as C  # noqa: E402
import covers_v2 as V  # noqa: E402

REPO = "/home/user/Riwaq_System_Repo"
DRIVE = f"{REPO}/google_drive"
OUT = f"{REPO}/outputs/SERIES_RIWAQ/covers_v2"

# key: (ملف الماستر, kicker, lines_a, lines_b, kicker_b, focus_a, focus_b)
EPISODES = {
    "01": ("الفيديو 01 — العلاقات أعمق من التواصل (ماستر).mp4", "بوصلة العلاقات",
           ["العلاقات أعمق", "من التواصل"], ["لا تكفي المهارات", "لتبني علاقة"],
           "مهارات لا تكفي", 0.5, 0.5),
    "02": ("الفيديو 02 — المقارنة أداة لا معيار (ماستر).mp4", "المقارنة وجلد الذات",
           ["المقارنة أداة", "لا معيار"], ["قارن… ولا تجلد", "ذاتك"],
           "أداة لا ميزان", 0.5, 0.5),
    "03": ("الفيديو 03 — النهايات في العلاقات (ماستر).mp4", "نهايات العلاقات",
           ["كل خروج", "هو دخول"], ["لا تنهِ علاقة", "قبل أن تعرف"],
           "لا تنهِ قبل أن تعرف", 0.5, 0.5),
    "04": ("الفيديو 04 — الشيطان يجري مجرى الدم (ماستر).mp4", "العدو الخفي",
           ["الشيطان في", "مجرى الدم"], ["لماذا يفرّق", "بين الزوجين؟"],
           "مجرى الدم", 0.5, 0.5),
    "05": ("الفيديو 05 — من يقود سيارتك؟ منظومة العلاقات (ماستر).mp4", "خريطة وسائق",
           ["من يقود", "سيارتك؟"], ["خريطة…", "وسائق… ووجهة"],
           "الوجهة أولًا", 0.5, 0.5),
    "06": ("الفيديو 06 — الرأي ليس الحقيقة النقد بلا جرح (ماستر).mp4", "رأي أم حقيقة",
           ["الرأي ليس", "الحقيقة"], ["«أنت لا تصلح", "لشيء»"],
           "لا تُكسر", 0.5, 0.5),
}

# لحظات اللقطة لكل حلقة (نفس لحظات الأغلفة المسلَّمة سابقًا)
FRAMES = {"01": (62, 150), "02": (20, 105), "03": (75, 45),
          "04": (95, 120), "05": (40, 191), "06": (60, 240)}

TOTAL = 6


def build(key: str) -> None:
    src, kicker, la, lb, kicker_b, fa, fb = EPISODES[key]
    master = f"{DRIVE}/{src}"
    d = f"{OUT}/{key}"
    os.makedirs(d, exist_ok=True)
    ta, tb = FRAMES[key]
    ia = V.grab(master, ta, f"/tmp/{key}_va.png")
    ib = V.grab(master, tb, f"/tmp/{key}_vb.png")
    badge = f"الحلقة {int(key)} من {TOTAL}"
    V.cover_h(ia, la, kicker, f"{d}/THUMB_A_1280x720.jpg", badge=badge, focus=fa)
    V.cover_h(ib, lb, kicker_b, f"{d}/THUMB_B_1280x720.jpg", badge=badge, focus=fb)
    V.cover_v(ia, la, kicker, f"{d}/COVER_1080x1920.jpg", focus=fa)
    print("OK", key, sorted(os.listdir(d)))


if __name__ == "__main__":
    keys = sys.argv[1:] or list(EPISODES)
    for k in keys:
        build(k)
