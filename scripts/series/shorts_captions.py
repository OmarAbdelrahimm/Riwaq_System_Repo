"""كابشن الشورتس: تنظيف بطاقات الإيجنت الآخر (تكرارات roll-up) + إنتاج AR/EN/ثنائي."""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))

import srtlib as S  # noqa: E402

WORK = "/home/user/Riwaq_System_Repo/google_drive/work"
FIXDIR = "/home/user/Riwaq_System_Repo/scripts/series/shorts_fix"


def norm_ar(s: str) -> str:
    """مفتاح مقارنة: بلا تشكيل ولا علامات ولا مسافات زائدة."""
    s = re.sub(r"[\u064B-\u0652\u0670\u0640]", "", s)
    s = re.sub(r"[^\w\u0600-\u06FF]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def clean_ar(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip(" -،.")
    words = [S.SAFE_FIXES.get(w, w) for w in s.split(" ")]
    s = " ".join(w for w in words if w)
    return s


def clean_en(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip().strip('"').strip()
    if s and s[-1] not in ".!?…":
        s += "."
    return s[0].upper() + s[1:] if s else s


def merge(cues) -> list[dict]:
    """يدمج البطاقات المتتالية المتطابقة نصًا (أثر نظام roll-up) في بطاقة واحدة."""
    out: list[dict] = []
    for c in cues:
        k = norm_ar(c.ar)
        if not k:
            continue
        if out and norm_ar(out[-1]["raw"]) == k:
            out[-1]["end"] = c.end
            if len(c.en) > len(out[-1]["en_raw"]):
                out[-1]["en_raw"] = c.en
            continue
        out.append({"start": c.start, "end": c.end, "raw": c.ar,
                    "en_raw": c.en, "cue": c.idx})
    rows = []
    for i, r in enumerate(out, 1):
        ar = clean_ar(r["raw"])
        if not ar:
            continue
        rows.append({"i": i, "start": round(r["start"], 3), "end": round(r["end"], 3),
                     "ar": ar, "en": clean_en(r["en_raw"]), "src_cue": r["cue"]})
    # إزالة التعارضات الزمنية (قصّ النهاية عند بداية التالي)
    for a, b in zip(rows, rows[1:]):
        if a["end"] > b["start"] - 0.02:
            a["end"] = round(max(a["start"] + 0.6, b["start"] - 0.04), 3)
    return rows


def load(key: str) -> list[dict]:
    rows = merge(S.parse_srt(f"{WORK}/srt_short_{key}.srt"))
    fixes = {}
    p = f"{FIXDIR}/{key}.json"
    if os.path.exists(p):
        fixes = json.load(open(p, encoding="utf-8"))
    for r in rows:
        f = fixes.get(str(r["i"]))
        if f:
            r["ar"] = f.get("ar", r["ar"])
            r["en"] = f.get("en", r["en"])
    return rows


def _srt(rows: list[dict], path: str, bilingual: bool = False, en_only: bool = False) -> None:
    blocks = []
    for i, r in enumerate(rows, 1):
        body = r["en"] if en_only else (f"{r['ar']}\n{r['en']}" if bilingual else r["ar"])
        blocks.append(f"{i}\n{S.srt_time(r['start'])} --> {S.srt_time(r['end'])}\n{body}\n")
    open(path, "w", encoding="utf-8").write("\n".join(blocks))


def write_srts(rows: list[dict], out_dir: str) -> None:
    _srt(rows, f"{out_dir}/CAPTIONS_AR.srt")
    _srt(rows, f"{out_dir}/CAPTIONS_EN.srt", en_only=True)
    _srt(rows, f"{out_dir}/CAPTIONS_AR_EN.srt", bilingual=True)


if __name__ == "__main__":
    import shorts_data as D
    for s in D.SHORTS:
        rows = merge(S.parse_srt(D.srt_path(s)))
        print(f"\n===== {s['key']}  (orig {s['orig']})  {len(rows)} بطاقة")
        for r in rows:
            print(f"{r['i']:>2} {r['start']:6.2f}-{r['end']:6.2f} | {r['ar']}")
            print(f"                        | {r['en']}")


# ------------------------------------------------------------------ ASS (كابشن رأسي)
ASS_HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,IBM Plex Sans Arabic,54,&H00DBEBF3,&H0069A4C2,&H0012100E,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,5,70,70,0,1
"""


def with_words(rows: list[dict]) -> list[dict]:
    """يوزّع زمن كل بطاقة على كلماتها بحسب طول الكلمة (توقيت كاريوكي تقريبي)."""
    for r in rows:
        ws = r["ar"].split()
        weights = [len(w) + 1.5 for w in ws]
        total = sum(weights)
        t = r["start"]
        span = max(0.4, r["end"] - r["start"])
        out = []
        for w, k in zip(ws, weights):
            d = span * k / total
            out.append({"text": w, "start": t, "end": t + d})
            t += d
        r["words"] = out
    return rows


def build_ass(rows: list[dict], path: str, y: int = 1404, max_w: int = 900,
              size: int = 54) -> None:
    import graphics as G
    lines = [ASS_HEAD]
    lines.append("[Events]")
    lines.append("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text")
    for r in with_words(rows):
        fnt = G.fit_font(G.PLEX_B, r["ar"], max_w, size, 42)
        # توزيع الكلمات على أسطر بقياس فعلي للخط (سطران كحد أقصى)
        groups: list[list[dict]] = [[]]
        cur = ""
        for w in r["words"]:
            t = (cur + " " + w["text"]).strip()
            if G.text_w(fnt, G.ar(t)) <= max_w or not cur:
                groups[-1].append(w)
                cur = t
            else:
                groups.append([w])
                cur = w["text"]
        if len(groups) > 2:
            mid = (len(groups) + 1) // 2
            groups = [sum(groups[:mid], []), sum(groups[mid:], [])]

        txt = "\\N".join(" ".join(w["text"] for w in g) for g in groups)
        head = "{\\fad(100,100)\\fs%d\\pos(540,%d)\\an5}" % (fnt.size, y)
        lines.append("Dialogue: 1,%s,%s,Cap,,0,0,0,,%s%s" % (
            S.ass_time(r["start"]), S.ass_time(r["end"]), head, txt))
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
