# Asset sidecars — Chapter 1 pilot (0:00–0:30)

One row per generated or reused asset. `prompt` is the text actually sent to the image
tool. The tool exposes **no seed, no reference image, no aspect control** — seed is
recorded as `not exposed` rather than invented. Every generated image is used as a
**plate** (a photographic base), never presented as archival material.

Licence for every generated plate: produced for this production with the AI image tool
described below; no third-party rights attached.

| # | file | source | tool | seed | prompt (verbatim) | used in |
|---|---|---|---|---|---|---|
| 1 | `ch1_03_legs_raw.png` | generated | AI image tool (text-to-image) | not exposed | "Low-angle documentary photograph of a 19th-century New England farmer's legs and muddy leather boots standing in a churned, waterlogged field furrow beside young green crops, weathered split-rail fence and bare trees behind, heavy grey overcast June sky, fine drizzle, cold desaturated slate and sage palette, no faces visible, no text, medium format film grain, soft low contrast, cinematic still" | S2 |
| 2 | `ch1_wheat_snow_raw.png` | generated | AI image tool | not exposed | "Photograph of green wheat ears heavy with fresh June snow in a field, snow caked along the stalks and across the furrows, dense grey freezing mist behind, bare trees barely visible, cold pale slate and frost-white palette with green showing through, no people, no text, shallow depth of field, medium format film grain, soft low contrast documentary still" | S1 (cold plate), S9 |
| 3 | `ch1_flooded_crops_raw.png` | generated | AI image tool | not exposed | "Photograph of a flooded 19th-century European crop field after relentless rain, rows of young green crops half submerged in grey-brown standing water with a broken wooden fence post leaning at an angle, black reflections on the water, distant treeline under a leaden sky, cold desaturated slate palette, no people, no text, cinematic documentary still, medium format film grain, soft low contrast" | S4 (second half) |
| 4 | `ch1_frost_leaf_raw.png` | generated | AI image tool | not exposed | "Extreme macro photograph of sharp white frost crystals growing across a single green wheat blade and a dead brown leaf, background of a frosted New England field thrown completely out of focus with frozen mud and grass, overcast blue-grey winter light, cold desaturated slate and pale sage palette, no people, no text, medium format film grain, soft low contrast, no warm tones" | S5a (second half) |
| 5 | `ch1_wheat_snow_mirror_raw.png` | derivative | horizontal mirror of #2 (PIL) | n/a | — (deterministic transform, no generation) | S9 |

## Reused repository assets

| file | origin | licence / status | used in |
|---|---|---|---|
| `LOOK01_field_dawn_2560x1440.png` | supplied look-dev plate (repo + Drive `03_LookDev`) | supplied production asset | S1 (warm plate) |
| `ch1_18_table_raw.png` | repo `episode/1816/build/` (v2.2 plate set) | supplied production asset | S4, S5 (the table the sheet sits on) |
| `ch1_20_window_outside_raw.png` | repo `episode/1816/build/` | supplied production asset | S5a (first half) |
| `ch1_23_shadow_raw.png` | repo `episode/1816/build/` | supplied production asset | S3 |
| `ch1_29_alley_raw.png` | repo `episode/1816/build/` | supplied production asset | S8 |
| `ch1_30_sumbawa_raw.png` | repo `episode/1816/build/` | supplied production asset | S6 |
| Natural Earth 1:110m admin-0 (via geopandas 0.14.4 wheel) | naturalearthdata.com | **public domain**, commercial use allowed, no credit required | map sheets, S4/S5/S6 |

## Drawn, not generated

Brand mark (portico), thread, circle/arrow annotations, paper, tape, pins, stamps, ink
marks, frost shards, water band, grain, vignette, light leak: **drawn in code**
(`eng/core.py`), deterministic from fixed seeds, reproducible frame-for-frame.

## Audio sources

| file | origin | note |
|---|---|---|
| `1816_OMAR_VO_FULL_MIX_48k.flac` | supplied (Drive `02_Audio`) | decoded once, lossless; measured −16.60 LUFS before levelling |
| `1816_ORIGINAL_MUSIC_BED_48k.flac` | supplied | −28.68 LUFS; sidechain-ducked 11 dB under voice |
| `1816_ORIGINAL_SFX_STEM_48k.flac` | supplied | −44.36 LUFS continuous bed, **no discrete transients** |
| designed prop hits (stamp, pin, needle, paper slide, thread, sting, sleet, water) | **synthesised in `eng/audio.py`** | replaces the cue-sheet hits that do not exist in the supplied stem; labelled as designed |
