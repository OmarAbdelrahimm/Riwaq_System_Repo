"""Hero objects: the fish and the milk glass.

Status of these objects (stated plainly, per AGENTS.md #3)
---------------------------------------------------------
There is no licensed fish or glass 3-D model in the project, and the handoff's
``FISH_SEPARATE`` / ``GLASS_SEPARATE`` are both MISSING. Rather than crop a flat
PNG and drift it across the frame (an explicit FAIL), each hero is authored here
as **independent 2.5-D geometry**:

  fish  — cast shadow, body, body gradient, belly bounce, dorsal fin, anal fin,
          tail fin, pectoral fin, gill plate, mouth, scale rows, lateral line,
          eye + glint, travelling specular, cyan/coral rim strokes  (16 layers)
  glass — contact shadow, floor reflection, inner cavity, milk body, meniscus,
          milk shading, glass wall, wall edges, rim ellipse, lip highlights,
          vertical speculars, travelling sheen, refraction tints, caustic (14)

What is real: independent per-layer motion, shadows that tighten as an object
lands, speculars that travel with rotation, parallax across separate planes.
What is NOT real: mesh lighting, true 3-D rotation, refraction, occlusion
changes from spinning. Depth is parallax + authored scale, not projection.
"""

from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import gfx
from .tokens import BRAND, RIM


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _bez(p0, p1, p2, p3, n=30):
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        out.append((
            u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1],
        ))
    return out


def _poly(*segments):
    pts: list[tuple[float, float]] = []
    for seg in segments:
        pts.extend(seg)
    return pts


def _rot(pts, pivot, deg):
    ca, sa = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    out = []
    for x, y in pts:
        dx, dy = x - pivot[0], y - pivot[1]
        out.append((pivot[0] + dx * ca - dy * sa, pivot[1] + dx * sa + dy * ca))
    return out


class Sprite:
    """A local-coordinate tile whose origin is its centre, blitted with rotation."""

    __slots__ = ("img", "w", "h", "ox", "oy")

    def __init__(self, w: float, h: float, ox: float = 0.0, oy: float = 0.0):
        self.w, self.h = max(2, int(round(w))), max(2, int(round(h)))
        self.img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        self.ox, self.oy = ox, oy

    def size(self) -> tuple[int, int]:
        return (self.w, self.h)

    def to_tile(self, x: float, y: float) -> tuple[float, float]:
        return (x + self.w / 2 + self.ox, y + self.h / 2 + self.oy)

    def mask_poly(self, pts, soft=1.0):
        return gfx.mask_polygon(self.size(), [self.to_tile(*p) for p in pts], soft=soft)

    def mask_ellipse(self, cx, cy, rx, ry, rot=0.0, soft=1.0):
        tx, ty = self.to_tile(cx, cy)
        return gfx.mask_ellipse(self.size(), (tx, ty, rx, ry), rotation=rot, soft=soft)

    def paint(self, mask, fill):
        self.img = gfx.over(self.img, gfx.apply_mask(fill, mask))

    def screen_layer(self, layer, strength: float = 1.0, color: str = "#FFFFFF"):
        if layer.mode == "L":
            layer = gfx.apply_mask(gfx.solid(self.size(), gfx.with_alpha(color, 1.0)), layer)
        self.img = gfx.screen(self.img, layer, strength)

    def blit(self, canvas: Image.Image, cx: float, cy: float, rot: float = 0.0,
             alpha: float = 1.0, flip: bool = False) -> None:
        img = self.img
        if flip:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        if abs(rot) > 1e-4:
            img = img.rotate(-rot, resample=Image.BICUBIC, expand=False)
        if alpha < 0.999:
            img = gfx.multiply_alpha(img, alpha)
        canvas.alpha_composite(img, (int(round(cx - self.w / 2)), int(round(cy - self.h / 2))))


def _line_mask(size, pts, width, soft=0.6):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).line(pts, fill=255, width=max(1, int(round(width))), joint="curve")
    return gfx.blur(m, soft) if soft > 0 else m


# --------------------------------------------------------------------------- #
# fish
# --------------------------------------------------------------------------- #
def fish_sprite(*, s: float = 1.0, tail: float = 0.0, dorsal: float = 0.0,
                pect: float = 0.0, sheen: float = 0.5, lift: float = 0.0,
                rim: float = 1.0, shadow: float = 1.0) -> Sprite:
    """Silver-blue fish, 16 independently transformed layers.

    ``tail`` / ``dorsal`` / ``pect`` are angles in degrees, ``sheen`` 0..1 slides
    the travelling specular, ``lift`` raises the fish off the plate (and loosens
    the cast shadow accordingly).
    """
    sp = Sprite(620 * s, 380 * s, oy=10 * s)

    def S(v):
        return v * s

    lift = max(-10.0, min(48.0, lift))

    # ---- cast shadow (tightens and shifts as the fish lifts) ----
    blur_r = S(11 - 4 * (lift / 48.0))
    sh = sp.mask_ellipse(S(6 + lift * 0.30), S(96 - lift * 0.22),
                         S(150 * (1 - 0.12 * lift / 48.0)), S(26 * (1 - 0.18 * lift / 48.0)),
                         rot=-3, soft=blur_r)
    sp.paint(sh, gfx.solid(sp.size(), (0, 0, 0, int(190 * shadow))))

    # ---- geometry ----
    body_pts = _poly(
        _bez((S(150), S(-12)), (S(132), S(-48)), (S(104), S(-64)), (S(84), S(-68))),
        _bez((S(84), S(-68)), (S(30), S(-78)), (S(-40), S(-70)), (S(-88), S(-46))),
        _bez((S(-88), S(-46)), (S(-104), S(-38)), (S(-110), S(-24)), (S(-112), S(-6))),
        _bez((S(-112), S(-6)), (S(-112), S(6)), (S(-110), S(20)), (S(-104), S(30))),
        _bez((S(-104), S(30)), (S(-64), S(52)), (S(-2), S(68)), (S(56), S(56))),
        _bez((S(56), S(56)), (S(104), S(46)), (S(138), S(18)), (S(150), S(-12))),
    )
    body = sp.mask_poly(body_pts, soft=S(0.9))

    # ---- fins are drawn first; the body overlaps their roots ----
    tail_pts = _poly(
        _bez((S(-96), S(-28)), (S(-126), S(-46)), (S(-176), S(-74)), (S(-186), S(-40))),
        [(S(-186), S(-40))],
        _bez((S(-186), S(-40)), (S(-166), S(-18)), (S(-150), S(-8)), (S(-158), S(6))),
        _bez((S(-158), S(6)), (S(-176), S(26)), (S(-196), S(56)), (S(-182), S(74))),
        _bez((S(-182), S(74)), (S(-150), S(52)), (S(-112), S(34)), (S(-98), S(24))),
    )
    tail_pts = _rot(tail_pts, (S(-98), S(0)), tail)
    tm = sp.mask_poly(tail_pts, soft=S(0.7))

    dorsal_pts = _poly(
        _bez((S(48), S(-64)), (S(28), S(-92)), (S(4), S(-102)), (S(-18), S(-100))),
        _bez((S(-18), S(-100)), (S(-40), S(-78)), (S(-56), S(-66)), (S(-62), S(-56))),
        [(S(-40), S(-50)), (S(6), S(-62))],
    )
    dorsal_pts = _rot(dorsal_pts, (S(0), S(-66)), dorsal)
    dm = sp.mask_poly(dorsal_pts, soft=S(0.7))

    anal_pts = _poly(
        _bez((S(-30), S(56)), (S(-56), S(78)), (S(-78), S(92)), (S(-92), S(80))),
        [(S(-84), S(50)), (S(-52), S(44))],
    )
    anal_pts = _rot(anal_pts, (S(-50), S(46)), dorsal * 0.6)
    am = sp.mask_poly(anal_pts, soft=S(0.7))

    pect_pts = _poly(
        _bez((S(58), S(16)), (S(44), S(40)), (S(24), S(52)), (S(12), S(50))),
        _bez((S(12), S(50)), (S(28), S(34)), (S(46), S(22)), (S(58), S(16))),
    )
    pect_pts = _rot(pect_pts, (S(58), S(16)), pect)
    pm = sp.mask_poly(pect_pts, soft=S(0.7))

    fin_fill = gfx.linear_gradient(sp.size(), [
        (0.0, "#7B93A6", 0.72), (0.4, "#4A5C6D", 0.70), (1.0, "#202A35", 0.72)], 88.0)
    for m in (tm, dm, am, pm):
        sp.paint(m, fin_fill)

    # fin rays
    ribs = Image.new("L", sp.size(), 0)
    d = ImageDraw.Draw(ribs)
    for i in range(5):
        a = -32 + i * 14
        p0 = sp.to_tile(S(-104), S(0))
        p1 = sp.to_tile(S(-104) - S(86) * math.cos(math.radians(a)),
                        S(0) + S(86) * math.sin(math.radians(a)))
        d.line([p0, p1], fill=90, width=max(1, int(round(S(1.0)))))
    ribs = gfx.blur(ribs, S(0.6))
    sp.screen_layer(gfx.apply_mask(gfx.solid(sp.size(), gfx.with_alpha("#D9ECF7", 0.18)),
                                   gfx.mask_mul(ribs, tm)))

    # ---- body ----
    # dark polished metal: lit from the cyan rim above, warm bounce below
    sp.paint(body, gfx.linear_gradient(sp.size(), [
        (0.00, "#93AEC2"), (0.08, "#688296"), (0.24, "#3C4E5F"),
        (0.46, "#243040"), (0.68, "#1B232D"), (0.86, "#2F3034"), (1.0, "#4C4133")], 94.0))
    belly = gfx.apply_mask(gfx.linear_gradient(sp.size(), [
        (0.62, "#000000", 0.0), (1.0, "#C79A6B", 0.38)], 90.0), body)
    sp.screen_layer(belly, 0.9)
    back = gfx.apply_mask(gfx.linear_gradient(sp.size(), [
        (0.0, "#CFE6F4", 0.30), (0.16, "#CFE6F4", 0.0)], 90.0), body)
    sp.screen_layer(back, 0.9)
    # hard specular streak along the back (the "wet metal" read)
    streak = gfx.mask_mul(sp.mask_ellipse(S(30), S(-54), S(74), S(4.5), rot=-3, soft=S(4)), body)
    sp.screen_layer(gfx.apply_mask(gfx.solid(sp.size(), gfx.with_alpha("#E8F6FF", 0.50)), streak), 1.0)
    # top contour highlight: edge light that survives at small sizes
    top_ring = gfx.stroke(body, max(1.0, S(3.2)), soft=S(2.2))
    top_hi = gfx.apply_mask(gfx.linear_gradient(sp.size(), [
        (0.0, "#FFFFFF", 0.55), (0.35, "#FFFFFF", 0.0)], 78.0), top_ring)
    sp.screen_layer(top_hi, 1.0)

    # brushed-metal banding (reads as sheen, not as a cartoon scale grid)
    bands = Image.new("L", sp.size(), 0)
    db = ImageDraw.Draw(bands)
    for i in range(9):
        x = S(-110 + i * 30)
        y0, y1 = sp.to_tile(x, S(-80))
        db.line([(x + sp.w / 2 + sp.ox, y0), (x + sp.w / 2 + sp.ox, sp.to_tile(x, S(72))[1])],
                fill=70, width=max(1, int(round(S(6)))))
    bands = gfx.blur(bands, S(6))
    sp.screen_layer(gfx.apply_mask(gfx.solid(sp.size(), gfx.with_alpha("#EAF4FA", 0.10)),
                                   gfx.mask_mul(bands, body)))

    # lateral line
    ll = _bez((S(140), S(-4)), (S(60), S(-12)), (S(-20), S(-14)), (S(-100), S(-6)), n=40)
    llm = _line_mask(sp.size(), [sp.to_tile(*p) for p in ll], S(1.8), S(0.8))
    sp.screen_layer(gfx.apply_mask(gfx.solid(sp.size(), gfx.with_alpha(BRAND["gold_pale"], 0.30)), llm))

    # gill plate
    gill = _bez((S(92), S(-46)), (S(74), S(-16)), (S(74), S(22)), (S(92), S(42)))
    gm = _line_mask(sp.size(), [sp.to_tile(*p) for p in gill], S(1.8), S(1.0))
    sp.screen_layer(gfx.apply_mask(gfx.solid(sp.size(), gfx.with_alpha("#0A1016", 0.45)), gm))

    # mouth
    mouth = _line_mask(sp.size(), [sp.to_tile(S(152), S(-8)), sp.to_tile(S(142), S(4))], S(2.0), S(0.6))
    sp.screen_layer(gfx.apply_mask(gfx.solid(sp.size(), gfx.with_alpha("#151E27", 0.8)), mouth))

    # eye
    socket = sp.mask_ellipse(S(119), S(-26), S(15), S(15), soft=S(7))
    sp.paint(socket, gfx.solid(sp.size(), (0, 0, 0, 60)))
    eye_o = sp.mask_ellipse(S(118), S(-26), S(8.2), S(8.2), soft=S(0.6))
    sp.paint(eye_o, gfx.solid(sp.size(), gfx.with_alpha("#0A1016", 1.0)))
    eye_i = sp.mask_ellipse(S(119), S(-25), S(4.4), S(4.4), soft=S(0.5))
    sp.paint(eye_i, gfx.linear_gradient(sp.size(), [(0.0, "#5C7A8E"), (0.5, "#16222C"), (1.0, "#080D12")], 90.0))
    eye_ring = gfx.stroke(eye_o, max(1.0, S(1.4)), soft=S(0.7))
    sp.screen_layer(gfx.apply_mask(gfx.solid(sp.size(), gfx.with_alpha("#CFE4F2", 0.45)), eye_ring), 0.8)
    glint = sp.mask_ellipse(S(116.5), S(-28), S(2.2), S(2.2), soft=S(0.4))
    sp.screen_layer(gfx.apply_mask(gfx.solid(sp.size(), gfx.with_alpha("#FFFFFF", 0.95)), glint))

    # travelling specular
    sx = S(-70 + 200 * sheen)
    spec = gfx.mask_mul(sp.mask_ellipse(sx, S(-52), S(80), S(11), rot=-14, soft=S(12)), body)
    sp.screen_layer(gfx.apply_mask(gfx.solid(sp.size(), gfx.with_alpha("#F2FAFF", 0.40)), spec), 0.9)

    # rim lights
    body_rim = gfx.stroke(body, max(1.0, S(2.0)), soft=S(1.0))
    sp.screen_layer(gfx.apply_mask(gfx.linear_gradient(sp.size(), [
        (0.0, RIM["cyan"], 1.0), (0.38, RIM["cyan"], 0.18), (1.0, RIM["cyan"], 0.0)], 58.0), body_rim), 1.15 * rim)
    sp.screen_layer(gfx.apply_mask(gfx.linear_gradient(sp.size(), [
        (0.55, RIM["coral"], 0.0), (1.0, RIM["coral"], 0.55)], 58.0), body_rim), 0.55 * rim)

    for m, a in ((tm, 0.55), (dm, 0.5), (am, 0.4), (pm, 0.45)):
        fr = gfx.stroke(m, max(1.0, S(1.4)), soft=S(0.8))
        sp.screen_layer(gfx.apply_mask(gfx.linear_gradient(sp.size(), [
            (0.0, RIM["cyan"], 0.55), (1.0, RIM["cyan"], 0.05)], 70.0), fr), a * rim)

    return sp


def plate_sprite(*, s: float = 1.0, warm: float = 0.5) -> Sprite:
    """Low ceramic plate seen at an oblique angle."""
    sp = Sprite(620 * s, 300 * s, oy=10 * s)

    def S(v):
        return v * s

    # tight ambient occlusion under the plate (no floating dark blob)
    sp.paint(sp.mask_ellipse(S(2), S(16), S(252), S(58), soft=S(18)),
             gfx.solid(sp.size(), (0, 0, 0, 130)))

    base = sp.mask_ellipse(0, 0, S(246), S(68), soft=S(1.0))
    sp.paint(base, gfx.linear_gradient(sp.size(), [
        (0.02, "#B3A794"), (0.20, "#E4D9C4"), (0.46, "#CBBFA8"),
        (0.70, "#8E8271"), (0.88, "#5C5346"), (1.0, "#332E27")], 96.0))

    # inner well
    well = sp.mask_ellipse(S(-4), S(-8), S(196), S(50), soft=S(7))
    sp.paint(well, gfx.linear_gradient(sp.size(), [
        (0.0, "#DCD2BF"), (0.45, "#C9BDA8"), (1.0, "#9B8F7B")], 96.0))
    well2 = sp.mask_ellipse(S(-4), S(-13), S(152), S(36), soft=S(12))
    sp.paint(well2, gfx.linear_gradient(sp.size(), [
        (0.0, "#EDE4D2"), (1.0, "#C2B59E")], 96.0))

    # gold hairline at the rim + bright top edge
    ring = gfx.stroke(base, max(1.0, S(1.5)), soft=S(0.8))
    sp.screen_layer(gfx.apply_mask(gfx.linear_gradient(sp.size(), [
        (0.0, BRAND["gold_light"], 0.60), (1.0, BRAND["gold"], 0.10)], 40.0), ring), 0.9)
    top_arc = gfx.apply_mask(gfx.linear_gradient(sp.size(), [
        (0.0, "#FFFFFF", 0.55), (0.55, "#FFFFFF", 0.0)], 74.0), gfx.stroke(base, max(1.0, S(3.2)), soft=S(2.0)))
    sp.screen_layer(top_arc, 0.85)

    # warm bounce pool on the plate (from the coral side light)
    sp.screen_layer(gfx.radial(sp.size(), sp.to_tile(S(130), S(4)), S(230), RIM["coral"],
                               0.10 * warm, 2.0, aspect=0.45), 1.0)
    return sp


# --------------------------------------------------------------------------- #
# milk glass
# --------------------------------------------------------------------------- #
def glass_sprite(*, s: float = 1.0, slosh: float = 0.0, sheen: float = 0.4,
                 rim: float = 1.0, shadow: float = 1.0, fill: float = 0.66) -> Sprite:
    """Tapered tumbler, 66 % full by default, with a real meniscus."""
    sp = Sprite(420 * s, 580 * s, oy=-30 * s)

    def S(v):
        return v * s

    top_y, bot_y = S(-196), S(180)
    tw, bw = S(74), S(60)          # half-widths at top / bottom
    r = S(16)
    wall = S(4.2)

    # ---- shadows ----
    sp.paint(sp.mask_ellipse(S(12), S(200), S(118), S(26), soft=S(20)),
             gfx.solid(sp.size(), (0, 0, 0, int(115 * shadow))))
    sp.paint(sp.mask_ellipse(S(3), S(191), S(74), S(15), soft=S(7)),
             gfx.solid(sp.size(), (0, 0, 0, int(205 * shadow))))

    def body_pts(y0=top_y, y1=bot_y, w0=tw, w1=bw):
        return _poly(
            _bez((-w0, y0), (-w0 * 0.42, y0 - S(13)), (w0 * 0.42, y0 - S(13)), (w0, y0)),
            _bez((w0, y0), (w0, y0 + (y1 - y0) * 0.5), (w1, y1 - r), (w1, y1)),
            _bez((w1, y1), (w1, y1 + r * 0.8), (-w1, y1 + r * 0.8), (-w1, y1)),
            _bez((-w1, y1), (-w0, y1 - r), (-w0, y0 + (y1 - y0) * 0.5), (-w0, y0)),
        )

    body = sp.mask_poly(body_pts(), soft=S(0.9))
    inner_w_top = tw - wall * 2.2
    inner_w_bot = bw - wall * 2.2

    # ---- milk (width follows the inner wall, so it touches the glass) ----
    milk_top = top_y + (bot_y - top_y) * (1.0 - fill) + S(slosh * 2.0)
    milk = sp.mask_poly(_poly(
        [(-inner_w_top, milk_top), (inner_w_top, milk_top)],
        _bez((inner_w_top, milk_top), (inner_w_top, S(20)), (inner_w_bot + S(2), S(150)), (inner_w_bot, S(168))),
        _bez((inner_w_bot, S(168)), (inner_w_bot * 0.4, S(182)), (-inner_w_bot * 0.4, S(182)), (-inner_w_bot, S(168))),
        _bez((-inner_w_bot, S(168)), (-inner_w_bot - S(2), S(150)), (-inner_w_top, S(20)), (-inner_w_top, milk_top)),
    ), soft=S(0.9))
    sp.paint(milk, gfx.linear_gradient(sp.size(), [
        (0.0, "#FDF8EC"), (0.30, "#F6EEDA"), (0.62, "#EADCC0"),
        (0.86, "#D4BF9B"), (1.0, "#B49C74")], 96.0))
    sp.paint(milk, gfx.apply_mask(gfx.linear_gradient(sp.size(), [
        (0.0, "#000000", 0.0), (0.5, "#000000", 0.0), (1.0, "#6A5637", 0.40)], 0.0), milk))

    # ---- empty glass above the milk: light, translucent, background visible ----
    above_pts = _poly(
        [(-inner_w_top, top_y), (inner_w_top, top_y), (inner_w_top, milk_top), (-inner_w_top, milk_top)])
    above = sp.mask_poly(above_pts, soft=S(1.0))
    sp.paint(above, gfx.linear_gradient(sp.size(), [
        (0.0, "#93AEBE", 0.055), (0.5, "#7E99AC", 0.02), (1.0, "#5C7385", 0.05)], 92.0))

    # ---- meniscus: the milk surface, thin bright front edge only ----
    men = sp.mask_ellipse(0, milk_top, inner_w_top, S(8.0), soft=S(0.9))
    sp.paint(men, gfx.linear_gradient(sp.size(), [
        (0.0, "#FFFEFA"), (0.55, "#FBF3E0"), (1.0, "#E6D7BA")], 90.0))
    men_edge = gfx.mask_ring(sp.size(), sp.to_tile(0, milk_top) + (inner_w_top, S(8.0)), S(1.6), soft=S(0.6))
    front = gfx.apply_mask(gfx.linear_gradient(sp.size(), [
        (0.0, "#FFFFFF", 0.55), (0.5, "#FFFFFF", 0.15), (1.0, "#FFFFFF", 0.45)], 90.0), men_edge)
    sp.screen_layer(front, 0.55)

    # ---- glass wall (a thin shell, brighter at the two vertical edges) ----
    wall_band = gfx.apply_mask(gfx.linear_gradient(sp.size(), [
        (0.0, "#B6D2E0", 0.42), (0.09, "#7FA0B4", 0.10), (0.5, "#C7DCE6", 0.05),
        (0.91, "#9FB2BE", 0.10), (1.0, "#B0C4CF", 0.36)], 0.0), body)
    sp.screen_layer(wall_band, 0.85)

    # outer contour: soft keyline + one crisp highlight on the left wall
    outline = gfx.stroke(body, max(1.0, S(1.6)), soft=S(0.9))
    sp.screen_layer(gfx.apply_mask(gfx.linear_gradient(sp.size(), [
        (0.0, "#EAF7FD", 0.45), (0.35, "#9EB6C4", 0.10), (0.7, "#E7D8C6", 0.12), (1.0, "#FFF1E2", 0.35)], 0.0), outline), 0.8)
    left_hi = sp.mask_poly([(-tw + 1.5, top_y + S(4)), (-tw + S(6), top_y + S(6)),
                            (-bw + S(6), bot_y - S(6)), (-bw + 1.5, bot_y - S(10))], soft=S(1.4))
    sp.screen_layer(gfx.apply_mask(gfx.solid(sp.size(), gfx.with_alpha("#FFFFFF", 0.34)), left_hi), 1.0)
    right_hi = sp.mask_poly([(tw - S(5), top_y + S(6)), (tw - 1.5, top_y + S(4)),
                             (bw - 1.5, bot_y - S(10)), (bw - S(5), bot_y - S(6))], soft=S(1.6))
    sp.screen_layer(gfx.apply_mask(gfx.solid(sp.size(), gfx.with_alpha("#FFF6EC", 0.22)), right_hi), 1.0)

    # ---- opening: the far rim seen through the glass, then the near lip ----
    open_m = sp.mask_ellipse(0, top_y + S(3), tw - S(2), S(13), soft=S(1.4))
    sp.paint(open_m, gfx.linear_gradient(sp.size(), [
        (0.0, "#A9C8D8", 0.14), (0.45, "#88A4B4", 0.07), (1.0, "#DCF0F8", 0.20)], 92.0))

    # ---- rim: back half dim, front half bright ----
    rim_ell = gfx.mask_ring(sp.size(), sp.to_tile(0, top_y) + (tw, S(12.5)), S(2.6), soft=S(0.7))
    sp.screen_layer(rim_ell, 0.55)
    front_hi = gfx.mask_ring(sp.size(), sp.to_tile(0, top_y) + (tw, S(12.5)), S(4.2), soft=S(2.6))
    front_hi = gfx.apply_mask(gfx.linear_gradient(sp.size(), [
        (0.0, "#FFFFFF", 0.0), (0.62, "#FFFFFF", 0.40), (1.0, "#FFFFFF", 0.0)], 34.0), front_hi)
    sp.screen_layer(front_hi, 1.25 * rim)

    # ---- speculars ----
    spec = sp.mask_poly([(-50, -160), (-33, -164), (-30, 120), (-45, 124)], soft=S(8))
    sp.screen_layer(gfx.apply_mask(gfx.solid(sp.size(), gfx.with_alpha("#FFFFFF", 0.22)), spec), 1.0)
    spec2 = sp.mask_poly([(44, -150), (50, -148), (45, 112), (39, 114)], soft=S(5))
    sp.screen_layer(gfx.apply_mask(gfx.solid(sp.size(), gfx.with_alpha("#FFF6EA", 0.16)), spec2), 1.0)
    chip = sp.mask_ellipse(S(-38), S(-130), S(5), S(14), rot=-6, soft=S(3.5))
    sp.screen_layer(gfx.apply_mask(gfx.solid(sp.size(), gfx.with_alpha("#FFFFFF", 0.38)), chip), 1.0)

    # travelling sheen (moves with the camera/entry, not a loop)
    sw = gfx.sweep(sp.size(), sheen, 100.0, 0.13, "#FFFFFF", 0.26, 1.6)
    sp.screen_layer(gfx.apply_mask(sw, body), 0.7)

    # refraction tints at the two glass edges
    sp.screen_layer(gfx.apply_mask(gfx.linear_gradient(sp.size(), [
        (0.0, RIM["cyan"], 0.42), (0.12, RIM["cyan"], 0.0),
        (0.88, RIM["coral"], 0.0), (1.0, RIM["coral"], 0.30)], 0.0), body), 0.45 * rim)

    # glass base thickness (a bright lens at the bottom of the tumbler)
    base_lens = sp.mask_ellipse(0, bot_y - S(6), bw - S(2), S(12), soft=S(2.5))
    sp.screen_layer(gfx.apply_mask(gfx.solid(sp.size(), gfx.with_alpha("#DDEFF6", 0.20)), base_lens), 0.9)
    base_line = gfx.stroke(base_lens, max(1.0, S(1.4)), soft=S(0.8))
    sp.screen_layer(gfx.apply_mask(gfx.solid(sp.size(), gfx.with_alpha("#F4FCFF", 0.30)), base_line), 0.9)

    # caustic pool under the base
    sp.screen_layer(gfx.apply_mask(gfx.solid(sp.size(), gfx.with_alpha("#FFF0D6", 0.36)),
                                   sp.mask_ellipse(S(-16), S(192), S(42), S(8), soft=S(6))), 0.9)
    return sp


def floor_reflection(sprite: Sprite, sink: int = 12, radius: float = 5.0,
                     alpha: float = 0.18) -> Image.Image:
    """Mirror a finished sprite for a table-top reflection."""
    flipped = sprite.img.transpose(Image.FLIP_TOP_BOTTOM)
    flipped = gfx.blur(flipped, radius)
    arr = np.array(flipped, dtype=np.float32)
    ramp = np.linspace(0, 1, arr.shape[0], dtype=np.float32) ** 1.5
    arr[..., 3] = arr[..., 3] * (1.0 - ramp)[:, None] * alpha
    return Image.fromarray(arr.astype(np.uint8), "RGBA")
