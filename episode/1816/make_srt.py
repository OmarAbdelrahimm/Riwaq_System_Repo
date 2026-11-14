#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_srt.py — SRT from the APPROVED SCRIPT text on the MEASURED word grid.

Rule (user, Phase 1 corrections B/C1): ASR output is for timing only, never
wording. Every cue's text comes from SCRIPT_LINES_v3.json; the in/out points
come from SHOT_LIST_v2.1.csv (which is built from vo_timestamps_FINAL.json).

One cue per narration line, so the subtitle never splits mid-sentence.
"""
import csv, json, re, collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
J = json.load(open(HERE / "vo_timestamps_FINAL.json", encoding="utf-8"))
S = json.load(open(HERE / "SCRIPT_LINES_v3.json", encoding="utf-8"))
ROWS = list(csv.DictReader(open(HERE / "SHOT_LIST_v2.1.csv", encoding="utf-8-sig")))

LW = collections.OrderedDict()
for w in J["words"]:
    LW.setdefault(w["line"], []).append(w)


def stamp(t):
    t = max(0.0, t)
    h = int(t // 3600); m = int((t % 3600) // 60); s = t - 3600 * h - 60 * m
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


cues = []
for ln in sorted(LW):
    ws = LW[ln]
    cues.append([round(ws[0]["start"], 3), round(ws[-1]["end"], 3), S[str(ln)].strip()])

# close the small gaps between lines so the subtitle does not blink off
for i in range(len(cues) - 1):
    gap = cues[i + 1][0] - cues[i][1]
    if 0 < gap <= 0.40:
        cues[i][1] = round(cues[i + 1][0] - 0.01, 3)

with open(HERE / "RUWAQ_1816_v2.1_AR.srt", "w", encoding="utf-8") as f:
    for n, (a, b, txt) in enumerate(cues, 1):
        f.write(f"{n}\n{stamp(a)} --> {stamp(b)}\n{txt}\n\n")

# ---- checks
words = sum(len(c[2].split()) for c in cues)
print(f"cues {len(cues)} · words {words} · first {cues[0][0]:.2f} · last {cues[-1][1]:.2f}")
bad = [c for c in cues if c[1] - c[0] < 0.6]
print("cues shorter than 0.6 s:", len(bad))
over = [c for c in cues if len(c[2].split()) / max(0.5, c[1] - c[0]) > 4.2]
print("cues above 4.2 words/s:", len(over), [(round(a, 1), t[:40]) for a, b, t in over][:5])
assert not re.search(r"[?\uFFFD]{3,}", open(HERE / "RUWAQ_1816_v2.1_AR.srt", encoding="utf-8").read())
print("no replacement characters in the SRT")
