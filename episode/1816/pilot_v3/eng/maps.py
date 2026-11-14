#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
eng/maps.py — real maps from Natural Earth, no abstract squiggles.

Source: Natural Earth 1:110m admin-0 countries, shipped inside the geopandas 0.14.4
wheel (build-time download from PyPI, not runtime).
Licence: Natural Earth Terms of Use — public domain, commercial use allowed, no
permission and no credit required (read at
https://www.naturalearthdata.com/about/terms-of-use/).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import shapefile

SHP = '/tmp/ne/geopandas/datasets/naturalearth_lowres/naturalearth_lowres'
_CACHE = {}


def load_shapes(path=SHP):
    if path in _CACHE:
        return _CACHE[path]
    sf = shapefile.Reader(path)
    shapes = []
    for sh in sf.shapes():
        pts = np.asarray(sh.points, np.float64)
        parts = list(sh.parts) + [len(pts)]
        for i in range(len(parts) - 1):
            shapes.append(pts[parts[i]:parts[i + 1]])
    _CACHE[path] = shapes
    return shapes


def project(lon, lat, kind='ortho', lon0=-30.0, lat0=45.0, w=1920, h=1080, scale=1.0,
            cx=0.5, cy=0.5):
    lon = np.asarray(lon, np.float64)
    lat = np.asarray(lat, np.float64)
    if kind == 'ortho':
        l, p = np.radians(lon), np.radians(lat)
        l0, p0 = math.radians(lon0), math.radians(lat0)
        cosc = np.sin(p0) * np.sin(p) + np.cos(p0) * np.cos(p) * np.cos(l - l0)
        ok = cosc > 0
        x = np.cos(p) * np.sin(l - l0)
        y = np.cos(p0) * np.sin(p) - np.sin(p0) * np.cos(p) * np.cos(l - l0)
        R = min(w, h) * 0.46 * scale
        return cx * w + x * R, cy * h - y * R, ok
    X = cx * w + (lon - lon0) / 360.0 * w * scale
    Y = cy * h - (lat - lat0) / 180.0 * h * scale
    return X, Y, np.ones_like(X, bool)


def map_sprite(w=1920, h=1080, kind='equirect', lon0=-30, lat0=45, scale=1.0,
               land=(236, 226, 205, 255), outline=(120, 110, 92, 130), lw=2,
               aa=2, disc_fade=2.0):
    """Land silhouette as an RGBA sprite. For the orthographic view each country is
    filled on its own layer and clipped by the globe disc, so a country that wraps
    the limb cannot close across the ocean and paint a wedge."""
    W2, H2 = w * aa, h * aa
    im = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
    shapes = load_shapes()
    R = min(W2, H2) * 0.46 * scale
    disc = Image.new('L', (W2, H2), 0)
    ImageDraw.Draw(disc).ellipse([W2 * 0.5 - R, H2 * 0.5 - R, W2 * 0.5 + R, H2 * 0.5 + R],
                                 fill=255)
    if disc_fade:
        disc = disc.filter(ImageFilter.GaussianBlur(disc_fade * aa))
    for pts in shapes:
        lon, lat = pts[:, 0], pts[:, 1]
        X, Y, ok = project(lon, lat, kind, lon0, lat0, W2, H2, scale)
        if kind == 'ortho' and ok.mean() < 0.55:
            continue
        layer = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        run = []
        for i in range(len(X)):
            if ok[i]:
                run.append((float(X[i]), float(Y[i])))
            else:
                if len(run) > 2:
                    d.polygon(run, fill=land, outline=outline)
                run = []
        if len(run) > 2:
            d.polygon(run, fill=land, outline=outline)
        if kind == 'ortho':
            a = Image.composite(layer.split()[-1], Image.new('L', (W2, H2), 0), disc)
            layer.putalpha(a)
        im = Image.alpha_composite(im, layer)
    return im.resize((w, h), Image.LANCZOS)


def route_points(waypoints, kind='equirect', lon0=-30, lat0=45, w=1920, h=1080, scale=1.0,
                 steps=48):
    """waypoints [(lon,lat), ...] -> screen points"""
    out = []
    for i in range(len(waypoints) - 1):
        a, b = waypoints[i], waypoints[i + 1]
        for s in range(steps):
            t = s / steps
            X, Y, ok = project(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t,
                               kind, lon0, lat0, w, h, scale)
            if ok:
                out.append((float(X), float(Y)))
    X, Y, ok = project(waypoints[-1][0], waypoints[-1][1], kind, lon0, lat0, w, h, scale)
    if ok:
        out.append((float(X), float(Y)))
    return out


# ---------------------------------------------------------------- physical sheet
def make_map_sheet(mw, mh, lon0, lat0, scale, seed=44, kind='equirect',
                   land=(230, 217, 188, 255), sea=(104, 112, 108), tape_corners=True):
    """A paper map as a physical object: painted ocean, cream land, open country
    borders, torn deckle edge, tape at two corners, soft shadow. The sea is slate,
    not the colour of the paper, so land reads as land instead of a cream card."""
    from eng.core import paper_sheet, torn_rect, drop_shadow, tape
    spr = map_sprite(mw, mh, kind, lon0, lat0, scale, land=land,
                     outline=(70, 64, 55, 150), lw=2)
    sea_im = Image.new('RGBA', (mw, mh), tuple(sea) + (255,))
    d = ImageDraw.Draw(sea_im)
    rng = np.random.default_rng(seed)
    for _ in range(90):                       # marbling, so the sea is not flat ink
        x, y = rng.uniform(0, mw), rng.uniform(0, mh)
        r = rng.uniform(40, 150)
        d.ellipse([x - r, y - r * 0.5, x + r, y + r * 0.5],
                  fill=(sea[0] + int(rng.integers(-8, 9)), sea[1] + int(rng.integers(-8, 9)),
                        sea[2] + int(rng.integers(-8, 9)), 255))
    sea_im = sea_im.filter(ImageFilter.GaussianBlur(22))
    sheet = Image.new('RGBA', (mw, mh), (0, 0, 0, 0))
    sheet.alpha_composite(sea_im)
    sheet.alpha_composite(spr)
    tex = paper_sheet(mw, mh, seed=seed, tone='parchment2')
    sheet = Image.blend(sheet.convert('RGB'), tex.convert('RGB'), 0.16).convert('RGBA')
    sheet.putalpha(Image.composite(sheet.split()[-1], Image.new('L', (mw, mh), 0),
                                   torn_rect(mw, mh, seed=seed, jitter=9, inset=0)))
    out = drop_shadow(sheet, blur=22, off=(16, 20), alpha=190)
    if tape_corners:
        for (tx, ty, ang) in ((-26, 16, -38), (out.width - 152, out.height - 60, 34)):
            tp = tape(w=150, h=44, seed=seed + 3).rotate(ang, expand=True,
                                                         resample=Image.BICUBIC)
            out.alpha_composite(tp, (tx, ty))
    return out


def shadow_of(sheet, at=(0, 0), blur=24, off=(20, 24), alpha=185, size=(1920, 1080)):
    """the shadow of a sheet that is itself placed at `at` — the shadow has to sit
    under the paper, not wherever the frame origin happens to be"""
    lay = Image.new('RGBA', size, (0, 0, 0, 0))
    sh = Image.new('RGBA', sheet.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, alpha), (0, 0), sheet.split()[-1])
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)),
                        (at[0] + off[0], at[1] + off[1]))
    return lay
