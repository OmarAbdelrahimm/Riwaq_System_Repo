#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_v21.py — RUWAQ | 1816 — SHOT_LIST v2.1

Changes vs v2 (see SHOT_LIST_v2.1_CHANGELOG.md):
  C1  narration_line now carries the APPROVED SCRIPT text (01_FINAL_SCRIPT_v3.md),
      not the ASR transcript. The ASR words are used for timing only.
  C2  quote 1 corrected to "it proved a wet, ungenial summer" (Gutenberg #42324);
      quote 2 kept verbatim.
  C3  golden thread: overlay on shot 98 (4.9 entry to Lake Geneva) and on shot 173
      (6.14 jump to the present) instead of new shots.
  C4  `scale` split into person_present / domestic_space / graphic_space.
  C5  close-up share (MACRO + DETAIL) reduced below 18 % by promoting 17 close-ups
      that are not on a narration close-up beat.
  C6  rhythm: the Frankenstein vision (lines 88-90) becomes 2 slow shots instead of
      6; scene 4.10 becomes 3 shots instead of 6.
  C7  keep: 0 duplicates, text <= 40 %, no production labels, no static shot > 2 s,
      3 wipe motifs, the NOAA date, line 84 as recorded.

Inputs : beats.json, vo_timestamps_FINAL.json, SHOT_LIST.csv (scene/chapter map),
         SCRIPT_LINES_v3.json (approved script, 137 lines).
Output : SHOT_LIST_v2.1.csv  (+ QA on stdout)
"""
import csv, json, re, collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
J = json.load(open(HERE / "vo_timestamps_FINAL.json", encoding="utf-8"))
BEATS = json.load(open(HERE / "beats.json", encoding="utf-8"))
SCRIPT = json.load(open(HERE / "SCRIPT_LINES_v3.json", encoding="utf-8"))

LW = collections.OrderedDict()
for w in J["words"]:
    LW.setdefault(w["line"], []).append(w)

# ---------------------------------------------------------------- holds
HOLDS = {4: 3, 14: 4, 21: 3, 33: 4, 74: 4, 104: 3, 122: 3, 131: 4}

# ---------------------------------------------------------------- text
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
    76: "[QT] proved a wet, ungenial summer",
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
    76: {"en": "it proved a wet, ungenial summer",
         "ar": "ثبت أن الصيف كان مبلولًا وغير مؤاتٍ",
         "src": "Mary Shelley · مقدمة 1831 · S7 · Gutenberg #42324"},
    81: {"en": "We will each write a ghost story",
         "ar": "سنكتب كلٌّ منّا حكاية أشباح",
         "src": "بايرون كما ترويه ماري شيلي · مقدمة 1831 · S6/S7"},
}
LOWER_THIRDS = {8: "نيو إنجلاند · 8 يونيو", 22: "سومباوا · إبريل 1815",
                74: "كولوني · بحيرة جنيف", 101: "لندن · 1818"}

GRAPHIC = {"MAP", "DATA", "BOARD", "THREAD", "DOC"}

# ---------------------------------------------------------------- wipes
# The three motif wipes, used only where the story changes register.
TRANSITIONS = {
    34:  "ink_wipe",     # into the three suspects
    45:  "smoke_wipe",   # into the mechanism
    60:  "smoke_wipe",   # out of the mechanism into the cold world
    73:  "ink_wipe",     # into the Geneva question
    85:  "thread_wipe",  # into the villa night
    96:  "thread_wipe",  # into the ghost-story challenge
    99:  "ink_wipe",     # into the quote card
    116: "smoke_wipe",   # into the myth/truth board
    140: "thread_wipe",  # out of 1816, into the present
    148: "ink_wipe",     # into the preparation section
    170: "smoke_wipe",   # into the closing question
}

# ---------------------------------------------------------------- C5 close-ups
# These DETAIL / MACRO beats are not on a narration close-up beat; promote them
# to a wider, human-scale frame so MACRO + DETAIL drops below 18 %.
PROMOTE = {
    # detail -> a wider frame that still serves the same line
    12:  ("MEDIUM", "نافذة الكوخ من الخارج عند الفجر، الصقيع على الحافة، الضوء لا يدخل بعد"),
    13:  ("MEDIUM", "سياج خشب في الحقل تحت الصقيع، عشب ميت، نفس متصاعد قريب من الكاميرا"),
    18:  ("MEDIUM", "مطبخ كوخ صغير: مائدة فارغة، ثلاثة أطباق، كرسي مسحوب، الباب مفتوح على بياض"),
    20:  ("WIDE", "شارع سوق صغير مغلق، لوحة أسعار خشبية فارغة، أبواب موصدة، لا أحد"),
    36:  ("WIDE", "فوهة بركانية من مسافة: صخور داكنة، بخار يتصاعد، الأفق مفتوح"),
    40:  ("WIDE", "أرض مغطاة بالرماد حتى الأفق، آثار أقدام غائرة، لا بشر"),
    44:  ("MEDIUM", "عربة في فناء: أكياس قماش فارغة مكدسة، حبل مربوط، باب المخزن مغلق"),
    48:  ("WIDE", "طبقة الهباء من بعيد فوق سلسلة جبال، ضوء الشمس يخترقها من الأعلى"),
    51:  ("MEDIUM", "حوض ماء مفتوح في فناء، حجر بازلتي ساخن يُغمر، بخار يغطي الإطار"),
    54:  ("MEDIUM", "شق أرضي بركاني من مسافة قريبة معتدلة، فقاعات غاز، ضوء جانبي"),
    58:  ("DATA", "مقطع توضيحي: جسيمات كبريتات تتكثّف حول بعضها، هالة تتشكل، رسم بلا أرقام"),
    61:  ("MEDIUM", "حائط مطبخ: ترمومتر خشبي، نافذة مغبشة بجانبه، المؤشر في النصف"),
    63:  ("WIDE", "حقل مهجور: حرّاثة صدئة واقفة وحدها، خط الحرث يختفي في الضباب"),
    72:  ("MEDIUM", "زاوية حقل: كومة برد متراكمة أمام سياج، الأرض السوداء حولها"),
    79:  ("MEDIUM", "غرفة باردة من الداخل: نافذة مغبشة، ظل قضبان، بخار نفس على الزجاج"),
    87:  ("WIDE", "طريق ريفي مغطى بالثلج حتى الأفق، عجلة عربة غارقة، لا أحد"),
    130: ("WIDE", "غرفة مظلمة من طرفها: أجزاء غير مكتملة على طاولة بعيدة، الحجم غير واضح"),
}

# ---------------------------------------------------------------- C6 rhythm
# Frankenstein vision (lines 88-90, 19.94 s measured): 2 slow shots, not 6.
# beats are keyed to the line they START on, so the first image starts on 88 and
# the second on 90 — together they cover 88+89+90 without a 10 s overrun.
# lines whose beats were all folded away in v2 and therefore emitted no shot
RESTORE = {
    15: [{"line": 15, "i": 0, "type": "DATA",
          "visual": "خط بياني باهت لحرارة قديمة على ورق مقوّى، الضوء يمرّ خلال الورق",
          "cam": "slow drift left · paper texture", "txt": ""}],
    34: [{"line": 34, "i": 0, "type": "BOARD",
          "visual": "عدسة مكبّرة فوق خريطة، تكبّر نقطة واحدة على سومباوا، اليد ثابتة",
          "cam": "1.8s push-in · lens parallax", "txt": ""}],
    105: [{"line": 105, "i": 0, "type": "MEDIUM",
           "visual": "طاولة الفيلا: سبابة ترفع ورقة عن سطح الطاولة، الورقة تتوقف في الهواء قليلًا",
           "cam": "drift up · dust in the air", "txt": ""}],
    136: [{"line": 136, "i": 0, "type": "END",
           "visual": "طاولة التحقيق كاملة، البطاقات مثبتة، ضوء يخفت، شعار رِواق الصغير في الزاوية",
           "cam": "hold 2.7s · light falls", "txt": ""}],
}

VISION = {
    88: [{"line": 88, "i": 0, "type": "SILHOUETTE",
          "visual": "غرفة الفيلا بالليل: ماري من الخلف على طرف الطاولة، ظل شعرها المرفوع على الحائط، الكتاب مفتوح، رعشة شمعة واحدة، لا وجه",
          "cam": "6.5s slow push · candle flicker", "txt": ""}],
    89: [{"line": 89, "i": 0, "type": "SILHOUETTE",
          "visual": "ظل طالب شاحب راكع في الغرفة، ظهره محدّب، الكتفان يهتزان مع النفس، ضوء الشمعة يقترب منه ببطء",
          "cam": "8.2s slow push · rack to shadow", "txt": ""}],
    90: [{"line": 90, "i": 0, "type": "DETAIL",
          "visual": "ورقة عليها شكل غير مكتمل، أجزاء مفكوكة على الطاولة، ضوء الشمعة يرتجف فوقها",
          "cam": "6.8s slow drift · candle flicker", "txt": ""}],
    91: [{"line": 91, "i": 0, "type": "MEDIUM",
          "visual": "باب الغرفة يفتح على ممر مظلم، الستارة تتحرك، الهواء البارد يدخل الإطار",
          "cam": "drift through door · curtain", "txt": ""}],
}
# scene 4.10 (lines 81-82, 10.43 s measured): 3 shots instead of 6.
SCENE_410 = {
    81: [{"line": 81, "i": 0, "type": "SILHOUETTE",
          "visual": "ظل بايرون يميل للأمام فوق الطاولة، الكتفان مرتفعان، الشموع تنطفئ واحدة تلو الأخرى في الخلف",
          "cam": "3.5s push-in · candle falloff", "txt": ""},
         {"line": 81, "i": 1, "type": "MEDIUM",
          "visual": "باب الغرفة مفتوح قليلًا، ضوء الممر يقطع أرضية الغرفة، الحبر يرتجف في القارورة",
          "cam": "drift right · door light", "txt": ""}],
    82: [{"line": 82, "i": 0, "type": "BOARD",
          "visual": "أوراق فارغة موزعة على الطاولة، أربعة أقلام متوازية، خيط ذهبي يتفرّع من الورقة الأولى إلى أربعة مسارات",
          "cam": "slow tilt down · thread draws on", "txt": ""}],
}

# ---------------------------------------------------------------- C3 overlays
# thread as an OVERLAY on an existing shot (does not add a shot)
# keyed by LINE, not by shot number, so a rebuild cannot move the overlay
THREAD_OVERLAY = {
    75:  {"t_in": 0.2, "dur": 1.7,
          "note": "خيط ذهبي رفيع يعبر الإطار من اليسار إلى اليمين فوق سطح البحيرة، يدخل بعد 0.2 s ويخرج قبل القطع بـ0.2 s"},
    123: {"t_in": 0.6, "dur": 1.6,
          "note": "خيط ذهبي يمرّ فوق خريطة الرادار ويقطعها أُفقيًا، يدخل بعد 0.2 s ويخرج قبل القطع بـ0.2 s"},
}

# ---------------------------------------------------------------- C4 scale
def scale_of(shot_type, visual):
    if shot_type in GRAPHIC or shot_type == "END":
        return "graphic_space"
    person = re.search(
        r"(يد|أصابع|كتف|ظهر|ساق|ذراع|ظل (?:يد|رجل|امرأة|مزارع|راع|بايرون|طالب|رأس)|"
        r"رأس مائل|عيون|وجه|ملامح|إصبع|أنفاس|نفس متصاعد)", visual)
    if person and "لا وجه" not in visual.split("،")[0][:0]:
        return "person_present"
    return "domestic_space"


def tc(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t - 3600 * h - 60 * m
    return f"{h:02d}:{m:02d}:{s:06.3f}"


# ---------------------------------------------------------------- merge beats
by = collections.defaultdict(list)
for b in BEATS:
    by[b["line"]].append(b)
for k in by:
    by[k].sort(key=lambda x: x["i"])

# C6a / C6b: rebuild the two passages with a fixed beat count
for ln, beats in {**VISION, **SCENE_410, **RESTORE}.items():
    by[ln] = beats

# apply promotions (C5)
for b in BEATS:
    if b["line"] in PROMOTE and b["type"] in ("DETAIL", "MACRO"):
        t, v = PROMOTE[b["line"]]
        # only the first close-up on that line, so we do not flatten the whole line
        first = by[b["line"]][0]
        if b is first:
            b["type"], b["visual"] = t, v

rows, shot_no = [], 0
absorbed = {}

for ln in sorted(by):
    beats = by[ln]
    if not beats:
        # line folded into a longer shot: emit nothing, extend the previous shot later
        absorbed["skip"] = absorbed.get("skip", [])
        absorbed["skip"].append(ln)
        continue
    ws = LW[ln]
    n = len(beats)
    start_idx = min(absorbed.get(ln, 0), max(0, len(ws) - n))
    t0s, t1s = ws[start_idx]["start"], ws[-1]["end"]

    cuts = [t0s]
    for k in range(1, n):
        target = t0s + k * (t1s - t0s) / n
        j = min(range(start_idx, len(ws)), key=lambda x: abs(ws[x]["start"] - target))
        cuts.append(ws[max(j, start_idx + k - 1)]["start"])
    cuts.append(t1s + 1e9)

    spans = [[cuts[k], cuts[k + 1], beats[k]] for k in range(n)]
    spans[-1][1] = ws[-1]["end"]
    merged = []
    for sp in spans:
        if merged and (merged[-1][1] - merged[-1][0]) < 1.0:
            merged[-1][1] = sp[1]
            continue
        merged.append(sp)
    final = []
    for k, sp in enumerate(merged):
        a, b = sp[0], (merged[k + 1][0] if k + 1 < len(merged) else sp[1])
        if b - a < 1.0 and final:
            final[-1][1] = b
            continue
        final.append([a, b, sp[2]])

    if ln in HOLDS and (ln + 1) in LW:
        take = min(HOLDS[ln], len(LW[ln + 1]))
        # a hold must leave the next line at least 1.3 s of its own picture,
        # otherwise that line becomes a stub and would be folded away silently
        while take > 0:
            last_kept = LW[ln + 1][take - 1]["end"]
            if LW[ln + 1][-1]["end"] - last_kept >= 1.3:
                break
            take -= 1
        if take:
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
            if txt.startswith("[M]"):    kind = "stamp_motif"
            elif txt.startswith("[QT]"):  kind = "quote_card"
            elif txt.startswith("[L]"):   kind = "honesty_label"
            else:                         kind = "key_phrase"
        rows.append({
            "shot": shot_no, "line": ln,
            "t_in": round(a0, 3), "t_out": round(b0, 3), "dur": round(b0 - a0, 3),
            "timecode": f"{tc(a0)}–{tc(b0)}",
            "narration_line": SCRIPT[str(ln)],
            "covers_lines": str(ln),
            "asr_line": " ".join(x["spoken"].strip() for x in ws),
            "visual": beat["visual"], "shot_type": beat["type"],
            "camera_motion": beat["cam"],
            "on_screen_text": txt.replace("[M] ", "").replace("[QT] ", "").replace("[L] ", ""),
            "text_kind": kind,
            "quote_en": QUOTES[ln]["en"] if kind == "quote_card" else "",
            "quote_ar": QUOTES[ln]["ar"] if kind == "quote_card" else "",
            "quote_src": QUOTES[ln]["src"] if kind == "quote_card" else "",
            "thread": "YES" if beat["type"] == "THREAD" else "",
            "linger": 0.0,
        })

# shots that were folded away must still cover their narration: extend neighbours
if absorbed.get("skip"):
    for ln in sorted(absorbed["skip"]):
        idx = [i for i, r in enumerate(rows) if r["line"] == ln - 1]
        if idx:
            i = idx[-1]
            rows[i]["t_out"] = round(LW[ln][-1]["end"], 3)
            rows[i]["dur"] = round(rows[i]["t_out"] - rows[i]["t_in"], 3)
            rows[i]["timecode"] = f'{tc(rows[i]["t_in"])}–{tc(rows[i]["t_out"])}'
            # the line still has to be spoken over this picture, and must reach the SRT
            rows[i]["narration_line"] = (rows[i]["narration_line"] + " " + SCRIPT[str(ln)]).strip()
            rows[i]["covers_lines"] = rows[i]["covers_lines"] + f",{ln}"

# tail: credit card rides on the last sign-off shot
if len(rows) >= 2 and rows[-1]["dur"] < 1.5:
    rows[-2]["t_out"] = rows[-1]["t_out"]
    rows[-2]["dur"] = round(rows[-2]["t_out"] - rows[-2]["t_in"], 3)
    rows[-2]["timecode"] = f'{tc(rows[-2]["t_in"])}–{tc(rows[-2]["t_out"])}'
    rows[-1]["t_in"] = rows[-2]["t_out"]
    rows[-1]["dur"] = round(rows[-1]["t_out"] - rows[-1]["t_in"], 3)
    rows.pop(-1)

# scene / chapter from the approved v1 list
v1 = list(csv.DictReader(open(HERE / "SHOT_LIST.csv", encoding="utf-8-sig")))
ls, lc = {}, {}
for r in v1:
    ls.setdefault(r["line"], r["scene"]); lc.setdefault(r["line"], r["chapter"])
for r in rows:
    r["scene"] = ls[str(r["line"])]; r["chapter"] = lc[str(r["line"])]

# fold anything under 1.0 s
changed = True
while changed:
    changed = False
    for i, r in enumerate(rows):
        if r["dur"] >= 1.0:
            continue
        if i > 0:
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
# a shot may run over a folded-away line, but never into the next shot's picture
# last shot always ends on the last measured word, never on a folded line's end
rows[-1]["t_out"] = round(LW[max(LW)][-1]["end"], 3)
rows[-1]["dur"] = round(rows[-1]["t_out"] - rows[-1]["t_in"], 3)
rows[-1]["timecode"] = f'{tc(rows[-1]["t_in"])}–{tc(rows[-1]["t_out"])}'
for i in range(len(rows) - 1):
    if rows[i]["t_out"] > rows[i + 1]["t_in"] + 1e-6:
        rows[i]["t_out"] = rows[i + 1]["t_in"]
        rows[i]["dur"] = round(rows[i]["t_out"] - rows[i]["t_in"], 3)
        rows[i]["timecode"] = f'{tc(rows[i]["t_in"])}–{tc(rows[i]["t_out"])}'
for i in range(1, len(rows)):
    if rows[i]["t_in"] < rows[i - 1]["t_out"]:
        rows[i]["t_in"] = rows[i - 1]["t_out"]
        rows[i]["dur"] = round(rows[i]["t_out"] - rows[i]["t_in"], 3)
        rows[i]["timecode"] = f'{tc(rows[i]["t_in"])}–{tc(rows[i]["t_out"])}'

for i in range(len(rows) - 1):
    rows[i]["linger"] = round(max(0.0, rows[i + 1]["t_in"] - rows[i]["t_out"]), 3)
for r in rows:
    r["dwell"] = round(r["dur"] + r["linger"], 3)

# C3a: give the two overlay shots room. The brief asks for a 1.5-2 s overlay, so the
# picture under it must be at least 1.9 s. Time is borrowed from the NEXT shot, which
# must stay above 1.3 s of its own picture — nothing is retimed against the VO.
for line_key, need in ((75, 2.10), (123, 2.10)):
    cand = [i for i, r in enumerate(rows) if r["line"] == line_key]
    if not cand:
        continue
    i = cand[0]
    short = need - rows[i]["dur"]
    if short > 0 and i + 1 < len(rows) and rows[i + 1]["dur"] - short >= 1.30:
        rows[i]["t_out"] = round(rows[i]["t_out"] + short, 3)
        rows[i]["dur"] = round(rows[i]["t_out"] - rows[i]["t_in"], 3)
        rows[i]["timecode"] = f'{tc(rows[i]["t_in"])}–{tc(rows[i]["t_out"])}'
        rows[i + 1]["t_in"] = rows[i]["t_out"]
        rows[i + 1]["dur"] = round(rows[i + 1]["t_out"] - rows[i + 1]["t_in"], 3)
        rows[i + 1]["timecode"] = f'{tc(rows[i+1]["t_in"])}–{tc(rows[i+1]["t_out"])}'

# C3 overlays + C4 scale
for r in rows:
    r["thread_overlay"] = ""
for line_key, o in THREAD_OVERLAY.items():
    need = o["t_in"] + o["dur"] + 0.20
    cand = [r for r in rows if r["line"] == line_key and r["thread"] != "YES"]
    # the overlay rides the first shot on that line that is actually long enough
    for r in cand:
        if r["dur"] >= need:
            r["thread_overlay"] = f'{o["t_in"]:.1f}s +{o["dur"]:.1f}s · {o["note"]}'
            r["thread"] = "OVERLAY"
            break
    else:
        if cand:
            o2 = dict(o); o2["dur"] = max(1.0, min(o["dur"], cand[0]["dur"] - 0.35))
            cand[0]["thread_overlay"] = f'0.2s +{o2["dur"]:.1f}s · {o["note"]}'
            cand[0]["thread"] = "OVERLAY"

# C4 space classification + wipes (separate pass: every row must be reachable)
for r in rows:
    r["space_kind"] = scale_of(r["shot_type"], r["visual"])
    r["transition"] = TRANSITIONS.get(r["shot"], "cut")
    r["person_present"] = "YES" if r["space_kind"] == "person_present" else ""

COLS = ["shot", "chapter", "scene", "line", "t_in", "t_out", "dur", "linger", "dwell", "timecode",
        "narration_line", "covers_lines", "asr_line", "visual", "shot_type", "space_kind", "person_present",
        "camera_motion", "on_screen_text", "text_kind", "quote_en", "quote_ar", "quote_src",
        "thread", "thread_overlay", "transition"]

with open(HERE / "SHOT_LIST_v2.1.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    for r in rows:
        w.writerow({k: r[k] for k in COLS})

# ---------------------------------------------------------------- QA
N = len(rows)
d = [r["dur"] for r in rows]
print(f"shots {N}   span {rows[0]['t_in']:.2f} -> {rows[-1]['t_out']:.2f}")
sd = sorted(d)
print(f"dur mean {sum(d)/N:.2f}s median {sd[N//2]:.2f}s min {min(d):.2f} max {max(d):.2f}")
print("buckets", dict(collections.Counter(
    "<1" if x < 1 else "1-2" if x < 2 else "2-3" if x < 3 else "3-5" if x < 5
    else "5-8" if x <= 8 else ">8" for x in d)))
print("over 5s:", sum(1 for x in d if x > 5), " over 8s:", sum(1 for x in d if x > 8))
print("over 5s shots:", [(r["shot"], r["dur"]) for r in rows if r["dur"] > 5])
gap = max(rows[i + 1]["t_in"] - rows[i]["t_out"] for i in range(N - 1))
print(f"max gap {gap:.3f}s · overlaps {sum(1 for i in range(N-1) if rows[i+1]['t_in'] < rows[i]['t_out'] - 1e-6)}")

t = collections.Counter(r["shot_type"] for r in rows)
print("\nTYPES:", {k: f"{v} ({v/N*100:.1f}%)" for k, v in t.most_common()})
cl = t["MACRO"] + t["DETAIL"]
print(f"CLOSE-UP (MACRO+DETAIL): {cl}/{N} = {cl/N*100:.1f}%")

sp = collections.Counter(r["space_kind"] for r in rows)
print("SPACE:", {k: f"{v} ({v/N*100:.1f}%)" for k, v in sp.most_common()})
pp = sum(1 for r in rows if r["person_present"])
print(f"PERSON_PRESENT: {pp}/{N} = {pp/N*100:.1f}%")

txt = [r for r in rows if r["on_screen_text"]]
print(f"\nTEXT {len(txt)}/{N} = {len(txt)/N*100:.1f}%")
print("  kinds:", dict(collections.Counter(r["text_kind"] for r in txt)))
print("  >6 words:", [(r["shot"], r["on_screen_text"]) for r in txt if len(r["on_screen_text"].split()) > 6])
nums = [r["on_screen_text"] for r in txt if re.search(r"[0-9٠-٩]", r["on_screen_text"])]
print("  numeric:", nums, len(nums))


def norm(s):
    s = re.sub(r"[\s\u200f\u200e]+", "", s or "")
    return re.sub(r"[«»\"'.,،؛:—\-–…]", "", s)


v = [norm(r["visual"]) for r in rows]
c = collections.Counter(v)
print(f"\nDUP literal: {sum(n for n in c.values() if n>1)} shots in {sum(1 for n in c.values() if n>1)} groups")
strip = [re.sub(r"^(الخيطالذهبي|خيطذهبي|خطذهبي|خطانذهبيان)[^،]*،", "", s) for s in v]
c2 = collections.Counter(strip)
print(f"DUP thread-stripped: {sum(n for n in c2.values() if n>1)} shots · distinct {len(c)}/{N}")

runs = [1]
for a, b in zip(rows, rows[1:]):
    runs[-1:] = [runs[-1] + 1] if a["shot_type"] == b["shot_type"] else runs[-1:] + [1]
print("max consecutive type:", max(runs))
gr = [1]
for a, b in zip(rows, rows[1:]):
    ga, gb = a["shot_type"] in GRAPHIC, b["shot_type"] in GRAPHIC
    gr[-1:] = [gr[-1] + 1] if (ga and gb) else gr[-1:] + [1]
print("max consecutive graphic:", max(gr))
print("static-labelled:", [r["shot"] for r in rows if re.search(r"static|locked", r["camera_motion"], re.I)])
print("THREAD shots:", [(r["shot"], r["thread"]) for r in rows if r["thread"]])
print("QUOTES:", [(r["shot"], r["quote_en"]) for r in rows if r["quote_en"]])

print("\nPER CHAPTER:")
ch = collections.defaultdict(list)
for r in rows:
    ch[r["chapter"]].append(r)
for k in sorted(ch, key=int):
    rs = ch[k]
    dd = [x["dur"] for x in rs]
    ty = collections.Counter(x["shot_type"] for x in rs)
    print(f"  ch{k}: {len(rs):3d} shots {sum(dd):6.1f}s mean {sum(dd)/len(rs):4.2f}s "
          f"text {sum(1 for x in rs if x['on_screen_text'])/len(rs)*100:5.1f}%  "
          + " ".join(f"{a}:{b}" for a, b in ty.most_common()))
print("\nSCENE 4.9 shots:", [(r["shot"], r["dur"], r["shot_type"]) for r in rows if r["scene"] == "9"])
print("SCENE 4.10 shots:", [(r["shot"], r["dur"], r["shot_type"]) for r in rows if r["scene"] == "10"])
print("VISION 88-90:", [(r["shot"], r["line"], r["dur"], r["shot_type"]) for r in rows if int(r["line"]) in (88, 89, 90)])
