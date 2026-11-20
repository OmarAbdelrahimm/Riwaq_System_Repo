#!/usr/bin/env python3
"""بوابة الشورتات: تتحقق من الإيقاع، مناطق الأمان، وحدود النص قبل أي ريندر."""
import re, sys
from pathlib import Path

W, H = 1080, 1920
SAFE = {"top": 220, "bottom": 480, "side": 64, "cap": (1210, 1360)}
FPS = 30
problems = []

SHORTS = {
    "ShortA": {"file": "src/compositions/shorts/ShortA.tsx", "target": (30, 32)},
    "ShortB": {"file": "src/compositions/shorts/ShortB.tsx", "target": (32, 34)},
}

# حدود من brand.json
MAX_CHARS_AR = 28
MAX_LINES = 2

for name, cfg in SHORTS.items():
    src = Path(cfg["file"]).read_text()

    # ── 1. المدة ──
    total = None
    m = re.search(r"const TOTAL = (\d+) \* FPS", src)
    if m:
        total = int(m.group(1)) * FPS
    if total is None:
        problems.append(f"{name}: مش قادر أحدد TOTAL")
    else:
        secs = total / FPS
        lo, hi = cfg["target"]
        if not (lo <= secs <= hi):
            problems.append(f"{name}: المدة {secs:.1f}s خارج النطاق {lo}–{hi}s")

    # ── 2. البيوت والمجموع ──
    beats = re.findall(r"\{ at: (\d+), dur: (\d+)", src)
    if not beats:
        problems.append(f"{name}: مفيش BEATS")
        continue
    beats = [(int(a), int(d)) for a, d in beats]

    # ترتيب متصل بدون فراغ
    expect = 0
    for i, (at, dur) in enumerate(beats):
        if at != expect:
            problems.append(f"{name}: فجوة/تراكب عند اللقطة {i+1} — متوقع {expect} وجاي {at}")
        expect = at + dur
    if total and expect != total:
        problems.append(f"{name}: مجموع اللقطات {expect} ≠ TOTAL {total}")

    # ── 3. إيقاع القطع أسرع من الطويل (3.5–6.0s) ──
    for i, (at, dur) in enumerate(beats):
        s = dur / FPS
        if s > 6.0:
            problems.append(f"{name}: اللقطة {i+1} طولها {s:.1f}s — أبطأ من الطويل نفسه")
        if s < 0.8:
            problems.append(f"{name}: اللقطة {i+1} طولها {s:.2f}s — أسرع من إن العين تلمح")

    avg = sum(d for _, d in beats) / len(beats) / FPS
    if avg > 3.0:
        problems.append(f"{name}: متوسط القطع {avg:.2f}s — لازم يبقى أسرع من كده")

    # ── 4. النصوص جوه مناطق الأمان ──
    for m2 in re.finditer(r'(?:BigTitle|BigNumber|KeyLine)[^>]*?from=\{[^}]*\}[^>]*?(?:y|bottom)=\{(\d+)\}', src):
        y = int(m2.group(1))
        if y < SAFE["top"] or y > H - SAFE["bottom"]:
            problems.append(f"{name}: نص عند y={y} خارج منطقة الأمان ({SAFE['top']}–{H - SAFE['bottom']})")

    # ── 5. طول السطور ──
    for m3 in re.finditer(r'text="([^"]+)"', src):
        t = m3.group(1)
        for line in t.split("\\n"):
            if len(line) > MAX_CHARS_AR:
                problems.append(f"{name}: سطر «{line[:24]}» فيه {len(line)} حرف > {MAX_CHARS_AR}")

# ── 6. الصوت لازم يكون مركّب ──
for name, cfg in SHORTS.items():
    src = Path(cfg["file"]).read_text()
    if "vo/short" not in src:
        problems.append(f"{name}: مفيش VO مركّب — شورت من غير صوت مش جاهز للنشر")

print()
if problems:
    print("\n".join("❌ " + p for p in problems))
    sys.exit(1)
print("✅ الشورتات سليمة — إيقاع أسرع من الطويل، ونصوص جوه الأمان")
