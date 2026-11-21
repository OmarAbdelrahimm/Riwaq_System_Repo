#!/usr/bin/env python3
"""بوابة تخطيط: تمنع نص عربي إنه يركب على صورة أو يطلع بره الكادر."""
import re, sys
from pathlib import Path

W, H = 1920, 1080
MARGIN = 40
src = Path("src/compositions/longform/scenes.tsx").read_text()
parts = re.split(r"/\* ═══ (\d+) ·", src)
problems = []

# 0) لازم الـ13 مشهد كلهم موجودين — التقسيم بيعتمد على التعليقات
_sec = [int(parts[k]) for k in range(1, len(parts), 2)]
if _sec != list(range(1, 14)):
    problems.append(f"تعليقات المشاهد ناقصة/مكررة: {_sec} (المتوقع 1..13)")

def num(pat, seg, default=None):
    m = re.search(pat, seg)
    return int(m.group(1)) if m else default

for k in range(1, len(parts), 2):
    i, body = parts[k], parts[k + 1]

    plates = []
    # scrims أفقية: بتغطي منطقة وتخلي النص مقروء فوق الصورة
    scrims = []
    for m in re.finditer(r'width:\s*(\d+),\s*height:\s*(\d+),\s*background:\s*`linear-gradient\((\d+)deg', body):
        sw, sh, ang = map(int, m.groups())
        if ang in (90, 270):
            scrims.append((0, sw))

    for m in re.finditer(r'<DepthBox x=\{(-?\d+)\} y=\{(-?\d+)\} z=\{[^}]*\} w=\{(\d+)\} h=\{(\d+)\}', body):
        cx, cy, w, h = map(int, m.groups())
        # الصورة اللي بتغطي الكادر كله مش "عائق" — النص لازم يقع عليها
        if w >= W and h >= H - 20:
            continue
        plates.append((cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2))

    # كل <div ... style={{ ... }}> فيه direction: rtl
    for m in re.finditer(r'<div\s+style=\{\{(.*?)\}\}\s*>', body, re.S):
        st = m.group(1)
        if 'direction: "rtl"' not in st:
            continue
        if 'position: "absolute"' not in st:
            continue  # عمود نسبي — يورث من الأب
        # الـscrims مش نصوص — دي طبقات تعتيم خلف النص
        if 'pointerEvents: "none"' in st or 'gradient(' in st:
            continue
        # لازم يكون نص فعلاً: textAlign أو fontFamily أو fontSize
        if not any(k in st for k in ('textAlign:', 'fontFamily:', 'fontSize:')):
            continue
        w = num(r'width:\s*(\d+)', st)
        if not w:
            continue
        # لازم يكون له موضع صريح (top/right/left) — وإلا ده container مش نص
        if 'top:' not in st and 'bottom:' not in st:
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
        # لو النص جوه منطقة scrim → مقروء، مش مشكلة
        covered = any(a >= s0 - 10 and b <= s1 + 10 for s0, s1 in scrims)
        for pl, pt, pr, pb in plates:
            if a < pr and b > pl and not covered:
                ov = min(b, pr) - max(a, pl)
                if ov > 60:
                    problems.append(f"S{i}: نص {a}..{b} يركب على صورة {pl}..{pr} — تداخل {ov}px (مفيش scrim)")

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
# 2.5) نص عريض في عمود ضيق → هيلف ويكسر الكلمة
AR_W = 0.52  # متوسط عرض الحرف العربي في Amiri Bold ≈ 0.52em
for k in range(1, len(parts), 2):
    i, body = parts[k], parts[k + 1]
    # اجمع الأحجام الكبيرة في هذا المشهد
    big = [int(x) for x in re.findall(r'fontSize: (\d+)', body) if int(x) >= 60]
    widths = [int(w) for w in re.findall(r'width=\{(\d+)\}', body)]
    widths += [int(w) for w in re.findall(r'width: (\d+)', body)]
    if not big or not widths: continue
    avail = max(widths)
    for fs in big:
        # ابحث عن أطول سطر عربي في المشهد
        pass
    # فحص بسيط: أطول كلمة عربية × حجم الخط
    for m in re.finditer(r'>([^<>{}]*[\u0600-\u06FF][^<>{}]*)<', body):
        txt = m.group(1).strip()
        if not txt or "&" in txt: continue
        words = txt.split()
        if len(words) < 4: continue          # عناوين حقيقية بس
        word = max(words, key=len)
        if len(word) < 6: continue
        for fs in big:
            need = len(word) * fs * AR_W
            if need > avail * 0.95:
                problems.append(
                    f"S{i}: «{word[:18]}» بحجم {fs}px محتاج {int(need)}px والعمود {avail}px — هيكسر السطر")
                break

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
