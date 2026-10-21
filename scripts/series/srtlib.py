"""أدوات الكابشن لسلسلة رواق — إعادة بناء نص متصل من بطاقات roll-up ثم إعادة تقسيمها.

الفكرة: بطاقات الإيجنت الآخر مبنية على نظام "سطر متدحرج" يكرّر ذيل البطاقة السابقة،
ما يُنتج تكرارات حرفية وأسطرًا مقطوعة في منتصف الجملة. هنا نستعيد الكلام المتصل
(نص + توقيت لكل كلمة) ثم نعيد تقطيعه إلى بطاقات نظيفة، ونبني ملف ASS بكاريوكي
كلمة-بكلمة، ونحافظ على ترجمة الإنجليزي عبر إعادة ربطها بالبطاقات الجديدة.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

AR_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")

# تصحيحات آمنة (إملاء/أخطاء تفريغ شائعة) — لا تمسّ مفردات اللهجة نفسها
SAFE_FIXES = {
    "الععلاقات": "العلاقات",
    "تعإلى": "تعالى",
    "مش": "مو",  # إبقاء طابع سعودي معياري أكث ر رسمية
    "بء": "باء",
    "الال": "",
    "الشبكه": "الشبكة",
    "البوصله": "البوصلة",
    "العابره": "العابرة",
    "الصاعده": "الصاعدة",
    "الهابطه": "الهابطة",
    "القاعده": "القاعدة",
    "مبادئك": "مبادئك",
    "هذول": "هؤلاء",
    "الاسئله": "الأسئلة",
    "الاسئلة": "الأسئلة",
    "الاخر": "الآخر",
    "الاخرين": "الآخرين",
    "الاخره": "الآخرة",
    "الاخرى": "الأخرى",
    "الانسان": "الإنسان",
    "افضل": "أفضل",
    "الافضل": "الأفضل",
    "الف": "ألف",
    "اهم": "أهم",
    "اول": "أول",
    "اذا": "إذا",
    "الا": "إلا",
    "انت": "أنت",
    "انا": "أنا",
    "ايضا": "أيضًا",
    "الان": "الآن",
    "ايش": "إيش",
    "اي": "أي",
    "تزكيه": "تزكية",
    "مرجعيه": "مرجعية",
    "بوصله": "بوصلة",
    "علاقتنا": "علاقتنا",
    "مثال": "مثال",
}

# لا نُصلح داخل هذه الكلمات (حماية من التغيير الخاطئ)
PROTECT = set()


def norm_space(s: str) -> str:
    s = s.replace("\u200f", "").replace("\u200e", "").replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def words_of(s: str) -> list[str]:
    return [w for w in norm_space(s).split(" ") if w]


def fix_words(ws: list[str]) -> list[str]:
    out = []
    for w in ws:
        core = re.sub(r"[^\u0621-\u064A]", "", w)
        out.append(SAFE_FIXES.get(core, w) if core not in PROTECT else w)
    return [w for w in out if w]


@dataclass
class Cue:
    idx: int
    start: float
    end: float
    ar: str
    en: str = ""


def parse_srt(path: str) -> list[Cue]:
    txt = open(path, encoding="utf-8-sig").read().replace("\r", "")
    cues: list[Cue] = []
    for block in re.split(r"\n\s*\n", txt):
        lines = [l for l in block.split("\n") if l.strip()]
        if len(lines) < 3:
            continue
        m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", lines[1])
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        st = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        en = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        body = lines[2:]
        # البطاقة الثنائية: السطر الأول عربي، والباقي إنجليزي
        ar = body[0]
        en_txt = " ".join(body[1:]) if len(body) > 1 else ""
        cues.append(Cue(len(cues) + 1, st, en, ar, en_txt))
    return cues


@dataclass
class Word:
    text: str
    start: float
    end: float
    cue: int


def reconstruct(cues: list[Cue]) -> list[Word]:
    """يبني قائمة كلمات متصلة مع توقيت تقريبي لكل كلمة، بإزالة تكرارات roll-up."""
    buf: list[str] = []
    times: list[tuple[float, float]] = []
    words: list[Word] = []
    for c in cues:
        t = fix_words(words_of(c.ar))
        if not t:
            continue
        # أطول تطابق بين بداية البطاقة وذيل النص المتراكم
        k = 0
        for cand in range(min(len(t), len(buf)), 0, -1):
            if t[:cand] == buf[-cand:]:
                k = cand
                break
        new = t[k:]
        # إزالة التكرار الفوري ("على على" / "لا يقف على على")
        dedup: list[str] = []
        for w in new:
            if dedup and w == dedup[-1]:
                continue
            if len(dedup) >= 2 and dedup[-2:] == [w, w]:
                continue
            dedup.append(w)
        new = dedup
        if not new:
            # البطاقة كلها مكررة: نمدّد توقيت آخر الكلمات فقط
            if times:
                times[-1] = (times[-1][0], max(times[-1][1], c.end))
            continue
        span = max(0.35, c.end - c.start)
        # الكلمات القديمة المكررة تأخذ حصة من الزمن حسب طولها
        old_ratio = k / max(1, len(t))
        t0 = c.start + span * old_ratio
        per = (c.end - t0) / len(new)
        for i, w in enumerate(new):
            ws = t0 + i * per
            words.append(Word(w, ws, ws + per, c.idx))
        buf.extend(new)
        times.extend([(t0 + i * per, t0 + (i + 1) * per) for i in range(len(new))])
        # إعادة مزامنة التوقيت التراكمي مع نهاية البطاقة
        if times:
            times[-1] = (times[-1][0], max(times[-1][1], c.end))
    return words


PUNCT_SPLIT = re.compile(r"[،؛:؟!.]")


def chunk_words(words: list[Word], max_chars: int = 46, max_words: int = 8) -> list[list[Word]]:
    """تقطيع إلى بطاقات قصيرة، مع تفضيل حدود البطاقات الأصلية (وقفات الكلام)."""
    chunks: list[list[Word]] = []
    cur: list[Word] = []
    cur_len = 0
    breaks: list[tuple[int, int]] = []  # (عدد الكلمات عند الحد، طول النص حينها)
    for w in words:
        if cur and w.cue != cur[-1].cue:
            breaks.append((len(cur), cur_len))
        add = len(w.text) + (1 if cur else 0)
        if cur and (cur_len + add > max_chars or len(cur) >= max_words):
            cut = None
            for bi, bl in reversed(breaks):
                if bl >= max_chars * 0.42 and bi < len(cur):
                    cut = bi
                    break
            if cut is None:
                cut = len(cur)
            head, tail = cur[:cut], cur[cut:]
            chunks.append(head)
            cur = tail
            cur_len = sum(len(x.text) + 1 for x in tail)
            breaks = [(bi - cut, bl) for bi, bl in breaks if bi > cut]
        cur.append(w)
        cur_len += add
    if cur:
        chunks.append(cur)
    # دمج البطاقات القصيرة جدًا مع الجارة
    merged: list[list[Word]] = []
    for ch in chunks:
        ln = sum(len(x.text) + 1 for x in ch)
        if merged and (ln < 15 or len(ch) <= 1) and len(merged[-1]) + len(ch) <= max_words + 2:
            merged[-1].extend(ch)
        else:
            merged.append(ch)
    return merged


def build_caption_rows(words: list[Word], duration: float,
                       max_chars: int = 52, max_words: int = 9) -> list[dict]:
    rows = []
    chunks = chunk_words(words, max_chars, max_words)
    for i, ch in enumerate(chunks):
        st = ch[0].start
        en = ch[-1].end
        nxt = chunks[i + 1][0].start if i + 1 < len(chunks) else duration
        # إغلاق الفجوات الصغيرة (شريط لا يفرغ)
        nn = min(nxt, st + 6.2)
        if nn - en < 0.55:
            en = min(nn, en + 0.45)
        rows.append({
            "start": max(0.0, st),
            "end": min(duration, max(en, st + 0.8)),
            "words": ch,
            "text": " ".join(w.text for w in ch),
        })
    return rows


def srt_time(t: float) -> str:
    if t < 0:
        t = 0
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    if ms == 1000:
        ms = 0
        s += 1
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def ass_time(t: float) -> str:
    if t < 0:
        t = 0
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


def write_srt(rows: list[dict], path: str, lang: str = "ar") -> None:
    out = []
    for i, r in enumerate(rows, 1):
        out.append(f"{i}\n{srt_time(r['start'])} --> {srt_time(r['end'])}\n{r['text'].strip()}\n")
    open(path, "w", encoding="utf-8").write("\n".join(out))


# ---------- الترجمة الإنجليزية: إعادة ربط ترجمة الإيجنت بالبطاقات الجديدة ----------

def en_for_range(cues: list[Cue], start: float, end: float) -> str:
    parts = []
    for c in cues:
        if not c.en:
            continue
        ov = min(c.end, end) - max(c.start, start)
        if ov > 0.25 * max(0.2, c.end - c.start) or (c.start >= start and c.start < end):
            parts.append(norm_space(c.en))
    # إزالة التكرار الحرفي والإنجليزي المتدحرج
    out: list[str] = []
    for p in parts:
        if out and (p == out[-1] or p.startswith(out[-1])):
            out[-1] = p
            continue
        out.append(p)
    txt = " ".join(out)
    return norm_space(re.sub(r"\s+([,.؟!])", r"\1", txt))


def build_en_rows(rows: list[dict], cues: list[Cue]) -> list[dict]:
    res = []
    for r in rows:
        t = en_for_range(cues, r["start"], r["end"])
        if not t:
            t = r["text"]  # سقوط آمن: نضع العربي بدلًا من فراغ
        res.append({"start": r["start"], "end": r["end"], "text": t})
    return res
