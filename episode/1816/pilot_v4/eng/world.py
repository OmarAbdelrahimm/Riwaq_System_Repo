#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eng4/world.py — the dark-mode map, drawn at full resolution from Natural Earth.

Geometry comes from the public-domain Natural Earth 1:110m vectors (verified
naturalearthdata.com/about/terms-of-use). Nothing here is a raster grab: every
coastline is projected once into a 9x supersampled path, then stroked so the
result stays crisp when the camera pushes into it.
"""
import math
import numpy as np
import shapefile
from PIL import Image, ImageDraw, ImageFilter

SHP = '/tmp/ne/geopandas/datasets/naturalearth_lowres/naturalearth_lowres'
SS = 6  # supersample factor for the map raster

MAP_W, MAP_H = 1920, 1080

SEA = (10, 13, 17)
LAND = (26, 30, 34)
LAND_HI = (34, 39, 44)
COAST = (74, 84, 92)
GRID = (22, 27, 32)
GOLD = (201, 168, 106)


def load_rings():
    """list of (list of (lon, lat)), skipping Antarctica"""
    sf = shapefile.Reader(SHP)
    out = []
    for shp in sf.shapes():
        pts = list(shp.points)
        parts = list(shp.parts) + [len(pts)]
        for i in range(len(parts) - 1):
            ring = pts[parts[i]:parts[i + 1]]
            if len(ring) < 4:
                continue
            lat = sum(p[1] for p in ring) / len(ring)
            if lat < -58:
                continue
            out.append(ring)
    return out


def project(lon, lat, x0, y0, w, h, lon_a, lon_b, lat_a, lat_b):
    """equirectangular into the (x0,y0,w,h) rect"""
    x = x0 + (lon - lon_a) / (lon_b - lon_a) * w
    y = y0 + (lat_b - lat) / (lat_b - lat_a) * h
    return x, y


class Map:
    """a projected, supersampled land mask + a shade layer, cropped on demand"""

    def __init__(self, lon_a=-126, lon_b=142, lat_a=-22, lat_b=74,
                 x0=40, y0=70, w=1840, h=940, ss=SS):
        self.rings = load_rings()
        self.box = (lon_a, lon_b, lat_a, lat_b)
        self.x0, self.y0, self.w, self.h = x0, y0, w, h
        self.ss = ss
        self.W, self.H = w * ss, h * ss
        self._edge = None
        self.mask, self.shade = self._raster()

    def _pts(self, ring):
        lon_a, lon_b, lat_a, lat_b = self.box
        x = (np.array([p[0] for p in ring]) - lon_a) / (lon_b - lon_a) * self.W
        y = (lat_b - np.array([p[1] for p in ring])) / (lat_b - lat_a) * self.H
        return list(zip(x.tolist(), y.tolist()))

    def px(self, lon, lat):
        lon_a, lon_b, lat_a, lat_b = self.box
        return (self.x0 + (lon - lon_a) / (lon_b - lon_a) * self.w,
                self.y0 + (lat_b - lat) / (lat_b - lat_a) * self.h)

    def _raster(self):
        mask = Image.new('L', (self.W, self.H), 0)
        d = ImageDraw.Draw(mask)
        for ring in self.rings:
            d.polygon(self._pts(ring), fill=255)
        mask = mask.resize((self.w, self.h), Image.LANCZOS)

        # inner shading: erode the mask a little and lift its edges
        small = mask.resize((self.w // 4, self.h // 4), Image.LANCZOS)
        blur = small.filter(ImageFilter.GaussianBlur(2.5)).resize((self.w, self.h), Image.LANCZOS)
        shade = Image.new('L', (self.w, self.h), 0)
        a = np.asarray(mask, np.float32) / 255.0
        b = np.asarray(blur, np.float32) / 255.0
        inner = np.clip(a - b, 0, 1) ** 0.6  # glow just inside the coast
        shade = Image.fromarray((inner * 255).astype(np.uint8))
        shade = shade.filter(ImageFilter.GaussianBlur(3.0))
        return mask, shade

    def coast_edge(self):
        """the coastline as an IMAGE derived from the fill boundary.

        Stroking the raw 110m rings separately let a Natural Earth closure seam in
        Kazakhstan draw a straight line across open steppe (stroke and fill disagreed).
        Deriving the line from the mask guarantees the two can never contradict.
        """
        from PIL import ImageFilter
        if getattr(self, '_edge', None) is None:
            m = self.mask.point(lambda v: 255 if v > 127 else 0)
            er = m.filter(ImageFilter.MinFilter(3))
            a = np.asarray(m, np.float32) / 255.0
            b = np.asarray(er, np.float32) / 255.0
            e = np.clip(a - b, 0, 1) * 255.0
            self._edge = Image.fromarray(e.astype('uint8')).filter(ImageFilter.GaussianBlur(0.6))
        return self._edge

    def coast_path(self):
        """the same rings as flat polylines in canvas pixels (for crisp strokes)"""
        out = []
        for ring in self.rings:
            pts = [(self.x0 + (p[0] - self.box[0]) / (self.box[1] - self.box[0]) * self.w,
                    self.y0 + (self.box[3] - p[1]) / (self.box[3] - self.box[2]) * self.h) for p in ring]
            out.append(pts)
        return out


def compose_map(canvas, m, t, ox=0, oy=0, label=True, cam=1.0, focus=None):
    """draw the map onto a canvas at (ox,oy) with a dark-mode look"""
    W, H = canvas.size
    lay = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)

    # basemap plate
    base = Image.new('RGB', (m.w, m.h), SEA)
    land = Image.new('RGB', (m.w, m.h), LAND)
    base.paste(land, (0, 0), m.mask)
    hi = Image.new('RGB', (m.w, m.h), LAND_HI)
    base = Image.composite(hi, base, m.shade)
    lay.paste(base, (ox, oy))

    # graticule
    for lon in range(-120, 150, 30):
        x, _ = m.px(lon, 0)
        d.line([(x, 0), (x, m.h)], fill=GRID + (255,), width=1)
    for lat in range(-10, 80, 20):
        _, y = m.px(0, lat)
        d.line([(0, y), (m.w, y)], fill=GRID + (255,), width=1)

    # coastline: composited from the fill boundary so line and land agree exactly
    coast = Image.new('RGB', (m.w, m.h), COAST)
    lay.paste(coast, (ox, oy), m.coast_edge().point(lambda v: int(v * 0.92)))

    # vignette the plate edges so it sits into the dark frame
    vig = Image.new('L', (m.w, m.h), 0)
    dv = ImageDraw.Draw(vig)
    dv.rectangle([0, 0, m.w, m.h], outline=255, width=3)
    vig = vig.filter(ImageFilter.GaussianBlur(60))
    dark = Image.new('RGBA', (m.w, m.h), (0, 0, 0, 0))
    dark.putalpha(vig.point(lambda v: int(v * 0.55)))
    lay.alpha_composite(dark, (ox, oy))

    # offset onto the canvas
    out = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    out.alpha_composite(lay)
    return out


def arc_points(pts, upto=1.0, step=2.0):
    """resample a polyline up to a fraction of its arc length"""
    segs = []
    total = 0.0
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        L = math.hypot(x1 - x0, y1 - y0)
        if L > 0:
            segs.append((x0, y0, x1, y1, L, total))
            total += L
    if not segs:
        return [], 0.0
    stop = total * max(0.0, min(1.0, upto))
    out = []
    s = 0.0
    while s <= stop:
        for x0, y0, x1, y1, L, s0 in segs:
            if s0 <= s <= s0 + L:
                u = (s - s0) / L
                out.append((x0 + (x1 - x0) * u, y0 + (y1 - y0) * u))
                break
        s += step
    return out, total


def dashed_line(draw, pts, color, width=3, dash=18, gap=13, upto=1.0):
    """draw a dashing polyline up to a fraction of its length (the thread drawing itself)"""
    sampled, total = arc_points(pts, upto)
    if not sampled:
        return 0.0
    for i in range(0, len(sampled) - 1):
        s = i * 2.0
        if (s % (dash + gap)) < dash:
            draw.line([sampled[i], sampled[i + 1]], fill=color, width=width)
    return total
