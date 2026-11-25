#!/usr/bin/env python3
"""qa.py — فحوص آلية على المخرجات النهائية → qa_report.md (أرقام مقاسة فعلًا، لا تقديرات)."""
import csv, glob, hashlib, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__)); EPDIR = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(EPDIR, "..", ".."))
EP = "WHAT_IF_BAGHDAD_NEVER_FELL"
EX = os.path.join(ROOT, "exports", EP)
FF = os.environ.get("FFMPEG", "/tmp/ffmpeg")
PAL = {"#1C1B19", "#242218", "#F3EBDB", "#EDE6D6", "#A98A4B", "#C2A469", "#EFE6D2", "#5E2230", "#8A7F6B", "#B9AE94"}


def run(args):
    return subprocess.run(args, capture_output=True, text=True).stderr


def probe(path):
    err = run([FF, "-hide_banner", "-i", path])
    dur = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    d = int(dur.group(1)) * 3600 + int(dur.group(2)) * 60 + float(dur.group(3)) if dur else 0
    v = re.search(r"Video: (\w+).*?, (\d{3,4})x(\d{3,4}).*?([\d.]+) fps", err)
    a = re.search(r"Audio: (\w+).*?(\d+) Hz, (\w+).*?(\d+) kb/s", err)
    pix = re.search(r"Video: \w+[^,]*, (\w+)\(", err) or re.search(r"Video: \w+[^,]*, (yuv\w+)", err)
    return {"dur": d, "vcodec": v.group(1) if v else None, "w": int(v.group(2)) if v else 0, "h": int(v.group(3)) if v else 0,
            "fps": float(v.group(4)) if v else 0, "pix": pix.group(1) if pix else "?", "acodec": a.group(1) if a else None,
            "ahz": int(a.group(2)) if a else 0, "akbps": int(a.group(4)) if a else 0}


def loud(path):
    err = run([FF, "-hide_banner", "-nostats", "-i", path, "-map", "0:a:0", "-af", "ebur128=peak=true", "-f", "null", "-"])
    tail = err[err.rfind("Summary:"):]
    I = re.search(r"I:\s+(-?[\d.]+) LUFS", tail); LRA = re.search(r"LRA:\s+([\d.]+) LU", tail); TP = re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail)
    return (float(I.group(1)) if I else None, float(TP.group(1)) if TP else None, float(LRA.group(1)) if LRA else None)


def srt_stats(path):
    txt = open(path, encoding="utf-8").read().strip().split("\n\n")
    n, short, longl, lines3, overlap = 0, 0, 0, 0, 0
    prev = 0.0
    lim = 28 if "_ar" in path else 42
    for b in txt:
        L = b.split("\n")
        if len(L) < 3: continue
        n += 1
        m = re.findall(r"(\d+):(\d+):(\d+),(\d+)", L[1])
        t = [int(h) * 3600 + int(mi) * 60 + int(s) + int(ms) / 1000 for h, mi, s, ms in m]
        if t[1] - t[0] < 1.2 - 1e-6: short += 1
        if t[0] < prev - 1e-6: overlap += 1
        prev = t[1]
        body = [re.sub("[\u2066\u2069]", "", x) for x in L[2:]]
        if len(body) > 2: lines3 += 1
        if any(len(x) > lim for x in body): longl += 1
    return n, short, longl, lines3, overlap


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""): h.update(ch)
    return h.hexdigest()


def main():
    rows, fails = [], []
    def chk(name, ok, val, target):
        rows.append((name, "PASS" if ok else "FAIL", val, target))
        if not ok: fails.append(name)

    vids = {"master.mp4": (1920, 1080, -14, "voice"), "master_no_voice.mp4": (1920, 1080, None, "nv"), "master_sfx_only.mp4": (1920, 1080, None, "sfx"),
            "short_v1.mp4": (1080, 1920, -14, "voice"), "short_v1_no_voice.mp4": (1080, 1920, None, "nv"), "short_v1_sfx_only.mp4": (1080, 1920, None, "sfx")}
    media = {}
    for f, (w, h, tgt, kind) in vids.items():
        p = os.path.join(EX, "video", f)
        if not os.path.exists(p):
            chk(f"{f} موجود", False, "غير موجود", "—"); continue
        pr = probe(p); I, TP, LRA = loud(p)
        media[f] = dict(pr, I=I, TP=TP, LRA=LRA, size_mb=round(os.path.getsize(p) / 1e6, 1), sha256=sha(p))
        chk(f"{f} · الأبعاد", (pr["w"], pr["h"]) == (w, h), f'{pr["w"]}x{pr["h"]}', f"{w}x{h}")
        chk(f"{f} · fps/codec", abs(pr["fps"] - 30) < 0.01 and pr["vcodec"] == "h264", f'{pr["fps"]} fps · {pr["vcodec"]} · {pr["pix"]}', "30 · h264 · yuv420p")
        chk(f"{f} · الصوت", pr["acodec"] == "aac" and pr["ahz"] == 48000, f'{pr["acodec"]} {pr["ahz"]} Hz {pr["akbps"]} kb/s', "AAC 48 kHz")
        if tgt is not None:
            chk(f"{f} · Loudness", I is not None and abs(I - tgt) <= 1.0, f"{I} LUFS", f"{tgt} ±1 LU")
        chk(f"{f} · True peak", TP is not None and TP <= -0.9, f"{TP} dBFS", "≤ −1 dBTP (تسامح 0.1)")
    if "master.mp4" in media:
        d = media["master.mp4"]["dur"]; chk("المدة · الطويل", 480 <= d <= 600, f"{d:.2f} s ({int(d // 60)}:{d % 60:04.1f})", "8–10 دقائق")
    if "short_v1.mp4" in media:
        d = media["short_v1.mp4"]["dur"]; chk("المدة · الشورت", 45 <= d <= 55, f"{d:.2f} s", "45–55 ث")

    for f in sorted(glob.glob(os.path.join(EX, "subtitles", "*.srt"))):
        n, short, longl, l3, ov = srt_stats(f)
        name = os.path.basename(f)
        chk(f"{name} · بنية", l3 == 0 and longl == 0 and ov == 0, f"{n} مقطع · >حد السطر: {longl} · >سطرين: {l3} · تداخل: {ov}", "≤2 سطر · بلا تداخل")
        rows.append((f"{name} · مقاطع < 1.2 ث", "INFO" if short else "PASS", str(short), "تحذير فقط (repo make_srt)"))

    for mf in ("episode_meta.json", "episode_meta_short.json"):
        m = json.load(open(os.path.join(ROOT, "data", "projects", EP, mf), encoding="utf-8"))
        cols = set(re.findall(r'#[0-9A-Fa-f]{6}', json.dumps(m)))
        chk(f"{mf} · قفل الباليت (البيانات)", cols <= PAL, ", ".join(sorted(cols)) or "لا ألوان حرفية", "ألوان brand.json فقط")
        ai = [v for v in m.get("visuals", []) if v["kind"] == "ai"]
        arch = [v for v in m.get("visuals", []) if v["kind"] == "archival"]
        chk(f"{mf} · وسم الصور", all(v.get("credit") for v in arch), f"AI={len(ai)} (وسم تلقائي «إعادة تصوّر») · أرشيف={len(arch)} بسطر مصدر", "كل صورة موسومة")
        chk(f"{mf} · نطاقات الخيال", bool(m.get("fiction")), json.dumps(m.get("fiction")), "وسم «خيال تاريخي» دائم داخل الافتراض")
    # ألوان حرفية في كود المكوّنات الجديدة
    newc = ["SceneTitle", "KeywordPop", "TimelineBar", "Transition", "ProgressBar", "ConceptMorph", "VisualLayer", "MapSchematic", "Bars", "SplitScreen"]
    lit = {}
    for c in newc:
        s = open(os.path.join(ROOT, "src", "components", c + ".tsx"), encoding="utf-8").read()
        found = set(x.upper() for x in re.findall(r'#[0-9A-Fa-f]{6}\b', s)) - PAL
        if found: lit[c] = sorted(found)
    chk("المكوّنات الجديدة · قفل الباليت", not lit, json.dumps(lit, ensure_ascii=False) or "كل الألوان عبر color()", "لا HEX خارج الهوية")
    fonts = set()
    for f in glob.glob(os.path.join(ROOT, "src", "**", "*.tsx"), recursive=True):
        s = open(f, encoding="utf-8").read()
        fonts |= set(re.findall(r'fontFamily:\s*"([^"]+)"', s))
    chk("قفل الخطوط", not ({"Cairo", "Inter"} & fonts), ", ".join(sorted(fonts)) or "headlineFont/bodyFont من الثيم فقط", "Amiri + IBM Plex Sans Arabic")
    with open(os.path.join(EPDIR, "credits.csv"), encoding="utf-8") as f:
        cr = list(csv.DictReader(f))
    imgs = [os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "public", "projects", EP, "img", "*.jpg"))]
    logged = {os.path.basename(r["file"]) for r in cr}
    chk("credits.csv يغطي كل الصور", set(imgs) <= logged, f"{len(imgs)} صورة · {len(cr)} سجل", "كل أصل مسجّل")
    fc = list(csv.DictReader(open(os.path.join(EPDIR, "FACT_CHECK.csv"), encoding="utf-8")))
    st = {}
    for r in fc:
        k = next((r[c] for c in r if c and c.lower().startswith("status")), "?")
        st[k] = st.get(k, 0) + 1
    rows.append(("FACT_CHECK", "INFO", json.dumps(st, ensure_ascii=False), "كل ادعاء ← مصدر"))

    json.dump(media, open(os.path.join(EX, "tmp", "qa_media.json"), "w"), indent=1)
    out = os.path.join(EPDIR, "qa_report_auto.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"# QA آلي — {EP}\n\n| الفحص | النتيجة | القيمة المقاسة | الهدف |\n|---|---|---|---|\n")
        for r in rows: f.write("| " + " | ".join(str(x) for x in r) + " |\n")
        f.write(f"\n**FAIL: {len(fails)}** {'— ' + ', '.join(fails) if fails else ''}\n")
    print(open(out, encoding="utf-8").read())


if __name__ == "__main__":
    main()
