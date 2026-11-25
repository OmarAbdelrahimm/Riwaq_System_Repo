#!/usr/bin/env python3
"""make_subs.py — ترجمات SRT للطويل والشورت (AR من captions.data، EN من en_sentences.py).
AR: يستخدم دوال scripts/make_srt.py (≤28 حرفًا × سطرين + عزل اللاتيني BiDi).
EN: جملة لكل مقطع (≤42 حرفًا × سطرين)، موزّعة زمنيًا على توقيت كلمات الجملة العربية المقابلة.
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); EPDIR = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(EPDIR, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts")); sys.path.insert(0, HERE)
from make_srt import ts, isolate_latin  # noqa: E402
from en_sentences import EN_LONG, EN_SHORT  # noqa: E402
EP = "WHAT_IF_BAGHDAD_NEVER_FELL"
OUT = os.path.join(ROOT, "exports", EP, "subtitles")
EN_MAX = 42

def wrap(text, n):
    lines, cur = [], ""
    for w in text.split():
        c = (cur + " " + w).strip()
        if len(c) <= n or not cur: cur = c
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def split_en(text):
    """يقسم النص الإنجليزي إلى مقاطع كل منها ≤ سطرين × 42."""
    if len(wrap(text, EN_MAX)) <= 2: return [text]
    parts = re.split(r"(?<=[,:;…])\s+", text)
    chunks, cur = [], ""
    for p in parts:
        c = (cur + " " + p).strip()
        if len(wrap(c, EN_MAX)) <= 2: cur = c
        else:
            if cur: chunks.append(cur)
            cur = p
            while len(wrap(cur, EN_MAX)) > 2:  # جزء طويل بلا فواصل
                ws = cur.split(); half = len(ws) // 2
                chunks.append(" ".join(ws[:half])); cur = " ".join(ws[half:])
    if cur: chunks.append(cur)
    return chunks

def sentences(words):
    out, buf = [], []
    for w in words:
        if buf and w.get("scene") != buf[0].get("scene"): out.append(buf); buf = []
        buf.append(w)
        if re.search(r"[.؟?!]»?\)?$|[.؟?!]»\.$", w["w"]): out.append(buf); buf = []
    if buf: out.append(buf)
    return out

def en_cues(spans, texts, total):
    assert len(spans) == len(texts), (len(spans), len(texts))
    cues = []
    for (a, b), t in zip(spans, texts):
        ch = split_en(t); L = sum(len(c) for c in ch); x = a
        for c in ch:
            d = (b - a) * len(c) / L
            cues.append([x, x + d, c]); x += d
    for c in cues:
        c[0] = max(0, c[0] - 0.08)
    for i, c in enumerate(cues):
        nxt = cues[i + 1][0] - 0.04 if i + 1 < len(cues) else total
        c[1] = min(max(c[1] + 0.25, c[0] + 1.2), nxt)
    return cues

def write_srt(path, cues):
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, txt) in enumerate(cues, 1):
            f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{txt}\n\n")

def main():
    os.makedirs(OUT, exist_ok=True)
    TL = json.load(open(os.path.join(EPDIR, "timeline.json"), encoding="utf-8"))
    TS = json.load(open(os.path.join(EPDIR, "timeline_short.json"), encoding="utf-8"))
    for name, meta_file in (("long", "episode_meta.json"), ("short", "episode_meta_short.json")):
        m = json.load(open(os.path.join(ROOT, "data", "projects", EP, meta_file), encoding="utf-8"))
        ar = [(c["t_in"], c["t_out"], isolate_latin(c["ar"])) for c in m["captions"]["data"]]
        suf = "" if name == "long" else "_short"
        write_srt(os.path.join(OUT, f"subtitles_ar{suf}.srt"), ar)
        if name == "long":
            spans = [(s[0]["t0"], s[-1]["t1"]) for s in sentences(TL["words"])]
            en = en_cues(spans, EN_LONG, TL["duration_s"])
        else:
            spans = [(b["vo_in"], b["vo_out"]) for b in TS["beats"]]
            en = en_cues(spans, EN_SHORT, TS["duration_s"])
        en = [(a, b, "\n".join(wrap(t, EN_MAX))) for a, b, t in en]
        write_srt(os.path.join(OUT, f"subtitles_en{suf}.srt"), en)
        short = sum(1 for a, b, _ in en if b - a < 1.2 - 1e-6)
        print(f"{name}: AR {len(ar)} cues · EN {len(en)} cues (EN <1.2s: {short})")

if __name__ == "__main__":
    main()
