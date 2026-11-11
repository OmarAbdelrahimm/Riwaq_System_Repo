#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eng5/tags5.py — a tag layout queue: no two callouts can ever be on screen together.

v4 drew each tag wherever its shot happened to put it, so in the Europe segment the
"أوروبا" tag and the "برد وتراب" strip landed on top of each other in the same corner.

This module makes overlap structurally impossible rather than visually unlikely:

  * four fixed slots (A upper-left, B upper-right, C lower-left, D lower-right)
  * a slot may hold at most one tag, AND only one tag may be on screen at all
  * a tag's entry cannot start until the previous tag's EXIT has fully finished
  * at least STAGGER seconds of dead air between an exit completing and the next entry
  * entry 0.4 s cubic-bezier(0.16, 1, 0.3, 1), 40 px slide, +-2 deg settling to 0
  * exit 0.3 s ease-in
  * hold 2.0-3.5 s, clamped to the tag's voice cue. The floor is 2.0 s rather than 2.5 s
    because the Europe pair has to fit inside a 5.99 s shot: two tags, one at a time, each
    with a 0.4 s entry, a 0.3 s exit and a 0.5 s gap, cannot both hold 2.5 s.

`plan()` produces the timeline; `render()` draws from it. `audit()` re-checks the whole
timeline frame by frame and is what the QA reports, so "0 overlaps" is measured.
"""
from PIL import Image

W, H = 1920, 1080

ENTER = 0.40
EXIT = 0.30
STAGGER = 0.50
HOLD_MIN, HOLD_MAX = 2.0, 3.5
SLIDE = 40.0
ROT = 2.0

SLOTS = ('A', 'B', 'C', 'D')


def cubic_bezier(t, x1=0.16, y1=1.0, x2=0.3, y2=1.0):
    """the CSS curve from the brief, solved for y at time x=t"""
    t = max(0.0, min(1.0, t))
    lo, hi = 0.0, 1.0
    for _ in range(24):
        u = (lo + hi) / 2
        bx = 3 * (1 - u) ** 2 * u * x1 + 3 * (1 - u) * u ** 2 * x2 + u ** 3
        if bx < t:
            lo = u
        else:
            hi = u
    u = (lo + hi) / 2
    return 3 * (1 - u) ** 2 * u * y1 + 3 * (1 - u) * u ** 2 * y2 + u ** 3


def ease_in_cubic(t):
    t = max(0.0, min(1.0, t))
    return t ** 3


class Tag:
    def __init__(self, name, slot, t_in, cue_len, sprite, sfx_in='paper_in', sfx_out='paper_out'):
        self.name = name
        self.slot = slot
        self.t_in = float(t_in)
        self.cue_len = float(cue_len)
        self.sprite = sprite
        self.sfx_in = sfx_in
        self.sfx_out = sfx_out
        self.t_hold_end = None
        self.t_out = None
        self.t_done = None

    @property
    def w(self):
        return self.sprite['sprite'].width

    @property
    def h(self):
        return self.sprite['sprite'].height

    def home(self):
        m = int(round(0.05 * W))
        w, h = self.w, self.h
        if self.slot == 'A':
            return m, int(round(0.08 * H))
        if self.slot == 'B':
            return W - m - w, int(round(0.08 * H))
        if self.slot == 'C':
            return m, H - int(round(0.08 * H)) - h
        return W - m - w, H - int(round(0.08 * H)) - h

    def edge_dir(self):
        if self.slot in ('A', 'C'):
            return -1.0, 0.0
        return 1.0, 0.0

    def state(self, t):
        if t < self.t_in or t >= self.t_done:
            return None
        if t < self.t_in + ENTER:
            u = (t - self.t_in) / ENTER
            return dict(phase='enter', u=u, a=cubic_bezier(u), alpha=min(1.0, u * 1.6))
        if t < self.t_out:
            return dict(phase='hold', u=1.0, a=1.0, alpha=1.0)
        u = (t - self.t_out) / EXIT
        return dict(phase='exit', u=u, a=1.0 - ease_in_cubic(u), alpha=max(0.0, 1.0 - u * 1.05))


class TagLayoutQueue:
    def __init__(self, tags, t_end=30.0):
        self.tags = sorted(tags, key=lambda x: x.t_in)
        self.t_end = t_end
        self._schedule()

    def _schedule(self):
        """walk the queue in time order; nothing enters until the previous tag is gone.

        Global sequencing, not just per-slot: the brief says a tag's entry may not begin
        until the previous EXIT has fully COMPLETED. Two tags in different corners were
        still both on screen at once (66 frames in the first cut), which breaks the
        "one active tag" rule even though no boxes overlapped.
        """
        prev_done = 0.0
        for tag in self.tags:
            ready = prev_done + (STAGGER if prev_done > 0 else 0.0)
            start = max(tag.t_in, ready)
            tag.t_in = round(start, 4)
            hold = max(HOLD_MIN, min(HOLD_MAX, tag.cue_len))
            tag.t_hold_end = round(start + ENTER + hold, 4)
            tag.t_out = tag.t_hold_end
            tag.t_done = round(tag.t_out + EXIT, 4)
            prev_done = tag.t_done

    def active(self, t):
        out = []
        for tag in self.tags:
            st = tag.state(t)
            if st:
                out.append((tag, st))
        return out

    def enters(self):
        return [(tg.t_in, tg.name, tg.slot) for tg in self.tags]

    def exits(self):
        return [(tg.t_out, tg.name, tg.slot) for tg in self.tags]

    def render(self, base, t):
        for tag, st in self.active(t):
            x, y = tag.home()
            dx, _ = tag.edge_dir()
            off = SLIDE * (1.0 - st['a'])
            x = x + dx * off
            rot = ROT * (1.0 - st['a']) * (1 if dx > 0 else -1)
            sp = tag.sprite['sprite']
            bx, by = tag.sprite['box'][0], tag.sprite['box'][1]
            sp = sp.copy()
            if st['alpha'] < 1.0:
                sp.putalpha(sp.split()[3].point(lambda v: int(v * st['alpha'])))
            if abs(rot) > 0.02:
                sp = sp.rotate(rot, expand=True, resample=Image.BICUBIC)
            base.alpha_composite(sp, (int(x - bx), int(y - by)))
        return base

    def audit(self, fps=30, t_end=30.0):
        """frame by frame: how many frames show more than one tag, do any boxes touch"""
        n = int(t_end * fps)
        multi = []
        touching = []
        for i in range(n):
            t = i / fps
            act = self.active(t)
            if len(act) > 1:
                multi.append(round(t, 3))
            boxes = []
            for tag, st in act:
                x, y = tag.home()
                boxes.append((tag.name, x, y, x + tag.w, y + tag.h))
            for a in range(len(boxes)):
                for b in range(a + 1, len(boxes)):
                    A, B = boxes[a], boxes[b]
                    if A[1] < B[3] and B[1] < A[3] and A[2] < B[4] and B[2] < A[4]:
                        touching.append((round(t, 3), A[0], B[0]))
        return dict(frames=n, frames_with_multiple_tags=len(multi),
                    overlap_frames=len(touching), ok=not touching,
                    multi_sample=multi[:5], overlap_sample=touching[:5])
