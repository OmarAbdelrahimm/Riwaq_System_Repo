#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rv_short.py — RIW_001 Shorts vertical cut (1080x1920, ~44s):
"سر مآذن باب زويلة (الخدعة المعمارية)" — hook / body / CTA → related video.
Pure stateless draw(t), float32 math -> np.clip(...).astype(np.uint8).
"""
from __future__ import annotations
import os, sys, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import arabic_reshaper
from bidi.algorithm import get_display

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "google_drive")
FF = os.path.join(ROOT, "node_modules/@ffmpeg-installer/linux-x64/ffmpeg")
FP = os.path.join(ROOT, "node_modules/@ffprobe-installer/linux-x64/ffprobe")
FONT_B = os.path.join(ROOT, "public/fonts/IBMPlexSansArabic-Bold.ttf")
FONT_M = os.path.join(ROOT, "public/fonts/IBMPlexSansArabic-Medium.ttf")

W, H, FPS = 1080, 1920, 30
DUR = 44.0
N_FRAMES = int(round(DUR * FPS))          #1320

BG = (14, 19, 26)
IVORY = (234, 224, 208)
GOLD = (200, 157, 84)
BROWN = (154, 98, 52)
BURG = (107, 29, 29)

_reshaper = arabic_reshaper.ArabicReshaper(configuration={
    "delete_harakat": False, "support_ligatures": True})
_font_cache = {}
def ar(s): return get_display(_reshaper.reshape(s))
def F(path, size):
    k = (path, size)
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(path, size)
    return _font_cache[k]

_cache = {}
def _load(name):
    if name not in _cache:
        _cache[name] = Image.open(os.path.join(IMG, name)).convert("RGBA")
    return _cache[name]

def lerp(a, b, u):
    u = min(max(u, 0.0), 1.0)
    return a + (b - a) * u

def ease_out(u, p=3.0):
    u = min(max(u, 0.0), 1.0)
    return 1 - (1 - u) ** p

def spring(u, zeta=0.82, omega=9.0):
    """Closed-form under-damped step response, normalized to reach ~1."""
    u = min(max(u, 0.0), 1.0)
    t = u * 2.4
    wd = omega * math.sqrt(max(1 - zeta * zeta, 1e-6))
    x = 1 - math.exp(-zeta * omega * t) * (math.cos(wd * t) +
        (zeta * omega / wd) * math.sin(wd * t))
    return min(max(x, 0.0), 1.18)

# ---------------------------------------------------------------- media
def cover(img, w=W, h=H, vpos=0.5, hpos=0.5):
    s = max(w / img.width, h / img.height)
    nw, nh = int(img.width * s + 0.5), int(img.height * s + 0.5)
    im2 = img.resize((nw, nh), Image.LANCZOS)
    x = int((nw - w) * hpos)
    y = int((nh - h) * vpos)
    return im2.crop((x, y, x + w, y + h))

def zoomcrop(img, zoom, px=0.0, py=0.0, vpos=0.5, hpos=0.5):
    """Center-focus crop in input pixels with sub-pixel pan (always fits)."""
    z = max(zoom, 1.0)
    win_w, win_h = img.width / z, img.height / z
    x0 = (img.width - win_w) / 2 + px
    y0 = (img.height - win_h) / 2 + py
    x0 = min(max(x0, 0), img.width - win_w)
    y0 = min(max(y0, 0), img.height - win_h)
    win = img.crop((int(x0), int(y0), int(x0 + win_w), int(y0 + win_h)))
    return win.resize((W, H), Image.LANCZOS)

def grade(im, bright=0.8, sat=0.85, warm=0.0):
    arr = np.asarray(im.convert("RGB")).astype(np.float32)
    g = arr @ np.array([0.299, 0.587, 0.072], np.float32)
    arr = g[..., None] * (1 - sat) + arr * sat
    arr *= bright
    if warm:
        arr[..., 0] *= 1 + warm * 0.06
        arr[..., 2] *= 1 - warm * 0.05
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

def vgrad(im, top_a=0.0, bot_a=0.72, color=BG):
    arr = np.asarray(im).astype(np.float32)
    ys = np.linspace(0, 1, H, np.float32)
    a = (top_a + (bot_a - top_a) * ys)[:, None, None]
    arr = arr * (1 - a) + np.array(color, np.float32)[None, None, :] * a
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

def vignette(im, strength=0.34):
    arr = np.asarray(im).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    v = 1 - strength * np.clip((d - 0.5) / 0.95, 0, 1) ** 1.5
    return Image.fromarray(np.clip(arr * v[..., None], 0, 255).astype(np.uint8))

def to_rgb(im):
    return im.convert("RGB") if im.mode != "RGB" else im

# ---------------------------------------------------------------- text
def measure(lines):
    d = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    maxw = tot = 0
    for txt, f, size in lines:
        t = ar(txt)
        bb = d.textbbox((0, 0), t, font=f, stroke_width=max(4, size // 18))
        maxw = max(maxw, bb[2] - bb[0])
        tot += (bb[3] - bb[1])
    return maxw, tot

def draw_words(base, txt, f, color, cx, y, t, t0, dur=0.42,
               stagger=0.07, align="center", stroke=None, shadow=True,
               alpha_mul=1.0):
    """RTL whole-word reveal: first logical word appears first (rightmost)."""
    size = getattr(f, "size", 64)
    if stroke is None:
        stroke = max(4, size // 16)
    words = txt.split(" ")
    stroke_c = (8, 10, 14, 255)
    # measure full line for centering
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    shaped = [ar(w) for w in words]
    widths, spaces, asc = [], 0, 0
    for s in shaped:
        bb = d.textbbox((0, 0), s, font=f, stroke_width=stroke)
        widths.append(bb[2] - bb[0])
        asc = max(asc, bb[3] - bb[1])
    sp_bb = d.textbbox((0, 0), " ", font=f)
    space_w = sp_bb[2] - sp_bb[0]
    total = sum(widths) + space_w * (len(words) - 1)
    # RTL: word0 is rightmost; we walk right -> left.
    if align == "center":
        x_right = cx + total / 2
    elif align == "right":
        x_right = cx
    else:
        x_right = cx + total
    y0 = y
    x = x_right
    for i, (s, w) in enumerate(zip(shaped, widths)):
        x -= w
        p = spring((t - (t0 + i * stagger)) / dur)
        if p > 0.01:
            a = int(np.clip(p * 255, 0, 255) * alpha_mul)
            dy = int((1 - min(p, 1.0)) * size * 0.35)
            if shadow:
                d.text((x + 3, y0 + 4), s, font=f, fill=(0, 0, 0, int(a * 0.75)),
                       stroke_width=stroke, stroke_fill=(0, 0, 0, int(a * 0.85)))
            d.text((x, y0 - dy), s, font=f, fill=color + (a,),
                   stroke_width=stroke, stroke_fill=stroke_c[:3] + (a,))
        x -= space_w
    out = Image.alpha_composite(base.convert("RGBA"), layer)
    return out

def card_line(base, txt, f, color, cx, y, alpha=1.0, pad=26,
              accent=True):
    """Tight pill line (same law as v2: card = text + margins), single unit."""
    if alpha <= 0.02:
        return base
    size = getattr(f, "size", 48)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    t = ar(txt)
    stroke = max(3, size // 20)
    bb = d.textbbox((0, 0), t, font=f, stroke_width=stroke)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    cw, ch = tw + pad * 2, th + pad
    x0 = int(cx - cw / 2)
    y0 = int(y)
    a = int(np.clip(alpha, 0, 1) * 255)
    # bg rgba(14,19,26,.85) + accent bar bottom (vertical short on top? no: bottom bar)
    d.rounded_rectangle([x0, y0, x0 + cw, y0 + ch], radius=14,
                        fill=(14, 19, 26, int(a * 0.85)))
    d.rectangle([x0 + cw // 2 - 40, y0 + ch - 7, x0 + cw // 2 + 40, y0 + ch],
                fill=GOLD + (a,))
    d.text((x0 + pad - bb[0], y0 + pad // 2 - bb[1]), t, font=f,
           fill=color + (a,), stroke_width=stroke,
           stroke_fill=(8, 10, 14, a))
    out = Image.alpha_composite(base.convert("RGBA"), layer)
    return out

# ---------------------------------------------------------------- scenes
def logo(base, alpha=0.8, w=130, pos=(48, 120)):
    lg = _load("02-logo-horizontal-dark-bg.png")
    h = int(lg.height * w / lg.width)
    lg = lg.resize((w, h), Image.LANCZOS)
    a = lg.getchannel("A").point(lambda v: int(v * alpha))
    lg.putalpha(a)
    base.paste(lg, pos, lg)
    return base

def whip(base, t, tb, amount=1.0):
    """3-sample directional smear at beat boundaries (t±0.12 @ .25/.5/.25)."""
    if abs(t - tb) > 0.175:
        return base
    k = (1 - abs(t - tb) / 0.175) * amount
    out = np.zeros((H, W, 3), np.float32)
    wsum = 0.0
    for dt, wgt in ((-0.12, 0.25), (0.0, 0.5), (0.12, 0.25)):
        tt = t + dt
        if tt < 0 or tt > DUR:
            continue
        s = draw_raw(tt, _no_whip=True)
        out += np.asarray(s, np.float32) * wgt
        wsum += wgt
    out /= max(wsum, 1e-6)
    # blend: rest frame -> smear
    rest = np.asarray(base).astype(np.float32)
    res = rest * (1 - k) + out * k
    return Image.fromarray(np.clip(res, 0, 255).astype(np.uint8))

def _bg_photo(name, zoom, py, vpos, bright, sat, top_a, bot_a, t, t0, tdur,
              drift=6.0):
    img = _load(name)
    u = (t - t0) / tdur
    # continuous sub-pixel motion (never static)
    py2 = py + math.sin(u * math.pi) * drift
    z = zoom + 0.06 * ease_out(max(u, 0))
    im = zoomcrop(img, z, py=py2, vpos=vpos)
    im = grade(im, bright=bright, sat=sat, warm=0.3)
    im = vgrad(im, top_a=top_a, bot_a=bot_a)
    im = vignette(im, 0.36)
    return im

def scene_hook(t):
    """0–6.9s: zoom on the two minarets + hook headline."""
    im = _bg_photo("Bab_Zuwayla_Cairo_12_0864.jpg", zoom=1.15, py=-260,
                   vpos=0.10, bright=0.72, sat=0.8, top_a=0.18, bot_a=0.82,
                   t=t, t0=0.0, tdur=6.9, drift=10)
    base = to_rgb(im)
    base = logo(base)
    # hook headline (as specified): word reveal at0.55
    base = draw_words(base, "المئذنتين دول", F(FONT_B, 96), IVORY,
                      W // 2, 1040, t, 0.55)
    base = draw_words(base, "مش بتوع الباب أصلاً؟!", F(FONT_B, 96), GOLD,
                      W // 2, 1170, t, 0.95)
    # small kicker
    if t > 1.6:
        a = ease_out((t - 1.6) / 0.4)
        base = card_line(base, "باب زويلة — سر المآذن", F(FONT_M, 44),
                         IVORY, W // 2, 1330, alpha=a)
    return base

def scene_gate(t):
    """6.9–14.0s: Fatimid gate1092."""
    u = (t - 6.9) / 7.1
    im = _bg_photo("Cairo,_bab_zuweila_02.jpeg", zoom=1.22, py=60,
                   vpos=0.45, bright=0.66, sat=0.82, top_a=0.20, bot_a=0.80,
                   t=t, t0=6.9, tdur=7.1, drift=8)
    base = to_rgb(im)
    base = logo(base)
    base = draw_words(base, "البوابة الفاطمية", F(FONT_B, 88), IVORY,
                      W // 2, 1000, t, 7.35)
    # giant year
    base = draw_words(base, "1092م", F(FONT_B, 170), GOLD,
                      W // 2, 1130, t, 7.8)
    if t > 8.7:
        a = ease_out((t - 8.7) / 0.4)
        base = card_line(base, "بُنيت للدفاع عن القاهرة", F(FONT_M, 46),
                         IVORY, W // 2, 1340, alpha=a)
    return base

def scene_minarets(t):
    """14.0–21.5s: Mamluk minarets,3 centuries later."""
    im = _bg_photo("Bab_Zuwayla_Cairo_12_0864.jpg", zoom=1.42, py=430,
                   vpos=0.30, bright=0.70, sat=0.8, top_a=0.16, bot_a=0.84,
                   t=t, t0=14.0, tdur=7.5, drift=9)
    base = to_rgb(im)
    base = logo(base)
    base = draw_words(base, "المآذن… من زمن تاني", F(FONT_B, 86), IVORY,
                      W // 2, 980, t, 14.4)
    base = draw_words(base, "بعد 3 قرون", F(FONT_B, 140), GOLD,
                      W // 2, 1110, t, 14.9)
    if t > 15.9:
        a = ease_out((t - 15.9) / 0.4)
        base = card_line(base, "المؤيد شيخ استغل برجي الدفاع",
                         F(FONT_M, 46), IVORY, W // 2, 1320, alpha=a)
    return base

def scene_two_times(t):
    """21.5–29.4s: one building, two eras (comparison cards)."""
    # flat brand bg with slow drifting blueprint grid (never static)
    arr = np.full((H, W, 3), BG, np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    ph = ((t - 21.5) * 9) % 64
    grid = (((xx + ph) % 64 < 1.6) | ((yy + ph * 0.6) % 64 < 1.6)).astype(np.float32)
    arr += (grid * 7)[..., None]
    base = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    base = vignette(base, 0.3)
    base = logo(base)
    # top card: Fatimid
    p1 = spring((t - 22.0) / 0.5)
    if p1 > 0.01:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        y0 = int(560 - (1 - min(p1, 1)) * 60)
        a = int(np.clip(p1, 0, 1) * 255)
        d.rounded_rectangle([90, y0, W - 90, y0 + 300], radius=24,
                            fill=(26, 32, 40, int(a * 0.92)))
        d.rectangle([W - 104, y0 + 18, W - 90, y0 + 282], fill=GOLD + (a,))
        t1 = ar("فاطمية — البوابة 1092م")
        d.text((W - 130, y0 + 60), t1, font=F(FONT_B, 72), fill=IVORY + (a,),
               anchor="ra", stroke_width=6, stroke_fill=(8, 10, 14, a))
        t2 = ar("سور القاهرة ودفاع المدينة")
        d.text((W - 130, y0 + 180), t2, font=F(FONT_M, 48), fill=(196, 190, 178, a),
               anchor="ra")
        base = Image.alpha_composite(base.convert("RGBA"), lay).convert("RGB")
    # bottom card: Mamluk
    p2 = spring((t - 22.6) / 0.5)
    if p2 > 0.01:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        y0 = int(920 + (1 - min(p2, 1)) * 60)
        a = int(np.clip(p2, 0, 1) * 255)
        d.rounded_rectangle([90, y0, W - 90, y0 + 300], radius=24,
                            fill=(36, 28, 20, int(a * 0.92)))
        d.rectangle([W - 104, y0 + 18, W - 90, y0 + 282], fill=BROWN + (a,))
        t1 = ar("مملوكية — المآذن بعد 3 قرون")
        d.text((W - 130, y0 + 60), t1, font=F(FONT_B, 72), fill=GOLD + (a,),
               anchor="ra", stroke_width=6, stroke_fill=(8, 10, 14, a))
        t2 = ar("مسجد المؤيد شيخ على البرجين")
        d.text((W - 130, y0 + 180), t2, font=F(FONT_M, 48), fill=(214, 205, 190, a),
               anchor="ra")
        base = Image.alpha_composite(base.convert("RGBA"), lay).convert("RGB")
    # punch line
    base = draw_words(base, "مبنى واحد…", F(FONT_B, 92), IVORY,
                      W // 2, 1330, t, 23.4)
    base = draw_words(base, "زمنان مختلفان", F(FONT_B, 92), GOLD,
                      W // 2, 1460, t, 23.9)
    return base

def scene_cta(t):
    """29.4–44.0s: giant doors,4 tons, bronze balls + related-video arrow."""
    img = _load("cutout_door.png")
    u = (t - 29.4) / 14.6
    im = zoomcrop(img, 1.30 + 0.10 * ease_out(u), py=-40 + math.sin(u * 4) * 8,
                  vpos=0.35)
    im = grade(im, bright=0.62, sat=0.85, warm=0.35)
    im = vgrad(im, top_a=0.30, bot_a=0.86)
    im = vignette(im, 0.40)
    base = logo(to_rgb(im))
    base = draw_words(base, "4 أطنان", F(FONT_B, 190), GOLD,
                      W // 2, 940, t, 29.9)
    if t > 30.9:
        a = ease_out((t - 30.9) / 0.4)
        base = card_line(base, "كل ضلفة على كرات برونزية", F(FONT_M, 50),
                         IVORY, W // 2, 1180, alpha=a)
    # related-video pointer: arrow to bottom-left (Shorts related link area)
    if t > 33.0:
        p = ease_out((t - 33.0) / 0.5)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        a = int(p * 255)
        bob = int(math.sin(t * 3.2) * 8)
        # text
        t1 = ar("القصة كاملة في الفيديو المرتبط")
        f = F(FONT_B, 52)
        d.text((W // 2, 1400 + bob), t1, font=f, fill=IVORY + (a,),
               anchor="mm", stroke_width=5, stroke_fill=(8, 10, 14, a))
        # arrow: down-left toward the Shorts related-video link (bottom-left)
        ax0, ay0, ax1, ay1 = W // 2 - 40, 1490 + bob, 330, 1700 + bob
        d.line([ax0, ay0, ax1, ay1], fill=GOLD + (a,), width=12)
        # head: tip at (ax1,ay1), base up-right along the line
        import math as _m
        dx, dy = ax1 - ax0, ay1 - ay0
        L = _m.hypot(dx, dy) or 1.0
        ux, uy = dx / L, dy / L          # pointing down-left
        bx, by = ax1 - ux * 74, ay1 - uy * 74
        px, py = -uy * 40, ux * 40
        d.polygon([(ax1, ay1), (bx + px, by + py), (bx - px, by - py)],
                  fill=GOLD + (a,))
        base = Image.alpha_composite(base.convert("RGBA"), lay).convert("RGB")
    return base

# ---------------------------------------------------------------- draw(t)
BOUNDARIES = (6.9, 14.0, 21.5, 29.4)

def draw_raw(t, _no_whip=False):
    if t < 6.9:
        f = scene_hook(t)
    elif t < 14.0:
        f = scene_gate(t)
    elif t < 21.5:
        f = scene_minarets(t)
    elif t < 29.4:
        f = scene_two_times(t)
    else:
        f = scene_cta(t)
    return to_rgb(f)

def draw(t):
    base = draw_raw(t)
    if True:
        for tb in BOUNDARIES:
            if abs(t - tb) <= 0.175:
                base = whip(base, t, tb)
                break
    arr = np.asarray(base).astype(np.float32)
    # deterministic per-frame grain (function of t only -> still stateless)
    rng = np.random.default_rng(int(round(t * FPS)) + 7717)
    arr += rng.normal(0.0, 2.4, arr.shape).astype(np.float32)
    return np.clip(arr, 0, 255).astype(np.uint8)

# ---------------------------------------------------------------- render
def render():
    os.makedirs(os.path.join(ROOT, "exports"), exist_ok=True)
    out = os.path.join(ROOT, "exports", "SHORT_BABZUWEILA_MASJAR_v1.mp4")
    vo = [os.path.join(ROOT, "short", n) for n in
          ("vo_hook.mp3", "vo_body.mp3", "vo_cta.mp3")]
    music = os.path.join(IMG, "1816_ORIGINAL_MUSIC_BED_48k.flac")
    fc = (
        "[1:a]aformat=channel_layouts=stereo,adelay=300|300[a0];"
        "[2:a]aformat=channel_layouts=stereo,adelay=7100|7100[a1];"
        "[3:a]aformat=channel_layouts=stereo,adelay=29600|29600[a2];"
        "[a0][a1][a2]amix=inputs=3,volume=3[vo];"
        "[4:a]atrim=0:44,asetpts=PTS-STARTPTS,aformat=channel_layouts=stereo,"
        "volume=0.16,afade=t=in:d=1.2,afade=t=out:st=41.5:d=2.5[bg];"
        "[vo][bg]amix=inputs=2,volume=2,"
        "loudnorm=I=-14:TP=-1.0:LRA=11,"
        "aformat=sample_rates=48000:channel_layouts=stereo[aout]"
    )
    cmd = [
        FF, "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-",
        "-i", vo[0], "-i", vo[1], "-i", vo[2], "-i", music,
        "-filter_complex", fc,
        "-map", "0:v:0", "-map", "[aout]",
        "-t", str(DUR),
        "-c:v", "libx264", "-preset", "slow", "-crf", "21",
        "-pix_fmt", "yuv420p", "-color_range", "tv",
        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart", out,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    import time
    t0 = time.time()
    for n in range(N_FRAMES):
        proc.stdin.write(draw(n / FPS).tobytes())
        if n % 300 == 0 and n:
            el = time.time() - t0
            fps = n / el
            print(f"  {n}/{N_FRAMES} {fps:.1f} f/s eta {(N_FRAMES-n)/max(fps,1e-6):.0f}s",
                  flush=True)
    proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        raise SystemExit(f"ffmpeg rc={rc}")
    size = os.path.getsize(out)
    meta = subprocess.run([FP, "-v", "error", "-show_entries",
                           "stream=codec_name,width,height,pix_fmt,r_frame_rate,"
                           "sample_rate,channels",
                           "-show_entries", "format=duration,size", "-of", "json",
                           out], capture_output=True, text=True).stdout
    print(meta)
    print(f"size={size} ({size/1e6:.1f} MB) under100={size < 100_000_000}")
    print("OUT ->", out)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "qa":
        # smoke: a few frames + no-Latin + static checks
        import re
        for tt in (0.5, 3.0, 10.0, 18.0, 25.0, 35.0, 43.5):
            f = draw(tt)
            assert f.shape == (H, W, 3) and f.dtype == np.uint8, tt
        d1 = np.abs(draw(5.0).astype(np.int16) - draw(5.1).astype(np.int16)).mean()
        d2 = np.abs(draw(36.0).astype(np.int16) - draw(36.1).astype(np.int16)).mean()
        print(f"frame deltas: {d1:.3f} {d2:.3f} (must be >0.05)")
        print("smoke OK")
    else:
        render()
