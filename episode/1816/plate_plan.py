#!/usr/bin/env python3
"""Per-chapter plate plan for v2.2.
A shot needs a generated plate only if it is NOT in the motion layer.
The motion layer is graphic_space: DATA, BOARD, THREAD, MAP, DOC, END."""
import csv, collections, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
rows=list(csv.DictReader(open(HERE/"SHOT_LIST_v2.2.csv",encoding="utf-8-sig")))
GEN=collections.OrderedDict()
for r in rows:
    GEN.setdefault(r["chapter"],{"plates":0,"graphic":0,"sec_plates":0.0,"types":collections.Counter()})
    g=r["space_kind"]=="graphic_space"
    GEN[r["chapter"]]["graphic" if g else "plates"]+=1
    if not g: GEN[r["chapter"]]["sec_plates"]+=float(r["dur"])
    GEN[r["chapter"]]["types"][r["shot_type"]]+=1
tot=collections.Counter(); tsec=0.0
print(f"{'ch':<3}{'shots':>6}{'plates':>7}{'graphic':>8}{'plate sec':>10}")
for ch,v in GEN.items():
    n=v["plates"]+v["graphic"]
    print(f"{ch:<3}{n:>6}{v['plates']:>7}{v['graphic']:>8}{v['sec_plates']:>10.1f}")
    tot["plates"]+=v["plates"]; tot["graphic"]+=v["graphic"]; tsec+=v["sec_plates"]
print(f"{'ALL':<3}{tot['plates']+tot['graphic']:>6}{tot['plates']:>7}{tot['graphic']:>8}{tsec:>10.1f}")
print("\nshare needing a generated plate: %.1f%%" % (tot['plates']/len(rows)*100))
print("graphic (motion layer): %.1f%%" % (tot['graphic']/len(rows)*100))
if len(sys.argv)>1:
    per=float(sys.argv[1])
    print(f"\nat {per:.1f} min per plate (measured, 2 vCPU):")
    for ch,v in GEN.items():
        print(f"  chapter {ch}: {v['plates']:>2} plates -> {v['plates']*per/60:5.2f} h")
    print(f"  TOTAL: {tot['plates']} plates -> {tot['plates']*per/60:.1f} h")
