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
    "h": dict(W=1920, H=1080, size=94, min_size=66, max_w=1300, max_words=3,
              cy=993, outline=4.5, spacing=3.0, glow_bord=0, glow_blur=5),
    "v": dict(W=1080, H=1920, size=140, min_size=80, max_w=900, max_words=3,
              cy=1403, outline=6.0, spacing=3.0, glow_bord=0, glow_blur=6),
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


def _envelope(audio: str | None) -> tuple | None:
    """مغلّف طاقة صوت المتحدث بدقة 10ms — لضبط حدود الكلمات على السكتات الحقيقية."""
    if not audio or not os.path.exists(audio):
        return None
    try:
        import numpy as np
        import subprocess
        ff = os.environ.get("FFMPEG") or "ffmpeg"
        p = subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-i", audio,
                            "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                           capture_output=True)
        if p.returncode != 0 or len(p.stdout) < 32000:
            return None
        x = np.frombuffer(p.stdout, dtype="<i2").astype("float32") / 32768.0
        hop = 160                                  # 10 ms
        n = len(x) // hop
        fr = x[: n * hop].reshape(n, hop)
        rms = np.sqrt((fr ** 2).mean(1))
        k = np.hanning(7)
        rms = np.convolve(rms, k / k.sum(), mode="same")
        return rms, 100.0                          # إطار/ثانية
    except Exception:
        return None


def _snap(env, t0: float, t1: float, weights: list[float]) -> list[float]:
    """حدود الكلمات داخل المقطع: توزيع بطول الكلمة ثم «تثبيت» كل حد على أقرب سكتة.

    هذا ما يجعل اللون الأصفر يقع مع النطق فعليًا بدل توزيع رياضي أعمى.
    """
    n = len(weights)
    if n <= 1:
        return [t0, t1]
    tot = sum(weights)
    bounds = [t0]
    acc = 0.0
    for w in weights[:-1]:
        acc += w
        bounds.append(t0 + (t1 - t0) * acc / tot)
    bounds.append(t1)
    if env is None:
        return bounds
    import numpy as np
    rms, fps = env
    span = max(0.06, t1 - t0)
    win = min(0.16, max(0.07, span / (n + 1) * 0.55))
    out = [t0]
    for i in range(1, n):
        guess = bounds[i]
        lo = max(out[-1] + 0.07, guess - win)
        hi = min(t1 - 0.07, guess + win)
        if hi <= lo:
            out.append(guess)
            continue
        a, b = int(lo * fps), int(hi * fps)
        a, b = max(0, a), min(len(rms), b + 1)
        if b - a < 3:
            out.append(guess)
            continue
        seg = rms[a:b]
        # نختار أهدأ نقطة (سكتة) مع تفضيل القريب من التقدير الرياضي
        idx = np.arange(len(seg))
        centre = (guess * fps) - a
        penalty = 0.35 * np.abs(idx - centre) / max(1.0, (b - a) / 2)
        score = seg / (seg.max() + 1e-9) + penalty
        out.append(round((a + int(np.argmin(score))) / fps, 3))
    out.append(t1)
    # اضمن تزايدًا صارمًا
    for i in range(1, len(out)):
        out[i] = max(out[i], out[i - 1] + 0.06)
    out[-1] = max(out[-1], out[-2] + 0.06)
    return out


def _chunk(words: list[str], prof: dict) -> list[list[int]]:
    """تقسيم كلمات المقطع إلى بطاقات (٣ كلمات كحد أقصى) دون تجاوز عرض السطر."""
    import graphics as G
    f = G.font(G.PLEX_B, prof["size"])
    chunks, cur = [], []
    for i, w in enumerate(words):
        trial = cur + [i]
        too_wide = len(cur) >= 2 and G.text_w(f, G.ar(" ".join(words[j] for j in trial))) > prof["max_w"]
        if cur and (len(cur) >= prof["max_words"] or too_wide):
            chunks.append(cur)
            cur = [i]
        else:
            cur = trial
    if cur:
        chunks.append(cur)
    # لا نترك كلمة يتيمة في آخر المقطع
    if len(chunks) > 1 and len(chunks[-1]) == 1 and len(chunks[-2]) >= 2:
        chunks[-1].insert(0, chunks[-2].pop())
    return chunks


PRE = 0.10      # البطاقة تظهر قبل نطق أول كلمة بقليل
LEAD = 0.05     # التلوين يسبق النطق بخمسين مللي لتصل الحركة مع الصوت
HOLD = 0.16     # بقاء البطاقة بعد آخر كلمة


def resegment(rows: list[dict], prof: dict, env=None) -> list[dict]:
    """بطاقات ≤ ثلاث كلمات، وكل كلمة تُوقَّت على سكتة حقيقية داخل المقطع."""
    out = []
    for r in rows:
        words = r["text"].split(" ")
        if not words:
            continue
        weights = [max(2.0, len(w)) + 1.2 for w in words]
        bounds = _snap(env, r["start"], r["end"], weights)
        wt = [{"text": w, "start": bounds[i], "end": bounds[i + 1]}
              for i, w in enumerate(words)]
        for ci, ch in enumerate(_chunk(words, prof)):
            ws = wt[ch[0]:ch[-1] + 1]
            st = max(0.0, ws[0]["start"] - PRE)
            en = ws[-1]["end"] + HOLD
            out.append({"start": st, "end": en, "text": " ".join(w["text"] for w in ws),
                        "words_txt": [w["text"] for w in ws], "words": ws,
                        "cue_start": ci == 0})
    # لا تسمح لبطاقة بأن تتجاوز بداية التالية
    for a_, b_ in zip(out, out[1:]):
        if a_["end"] > b_["start"] and b_["start"] > a_["start"] + 0.2:
            a_["end"] = b_["start"]
    for r in out:
        r["px"] = fit_size(r["words_txt"], prof)
        ws = r["words_txt"]
        r["vtok"] = [vis(w) for w in reversed(ws)]
        r["vmap"] = {i: len(ws) - 1 - i for i in range(len(ws))}
        # إزاحة الإبراز قليلًا للأمام (LEAD) مع الحفاظ على تسلسل الكلمات
        for i, w in enumerate(r["words"]):
            w["hl"] = max(r["start"], w["start"] - LEAD)
            if i:
                w["hl"] = max(w["hl"], r["words"][i - 1]["hl"] + 0.05)
    return out


def add_words(rows: list[dict]) -> list[dict]:
    """توافق خلفي: الزمن محسوب مسبقًا في resegment."""
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


def prepare(rows: list[dict], fmt: str = "h", audio: str | None = None):
    prof = PROFILES[fmt]
    env = _envelope(audio)
    cards = resegment(rows, prof, env)
    return prof, cards


def timeline(rows: list[dict]) -> list[dict]:
    """أحداث المؤثرات الصوتية: هوشة لكل بطاقة + نقرة لكل كلمة."""
    ev = []
    for r in rows:
        if r.get("cue_start", True):
            ev.append({"t": round(r["start"], 3), "kind": "card"})
        for w in r["words"]:
            ev.append({"t": round(w.get("hl", w["start"]), 3), "kind": "word"})
    ev.sort(key=lambda e: e["t"])
    return ev


def build_ass(rows: list[dict], out_path: str, fmt: str = "h", fade: int = 90,
              glow: bool = True, audio: str | None = None) -> dict:
    prof, rows = prepare(rows, fmt, audio)
    head = HEAD.format(W=prof["W"], H=prof["H"], size=prof["size"], outline=prof["outline"],
                       spacing=prof.get("spacing", 2.0), parch=PARCH, gold=GOLD, ink=INK)
    ev = []
    hi = ("\\fscx92\\fscy92\\t(0,90,\\fscx107\\fscy107)\\t(90,190,\\fscx100\\fscy100)"
          "\\bord%d\\3c%s\\blur0\\fsp3\\shad3" % (prof["outline"] + 1.5, INK))
    hi_reset = "\\fscx100\\fscy100\\bord%d.0\\blur0\\fsp0" % prof["outline"]
    for r in rows:
        en = r["end"]
        px = r["px"]
        pos = "\\pos(%d,%d)\\an5\\q2" % (prof["W"] // 2, prof["cy"])
        fad = "\\fad(%d,%d)\\fs%d" % (fade, fade, px)
        n = len(r["vtok"])
        steps = [w.get("hl", w["start"]) for w in r["words"]] + [en]
        for i in range(len(r["words"])):
            a_, b_ = max(r["start"], steps[i]), min(en, steps[i + 1])
            if b_ - a_ < 0.05:
                continue
            j = r["vmap"][i]
            hide = set(range(n)) - {j}
            # 1) هالة ذهبية ناعمة خلف الكلمة المنطوقة (لحظة النطق فقط)
            if glow:
                ev.append("Dialogue: 1,%s,%s,Cap,,0,0,0,,{%s%s%s}%s" % (
                    _as(a_), _as(b_), pos,
                    "\\fad(60,80)\\fs%d\\bord%d\\3c%s\\blur%d\\shad0\\fsp3\\alpha&H7A&"
                    % (px, prof.get("glow_bord", 10), GOLD, prof.get("glow_blur", 9)),
                    "", _line(r["vtok"], hide, {j: GOLD})))
            # 2) الأساس: الكلمة النشطة مخفيّة، والبقية بالعاجي
            ev.append("Dialogue: 2,%s,%s,Cap,,0,0,0,,{%s%s\\bord%d\\shad3}%s" % (
                _as(a_), _as(b_), pos, fad, prof["outline"], _line(r["vtok"], {j}, {})))
            # 3) الإبراز: ذهب + تكبير مع تجاوز سريع، والبقية مخفيّة
            ev.append("Dialogue: 3,%s,%s,Cap,,0,0,0,,{%s%s%s}%s" % (
                _as(a_), _as(b_), pos, fad, hi,
                _line(r["vtok"], hide, {j: GOLD}) + "{\\c%s%s}" % (PARCH, hi_reset)))
    out = [head, "[Events]",
           "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    out += ev
    open(out_path, "w", encoding="utf-8").write("\n".join(out) + "\n")
    return {"cards": len(rows), "events": len(ev),
            "words": sum(len(r["words"]) for r in rows), "timeline": timeline(rows)}


if __name__ == "__main__":
    src, fmt, out = sys.argv[1], sys.argv[2], sys.argv[3]
    print(build_ass(parse_srt(src), out, fmt=fmt))
