"""Stage: atmosphere, table top, dust and camera.

The background is baked once per segment and then cropped per frame with the
camera transform applied to each depth plane. Baking avoids the runtime
full-frame blur that previously stalled renders (AGENTS.md #5).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from PIL import Image

from . import gfx
from .tokens import ATMO, BRAND, PLANES, RIM


@dataclass
class Camera:
    """Camera moves are small and deliberate; objects keep their own motion."""

    pan_x: float = 0.0      # logical px
    pan_y: float = 0.0
    zoom: float = 1.0
    enabled: bool = True    # zeroed for the objective "camera off" control render

    def plane(self, dx: float, dy: float, factor: float) -> tuple[float, float]:
        if not self.enabled:
            return 0.0, 0.0
        return dx * factor, dy * factor


def bake_background(size: tuple[int, int], seed: int = 1301, margin: float = 1.16) -> Image.Image:
    """Deep ink/navy field with cyan + coral edge pools and a warm core."""
    w, h = int(size[0] * margin), int(size[1] * margin)
    base = gfx.linear_gradient((w, h), [
        (0.0, ATMO["void"], 1.0),
        (0.35, ATMO["deep"], 1.0),
        (0.72, ATMO["navy_soft"], 1.0),
        (1.0, "#080C18", 1.0),
    ], 90.0)

    # Cyan pool, camera-left; coral pool, camera-right; gold core behind the type.
    base = gfx.screen(base, gfx.radial((w, h), (w * 0.06, h * 0.62), w * 0.52, RIM["cyan"], 0.30, 2.6, aspect=0.85))
    base = gfx.screen(base, gfx.radial((w, h), (w * 0.97, h * 0.22), w * 0.46, RIM["coral"], 0.26, 2.5, aspect=0.9))
    base = gfx.screen(base, gfx.radial((w, h), (w * 0.52, h * 0.44), w * 0.34, BRAND["gold_light"], 0.10, 3.0, aspect=1.15))
    base = gfx.screen(base, gfx.radial((w, h), (w * 0.30, h * 0.10), w * 0.30, "#2E5C86", 0.16, 2.2))

    # Broad specular streak on the table plane (very low, sells the surface).
    streak = gfx.sweep((w, h), 0.62, 168.0, 0.10, BRAND["gold_pale"], 0.05, 2.2)
    base = gfx.screen(base, gfx.apply_mask(streak, _lower_band((w, h), 0.52)))

    # Fine "paper" grain in the dark field (pre-baked, not per-frame).
    base = gfx.grain(base, 0.006, seed)
    base = gfx.vignette(base, 0.42, 1.7)
    return base


def _lower_band(size: tuple[int, int], top: float) -> Image.Image:
    w, h = size
    yy = np.mgrid[0:h, 0:w][0].astype(np.float32) / h
    return Image.fromarray((np.clip((yy - top) / (1 - top), 0, 1) * 255).astype(np.uint8), "L")


def camera_crop(bg: Image.Image, size: tuple[int, int], cam: "Camera") -> Image.Image:
    """Crop the baked background with the camera transform + zoom (one resize)."""
    w, h = size
    bw, bh = bg.size
    zoom = max(1.0, cam.zoom) * (bw / w)
    cw, ch = w * zoom, h * zoom
    cx = bw / 2 + (cam.pan_x * PLANES["far_glow"] * bw / w if cam.enabled else 0.0)
    cy = bh / 2 + (cam.pan_y * PLANES["far_glow"] * bh / h if cam.enabled else 0.0)
    x0 = cx - cw / 2
    y0 = cy - ch / 2
    # single resample straight out of the baked plate
    return bg.transform(
        (w, h), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BICUBIC
    )


def dust(size: tuple[int, int], frame: int, count: int = 34, seed: int = 77) -> Image.Image:
    """Slow drifting motes on a near plane — a real, cheap parallax cue.

    Drawn straight into a numpy buffer (no per-mote mask allocation).
    """
    w, h = size
    rng = np.random.default_rng(seed)
    buf = np.zeros((h, w, 3), dtype=np.float32)
    scale = w / 1280.0
    for _ in range(count):
        bx = rng.uniform(0, w)
        by = rng.uniform(0, h)
        r = rng.uniform(0.9, 3.2) * scale
        speed = rng.uniform(0.22, 0.85)
        drift = rng.uniform(-0.38, 0.38)
        a = rng.uniform(0.05, 0.24)
        x = (bx + drift * frame * scale) % (w + 40) - 20
        y = (by - speed * frame * scale) % (h + 40) - 20
        x0, x1 = int(max(0, x - r * 4)), int(min(w, x + r * 4 + 1))
        y0, y1 = int(max(0, y - r * 4)), int(min(h, y + r * 4 + 1))
        if x1 <= x0 or y1 <= y0:
            continue
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        d2 = ((xx - x) ** 2 + (yy - y) ** 2) / (r * r)
        glow = np.exp(-d2 * 1.6) * a
        buf[y0:y1, x0:x1] += glow[..., None] * np.array(gfx.rgb(BRAND["gold_pale"]), np.float32) / 255.0
    out = np.zeros((h, w, 4), dtype=np.uint8)
    out[..., :3] = np.clip(buf * 255, 0, 255).astype(np.uint8)
    out[..., 3] = 255
    return Image.fromarray(out, "RGBA")


def foreground_occluder(size: tuple[int, int], frame: int, total: int = 180) -> Image.Image:
    """Out-of-focus foreground rim + two counter-sweeping light arcs.

    Present for the first frames only (a shallow depth-of-field cue, per the
    method of statement), then it clears. It must never black out the frame.
    """
    w, h = size
    t = gfx.clamp01(frame / max(1, total))
    reach = 1.0 - gfx.ease_out(gfx.clamp01(frame / 26.0))
    if reach <= 0.01:
        return Image.new("RGBA", (w, h), (0, 0, 0, 0))

    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ny = yy / h
    # bottom band, soft top edge
    band = np.clip((ny - (0.80 - 0.10 * reach)) / 0.12, 0, 1) ** 1.5
    dark = np.zeros((h, w, 4), dtype=np.float32)
    dark[..., 3] = band * 220 * reach
    out = Image.fromarray(dark.astype(np.uint8), "RGBA")

    # two sweeping arcs of light on the near plane
    for k, (speed, off) in enumerate(((1.0, 0.0), (-0.7, 0.45))):
        pos = (frame * 0.021 * speed + off) % 1.0
        sweep = gfx.sweep((w, h), pos, 168.0, 0.10, BRAND["gold_pale"], 0.22 * reach, 2.0)
        band_mask = Image.fromarray((band * 255).astype(np.uint8), "L")
        out = gfx.screen(out, gfx.apply_mask(sweep, band_mask))
    return out
