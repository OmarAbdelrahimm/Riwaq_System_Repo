"""توليد ملف ASS للكابشن الكينتيك: نص عربي كبير داخل شريط رواق + إبراز الكلمة المنطوقة (كاريوكي ذهبي)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import srtlib as S  # noqa: E402
import graphics as G  # noqa: E402

PARCH = "&H00DBEBF3"   # #F3EBDB بالترتيب BGR
GOLD = "&H0069A4C2"    # #C2A469
INK = "&H000E1316"

HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,IBM Plex Sans Arabic,56,{gold},{parch},&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,230,230,0,1
"""


def karaoke_text(row: dict, size: int = 56, x: int = 960, y: int = 993) -> str:
    """نص البطاقة بصيغة ASS: كاريوكي لكل كلمة (المنطوق يصير ذهبيًا).

    PrimaryColour = الذهبي (بعد النطق) — SecondaryColour = الورقي (قبل النطق).
    """
    parts = []
    prev_end = row["start"]
    for w in row["words"]:
        lead = max(0.0, w.start - prev_end)
        if lead > 0.01:
            parts.append("{\\k%d}" % max(1, int(round(lead * 100))))
        dur = max(0.04, w.end - w.start)
        parts.append("{\\k%d}%s " % (max(2, int(round(dur * 100))), w.text))
        prev_end = w.end
    if prev_end < row["end"]:
        parts.append("{\\k%d}" % max(1, int(round((row["end"] - prev_end) * 100))))
    body = "".join(parts).rstrip()
    return "{\\fad(120,120)\\fs%d\\pos(%d,%d)}" % (size, x, y) + body


def build_ass(rows: list[dict], out_path: str, size: int = 56,
              y: int = 993, x: int = 960) -> None:
    lines = [HEADER.format(gold=GOLD, parch=PARCH)]
    lines.append("[Events]")
    lines.append("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text")
    for r in rows:
        # حجم الخط يتكيّف مع طول السطر ليبقى داخل الشريط بعرضه الكامل
        fit = G.fit_font(G.PLEX_B, r["text"], 1240, size + 8, min_px=44)
        txt = karaoke_text(r, fit.size, x, y)
        lines.append("Dialogue: 1,%s,%s,Cap,,0,0,0,,%s" % (
            S.ass_time(r["start"]), S.ass_time(r["end"]), txt))
    open(out_path, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def apply_final(rows: list[dict], ar_final: list[str] | None, en_final: list[str] | None,
                silences: list[tuple[float, float]] | None = None):
    """يستبدل نص البطاقات بنسخة محرّرة يدويًا، ويعيد بناء توقيت الكلمات داخل كل بطاقة."""
    import srtlib as S2
    out = []
    drop = set()
    for i, r in enumerate(rows):
        txt = (ar_final[i] if ar_final and i < len(ar_final) else r["text"]).strip()
        if not txt:
            drop.add(i)
            continue
        ws = S2.words_of(txt)
        span = max(0.6, r["end"] - r["start"])
        per = span / max(1, len(ws))
        words = [S2.Word(w, r["start"] + k * per, r["start"] + (k + 1) * per, 0) for k, w in enumerate(ws)]
        out.append({"start": r["start"], "end": r["end"], "words": words, "text": txt,
                    "en": (en_final[i].strip() if en_final and i < len(en_final) else "")})
    # سدّ الفراغات حتى لا يفرغ الشريط، مع إبقاء وقفات الكلام الحقيقية فقط
    for idx in range(len(out) - 1):
        gap = out[idx + 1]["start"] - out[idx]["end"]
        is_break = False
        if silences and gap > 0.05:
            mid = out[idx]["end"] + gap / 2
            is_break = any(a - 0.25 <= mid <= b + 0.25 for a, b in silences)
        if gap > 0.02 and gap <= 7.0 and not is_break:
            out[idx]["end"] = out[idx + 1]["start"]
            if out[idx]["words"]:
                w = out[idx]["words"][-1]
                out[idx]["words"][-1] = type(w)(w.text, w.start, out[idx]["end"], 0)
    # لا تبقى أي بطاقة على الشاشة أكثر من 7.5 ثوانٍ
    for r in out:
        if r["end"] - r["start"] > 7.5:
            r["end"] = r["start"] + 7.5
    # ثم: لا شريط فارغ أطول من 1.2s في أي حال (الفراغ يبدو خللًا للمشاهد)
    for idx in range(len(out) - 1):
        gap = out[idx + 1]["start"] - out[idx]["end"]
        if gap > 1.2:
            out[idx]["end"] = out[idx + 1]["start"] - 0.12
            if out[idx]["words"]:
                w = out[idx]["words"][-1]
                out[idx]["words"][-1] = type(w)(w.text, w.start, out[idx]["end"], 0)
    # تقسيم أي بطاقة طويلة جدًا (فوق 9 ثوانٍ) إلى بطاقتين بنفس النص الأصلي
    split: list[dict] = []
    for r in out:
        dur = r["end"] - r["start"]
        ws = r["words"]
        if dur > 9.0 and len(ws) >= 4:
            mid_t = r["start"] + dur / 2
            left, right = [], []
            for w in ws:
                (left if w.start < mid_t else right).append(w)
            if left and right:
                for part, a, b in ((left, r["start"], right[0].start), (right, right[0].start, r["end"])):
                    split.append({"start": a, "end": b, "words": part,
                                  "text": " ".join(w.text for w in part), "en": r["en"]})
                continue
        split.append(r)
    out = split
    # بطاقة القراءة الأولى لا تقل عن ثانيتين
    if out and out[0]["end"] - out[0]["start"] < 2.0 and len(out) > 1:
        out[0]["end"] = out[1]["start"]
    return out


def build_en_srt(en_rows: list[dict], path: str) -> None:
    S.write_srt(en_rows, path)


def build_ar_srt(rows: list[dict], path: str) -> None:
    S.write_srt(rows, path)


def build_bilingual_srt(rows: list[dict], en_rows: list[dict], path: str) -> None:
    out = []
    for i, (r, e) in enumerate(zip(rows, en_rows), 1):
        out.append(f"{i}\n{S.srt_time(r['start'])} --> {S.srt_time(r['end'])}\n{r['text'].strip()}\n{e['text'].strip()}\n")
    open(path, "w", encoding="utf-8").write("\n".join(out))


if __name__ == "__main__":
    src, dur, outp = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    cues = S.parse_srt(src)
    words = S.reconstruct(cues)
    rows = S.build_caption_rows(words, dur)
    build_ass(rows, outp)
    print(f"rows={len(rows)} words={len(words)} -> {outp}")
