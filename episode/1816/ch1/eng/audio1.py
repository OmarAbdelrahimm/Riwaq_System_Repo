#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eng1/audio1.py — the Chapter 1 mix.

Same chain the approved pilot used (music -17 dB under the voice with a -6 dB pocket at
1.1 kHz, paper hits calibrated against the speech in their own window, loudnorm to -14 LUFS),
but the score is given the chapter's own section map instead of the pilot's 30 s one.
"""
import json
import os
import sys

sys.path.insert(0, '/home/user/work')
sys.path.insert(0, '/home/user/Riwaq_System_Repo/episode/1816')

from eng5 import audio5 as A

OUT = '/home/user/work/out1'
T_END = 109.48
MARKS = dict(b2=4.35, b3=9.97, b4=15.96, b5=22.42, out=25.60)
STINGS = [22.42, 96.11]

# the score's other sections follow the witnesses, not the pilot
EXTRA_PADS = [(33.14, (146.83, 174.61, 261.63), 0.13),
              (46.22, (146.83, 220.00, 293.66), 0.14),
              (57.20, (233.08, 293.66, 349.23), 0.13),
              (64.31, (146.83, 220.00, 349.23), 0.15),
              (71.92, (146.83, 174.61, 293.66), 0.14),
              (79.25, (233.08, 261.63, 349.23), 0.12),
              (88.89, (146.83, 174.61, 261.63), 0.16),
              (102.60, (146.83, 220.00, 293.66), 0.17)]


def main():
    os.makedirs(OUT, exist_ok=True)
    from ch1.eng import ch1 as P
    import numpy as np
    from eng5 import music5

    # the score, with the chapter's section map, written where audio5 expects to find it
    score = music5.build(T_END, marks=MARKS, stings=STINGS)
    np.save(os.path.join(OUT, 'score_raw.npy'), score)
    # audio5 imports music5 inside build(); hand it the finished score instead of letting
    # it compose the pilot's 30 s cue again
    music5.build = lambda t_end=30.0, **kw: score[:int(round(t_end * music5.SR))]

    evs = [dict(t=e['t'], sfx=e['sfx'], what=e['what']) for e in P.EVENTS if e.get('sfx')]
    A.OUT = OUT
    wav, stems, meta = A.build(T_END, evs, 'ch1')
    j = A.master(wav, os.path.join(OUT, 'ch1_master.wav'))
    json.dump(meta, open(os.path.join(OUT, 'audio1_meta.json'), 'w'), indent=1,
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
