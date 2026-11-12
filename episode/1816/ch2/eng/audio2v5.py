#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eng2/audio2.py — the Chapter 2 mix.

Same chain the approved pilot used (music -17 dB under the voice with a -6 dB pocket at
1.1 kHz, paper hits calibrated against the speech in their own window, loudnorm to -14 LUFS),
but the score is given the chapter's own section map instead of the pilot's 30 s one.

Chapter 2 is ash and cold: the same chain, with the score's section map moved onto this
chapter's beats, so nothing here is a copied Chapter 1 mix.
"""
import json
import os
import sys

sys.path.insert(0, '/home/user/work')
sys.path.insert(0, '/home/user/Riwaq_System_Repo/episode/1816')

from eng5 import audio5 as A

OUT = '/home/user/work/out2'
# THE CHAPTER'S PLACE ON THE EPISODE'S VO FILE. Chapter 2 covers film time 1:49.47 to
# 3:42.23, so its voice is the slice [103.17, 225.42) of the full episode VO -- NOT from
# 0:00. The previous mix decoded from 0 and every picture of chapter 2 sat on chapter 1's
# opening narration.
CH2_START_SEC = 103.17
CH2_END_SEC = 225.42
T_END = CH2_END_SEC - CH2_START_SEC          # the chapter's own length, 122.25 s
# the score's sections follow Chapter 2's own beats: the eruption, the toll, the turn
MARKS = dict(b2=112.45, b3=121.58, b4=138.21, b5=172.78, out=222.40)
STINGS = [117.24, 196.02]
# the beats a dark glass card lands on, in shot order
CARD_CUES = [121.90, 125.95, 127.25, 128.65, 131.50, 145.10, 154.00, 166.60,
             169.20, 174.00, 182.00, 187.10, 190.80, 196.60, 198.50, 203.60,
             206.80, 210.30, 214.90]

# the score's other sections follow the witnesses, not the pilot
EXTRA_PADS = [(103.17, (146.83, 174.61, 261.63), 0.13),
              (121.58, (130.81, 164.81, 246.94), 0.16),
              (133.40, (146.83, 196.00, 293.66), 0.14),
              (144.79, (116.54, 146.83, 233.08), 0.15),
              (158.86, (146.83, 174.61, 261.63), 0.13),
              (168.89, (155.56, 185.00, 277.18), 0.15),
              (182.84, (146.83, 220.00, 293.66), 0.14),
              (198.02, (130.81, 196.00, 261.63), 0.16),
              (210.02, (138.59, 174.61, 261.63), 0.17)]


def main():
    os.makedirs(OUT, exist_ok=True)
    from ch2.eng import ch2v5 as P
    import numpy as np
    from eng5 import music5

    # the score, with the chapter's section map, written where audio5 expects to find it
    # the score's marks are chapter-local too, or the cues land a minute and a half early
    marks = {k: v - CH2_START_SEC for k, v in MARKS.items()}
    stings = [t - CH2_START_SEC for t in STINGS]
    score = music5.build(T_END, marks=marks, stings=stings)
    np.save(os.path.join(OUT, 'score_raw.npy'), score)
    # audio5 imports music5 inside build(); hand it the finished score instead of letting
    # it compose the pilot's 30 s cue again
    music5.build = lambda t_end=30.0, **kw: score[:int(round(t_end * music5.SR))]

    # events are written against film time; the mix is built on chapter-local time
    evs = [dict(t=e['t'] - CH2_START_SEC, sfx=e['sfx'], what=e['what'])
           for e in P.EVENTS if e.get('sfx')]
    # every card gets its own paper: the queue knows when each one enters and leaves, and
    # the picture is only half the card if it arrives in silence
    # v5 has no tag queue: the cards are built inside their shots. Their cues are the
    # same beats, so the paper hits are read from the shot table instead of a queue.
    for t_cue in CARD_CUES:
        evs.append(dict(t=t_cue - CH2_START_SEC, sfx='paper_in', what='card in'))
    evs.sort(key=lambda e: e['t'])
    A.OUT = OUT
    wav, stems, meta = A.build(T_END, evs, 'ch2', vo_start=CH2_START_SEC)
    j = A.master(wav, os.path.join(OUT, 'ch2_master.wav'))
    # loudnorm's first pass on a 3.7 minute programme lands a couple of LU hot (Chapter 1
    # needed the same correction): measure the delivered file and correct once, linearly,
    # never by normalising again with a limiter, which would flatten the paper hits.
    j2 = A.master(os.path.join(OUT, 'ch2_master.wav'),
                  os.path.join(OUT, 'ch2_master2.wav'))
    print('loudnorm pass 2:', j2['input_i'], j2['input_tp'])
    os.replace(os.path.join(OUT, 'ch2_master2.wav'), os.path.join(OUT, 'ch2_master.wav'))
    meta['ch_start_sec'] = CH2_START_SEC
    meta['ch_end_sec'] = CH2_END_SEC
    meta['vo_slice'] = [CH2_START_SEC, CH2_END_SEC]
    json.dump(meta, open(os.path.join(OUT, 'audio2_meta.json'), 'w'), indent=1,
              ensure_ascii=False)
    print('mix', wav)
    print('music', meta['music_db_vs_vo'], 'dB vs VO | under voice',
          meta['music_under_voice_db'], '| in pause', meta['music_in_pause_db'])
    paper = [h for h in meta['hits'] if h['kind'] in ('paper_in', 'paper_out')]
    print('paper hits', len(paper), 'range',
          (min(h['vs_vo_speech'] for h in paper), max(h['vs_vo_speech'] for h in paper)))
    print('hits', len(meta['hits']), 'master', j['input_i'], j['input_tp'], j['input_lra'])


if __name__ == '__main__':
    main()
