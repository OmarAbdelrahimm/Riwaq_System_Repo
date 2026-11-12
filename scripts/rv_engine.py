#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rv_engine.py — Bab Zuwayla · Riwaq · 12-State STATELESS engine  (v2 / visual-fix build)
========================================================================================
Laws:
  * One pure function draw(t) -> (H,W,3) uint8 — no inter-frame state.
  * float32 math, final np.clip(frame,0,255).astype(np.uint8).
  * v2 visual fixes (user-locked, exact measurements):
      1) Real hero photography for STATE 01 (tilt-down minarets->towers);
         STATE 03 uses the dramatic gate photograph; STATE 08 uses the
         architectural comparison board (smart zoom/pan) — flat beige 3D
         renders banned as full-screen backgrounds.
         STATE 02/07 doors: blurred darkened self-fill (25%) + blueprint grid.
      2) Auto-Fit Compact Pill card: font 42px (38px long), tight box
         card_w = text_w + 64, card_h = text_h + 36, radius 8,
         backdrop Gaussian blur 12 on rgba(14,19,26,0.85), 6px accent bar on
         the RIGHT edge only, anchored Bottom-Right (right x=1840, bottom y=1010).
      3) Zero empty rectangles: card_alpha == text_alpha; unit slide-in 30px
         from right + fade 0.30s, out 0.25s. Nothing drawn when alpha ~ 0.
      4) Clean HUD: no top watermark, no slide counter, no corner captions;
         official logo ONCE, top-left x=56 y=44, width 145px, alpha 80%.
      5) No Latin letters inside Arabic on-screen strings.
"""
from __future__ import annotations
import math, os, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import arabic_reshaper
from bidi.algorithm import get_display

# ───────────────────────── constants ─────────────────────────
W, H, FPS = 1920, 1080, 30
DUR = 237.82
N_FRAMES = int(round(DUR * FPS))  # 7135

BG      = (14, 19, 26)      # #0E131A
IVORY   = (234, 224, 208)   # #EAE0D0
GOLD    = (200, 157, 84)    # #C89D54
BRONZE  = (154, 98, 52)     # #9A6234
CRIMSON = (107, 29, 29)     # #6B1D1D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG  = os.path.join(ROOT, "google_drive")
FONT_BOLD = os.path.join(ROOT, "public/fonts/IBMPlexSansArabic-Bold.ttf")
FONT_MED  = os.path.join(ROOT, "public/fonts/IBMPlexSansArabic-Medium.ttf")

# card law (exact numbers from the fix order)
CARD_RIGHT, CARD_BOTTOM = 1840, 1010
MARGIN_X, MARGIN_Y = 32, 18          # card_w = text_w + 64 · card_h = text_h + 36
CARD_RADIUS, ACCENT_W = 8, 6
FONT_CARD, FONT_CARD_LONG, LONG_THRESHOLD = 42, 38, 1100
SLIDE_PX, FADE_IN_S, FADE_OUT_S = 30, 0.30, 0.25

# logo law (exact numbers from the fix order)
LOGO_W, LOGO_POS, LOGO_ALPHA = 145, (56, 44), 0.80

ZETA, OMEGA = 0.82, 9.0

# ───────────────────────── arabic shaping ─────────────────────────
_reshaper = arabic_reshaper.ArabicReshaper(configuration={
    "delete_harakat": False, "support_ligatures": True, "map_ligatures": True,
})

@functools.lru_cache(maxsize=4096)
def shape(text: str) -> str:
    return get_display(_reshaper.reshape(text))

@functools.lru_cache(maxsize=4096)
def _text_png(text: str, size: int, color: tuple, font_path: str) -> Image.Image:
    font = ImageFont.truetype(font_path, size)
    sh = shape(text)
    tmp = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    bbox = d.textbbox((0, 0), sh, font=font)
    w, h = bbox[2] - bbox[0] + 8, bbox[3] - bbox[1] + 8
    im = Image.new("RGBA", (max(w, 4), max(h, 4)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4 - bbox[0], 4 - bbox[1]), sh, font=font, fill=color + (255,))
    return im

def text_size(text: str, size: int, font_path: str = FONT_BOLD):
    return _text_png(text, size, (255, 255, 255), font_path).size

def paste_text(base: Image.Image, text, x, y, size, color, font=FONT_BOLD,
               anchor="mm", alpha=255):
    im = _text_png(text, size, color, font)
    if alpha < 255:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: v * alpha // 255))
    px = int(x - im.size[0] / 2) if anchor[0] == "m" else int(x)
    py = int(y - im.size[1] / 2) if anchor[1] == "m" else int(y)
    base.alpha_composite(im, (px, py))

# ───────────────────────── closed-form helpers ─────────────────────────
def spring_step(t, t0, zeta=ZETA, omega=OMEGA) -> float:
    tau = t - t0
    if tau <= 0.0:
        return 0.0
    wd = omega * math.sqrt(max(1e-9, 1.0 - zeta * zeta))
    e = math.exp(-zeta * omega * tau)
    return 1.0 - e * (math.cos(wd * tau) + (zeta * omega / wd) * math.sin(wd * tau))

def lerp(a, b, u):
    u = 0.0 if u < 0 else (1.0 if u > 1 else u)
    return a + (b - a) * u

def ramp(t, t0, t1):
    if t1 <= t0:
        return 1.0 if t >= t0 else 0.0
    return lerp(0.0, 1.0, (t - t0) / (t1 - t0))

# ───────────────────────── assets ─────────────────────────
@functools.lru_cache(maxsize=64)
def _load(name: str) -> Image.Image:
    im = Image.open(os.path.join(IMG, name))
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    return im

@functools.lru_cache(maxsize=64)
def _cover(name: str) -> Image.Image:
    """Scale to width 2400 keeping the FULL frame (no crop) -> pan/tilt room."""
    im = _load(name)
    iw, ih = im.size
    w = 2400
    h = max(int(round(ih * w / iw)), 1352)
    im = im.resize((w, h), Image.LANCZOS)
    bg = Image.new("RGB", (w, h), BG)
    bg.paste(im, (0, 0), im)
    return bg

@functools.lru_cache(maxsize=8)
def _door_scene(name: str) -> Image.Image:
    """Door hero: blurred darkened self-fill @25% + blueprint grid + sharp frame."""
    src = _load(name)
    iw, ih = src.size
    tr, sr = W / H, iw / ih
    if sr > tr:
        nw = int(ih * tr); x0 = (iw - nw) // 2
        fill = src.crop((x0, 0, x0 + nw, ih))
    else:
        nh = int(iw / tr); y0 = (ih - nh) // 2
        fill = src.crop((0, y0, iw, y0 + nh))
    fill = fill.resize((W, H), Image.LANCZOS).convert("RGB")
    fill = fill.filter(ImageFilter.GaussianBlur(40))
    arr = np.asarray(fill, np.float32) * 0.25
    base = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    base.alpha_composite(_grid_layer())
    fh = int(H * 0.84); fw = int(round(iw * fh / ih))
    fg = src.resize((fw, fh), Image.LANCZOS)
    base.alpha_composite(fg, ((W - fw) // 2, (H - fh) // 2))
    return base

@functools.lru_cache(maxsize=4)
def _vignette() -> np.ndarray:
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W / 2, H / 2
    r = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2)
    v = 1.0 - 0.12 * np.clip(r - 0.35, 0, 1.4) / 1.05
    return v[..., None].astype(np.float32)

@functools.lru_cache(maxsize=4)
def _grain() -> np.ndarray:
    rng = np.random.default_rng(20261111)
    return rng.normal(0.0, 4.2, (H, W, 1)).astype(np.float32)

@functools.lru_cache(maxsize=8)
def _grid_layer(major: int = 96) -> Image.Image:
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x in range(0, W + 1, major):
        d.line([(x, 0), (x, H)], fill=GOLD + (16,), width=1)
    for y in range(0, H + 1, major):
        d.line([(0, y), (W, y)], fill=GOLD + (16,), width=1)
    for x in range(0, W + 1, major * 4):
        d.line([(x, 0), (x, H)], fill=GOLD + (30,), width=1)
    for y in range(0, H + 1, major * 4):
        d.line([(0, y), (W, y)], fill=GOLD + (30,), width=1)
    return im

@functools.lru_cache(maxsize=8)
def _scrim(side: str) -> Image.Image:
    a = np.zeros((H, W, 4), np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    if side == "bottom":
        g = np.clip((yy - H * 0.52) / (H * 0.48), 0, 1) ** 1.35
    elif side == "left":
        g = np.clip((W * 0.56 - xx) / (W * 0.56), 0, 1) ** 1.25
    elif side == "full":
        g = np.full((H, W), 0.34, np.float32)
    else:
        g = np.zeros((H, W), np.float32)
    a[..., 3] = g * 205
    a[..., 0], a[..., 1], a[..., 2] = BG[0], BG[1], BG[2]
    return Image.fromarray(a.astype(np.uint8), "RGBA")

# ───────────────────────── camera ─────────────────────────
def _warp(img: Image.Image, zoom: float, px: float, py: float) -> Image.Image:
    """Sub-pixel affine window; px,py = focus offset from center in INPUT px."""
    iw, ih = img.size
    a = 1.0 / zoom
    c = iw / 2.0 - (W / 2.0) / zoom - px
    e = 1.0 / zoom
    f = ih / 2.0 - (H / 2.0) / zoom - py
    return img.transform((W, H), Image.AFFINE, (a, 0.0, c, 0.0, e, f),
                         resample=Image.BICUBIC)

def _sway(t, amp=5.0):
    return (amp * math.sin(t * 2 * math.pi / 7.0),
            amp * 0.6 * math.cos(t * 2 * math.pi / 5.3))

def _bg_photo(t, name, z0, z1, px0, py0, px1, py1, scrim_side, grid=False,
              focus_tilt=None):
    k = state_index(t); u = state_progress(t, k)
    z = lerp(z0, z1, u)
    sx, sy = _sway(t)
    px = lerp(px0, px1, u) + sx
    py = lerp(py0, py1, u) + sy
    base = _warp(_cover(name), z, px, py).convert("RGBA")
    base.alpha_composite(_scrim(scrim_side))
    if grid:
        base.alpha_composite(_grid_layer())
    return base

# ───────────────────────── states / segments ─────────────────────────
STATES = [
    (0.000,   6.420), (6.420,  16.280), (16.280, 21.233), (21.233, 42.713),
    (43.193, 56.673), (56.873, 72.000), (72.000, 101.367), (101.367, 142.933),
    (142.933, 170.267), (170.267, 186.700), (186.700, 216.620), (216.700, 237.820),
]
BOUNDS = [6.420, 16.280, 21.233, 42.953, 56.773, 72.000, 101.367,
          142.933, 170.267, 186.700, 216.660]

def state_index(t: float) -> int:
    i = 0
    for k, (a, b) in enumerate(STATES):
        if t >= a:
            i = k
    return i

def state_progress(t: float, k: int | None = None) -> float:
    k = state_index(t) if k is None else k
    a, b = STATES[k]
    return lerp(0.0, 1.0, (t - a) / max(1e-6, b - a))

# card content segments — (state, t_in, t_out, accent, rows)
SEGMENTS = [
    (1,  1.10,  5.60, GOLD,
     [{"arrow": "up",   "text": "المئذنتان (القرن 15)"},
      {"arrow": "down", "text": "البرجان الحجريان: أقدم بـ +3 قرون"}]),
    (2,  7.40,  9.10, BRONZE, [{"text": "ارتفاع الضلفة: 6 أمتار"}]),
    (2, 10.00, 12.40, BRONZE, [{"text": "الوزن: ~4 أطنان"}]),
    (2, 13.30, 15.60, BRONZE, [{"text": "آلية الحركة: كرات برونزية"}]),
    (3, 17.30, 20.60, GOLD,
     [{"runs": [("text", "بوابة دفاعية"), ("arrow", "left"), ("text", "قاعدة لمئذنتين؟")]}]),
    (4, 22.30, 31.50, GOLD, [{"text": "تأسيس القاهرة: 969 م (المدخل الجنوبي)"}]),
    (4, 32.40, 41.90, GOLD, [{"text": "البناء الحجري: 1092 م — الوزير بدر الجمالي"}]),
    (5, 44.20, 55.90, BRONZE, [{"text": "تصميم دفاعي: برجان نصف دائريان ومدخل محصّن"}]),
    (6, 57.80, 71.20, GOLD,
     [{"runs": [("text", "قبيلة «زويلة» — شمال أفريقيا"), ("arrow", "left"),
                ("text", "القاهرة الفاطمية")]}]),
    (7, 73.00, 85.50, BRONZE,
     [{"text": "توثيق مركز الأبحاث الأمريكي: 6م ارتفاع × 3م عرض × 4 أطنان"}]),
    (7, 86.40, 100.60, BRONZE,
     [{"text": "نظام محامل حديث يحاكي الكرات البرونزية الأصلية"}]),
    (8, 102.40, 113.00, GOLD,
     [{"text": "القاعدة: بوابة فاطمية (1092 م)"},
      {"text": "القمة: مئذنتا مسجد المؤيد شيخ (القرن 15)"}]),
    (8, 113.90, 127.00, GOLD,
     [{"text": "القمة: مئذنتا مسجد المؤيد شيخ (القرن 15)"}]),
    (8, 127.90, 142.10, CRIMSON,
     [{"text": "مبنى واحد... وزمنان يفصل بينهما +3 قرون"}]),
    (9, 143.80, 169.50, GOLD,
     [{"text": "المنصة بين البرجين: متابعة انطلاق موكب المحمل السنوي"}]),
    (10, 171.20, 185.90, CRIMSON,
     [{"text": "1517 م — إعدام طومان باي ونهاية الحكم المملوكي"}]),
    (11, 187.60, 215.80, GOLD,
     [{"text": "مشروع الترميم والتوثيق (1998 – 2003) — مركز الأبحاث الأمريكي ووزارة الآثار"}]),
    (12, 217.60, 237.00, GOLD,
     [{"text": "الحلقة القادمة في رِواق: قصر المصمك"}]),
]

def _assert_no_overlap():
    segs = sorted(SEGMENTS, key=lambda s: s[1])
    for a, b in zip(segs, segs[1:]):
        assert b[1] >= a[2] + 0.50, f"content windows too close: {a} / {b}"
_assert_no_overlap()

# ───────────────────────── row + card (Auto-Fit Compact Pill) ─────────────────────────
def _arrow_px(canvas: Image.Image, x_center, y_center, size, direction, color, width=5):
    d = ImageDraw.Draw(canvas)
    if direction == "up":
        d.polygon([(x_center, y_center - size), (x_center - size * 0.62, y_center + size * 0.35),
                   (x_center + size * 0.62, y_center + size * 0.35)], fill=color)
        d.line([(x_center, y_center + size * 0.35), (x_center, y_center + size * 1.35)],
               fill=color, width=width)
    elif direction == "down":
        d.polygon([(x_center, y_center + size), (x_center - size * 0.62, y_center - size * 0.35),
                   (x_center + size * 0.62, y_center - size * 0.35)], fill=color)
        d.line([(x_center, y_center - size * 0.35), (x_center, y_center - size * 1.35)],
               fill=color, width=width)
    elif direction == "left":
        d.polygon([(x_center - size, y_center), (x_center + size * 0.35, y_center - size * 0.62),
                   (x_center + size * 0.35, y_center + size * 0.62)], fill=color)
        d.line([(x_center + size * 0.35, y_center), (x_center + size * 1.3, y_center)],
               fill=color, width=width)

def _row_image(row: dict, size: int, accent: tuple) -> Image.Image:
    """Render one content row (RTL) incl. any vector arrows -> tight RGBA image."""
    if "runs" in row:
        parts = []
        for kind, val in row["runs"]:
            if kind == "text":
                im = _text_png(val, size, IVORY, FONT_BOLD)
                parts.append(("img", im, im.size[0]))
            else:
                parts.append(("arrow", None, 44))
        gap = 18
        total = sum(p[2] for p in parts) + gap * (len(parts) - 1)
        hmax = max((p[1].size[1] if p[0] == "img" else size + 18) for p in parts)
        canvas = Image.new("RGBA", (total + 4, hmax + 4), (0, 0, 0, 0))
        cx = total + 2  # RTL: first part at the right
        cyc = hmax // 2 + 2
        for kind, im, pw in parts:
            cx -= pw
            if kind == "img":
                canvas.alpha_composite(im, (cx, cyc - im.size[1] // 2))
            else:
                _arrow_px(canvas, cx + pw // 2, cyc, 14, "left", accent + (255,), 5)
            cx -= gap
        return canvas
    txt = row["text"]
    tim = _text_png(txt, size, IVORY, FONT_BOLD)
    if row.get("arrow"):
        aw = 40
        canvas = Image.new("RGBA", (tim.size[0] + aw + 6, max(tim.size[1], size + 16)),
                           (0, 0, 0, 0))
        canvas.alpha_composite(tim, (aw, (canvas.size[1] - tim.size[1]) // 2))
        _arrow_px(canvas, aw // 2 + 4, canvas.size[1] // 2, 15, row["arrow"],
                  accent + (255,), 6)
        return canvas
    return tim

def card_state(t: float):
    """(rows, accent, alpha, slide_px) — alpha==0 -> NOTHING is drawn."""
    for (st, t_in, t_out, acc, rows) in SEGMENTS:
        if t_in <= t <= t_out:
            enter = ramp(t, t_in, t_in + FADE_IN_S)
            exit_ = 1.0 - ramp(t, t_out - FADE_OUT_S, t_out)
            alpha = enter * exit_
            slide = SLIDE_PX * (1.0 - enter) + SLIDE_PX * (1.0 - exit_)
            if alpha <= 0.02:
                return None, acc, 0.0, 0.0
            return rows, acc, alpha, slide
    return None, GOLD, 0.0, 0.0

def _measure_card(rows, accent):
    """Font size pick + tight box: returns (row_images, text_w, text_h, size)."""
    size = FONT_CARD
    imgs = [_row_image(r, size, accent) for r in rows]
    text_w = max(im.size[0] for im in imgs)
    if text_w > LONG_THRESHOLD:
        size = FONT_CARD_LONG
        imgs = [_row_image(r, size, accent) for r in rows]
        text_w = max(im.size[0] for im in imgs)
    gap = 10
    text_h = sum(im.size[1] for im in imgs) + gap * (len(imgs) - 1)
    return imgs, text_w, text_h, size

def draw_card(base: Image.Image, t: float):
    rows, accent, alpha, slide = card_state(t)
    if alpha <= 0.02 or rows is None:
        return                      # ZERO empty rectangles — ever.
    imgs, text_w, text_h, size = _measure_card(rows, accent)
    card_w = text_w + MARGIN_X * 2          # text_w + 64
    card_h = text_h + MARGIN_Y * 2          # text_h + 36
    x = CARD_RIGHT - card_w + int(round(slide))
    y = CARD_BOTTOM - card_h
    # rounded backdrop: blurred underlying frame @ rgba(14,19,26,0.85)
    crop = base.convert("RGB").crop((x, y, x + card_w, y + card_h))
    crop = crop.filter(ImageFilter.GaussianBlur(12)).convert("RGBA")
    crop.alpha_composite(Image.new("RGBA", (card_w, card_h), (14, 19, 26, 217)))
    # accent bar — RIGHT edge only, 6px
    ImageDraw.Draw(crop).rectangle(
        [card_w - ACCENT_W, CARD_RADIUS, card_w, card_h - CARD_RADIUS],
        fill=accent + (255,))
    # rows: right-aligned, 32px padding, 18px top
    ry = MARGIN_Y
    for im in imgs:
        crop.alpha_composite(im, (card_w - MARGIN_X - im.size[0], ry))
        ry += im.size[1] + 10
    # unit alpha + rounded mask
    a = crop.getchannel("A").point(lambda v: int(v * alpha))
    crop.putalpha(a)
    mask = Image.new("L", (card_w, card_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, card_w - 1, card_h - 1], radius=CARD_RADIUS, fill=255)
    mask = Image.fromarray(
        (np.asarray(mask, np.float32) * np.asarray(crop.getchannel("A"), np.float32)
         / 255.0).astype(np.uint8))
    base.paste(crop, (x, y), mask)

# ───────────────────────── annotations ─────────────────────────
def _dim_line(d, p0, p1, prog, color=GOLD, width=4, ticks=14):
    if prog <= 0.02:
        return
    x0, y0 = p0; x1, y1 = p1
    x = x0 + (x1 - x0) * min(prog, 1)
    y = y0 + (y1 - y0) * min(prog, 1)
    d.line([(x0, y0), (x, y)], fill=color, width=width)
    if prog >= 1.0:
        nx, ny = -(y1 - y0), (x1 - x0)
        L = math.hypot(nx, ny) or 1
        nx, ny = nx / L * ticks, ny / L * ticks
        d.line([(x0 - nx, y0 - ny), (x0 + nx, y0 + ny)], fill=color, width=width)
        d.line([(x1 - nx, y1 - ny), (x1 + nx, y1 + ny)], fill=color, width=width)

def _label_pill(base, text, cx, cy, size=32, fg=IVORY):
    """Callout label with subtle dark pill (contrast on bright imagery)."""
    im = _text_png(text, size, fg, FONT_BOLD)
    w, h = im.size
    ov = Image.new("RGBA", (w + 28, h + 18), (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle(
        [0, 0, w + 27, h + 17], radius=4, fill=(14, 19, 26, 190))
    ov.alpha_composite(im, (14, 9))
    base.alpha_composite(ov, (int(cx - (w + 28) / 2), int(cy - (h + 18) / 2)))

# ───────────────────────── per-state backgrounds (v2 assets) ─────────────────────────
def bg_state(t: float) -> Image.Image:
    k = state_index(t); u = state_progress(t, k)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    if k == 0:
        # STATE 01 — REAL photograph, cinematic tilt-down: minarets -> towers
        base = _bg_photo(t, "Bab_Zuwayla_Cairo_12_0864.jpg",
                         1.18, 1.08, 0, -880, 0, 860, "bottom")
        p1 = ramp(t, 1.6, 3.1); p2 = ramp(t, 3.4, 4.9)
        if p1 > 0:
            _dim_line(d, (1560, 210), (1560, 430), p1, GOLD)
            _label_pill(base, "مئذنتا المؤيد شيخ — القرن 15", 1560, 168, 30, GOLD)
        if p2 > 0:
            _dim_line(d, (400, 560), (400, 820), p2, IVORY)
            _label_pill(base, "أبراج حجرية فاطمية — 1092 م", 400, 872, 30, IVORY)

    elif k == 1:
        # STATE 02 — giant door leaf, blurred-fill 16:9 (no sidebars)
        sx, sy = _sway(t)
        base = _warp(_door_scene("door_front.png"), lerp(1.04, 1.10, u),
                     sx, sy).convert("RGBA")
        p1 = ramp(t, 7.6, 9.2); p2 = ramp(t, 10.2, 11.6); p3 = ramp(t, 13.4, 15.0)
        if p1 > 0:
            _dim_line(d, (1500, 150), (1500, 780), p1, GOLD)
            _label_pill(base, "6 م", 1560, 460, 34, IVORY)
        if p2 > 0:
            _dim_line(d, (1180, 850), (1740, 850), p2, BRONZE)
            _label_pill(base, "~4 طن", 1460, 806, 32, IVORY)
        if p3 > 0:
            cx, cy, r = 640, 905, int(95 * p3)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=BRONZE + (255,), width=6)
            _label_pill(base, "كرات برونزية — محور الحركة", 640, 752, 30, IVORY)

    elif k == 2:
        # STATE 03 — dramatic full gate photograph (no split line, no captions)
        base = _bg_photo(t, "Cairo,_bab_zuweila_02.jpeg",
                         1.12, 1.19, 0, -40, 0, 50, "bottom", grid=True)

    elif k == 3:
        # STATE 04 — Fatimid Cairo map 969 -> 1092
        base = _bg_photo(t, "خريطة_القاهرة_الفاطمية_وباب_زويلة(1).png",
                         1.18, 1.10, 170, 40, -150, -20, "left")
        p1 = ramp(t, 23.0, 25.0); p2 = ramp(t, 33.0, 35.0)
        if p1 > 0:
            cx, cy = int(lerp(1380, 1300, p1)), 700
            d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], outline=IVORY + (255,), width=5)
            d.line([(cx, cy), (cx, cy - 150 * p1)], fill=IVORY + (255,), width=3)
            _label_pill(base, "969 م — المدخل الجنوبي", cx, cy - 190, 32, IVORY)
        if p2 > 0:
            cx, cy = 1470, 520
            d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], outline=GOLD + (255,), width=6)
            _label_pill(base, "1092 م — البناء الحجري", cx, cy - 64, 32, GOLD)

    elif k == 4:
        # STATE 05 — architectural comparison/exploded board + sightlines
        base = _bg_photo(t, "bab_zuweila_architectural_transformation_board(1).png",
                         1.14, 1.26, -70, 40, 50, -50, "bottom", grid=True)
        p = ramp(t, 45.5, 48.5)
        if p > 0:
            for cx in (760, 1160):
                d.arc([cx - 120, 640, cx + 120, 880], 200, 340,
                      fill=BRONZE + (255,), width=6)
                for ang in (-40, -14, 14, 40):
                    a = math.radians(90 + ang)
                    x2 = cx + math.cos(a) * 460 * p
                    y2 = 760 + math.sin(a) * 460 * p
                    d.line([(cx, 760), (x2, y2)], fill=GOLD + (150,), width=3)
            _label_pill(base, "خط رؤية دفاعي", 1160, 340, 30, IVORY)

    elif k == 5:
        # STATE 06 — Zuweila tribe route sweep
        base = _bg_photo(t, "cutout_cairo_map.png", 1.20, 1.08, -220, 0, 200, 30, "bottom")
        p = ramp(t, 58.6, 66.0)
        pts = [(240, 420), (560, 500), (900, 560), (1230, 620), (1500, 680)]
        if p > 0:
            n = max(2, int(len(pts) * p))
            seg = pts[:n]
            for a, b in zip(seg, seg[1:]):
                d.line([a, b], fill=GOLD + (255,), width=6)
            if p < 1.0 and len(seg) >= 2:
                a, b = seg[-2], seg[-1]
                f = (p * len(pts)) % 1.0
                mx, my = lerp(a[0], b[0], f), lerp(a[1], b[1], f)
                d.ellipse([mx - 12, my - 12, mx + 12, my + 12], fill=IVORY + (255,))
            _label_pill(base, "شمال أفريقيا", 240, 360, 32, IVORY)
            if p > 0.85:
                d.ellipse([1474, 654, 1526, 706], outline=IVORY + (255,), width=5)
                _label_pill(base, "القاهرة الفاطمية", 1500, 756, 32, IVORY)

    elif k == 6:
        # STATE 07 — door + engineering dims + bearing comparison (no Latin)
        base = _warp(_door_scene("cutout_door.png"),
                     lerp(1.05, 1.13, u), *_sway(t)).convert("RGBA")
        p1 = ramp(t, 74.0, 77.0); p2 = ramp(t, 87.5, 91.0)
        if p1 > 0:
            _dim_line(d, (1460, 150), (1460, 760), p1, GOLD)
            _label_pill(base, "6 م", 1520, 450, 34, IVORY)
            _dim_line(d, (1180, 840), (1720, 840), p1, GOLD)
            _label_pill(base, "3 م", 1450, 796, 32, IVORY)
        if p2 > 0:
            cx1, cx2, cy, r = 1330, 1640, 540, 120
            d.ellipse([cx1 - r, cy - r, cx1 + r, cy + r], outline=BRONZE + (255,), width=7)
            d.ellipse([cx1 - r // 2, cy - r // 2, cx1 + r // 2, cy + r // 2],
                      fill=BRONZE + (255,))
            d.ellipse([cx2 - r, cy - r, cx2 + r, cy + r], outline=GOLD + (255,), width=7)
            for a in range(0, 360, 45):
                aa = math.radians(a + p2 * 180)
                d.line([(cx2, cy), (cx2 + math.cos(aa) * r, cy + math.sin(aa) * r)],
                       fill=GOLD + (200,), width=4)
            _label_pill(base, "كرات برونزية أصلية", cx1, cy + r + 46, 30, IVORY)
            _label_pill(base, "نظام محامل حديث", cx2, cy + r + 46, 30, IVORY)

    elif k == 7:
        # STATE 08 — architectural comparison board, smart zoom/pan between halves
        #   seg1 (102.4-113): focus LEFT half (Fatimid base 1092)
        #   seg2 (113.9-127): focus RIGHT half (Mamluk minarets 1415-1421)
        #   seg3 (127.9+):    pull wide, centered synthesis
        if t < 113.45:
            fx0, fx1, z0, z1 = 0.30, 0.36, 1.42, 1.34
        elif t < 127.45:
            fx0, fx1, z0, z1 = 0.70, 0.64, 1.42, 1.34
        else:
            fx0, fx1, z0, z1 = 0.50, 0.50, 1.06, 1.02
        uu = state_progress(t, 7)
        z = lerp(z0, z1, uu)
        fx = lerp(fx0, fx1, uu)
        sx, sy = _sway(t)
        img = _cover("bab_zuweila_architectural_transformation_board(1).png")
        iw, ih = img.size
        px = (fx - 0.5) * iw + sx
        py = sy
        base = _warp(img, z, px, py).convert("RGBA")
        base.alpha_composite(_scrim("bottom"))

    elif k == 8:
        # STATE 09 — platform + archival collage (labels top-right, bottom clean)
        base = _bg_photo(t, "Street_scene_with_the_gate_of_the_Metwaleys,_Cairo,_Egypt._T_Wellcome_V0049382.jpg",
                         1.14, 1.24, -60, -60, 70, 60, "left")
        p = ramp(t, 145.5, 147.5)
        if p > 0:
            w = int(520 * p); h = int(640 * p)
            if w > 8:
                arch = _load("Gate_of_Bab_Ez_Zuweleh,_Cairo_(1906)_-_TIMEA.jpg")
                arch = arch.resize((w, h), Image.LANCZOS)
                px_, py_ = 1300, 210
                base.paste(arch, (px_, py_))
                ImageDraw.Draw(base).rectangle(
                    [px_ - 6, py_ - 6, px_ + w + 6, py_ + h + 6],
                    outline=GOLD + (255,), width=5)
        pm = ramp(t, 152.0, 155.0)
        if pm > 0:
            cx, cy = 640, 470
            r = int(40 + 14 * math.sin(t * 3.1))
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD + (255,), width=6)
            d.line([(cx + r, cy), (cx + r + 150, cy - 90)], fill=GOLD + (255,), width=4)
            _label_pill(base, "المنصة بين البرجين", cx + r + 250, cy - 120, 30, GOLD)
        paste_text(base, "أرشيف — ويلكم / تايمآ", W - 56, 56, 26, IVORY,
                   anchor="rm", alpha=166)

    elif k == 9:
        # STATE 10 — somber 1517
        base = _bg_photo(t, "David_Roberts_minarets_Bab_Zuweyleh.jpg",
                         1.12, 1.22, 0, 0, 0, -60, "left")
        arr = np.asarray(base.convert("RGB"), np.float32)
        g = arr.mean(axis=2, keepdims=True)
        arr = np.clip((g * 0.75 + arr * 0.25 - 14) * 1.22, 0, 255)
        base = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
        base.alpha_composite(_scrim("left"))
        paste_text(base, "1517", 1520, 520, 300, (90, 60, 40), alpha=110)
        p = ramp(t, 172.5, 175.0)
        if p > 0:
            _dim_line(d, (240, 300), (240, 760), p, CRIMSON, width=8)
            _label_pill(base, "نهاية الحكم المملوكي", 430, 300, 34, IVORY)
        paste_text(base, "لوحة — ديفيد روبرتس", W - 56, 56, 26, IVORY,
                   anchor="rm", alpha=166)

    elif k == 10:
        # STATE 11 — restoration journey board + 1998–2003 timeline
        base = _bg_photo(t, "باب_زويلة_رحلة_ترميم_تاريخية(1).png",
                         1.14, 1.08, 150, 0, -130, 0, "bottom")
        p = ramp(t, 189.0, 194.0)
        if p > 0:
            y = 300
            x0, x1 = 360, int(lerp(360, 1560, p))
            d.line([(x0, y), (x1, y)], fill=GOLD + (255,), width=6)
            for frac, lab in ((0.0, "1998"), (0.5, "2001"), (1.0, "2003")):
                if p >= frac - 0.02:
                    x = int(lerp(360, 1560, frac))
                    d.ellipse([x - 16, y - 16, x + 16, y + 16],
                              fill=BG + (255,), outline=GOLD + (255,), width=5)
                    _label_pill(base, lab, x, y - 54, 32, IVORY)
            if p > 0.55:
                _label_pill(base, "توثيق · ترميم · إعادة تركيب الباب", 960, y + 64, 32, IVORY)

    else:
        # STATE 12 — synthesis pull-back + Qasr Masmak silhouette (logo stays top-left only)
        base = _bg_photo(t, "ruwaq_paper_art.png", 1.20, 1.02, 0, -60, 0, 30, "full")
        sil = ramp(t, 233.0, 235.2)
        if sil > 0:
            gy = 880
            col = GOLD + (int(230 * sil),)
            x0s = 660
            d.rectangle([x0s, gy - 240, x0s + 600, gy], outline=col, width=6)
            d.rectangle([x0s - 30, gy - 330, x0s + 70, gy], outline=col, width=6)
            d.rectangle([x0s + 530, gy - 330, x0s + 630, gy], outline=col, width=6)
            xx = x0s
            while xx < x0s + 600:
                d.rectangle([xx, gy - 240 - 26, xx + 34, gy - 240], fill=col)
                xx += 68
            _label_pill(base, "قصر المصمك", x0s + 300, gy + 56, 36, GOLD)

    base.alpha_composite(ov)
    return base

# ───────────────────────── chrome (clean HUD) ─────────────────────────
def draw_chrome(base: Image.Image, t: float):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    # bottom progress + state ticks
    d.rectangle([0, H - 6, W, H], fill=BG + (255,))
    d.rectangle([0, H - 6, int(W * t / DUR), H], fill=GOLD + (255,))
    for (a, b) in STATES:
        x = int(W * a / DUR)
        d.line([(x, H - 12), (x, H)], fill=GOLD + (160,), width=2)
    base.alpha_composite(ov)
    # official logo — ONCE, top-left, width 145, alpha 80%
    logo = _load("02-logo-horizontal-dark-bg.png")
    lw = LOGO_W
    lh = int(round(lw * logo.size[1] / logo.size[0]))
    lg = logo.resize((lw, lh), Image.LANCZOS)
    lg = lg.copy()
    lg.putalpha(lg.getchannel("A").point(lambda v: int(v * LOGO_ALPHA)))
    base.alpha_composite(lg, LOGO_POS)

# ───────────────────────── frame assembly ─────────────────────────
def _bg_processed(t: float) -> Image.Image:
    bg = bg_state(t)
    arr = np.asarray(bg.convert("RGB"), np.float32)
    arr = (arr * _vignette() + _grain() * 0.9).astype(np.float32)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")

def draw(t: float) -> np.ndarray:
    """PURE stateless frame: t (seconds) -> (H,W,3) uint8."""
    t = max(0.0, min(DUR - 1e-4, t))
    near = None
    for b in BOUNDS:
        if abs(t - b) <= 0.175:
            near = b; break
    if near is None:
        bg = _bg_processed(t)
    else:
        s1 = _bg_processed(max(0.0, t - 0.12))
        s2 = _bg_processed(t)
        s3 = _bg_processed(min(DUR - 1e-4, t + 0.12))
        a1 = np.asarray(s1, np.float32); a2 = np.asarray(s2, np.float32)
        a3 = np.asarray(s3, np.float32)
        bg = Image.fromarray(
            np.clip(a1 * 0.25 + a2 * 0.50 + a3 * 0.25, 0, 255).astype(np.uint8)
        ).convert("RGBA")
    draw_card(bg, t)
    draw_chrome(bg, t)
    frame = np.asarray(bg.convert("RGB"), np.float32)
    return np.clip(frame, 0, 255).astype(np.uint8)

if __name__ == "__main__":
    import sys
    tt = float(sys.argv[1]) if len(sys.argv) > 1 else 3.5
    f = draw(tt)
    Image.fromarray(f).save("/tmp/rv_test.png")
    print("ok", f.shape, f.dtype)
