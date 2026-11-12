#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""proof1.py — the acceptance artefact: CH2_PROOF_FRAMES.jpg

Six frames, pulled from the engine at the six times the review asked for, assembled as a
2 x 3 grid at 960 x 540 per cell. Every cell is labelled with its timecode and with what
the reviewer should be looking at, so a claim cannot be made without the frame to back it.
"""
import sys

sys.path.insert(0, '/home/user/work')
sys.path.insert(0, '/home/user/Riwaq_System_Repo/episode/1816')

from PIL import Image                                     # noqa: E402
from eng5 import core5 as C                               # noqa: E402
from ch2.eng import ch2 as P                              # noqa: E402

CELL = (960, 540)
PROOF = [
    (108.6, '1:48.6  land on Sumbawa · إبريل ١٨١٥'),
    (119.6, '1:59.6  the section: 4300 m down to 2850 m'),
    (123.3, '2:03.3  VEI 7 · تامبورا ١٨١٥ marked on the bar'),
    (141.0, '2:21.0  clip 06 — the buried village, faces cropped out'),
    (148.0, '2:28.0  عشرات الآلاف, counted on stock'),
    (197.0, '3:17.0  the veil goes round the planet'),
]

BAR = 46
HDR = 54


def frame_from_master(t):
    """pull the graded, encoded frame out of the delivered master: the proof must show
    what was delivered, not what the engine produced before encoding."""
    import subprocess
    # the chapter master is chapter-local: seeking film time would land past the end of
    # the file and hold the last frame, which is how the first proof sheet showed the
    # same map in all six cells
    subprocess.run(['/home/user/ffmpeg', '-v', 'error', '-y', '-ss', f'{t - P.T0:.3f}',
                    '-i', '/home/user/work/out2/RUWAQ_CH2_master_av.mp4', '-frames:v', '1',
                    '/tmp/_proof.png'], check=True)
    return Image.open('/tmp/_proof.png').convert('RGB')


def main(out='/home/user/work/out2/CH2_PROOF_FRAMES.jpg'):
    cells = []
    for t, cap in PROOF:
        im = frame_from_master(t).resize(CELL, Image.LANCZOS)
        cell = Image.new('RGB', (CELL[0], CELL[1] + BAR), (18, 16, 14))
        cell.paste(im, (0, 0))
        d = __import__('PIL.ImageDraw', fromlist=['ImageDraw']).Draw(cell)
        d.rectangle([0, CELL[1], CELL[0], CELL[1] + BAR], fill=(18, 16, 14))
        sp = C.text_sprite(cap, 26, fill=(238, 230, 214))
        cell.paste(sp, (16, CELL[1] + (BAR - sp.height) // 2), sp)
        cells.append(cell)

    W = CELL[0] * 3
    H = (CELL[1] + BAR) * 2 + HDR
    sheet = Image.new('RGB', (W, H), (12, 11, 10))
    d = __import__('PIL.ImageDraw', fromlist=['ImageDraw']).Draw(sheet)
    head = C.text_sprite('RUWAQ 1816 · CHAPTER 2 · PROOF FRAMES', 30, fill=(230, 200, 150))
    sheet.paste(head, (18, (HDR - head.height) // 2), head)
    note = C.text_sprite('frames from the delivered master, 1920x1080 -> 960x540 per cell', 24,
                         fill=(150, 142, 130))
    sheet.paste(note, (W - note.width - 18, (HDR - note.height) // 2), note)
    for k, c in enumerate(cells):
        x = (k % 3) * CELL[0]
        y = HDR + (k // 3) * (CELL[1] + BAR)
        sheet.paste(c, (x, y))
    sheet.save(out, quality=92, subsampling=0)
    print('proof', out, sheet.size)


if __name__ == '__main__':
    main()
