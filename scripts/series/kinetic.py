"""كابشن كينتيك v2 — بطاقة = سطر واحد، والكلمة المنطوقة تتوهّج وتكبر مع النطق.

المبادئ:
  • لا معالجة اتجاه ولا arabic_reshaper: libass يشكّل العربية ويرتّبها RTL بنفسه،
    فنُمرّر النص المنطقي كما هو (هذا سبب «الكلام المعكوس» في النظام القديم).
  • بطاقة واحدة = سطر واحد قصير (٣–٧ كلمات): حجم أكبر، قراءة أسرع، وإيقاع حيّ.
  • لكل كلمة نافذة زمنية؛ عند نطقها تُلوَّن ذهبيًا وتُكبَّر قليلًا مع توهّج،
    ثم تعود. الخطوة تُرسَم بحدثين: الأساس (الكلمة مخفيّة) + الإبراز (بقية السطر مخفيّ)
    حتى لا يحدث تراكب أو انزياح في المحاذاة.
  • بلا صندوق ميّت: توهّج + ظلّ فقط، فوق شريط رواق / شريط زجاجي حسب التنسيق.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import arabic_reshaper
from bidi.algorithm import get_display

PARCH = "&H00F2F7FC"    # #FCF7F2 أبيض دافئ
GOLD = "&H005AC0F7"     # #F7C05A ذهب مضيء
GOLD_HI = "&H00468FE0"  # #E08F46 هالة
INK = "&H00120F0B"      # #0B0F12

HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,IBM Plex Sans Arabic,{size},{parch},{gold},{ink},&H00000000,-1,0,0,0,100,100,{spacing},0,1,{outline},0,5,40,40,0,1
"""

PROFILES = {
    "h": dict(W=1920, H=1080, size=100, min_size=62, max_w=1440, max_words=6,
              cy=962, outline=4.0, spacing=3.0, glow_bord=11, glow_blur=8),
    "v": dict(W=1080, H=1920, size=118, min_size=72, max_w=900, max_words=5,
              cy=1318, outline=5.0, spacing=3.0, glow_bord=13, glow_blur=9),
}


# ------------------------------------------------------------------ srt
def _t(s: str) -> float:
    h, m, rest = s.strip().replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(rest)


def parse_srt(path: str) -> list[dict]:
    import re
    txt = open(path, encoding="utf-8-sig").read().replace("\r", "")
    rows = []
    for block in re.split(r"\n\s*\n", txt):
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if len(lines) < 2:
            continue
        m = re.match(r"([\d:.,]+)\s*-->\s*([\d:.,]+)", lines[1])
        if not m:
            continue
        body = " ".join(" ".join(lines[2:]).split())
        if not body:
            continue
        rows.append({"start": _t(m.group(1)), "end": _t(m.group(2)), "text": _clean(body)})
    rows.sort(key=lambda r: r["start"])
    return rows


def vis(text: str) -> str:
    """العربية بصيغة العرض (أشكال مترابطة + ترتيب بصري) — libass يرسم هذه الأشكال كما هي.

    نعتمد على reshaped+bidi مرة واحدة على مستوى النص، ثم نبني السطر من الكلمات
    بترتيب بصري معاكس، وهو ما يعطي نفس البايتات بالضبط (مُختبَر) فيبقى الترتيب سليمًا.
    """
    return get_display(arabic_reshaper.reshape(text))


def _clean(text: str) -> str:
    t = " ".join(text.split())
    t = t.replace(" …", "…").replace("،،", "،")
    t = t.strip()
    while t[:1] in ("…", "،", "."):
        t = t[1:].strip()
    return t


# ------------------------------------------------------------------ layout / resegment
def fit_size(words: list[str], prof: dict) -> int:
    """أكبر حجم خط يُبقي السطر داخل العرض المسموح."""
    import graphics as G
    text = " ".join(words)
    px = prof["size"]
    while px > prof["min_size"]:
        f = G.font(G.PLEX_B, px)
        if G.text_w(f, G.ar(text)) <= prof["max_w"]:
            return px
        px -= 2
    return prof["min_size"]


def resegment(rows: list[dict], prof: dict) -> list[dict]:
    """يقطع البطاقات الطويلة إلى أسطر قصيرة (٣–max_words كلمة) ويوزّع الزمن عليها."""
    import graphics as G
    out = []
    for r in rows:
        words = r["text"].split(" ")
        chunks: list[list[str]] = []
        cur: list[str] = []
        for w in words:
            trial = cur + [w]
            f = G.font(G.PLEX_B, prof["size"])
            too_wide = len(cur) >= 2 and G.text_w(f, G.ar(" ".join(trial))) > prof["max_w"]
            if cur and (len(cur) >= prof["max_words"] or too_wide):
                chunks.append(cur)
                cur = [w]
            else:
                cur = trial
            # إن كانت الكلمة وحدها أعرض من السطر نحاول تصغير الكل لاحقًا
        if cur:
            chunks.append(cur)
        # لا نترك كلمة يتيمة في آخر المقطع
        if len(chunks) > 1 and len(chunks[-1]) == 1 and len(chunks[-2]) >= 3:
            chunks[-1].insert(0, chunks[-2].pop())
        weights = [sum(len(w) + 1.4 for w in c) for c in chunks]
        total_w = sum(weights)
        span = max(0.4, r["end"] - r["start"])
        t = r["start"]
        for c, wt in zip(chunks, weights):
            dur = span * wt / total_w
            out.append({"start": t, "end": t + dur, "text": " ".join(c), "words_txt": c})
            t += dur
    # سدّ الفراغات الصغيرة بين البطاقات
    for a, b in zip(out, out[1:]):
        if 0 < b["start"] - a["end"] < 0.45:
            a["end"] = b["start"]
    for r in out:
        r["px"] = fit_size(r["words_txt"], prof)
        ws = r["words_txt"]
        r["vtok"] = [vis(w) for w in reversed(ws)]      # ترتيب بصري = معاكس للمنطقي
        r["vmap"] = {i: len(ws) - 1 - i for i in range(len(ws))}
    return out


def add_words(rows: list[dict]) -> list[dict]:
    """توزيع زمن البطاقة على كلماتها بوزن طول الكلمة."""
    for r in rows:
        ws = r["words_txt"]
        weights = [max(2.0, len(w)) + 1.2 for w in ws]
        total = sum(weights)
        span = max(0.3, r["end"] - r["start"])
        t = r["start"]
        words = []
        for w, k in zip(ws, weights):
            d = span * k / total
            words.append({"text": w, "start": t, "end": min(r["end"], t + d)})
            t += d
        if words:
            words[-1]["end"] = r["end"]
        r["words"] = words
    return rows


# ------------------------------------------------------------------ ass
def _as(t: float) -> str:
    t = max(0.0, t)
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    return "%d:%02d:%05.2f" % (h, m, t % 60)


def _esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace("{", "(").replace("}", ")")


def _line(ws: list[str], hide: set[int], colour_of: dict[int, str]) -> str:
    """سطر كامل؛ الكلمات في hide شفافة تمامًا، والباقي بلونه (افتراضيًا الأبيض)."""
    parts = []
    for i, w in enumerate(ws):
        e = _esc(w)
        if i in hide:
            parts.append("{\\alpha&HFF&}%s{\\alpha&H00&}" % e)
        elif i in colour_of:
            parts.append("{\\c%s}%s{\\c%s}" % (colour_of[i], e, PARCH))
        else:
            parts.append(e)
    return " ".join(parts)


def build_ass(rows: list[dict], out_path: str, fmt: str = "h", fade: int = 100,
              glow: bool = True) -> dict:
    prof = PROFILES[fmt]
    rows = add_words(resegment(rows, prof))
    head = HEAD.format(W=prof["W"], H=prof["H"], size=prof["size"], outline=prof["outline"],
                       spacing=prof.get("spacing", 2.0), parch=PARCH, gold=GOLD, ink=INK)
    ev = []
    base_bord = "\\bord%d\\shad3" % prof["outline"]
    hi = ("\\fscx100\\fscy100\\t(0,60,\\fscx107\\fscy107)\\bord%d\\3c%s\\blur0\\fsp3\\shad3"
          % (prof["outline"] + 1.5, INK))
    hi_reset = "\\fscx100\\fscy100\\bord%d.0\\blur0\\fsp0" % prof["outline"]
    for r in rows:
        st, en = r["start"], r["end"]
        px = r["px"]
        pos = "\\pos(%d,%d)\\an5\\q2" % (prof["W"] // 2, prof["cy"])
        fad = "\\fad(%d,%d)\\fs%d" % (fade, fade, px)
        plain = _line(r["vtok"], set(), {})
        # (لا هالة على السطر كاملًا: تُنتج شبحًا خلف الكلمة المكبّرة)
        # الظلّ يُدمج داخل حدث النص نفسه (\\shad) بدل طبقة منفصلة تُبقي صورة رمادية للكلمات المخفيّة
        # خطوة لكل كلمة: الأساس (الكلمة مخفيّة) + الإبراز (بقية السطر مخفيّ)
        n = len(r["vtok"])
        for i, w in enumerate(r["words"]):
            a, b = max(st, w["start"]), min(en, w["end"])
            if b - a < 0.04:
                continue
            j = r["vmap"][i]
            ev.append("Dialogue: 2,%s,%s,Cap,,0,0,0,,{%s%s%s}%s" % (
                _as(a), _as(b), pos, fad, "\\bord%d\\shad3" % prof["outline"], _line(r["vtok"], {j}, {})))
            hide = set(range(n)) - {j}
            ev.append("Dialogue: 2,%s,%s,Cap,,0,0,0,,{%s%s%s}%s" % (
                _as(a), _as(b), pos, fad, hi,
                _line(r["vtok"], hide, {j: GOLD}) + "{\\c%s%s}" % (PARCH, hi_reset)))
    out = [head, "[Events]",
           "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    out += ev
    open(out_path, "w", encoding="utf-8").write("\n".join(out) + "\n")
    return {"cards": len(rows), "events": len(ev), "words": sum(len(r["words"]) for r in rows)}


if __name__ == "__main__":
    src, fmt, out = sys.argv[1], sys.argv[2], sys.argv[3]
    print(build_ass(parse_srt(src), out, fmt=fmt))
