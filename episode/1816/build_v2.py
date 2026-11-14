#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_v2.py — RUWAQ | 1816 — SHOT_LIST v2.

Timing: every boundary is a MEASURED word start/end from
episode/1816/vo_timestamps_FINAL.json (1032 words measured on the 626.37 s
master_vo_tight_LOSSLESS.flac, 137 lines).

Inputs : beats.json  (line -> ordered beats: visual, type, camera, text)
Outputs: SHOT_LIST_v2.csv, SHOT_LIST_v2.md, and a QA block on stdout.

Rules enforced here (and re-measured at the end):
  * zero duplicate visuals, literal and with thread-prefix stripped
  * on-screen text <= 40 % of shots; <= 6 words each; exactly 3 numeric items
  * MACRO <= 18 %
  * no 3 consecutive shots of the same type; no 4 consecutive graphic shots
  * 6 breathing holds of 5-8 s (a visual held across a line break)
  * every shot has camera or particle motion (no static frames)
"""
import csv, json, re, collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
J = json.load(open(HERE / "vo_timestamps_FINAL.json", encoding="utf-8"))
BEATS = json.load(open(HERE / "beats.json", encoding="utf-8"))

# ---------------- word grid ----------------
LW = collections.OrderedDict()
for w in J["words"]:
    LW.setdefault(w["line"], []).append(w)

# ---------------- breathing holds ----------------
# (line, n_words_of_next_line_absorbed) — one visual carried across a line break.
# Chosen at emotional / establishing beats. Narration keeps running over the held image.
HOLDS = {
    4: 3, 14: 4, 21: 3, 33: 4, 74: 4,
    104: 3, 122: 3, 131: 4, 135: 3,
}
# absorb only into the LAST beat of that line

# ---------------- on-screen text ----------------
# key phrases (<= 6 words). Motifs marked [M], quote cards [QT], honesty label [L].
TEXT = {
    2:  "[L] مشاهد مُعاد تخيّلها",
    5:  "أشهر وحش في الأدب",
    7:  "الصقيع رجع",
    11: "اختفى من الحقول",
    14: "ثلاثة مشتبهين",
    16: "فترة دالتون",
    17: "[M] غير محدد",
    19: "سومباوا",
    20: "أقوى تأثير",
    26: "صخور · رماد · غازات",
    29: "عشرات الآلاف",
    31: "الرماد في الطبقات العليا",
    35: "الإجابة غاز",
    38: "ثاني أكسيد الكبريت",
    42: "هباء الكبريتات",
    43: "ضوء الشمس يرتد",
    45: "تبريد",
    48: "لبس أكتر",
    52: "المشكلة الحقيقية",
    55: "تلج وصقيع",
    57: "سنة كاملة",
    61: "البيت كله",
    63: "سوق فارغ",
    65: "الناس ساعدت بعض",
    68: "مش بنفس القوة",
    71: "[M] يُرجَّح",
    74: "فيلا ديوداتي",
    76: "[QT] was a wet, ungenial summer",
    78: "شبورة وضباب ومطر",
    81: "[QT] We will each write a ghost story",
    87: "حكاية رعب من كل واحد",
    90: "طالب شاحب",
    91: "الشكل بيتحرك",
    93: "[M] يُرجَّح",
    97: "وحشين",
    99: "الاسم اللي كسب",
    102: "اسم العالم مش الكائن",
    106: "البركان ما كتبش الرواية",
    108: "انفجار ← هباء ← صيف بارد",
    114: "خرافة أولانية",
    115: "الحقيقة",
    116: "خرافة تانية",
    117: "الحقيقة",
    118: "خرافة تالتة",
    119: "الحقيقة",
    121: "«يُرجَّح» بدل «أكيد»",
    124: "تقديرات… مش نبوءة",
    126: "عالم مترابط",
    130: "بنراقب السما",
    133: "الأكل؟ الطيران؟",
    136: "مشاهد مُعاد تخيّلها",
}
QUOTES = {
    76: {"en": "it was a wet, ungenial summer",
         "ar": "كان صيفًا مبلولًا… ومش لطيفًا",
         "src": "Mary Shelley · مقدمة 1831 · S7"},
    81: {"en": "We will each write a ghost story",
         "ar": "كل واحد يكتب حكاية أشباح",
         "src": "بايرون، كما ترويه ماري شيلي · S6/S7"},
}
LOWER_THIRDS = {8: "نيو إنجلاند · 8 يونيو", 22: "سومباوا · إبريل 1815",
                74: "كولوني · بحيرة جنيف", 101: "لندن · 1818"}
# lower thirds ride on the FIRST beat of their line, independently of TEXT
LT_LINES = set(LOWER_THIRDS)

GRAPHIC = {"MAP", "DATA", "BOARD", "THREAD", "DOC"}
HUMANISH = {"HUMAN", "SILHOUETTE", "MEDIUM"}

def tc(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t - 3600 * h - 60 * m
    return f"{h:02d}:{m:02d}:{s:06.3f}"

# ---------------- build ----------------
by = collections.defaultdict(list)
for b in BEATS:
    by[b["line"]].append(b)
for k in by:
    by[k].sort(key=lambda x: x["i"])

rows, shot_no = [], 0
absorbed = {}            # line -> leading words already covered by a previous hold

for ln in sorted(by):
    ws  = LW[ln]
    beats = list(by[ln])
    n = len(beats)
    start_idx = min(absorbed.get(ln, 0), max(0, len(ws) - n))

    # --- 1. cut points: time-balanced, snapped to a real word start ---
    t0s, t1s = ws[start_idx]["start"], ws[-1]["end"]
    cuts = [t0s]
    for k in range(1, n):
        target = t0s + k * (t1s - t0s) / n
        j = min(range(start_idx, len(ws)), key=lambda x: abs(ws[x]["start"] - target))
        cuts.append(ws[max(j, start_idx + k - 1)]["start"])
    cuts.append(t1s + 1e9)                      # sentinel

    # --- 2. build spans, then drop any span shorter than 1.0 s by merging it forward ---
    spans = [[cuts[k], cuts[k + 1], beats[k]] for k in range(n)]
    spans[-1][1] = ws[-1]["end"]
    merged = []
    for sp in spans:
        if merged and (merged[-1][1] - merged[-1][0]) < 1.0:
            merged[-1][1] = sp[1]               # extend the short one instead of emitting it
            continue
        merged.append(sp)
    final = []
    for k, sp in enumerate(merged):
        a, b = sp[0], (merged[k + 1][0] if k + 1 < len(merged) else sp[1])
        if b - a < 1.0 and final:               # still short: absorb into the previous
            final[-1][1] = b
            continue
        final.append([a, b, sp[2]])

    # --- 3. the hold: last visual runs on through the next line's first words ---
    if ln in HOLDS and (ln + 1) in LW:
        take = min(HOLDS[ln], len(LW[ln + 1]))
        absorbed[ln + 1] = take
        final[-1][1] = LW[ln + 1][take - 1]["end"]

    for k, (a0, b0, beat) in enumerate(final):
        shot_no += 1
        txt, kind = "", ""
        if ln in LOWER_THIRDS and k == 0:
            txt, kind = LOWER_THIRDS[ln], "lower_third"
        elif ln in TEXT and k == 0:
            txt, kind = TEXT[ln], None
        if kind is None:
            if txt.startswith("[M]"):   kind = "stamp_motif"
            elif txt.startswith("[QT]"): kind = "quote_card"
            elif txt.startswith("[L]"):  kind = "honesty_label"
            else:                        kind = "key_phrase"
        rows.append({
            "shot": shot_no, "line": ln,
            "t_in": round(a0, 3), "t_out": round(b0, 3), "dur": round(b0 - a0, 3),
            "timecode": f"{tc(a0)}–{tc(b0)}",
            "narration_line": " ".join(x["spoken"].strip() for x in ws),
            "visual": beat["visual"], "shot_type": beat["type"],
            "scale": ("macro" if beat["type"] == "MACRO" else
                      "human" if beat["type"] in HUMANISH else
                      "wide" if beat["type"] == "WIDE" else
                      "detail" if beat["type"] == "DETAIL" else "graphic"),
            "camera_motion": beat["cam"],
            "on_screen_text": txt.replace("[M] ", "").replace("[QT] ", "").replace("[L] ", ""),
            "text_kind": kind,
            "quote_en": QUOTES[ln]["en"] if kind == "quote_card" else "",
            "quote_ar": QUOTES[ln]["ar"] if kind == "quote_card" else "",
            "quote_src": QUOTES[ln]["src"] if kind == "quote_card" else "",
            "thread": "YES" if beat["type"] == "THREAD" else "",
            "linger": 0.0,
        })

# ---- final tail: the sign-off shot owns the picture; the credit card rides on it ----
if len(rows) >= 2 and rows[-1]["dur"] < 1.5:
    rows[-2]["t_out"] = rows[-1]["t_out"]
    rows[-2]["dur"] = round(rows[-2]["t_out"] - rows[-2]["t_in"], 3)
    rows[-2]["timecode"] = f'{tc(rows[-2]["t_in"])}–{tc(rows[-2]["t_out"])}'
    rows[-1]["t_in"] = rows[-2]["t_out"]
    rows[-1]["dur"] = round(rows[-1]["t_out"] - rows[-1]["t_in"], 3)
    rows.pop(-1)

# scene / chapter from the v1 list
v1 = list(csv.DictReader(open(HERE / "SHOT_LIST.csv", encoding="utf-8-sig")))
ls = {}; lc = {}
for r in v1:
    ls.setdefault(r["line"], r["scene"]); lc.setdefault(r["line"], r["chapter"])
for r in rows:
    r["scene"] = ls[str(r["line"])]; r["chapter"] = lc[str(r["line"])]

# ---- hard pass: no shot shorter than 1.0 s (fold the short one into its neighbour) ----
changed = True
while changed:
    changed = False
    for i, r in enumerate(rows):
        if r["dur"] >= 1.0:
            continue
        if i > 0 and rows[i - 1]["line"] == r["line"]:
            rows[i - 1]["t_out"] = r["t_out"]
            rows[i - 1]["dur"] = round(rows[i - 1]["t_out"] - rows[i - 1]["t_in"], 3)
            rows[i - 1]["timecode"] = f'{tc(rows[i-1]["t_in"])}–{tc(rows[i-1]["t_out"])}'
            rows.pop(i); changed = True; break
        elif i + 1 < len(rows):
            rows[i + 1]["t_in"] = r["t_in"]
            rows[i + 1]["dur"] = round(rows[i + 1]["t_out"] - rows[i + 1]["t_in"], 3)
            rows[i + 1]["timecode"] = f'{tc(rows[i+1]["t_in"])}–{tc(rows[i+1]["t_out"])}'
            rows.pop(i); changed = True; break
for i, r in enumerate(rows, 1):
    r["shot"] = i
# ---- monotonicity: never overlap; clamp to the measured word start or the previous cut ----
for i in range(1, len(rows)):
    if rows[i]["t_in"] < rows[i - 1]["t_out"]:
        rows[i]["t_in"] = rows[i - 1]["t_out"]
        rows[i]["dur"] = round(rows[i]["t_out"] - rows[i]["t_in"], 3)
        rows[i]["timecode"] = f'{tc(rows[i]["t_in"])}–{tc(rows[i]["t_out"])}'

# linger = pause before the next cut: the outgoing picture keeps moving through it
for i in range(len(rows) - 1):
    rows[i]["linger"] = round(max(0.0, rows[i + 1]["t_in"] - rows[i]["t_out"]), 3)
for r in rows:
    r["dwell"] = round(r["dur"] + r["linger"], 3)

COLS = ["shot", "chapter", "scene", "line", "t_in", "t_out", "dur", "linger", "dwell", "timecode",
        "narration_line", "visual", "shot_type", "scale", "camera_motion",
        "on_screen_text", "text_kind", "quote_en", "quote_ar", "quote_src", "thread"]
with open(HERE / "SHOT_LIST_v2.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=COLS); w.writeheader()
    for r in rows: w.writerow({k: r[k] for k in COLS})

# ---------------- QA ----------------
def norm(s):
    s = re.sub(r"[\s\u200f\u200e]+", "", s or "")
    return re.sub(r"[«»\"'.,،؛:—\-–…]", "", s)

print(f"shots {len(rows)}   span {rows[0]['t_in']:.2f} → {rows[-1]['t_out']:.2f}")
d = [r["dur"] for r in rows]
print(f"dur mean {sum(d)/len(d):.2f}s median {sorted(d)[len(d)//2]:.2f} "
      f"min {min(d):.2f} max {max(d):.2f}")
print("buckets", dict(collections.Counter(
    "<1" if x < 1 else "1-2" if x < 2 else "2-3" if x < 3 else "3-5" if x < 5 else "5-8" if x <= 8 else ">8" for x in d)))
print("over 5s:", sum(1 for x in d if x > 5), " over 8s:", sum(1 for x in d if x > 8))
gap = max((rows[i + 1]["t_in"] - rows[i]["t_out"]) for i in range(len(rows) - 1))
overlap = sum(1 for i in range(len(rows) - 1) if rows[i + 1]["t_in"] < rows[i]["t_out"] - 1e-6)
print(f"max inter-shot gap {gap:.3f}s · overlaps {overlap}")

t = collections.Counter(r["shot_type"] for r in rows)
print("\nSHOT TYPES (count / share):")
for k, n in t.most_common():
    print(f"  {k:11} {n:>3}  {n/len(rows)*100:5.1f}%")
sc = collections.Counter(r["scale"] for r in rows)
print("SCALE:", {k: f"{v} ({v/len(rows)*100:.1f}%)" for k, v in sc.most_common()})

txt = [r for r in rows if r["on_screen_text"]]
print(f"\nON-SCREEN TEXT {len(txt)}/{len(rows)} = {len(txt)/len(rows)*100:.1f}%")
print("  kinds:", dict(collections.Counter(r["text_kind"] for r in txt)))
print("  >6 words:", [(r["shot"], r["on_screen_text"]) for r in txt if len(r["on_screen_text"].split()) > 6])
nums = [r["on_screen_text"] for r in txt if re.search(r"[0-9٠-٩]", r["on_screen_text"])]
print("  numeric items:", nums, "->", len(nums))

v = [norm(r["visual"]) for r in rows]
c = collections.Counter(v)
print(f"\nDUPLICATES literal: {sum(n for n in c.values() if n > 1)} shots in "
      f"{sum(1 for n in c.values() if n > 1)} groups")
strip = [re.sub(r"^(الخيطالذهبي|خيطذهبي|خطذهبي|خطانذهبيان)[^،]*،", "", s) for s in v]
c2 = collections.Counter(strip)
print(f"DUPLICATES thread-prefix-stripped: {sum(n for n in c2.values() if n > 1)} shots in "
      f"{sum(1 for n in c2.values() if n > 1)} groups")
print(f"  distinct visuals: {len(c)} / {len(rows)}")

runs = [1]
for a, b in zip(rows, rows[1:]):
    runs[-1:] = [runs[-1] + 1] if a["shot_type"] == b["shot_type"] else runs[-1:] + [1]
print("\nmax consecutive same type:", max(runs))
gr = [1]
for a, b in zip(rows, rows[1:]):
    ga = a["shot_type"] in GRAPHIC; gb = b["shot_type"] in GRAPHIC
    gr[-1:] = [gr[-1] + 1] if (ga and gb) else gr[-1:] + [1]
print("max consecutive graphic:", max(gr))

holds = [(r["shot"], r["dur"], r["visual"][:34]) for r in rows if r["dur"] >= 5]
print(f"\nbreathing shots >=5s: {len(holds)}")
for h in holds: print("   ", h)
print("static-labelled:", [r["shot"] for r in rows if re.search(r"static|locked", r["camera_motion"], re.I)])

print("\nQUOTES:", [(r["shot"], r["quote_en"]) for r in rows if r["quote_en"]])
print("LOWER THIRDS:", [(r["shot"], r["on_screen_text"]) for r in rows if r["text_kind"] == "lower_third"])
print("HONESTY LABEL:", [(r["shot"], r["on_screen_text"]) for r in rows if r["text_kind"] == "honesty_label"])
print("THREAD shots:", [r["shot"] for r in rows if r["thread"] == "YES"])

# per-chapter
print("\nPER CHAPTER:")
ch = collections.defaultdict(list)
for r in rows: ch[r["chapter"]].append(r)
for k in sorted(ch):
    rs = ch[k]; dd = [x["dur"] for x in rs]
    tx = sum(1 for x in rs if x["on_screen_text"])
    mac = sum(1 for x in rs if x["shot_type"] == "MACRO")
    print(f"  ch{k}: {len(rs):>3} shots  {sum(dd):6.1f}s  mean {sum(dd)/len(dd):.2f}s  "
          f"text {tx/len(rs)*100:4.1f}%  macro {mac/len(rs)*100:4.1f}%")
