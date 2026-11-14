#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eng1/sheet1.py — the contact sheet for Chapter 1, cut from the delivered MP4."""
import os
import subprocess
import sys

FF = '/home/user/ffmpeg'
OUT = '/home/user/work/out1'


def build(mp4, dst, cols=6, rows=4, w=320):
    from PIL import Image, ImageDraw
    h = int(w * 9 / 16)
    dur = 109.48
    n = cols * rows
    sheet = Image.new('RGB', (cols * w, rows * h), (10, 10, 12))
    d = ImageDraw.Draw(sheet)
    for k in range(n):
        t = (k + 0.5) * dur / n
        p = f'/tmp/_sh{k}.png'
        subprocess.run([FF, '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', mp4,
                        '-frames:v', '1', p], check=True)
        im = Image.open(p).convert('RGB').resize((w, h))
        x, y = (k % cols) * w, (k // cols) * h
        sheet.paste(im, (x, y))
        lab = f'{int(t // 60)}:{t % 60:04.1f}'
        d.rectangle([x + 4, y + 4, x + 58, y + 22], fill=(0, 0, 0))
        d.text((x + 8, y + 7), lab, fill=(255, 220, 130))
    sheet.save(dst, quality=92)
    return dst


if __name__ == '__main__':
    p = build(os.path.join(OUT, 'ch1_master.mp4'),
              os.path.join(OUT, 'CH1_contact_sheet.jpg'))
    print('contact sheet ->', p)
