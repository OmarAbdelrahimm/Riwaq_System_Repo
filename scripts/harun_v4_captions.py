"""HARUN v4 — محرك الكابشن (كلمة بكلمة) + شعار اليسار.

المبدأ: السطر يُرسم مرة واحدة عبر libass (تشكيل عربي + اتجاه RTL بخوارزمية
يونيكود/فريبيدي التي يطبّقها libass)، والكلمة المنطوقة تُلوَّن وحدها بوسم
`\\1c` — فلا يوجد أي `\\pos` لكل كلمة، وبالتالي لا انزياح ولا تراكم أخطاء.

طبقتان بنفس التوقيت:
  • Halo — نسخة ذهبية مُموّهة (blur) بشفافية على الكلمة المنطوقة فقط (هالة ناعمة).
  • Cap  — النص الحاد: المنطوق ذهبي، والباقي بلون الرق.

المخرجات: /tmp/harun_v4.ass + data/projects/HARUN_001/word_timings_v4.json
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

REPO = Path("/home/user/Riwaq_System_Repo")
SRT = REPO / "docs/harun-vo-transcript-approved.srt"
ASR = Path("/home/user/words_raw.json")
ASS_OUT = REPO / "data/projects/HARUN_001/captions_v4.ass"
ASS_TMP = Path("/tmp/harun_v4.ass")
TIMINGS = REPO / "data/projects/HARUN_001/word_timings_v4.json"

FONT = "IBM Plex Sans Arabic"
CX, CY = 960, 944
MAX_W = 1330
BUG = "حكايات رِواق"
BUG_XY = (172, 107)

PARCH = "&H00DBEBF3&"
PARCH_B = "&H00DBEBF2&"   # فرق غير مرئي — يفرض «run» منفصل لكل كلمة
GOLD_HOT = "&H007EC8E9&"  # ذهبي فاتح هادئ (#E9C87E) بدل الأصفر النيون
GOLD_SOFT = "&H0058CDFF&"
GOLD_SOFT_B = "&H0058CDFE&"
BLACK = "&H00121010&"
HALO_OUT = "&H9A3AA0E8&"
HALO_ALPHA = "&H6A&"      # هالة أشفّ وأنعم (كانت &H50&)
HALO_BLUR = 22            # كانت 12 → كانت «مبكسلة»
HALO_BORD = 1.1
DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def tstamp(t: float) -> str:
    t = max(0.0, t)
    return f"{int(t//3600)}:{int((t%3600)//60):02d}:{t%60:05.2f}"


def norm(w: str) -> str:
    w = w.translate(DIGITS)
    w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^\w\u0600-\u06FF]", "", w.replace("ـ", ""))


def parse_srt() -> list[dict]:
    out = []
    for b in re.split(r"\n\s*\n", SRT.read_text(encoding="utf-8").strip()):
        lines = [x for x in b.splitlines() if x.strip()]
        if len(lines) < 2:
            continue
        m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", lines[1])
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        text = " ".join(lines[2:]).strip()
        if text:
            out.append({"start": g[0]*3600+g[1]*60+g[2]+g[3]/1000,
                        "end": g[4]*3600+g[5]*60+g[6]+g[7]/1000, "text": text})
    return out


def load_asr() -> list[dict]:
    d = json.loads(ASR.read_text())
    return [{"w": w["w"], "s": w["s"], "e": w["e"]}
            for seg in d["segments"] for w in seg["words"] if w["w"]]


def align(lines: list[dict], asr: list[dict]) -> list[dict]:
    used = [False] * len(asr)
    out = []
    for ln in lines:
        words = ln["text"].split()
        n = len(words)
        cand = [i for i, w in enumerate(asr) if not used[i]
                and w["s"] >= ln["start"] - 0.35 and w["e"] <= ln["end"] + 0.45]
        if len(cand) == n:
            ws = []
            for k, i in enumerate(cand):
                used[i] = True
                ws.append({"t": words[k], "s": asr[i]["s"], "e": asr[i]["e"]})
            method = "asr"
        else:
            total = sum(len(norm(w)) + 1 for w in words)
            t, span, ws = ln["start"], ln["end"] - ln["start"], []
            for w in words:
                d = span * (len(norm(w)) + 1) / total
                ws.append({"t": w, "s": round(t, 3), "e": round(t + d, 3)})
                t += d
            method = "ratio"
        for k in range(len(ws) - 1):
            ws[k]["e"] = max(ws[k]["s"] + 0.05, ws[k + 1]["s"])
        ws[-1]["e"] = max(ws[-1]["s"] + 0.05, ln["end"])
        out.append({**ln, "words": ws, "method": method})
    return out


def font_px(text: str) -> int:
    from PIL import ImageFont
    path = str(REPO / "public/fonts/IBMPlexSansArabic-Bold.ttf")
    for px in (58, 56, 54, 52, 50, 48, 46, 44):
        f = ImageFont.truetype(path, px)
        b = f.getbbox(text)
        if b[2] - b[0] <= MAX_W:
            return px
    return 42


def strip(words: list[dict], hot: int) -> tuple[str, str]:
    """يبني سطرين (حاد + هالة) بترتيب **معكوس** عن الترتيب المنطقي.

    libass في هذه النسخة بلا fribidi: السطر الخالي من الوسوم يُعاد ترتيبه
    صحيحًا (RTL)، لكن أي تغيير لون يقسم السطر إلى «runs» تُرسم من الشمال
    لليمين — وهو سبب ظهور الكابشن مقلوبًا. الحل المُثبَت بالقياس: كل كلمة
    في run مستقل، وتُرسَل الكلمات بترتيب معكوس فتظهر من اليمين لليسار.
    """
    n = len(words)
    order = list(range(n - 1, -1, -1))          # إرسال معكوس
    sharp, halo = [], []
    for k, i in enumerate(order):
        w = words[i]["t"]
        sp = " " if k < n - 1 else ""
        pa = PARCH if k % 2 == 0 else PARCH_B
        pb = GOLD_SOFT if k % 2 == 0 else GOLD_SOFT_B
        if i == hot:
            sharp.append("{\\1c" + GOLD_HOT + "\\3c" + BLACK + "}" + w + sp)
            halo.append("{\\1c" + pb + "\\alpha&HFF&\\3c" + HALO_OUT +
                        "\\alpha&H" + HALO_ALPHA[1:] + "\\blur" + str(HALO_BLUR) +
                        "\\bord" + str(HALO_BORD) + "}" + w + sp)
        else:
            sharp.append("{\\1c" + pa + "}" + w + sp)
            halo.append("{\\1c" + pb + "\\alpha&HFF&}" + w + sp)
    return "".join(sharp), "".join(halo)


HEAD = f"""[Script Info]
; HARUN v4 — الكلمة المنطوقة تُلوَّن وحدها، والسطر كله يرسمه libass (RTL صحيح)
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{FONT},58,{PARCH},{PARCH},{BLACK},&H00000000&,-1,0,0,0,100,100,0,0,1,2.6,1.9,5,0,0,0,1
Style: Halo,{FONT},58,{GOLD_SOFT},{GOLD_SOFT},{HALO_OUT},&H00000000&,-1,0,0,0,100,100,0,0,1,2.6,0,5,0,0,0,1
Style: Bug,{FONT},27,{GOLD_SOFT},{GOLD_SOFT},&H00000000&,&H00000000&,0,0,0,0,100,100,0.4,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def main() -> None:
    groups = align(parse_srt(), load_asr())
    ev, meta = [], []
    for g in groups:
        px = font_px(g["text"])
        pos = f"{{\\an5\\pos({CX},{CY})\\fs{px}}}"
        n = len(g["words"])
        for i, w in enumerate(g["words"]):
            t0 = w["s"]
            t1 = g["words"][i + 1]["s"] if i + 1 < n else g["end"]
            if t1 <= t0 + 0.03:
                t1 = t0 + 0.10
            sharp, halo = strip(g["words"], i)
            ev.append(f"Dialogue: 0,{tstamp(t0)},{tstamp(t1)},Halo,,0,0,0,,{pos}{halo}")
            ev.append(f"Dialogue: 1,{tstamp(t0)},{tstamp(t1)},Cap,,0,0,0,,{pos}{sharp}")
            meta.append({"group": g["text"], "word": w["t"], "start": round(t0, 3),
                         "end": round(t1, 3), "fs": px, "method": g["method"]})

    # شعار اليسار: 5 ظهورات كل 30 ث من 20 ث، 6 ث لكل ظهور
    t = 20.0
    while t + 6.0 < 156.0:
        ev.append(f"Dialogue: 2,{tstamp(t)},{tstamp(t+6)},Bug,,0,0,0,,"
                  f"{{\\an5\\pos({BUG_XY[0]},{BUG_XY[1]})\\fad(700,700)}}{BUG}")
        t += 30.0

    body = HEAD + "\n".join(ev) + "\n"
    ASS_OUT.parent.mkdir(parents=True, exist_ok=True)
    ASS_OUT.write_text(body, encoding="utf-8")
    try:
        ASS_TMP.write_text(body, encoding="utf-8")
    except OSError:
        pass
    n_asr = sum(1 for g in groups if g["method"] == "asr")
    TIMINGS.parent.mkdir(parents=True, exist_ok=True)
    TIMINGS.write_text(json.dumps({"lines": len(groups), "lines_from_asr": n_asr,
                                   "lines_proportional": len(groups) - n_asr,
                                   "words": meta}, ensure_ascii=False, indent=1),
                       encoding="utf-8")
    print(f"lines {len(groups)} · asr {n_asr} · ratio {len(groups)-n_asr} · words {len(meta)}")
    print("ass ->", ASS_OUT, ASS_OUT.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
