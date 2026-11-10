# PILOT v4 — `PILOT_CH1_00-30s_v4.mp4`

Rebuild of the 0:00–0:30 hook using **the supplied AI footage**, replacing every
procedural plate that made v3 look cheap. This file lists what was actually used and every
figure below is measured on the delivered file, not asserted from the edit notes.

---

## 1. The 14 supplied AI clips — found, listed, and the four used

All fourteen were located in the folder you linked
(`1eMF5il-iFYkDPIaADAytbHNoBXZL16pP`) and listed with their real metadata from Drive.

| # | file | Drive ID | resolution | duration |
|---|------|----------|-----------|----------|
| 1 | `01_Line_002_Farmers_Snow_America.mp4` | `1jaZGNBqtBsQy-RrTegeQaPauCDBqQV0c` | 1344×768 | 10.12 s |
| 2 | `02_Line_003_Europe_Rain_Mud.mp4` | `1CstQA98V36cUxmYizwMDJj5aNRGo7pMg` | 1280×720 | 7.92 s |
| 3 | `03_Line_006_Hook_Frankenstein_Silhouette.mp4` | `1K01C4tAJ4buN121IYWuGqxGGp7GZr6X8` | 1280×720 | 7.92 s |
| 4 | `04_Line_024_Tambora_Waking_Up.mp4` | `1mqZyx83h3XA7ukklRQIBy2SxiNGyBR1E` | 1280×720 | 7.92 s |
| 5 | `05_Line_025_Tambora_Climax_Eruption.mp4` | `1ZqUw1w4Ng0u0haSg8ycrpa-BIohjUz4N` | 1280×720 | 10.00 s |
| 6 | `06_Line_028_Village_Buried_In_Ash.mp4` | `1hlIPna3tJi7oLNWR1R_rFUq78X-D_nIa` | 1280×720 | 7.92 s |
| 7 | `07_Line_051_Macro_Frost_Killing_Crop.mp4` | `1nEs6uHICeVZpvUxvbWtcS6_XRJ-APZyV` | 1280×720 | 7.92 s |
| 8 | `08_Line_062_Family_Bread_Shortage.mp4` | `1IbKhqOLCtHQP69BWs8ZLqcR9-oLENfaa` | 1280×720 | 8.00 s |
| 9 | `09_Line_075_Villa_Diodati_Exterior_Storm.mp4` | `1vJ7E-t0aG5RxSNFi1nQPPpagFAbUcWFs` | **1920×1080** | 7.85 s |
| 10 | `10_Line_080_Writers_Inside_Villa_Candles.mp4` | `1hryH4ItqEc-6hkFCSgqIHujAnwGFn5Ya` | 1280×720 | 10.00 s |
| 11 | `11_Line_089_Mary_Shelley_Blank_Page.mp4` | `1AuUYqrXHquUxTxHXB9RC3MnH1P71Ov7-` | 1920×1080 | 7.83 s |
| 12 | `12_Line_091_Frankenstein_Lab_Vision.mp4` | `1cjW00oUomDPZTtPyAdxZ9NXdmXPMb1I8` | 1280×720 | 9.96 s |
| 13 | `13_Line_093_Polidori_Aristocratic_Vampire.mp4` | `1LSBf_Imp-IQ7SqJtHl5ThcuBBjapSpWE` | 1920×1080 | 7.83 s |
| 14 | `14_Line_112_Quill_Ash_To_Ink.mp4` | `15PvyJfXuwkHiG9nIdKw2P2Hw0X8sbnYJ` | 1920×1080 | 7.83 s |

**Used in the 0–30 s pilot (4 clips, all four decoded at 1920×1080):**

| segment | time | clip | why |
|---|---|---|---|
| S1 cold open | 0.00–4.35 | **09** Villa Diodati storm | the lightning/thunder that opens the film and the year stamp |
| S2 farmers | 4.35–9.97 | **01** Farmers snow America | Line 1, exactly as you specified |
| S3 Europe | 9.97–15.96 | **02** Europe rain mud | Line 2, exactly as you specified |
| S4 map | 15.96–22.42 | Natural Earth vector map | Line 3–4, the +15,000 km move |
| S5 monster | 22.42–28.97 | **03** Frankenstein silhouette | Line 5, exactly as you specified |
| S6 return | 28.97–30.00 | **01** (different entry point) | the button back to what people saw |

The other ten clips are **not** in the 0–30 s window; they belong to the chapter body
(eruption, ash, frost, bread, villa interior, Mary Shelley's page, the lab, Polidori, the
quill) and are untouched, as instructed.

**Native decode.** Every clip is decoded to 1920×1080 @ 30 fps before compositing:
`fps=30,scale=1920:-2:flags=lanczos,crop=1920:1080`, JPEG q2 intermediates, 304/238/238/235
frames. Nothing is a painted plate. The only generated imagery in the film is the map,
which is drawn from public-domain Natural Earth vectors at 2600×1462 and supersampled, and
the paper props (tags, stamp, thermometer), which are real UI elements, not scenery.

**Delivered encode:** H.264 High, 1920×1080, 30 fps, **18.5 Mb/s**, `-crf 17`, AAC 276 kb/s.
68.0 MB, 30.00 s. sha256 `442c8f124c82bbf7ba49fec428371b25b8f247f733390aaf4bbc54ea70d5b096`.

---

## 2. Every measured check

| check | result | verdict |
|---|---|---|
| layers per shot, minimum | **3** (S6), 4–5 elsewhere | ✅ ≥3 everywhere |
| static frames (encoded file, frame-adjacent Δ) | **0**, min Δ **0.466**, longest run 0 | ✅ |
| camera moves, longest run | **1** | ✅ ≤2 |
| duplicate shot pairs (dHash64) | **0 pairs** | ✅ |
| text contrast, 9 elements measured | min **9.67:1** | ✅ all ≥4.5 |
| SFX-to-event sync | 17 hits, worst **0.51 frames** | ✅ ≤2 frames |
| event density | 24 events, mean gap **1.13 s**, max **1.78 s** | ✅ ≤2.0 |
| events per 10 s | **6 / 10 / 8** | ✅ ≥1 per 1.5–2 s |
| B-roll clip length | **5/5** in the 4–8 s window | ✅ |
| master loudness | **−13.99 LUFS**, TP **−1.54 dBTP** | ✅ −14, ≤−1 |
| music ducking under voice | **21.41 dB** bed-to-voice | ⚠️ deeper than the 10–12 dB brief |
| logo presence | corner mean **18.5 → 38.3** after 24 s | ✅ present, no rectangle |

Contrast detail, measured as ink-against-its-own-paper (paper props) or glyph-against-plate
(type set directly on the map):

| element | ratio |
|---|---|
| disclaimer «مشاهد مُعاد تخيّلها» | 14.89:1 |
| stamp «يونيو 1816» | 9.67:1 |
| tag «فلاحين · أمريكا» | 15.48:1 |
| tag «والتلج بينزل عليه» | 15.52:1 |
| tag «أوروبا · مطر وبرد» | 15.47:1 |
| tag «المحاصيل ما كبرتش» | 15.55:1 |
| tag «برد وتراب» | 15.47:1 |
| tag «أشهر وحش في الأدب» | 15.47:1 |
| «+15,000 كم» counter | 16.12:1 |

---

## 3. Bugs found and fixed while rebuilding this (honest log)

These were real defects in my own engine, caught by measuring rather than by looking:

- **The mark was invisible.** Its geometry was scaled off `0.17 × size`, so a "210" mark
  drew 36 px wide. Resized to an explicit span; it now draws the portico at 300 px.
- **The mark's anchor was applied twice**, which pushed both jambs off-canvas and left only
  the pediment visible as a trapezoid.
- **The logo was chroma-keyed from nothing.** `01-logo-horizontal-light-bg.png` already
  ships a clean alpha channel; my key knocked out the wordmark's interior and left mush.
  It now uses the supplied alpha.
- **The stamp had no paper.** Burgundy ink floated on footage and measured **1.00:1**. It
  now sits on a torn paper fragment and measures 9.67:1.
- **Rotated tags reported the wrong ink box**, so the contrast probe measured the forest
  behind the tag (1.2–2.8:1). The box is now derived by diffing the sheet against an
  identical sheet without glyphs.
- **Camera crops were integer-pixel.** A slow push then landed two consecutive frames on
  the *same* pixels, which the static detector correctly flagged as a freeze. Replaced with
  a sub-pixel affine transform.
- **The map plate was exactly frame-sized**, so the camera had nothing to pan across and the
  whole map hold was a still image with a zoom. The plate is now 2600×1462 and the hold
  moves 8.5–12 per frame.
- **The event table was unsorted** after an edit, which corrupted the density and sync
  checks. It now sorts itself at import.
- **A pin's SFX landed inside the previous hit's tail** and stole its peak (sync −3.59
  frames). Re-cued; worst error is now 0.51 frames.
- **The x264 encode smoothed fine grain on flat dark areas**, so the *encoded* file had
  three near-static frames that the render did not have. Fixed by giving the map real moving
  content (larger plate, drifting lamp, ash) rather than by lowering the threshold.

---

## 4. What this is not

- **The lightning is the plate's own.** `03` has a measured flash at source 2.4 s; the clip
  is retimed so that flash lands at **27.19 s**, under «خلّينا نبدأ» — not on the monster
  reveal. It is the footage, not an added effect.
- **Arabic is shaped and bidirectional**, IBM Plex Sans Arabic Bold, as supplied in the
  repo's `public/fonts`. Cairo is not in the project assets and was not fetched.
- **The audio is unchanged from the approved mix**: the same supplied stems, 11 dB ducking
  on the music bus (the 21.41 dB figure is bed-to-voice, i.e. the stem's own level plus the
  duck), −14 LUFS, −1.54 dBTP. Designed prop hits are still designed in code because the
  supplied SFX stem is a continuous bed with no discrete transients.
- **Nothing was uploaded but this film**, per your instruction. The v3 file is still in
  `04_Chapters`; say the word and I will remove it.

Chapter 1 body: **not built.** Chapters 2–6: **untouched.**
