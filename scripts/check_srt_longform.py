#!/usr/bin/env python3
"""فحص جودة SRT — يمنع رفع ملف كابشنز مكسور."""
import re, sys

def parse(fn):
    out = []
    for b in open(fn, encoding="utf-8").read().strip().split("\n\n"):
        L = b.split("\n")
        if len(L) < 2: continue
        m = re.match(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)", L[1])
        if not m: continue
        g = [int(x) for x in m.groups()]
        out.append((int(L[0]),
                    g[0]*3600+g[1]*60+g[2]+g[3]/1000,
                    g[4]*3600+g[5]*60+g[6]+g[7]/1000,
                    "\n".join(L[2:])))
    return out

ar = parse("outputs/CAPTIONS_AR_TMB_001_LONGFORM.srt")
en = parse("outputs/CAPTIONS_EN_TMB_001_LONGFORM.srt")
fails = []

if [c[0] for c in ar] != list(range(1, len(ar)+1)):
    fails.append("ترقيم غير متسلسل")

for i in range(len(ar)-1):
    if ar[i][2] > ar[i+1][1] + 0.01:
        fails.append(f"تداخل بين #{ar[i][0]} و#{ar[i+1][0]}")

for c in ar:
    d = c[2]-c[1]
    if d < 0.4:  fails.append(f"#{c[0]} قصير جدًا ({d:.2f}s)")
    if d > 8.0:  fails.append(f"#{c[0]} طويل جدًا ({d:.2f}s)")
    cps = len(c[3].replace("\n"," "))/max(d,0.01)
    if cps > 22: fails.append(f"#{c[0]} سريع ({cps:.1f} ح/ث)")
    for line in c[3].split("\n"):
        if len(line) > 28: fails.append(f"#{c[0]} سطر > 28 حرف")

if len(en) != len(ar):
    fails.append(f"تطابق AR/EN: {len(ar)} ≠ {len(en)}")

print(f"AR: {len(ar)} cue · EN: {len(en)} cue · ينتهي {ar[-1][2]:.1f}s")
if fails:
    print(f"\n❌ {len(fails)} مشكلة:")
    for f in fails[:20]: print("  ·", f)
    sys.exit(1)
print("✅ كل الفحوصات ناجحة")
