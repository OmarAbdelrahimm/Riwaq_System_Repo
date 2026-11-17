#!/usr/bin/env python3
"""بوابة تخطيط: تمنع نص عربي إنه يركب على صورة أو يطلع بره الكادر."""
import re, sys
from pathlib import Path

W, H = 1920, 1080
MARGIN = 40
src = Path("src/compositions/longform/scenes.tsx").read_text()
parts = re.split(r"/\* ═══ (\d+) ·", src)
problems = []

def num(pat, seg, default=None):
    m = re.search(pat, seg)
    return int(m.group(1)) if m else default

for k in range(1, len(parts), 2):
    i, body = parts[k], parts[k + 1]

    plates = []
    for m in re.finditer(r'<DepthBox x=\{(-?\d+)\} y=\{(-?\d+)\} z=\{[^}]*\} w=\{(\d+)\} h=\{(\d+)\}', body):
        cx, cy, w, h = map(int, m.groups())
        plates.append((cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2))

    # كل <div ... style={{ ... }}> فيه direction: rtl
    for m in re.finditer(r'<div\s+style=\{\{(.*?)\}\}\s*>', body, re.S):
        st = m.group(1)
        if 'direction: "rtl"' not in st:
            continue
        if 'position: "absolute"' not in st:
            continue  # عمود نسبي — يورث من الأب
        w = num(r'width:\s*(\d+)', st)
        if not w:
            continue
        right, left, sid = num(r'right:\s*(\d+)', st), num(r'left:\s*(\d+)', st), None
        if right is not None:
            a = W - right - w
        elif left is not None:
            a = left
        else:
            continue
        b = a + w
        if a < MARGIN or b > W - MARGIN:
            problems.append(f"S{i}: عمود نص {a}..{b} خارج الكادر")
        for pl, pt, pr, pb in plates:
            if a < pr and b > pl:
                ov = min(b, pr) - max(a, pl)
                if ov > 60:
                    problems.append(f"S{i}: نص {a}..{b} يركب على صورة {pl}..{pr} — تداخل {ov}px")

    for m in re.finditer(r'<TextRail side="(left|right)" top=\{(\d+)\} width=\{(\d+)\}', body):
        side, top, w = m.group(1), int(m.group(2)), int(m.group(3))
        a = 76 if side == "left" else W - 76 - w
        b = a + w
        if a < MARGIN or b > W - MARGIN:
            problems.append(f"S{i}: TextRail {a}..{b} خارج الكادر")
        for pl, pt, pr, pb in plates:
            if a < pr and b > pl:
                ov = min(b, pr) - max(a, pl)
                if ov > 60:
                    problems.append(f"S{i}: TextRail {a}..{b} يركب على صورة {pl}..{pr} — تداخل {ov}px")

if problems:
    print("\n".join("❌ " + p for p in problems))
    sys.exit(1)
# 3) نصوص فوق الصور (title cards) لازم يكون معاها طبقة تعتيم أو ظل قوي
for k in range(1, len(parts), 2):
    i, body = parts[k], parts[k + 1]
    for m in re.finditer(r'<AbsoluteFill[^>]*alignItems: "center"[^>]*>(.*?)</AbsoluteFill>', body, re.S):
        blk = m.group(1)
        if "fontFamily" not in blk: continue
        # لو المشهد كله مفيهوش PhotoCard، يبقى النص على خلفية مجردة — آمن
        if "PhotoCard" not in body:
            continue
        if ("radial-gradient" in blk or "rgba(0,0,0,1)" in blk
                or "background:" in blk or "backdropFilter" in blk):
            continue
        problems.append(f"S{i}: نص mid-screen فوق صورة بدون طبقة تعتيم — مش هيبان")

if problems:
    print("\n".join("❌ " + p for p in problems)); sys.exit(1)
print("✅ التخطيط سليم — مفيش تراكب نص/صورة، والنصوص فوق الصور مقروءة")
