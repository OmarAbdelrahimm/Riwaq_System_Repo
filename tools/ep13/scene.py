"""RUWAQ EP13 — the 0-6 s motion proof, frame as a pure function.

Design space is 1920x1080; the proof renders at 1280x720 (review size) with a
2x supersample and a Lanczos downsample. Every value below is deterministic in
the frame number: no clocks, no unseeded randomness, no CSS animation.

Layer order (back to front): baked atmosphere → stage pool → far cards →
heroes (own plane) → connector → near cards → typography → dust → foreground
occluder → vignette + grain.
"""

from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
from PIL import Image

from . import gfx, heroes, stage
from .text import engine
from .tokens import BRAND, FONTS, PLANES, RIM
from .timeline import (BEATS, CLAIM, CLAIM_FOOTER, CLAIM_LABEL, EVIDENCE_LABEL,
                       EVIDENCE_NOTE, EVIDENCE_TITLE,
                       FRAMES, HEADLINE, KICKER, MICRO, PHRASES, REPEAT_KICKER,
                       REPEAT_TITLE, S1, S2, S3)

COL = {"parchment": BRAND["parchment"], "gold": BRAND["gold_light"],
       "stone": BRAND["stone"], "ivory": RIM["ivory"], "gold_deep": BRAND["gold"]}


class Renderer:
    def __init__(self, width: int = 1280, height: int = 720, ss: int = 2):
        self.W, self.H, self.SS = width, height, ss
        self.canvas = (width * ss, height * ss)
        self.k = (width / 1920.0) * ss           # design px -> canvas px
        self.eng = engine()
        self.bg = stage.bake_background(self.canvas)
        self._plate = None
        self._plate_refl = None
        self._pool = None

    # -- scaling helpers ----------------------------------------------------
    def px(self, v: float) -> float:
        return v * self.k

    def font(self, key: str, size_design: float) -> tuple[str, int]:
        return FONTS[key], max(6, int(round(self.px(size_design))))

    # -- camera -------------------------------------------------------------
    def camera(self, f: int) -> stage.Camera:
        if f < S2[0]:
            t = gfx.clamp01((f - 20) / 34.0)
            pan = -14.0 * gfx.ease_in_out(t)
            zoom = 1.0 + 0.020 * gfx.ease_in_out(t)
        elif f < S3[0]:
            pan = -14.0 - 6.0 * gfx.ease_in_out((f - S2[0]) / 20.0)
            zoom = 1.020 + 0.010 * gfx.ease_in_out((f - S2[0]) / 20.0)
        else:
            t = gfx.ease_in_out((f - S3[0]) / 89.0)
            pan = -20.0 + 30.0 * t
            zoom = 1.030 - 0.030 * t
        return stage.Camera(pan_x=pan, pan_y=2.0 * math.sin(f * 0.02), zoom=zoom)

    def place(self, x: float, y: float, plane: float, cam: stage.Camera) -> tuple[float, float]:
        dx, dy = cam.plane(cam.pan_x, cam.pan_y, plane)
        zx = 960 + (x - 960) * cam.zoom if cam.enabled else 960 + (x - 960)
        zy = 540 + (y - 540) * cam.zoom if cam.enabled else 540 + (y - 540)
        return self.px(zx + dx), self.px(zy + dy)

    # -- static assets ------------------------------------------------------
    def plate(self) -> heroes.Sprite:
        if self._plate is None:
            self._plate = heroes.plate_sprite(s=self.px(1.02))
            self._plate_refl = heroes.floor_reflection(self._plate, alpha=0.18)
        return self._plate

    def plate_refl(self) -> Image.Image:
        self.plate()
        assert self._plate_refl is not None
        return self._plate_refl

    def pool(self) -> Image.Image:
        if self._pool is None:
            self._pool = gfx.radial(self.canvas, (self.px(960), self.px(830)), self.px(680),
                                    BRAND["gold"], 0.10, 2.2, aspect=0.42)
        return self._pool

    # -- type helpers -------------------------------------------------------
    def line(self, img, words, font_key, size, baseline, *, right=None, center=None,
             alpha=1.0, offsets=None, tracking=0.0, space=None):
        fp, sz = self.font(font_key, size)
        return self.eng.draw_line(
            img, [(t, COL[c]) for t, c in words], fp, sz, self.px(baseline),
            right=None if right is None else self.px(right),
            center=None if center is None else self.px(center),
            alpha=alpha, word_offsets=offsets, tracking=self.px(tracking),
            space=None if space is None else self.px(space))

    # -- cards --------------------------------------------------------------
    def card(self, *, w=600, h=320, title=CLAIM, label=CLAIM_LABEL, footer=CLAIM_FOOTER,
             accent=BRAND["gold_light"], tilt=0.0, alpha=1.0, muted: float = 0.0) -> Image.Image:
        k = self.k
        cw, ch = int(round(self.px(w))), int(round(self.px(h)))
        card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        pad = int(self.px(6))
        body = gfx.mask_rrect((cw, ch), (pad, pad, cw - pad, ch - pad), self.px(22), soft=self.px(1.2))

        fill = gfx.linear_gradient((cw, ch), [
            (0.0, "#232830", 0.96), (0.35, "#181B22", 0.97),
            (0.72, "#111318", 0.98), (1.0, "#0B0C0F", 0.98)], 96.0)
        card = gfx.over(card, gfx.apply_mask(fill, body))

        # inner top sheen + bottom falloff
        card = gfx.screen(card, gfx.apply_mask(gfx.linear_gradient((cw, ch), [
            (0.0, "#FFFFFF", 0.10), (0.28, "#FFFFFF", 0.0)], 90.0), body))
        card = gfx.over(card, gfx.apply_mask(gfx.linear_gradient((cw, ch), [
            (0.62, "#000000", 0.0), (1.0, "#000000", 0.35)], 90.0), body))

        # illuminated keyline
        edge = gfx.stroke(body, max(1.0, self.px(1.4)), soft=self.px(0.6))
        key = gfx.apply_mask(gfx.linear_gradient((cw, ch), [
            (0.0, accent, 0.85), (0.45, accent, 0.22), (1.0, accent, 0.45)], 20.0), edge)
        card = gfx.screen(card, key, 0.9)

        # content: label + gold dot (RTL: dot sits at the leading edge of the label)
        fp, sz = self.font("body", 25)
        lab = self.eng.word(label, fp, sz, gfx.mix(BRAND["stone_light"], BRAND["stone"], muted))
        lab_img = lab.image if muted < 0.01 else gfx.multiply_alpha(lab.image, 1.0 - 0.45 * muted)
        lab_x = int(cw - pad - self.px(30) - lab.width)
        card.alpha_composite(lab_img, (lab_x, int(self.px(30) + pad)))
        dot_cx = lab_x - self.px(16)
        dot = gfx.mask_ellipse((cw, ch), (dot_cx, self.px(52) + pad, self.px(5), self.px(5)),
                               soft=self.px(0.6))
        card = gfx.screen(card, gfx.apply_mask(
            gfx.solid((cw, ch), gfx.with_alpha(BRAND["gold_light"], 0.9)), dot))
        # title (right aligned)
        t_words = [(t_, c_) for t_, c_ in title]
        if muted > 0.01:
            t_words = [(t_, "parchment" if c_ == "parchment" else "gold_deep") for t_, c_ in title]
        self.line(card, t_words, "title", 62, baseline=40 + 92, right=w - 46,
                  alpha=1.0 - 0.40 * muted)
        # divider
        dy = self.px(h - 84)
        div = Image.new("L", (cw, ch), 0)
        from PIL import ImageDraw as _D
        _D.Draw(div).line([(self.px(46) + pad, dy), (cw - self.px(46) - pad, dy)],
                          fill=90, width=max(1, int(self.px(1.2))))
        card = gfx.screen(card, gfx.apply_mask(gfx.solid((cw, ch), gfx.with_alpha(accent, 0.5)), div))
        # footer
        fp, sz = self.font("body", 23)
        foot = self.eng.word(footer, fp, sz, gfx.mix(BRAND["stone"], "#0E1014", 0.35 * muted))
        foot_img = foot.image if muted < 0.01 else gfx.multiply_alpha(foot.image, 1.0 - 0.5 * muted)
        card.alpha_composite(foot_img, (int(cw - pad - self.px(30) - foot.width), int(self.px(h - 66) + pad)))

        # soft light sweep across the glass face (subtle, static per instance)
        sweep = gfx.sweep((cw, ch), 0.28, 118.0, 0.16, "#FFFFFF", 0.05, 2.0)
        card = gfx.screen(card, gfx.apply_mask(sweep, body), 0.9)

        if tilt:
            quad = [
                (pad + tilt * self.px(16), pad + abs(tilt) * self.px(10)),
                (cw - pad - tilt * self.px(4), pad - abs(tilt) * self.px(4)),
                (cw - pad + tilt * self.px(6), ch - pad + abs(tilt) * self.px(8)),
                (pad - tilt * self.px(10), ch - pad - abs(tilt) * self.px(6)),
            ]
            card = gfx.warp_quad(card, quad, (cw, ch))
        if alpha < 0.999:
            card = gfx.multiply_alpha(card, alpha)
        return card

    # -- connector ----------------------------------------------------------
    def arc(self, img, p0, p1, progress, *, width=2.2, color=BRAND["gold_light"],
            alpha=1.0, sag=52.0):
        pts = []
        n = 64
        for i in range(n + 1):
            t = i / n
            u = 1 - t
            x = u * u * p0[0] + 2 * u * t * ((p0[0] + p1[0]) / 2) + t * t * p1[0]
            y = u * u * p0[1] + 2 * u * t * ((p0[1] + p1[1]) / 2 + sag) + t * t * p1[1]
            pts.append((x, y))
        cut = max(2, int(len(pts) * gfx.clamp01(progress)))
        vis = pts[:cut]
        layer = Image.new("L", img.size, 0)
        from PIL import ImageDraw as _D
        _D.Draw(layer).line(vis, fill=255, width=max(1, int(round(self.px(width)))), joint="curve")
        glow = gfx.blur(layer, self.px(width * 3))
        img = gfx.screen(img, gfx.apply_mask(gfx.solid(img.size, gfx.with_alpha(color, 0.55 * alpha)), glow), 0.9)
        img = gfx.screen(img, gfx.apply_mask(gfx.solid(img.size, gfx.with_alpha(color, 0.95 * alpha)), layer))
        if progress < 0.999:
            hx, hy = vis[-1]
            head = gfx.mask_ellipse(img.size, (hx, hy, self.px(4.5), self.px(4.5)), soft=self.px(1.0))
            img = gfx.screen(img, gfx.apply_mask(
                gfx.solid(img.size, gfx.with_alpha("#FFF6DF", 0.95 * alpha)), head))
        return img

    def question(self, img, cx, cy, size, reveal, alpha=1.0, color=BRAND["gold_light"]):
        fp, sz = self.font("title", size)
        tile = self.eng.word("؟", fp, sz, color)
        if reveal < 0.999:
            m = gfx.linear_gradient(tile.image.size, [
                (0.0, "#FFFFFF", 0.0), (max(0.001, 1.0 - reveal - 0.08), "#FFFFFF", 0.0),
                (min(1.0, 1.0 - reveal + 0.02), "#FFFFFF", 1.0), (1.0, "#FFFFFF", 1.0)], 90.0)
            tile_img = gfx.apply_mask(tile.image, m.getchannel("A"))
        else:
            tile_img = tile.image
        x = int(cx - tile_img.width / 2)
        y = int(cy - tile_img.height / 2)
        if alpha < 0.999:
            tile_img = gfx.multiply_alpha(tile_img, alpha)
        glow = gfx.blur(tile_img, self.px(9))
        img = gfx.screen_at(img, glow, x, y, 0.55)
        img.alpha_composite(tile_img, (x, y))
        return img

    def stage_tile(self, box, r, alpha=1.0) -> Image.Image:
        """The RUWAQ glass stage: one rounded tile the heroes stand inside."""
        x0, y0, x1, y1 = (self.px(v) for v in box)
        tile = Image.new("RGBA", self.canvas, (0, 0, 0, 0))
        m = gfx.mask_rrect(self.canvas, (x0, y0, x1, y1), self.px(r), soft=self.px(1.6))
        fill = gfx.linear_gradient(self.canvas, [
            (0.0, "#232C3B", 0.62 * alpha), (0.42, "#12171F", 0.40 * alpha),
            (1.0, "#1B2230", 0.52 * alpha)], 124.0)
        tile = gfx.over(tile, gfx.apply_mask(fill, m))
        # top-left soft light inside the glass
        inner = gfx.apply_mask(gfx.linear_gradient(self.canvas, [
            (0.0, RIM["ivory"], 0.16 * alpha), (0.35, RIM["ivory"], 0.0)], 70.0), m)
        tile = gfx.screen(tile, inner)
        edge = gfx.stroke(m, max(1.2, self.px(1.8)), soft=self.px(1.0))
        tile = gfx.screen(tile, gfx.apply_mask(gfx.linear_gradient(self.canvas, [
            (0.0, RIM["ivory"], 0.55 * alpha), (0.55, RIM["ivory"], 0.12 * alpha),
            (1.0, RIM["ivory"], 0.30 * alpha)], 96.0), edge))
        return tile

    def pagination(self, cx, cy, n=5, active=0, alpha=1.0) -> Image.Image:
        """RUWAQ dot pagination — the identity beat the reference uses under its stage."""
        from PIL import ImageDraw as _D
        layer = Image.new("RGBA", self.canvas, (0, 0, 0, 0))
        gap = self.px(30)
        for i in range(n):
            x = self.px(cx) + (i - (n - 1) / 2) * gap
            gold = i == active
            r = self.px(5.4 if gold else 4.2)
            rgba = gfx.rgb(BRAND["gold_light"] if gold else BRAND["stone_light"])
            a = (0.95 if gold else 0.52) * alpha
            dot = Image.new("RGBA", (int(2 * r) + 4, int(2 * r) + 4), (0, 0, 0, 0))
            _D.Draw(dot).ellipse([2, 2, 2 + 2 * r, 2 + 2 * r],
                                 fill=(rgba[0], rgba[1], rgba[2], int(255 * a)))
            if gold:
                glow = gfx.blur(dot, self.px(4))
                layer.alpha_composite(glow, (int(x - r - 2), int(self.px(cy) - r - 2)))
            layer.alpha_composite(dot, (int(x - r - 2), int(self.px(cy) - r - 2)))
        return layer

    # -- main ---------------------------------------------------------------
    def render(self, f: int, camera: bool = True) -> Image.Image:
        f = int(max(0, min(FRAMES, f)))
        cam = self.camera(f)
        cam.enabled = camera
        img = Image.new("RGBA", self.canvas, (4, 5, 9, 255))
        img.alpha_composite(stage.camera_crop(self.bg, self.canvas, cam))

        # ---- stage pool behind heroes (baked once) ----
        img = gfx.screen(img, self.pool())
        # RUWAQ glass stage: one tile holds both heroes, dot pagination beneath it.
        # (see docs/ep13/QC.md — this is the identity beat borrowed from the reference)
        tile_a = gfx.clamp01((f - 2) / 12.0) * (1.0 - 0.88 * gfx.clamp01((f - S3[0]) / 46.0))
        if tile_a > 0.01:
            img.alpha_composite(self.stage_tile((288, 404, 1632, 1024), 48, tile_a))
            img.alpha_composite(self.pagination(960, 1052, 5, 1 if f >= S2[0] else 0, tile_a))

        # ---- scene state ----
        in_s1 = f < S2[0]
        in_s2 = S2[0] <= f < S3[0]
        s3_t = gfx.clamp01((f - S3[0]) / 40.0)
        s2_t = gfx.ease_in_out(gfx.clamp01((f - S2[0]) / 30.0)) if f >= S2[0] else 0.0

        # fish / glass ------------------------------------------------------
        fe = gfx.ease_out_expo(gfx.span(f, BEATS["fish_enter"][0], BEATS["fish_enter"][1] - BEATS["fish_enter"][0]))
        ge = gfx.spring(gfx.span(f, BEATS["glass_enter"][0], BEATS["glass_enter"][1] - BEATS["glass_enter"][0]), 6.5, 2.2)
        fish_x = 566 - 74 * (1 - fe) - 46 * s3_t - 40 * s2_t
        glass_x = 1382 + 96 * (1 - ge) + 40 * s3_t + 56 * s2_t
        fish_y = 762 + 10 * math.sin(f * 0.045) + 26 * s3_t
        glass_y = 730 + 4 * math.sin(f * 0.03 + 1.1) + 22 * s3_t
        fish_rot = -6.5 * (1 - fe) - 1.4 + 1.2 * math.sin(f * 0.05)
        glass_rot = 3.6 * (1 - ge) + 0.6 * math.sin(f * 0.035)
        lift = 30 * (1 - fe) + 5
        hero_alpha = 1.0 - 0.72 * s3_t
        fish_alpha = hero_alpha * gfx.clamp01(fe * 1.4)
        glass_alpha = hero_alpha * gfx.clamp01(ge * 1.3)

        fx, fy = self.place(fish_x, fish_y, PLANES["heroes"], cam)
        gx, gy = self.place(glass_x, glass_y, PLANES["heroes"], cam)
        px_, py_ = self.place(566, 828 + 26 * s3_t, PLANES["heroes"], cam)

        plate = self.plate()
        if fish_alpha > 0.02:
            refl = gfx.multiply_alpha(self.plate_refl(), 0.7)
            img.alpha_composite(refl, (int(px_ - plate.w / 2), int(py_ + plate.h * 0.09)))
        plate.blit(img, px_, py_, rot=0.0, alpha=1.0 - 0.55 * s3_t)

        fish = heroes.fish_sprite(
            s=self.px(1.12), tail=9 * math.sin(f * 0.24) * (0.45 + 0.55 * fe) + 4 * s3_t,
            dorsal=3.0 * math.sin(f * 0.18 + 0.6), pect=6.0 * math.sin(f * 0.21 + 1.2),
            sheen=0.30 + 0.35 * fe, lift=lift, rim=1.0, shadow=1.0)
        fish.blit(img, fx, fy - self.px(46), rot=fish_rot, alpha=fish_alpha)

        glass = heroes.glass_sprite(
            s=self.px(1.0), slosh=0.55 * math.sin(f * 0.13) * (0.6 + 0.4 * ge),
            sheen=0.30 + 0.25 * ge)
        if glass_alpha > 0.02:
            refl2 = gfx.multiply_alpha(heroes.floor_reflection(glass, alpha=0.13), 1.0)
            img.alpha_composite(refl2, (int(gx - glass.w / 2), int(gy + glass.h * 0.145)))
        glass.blit(img, gx, gy, rot=glass_rot, alpha=glass_alpha)

        # ---- connector: arc -> question -> repeat -------------------------
        snout = self.place(fish_x + 150, fish_y - 26, PLANES["heroes"], cam)
        lip = self.place(glass_x - 70, glass_y - 46, PLANES["heroes"], cam)
        if f >= BEATS["arc_draw"][0]:
            prog = gfx.ease_in_out(gfx.span(f, BEATS["arc_draw"][0], 18))
            brk = gfx.span(f, BEATS["arc_break"][0], BEATS["arc_break"][1] - BEATS["arc_break"][0])
            arc_alpha = (1.0 - 0.75 * brk) * (1.0 - 0.6 * s3_t)
            img = self.arc(img, snout, lip, prog, alpha=arc_alpha, sag=118, width=2.4)
            if 0.02 < brk < 0.99:
                # the claim evaporates: points leave the arc's midpoint, no reaction
                mx = (snout[0] + lip[0]) / 2
                my = (snout[1] + lip[1]) / 2 + self.px(58 * 0.55)
                rng = np.random.default_rng(9)
                for i in range(9):
                    ang = rng.uniform(-math.pi, math.pi)
                    dist = self.px(rng.uniform(30, 120)) * gfx.ease_out(brk)
                    a = (1 - brk) * 0.9
                    p = (mx + math.cos(ang) * dist, my + math.sin(ang) * dist - self.px(40) * brk)
                    m = gfx.mask_ellipse(self.canvas, (p[0], p[1], self.px(3.2), self.px(3.2)), soft=self.px(1.0))
                    img = gfx.screen(img, gfx.apply_mask(
                        gfx.solid(self.canvas, gfx.with_alpha(BRAND["gold_pale"], a)), m))

        qa = gfx.clamp01(gfx.span(f, BEATS["question_draw"][0] - 4, 10)) * (1.0 - 1.7 * s3_t)
        if qa > 0.02:
            qx, qy = self.place(1006 - 40 * s3_t, 462 - 30 * s3_t, PLANES["heroes"], cam)
            img = self.question(img, qx, qy, 196 - 40 * s3_t,
                                gfx.ease_in_out(gfx.span(f, BEATS["question_draw"][0], 20)), qa)

        # ---- evidence keyline enters (the transition, not a fade) ---------
        ev = gfx.span(f, BEATS["evidence_enter"][0], BEATS["evidence_enter"][1] - BEATS["evidence_enter"][0])
        if ev > 0.01:
            e = gfx.ease_out_expo(ev)
            x0 = 2060 - 700 * e
            panel = Image.new("RGBA", self.canvas, (0, 0, 0, 0))
            ph = self.px(430)
            y0 = self.px(300)
            m = gfx.mask_rrect(self.canvas, (x0, y0, x0 + self.px(520), y0 + ph), self.px(20), soft=self.px(1.2))
            fill = gfx.linear_gradient(self.canvas, [
                (0.0, "#1F232B", 0.95), (1.0, "#0F1115", 0.97)], 96.0)
            panel = gfx.over(panel, gfx.apply_mask(fill, m))
            edge = gfx.stroke(m, max(1.0, self.px(1.4)), soft=self.px(0.7))
            panel = gfx.screen(panel, gfx.apply_mask(gfx.linear_gradient(self.canvas, [
                (0.0, BRAND["gold_light"], 0.9), (0.6, BRAND["gold_light"], 0.25)], 30.0), edge), 0.9)
            img.alpha_composite(panel)
            sweep = gfx.sweep(self.canvas, 0.5 + 0.4 * (1 - e), 100.0, 0.12, BRAND["gold_pale"], 0.35 * e, 1.8)
            img = gfx.screen(img, gfx.apply_mask(sweep, m), 0.8)
            # RTL block: everything hangs off the right edge of the card
            xr = x0 + self.px(520) - self.px(46)
            fp, sz = self.font("body", 23)
            lab = self.eng.word(EVIDENCE_LABEL, fp, sz, BRAND["stone_light"])
            lab = gfx.multiply_alpha(lab.image, 0.80 * e)
            img.alpha_composite(lab, (int(xr - lab.width), int(y0 + self.px(46))))
            dotm = gfx.mask_ellipse(self.canvas, (xr - lab.width - self.px(20), y0 + self.px(46) + self.px(9),
                                                  self.px(4.5), self.px(4.5)), soft=self.px(0.8))
            img = gfx.screen(img, gfx.apply_mask(
                gfx.solid(self.canvas, gfx.with_alpha(BRAND["gold"], 0.95 * min(1.0, 1.6 * e))), dotm))
            fp2, sz2 = self.font("title", 40)
            ttl = self.eng.word(EVIDENCE_TITLE, fp2, sz2, BRAND["parchment"])
            ttl = gfx.multiply_alpha(ttl.image, min(1.0, 1.6 * e))
            img.alpha_composite(ttl, (int(xr - ttl.width), int(y0 + self.px(108))))
            fp3, sz3 = self.font("body", 24)
            nt = self.eng.word(EVIDENCE_NOTE, fp3, sz3, BRAND["stone"])
            nt = gfx.multiply_alpha(nt.image, 0.9 * min(1.0, 1.6 * e))
            img.alpha_composite(nt, (int(xr - nt.width), int(y0 + self.px(186))))

        # ---- cards -------------------------------------------------------
        if f >= BEATS["claim_card"][0]:
            ct = gfx.spring(gfx.span(f, BEATS["claim_card"][0], 14), 7.0, 2.4)
            if f < S3[0]:
                cx, cy = 1010, 762 - 96 * (1 - ct)
                card = self.card(tilt=0.15, alpha=gfx.clamp01(ct * 1.2))
                x, y = self.place(cx, cy, PLANES["far_cards"], cam)
                shadow = gfx.blur(gfx.multiply_alpha(card, 0.55), self.px(16))
                img.alpha_composite(shadow, (int(x - card.width / 2) + int(self.px(8)),
                                             int(y - card.height / 2) + int(self.px(14))))
                img.alpha_composite(card, (int(x - card.width / 2), int(y - card.height / 2)))
            else:
                # scene 3: claim card travels forward, two anonymous echoes behind
                trav = gfx.ease_in_out(gfx.clamp01((f - S3[0]) / 26.0))
                cx = 1010 + 250 * trav
                cy = 762 - 96 * (1 - ct) + 10 * trav
                card = self.card(tilt=0.18, alpha=1.0)
                for idx, (beat, ox, oy, al, mut) in enumerate((
                        (BEATS["echo_1"], -46, -350, 0.74, 0.62),
                        (BEATS["echo_2"], -398, -188, 0.66, 0.82))):
                    e = gfx.spring(gfx.span(f, beat, 16), 6.0, 2.0)
                    if e <= 0.01:
                        continue
                    echo = self.card(tilt=0.24 * (-1) ** idx,
                                     alpha=al * gfx.clamp01(e) * (1.0 - 0.97 * gfx.ease_out_expo(
                                         gfx.span(f, BEATS["evidence_enter"][0],
                                                  BEATS["evidence_enter"][1] - BEATS["evidence_enter"][0]))),
                                     muted=mut)
                    x, y = self.place(cx + ox - 44 * (1 - e), cy + oy + 18 * (1 - e),
                                      PLANES["far_cards"], cam)
                    img.alpha_composite(echo, (int(x - echo.width / 2), int(y - echo.height / 2)))
                ev_t = gfx.ease_out_expo(gfx.span(f, BEATS["evidence_enter"][0],
                                                 BEATS["evidence_enter"][1] - BEATS["evidence_enter"][0]))
                cx += 150 * ev_t
                cy += 10 * ev_t
                card = gfx.multiply_alpha(card, 1.0 - 0.97 * ev_t)
                x, y = self.place(cx, cy, PLANES["far_cards"], cam)
                shadow = gfx.multiply_alpha(gfx.blur(gfx.multiply_alpha(card, 0.6), self.px(20)), 1.0 - 0.5 * ev_t)
                img.alpha_composite(shadow, (int(x - card.width / 2) + int(self.px(10)),
                                             int(y - card.height / 2) + int(self.px(18))))
                img.alpha_composite(card, (int(x - card.width / 2), int(y - card.height / 2)))

        # ---- typography ---------------------------------------------------
        t_in = BEATS["type_in"]
        # kicker + rule
        ka = gfx.clamp01(gfx.span(f, t_in[0], 12)) * (1.0 - gfx.clamp01((f - 58) / 12.0))
        if ka > 0.02:
            kx, ky = self.px(960), self.px(196)
            fp, sz = self.font("body", 26)
            kick = self.eng.word(KICKER, fp, sz, BRAND["stone_light"])
            al = gfx.multiply_alpha(kick.image, ka)
            img.alpha_composite(al, (int(kx - al.width / 2), int(ky - kick.baseline)))
            rule_w = self.px(58) * gfx.ease_out(gfx.span(f, t_in[0] + 4, 12))
            if rule_w > 1:
                rm = Image.new("L", self.canvas, 0)
                from PIL import ImageDraw as _D
                rr = int(ky - self.px(9))
                _D.Draw(rm).line([(kx + al.width / 2 + self.px(18), rr),
                                  (kx + al.width / 2 + self.px(18) + rule_w, rr)],
                                 fill=int(210 * ka), width=max(1, int(self.px(1.4))))
                img = gfx.screen(img, gfx.apply_mask(
                    gfx.solid(self.canvas, gfx.with_alpha(BRAND["gold"], 0.9)), rm))

        # headline, word by word inside the measured P1 window
        hw = len(HEADLINE)
        offsets = {}
        for i in range(hw):
            st = t_in[0] + 2 + i * 4.5
            p = gfx.ease_out(gfx.clamp01((f - st) / 11.0))
            out = 1.0 - gfx.clamp01((f - 60) / 14.0)
            base = gfx.clamp01(p * out)
            offsets[i] = (0.0, self.px(16 * (1 - p)) * (1 if cam.enabled else 1), base)
        head_alpha = 1.0
        if any(v[2] > 0.02 for v in offsets.values()):
            self.line(img, HEADLINE, "title", 96, baseline=316, center=960,
                      offsets=offsets, alpha=head_alpha, space=self.px(30))

        # micro line
        ma = gfx.clamp01(gfx.span(f, 26, 16)) * (1.0 - gfx.clamp01((f - 58) / 14.0))
        if ma > 0.02:
            fp, sz = self.font("body", 25)
            mi = self.eng.word(MICRO, fp, sz, BRAND["stone"])
            mi = gfx.multiply_alpha(mi.image, 0.9 * ma)
            img.alpha_composite(mi, (int(self.px(960) - mi.width / 2), int(self.px(374))))

        # scene 3 primary phrase, right-aligned block on the left
        rt = gfx.ease_out(gfx.span(f, BEATS["repeat_text"][0], 12)) * (1.0 - gfx.clamp01((f - 150) / 14.0))
        if rt > 0.02:
            fp, sz = self.font("body", 26)
            kick = self.eng.word(REPEAT_KICKER, fp, sz, BRAND["stone_light"])
            kick_img = gfx.multiply_alpha(kick.image, rt)
            kw = self.eng.line_width([REPEAT_KICKER], fp, sz)
            img.alpha_composite(kick_img, (int(self.px(760) - kw / 2), int(self.px(206) - kick.baseline)))
            self.line(img, REPEAT_TITLE, "title", 84, baseline=300, center=740,
                      alpha=rt, space=self.px(26))

        # ---- dust, occluder, finish --------------------------------------
        img = gfx.screen(img, stage.dust(self.canvas, f))
        occ = stage.foreground_occluder(self.canvas, f, total=30)
        img = gfx.over(img, occ)
        img = gfx.vignette(img, 0.30, 1.8)
        img = gfx.grain(img, 0.0085, 1000 + f)
        return gfx.downscale(img, (self.W, self.H)).convert("RGB")


@lru_cache(maxsize=2)
def renderer(width: int = 1280, height: int = 720) -> Renderer:
    return Renderer(width, height)
