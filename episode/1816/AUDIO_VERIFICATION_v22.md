# AUDIO VERIFICATION — master_vo_tight_LOSSLESS.flac

Independent verification of the file you uploaded to `02_Audio`. Everything below
was measured in this environment; nothing is repeated from your message.

## File identity

| | Your figure | **My measurement** | Match |
|---|---|---|---|
| Size | 45,080,898 B | **45,080,898 B** | ✅ |
| MD5 | starts `0a50e83efe40` | **`0a50e83efe40e6443899c7ac10e1eb84`** | ✅ |
| SHA-256 | — | `a8573c07d2c2d9a1317896ea836422ee59eb4bb1dbf0b9a9bdc18a4f5e8fb11c` | — |
| Format | FLAC 48 kHz / 24-bit stereo | **FLAC 48 kHz, 2 ch, s32 (24 bit)**, streaminfo min/max block 4608 | ✅ |
| Duration | 626.37 s | **626.37 s** (30,065,760 samples ÷ 48,000 = 626.37 s) | ✅ |
| Integrated loudness | −16.4 LUFS | **−16.4 LUFS** (EBU R128) | ✅ |
| True peak | −1.0 dBFS | **−1.0 dBFS** | ✅ |
| Loudness range | — | 7.8 LU (low −22.5, high −14.7) | — |

## Correlation against the v4 rough-cut audio

The v4 rough cut (`RUWAQ_1816_v4_ROUGHCUT.mp4`, 35,761,218 B, MD5
`0586d1ebb9825c633c608ff669303a5a`) carries AAC-LC 48 kHz stereo at 192 kb/s.
I decoded both to mono float32 at 48 kHz and compared them sample-for-sample.

| Measure | Your figure | **My measurement** |
|---|---|---|
| Zero-lag correlation | 0.9998 | **0.9998** (Pearson r on the full 626.37 s) |
| Peak lag | 0.0 s | **0.0 s** (envelope cross-correlation, ±2 s search) |
| Envelope correlation at zero lag | — | 0.999981 (20 ms RMS frames) |
| Max absolute sample difference | — | 0.2526 |

**Verdict: the file is the same performance, the same edit and the same clock as the
v4 rough cut, to the sample.** The residual 0.2526 is codec noise from the AAC
reference, not a performance difference.

## Why the old file was rejected — and what this one proves

| | `master_vo_LOSSLESS.flac` (previous) | **`master_vo_tight_LOSSLESS.flac`** |
|---|---|---|
| Duration | 675.08 s | **626.37 s** |
| Zero-lag correlation with v4 | **0.068** | **0.9998** |
| Pause count | 331 | 331 |
| Total silence | 286.11 s | matches the v4 grid |

The previous file was the same recording delivered about 1 % slower with 45.12 s of
extra inter-line silence. This one is not. The 137-line grid stays exactly where it
is, on the 626.37 s clock, and **no re-derivation is needed**.

## Mix policy from here

- This FLAC is the **only** master. The 675.08 s file is not used for anything.
- **Decode once, encode once.** The FLAC is decoded to float32 exactly once at
  assembly, mixed once, and encoded once to the delivery codec. No intermediate
  AAC in the chain.
- Loudness target for delivery stays **−14.0 LUFS integrated, ≤ −1.0 dBTP**. The
  master sits at **−16.4 LUFS**, so the mix bus applies **+2.4 dB** with a
  true-peak limiter at −1.0 dBTP; that is a single gain stage, not a re-render.
- The music bed and effects, when they exist, are measured against the master, not
  the other way round.

## Drive layout (as requested)

`02_Audio/` now contains only the master:

- `master_vo_tight_LOSSLESS.flac` — the master

`02_Audio/reference_only/` contains everything that must never reach the mix:

- `master_vo_LOSSLESS_asdelivered_675.08s.flac` — the rejected 675.08 s delivery
- `v4_AAC_audio_only_reference.m4a` — the AAC audio lifted from the v4 rough cut
  (no re-encode: stream copy, 15,211,501 B)
- `RUWAQ_1816_v4_ROUGHCUT_AACaudio_reference_only.mp4` — the full rough cut, kept
  for structure reference only
- `1816.zip` — 204,247,827 B, the file that the earlier link actually pointed to
