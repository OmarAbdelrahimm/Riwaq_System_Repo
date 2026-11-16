"""Arabic typography for the EP13 renderer.

Why this module exists
----------------------
The sandbox has no browser binary (no Chrome/Chromium, and the Remotion host
that serves one is unreachable), and Pillow's wheels here are built without
Raqm, so Pillow cannot shape Arabic at all (it would emit disconnected,
wrongly-ordered letters).

This module therefore shapes with HarfBuzz (``uharfbuzz``) and rasterises the
resulting glyph IDs with FreeType (``freetype-py``) — the same two libraries
that back browser text. The output is a normal Pillow RGBA tile, so the rest of
the raster pipeline is unaffected.

Rules honoured (AGENTS.md / 02_METHOD_OF_STATEMENT):
  * Text is never baked into artwork; it is composited by code, per frame.
  * Word-level granularity only. Splitting Arabic into letters would break the
    joining forms, so emphasis is applied per word (e.g. one gold stress word).
  * No Latin fallback, no synthetic bold, no font substitution.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import freetype
import numpy as np
import uharfbuzz as hb
from PIL import Image

RTL = "\u202b"  # right-to-left embedding, used only for run detection


@dataclass
class Glyph:
    gid: int
    x_advance: float
    x_offset: float
    y_offset: float
    cluster: int


class _ShapedWord:
    """A shaped word rasterised at one (font, size, colour) combination."""

    __slots__ = ("image", "width", "height", "baseline", "advance", "text")

    def __init__(self, image: Image.Image, baseline: int, advance: float, text: str):
        self.image = image
        self.width = image.width
        self.height = image.height
        self.baseline = baseline
        self.advance = advance
        self.text = text


class TextEngine:
    """HarfBuzz shaping + FreeType rasterisation, with a per-word tile cache."""

    def __init__(self) -> None:
        self._hb_fonts: dict[tuple[str, int], tuple[hb.Font, hb.Face]] = {}
        self._ft_faces: dict[str, freetype.Face] = {}
        self._tiles: dict[tuple[str, int, str, int], _ShapedWord] = {}

    # -- setup ---------------------------------------------------------------
    def _hb(self, font_path: str, size_px: int) -> tuple[hb.Font, hb.Face]:
        key = (font_path, size_px)
        if key not in self._hb_fonts:
            with open(font_path, "rb") as fh:
                data = fh.read()
            face = hb.Face(data)
            font = hb.Font(face)
            hb.ot_font_set_funcs(font)
            # 26.6 fixed point: em size in pixels
            font.scale = (int(size_px * 64), int(size_px * 64))
            self._hb_fonts[key] = (font, face)
        return self._hb_fonts[key]

    def _ft(self, font_path: str) -> freetype.Face:
        if font_path not in self._ft_faces:
            self._ft_faces[font_path] = freetype.Face(font_path)
        return self._ft_faces[font_path]

    # -- shaping -------------------------------------------------------------
    def shape(self, text: str, font_path: str, size_px: int) -> list[Glyph]:
        font, _face = self._hb(font_path, size_px)
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(font, buf)
        return [
            Glyph(i.codepoint, p.x_advance / 64.0, p.x_offset / 64.0,
                  p.y_offset / 64.0, i.cluster)
            for i, p in zip(buf.glyph_infos, buf.glyph_positions)
        ]

    # -- rasterisation -------------------------------------------------------
    def _rasterise(self, glyphs: list[Glyph], font_path: str, size_px: int) -> tuple[np.ndarray, int, int]:
        """Return (alpha float array, baseline row, advance px)."""
        face = self._ft(font_path)
        face.set_pixel_sizes(0, size_px)
        ascender = int(round(size_px * 0.92))
        descender = int(round(size_px * 0.40))
        advance = int(round(sum(g.x_advance for g in glyphs))) + 4
        width = advance + int(size_px * 0.35)
        height = ascender + descender

        alpha = np.zeros((height, width), dtype=np.float32)
        pen_x = 0.0
        for g in glyphs:
            face.load_glyph(g.gid, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_NO_HINTING)
            slot = face.glyph
            bmp = slot.bitmap
            if bmp.width and bmp.rows:
                raw = bmp.buffer
                if not isinstance(raw, (bytes, bytearray)):
                    raw = bytes(raw)
                pitch = abs(bmp.pitch)
                arr = np.frombuffer(raw, dtype=np.uint8)
                arr = arr.reshape((bmp.rows, pitch))[:, : bmp.width]
                gx = int(round(pen_x + g.x_offset + slot.bitmap_left))
                gy = int(round(ascender - g.y_offset - slot.bitmap_top))
                x0, y0 = max(gx, 0), max(gy, 0)
                x1 = min(gx + arr.shape[1], width)
                y1 = min(gy + arr.shape[0], height)
                if x1 > x0 and y1 > y0:
                    sub = arr[y0 - gy : y1 - gy, x0 - gx : x1 - gx].astype(np.float32) / 255.0
                    np.maximum(alpha[y0:y1, x0:x1], sub, out=alpha[y0:y1, x0:x1])
            pen_x += g.x_advance
        return alpha, ascender, pen_x

    def word(self, text: str, font_path: str, size_px: int, color: str) -> _ShapedWord:
        key = (font_path, size_px, color, hash(text))
        cached = self._tiles.get(key)
        if cached is not None and cached.text == text:
            return cached
        glyphs = self.shape(text, font_path, size_px)
        alpha, baseline, advance = self._rasterise(glyphs, font_path, size_px)
        rgb = np.array(_to_rgb(color), dtype=np.float32)
        rgba = np.zeros((alpha.shape[0], alpha.shape[1], 4), dtype=np.uint8)
        rgba[..., :3] = rgb.astype(np.uint8)
        rgba[..., 3] = np.clip(alpha * 255.0, 0, 255).astype(np.uint8)
        tile = _ShapedWord(Image.fromarray(rgba, "RGBA"), baseline, advance, text)
        self._tiles[key] = tile
        return tile

    # -- layout --------------------------------------------------------------
    def line_width(self, words: list[str], font_path: str, size_px: int, tracking: float = 0.0) -> float:
        widths = [self.word(w, font_path, size_px, "#FFFFFF").advance for w in words]
        return sum(widths) + tracking * max(len(words) - 1, 0)

    def draw_line(
        self,
        canvas: Image.Image,
        words: list[tuple[str, str]],
        font_path: str,
        size_px: int,
        y: float,
        *,
        right: float | None = None,
        center: float | None = None,
        tracking: float = 0.0,
        space: float | None = None,
        alpha: float = 1.0,
        word_offsets: dict[int, tuple[float, float, float]] | None = None,
        scale: float = 1.0,
    ) -> tuple[float, float, float, float]:
        """Draw a right-to-left run of coloured words.

        ``words`` is (text, colour) in logical reading order (first = rightmost).
        ``word_offsets`` maps word index -> (dx, dy, alpha_multiplier) so a
        per-word kinetic stagger needs no re-shaping.
        Returns the bounding box actually touched (x0, y0, x1, y1).
        """
        tiles = [self.word(t, font_path, size_px, c) for t, c in words]
        gap = space if space is not None else size_px * 0.26 + tracking
        total = sum(t.advance for t in tiles) + gap * max(len(tiles) - 1, 0)
        if right is not None:
            pen = right
        elif center is not None:
            pen = center + total / 2.0
        else:  # left aligned
            pen = total
        x0 = y0 = 10**9
        x1 = y1 = -10**9
        for idx, tile in enumerate(tiles):
            dx, dy, amul = (word_offsets or {}).get(idx, (0.0, 0.0, 1.0))
            a = max(0.0, min(1.0, alpha * amul))
            if a > 0.004:
                img = tile.image if abs(scale - 1.0) < 1e-4 else _scale_rgba(tile.image, scale)
                if a < 0.999:
                    img = _with_alpha(img, a)
                px = int(round(pen - tile.advance + dx))
                py = int(round(y - tile.baseline + dy))
                canvas.alpha_composite(img, (px, py))
                x0, y0 = min(x0, px), min(y0, py)
                x1, y1 = max(x1, px + img.width), max(y1, py + img.height)
            pen -= tile.advance + gap
        return (x0, y0, x1, y1)


def _scale_rgba(img: Image.Image, factor: float) -> Image.Image:
    return img.resize(
        (max(1, int(round(img.width * factor))), max(1, int(round(img.height * factor)))),
        Image.LANCZOS,
    )


def _with_alpha(img: Image.Image, a: float) -> Image.Image:
    arr = np.array(img)
    arr[..., 3] = (arr[..., 3].astype(np.float32) * a).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def _to_rgb(value) -> tuple[int, int, int]:
    if isinstance(value, (tuple, list)):
        return tuple(int(v) for v in value[:3])  # type: ignore[return-value]
    return _hex_to_rgb(value)


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    v = value.lstrip("#")
    return tuple(int(v[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


@lru_cache(maxsize=1)
def engine() -> TextEngine:
    return TextEngine()
