#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_thumbnails.py — two YouTube-ready thumbnails (1280x720) for RIW_001 Bab Zuwayla.
Design rules: <=6 words, mobile-legible, high contrast, brand palette, logo bottom-left,
gold RTL anchor bar, no text in bottom-right (timestamp safe zone), <2MB JPG.
Arabic rendered via arabic_reshaper + python-bidi (no raqm in this Pillow build).
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import arabic_reshaper
from bidi.algorithm import get_display

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "google_drive")
OUT = os.path.join(ROOT, "previews")
os.makedirs(OUT, exist_ok=True)

W, H = 1280, 720
GOLD = (200, 157, 84)
IVORY = (234, 224, 208)
INK = (10, 13, 18)
FONT_BOLD = os.path.join(ROOT, "public/fonts/IBMPlexSansArabic-Bold.ttf")
FONT_MED = os.path.join(ROOT, "public/fonts/IBMPlexSansArabic-Medium.ttf")

_reshaper = arabic_reshaper.ArabicReshaper(configuration={
    "delete_harakat": False, "support_ligatures": True})


def ar(s: str) -> str:
    return get_display(_reshaper.reshape(s))


def font(path, size):
    return ImageFont.truetype(path, size)


def cover(im, w=W, h=H, vpos=0.5):
    s = max(w / im.width, h / im.height)
    nw, nh = int(im.width * s + 0.5), int(im.height * s + 0.5)
    im2 = im.resize((nw, nh), Image.LANCZOS)
    x = (nw - w) // 2
    y = int((nh - h) * vpos)
    return im2.crop((x, y, x + w, y + h))


def scrim(base, side="right", frac=0.55, max_a=0.82):
    """Linear dark gradient over one side for text legibility."""
    arr = np.asarray(base).astype(np.float32)
    xs = np.linspace(0, 1, W, dtype=np.float32)
    if side == "right":
        ramp = np.clip((xs - (1 - frac)) / frac, 0, 1) ** 1.4
    else:
        ramp = np.clip(((1 - frac) - xs) / frac, 0, 1) ** 1.4
    a = (ramp * max_a)[None, :, None]
    arr = arr * (1 - a) + np.array(INK, np.float32)[None, None, :] * a
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def bottom_scrim(base, frac=0.34, max_a=0.7):
    arr = np.asarray(base).astype(np.float32)
    ys = np.linspace(0, 1, H, dtype=np.float32)
    ramp = np.clip((ys - (1 - frac)) / frac, 0, 1) ** 1.5
    a = (ramp * max_a)[:, None, None]
    arr = arr * (1 - a) + np.array(INK, np.float32)[None, None, :] * a
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def vignette(base, strength=0.38):
    arr = np.asarray(base).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    v = 1 - strength * np.clip((d - 0.55) / 0.9, 0, 1) ** 1.6
    arr *= v[:, :, None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def text_layer(lines, fnt, fill, stroke, align_right_x, y0, lh, shadow=True):
    """Draw shaped Arabic lines right-aligned; returns (layer, bottom_y)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y = y0
    for s, f, col in lines:
        t = ar(s)
        bb = d.textbbox((0, 0), t, font=f, stroke_width=stroke)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        x = align_right_x - tw - bb[0]
        if shadow:
            d.text((x + 4, y + 5), t, font=f, fill=(0, 0, 0, 170),
                   stroke_width=stroke, stroke_fill=(0, 0, 0, 210))
        d.text((x, y), t, font=f, fill=col, stroke_width=stroke,
               stroke_fill=stroke_color(stroke))
        y += th + lh
    return layer, y


def stroke_color(w):
    return (8, 10, 14, 255)


def paste_logo(base, x=40, y=None, width=230, alpha=0.95):
    logo = Image.open(os.path.join(IMG, "02-logo-horizontal-dark-bg.png")).convert("RGBA")
    h = int(logo.height * width / logo.width)
    logo = logo.resize((width, h), Image.LANCZOS)
    if y is None:
        y = H - h - 34
    if alpha < 1:
        a = logo.getchannel("A").point(lambda v: int(v * alpha))
        logo.putalpha(a)
    base.paste(logo, (x, y), logo)
    return base


def gold_bar(base, x_right_edge, y_top, y_bot, w=8):
    d = ImageDraw.Draw(base)
    d.rectangle([x_right_edge - w, y_top, x_right_edge, y_bot], fill=GOLD)
    return base


def text_block_size(lines, stroke=5):
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    maxw, tot = 0, 0
    for s, f, _ in lines:
        t = ar(s)
        bb = d.textbbox((0, 0), t, font=f, stroke_width=stroke)
        maxw = max(maxw, bb[2] - bb[0])
        tot += (bb[3] - bb[1])
    return maxw, tot


def make_A():
    """Hook: mystery of the two minarets (pairs with title A)."""
    base = Image.open(os.path.join(IMG, "Bab_Zuwayla_Cairo_12_0864.jpg")).convert("RGB")
    base = cover(base, vpos=0.12)          # top band: minarets + towers
    base = ImageEnhance.Color(base).enhance(0.82)
    base = ImageEnhance.Brightness(base).enhance(0.78)
    base = scrim(base, "right", frac=0.60, max_a=0.86)
    base = scrim(base, "left", frac=0.22, max_a=0.45)
    base = bottom_scrim(base, frac=0.30, max_a=0.65)
    base = vignette(base, 0.42)

    f_k = font(FONT_MED, 46)
    f_m1 = font(FONT_BOLD, 96)
    f_m2 = font(FONT_BOLD, 88)
    f_s = font(FONT_MED, 44)
    lines = [
        ("باب زويلة", f_k, GOLD + (255,)),
        ("مئذنتان ليستا", f_m1, IVORY + (255,)),
        ("من بناء البوابة", f_m2, IVORY + (255,)),
        ("زمنان في مبنى واحد", f_s, (214, 205, 190, 255)),
    ]
    xr = W - 76
    tw, th = text_block_size(lines)
    lh = 16
    y0 = (H - (th + lh * (len(lines) - 1))) // 2 - 8
    layer, ybot = text_layer(lines, None, None, 5, xr, y0, lh)
    base = Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")
    base = gold_bar(base, W - 44, y0 - 10, ybot + 4)
    base = paste_logo(base)
    out = os.path.join(OUT, "THUMBNAIL_A_RIWAQ_BABZUWEILA.jpg")
    base.save(out, quality=93, subsampling=1)
    return out


def make_B():
    """Hook: giant number — 4-ton doors on bronze balls (pairs with title B)."""
    base = Image.open(os.path.join(IMG, "Cairo,_bab_zuweila_02.jpeg")).convert("RGB")
    base = cover(base, vpos=0.5)
    base = ImageEnhance.Color(base).enhance(0.88)
    base = ImageEnhance.Brightness(base).enhance(0.74)
    base = scrim(base, "right", frac=0.58, max_a=0.87)
    base = bottom_scrim(base, frac=0.28, max_a=0.6)
    base = vignette(base, 0.44)

    f_k = font(FONT_MED, 46)
    f_big = font(FONT_BOLD, 168)
    f_s1 = font(FONT_BOLD, 52)
    f_s2 = font(FONT_MED, 44)
    lines = [
        ("باب زويلة", f_k, IVORY + (255,)),
        ("4 أطنان", f_big, GOLD + (255,)),
        ("تتحرك على كرات برونزية", f_s1, IVORY + (255,)),
        ("وأبوابها6 أمتار!", f_s2, (214, 205, 190, 255)),
    ]
    xr = W - 76
    tw, th = text_block_size(lines)
    lh = 14
    y0 = (H - (th + lh * (len(lines) - 1))) // 2 - 6
    layer, ybot = text_layer(lines, None, None, 5, xr, y0, lh)
    base = Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")
    base = gold_bar(base, W - 44, y0 - 10, ybot + 4)
    base = paste_logo(base)
    out = os.path.join(OUT, "THUMBNAIL_B_RIWAQ_BABZUWEILA.jpg")
    base.save(out, quality=93, subsampling=1)
    return out


def qa(path, tag):
    im = Image.open(path)
    size = os.path.getsize(path)
    arr = np.asarray(im).astype(np.float32)
    # text zone: right half where headline sits
    zone = arr[140:600, 520:1200]
    lum = zone.mean(2)
    bright = float((lum > 145).mean())        # ivory/gold text pixels (post-JPEG)
    dark_bg = float((lum < 70).mean())        # scrim behind text
    # logo zone bottom-left
    lz = arr[600:700, 30:280]
    # timestamp safe corner (bottom-right) must stay free of bright text
    tr = arr[640:710, 1100:1270].mean()
    ok = (im.size == (W, H) and size < 2_000_000 and im.mode == "RGB"
          and bright > 0.04 and dark_bg > 0.30 and lz.std() > 8 and tr < 140)
    print(f"{tag}: size={im.size} mode={im.mode} bytes={size} "
          f"text_px={bright:.3f} scrim={dark_bg:.3f} logo_std={lz.std():.1f} "
          f"corner_mean={tr:.1f} -> {'PASS' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    a = make_A()
    b = make_B()
    ok = qa(a, "A") and qa(b, "B")
    print("ALL PASS" if ok else "QA FAILED")
    sys.exit(0 if ok else 1)
