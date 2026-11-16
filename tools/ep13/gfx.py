"""Deterministic raster primitives for the EP13 renderer.

Everything is a pure function of its arguments (no clocks, no RNG without an
explicit seed), so a given frame renders identically on every machine — the
same contract Remotion's ``useCurrentFrame`` gives, enforced here by hand.

Design notes
------------
* Masks are anti-aliased by drawing polygons at ``AA``x and box-downsampling,
  then softened by an explicit 1-px smoothstep. No runtime CSS blur anywhere.
* Glows are *pre-baked* numpy gradients screened onto the frame, not GPU blurs.
* ``warp_quad`` gives real perspective on flat cards (a genuine depth cue) so
  panels can be tilted without pretending they are 3-D meshes.
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

AA = 3  # mask supersample factor


# --------------------------------------------------------------------------- #
# colour helpers
# --------------------------------------------------------------------------- #
def rgb(hex_str: str) -> tuple[int, int, int]:
    v = hex_str.lstrip("#")
    return int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)


def mix(a: str | Sequence[int], b: str | Sequence[int], t: float) -> tuple[int, int, int]:
    aa = rgb(a) if isinstance(a, str) else a
    bb = rgb(b) if isinstance(b, str) else b
    t = max(0.0, min(1.0, t))
    return tuple(int(round(aa[i] + (bb[i] - aa[i]) * t)) for i in range(3))


def with_alpha(hex_str: str, alpha: float) -> tuple[int, int, int, int]:
    r, g, b = rgb(hex_str)
    return r, g, b, int(round(max(0.0, min(1.0, alpha)) * 255))


# --------------------------------------------------------------------------- #
# masks
# --------------------------------------------------------------------------- #
def _downsample_mask(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    return img.resize(size, Image.BOX)


def mask_ellipse(size: tuple[int, int], box: tuple[float, float, float, float],
                 rotation: float = 0.0, soft: float = 1.2) -> Image.Image:
    """Ellipse mask inside ``box`` = (cx, cy, rx, ry). Rotated about its centre."""
    w, h = size
    big = Image.new("L", (w * AA, h * AA), 0)
    d = ImageDraw.Draw(big)
    cx, cy, rx, ry = box
    if abs(rotation) < 1e-6:
        d.ellipse([(cx - rx) * AA, (cy - ry) * AA, (cx + rx) * AA, (cy + ry) * AA], fill=255)
    else:
        # rotated ellipse sampled as a polygon
        pts = []
        n = 96
        ca, sa = math.cos(rotation), math.sin(rotation)
        for i in range(n):
            t = 2 * math.pi * i / n
            x, y = rx * math.cos(t), ry * math.sin(t)
            pts.append(((cx + x * ca - y * sa) * AA, (cy + x * sa + y * ca) * AA))
        d.polygon(pts, fill=255)
    m = _downsample_mask(big, size)
    return m.filter(ImageFilter.GaussianBlur(soft)) if soft > 0 else m


def mask_polygon(size: tuple[int, int], points: Iterable[tuple[float, float]],
                 soft: float = 1.2) -> Image.Image:
    w, h = size
    big = Image.new("L", (w * AA, h * AA), 0)
    ImageDraw.Draw(big).polygon([(x * AA, y * AA) for x, y in points], fill=255)
    m = _downsample_mask(big, size)
    return m.filter(ImageFilter.GaussianBlur(soft)) if soft > 0 else m


def mask_rrect(size: tuple[int, int], box: tuple[float, float, float, float],
               radius: float, soft: float = 1.2) -> Image.Image:
    """Rounded rect mask inside box = (x0, y0, x1, y1)."""
    w, h = size
    big = Image.new("L", (w * AA, h * AA), 0)
    x0, y0, x1, y1 = (v * AA for v in box)
    r = max(0.0, min(radius * AA, min(x1 - x0, y1 - y0) / 2))
    ImageDraw.Draw(big).rounded_rectangle([x0, y0, x1, y1], radius=r, fill=255)
    m = _downsample_mask(big, size)
    return m.filter(ImageFilter.GaussianBlur(soft)) if soft > 0 else m


def mask_ring(size: tuple[int, int], box: tuple[float, float, float, float],
              width: float, soft: float = 1.0) -> Image.Image:
    outer = mask_ellipse(size, box, soft=0)
    inner = mask_ellipse(size, (box[0], box[1], max(0.1, box[2] - width), max(0.1, box[3] - width)), soft=0)
    m = Image.fromarray(np.clip(np.array(outer, np.int16) - np.array(inner, np.int16), 0, 255).astype(np.uint8))
    return m.filter(ImageFilter.GaussianBlur(soft)) if soft > 0 else m


def mask_from_func(size: tuple[int, int], fn) -> Image.Image:
    """Build a mask from ``fn(xx, yy) -> float|bool`` evaluated on a float grid."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    out = fn(xx, yy)
    arr = np.clip(out if out.dtype != bool else out.astype(np.float32), 0, 1) * 255
    return Image.fromarray(arr.astype(np.uint8), "L")


def stroke(mask: Image.Image, width: float, soft: float = 1.0) -> Image.Image:
    """Outline of a mask (dilate - erode), in supersampled-safe image space."""
    size = max(1, int(round(width)))
    k = ImageFilter.MaxFilter(size if size % 2 else size + 1)
    grown = mask.filter(k)
    k2 = ImageFilter.MinFilter(size if size % 2 else size + 1)
    inner = mask.filter(k2)
    m = Image.fromarray(np.clip(np.array(grown, np.int16) - np.array(inner, np.int16), 0, 255).astype(np.uint8))
    return m.filter(ImageFilter.GaussianBlur(soft)) if soft > 0 else m


# --------------------------------------------------------------------------- #
# fills
# --------------------------------------------------------------------------- #
def solid(size: tuple[int, int], color: tuple[int, int, int, int]) -> Image.Image:
    return Image.new("RGBA", size, color)


def linear_gradient(size: tuple[int, int], stops: Sequence, angle: float = 90.0) -> Image.Image:
    """``angle`` in degrees, 0 = left->right, 90 = top->bottom."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = math.radians(angle)
    t = (xx * math.cos(a) + yy * math.sin(a))
    t = (t - t.min()) / max(1e-6, (t.max() - t.min()))
    out = np.zeros((h, w, 4), dtype=np.float32)
    stops = sorted(stops, key=lambda s: s[0])
    if len(stops) == 1:
        p0, c0, a0 = _stop(stops[0])
        out[..., 0], out[..., 1], out[..., 2] = c0
        out[..., 3] = a0 * 255.0
        return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")
    for i in range(len(stops) - 1):
        p0, c0, a0 = _stop(stops[i])
        p1, c1, a1 = _stop(stops[i + 1])
        seg = (t >= p0) & (t <= p1)
        if not seg.any():
            continue
        local = (t[seg] - p0) / max(1e-6, (p1 - p0))
        for ch in range(3):
            out[..., ch][seg] = c0[ch] + (c1[ch] - c0[ch]) * local
        out[..., 3][seg] = (a0 + (a1 - a0) * local) * 255.0
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def _stop(s: Sequence) -> tuple[float, tuple[int, int, int], float]:
    pos, colour = s[0], s[1]
    alpha = s[2] if len(s) > 2 else 1.0
    c = rgb(colour) if isinstance(colour, str) else tuple(colour)
    return float(pos), c, float(alpha)


def radial(size: tuple[int, int], centre: tuple[float, float], radius: float,
           color: str, alpha: float = 1.0, falloff: float = 2.4,
           aspect: float = 1.0) -> Image.Image:
    """Pre-baked radial glow (alpha built into the image; screen-blend it)."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx = (xx - centre[0]) / max(1e-3, radius)
    dy = (yy - centre[1]) / max(1e-3, radius * aspect)
    d = np.sqrt(dx * dx + dy * dy)
    a = np.clip(1.0 - d, 0.0, 1.0) ** falloff * alpha
    out = np.zeros((h, w, 4), dtype=np.float32)
    out[..., 0], out[..., 1], out[..., 2] = rgb(color)
    out[..., 3] = a * 255.0
    return Image.fromarray(out.astype(np.uint8), "RGBA")


def apply_mask(fill: Image.Image, mask: Image.Image) -> Image.Image:
    arr = np.array(fill, dtype=np.uint8).copy()
    arr[..., 3] = (arr[..., 3].astype(np.float32) * (np.array(mask, dtype=np.float32) / 255.0)).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def blur(img: Image.Image, radius: float) -> Image.Image:
    if radius <= 0:
        return img
    return img.filter(ImageFilter.GaussianBlur(radius))


def offset(img: Image.Image, dx: float, dy: float, size: tuple[int, int]) -> Image.Image:
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.alpha_composite(img, (int(round(dx)), int(round(dy))))
    return out


# --------------------------------------------------------------------------- #
# compositing
# --------------------------------------------------------------------------- #
def over(dst: Image.Image, src: Image.Image) -> Image.Image:
    out = dst.copy()
    out.alpha_composite(src)
    return out


def screen(dst: Image.Image, src: Image.Image, strength: float = 1.0) -> Image.Image:
    """Screen-blend ``src`` onto ``dst`` (both RGBA), restricted to src's bbox."""
    box = src.getbbox()
    if box is None or strength <= 0.0:
        return dst
    s = src.crop(box)
    d = dst.crop(box)
    da = np.array(d, dtype=np.float32) / 255.0
    sa = np.array(s, dtype=np.float32) / 255.0
    win = sa[..., 3:4] * strength
    da[..., :3] = 1.0 - (1.0 - da[..., :3]) * (1.0 - sa[..., :3] * win)
    out = dst.copy()
    out.paste(Image.fromarray((np.clip(da, 0, 1) * 255).astype(np.uint8), "RGBA"), box[:2])
    return out


def screen_at(dst: Image.Image, src: Image.Image, x: float, y: float,
              strength: float = 1.0) -> Image.Image:
    """Screen a small layer onto a larger canvas at (x, y)."""
    layer = Image.new("RGBA", dst.size, (0, 0, 0, 0))
    layer.alpha_composite(src, (int(round(x)), int(round(y))))
    return screen(dst, layer, strength)


def multiply_alpha(img: Image.Image, factor: float) -> Image.Image:
    arr = np.array(img)
    arr[..., 3] = np.clip(arr[..., 3].astype(np.float32) * factor, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def clip_to(img: Image.Image, mask: Image.Image) -> Image.Image:
    return apply_mask(img, mask)


def mask_mul(a: Image.Image, b: Image.Image) -> Image.Image:
    """Intersection of two masks (both L)."""
    return Image.fromarray(
        ((np.array(a, np.float32) / 255.0) * (np.array(b, np.float32) / 255.0) * 255).astype(np.uint8), "L")


# --------------------------------------------------------------------------- #
# transforms
# --------------------------------------------------------------------------- #
def _homography(src: Sequence[Sequence[float]], dst: Sequence[Sequence[float]]) -> np.ndarray:
    A = []
    b = []
    for (x, y), (u, v) in zip(src, dst):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        b.extend([u, v])
    res = np.linalg.solve(np.array(A, dtype=np.float64), np.array(b, dtype=np.float64))
    return np.append(res, 1.0).reshape(3, 3)


def warp_quad(src: Image.Image, quad: Sequence[tuple[float, float]],
              out_size: tuple[int, int]) -> Image.Image:
    """Perspective-warp ``src`` so its four corners land on ``quad`` (TL,TR,BR,BL)."""
    w, h = src.size
    src_pts = [(0, 0), (w, 0), (w, h), (0, h)]
    # PIL PERSPECTIVE maps *output* -> *input*, so invert.
    H = _homography(list(quad), src_pts)
    coeffs = (H / H[2, 2]).flatten()[:8]
    return src.transform(out_size, Image.PERSPECTIVE, tuple(coeffs), Image.BICUBIC)


def rotate_about(img: Image.Image, angle_deg: float) -> Image.Image:
    return img.rotate(-angle_deg, resample=Image.BICUBIC, expand=False)


# --------------------------------------------------------------------------- #
# light / film
# --------------------------------------------------------------------------- #
def sweep(size: tuple[int, int], pos: float, angle: float, width: float,
          color: str = "#FFFFFF", strength: float = 0.55, softness: float = 1.4) -> Image.Image:
    """A soft moving band of light (used on glass, plate rims and type)."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = math.radians(angle)
    t = xx * math.cos(a) + yy * math.sin(a)
    t = (t - t.min()) / max(1e-6, (t.max() - t.min()))
    d = np.abs(t - pos) / max(1e-4, width)
    env = np.clip(1.0 - d, 0, 1) ** softness * strength
    out = np.zeros((h, w, 4), dtype=np.float32)
    out[..., 0], out[..., 1], out[..., 2] = rgb(color)
    out[..., 3] = env * 255
    return Image.fromarray(out.astype(np.uint8), "RGBA")


def grain(img: Image.Image, amount: float, seed: int) -> Image.Image:
    """Deterministic film grain. ``amount`` ~ 0.008 - 0.02."""
    arr = np.array(img, dtype=np.float32)
    rng = np.random.default_rng(seed)
    n = rng.normal(0.0, amount * 255.0, arr.shape[:2]).astype(np.float32)
    arr[..., :3] = np.clip(arr[..., :3] + n[..., None], 0, 255)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def vignette(img: Image.Image, strength: float = 0.35, power: float = 2.0,
             aspect: float = 1.0) -> Image.Image:
    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (xx / w - 0.5) * 2.0
    ny = (yy / h - 0.5) * 2.0 * aspect
    d = np.sqrt(nx * nx + ny * ny) / math.sqrt(2.0)
    v = 1.0 - strength * np.clip(d, 0, 1) ** power
    arr = np.array(img, dtype=np.float32)
    arr[..., :3] = arr[..., :3] * v[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")


def downscale(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    return img.resize(size, Image.LANCZOS)


def ease_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) ** 3


def ease_in_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def ease_out_expo(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1.0 if t >= 1.0 else 1.0 - 2.0 ** (-10.0 * t)


def spring(t: float, damping: float = 7.0, frequency: float = 2.6) -> float:
    """Critically-under-damped settle, normalised to land on 1.0 at t>=1."""
    t = max(0.0, min(1.0, t))
    raw = 1.0 - math.exp(-damping * t) * math.cos(frequency * math.pi * t)
    end = 1.0 - math.exp(-damping) * math.cos(frequency * math.pi)
    return raw / end if end else raw


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def span(frame: int, start: int, length: int) -> float:
    """0..1 progress for an event starting at ``start`` lasting ``length`` frames."""
    if length <= 0:
        return 1.0 if frame >= start else 0.0
    return clamp01((frame - start) / float(length))
