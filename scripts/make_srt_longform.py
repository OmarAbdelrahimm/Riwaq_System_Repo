#!/usr/bin/env python3
"""يبني SRT من CUES_LONGFORM.py بتوقيتات مقاسة من الملفات نفسها."""
import sys, wave, os
sys.path.insert(0, "data/projects/TMB_001/vo")
from CUES_LONGFORM import CLIPS, CUES

LEAD = 0.06      # نبدأ الكابشن قبل الكلام بشوية
TAIL = 0.10      # ونخلص بعده بشوية
MAX_CHARS = 44   # سطرين × 22

def ts(t):
    if t < 0: t = 0
    h = int(t//3600); m = int((t%3600)//60); s = int(t%60)
    ms = int(round((t - int(t))*1000))
    if ms == 1000: s += 1; ms = 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def clip_dur(p):
    w = wave.open(p); d = w.getnframes()/w.getframerate(); w.close(); return d

rows, prev_end = [], -1
for idx, fn, off in CLIPS:
    p = f"public/projects/TMB_001/vo/{fn}"
    total = clip_dur(p)
    for i, (a, b, ar, en) in enumerate(CUES[idx]):
        start = off + a + LEAD
        end   = off + min(b, total) - TAIL
        # لا تداخل
        if start < prev_end + 0.02:
            start = prev_end + 0.02
        if end <= start + 0.35:
            end = start + 0.35
        prev_end = end
        rows.append((start, end, ar, en))

srt_ar, srt_en = [], []
for n, (s, e, ar, en) in enumerate(rows, 1):
    srt_ar.append(f"{n}\n{ts(s)} --> {ts(e)}\n{ar}\n")
    srt_en.append(f"{n}\n{ts(s)} --> {ts(e)}\n{en}\n")

os.makedirs("outputs", exist_ok=True)
open("outputs/CAPTIONS_AR_TMB_001_LONGFORM.srt","w",encoding="utf-8").write("\n".join(srt_ar))
open("outputs/CAPTIONS_EN_TMB_001_LONGFORM.srt","w",encoding="utf-8").write("\n".join(srt_en))

print(f"✅ {len(rows)} cue")
print(f"   AR: outputs/CAPTIONS_AR_TMB_001_LONGFORM.srt")
print(f"   EN: outputs/CAPTIONS_EN_TMB_001_LONGFORM.srt")
print(f"   آخر cue عند {ts(rows[-1][1])}")

# تحقق: طول الأسطر
bad = [ (i,a) for i,(s,e,a,en) in enumerate(rows,1) if max((len(l) for l in a.split('\n')), default=0) > 28 ]
print(f"\n⚠️  أسطر > 28 حرف: {len(bad)}")
for i,a in bad[:8]: print(f"   #{i}: {a.replace(chr(10),' / ')}")
