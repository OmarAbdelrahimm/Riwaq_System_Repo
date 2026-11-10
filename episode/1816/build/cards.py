#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cards.py — the archive inserts: drawn, never photographed.

The chapter has nine graphic shots in a row. Photographs of paper would be a claim
we cannot support, and near-black fields read as nothing, so the inserts are built
as documents: a warm sheet lying on the ink table, ink marks and one gold thread.
Every mark is drawn onto its own layer and alpha-composited, because ImageDraw
overwrites alpha rather than blending it.
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from gfx import C, hexrgb, W, H, ar, font

PAPER = [(236, 226, 206), (212, 199, 171), (243, 234, 216)]


def _nz(size, scale, seed):
    w, h = size
    sw, sh = max(2, w // scale), max(2, h // scale)
    rng = np.random.default_rng(seed)
    a = rng.random((sh, sw)).astype(np.float32)
    im = Image.fromarray((a * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    a = np.asarray(im, np.float32) / 255.0
    return (a - a.min()) / (np.ptp(a) + 1e-6)


def sheet_tex(size, seed=3, tone=0):
    """paper: fine fibre, light mottling, no splotches that read as compression"""
    w, h = size
    tone = PAPER[tone % len(PAPER)]
    fibre = (_nz((w, h), 2, seed + 1) - 0.5) * 7.0
    mottle = (_nz((w, h), 140, seed + 2) - 0.5) * 9.0
    fibre_v = _nz((max(2, w // 6), h), 1, seed + 4)
    fibre_v = np.asarray(Image.fromarray((fibre_v * 255).astype(np.uint8))
                         .resize((w, h), Image.BILINEAR), np.float32) / 255.0
    n = fibre + mottle + (fibre_v - 0.5) * 5.0
    base = np.zeros((h, w, 3), np.float32)
    for c in range(3):
        base[..., c] = tone[c]
    base += n[..., None]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    base *= (1.05 - 0.18 * (0.5 * xx / w + 0.5 * yy / h))[..., None]     # light from top-left
    base *= np.array([1.0, 0.988, 0.963], np.float32)                    # warm bias
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))


def torn_mask(size, seed=5, inset=0.012, jitter=7):
    """rounded rectangle with a hand-cut wobble; no corner artefacts"""
    w, h = size
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    rng = random.Random(seed)
    x0, y0 = w * inset, h * inset * 1.6
    x1, y1 = w * (1 - inset), h * (1 - inset * 1.6)
    pts = []
    steps = 60
    for i in range(steps + 1):
        pts.append((x0 + (x1 - x0) * i / steps, y0 + rng.uniform(-jitter, jitter)))
    for i in range(int(steps * h / w) + 1):
        pts.append((x1 + rng.uniform(-jitter, jitter), y0 + (y1 - y0) * i / (steps * h / w)))
    for i in range(steps + 1):
        pts.append((x1 - (x1 - x0) * i / steps, y1 + rng.uniform(-jitter, jitter)))
    for i in range(int(steps * h / w) + 1):
        pts.append((x0 + rng.uniform(-jitter, jitter), y1 - (y1 - y0) * i / (steps * h / w)))
    d.polygon(pts, fill=255)
    return m.filter(ImageFilter.GaussianBlur(1.1))


def ink_field(size=(W, H), seed=9):
    w, h = size
    v = _nz((w, h), 300, seed) * 0.6 + _nz((w, h), 30, seed + 1) * 0.4
    ink = np.array(hexrgb(C['ink_deep']), np.float32)
    base = np.stack([ink[c] * (0.70 + 0.75 * v) for c in range(3)], -1)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    base *= (1.0 - 0.45 * np.clip(r - 0.3, 0, 1.6))[..., None]
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert('RGBA')


def _layer():
    return Image.new('RGBA', (W, H), (0, 0, 0, 0))


def draw_text(lay, text, size_px, color, cx, y, alpha=255, fkey='amiri_bold', anchor_x=True):
    d = ImageDraw.Draw(lay)
    f = font(fkey, size_px)
    s = ar(text)
    bb = d.textbbox((0, 0), s, font=f)
    tw = bb[2] - bb[0]
    x = (cx - tw / 2) if anchor_x else cx
    d.text((x - bb[0], y - bb[1]), s, font=f, fill=hexrgb(color) + (alpha,))
    return bb[3] - bb[1], tw


def rule(lay, y, x0, x1, color=None, alpha=170, thick=2):
    d = ImageDraw.Draw(lay)
    d.rectangle([x0, y, x1, y + thick], fill=hexrgb(color or C['gold']) + (alpha,))
    return lay


class Doc:
    """a sheet lying on the ink table; all marks are placed in sheet coordinates"""

    def __init__(self, seed=3, tone=0, scale=0.84, rot=-0.7, ar_ratio=16 / 9, bleed=False):
        """bleed=True: the sheet is the frame itself, no table edge, no tilt."""
        self.bleed = bleed
        if bleed:
            self.w, self.h = W, H
        else:
            self.w = int(W * scale)
            self.h = int(self.w / ar_ratio)
        s = sheet_tex((self.w, self.h), seed=seed, tone=tone).convert('RGBA')
        if bleed:
            m = Image.new('L', (self.w, self.h), 255)
            rot = 0
        else:
            m = torn_mask((self.w, self.h), seed=seed + 40)
        s.putalpha(m)
        if rot and not bleed:
            s = s.rotate(rot, expand=True, resample=Image.BICUBIC)
            m = m.rotate(rot, expand=True, resample=Image.BICUBIC)
        self.sheet = s
        self.mask = m
        canvas = ink_field()
        # shadow: mask blurred, then tinted, then composited under the sheet
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        if not bleed:
            sh.paste((0, 0, 0, 210), ((W - m.width) // 2 + 22, (H - m.height) // 2 + 30), m)
            sh = sh.filter(ImageFilter.GaussianBlur(40))
            canvas = Image.alpha_composite(canvas, sh)
        self.ox = (W - s.width) // 2
        self.oy = (H - s.height) // 2
        canvas.alpha_composite(s, (self.ox, self.oy))
        self.canvas = canvas
        self.lay = _layer()
        self.fullmask = Image.new('L', (W, H), 0)
        self.fullmask.paste(m, (self.ox, self.oy))

    # sheet-relative helpers -------------------------------------------------
    def X(self, f):
        return self.ox + self.sheet.width * f

    def Y(self, f):
        return self.oy + self.sheet.height * f

    def commit(self):
        """clip marks to the sheet, then composite them over it"""
        full = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        full.paste(self.lay, (0, 0), self.fullmask)   # marks clipped to the sheet
        return Image.alpha_composite(self.canvas, full)


def label_block(doc, text, y_bottom=0.90, size=104, rule_above=True):
    """bottom-anchored so Amiri's descenders never touch the cut edge"""
    cx = W / 2
    probe = ImageDraw.Draw(_layer())
    f = font('amiri_bold', size)
    bb = probe.textbbox((0, 0), ar(text), font=f)
    h = bb[3] - bb[1]
    y_top = doc.Y(y_bottom if not doc.bleed else y_bottom - 0.02) - h
    if rule_above:
        rule(doc.lay, y_top - 40, doc.X(0.19), doc.X(0.81), color=C['ink_deep'],
             alpha=90, thick=3)
    draw_text(doc.lay, text, size, C['ink_deep'], cx, y_top, alpha=250)
    return doc


# ------------------------------------------------------------------ surfaces
def card_map(label='', seed=71, arc=True, stamp=None, scale=0.84, rot=-0.7, tone=0, bleed=False):
    doc = Doc(seed=seed, scale=scale, rot=rot, tone=tone, bleed=bleed)
    d = ImageDraw.Draw(doc.lay)
    ink = hexrgb(C['ink_deep'])
    gx0, gx1 = doc.X(0.09), doc.X(0.91)
    gy0, gy1 = doc.Y(0.16), doc.Y(0.66)
    for i in range(9):
        y = gy0 + (gy1 - gy0) * i / 8
        d.line([(gx0, y), (gx1, y)], fill=ink + (30,), width=2)
    for i in range(13):
        x = gx0 + (gx1 - gx0) * i / 12
        d.line([(x, gy0), (x, gy1)], fill=ink + (26,), width=2)
    # distance marks along the route, drawn as ticks rather than a coastline:
    # the diagram must not imply a map we do not have.
    rng = random.Random(seed)
    for k in range(3):
        cx, cy = doc.X(0.30 + 0.20 * k), doc.Y(0.52 - 0.06 * (k % 2))
        rr = doc.sheet.height * 0.028
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=ink + (120,), width=3)
        d.ellipse([cx - rr * .3, cy - rr * .3, cx + rr * .3, cy + rr * .3], fill=ink + (120,))
    if arc:
        pts = [(doc.X(.14), doc.Y(.54)), (doc.X(.33), doc.Y(.30)),
               (doc.X(.52), doc.Y(.48)), (doc.X(.70), doc.Y(.26)), (doc.X(.87), doc.Y(.40))]
        t = _thread(pts, width=7)
        doc.lay = Image.alpha_composite(doc.lay, t)
    if label:
        label_block(doc, label, 0.905)
    if stamp:
        doc.lay = _stamp(doc, stamp, 0.72, 0.26)
    return doc.commit()


def card_ledger(label='', sub='', seed=91, stamp=None, scale=0.84, rot=-0.6, tone=0, bleed=False,
                pointer=None):
    doc = Doc(seed=seed, scale=scale, rot=rot, tone=tone, bleed=bleed)
    d = ImageDraw.Draw(doc.lay)
    ink = hexrgb(C['ink_deep'])
    top, bot = doc.Y(0.14), doc.Y(0.70)
    left, right = doc.X(0.12), doc.X(0.88)
    n = 9
    rng = random.Random(seed)
    for i in range(n):
        y = top + (bot - top) * i / (n - 1)
        d.line([(left, y), (right, y)], fill=ink + (58,), width=2)
        x = left + 6
        end = right - rng.uniform(20, doc.sheet.width * .22)
        while x < end:
            ln = rng.uniform(11, 40)
            yy = y - (bot - top) / n * 0.42
            d.line([(x, yy + rng.uniform(-4, 4)), (x + ln * .5, yy + rng.uniform(-8, 8)),
                    (x + ln, yy + rng.uniform(-3, 4))], fill=ink + (185,), width=rng.choice([2, 3, 3]))
            x += ln + rng.uniform(6, 18)
    if label:
        label_block(doc, label, 0.875, size=92)
    if sub:
        draw_text(doc.lay, sub, 48, C['stone'], W / 2, doc.Y(0.885), alpha=235)
    if stamp:
        doc.lay = _stamp(doc, stamp, 0.70, 0.22)
    return doc.commit()


def card_board(label='', pins=3, seed=101, stamp=None, scale=0.84, rot=0.5, tone=0, bleed=False,
               pin_x=(0.26, 0.50, 0.74), map_grid=True):
    doc = Doc(seed=seed, scale=scale, rot=rot, tone=tone, bleed=bleed)
    d = ImageDraw.Draw(doc.lay)
    ink = hexrgb(C['ink_deep'])
    rng = random.Random(seed)
    slots = [(0.28, 0.36), (0.52, 0.30), (0.72, 0.44), (0.36, 0.60), (0.60, 0.62)]
    for fx, fy in slots:
        cx, cy = doc.X(fx), doc.Y(fy)
        w2, h2 = doc.sheet.width * .085, doc.sheet.height * .105
        d.rectangle([cx - w2, cy - h2, cx + w2, cy + h2], fill=(255, 255, 255, 90),
                    outline=ink + (135,), width=3)
        for k in range(3):
            d.line([(cx - w2 * .68, cy - h2 * .45 + k * h2 * .42),
                    (cx + w2 * .68, cy - h2 * .45 + k * h2 * .42)], fill=ink + (60,), width=2)
    px = [doc.X(f) for f in pin_x][:max(1, pins)]
    anchors = [(x, doc.Y(0.26 + 0.10 * (i % 2))) for i, x in enumerate(px)]
    if len(anchors) >= 2:
        doc.lay = Image.alpha_composite(doc.lay, _thread(anchors, width=6))
        d = ImageDraw.Draw(doc.lay)
    if map_grid:
        d2 = ImageDraw.Draw(doc.lay)
        ruled = [doc.Y(f) for f in (0.15, 0.25, 0.35, 0.55, 0.65, 0.75)]
        ruled += [doc.Y(f) for f in (0.15, 0.35, 0.55, 0.75)]
        ruled = [doc.Y(f) for f in (0.15, 0.25, 0.45, 0.55, 0.65, 0.75)]
        for y in ruled:
            d2.line([(doc.X(0.04), y), (doc.X(0.96), y)], fill=ink + (16,), width=2)
    d = ImageDraw.Draw(doc.lay)
    for x, y in anchors:
        r = 13
        d.ellipse([x - r, y - r, x + r, y + r], fill=hexrgb(C['burgundy']) + (245,))
    if label:
        label_block(doc, label, 0.905, size=96)
    if stamp:
        doc.lay = _stamp(doc, stamp, 0.70, 0.24)
    return doc.commit()


def card_data(label='', seed=111, sun=True, stamp=None, scale=0.84, rot=-0.5, tone=0, bleed=False):
    doc = Doc(seed=seed, scale=scale, rot=rot, tone=tone, bleed=bleed)
    d = ImageDraw.Draw(doc.lay)
    gold = hexrgb(C['gold'])
    ink = hexrgb(C['ink_deep'])
    if sun:
        cx, cy = W / 2, doc.Y(0.40)
        r0 = doc.sheet.height * 0.115
        d.ellipse([cx - r0, cy - r0, cx + r0, cy + r0], fill=gold + (165,))
        for k in range(14):
            rr = r0 + k * doc.sheet.height * 0.016
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                      outline=gold + (max(200 - k * 13, 16),), width=3)
        d.line([(doc.X(0.14), cy + r0 * 2.3), (doc.X(0.86), cy + r0 * 2.3)],
               fill=ink + (70,), width=3)
    else:
        rng = random.Random(seed)
        pts = []
        for i in range(72):
            x = doc.X(0.13) + (doc.X(0.87) - doc.X(0.13)) * i / 71
            y = doc.Y(0.44) - doc.sheet.height * 0.10 * (i / 71) + rng.uniform(-6, 6)
            pts.append((x, y))
        d.line(pts, fill=ink + (175,), width=4)
        for i in range(0, 72, 9):
            d.ellipse([pts[i][0] - 6, pts[i][1] - 6, pts[i][0] + 6, pts[i][1] + 6],
                      fill=gold + (240,))
    if label:
        label_block(doc, label, 0.905)
    if stamp:
        doc.lay = _stamp(doc, stamp, 0.70, 0.70)
    return doc.commit()


def card_folder(seed=101, tone=2, pin=(0.50, 0.52)):
    """shot 21: a paper file laid open, one gold pin in it"""
    doc = Doc(seed=seed, bleed=True, tone=tone)
    d = ImageDraw.Draw(doc.lay)
    ink = hexrgb(C['ink_deep'])
    w2, h2 = W * 0.30, H * 0.30
    cx, cy = W * pin[0], H * pin[1]
    d.rectangle([cx - w2, cy - h2, cx + w2, cy + h2], fill=(255, 255, 255, 70),
                outline=ink + (130,), width=4)
    for k in range(3):
        y = cy - h2 * 0.55 + k * h2 * 0.36
        d.line([(cx - w2 * .76, y), (cx + w2 * .76, y)], fill=ink + (52,), width=3)
    d.line([(cx - w2 * .52, cy - h2 * .80), (cx + w2 * .12, cy - h2 * .80)],
           fill=ink + (90,), width=6)
    r = 17
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=hexrgb(C['gold']) + (245,))
    d.ellipse([cx - r * .5, cy - r * .5, cx + r * .5, cy + r * .5],
              fill=(255, 246, 226, 190))
    return doc.commit()


def card_pins(seed=102, tone=0, xs=(0.28, 0.50, 0.72), scale=0.84, rot=0.5):
    """shot 22: three pins planted along a route on a stretched map"""
    doc = Doc(seed=seed, scale=scale, rot=rot, tone=tone)
    d = ImageDraw.Draw(doc.lay)
    ink = hexrgb(C['ink_deep'])
    for i in range(9):
        y = doc.Y(0.12 + 0.09 * i)
        d.line([(doc.X(0.05), y), (doc.X(0.95), y)], fill=ink + (22,), width=2)
    for i in range(11):
        x = doc.X(0.05 + 0.09 * i)
        d.line([(x, doc.Y(0.12)), (x, doc.Y(0.84))], fill=ink + (20,), width=2)
    pts = [(doc.X(x), doc.Y(0.44 + 0.06 * (i % 2))) for i, x in enumerate(xs)]
    doc.lay = Image.alpha_composite(doc.lay, _thread(pts, width=7, alpha=190))
    d = ImageDraw.Draw(doc.lay)      # the composite replaced the layer
    for i, (x, y) in enumerate(pts):
        r = 16
        d.ellipse([x - r, y - r, x + r, y + r], fill=hexrgb(C['gold']) + (250,))
        d.ellipse([x - r * .45, y - r * .45, x + r * .45, y + r * .45],
                  fill=(255, 247, 230, 200))
        d.line([(x, y + r), (x, y + r * 3.2)], fill=ink + (120,), width=3)
    return doc.commit()


def card_blank(seed=103, tone=1, scale=0.62, rot=-1.4, stamp=None):
    """shot 27: a blank index card on the table, faint stamp, no name on it"""
    doc = Doc(seed=seed, scale=scale, rot=rot, tone=tone)
    d = ImageDraw.Draw(doc.lay)
    ink = hexrgb(C['ink_deep'])
    w2, h2 = doc.X(0.80) - doc.X(0.20), doc.Y(0.70) - doc.Y(0.26)
    cx, cy = (doc.X(0.20) + doc.X(0.80)) / 2, (doc.Y(0.26) + doc.Y(0.70)) / 2
    d.rectangle([cx - w2, cy - h2, cx + w2, cy + h2], fill=(252, 249, 240, 120),
                outline=ink + (120,), width=4)
    for k in range(4):
        y = cy - h2 * 0.5 + k * h2 * 0.33
        d.line([(cx - w2 * .82, y), (cx + w2 * .82, y)], fill=ink + (45,), width=3)
    if stamp:
        doc.lay = _stamp(doc, stamp, 0.50, 0.50, color=C['stone'])
    return doc.commit()


def card_plain(seed=141, tone=2, label=''):
    """shot 34 base: paper only. The thread leaves before the chapter title lands."""
    doc = Doc(seed=seed, bleed=True, tone=tone)
    if label:
        label_block(doc, label, 0.86)
    return doc.commit()


def thread_layer(seed=141, tone=2, path=None):
    """the same paper with only a thread on it: composited over card_plain and faded
    out, so the thread reads as leaving the frame."""
    doc = Doc(seed=seed, bleed=True, tone=tone)
    pts = [(W * a, H * b) for a, b in
           (path or [(.10, .52), (.40, .50), (.66, .54), (1.06, .44)])]
    doc.lay = Image.alpha_composite(doc.lay, _thread(pts, width=9))
    out = doc.commit()
    # keep only what differs from the bare sheet: the thread, not the paper
    plain = Image.open(f'/tmp/_plain_{seed}_{tone}.png').convert('RGB')
    a = np.asarray(out.convert('RGB'), np.int16)
    b = np.asarray(plain, np.int16)
    d = np.abs(a - b).max(2)
    alpha = np.clip((d - 6) * 8, 0, 255).astype(np.uint8)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    lay.paste(out.convert('RGB'), (0, 0), Image.fromarray(alpha))
    return lay


def card_cloud(seed=122, tone=2, scale=0.84, rot=-0.7):
    """shot 28: an unlocated cloud on an empty map, dashed ring around it"""
    doc = Doc(seed=seed, scale=scale, rot=rot, tone=tone)
    d = ImageDraw.Draw(doc.lay)
    ink = hexrgb(C['ink_deep'])
    for i in range(9):
        y = doc.Y(0.12 + 0.09 * i)
        d.line([(doc.X(0.05), y), (doc.X(0.95), y)], fill=ink + (24,), width=2)
    for i in range(11):
        x = doc.X(0.05 + 0.09 * i)
        d.line([(x, doc.Y(0.12)), (x, doc.Y(0.84))], fill=ink + (22,), width=2)
    cx, cy = doc.X(0.50), doc.Y(0.44)
    rx, ry = doc.sheet.width * 0.11, doc.sheet.height * 0.11
    # cloud: three overlapping soft discs
    c = _layer()
    cd = ImageDraw.Draw(c)
    for ox, oy, rr in [(-0.6, 0.1, 0.75), (0.0, -0.25, 0.95), (0.62, 0.12, 0.7)]:
        cd.ellipse([cx + ox * rx - rx * rr, cy + oy * ry - ry * rr,
                    cx + ox * rx + rx * rr, cy + oy * ry + ry * rr],
                   fill=(120, 118, 112, 150))
    c = c.filter(ImageFilter.GaussianBlur(18))
    doc.lay = Image.alpha_composite(doc.lay, c)
    d = ImageDraw.Draw(doc.lay)
    import math as _m
    for k in range(28):          # dashed ring
        a0 = 2 * _m.pi * k / 28
        a1 = a0 + 2 * _m.pi / 28 * 0.55
        d.arc([cx - rx * 1.7, cy - ry * 1.7, cx + rx * 1.7, cy + ry * 1.7],
              _m.degrees(a0), _m.degrees(a1), fill=ink + (150,), width=4)
    return doc.commit()


def card_thread(label='', seed=141, path=None, stamp=None, scale=0.88, rot=-0.4, tone=0,
                grid=True, bleed=False, beats=0, emphasis=False):
    doc = Doc(seed=seed, scale=scale, rot=rot, tone=tone, bleed=bleed)
    if grid:
        d0 = ImageDraw.Draw(doc.lay)
        ink0 = hexrgb(C['ink_deep'])
        span = (0.10, 0.90) if not doc.bleed else (0.02, 0.98)
        for i in range(1, 8):
            y = doc.Y(0.12 + 0.10 * i)
            d0.line([(W * span[0], y), (W * span[1], y)], fill=ink0 + (30,), width=2)
    f = path or [(.10, .56), (.34, .38), (.62, .50), (.90, .36)]
    pts = [(doc.X(a), doc.Y(b)) for a, b in f]
    if beats:
        # three strands starting apart and converging on the same point; the
        # strongest is wider and brighter. Width and alpha only, no glow tricks.
        end = pts[-1]
        starts = [(doc.X(f), doc.Y(g)) for f, g in
                  ((0.06, 0.30), (0.06, 0.55), (0.06, 0.78))][:beats]
        for i, st in enumerate(starts):
            mid = ((st[0] + end[0]) / 2, (st[1] + end[1]) / 2 + doc.sheet.height * 0.04)
            k = (i == beats - 1)
            t = _thread([st, mid, end], width=16 if (emphasis and k) else 8,
                        alpha=252 if (emphasis and k) else 170)
            doc.lay = Image.alpha_composite(doc.lay, t)
    else:
        doc.lay = Image.alpha_composite(doc.lay, _thread(pts, width=9))
    if label:
        label_block(doc, label, 0.905)
    if stamp:
        doc.lay = _stamp(doc, stamp, 0.70, 0.26)
    return doc.commit()


# ------------------------------------------------------------------ primitives
def _thread(pts, width=6, alpha=228, offset=(0, 0)):
    """gold thread, catmull-rom, with a soft glow underneath"""
    lay = _layer()
    d = ImageDraw.Draw(lay)
    if offset != (0, 0):
        pts = [(x + offset[0], y + offset[1]) for x, y in pts]
    if len(pts) < 2:
        return lay
    dense = []
    for i in range(len(pts) - 1):
        p0 = pts[max(i - 1, 0)]; p1 = pts[i]; p2 = pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        for t in np.linspace(0, 1, 28, endpoint=False):
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t +
                       (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t +
                       (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            dense.append((x, y))
    deep = (140, 112, 56)
    d.line(dense, fill=deep + (min(255, alpha),), width=width, joint='curve')
    d.line(dense, fill=hexrgb(C['gold_light']) + (200,), width=max(2, int(width * .45)),
           joint='curve')
    return lay


def _stamp(doc, text, fx, fy, color=None, size=70):
    color = color or C['burgundy']
    tmp = Image.new('RGBA', (int(doc.sheet.width * .46), 230), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    f = font('amiri_bold', size)
    s = ar(text)
    bb = d.textbbox((0, 0), s, font=f)
    tw = bb[2] - bb[0]
    pad = 30
    d.rounded_rectangle([(tmp.width - tw) / 2 - pad, 34, (tmp.width + tw) / 2 + pad,
                         34 + (bb[3] - bb[1]) + pad * 2],
                        radius=6, outline=hexrgb(color) + (240,), width=6)
    d.text(((tmp.width - tw) / 2 - bb[0], 34 + pad - bb[1]), s, font=f,
           fill=hexrgb(color) + (240,))
    a = np.asarray(tmp, np.float32)
    a[..., 3] *= (0.60 + 0.6 * _nz((tmp.width, tmp.height), 5, 77))   # uneven ink
    tmp = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).rotate(-8, expand=True,
                                                                      resample=Image.BICUBIC)
    out = doc.lay.copy()
    out.alpha_composite(tmp, (int(doc.X(fx) - tmp.width / 2), int(doc.Y(fy) - tmp.height / 2)))
    return out


if __name__ == '__main__':
    specs = [
        ('map',    card_map(label='آلاف الكيلومترات', seed=71)),
        ('ledger', card_ledger(label='نيو إنجلاند · 8 يونيو', seed=91)),
        ('board',  card_board(label='ثلاثة مشتبهين', pins=3, seed=102)),
        ('data',   card_data(label='فترة دالتون', sun=True, seed=112)),
        ('thread', card_thread(label='أقوى تأثير', seed=104,
                               path=[(.08, .60), (.34, .40), (.66, .54), (.92, .36)])),
        ('stamp',  card_map(label='غير محدد', seed=121, arc=False, stamp='غير محدد')),
    ]
    for k, im in specs:
        im.convert('RGB').resize((960, 540), Image.LANCZOS).save(f'/tmp/c_{k}.png')
    grp = Image.new('RGB', (960 * 3, 540 * 2))
    for i, (k, _) in enumerate(specs):
        grp.paste(Image.open(f'/tmp/c_{k}.png'), ((i % 3) * 960, (i // 3) * 540))
    grp.save('/tmp/cards_grid3.png')
    print('ok')
