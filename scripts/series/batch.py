"""دفعة إعادة الرندر: الكابشن v4 على كل الفيديوهات الطويلة والشورتس.

- الطويل: الأساس = الماستر الحالي (الذي فيه الكابشن القديم) ثم delogo + زجاج جديد + كابشن v4 + مؤثرات.
- الشورت: نفس الشيء بالهندسة الرأسية.
- الترتيب مهم: تشغيل متسلسل لتفادي ضغط الذاكرة (كل ffmpeg يصل ~2GB).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

import graphics as G
import recap as R

DRIVE = R.DRIVE
OUT = R.OUT
SRT = f"{R.REPO}/outputs/SERIES_RIWAQ"

# (رقم الحلقة، العنوان للماستـر، الحلقة التالية، ملف الأساس، ملف الترجمة)
LONG = [
    (2, "المقارنة أداة لا معيار", "النهايات في العلاقات",
     f"{DRIVE}/الفيديو 02 — المقارنة أداة لا معيار (ماستر).mp4", f"{SRT}/003/CAPTIONS_AR.srt"),
    (3, "النهايات في العلاقات", "الشيطان يجري مجرى الدم",
     f"{DRIVE}/الفيديو 03 — النهايات في العلاقات (ماستر).mp4", f"{SRT}/004/CAPTIONS_AR.srt"),
    (4, "الشيطان يجري مجرى الدم", "من يقود سيارتك؟ منظومة العلاقات",
     f"{DRIVE}/الفيديو 04 — الشيطان يجري مجرى الدم (ماستر).mp4", f"{SRT}/NEW/EP04/CAPTIONS_AR.srt"),
    (5, "من يقود سيارتك؟ منظومة العلاقات", "الرأي ليس الحقيقة: النقد بلا جرح",
     f"{DRIVE}/الفيديو 05 — من يقود سيارتك؟ منظومة العلاقات (ماستر).mp4", f"{SRT}/NEW/EP05/CAPTIONS_AR.srt"),
    (6, "الرأي ليس الحقيقة: النقد بلا جرح", None,
     f"{DRIVE}/الفيديو 06 — الرأي ليس الحقيقة النقد بلا جرح (ماستر).mp4", f"{SRT}/NEW/EP06/CAPTIONS_AR.srt"),
]
TOTAL = 6

SHORTS = [f"S{i:02d}" for i in range(2, 10)]


def dur_of(path: str) -> float:
    p = subprocess.run([R.FF, "-hide_banner", "-i", path], capture_output=True, text=True)
    for line in p.stderr.splitlines():
        if "Duration:" in line:
            t = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = t.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(f"no duration: {path}")


def build_manifest() -> dict:
    return {"long": [], "shorts": []}


def main() -> None:
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    only = set(sys.argv[2:])          # e.g. batch.py long 04 05 06   /  batch.py shorts S03 S04
    man = build_manifest()
    os.makedirs(OUT, exist_ok=True)

    if which in ("all", "long"):
        for order, title, nxt, base, srt in LONG:
            if only and f"{order:02d}" not in only:
                continue
            dur = dur_of(base)
            ec = G.endcard(order, TOTAL, nxt)
            meta = {"key": f"{order:02d}", "base": base, "audio": base, "srt": srt,
                    "dur": dur, "order": order, "total": TOTAL, "next": nxt,
                    "endcard": ec}
            out = f"{OUT}/MASTER_EP{order:02d}_CAPFIX.mp4"
            print(f"\n=== long {order:02d}  dur={dur:.2f}  srt={os.path.basename(srt)}", flush=True)
            R.render_h(base, base, srt, out, meta=meta)
            man["long"].append({"order": order, "title": title, "path": out,
                                "dur": round(dur, 2), "src": base})
            json.dump(man, open(f"{OUT}/MANIFEST.json", "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)

    if which in ("all", "shorts"):
        for s in SHORTS:
            if only and s not in only:
                continue
            base = f"{SRT}/SHORTS/{s}/MASTER_FINAL_{s}.mp4"
            srt = f"{SRT}/SHORTS/{s}/CAPTIONS_AR.srt"
            dur = dur_of(base)
            out = f"{OUT}/{s}_CAPFIX.mp4"
            print(f"\n=== short {s}  dur={dur:.2f}", flush=True)
            R.render_v(base, srt, out, dur)
            man["shorts"].append({"id": s, "path": out, "dur": round(dur, 2), "src": base})
            json.dump(man, open(f"{OUT}/MANIFEST.json", "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)

    print("\nBATCH_DONE", which, flush=True)


if __name__ == "__main__":
    main()
