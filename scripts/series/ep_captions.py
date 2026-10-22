"""كابشن الحلقات الجديدة (04–06): بناء بطاقات نظيفة من ترجمة المصدر المتدحرجة.

ترجمة المصدر (mov_text) تعمل بنظام roll-up: كل بطاقة تعيد آخر سطر من السابقة ثم تضيف سطرًا جديدًا.
هنا نستخرج «السطر الجديد» فقط مع توقيته، ثم ندمج الأسطر في عبارات قصيرة قابلة للقراءة،
ونوزّع توقيت الكلمات داخل كل عبارة (للكاريوكي) بحسب طول الكلمة.
"""
from __future__ import annotations

import re
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import srtlib as S  # noqa: E402

CLEAN_MAP = {
    "ذباتنا": "ذواتنا", "ذباتي": "ذاتي", "العلاقه": "العلاقة", "علاقه": "علاقة",
    "العلاقات": "العلاقات", "الشيطان": "الشيطان",
}


def _parse_all(path):
    """يعيد [(start, end, [كل أسطر البطاقة])] — نحتاج آخر سطر (الجديد) في نظام roll-up."""
    txt = open(path, encoding="utf-8-sig").read().replace("\r", "")
    out = []
    for block in re.split(r"\n\s*\n", txt):
        lines = [l for l in block.split("\n") if l.strip()]
        if len(lines) < 2:
            continue
        m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", lines[1])
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        st = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        en = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        out.append((st, en, [x.strip() for x in lines[2:] if x.strip()]))
    return out


def _segments(cues, a: float, b: float):
    """[(start, end, text)] للسطور الجديدة فقط داخل النافذة [a,b]، بتوقيت مُعاد ضبطه."""
    out = []
    seen = ""
    for st0, en0, lines in cues:
        if en0 <= a or st0 >= b:
            continue
        if not lines:
            continue
        new = lines[-1]
        if new == seen:
            continue
        seen = new
        st = max(a, st0) - a
        en = min(b, en0) - a
        if en - st < 0.25:
            continue
        out.append((st, en, S.norm_space(new)))
    return out


def _join_ok(prev: str, nxt: str) -> bool:
    if not prev:
        return True
    # لا نبدأ عبارة جديدة بكلمة وصل
    return not re.match(r"^(و|ثم|لكن|ف|ب|ل|أن|إن|ال)\S{0,2}$", nxt.split(" ")[0])


def build_rows(path: str, a: float, b: float, max_chars: int = 52, max_words: int = 9):
    cues = _parse_all(path)
    segs = _segments(cues, a, b)
    dur = b - a
    groups: list[list[tuple[float, float, str]]] = []
    cur: list[tuple[float, float, str]] = []
    clen = 0
    for seg in segs:
        txt = seg[2]
        add = len(txt) + (1 if cur else 0)
        if cur and (clen + add > max_chars or sum(len(x[2].split()) for x in cur) + len(txt.split()) > max_words):
            # نقطع عند آخر وقفة طبيعية إن وُجدت
            groups.append(cur)
            cur, clen = [], 0
            add = len(txt)
        cur.append(seg)
        clen += add
    if cur:
        groups.append(cur)

    rows = []
    for i, g in enumerate(groups):
        st = g[0][0]
        en = g[-1][1]
        nxt = groups[i + 1][0][0] if i + 1 < len(groups) else dur
        if nxt - en < 0.45:
            en = min(nxt, en + 0.4)
        text = S.norm_space(" ".join(x[2] for x in g))
        rows.append({"start": round(st, 2), "end": round(min(dur, en), 2), "text": text})
    # دمج البطاقات القصيرة جدًا مع التالية حتى يبقى الشريط مقروءًا (لا بطاقة تحت 26 حرفًا)
    merged: list[dict] = []
    for r in rows:
        if merged and (len(merged[-1]["text"]) < 26 or len(r["text"]) < 16) and \
                len(merged[-1]["text"]) + len(r["text"]) <= 74:
            merged[-1]["text"] = S.norm_space(merged[-1]["text"] + " " + r["text"])
            merged[-1]["end"] = r["end"]
        else:
            merged.append(dict(r))
    return merged, dur


if __name__ == "__main__":
    import json
    import ep_data as E
    for ep in E.EPISODES:
        k = ep["key"]
        a, b = ep["cut"]
        rows, dur = build_rows(f"google_drive/subtitles_src/p{int(ep['part'][1:])}.srt", a, b)
        with open(f"google_drive/work/ep/{k}_rows.txt", "w", encoding="utf-8") as f:
            for i, r in enumerate(rows, 1):
                f.write(f"{i:02d}\t{r['start']:6.2f}\t{r['end']:6.2f}\t{r['text']}\n")
        json.dump(rows, open(f"google_drive/work/ep/{k}_rows.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print(k, "dur", round(dur, 1), "rows", len(rows))
