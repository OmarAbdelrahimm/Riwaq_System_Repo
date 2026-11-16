"""RUWAQ EP13 — design tokens.

Two sources, kept separate on purpose:

1. BRAND_* — the approved RUWAQ palette read from ``data/brand.json``
   (``theme.colors``). Never substituted, never re-tinted.
2. ATMO_* / RIM_* — the *proposed* extension required by the user's reference
   style DNA (``01_REFERENCE_STYLE_DNA.md`` §C): dark navy atmospherics and a
   cyan/coral rim light pair. These are NOT brand colours. They are documented
   in ``docs/ep13/QC.md`` as an exception awaiting sign-off and are confined to
   light pools and 1-2 px rim highlights (no typography, no logo, no fills).

Nothing here is sampled from the reference video's brand elements.
"""

from __future__ import annotations

from dataclasses import dataclass

# --- 1. Approved brand palette (data/brand.json) -----------------------------
BRAND = {
    "ink_deep": "#1C1B19",
    "ink_second": "#242218",
    "parchment": "#F3EBDB",
    "parchment2": "#EDE6D6",
    "gold": "#A98A4B",
    "gold_light": "#C2A469",
    "gold_pale": "#EFE6D2",
    "burgundy": "#5E2230",
    "stone": "#8A7F6B",
    "stone_light": "#B9AE94",
}

# --- 2. Proposed atmospheric extension (needs user sign-off) ------------------
ATMO = {
    "void": "#05070F",
    "deep": "#070B1C",
    "navy": "#101D35",
    "navy_soft": "#0E172E",
    "graphite": "#141821",
}
RIM = {
    "cyan": "#47B8CC",
    "cyan_deep": "#2C7E96",
    "coral": "#E48672",
    "coral_deep": "#C46550",
    "ivory": "#F6F1E6",
}

# --- 3. Type -----------------------------------------------------------------
FONTS = {
    "title": "public/fonts/Amiri-Bold.ttf",
    "title_reg": "public/fonts/Amiri-Regular.ttf",
    "body": "public/fonts/IBMPlexSansArabic-Medium.ttf",
    "body_bold": "public/fonts/IBMPlexSansArabic-Bold.ttf",
    "body_reg": "public/fonts/IBMPlexSansArabic-Regular.ttf",
}

# Authored at 1920x1080 logical units (brand.json type_scale_1080x1920 is for
# 9:16; this episode is 16:9, so the scale is re-derived and recorded in QC).
TYPE_SCALE = {
    "hook_title": 96,
    "claim": 104,
    "kicker": 30,
    "micro": 24,
    "card_title": 46,
    "card_body": 32,
    "caption": 40,
}

# --- 4. Depth planes (camera parallax factors) -------------------------------
# factor = how much a plane moves per unit of camera move. Real parallax needs
# planes that are genuinely different, not one image scaled.
PLANES = {
    "far_glow": 0.15,
    "far_cards": 0.45,
    "heroes": 1.0,
    "near_occluder": 1.9,
}


@dataclass(frozen=True)
class Canvas:
    """Render at ``scale``x then downsample: cheap, stable anti-aliasing."""

    width: int = 1280
    height: int = 720
    scale: int = 2

    @property
    def w(self) -> int:
        return self.width * self.scale

    @property
    def h(self) -> int:
        return self.height * self.scale

    def s(self, value: float) -> float:
        """Scale a logical pixel value to supersampled pixels."""
        return value * self.scale
