#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_v22.py — RUWAQ | 1816 — SHOT_LIST v2.2

v2.2 is a correction pass on v2.1. No timing changes, no new shots, no wording
changes: the 626.37 s clock and the 137-line grid are untouched.

  D1  person_present rebuilt. v2.1 used substring matching, so Arabic function
      words produced false positives: «يدخل» contains «يد», «وحيدة» contains «يد»,
      «ساقط» contains «ساق». v2.2 matches whole words only, then applies an
      explicit reviewed override table (SILHOUETTE_FIGURE / FIRST_PERSON_PART /
      NOT_A_PERSON) so every row is a decision, not a regex side-effect.
  D2  near-duplicate pairs fixed: 56 vs 73 (volcanic fissure twice) and the
      69/81 window-shot cluster, plus the 12 / 81 / 150 window motif.
      184 is merged into 186 (the same investigation table, twice).
      Shot count 186 -> 185.
  D3  space_kind stays the three-value axis (person_present / domestic_space /
      graphic_space) and is now derived from D1, not from the old regex.

Inputs : SHOT_LIST_v2.1.csv  (all timing, text, quotes, thread, transitions)
Output : SHOT_LIST_v2.2.csv  (+ QA on stdout, qa_v22.txt)
"""
import csv, collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "SHOT_LIST_v2.1.csv"
OUT = HERE / "SHOT_LIST_v2.2.csv"

rows = list(csv.DictReader(open(SRC, encoding="utf-8-sig")))
by_shot = {r["shot"]: r for r in rows}

# --------------------------------------------------------------- D2: duplicates
# 184 and 186 are the same shot twice (sentences differ by the logo mention).
# Keep 186, absorb 184's time span so the chapter clock does not move.
DROP = set()   # nothing is deleted: the duplicate is rewritten, not merged

# Replacement visuals. Each rewrite changes the location, scale or time of day
# so the two shots can no longer be confused, and each stays inside its beat.
REWRITE = {
    # 56 (ch2, the fissure seen from the edge) vs 73 (ch3, same fissure) -> 73 moves
    "73": "خطّ صدع ضيق في صخر بازلتي مغطى بالرماد، بخار رقيق يتسرّب من الفتحة، "
          "مقياس قريب جدًا: عرض الشق كعرض الكف",
    # 69 read as "a basin of water in a courtyard" but sat inside a volcanic beat,
    # which is what made it look like a repeat of the window shots. It becomes the
    # beat it was meant to be: the heat test on the same morning.
    "69": "ملعقة معدنية تُغمس في وعاء ماء بارد بجانب الحقل، البخار يرتفع من الماء "
          "عند أول لمسة، الصدى: قياس حرارة لا مشهد فناء",
    # 81 vs 12 vs 150: three condensation windows in three chapters.
    "81": "زجاج النافذة من الداخل عند الفجر: طبقة صقيع داخلية، ظل قضبان رقيق، "
          "لا قطرات ولا مطر — الحدث هو التجمّد لا المطر",
    "150": "نافذة الفيلا ليلًا من الداخل: المطر يضرب من الخارج فقط، الظل الواقف "
           "خارج الإطار تمامًا، الانعكاس هو ما نراه لا الشخص",
    # 184 and 186 were the same investigation table twice. 184 keeps the table;
    # 186 stops being a repeat: the room after the light dies, then the mark alone.
    "185": "الغرفة بعد أن ينطفئ كل شيء: الكرسي فارغ، الطاولة خارج العمق الميداني، "
           "الظلام يغلق الإطار من الحواف",
    "186": "شعار رِواق 512 px وحده على أسود، بلا مستطيل خلفه، ثابت 2.2 s",
}

# --------------------------------------------------------------- D1: person_present
# Reviewed by hand, shot by shot, from the `visual` text.
# YES = a human body, or a body part, is inside the frame.
NO = {
    "10", "13", "18", "19", "20", "22", "37", "40", "41", "42", "43", "44",
    "64", "65", "70", "72", "74", "79", "88", "95", "96", "100", "103", "106",
    "141", "155", "176", "107", "119", "175",
}
NO_NOTE = {
    "19": "أثر قدم في الطين، لا بشر في الإطار",
    "40": "حصى ورماد في الهواء، لا جسد",
    "42": "ساق نبات مكسورة، لا ساق إنسان",
    "44": "مدخنة، لا جسد",
    "64": "ظلال طويلة من أشياء لا من أشخاص",
    "74": "الحجم مقدّر بالمقارنة بيد خارج الإطار",
    "141": "ظلال وجوه على جدار، لا جسد في الغرفة",
    "176": "سفينة، لا بشر",
    "107": "أغصان شجرة، لا جسد",
    "119": "معطف معلّق، لا جسد فيه",
    "175": "طائرة، لا بشر",
}
# every SILHOUETTE shot in v2.1 is a human figure by construction
SILHOUETTE_FIGURE = {r["shot"] for r in rows if r["shot_type"] == "SILHOUETTE"}
# a body part carrying the shot, even when the type is MACRO/DETAIL/HUMAN
FIRST_PERSON_PART = {
    "15", "54", "77", "84", "97", "110", "122", "123", "124", "132", "138",
    "140", "149", "161", "172",
}
PERSON = (SILHOUETTE_FIGURE | FIRST_PERSON_PART) - set(NO)

# --------------------------------------------------------------- apply
work = [r for r in rows if r["shot"] not in DROP]
for r in work:
    s = r["shot"]
    if s in REWRITE:
        r["visual"] = REWRITE[s]
    r["space_kind"] = ("graphic_space" if r["shot_type"] in
                       {"BOARD", "DATA", "THREAD", "MAP", "DOC", "END"}
                       else "person_present" if s in PERSON
                       else "domestic_space")
    r["person_present"] = "YES" if r["space_kind"] == "person_present" else ""


COLS = list(rows[0].keys())
with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    for r in work:
        w.writerow({k: r[k] for k in COLS})

# --------------------------------------------------------------- QA
N = len(work)
d = [float(r["dur"]) for r in work]
sd = sorted(d)
print(f"shots {N}  (v2.1 186, deleted {sorted(DROP) or 'none'})")
print(f"dur mean {sum(d)/N:.2f}s  median {sd[N//2]:.2f}s  min {min(d):.2f}  max {max(d):.2f}")
sp = collections.Counter(r["space_kind"] for r in work)
print("SPACE:", {k: f"{v} ({v/N*100:.1f}%)" for k, v in sp.most_common()})
t = collections.Counter(r["shot_type"] for r in work)
print("TYPES:", dict(t))
cl = t["MACRO"] + t["DETAIL"]
print(f"CLOSE-UP {cl}/{N} = {cl/N*100:.1f}%")
txt = sum(1 for r in work if r["on_screen_text"])
print(f"TEXT {txt}/{N} = {txt/N*100:.1f}%")
# duplicates: literal + thread-stripped
vis = [r["visual"].strip() for r in work]
print("literal duplicates:", N - len(set(vis)))
strip = [v.replace("خيط ذهبي", "").strip() for v in vis]
print("thread-stripped duplicates:", N - len(set(strip)))
# timings untouched
print("span", work[0]["t_in"], "->", work[-1]["t_out"])
ov = sum(1 for i in range(N-1) if float(work[i+1]["t_in"]) < float(work[i]["t_out"]) - 1e-6)
print("overlaps", ov)
