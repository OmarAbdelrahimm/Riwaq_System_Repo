#!/usr/bin/env python3
"""make_srt.py — توليد كابشنز AR/EN من episode_meta.json
القواعد: سطران أقصى · حد الأحرف من إعداد المشروع (28 افتراضيًا) · عزل النص اللاتيني (BiDi)
"""
import json, os, re, sys

MAX_CHARS = 28
MAX_LINES = 2

def ts(sec: float) -> str:
    ms = int(round((sec - int(sec)) * 1000)); s = int(sec)
    m, s = divmod(s, 60); h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def wrap_ar(text: str, max_chars: int = MAX_CHARS, max_lines: int = MAX_LINES):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        cand = (cur + " " + w).strip()
        if len(cand) <= max_chars or not cur:
            cur = cand
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    if len(lines) > max_lines:  # دمج الزائد في السطر الأخير (بدل فقد النص)
        lines = lines[:max_lines - 1] + [" ".join(lines[max_lines - 1:])]
    return "\n".join(lines)

def isolate_latin(text: str) -> str:
    # عزل المقاطع اللاتينية بعلامات اتجاه (Unicode BiDi isolates)
    return re.sub(r"([A-Za-z][A-Za-z0-9 .&\-]*)", "\u2066\\1\u2069", text)

def build(meta_path: str, out_dir: str):
    meta = json.load(open(meta_path, encoding="utf-8"))
    pid = meta["project"]["id"]
    captions = meta.get("captions") or {}
    lines = captions.get("data") or []
    rules = captions.get("rules") or {}
    max_chars = int(rules.get("max_chars_ar", MAX_CHARS))
    max_lines = int(rules.get("max_lines", MAX_LINES))
    if not lines:
        print("لا كابشنز في episode_meta.json"); return
    os.makedirs(out_dir, exist_ok=True)
    ar_path = os.path.join(out_dir, f"CAPTIONS_AR_{pid}.srt")
    en_path = os.path.join(out_dir, f"CAPTIONS_EN_{pid}.srt")

    warn = []
    english_lines = [ln for ln in lines if ln.get("en")]
    ar_cues = []
    ia = 0
    for ln in lines:
        dur = ln["t_out"] - ln["t_in"]
        if dur < 1.2:
            warn.append(f"مدة قصيرة ({dur:.2f}s): {ln.get('ar', '')[:24]}…")
        if ln.get("ar"):
            ia += 1
            ar_cues.append(
                f"{ia}\n{ts(ln['t_in'])} --> {ts(ln['t_out'])}\n"
                f"{isolate_latin(wrap_ar(ln['ar'], max_chars=max_chars, max_lines=max_lines))}"
            )
    with open(ar_path, "w", encoding="utf-8") as fa:
        fa.write("\n\n".join(ar_cues) + "\n")
    ie = 0
    if english_lines:
        en_cues = []
        for ln in english_lines:
            ie += 1
            en_cues.append(f"{ie}\n{ts(ln['t_in'])} --> {ts(ln['t_out'])}\n{ln['en']}")
        with open(en_path, "w", encoding="utf-8") as fe:
            fe.write("\n\n".join(en_cues) + "\n")
        print(f"✔ {ar_path} ({ia}) · {en_path} ({ie})")
    else:
        if os.path.exists(en_path):
            os.remove(en_path)
        print(f"✔ {ar_path} ({ia}) · لا يوجد SRT إنجليزي")
    for w in warn[:8]:
        print("  ⚠", w)

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "data/projects/GOLDEN_001/episode_meta.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "outputs"
    build(src, out)
