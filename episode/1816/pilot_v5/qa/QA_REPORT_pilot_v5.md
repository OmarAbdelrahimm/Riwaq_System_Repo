# Pilot v5 — Chapter 1, 0:00–0:30

Rebuilt from v4 after the review. v4 was footage-correct but had five defects; this is the
answer to each, with the measurement that proves it.

**Deliverable:** `PILOT_CH1_00-30s_v5.mp4` — 1920×1080, 30 fps, 70.0 MB, 30.00 s,
CRF 17 / maxrate 18M, AAC 320k, −13.9 LUFS, true peak −1.1 dBTP.

## The five fixes

| # | Defect in v4 | What v5 does | Measured |
|---|---|---|---|
| 1 | Two callouts shared a corner in the Europe segment | `tags5.TagLayoutQueue`: four fixed slots, one tag on screen at a time, entry only after the previous exit has *completed*, 0.5 s stagger, 0.4 s `cubic-bezier(0.16,1,0.3,1)` entry with 40 px slide and ±2° settle, 0.3 s ease-in exit | 0 frames with >1 tag (of 900); 0 overlapping boxes; max 1 tag in any frame; min exit→entry gap 0.80 s |
| 2 | A white house/pentagon shape at ~24 s | That shape was a *procedurally drawn portico*, not the logo. It is deleted. The sting and the corner watermark are both the supplied `02-logo-horizontal-dark-bg.png` (1600×1063 RGBA, ivory ink, lum 225.2) | native 1600×1063, aspect 1.5052 unchanged, drawn at 300 px wide, no key, no rotation; corner holds 0 ivory px at 23.0 s and 6 717 at 29.0 s |
| 3 | Text SFX too loud and harsh | New soft-body kit (`sfx5`): paper-on-felt slides, a damped wood tap, band-limited rustle. No click, no beep, no short bright transient. Each hit calibrated against the speech in *its own* window | paper hits −14.2 to −15.6 dB under speech (spec −12…−18), 6.5 dB under the music, −33.0 to −37.0 dBFS |
| 4 | Music too slow and ambient | The supplied bed measures 69.8 BPM with 0 % of its energy above 2 kHz — it is a pad and cannot be sped up, so `music5` composes a 116 BPM score: four-on-the-floor, eighth-note ostinato, D minor, tension riser into the sting | 116.5 BPM measured by onset autocorrelation; ducked 11.0 dB under the voice, sitting at −8.0 dB vs voice |
| 5 | Pacing and transitions | Cross-dissolve 0.65 s storm→farmers; whip-pan 0.30 s farmers→Europe; zoom-blur 0.60 s in and out of the map; hard cut into the monster at 22.42; hard cut to the button; Ken Burns on every plate; one grade (`grade5`) and one grain pass over everything | 0 static frames, motion min 4.18 / mean 8.28, ≥3 moving layers every shot, longest shot 6.57 s, 26 events, max event gap 1.75 s |

## Measured QA

Full numbers: `qa/QA_pilot5.json`, `qa/contrast_pilot5.json`, `qa/audio5_meta.json`.

* **Tags** 0 overlap frames · 0 multi-tag frames · 1 tag max · slots A and C used ·
  entries 0.70 / 5.05 / 9.97 / 13.27 / 25.75 · exits 3.70 / 8.35 / 12.47 / 15.67 / 28.55
* **Logo** supplied file only; native 1600×1063; 300 px wide; ivory ink on the darkest
  upper corner; contrast 14.35:1
* **Audio** music −8.0 dB vs voice (ducked 11.0 dB), paper hits −14.2…−15.6 dB under speech,
  sting −10.0 dB (deliberate accent), −13.92 LUFS, TP −1.10, LRA 3.4
* **Music** 116.5 BPM, energy 62 % at 200–600 Hz (a pulse, not a pad)
* **Pacing** 900 frames, 0 static, motion min 4.18, 26 events, max gap 1.75 s, longest shot
  6.57 s, ≥3 layers/shot
* **Transitions** dissolve 9.30, whip 13.08, map zoom 12.60, hard cut 5.00, button 9.46
  (mean frame-to-frame difference across the boundary)
* **Contrast** 10 / 10 elements pass 4.5:1, min 9.67:1 (the 1816 stamp)
* **Shots** S1 4.37 · S2 5.63 · S3 5.97 · S4 6.47 · S5 6.57 · S6 1.00

## Honest notes

* The music is composed, not sourced. The brief asked for 95–120 BPM with a pulse; the
  supplied bed is 70 BPM and spectrally a pad, so it is not used in this cut. The supplied
  bed remains in `02_Audio` and is still the reference if a re-timed version is supplied.
* Tag hold is 2.0–3.5 s, not the 2.5–3.5 s in the brief. Two Europe tags in a 5.99 s shot,
  one at a time with a 0.4 s entry, 0.3 s exit and 0.5 s stagger, cannot both hold 2.5 s.
  The alternative was dropping a tag or letting two overlap — both worse.
* The sting's wordmark writes on right-to-left over 1.2 s. It is a soft-edged reveal of the
  supplied file, not a redraw, and it is a cut-in element, not the 2 s opener.

## Rebuild

`eng/` is the whole engine (`core5`, `tags5`, `pilot5`, `music5`, `sfx5`, `audio5`,
`render5`, `qa5`, `contrast5`, plus `world5` for the Natural Earth map).

```
ffmpeg -i out/pilot5.mp4 -i out/PILOT5_mix_master.wav -map 0:v -map 1:a \
  -c:v libx264 -preset slow -crf 17 -maxrate 18M -bufsize 36M -pix_fmt yuv420p \
  -c:a aac -b:a 320k -shortest -movflags +faststart out/PILOT_CH1_00-30s_v5.mp4
```

Sources and licences are unchanged from v4: see `../pilot_v4/src_manifest/AI_CLIPS.csv`.
Natural Earth 1:110m, public domain. All AI scenes are labelled «مشاهد مُعاد تخيّلها» at
0.70 s.
