#!/usr/bin/env python3
"""Align the VO clips to script text without an STT model.

Method (approximate, documented in qa_report):
1. Detect silences in each clip (RMS 10ms, threshold = peak-40dB, ≥0.12s).
2. Map script letters (no spaces/diacritics/punctuation) linearly onto the voiced time.
3. Strong boundaries (scene breaks, . ؟ ! … : ؛) snap to the nearest silence via DP (order-preserving).
4. Commas and words are interpolated inside the anchored segments.
5. Apply the tempo factor (atempo, pitch preserved) and lay clips on a global timeline.

Output: timeline.json (scenes, cues ≤2×28 chars, approximate word timestamps).
"""
import json, re, sys, pathlib
import numpy as np, soundfile as sf

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXP = ROOT.parents[1] / "exports" / ROOT.name
HARAKAT = re.compile(r"[\u064B-\u0652\u0670\u0640]")
STRONG = set(".؟?!…:؛;")


def letters(s):
    return len(re.sub(r"[^\w]", "", HARAKAT.sub("", s)))


def silences(x, sr, thr_db=-35, min_s=0.12, merge_gap=0.09):
    hop = int(sr * 0.01); n = len(x) // hop
    r = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12)
    db = 20 * np.log10(r); s = db < db.max() + thr_db
    out = []; i = 0
    while i < n:
        if s[i]:
            j = i
            while j < n and s[j]: j += 1
            if (j - i) * 0.01 >= min_s or i == 0 or j == n: out.append((i * 0.01, j * 0.01))
            i = j
        else:
            i += 1
    raw = []
    i = 0
    # merge fragments separated by tiny voiced blips, then filter by length
    hop_s = 0.01; segs = []
    k = 0
    while k < n:
        if s[k]:
            j = k
            while j < n and s[j]: j += 1
            segs.append([k * hop_s, j * hop_s]); k = j
        else: k += 1
    merged = []
    for a, b in segs:
        if merged and a - merged[-1][1] <= merge_gap: merged[-1][1] = b
        else: merged.append([a, b])
    out = [(a, b) for a, b in merged if b - a >= min_s or a == 0 or abs(b - n * hop_s) < 1e-6]
    return out, len(x) / sr


def tokenize(scenes_text):
    """Return list of (scene_idx, token, strong_after) with tokens = words."""
    toks = []
    for si, t in enumerate(scenes_text):
        words = t.split()
        for wi, w in enumerate(words):
            last = wi == len(words) - 1
            strong = last or (w[-1] in STRONG) or w.endswith("…")
            toks.append({"scene": si, "w": w, "strong": strong, "scene_end": last})
    return toks


def align_clip(path, scenes_text):
    x, sr = sf.read(path)
    if x.ndim > 1: x = x.mean(1)
    sil, dur = silences(x, sr)
    on = sil[0][1] if sil and sil[0][0] == 0 else 0.0
    off = sil[-1][0] if sil and abs(sil[-1][1] - dur) < 0.02 else dur
    inner = [s for s in sil if s[0] > on + 0.05 and s[1] < off - 0.05]
    # voiced map
    segs = []; cur = on
    for a, b in inner:
        segs.append((cur, a)); cur = b
    segs.append((cur, off))
    vtot = sum(b - a for a, b in segs)
    def v2t(v):
        acc = 0
        for a, b in segs:
            if acc + (b - a) >= v: return a + (v - acc)
            acc += b - a
        return off
    toks = tokenize(scenes_text)
    L = [letters(t["w"]) for t in toks]; tot = sum(L); cum = np.cumsum(L)
    est_end = [v2t(c / tot * vtot) for c in cum]
    # DP: assign strong boundaries (except final) to silences in order
    B = [i for i, t in enumerate(toks) if t["strong"] and i < len(toks) - 1]
    N = len(inner); INF = 1e9
    cen = [(a + b) / 2 for a, b in inner]
    # cost[i][j]: boundaries[:i] assigned with last silence < j; allow boundary unassigned with penalty
    UNASSIGNED = 0.9
    dp = np.full((len(B) + 1, N + 1), INF); dp[0, :] = 0; back = {}
    for i in range(1, len(B) + 1):
        for j in range(0, N + 1):
            # option unassigned
            best = dp[i - 1, j] + UNASSIGNED * (2.5 if toks[B[i - 1]]["scene_end"] else 1.0); arg = (i - 1, j, None)
            if j > 0:
                c = abs(cen[j - 1] - est_end[B[i - 1]])
                if c < 2.5:
                    v = dp[i - 1, j - 1] + c
                    if v < best: best, arg = v, (i - 1, j - 1, j - 1)
                # carry: silence j-1 skipped
                if dp[i, j - 1] < best: best, arg = dp[i, j - 1], (i, j - 1, "skip")
            dp[i, j] = best; back[(i, j)] = arg
    assign = {}; i, j = len(B), N
    while i > 0:
        pi, pj, s = back[(i, j)]
        if s == "skip": j = pj; continue
        if s is not None: assign[B[i - 1]] = s
        i, j = pi, pj
    # anchors: token index -> (end_time, next_start)
    anchors = [(-1, on, on)]
    for ti in sorted(assign):
        a, b = inner[assign[ti]]; anchors.append((ti, a, b))
    anchors.append((len(toks) - 1, off, off))
    # interpolate words between anchors
    for k in range(len(anchors) - 1):
        t0i, _, start = anchors[k]; t1i, end, _ = anchors[k + 1]
        idx = list(range(t0i + 1, t1i + 1))
        lw = [L[q] for q in idx]; s = sum(lw) or 1; acc = 0
        for q, l in zip(idx, lw):
            toks[q]["t0"] = start + (end - start) * acc / s; acc += l
            toks[q]["t1"] = start + (end - start) * acc / s
    stats = {"silences": N, "strong": len(B), "snapped": len(assign), "dur": dur, "on": on, "off": off}
    return toks, stats


def build_cues(toks, max_chars=28, max_lines=2):
    """Split into cues: break at strong punctuation, commas, or when exceeding 2×28 chars."""
    cues = []; cur = []
    def flush():
        if cur:
            cues.append(cur.copy()); cur.clear()
    for t in toks:
        cand = " ".join(x["w"] for x in cur + [t])
        if cur and (len(HARAKAT.sub("", cand)) > max_chars * max_lines - 4 or cur[-1]["scene"] != t["scene"]):
            # try to break at last comma inside cur
            flush()
        cur.append(t)
        if t["strong"] or (t["w"].endswith("،") and len(" ".join(x["w"] for x in cur)) > 30):
            flush()
    flush()
    return cues


def wrap(text, max_chars=28):
    words = text.split(); lines = [""]
    for w in words:
        c = (lines[-1] + " " + w).strip()
        if len(HARAKAT.sub("", c)) <= max_chars or not lines[-1]: lines[-1] = c
        else: lines.append(w)
    if len(lines) > 2: lines = [lines[0], " ".join(lines[1:])]
    return lines


def main():
    meta = json.loads((ROOT / "script_scenes.json").read_text(encoding="utf-8"))
    cfg = json.loads((ROOT / "tools" / "audio_cfg.json").read_text(encoding="utf-8"))
    tempo = cfg["tempo"]; gap = cfg["gap_between_clips_s"]; head = cfg["head_s"]
    scenes = meta["scenes"]; out = {"tempo": tempo, "clips": [], "scenes": [], "cues": [], "words": []}
    t = head
    for gi, grp in enumerate(cfg["groups"]):
        st = [scenes[int(s) - 1]["text"].replace("ـ", "") for s in grp]
        toks, stats = align_clip(str(EXP / "vo" / f"G{gi + 1:02d}.wav"), st)
        base = t - stats["on"] / tempo
        clip_len = (stats["off"] - stats["on"]) / tempo
        out["clips"].append({"file": f"G{gi + 1:02d}.wav", "src_in": stats["on"], "src_out": stats["off"], "t_in": t, "t_out": t + clip_len, **stats})
        for q in toks:
            q["T0"] = base + q["t0"] / tempo; q["T1"] = base + q["t1"] / tempo; q["sid"] = grp[q["scene"]]
            out["words"].append({"w": q["w"], "t0": round(q["T0"], 3), "t1": round(q["T1"], 3), "scene": q["sid"]})
        for si, sid in enumerate(grp):
            ws = [q for q in toks if q["scene"] == si]
            out["scenes"].append({"id": sid, "vo_in": round(ws[0]["T0"], 3), "vo_out": round(ws[-1]["T1"], 3)})
        for c in build_cues(toks):
            text = " ".join(q["w"] for q in c)
            out["cues"].append({"t_in": round(c[0]["T0"], 3), "t_out": round(c[-1]["T1"], 3), "text": text, "lines": wrap(text), "scene": c[0]["sid"]})
        t += clip_len + gap
    total = t - gap + cfg["tail_s"]
    # visual scene boundaries: midpoint of gap between VO segments
    sc = out["scenes"]
    for i, s in enumerate(sc):
        s["t_in"] = 0.0 if i == 0 else round((sc[i - 1]["vo_out"] + s["vo_in"]) / 2, 3)
    for i, s in enumerate(sc):
        s["t_out"] = round(total, 3) if i == len(sc) - 1 else sc[i + 1]["t_in"]
    # cue timing hygiene: min 1.0s, small lead-in, no overlap
    cues = out["cues"]
    for i, c in enumerate(cues):
        c["t_in"] = max(0, c["t_in"] - 0.08)
        nxt = cues[i + 1]["t_in"] - 0.04 if i + 1 < len(cues) else total
        c["t_out"] = min(max(c["t_out"] + 0.25, c["t_in"] + 1.0), nxt)
    out["duration_s"] = round(total, 3)
    (ROOT / "timeline.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for c in out["clips"]:
        print(c["file"], "sil", c["silences"], "strong", c["strong"], "snapped", c["snapped"], "len", round(c["t_out"] - c["t_in"], 2))
    print("duration", round(total, 2), "cues", len(cues), "max cue chars", max(len(c["text"]) for c in cues))


if __name__ == "__main__" and len(sys.argv) == 1:
    main()


def main_short(head=0.3, tail=1.6):
    meta = json.loads((ROOT / "script_scenes.json").read_text(encoding="utf-8"))
    text = meta["short"]["text"].replace("ـ", "")
    # one "scene" per sentence → sentence-level beats for visuals
    sents = [s.strip() for s in re.split(r"(?<=[.؟?!])\s+", text) if s.strip()]
    toks, stats = align_clip(str(EXP / "tmp" / "vo_short_edit_only.wav"), sents)
    for q in toks: q["T0"] = head + q["t0"] - stats["on"]; q["T1"] = head + q["t1"] - stats["on"]; q["sid"] = q["scene"]
    total = head + (stats["off"] - stats["on"]) + tail
    beats = []
    for si, s in enumerate(sents):
        ws = [q for q in toks if q["scene"] == si]
        beats.append({"i": si, "text": s, "vo_in": round(ws[0]["T0"], 3), "vo_out": round(ws[-1]["T1"], 3)})
    for i, b in enumerate(beats):
        b["t_in"] = 0.0 if i == 0 else round((beats[i - 1]["vo_out"] + b["vo_in"]) / 2, 3)
    for i, b in enumerate(beats):
        b["t_out"] = round(total, 3) if i == len(beats) - 1 else beats[i + 1]["t_in"]
    cues = []
    for c in build_cues(toks, max_chars=22):
        t = " ".join(q["w"] for q in c)
        cues.append({"t_in": round(max(0, c[0]["T0"] - 0.06), 3), "t_out": round(c[-1]["T1"] + 0.2, 3), "text": t, "lines": wrap(t, 22)})
    for i in range(len(cues) - 1): cues[i]["t_out"] = min(cues[i]["t_out"], cues[i + 1]["t_in"] - 0.04)
    out = {"duration_s": round(total, 3), "beats": beats, "cues": cues, "stats": stats,
           "words": [{"w": q["w"], "t0": round(q["T0"], 3), "t1": round(q["T1"], 3)} for q in toks]}
    (ROOT / "timeline_short.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("short", out["duration_s"], "beats", len(beats), "cues", len(cues), stats)


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "--short":
    main_short()
