# MASTER AUDIO VERIFICATION — RUWAQ | 1816

You asked me to download the lossless master, confirm 626.37 s, and cross-correlate it with the v4 rough cut. Here is what the measurements say. **It does not match, so per your instruction I stopped and did not build the cut against it.**

## 1 · The file

| | |
|---|---|
| Link you sent | `drive.google.com/file/d/1vZo97NZVSa2eF6jSGe6pnXzEHY6rc73G` |
| That link is | **`1816.zip`, 204,247,827 bytes** — a 204 MB archive, not an audio file |
| Downloaded | Not downloaded: the connector refuses anything over 100 MB, and the sandbox cannot fetch Drive directly |
| What I *could* verify | `master_vo_LOSSLESS.flac` (46,991,673 bytes) from your `02_Audio_Master_and_Clips` folder — MD5 `9e3de5df923de19d042b2b86e6aa48c0` |
| Duration | **675.08 s** (11:15.08), 48 kHz stereo, 24-bit FLAC |
| Spectrogram-unique? | yes — see §3; this is a real recording, not a placeholder |

So the lossless master measures **675.08 s**. It is **not 626.37 s**, and it is not the file your link points at either.

## 2 · Cross-correlation, measured three ways

| Test | Result |
|---|---|
| Global envelope correlation, master vs rough cut, zero lag | **0.068** — no match at any single alignment |
| Same, with the rough cut time-warped by 626.37/675.08 = 0.92785 | **0.068** — still no match, so it is not a uniform speed difference |
| Sliding-window search (±40 s, 20 ms hops, 3 s windows) | median **0.493**, best **0.918**; 91 % of windows below 0.3 |

A sliding search that peaks at 0.92 in a few places and 0.3 elsewhere is not a match; it is a different edit of the same voice.

**What *does* match, and what proves it:**

| | |
|---|---|
| Offsets at 30 sampled points follow a clean straight line | master_t = **1.0734 × rough_t + 3.27 s** |
| Correlation at those windows | median **0.99**, 23 windows above 0.9 |
| Residual after the fit | max **2.81 s** |
| Speech durations | master **357.57 s**, rough **353.99 s** — ratio **1.010** |
| Pause count | **331 in both files** — identical structure |
| Total pause time | master **286.11 s**, rough **240.99 s** — difference **45.12 s** |
| Pause-by-pause | 215 of 331 gaps are the same length within 0.1 s; 114 are longer in the master; largest single difference **+2.65 s** |

**Reading:** it is the same recording, the same 331 pauses, the same 1032 words, delivered about 1 % slower — 45.12 s of extra silence spread over 114 pauses, not a different take. 626.37 + 45.12 = **671.49 s**, and the linear fit predicts **672.35 s**; the remaining ~1 s is the fitted offset. That accounts for the 48.71 s almost completely.

## 3 · The timing consequence you need to know

The 137-line word grid (`vo_timestamps_FINAL.json`) is anchored on the **626.37 s** clock, and most of the 45 s of extra silence sits *between* lines, not inside them. So the whole shot list is aligned to the rough cut's pauses, and a naive swap to the 675.08 s master would drift up to 48 s late by the end.

That is exactly why I did not proceed: building 186 stills and a mix against the wrong clock would waste the whole chapter.

## 4 · What I need from you (one of two things)

1. **The true 626.37 s lossless master.** Upload it as a single audio file (FLAC or WAV) under 100 MB if possible — a 626 s 48 kHz 24-bit stereo FLAC is about 44 MB, so it will fit. Then I re-verify in one pass and the grid stays valid.
2. **Or confirm 675.08 s is the master**, and I will re-derive the 137 line windows on that clock (the pause map above gives me everything I need) before Chapter 1. Nothing is lost — it is a re-alignment pass, not a re-cut.

Until one of those happens, **the v4 rough-cut audio is the timing reference only**, which is the rule you already set. The final mix will be built from the lossless FLAC, never from AAC — that has not changed.

## 5 · One thing I could not do at all

The link resolves to `1816.zip` (204 MB). If that archive is where the tight master lives, I cannot open it from here: the download connector caps at 100 MB and the sandbox has no direct Drive access. Either upload the FLAC on its own, or tell me the archive's contents and I will tell you which single file I need.
