#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""conform.py — glue the 34 segments, then lay the narration down and master it.

Video: concat of frame-exact segments, 1920x1080/30, CRF 18 master.
Audio: one decode, one gain stage (+2.4 dB to bring -16.4 LUFS to -14.0),
limiter at -1.0 dBTP, resample 48k, then trim to the frame-exact picture window.
Nothing is re-decoded: the FLAC is read once per conform run.
"""
import json, os, subprocess, sys

FF = '/home/user/.local/bin/ffmpeg'
FP = None  # imageio ships ffmpeg only; probe via ffmpeg -i
CUT = '/home/user/work/cut'
VO = '/home/user/Riwaq_System_Repo/google_drive/master_vo_tight_LOSSLESS.flac'
FPS = 30
START_F, END_F = 2, 3284          # from assemble.py: absolute timeline, 0.0667-109.4667s
DUR = (END_F - START_F) / FPS


def run(c):
    p = subprocess.run(c, capture_output=True, text=True)
    if p.returncode:
        print(p.stderr[-3000:]); sys.exit(1)
    return p


def probe(path):
    import re
    p = subprocess.run([FF, '-hide_banner', '-i', path], capture_output=True, text=True)
    e = p.stderr
    dm = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', e)
    dur = int(dm.group(1)) * 3600 + int(dm.group(2)) * 60 + float(dm.group(3))
    vm = re.search(r'Video: .*?, (\d+)x(\d+).*?, ([\d.]+) fps', e)
    am = re.search(r'Audio: (\w+).*?(\d+) Hz, (\w+)', e)
    fr = 1
    return {'format': {'duration': dur},
            'streams': [{'codec_type': 'video', 'width': int(vm.group(1)), 'height': int(vm.group(2)),
                         'r_frame_rate': vm.group(3), 'nb_frames': str(int(round(dur * float(vm.group(3)))))},
                        {'codec_type': 'audio', 'codec_name': am.group(1) if am else 'none',
                         'sample_rate': am.group(2) if am else '0', 'channels': 2}]}


def main():
    run([FF, '-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0',
         '-i', f'{CUT}/concat.txt', '-c', 'copy', f'{CUT}/picture_silent.mp4'])
    v = f'{CUT}/picture_silent.mp4'
    info = probe(v)
    st = [s for s in info['streams'] if s['codec_type'] == 'video'][0]
    print('picture:', st['width'], st['height'], st['r_frame_rate'], st['nb_frames'], 'frames',
          f"= {float(info['format']['duration']):.3f}s")

    # audio: single gain stage -> limiter -> 48k, trimmed to picture window
    af = (f"atrim=start={START_F/FPS:.6f}:end={END_F/FPS:.6f},asetpts=PTS-STARTPTS,"
          f"volume=2.4dB,alimiter=limit=0.80:attack=3:release=80:level=0,"
          f"aresample=48000:resampler=soxr:precision=28")
    run([FF, '-hide_banner', '-loglevel', 'error', '-y', '-i', VO,
         '-af', af, '-ac', '2', '-c:a', 'pcm_s24le', f'{CUT}/audio_mastered.wav'])

    run([FF, '-hide_banner', '-loglevel', 'error', '-y', '-i', v, '-i', f'{CUT}/audio_mastered.wav',
         '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
         '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-g', '60',
         '-c:a', 'aac', '-b:a', '320k', '-ar', '48000',
         '-movflags', '+faststart', '-shortest', f'{CUT}/CH01_cut_v1.mp4'])

    i2 = probe(f'{CUT}/CH01_cut_v1.mp4')
    vs = [s for s in i2['streams'] if s['codec_type'] == 'video'][0]
    as_ = [s for s in i2['streams'] if s['codec_type'] == 'audio'][0]
    print('master:', vs['width'], 'x', vs['height'], vs['nb_frames'], 'frames',
          as_['sample_rate'], as_['channels'], 'ch', as_['codec_name'])
    print('duration:', round(i2['format']['duration'], 3), 'size:', os.path.getsize(f'{CUT}/CH01_cut_v1.mp4'))


if __name__ == '__main__':
    main()
