#!/usr/bin/env python3
"""
ترقية مزامنة PARADOX_012 إلى دقة Whisper (اختياري — يُشغَّل محليًا)

المزامنة الحالية في timestamps_paradox.json حقيقية ومبنية على ترجمات المصدر
المدمجة + محاذاة على موجة الصوت. هذا السكربت يعيد توليد نفس الملف بطوابع
كلمات من faster-whisper لمن أراد دقة أعلى قبل النشر.

المتطلبات (نفس خط إنتاج النظام):
    pip install faster-whisper
التشغيل:
    python scripts/sync_paradox_whisper.py [--model small]
يقرأ:  public/projects/PARADOX_012/audio/voice.wav
يكتب:  public/projects/PARADOX_012/timestamps_paradox.json (بنفس البنية)
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO = os.path.join(ROOT, "public/projects/PARADOX_012/audio/voice.wav")
OUT = os.path.join(ROOT, "public/projects/PARADOX_012/timestamps_paradox.json")
FPS = 30
S1_END, S2_END = 86.36, 127.52


def scene_of(t: float) -> int:
    return 1 if t < S1_END else (2 if t < S2_END else 3)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="small", help="حجم نموذج faster-whisper")
    args = ap.parse_args()

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("faster-whisper غير مثبّت: pip install faster-whisper", file=sys.stderr)
        return 1

    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        AUDIO, language="ar", word_timestamps=True, vad_filter=True
    )

    words = []
    for seg in segments:
        for w in seg.words or []:
            words.append({"word": w.word.strip(), "start": w.start, "end": w.end})
    words = [w for w in words if w["word"]]

    for w in words:
        w["sf"] = int(round(w["start"] * FPS))
        w["ef"] = int(round(w["end"] * FPS))
    for i in range(len(words)):
        if i and words[i]["sf"] <= words[i - 1]["ef"]:
            words[i]["sf"] = words[i - 1]["ef"] + 1
        if words[i]["ef"] < words[i]["sf"] + 1:
            words[i]["ef"] = words[i]["sf"] + 1

    frags, cur = [], []
    for w in words:
        if cur:
            gap = w["start"] - cur[-1]["end"]
            if (
                gap >= 0.45
                or len(cur) >= 9
                or (w["end"] - cur[0]["start"]) > 5.5
                or scene_of(w["start"]) != scene_of(cur[0]["start"])
            ):
                frags.append(cur)
                cur = []
        cur.append(w)
    if cur:
        frags.append(cur)

    old = json.load(open(OUT, encoding="utf-8"))
    old["meta"]["sync_status"] = "REAL_SYNC_WHISPER"
    old["meta"]["sync_method"] = f"faster-whisper {args.model} word_timestamps (local run)"
    old["fragments"] = [
        {
            "segment_id": i + 1,
            "text": " ".join(w["word"] for w in fr),
            "start_frame": fr[0]["sf"],
            "end_frame": fr[-1]["ef"],
            "scene": scene_of(fr[0]["start"]),
            "words": [
                {"word": w["word"], "start_frame": w["sf"], "end_frame": w["ef"]}
                for w in fr
            ],
        }
        for i, fr in enumerate(frags)
    ]
    json.dump(old, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"done: {len(words)} words, {len(frags)} fragments, lang={info.language}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
