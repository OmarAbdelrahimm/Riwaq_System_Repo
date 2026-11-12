#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rv_render.py — contact sheet (v2) / segmented full render for rv_engine.
  python3 scripts/rv_render.py sheet   # CONTACT_SHEET_12_STATES_v2.jpg + QA checks
  python3 scripts/rv_render.py full     # BAB_ZUWEILA_FINAL_v2.mp4 (<100MB delivery)
"""
from __future__ import annotations
import os, sys, subprocess, json, time, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_engine as E

ROOT = E.ROOT
FF = os.path.join(ROOT, "tools/node_modules/@ffmpeg-installer/linux-x64/ffmpeg")
FP = os.path.join(ROOT, "tools/node_modules/@ffprobe-installer/linux-x64/ffprobe")
PREV = os.path.join(ROOT, "previews"); OUT = os.path.join(ROOT, "exports")
os.makedirs(PREV, exist_ok=True); os.makedirs(OUT, exist_ok=True)

SHEET_TIMES = [3.5, 8.2, 18.5, 30.0, 49.0, 64.0, 80.0, 118.0, 155.0, 178.0, 200.0, 225.0]

def wcag(c1, c2):
    def lin(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    L1 = sum(w * v for w, v in zip((0.2126, 0.7152, 0.0722), map(lin, c1)))
    L2 = sum(w * v for w, v in zip((0.2126, 0.7152, 0.0722), map(lin, c2)))
    a, b = max(L1, L2), min(L1, L2)
    return (a + 0.05) / (b + 0.05)

def qa_metrics():
    rep = {}
    # 1) card box law: card_w == text_w + 64 (dynamic per content), report spread
    widths, boxes = [], []
    for (st, t_in, t_out, acc, rows) in E.SEGMENTS:
        imgs, tw, th, size = E._measure_card(rows, acc)
        cw, ch = tw + E.MARGIN_X * 2, th + E.MARGIN_Y * 2
        assert cw == tw + 64 and ch == th + 36, (st, cw, tw)
        assert cw <= tw + 64
        widths.append(cw)
        boxes.append({"state": st, "t_in": t_in, "text_w": tw, "card_w": cw,
                      "card_h": ch, "font": size})
    rep["card_w_law_pass"] = True
    rep["card_w_spread"] = [min(widths), max(widths)]
    rep["card_w_dynamic"] = (max(widths) - min(widths)) > 200
    rep["boxes"] = boxes
    # 2) ZERO empty rectangles when text_alpha == 0
    gap_times = [6.0, 16.5, 42.5, 113.5, 143.0, 170.0, 187.0, 216.65, 0.4]
    empties = []
    for tg in gap_times:
        rows, acc, a, dx = E.card_state(tg)
        empties.append(a == 0.0 and rows is None)
    rep["zero_empty_rectangles"] = all(empties)
    # structural: draw_card returns before ANY drawing when alpha<=0.02
    rep["empty_guard_in_code"] = "return                      # ZERO empty rectangles" in \
        open(os.path.join(ROOT, "scripts/rv_engine.py"), encoding="utf-8").read()
    # 3) logo: exactly once, top-left, width 145, alpha 80%
    src = open(os.path.join(ROOT, "scripts/rv_engine.py"), encoding="utf-8").read()
    n_logo_loads = src.count('_load("02-logo-horizontal-dark-bg.png")')
    rep["logo_occurrences"] = n_logo_loads
    rep["logo_once"] = (n_logo_loads == 1)
    rep["logo_width"] = E.LOGO_W
    rep["logo_pos"] = list(E.LOGO_POS)
    rep["logo_alpha"] = E.LOGO_ALPHA
    rep["logo_pass"] = (E.LOGO_W == 145 and tuple(E.LOGO_POS) == (56, 44)
                        and abs(E.LOGO_ALPHA - 0.80) < 1e-9 and n_logo_loads == 1)
    # 4) ZERO Latin letters inside on-screen Arabic strings
    latin = []
    for (st, t_in, t_out, acc, rows) in E.SEGMENTS:
        for r in rows:
            texts = [r["text"]] if "text" in r else [v for k, v in r["runs"] if k == "text"]
            for tx in texts:
                if re.search(r"[A-Za-z]", tx):
                    latin.append(tx)
    for m in re.finditer(r'paste_text\(base,\s*"([^"]+)"', src):
        if re.search(r"[A-Za-z]", m.group(1)):
            latin.append(m.group(1))
    for m in re.finditer(r'_label_pill\(base,\s*"([^"]+)"', src):
        if re.search(r"[A-Za-z]", m.group(1)):
            latin.append(m.group(1))
    rep["latin_in_arabic"] = latin
    rep["zero_latin_pass"] = len(latin) == 0
    # 5) contrast (worst case: ivory over 0.85 BG + 0.15 bright board)
    worst = tuple(int(round(0.85 * E.BG[i] + 0.15 * 200)) for i in range(3))
    rep["contrast_worst"] = round(wcag(E.IVORY, worst), 2)
    rep["contrast_pass"] = rep["contrast_worst"] >= 4.5
    # 6) no static frames / no black frames
    diffs = []
    for t0 in (2.0, 40.0, 99.0, 160.0, 231.0):
        a = E.draw(t0).astype(np.int16); b = E.draw(t0 + 1 / E.FPS).astype(np.int16)
        diffs.append(float(np.abs(a - b).mean()))
    rep["frame_delta_means"] = [round(x, 3) for x in diffs]
    rep["zero_static_pass"] = all(x > 0.05 for x in diffs)
    mins = [E.draw(n / E.FPS).mean() for n in range(0, E.N_FRAMES, 400)]
    rep["min_frame_mean"] = round(min(mins), 1)
    rep["no_black_pass"] = rep["min_frame_mean"] > 8
    return rep

def cmd_sheet():
    os.makedirs("/tmp/rv_sheet", exist_ok=True)
    paths = []
    for i, t in enumerate(SHEET_TIMES, 1):
        f = E.draw(t)
        p = f"/tmp/rv_sheet/s{i:02d}.png"
        Image.fromarray(f).save(p)
        paths.append(p)
        print(f"  state {i:02d} @ {t}s ok")
    cell_w, cell_h = 640, 360
    sheet = Image.new("RGB", (cell_w * 4 + 20, cell_h * 3 + 40), (10, 10, 12))
    dr = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    except Exception:
        font = ImageFont.load_default()
    for i, p in enumerate(paths):
        im = Image.open(p).resize((cell_w - 8, cell_h - 8), Image.LANCZOS)
        cx, cy = (i % 4) * cell_w + 4, (i // 4) * cell_h + 4
        sheet.paste(im, (cx, cy))
        dr.rectangle([cx, cy, cx + 150, cy + 30], fill=(0, 0, 0))
        dr.text((cx + 8, cy + 4), f"STATE {i+1:02d}", fill=(255, 220, 120), font=font)
    out = os.path.join(PREV, "CONTACT_SHEET_12_STATES_v2.jpg")
    sheet.save(out, quality=93)
    rep = qa_metrics()
    with open("/tmp/rv_qa_v2.json", "w") as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k != "boxes"},
                     ensure_ascii=False, indent=1))
    print("SHEET ->", out)

def render_range(a: int, b: int, out_path: str, crf: int = 17):
    cmd = [FF, "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{E.W}x{E.H}",
           "-r", str(E.FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
           "-pix_fmt", "yuv420p", "-color_range", "tv",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for n in range(a, b):
        proc.stdin.write(E.draw(n / E.FPS).tobytes())
        if (n - a) % 600 == 0 and n > a:
            el = time.time() - t0
            fps = (n - a) / max(el, 1e-6)
            print(f"    [{a}-{b}] {n-a}/{b-a}  {fps:.1f} f/s  eta {(b-n)/max(fps,1e-6):.0f}s",
                  flush=True)
    proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"ffmpeg failed rc={rc}")
    print(f"    segment done {out_path} ({time.time()-t0:.0f}s)")

def cmd_full():
    N = E.N_FRAMES
    mid = N // 2
    seg1, seg2 = "/tmp/rv2_seg1.mp4", "/tmp/rv2_seg2.mp4"
    print(f"full render: frames 0..{N} (split at {mid})")
    render_range(0, mid, seg1)
    render_range(mid, N, seg2)
    with open("/tmp/rv2_concat.txt", "w") as fh:
        fh.write(f"file '{seg1}'\nfile '{seg2}'\n")
    subprocess.run([FF, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", "/tmp/rv2_concat.txt", "-c", "copy", "/tmp/rv2_video.mp4"],
                   check=True)
    # delivery encode: high quality, light grain denoise, under 100MB
    final = os.path.join(OUT, "BAB_ZUWEILA_FINAL_v2.mp4")
    subprocess.run([FF, "-y", "-loglevel", "error", "-stats",
                    "-i", "/tmp/rv2_video.mp4",
                    "-i", os.path.join(E.IMG, "MASTER_FINAL_RIW_001.mp4"),
                    "-map", "0:v:0", "-map", "1:a:0", "-t", f"{E.DUR}",
                    "-vf", "hqdn3d=6:4:8:8",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "24",
                    "-pix_fmt", "yuv420p", "-color_range", "tv",
                    "-colorspace", "bt709", "-color_primaries", "bt709",
                    "-color_trc", "bt709",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                    "-movflags", "+faststart", final],
                   check=True)
    size = os.path.getsize(final)
    out = subprocess.run([FP, "-v", "error", "-show_entries",
                          "stream=codec_name,width,height,pix_fmt,r_frame_rate,sample_rate,channels",
                          "-show_entries", "format=duration,size", "-of", "json", final],
                         capture_output=True, text=True).stdout
    print(out)
    print(f"size={size} bytes ({size/1e6:.1f} MB)  under100={size < 100_000_000}")
    print("FINAL ->", final)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "sheet":
        cmd_sheet()
    elif cmd == "full":
        cmd_full()
    else:
        print("unknown"); sys.exit(1)
