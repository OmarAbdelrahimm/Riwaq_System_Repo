# CHANGELOG — SHOT_LIST v2 → v2.1

Every number below is counted by `build_v21.py` from `SHOT_LIST_v2.1.csv`. Nothing is estimated.

## C1 · Narration text restored from the approved script
`narration_line` now carries the **approved script** (`01_FINAL_SCRIPT_v3.md`, 137 VO lines), not the ASR transcript. `asr_line` is kept beside it, clearly labelled, for timing only.

| | measured |
|---|---|
| Lines in the produced SRT | **137 of 137** |
| Lines whose ASR text differed from the script | **55** |
| Word-level ASR substitutions replaced | **66** |
| Example | `فلحين` → `فلاحين` · `القرات دي` → `القارات دي` · `التقوين` → `التقويم` · `زرعوهم` → `زرعهم` |

The 66 edits are the ASR's, not the script's: the script text is the wording that was recorded and approved. The SRT is generated from the script (`make_srt.py`), never from ASR.

## C2 · Quote accuracy (checked character by character)

**Quote 1 — corrected.** v2 read «it **was** a wet, ungenial summer». The 1831 Introduction, Project Gutenberg #42324 (S7) reads:

> «But it **proved** a wet, ungenial summer, and incessant rain often confined us for days to the house.»

`quote_en` is now **«it proved a wet, ungenial summer»**. You were right. The card shows the English on line 1, the Arabic on line 2, and the label «ترجمة» with the source.

**Quote 2 — kept verbatim.** «We will each write a ghost story» is exact, including the comma placement used in the source: Gutenberg prints it inside quotation marks as Byron's line and Mary Shelley attributes it to him, so the credit now reads «بايرون كما ترويه ماري شيلي» (Byron as Mary Shelley reports him) — not a direct Shelley sentence.

## C3 · Golden thread
Two **overlays**, no new shots:

| Shot | Line | Scene | Overlay | Duration |
|---|---|---|---|---|
| 100 | 75 | 4·9 entry to Lake Geneva | enters 0.2 s after the cut, leaves 0.2 s before it | **1.7 s** |
| 169 | 123 | 6·14 jump to the present | enters 0.2 s after the cut, leaves 0.2 s before it | **1.6 s** |

Both shots were extended to 2.1 s by borrowing time from the shot that follows (which stays above 1.3 s). Nothing was retimed against the VO.

Every other scene without a thread has **no location or time change**. Thread coverage is now **11 of 15 scenes**:

| Scene | Why no thread |
|---|---|
| 3·6 | same field, same day — no travel |
| 4·10 | stays at the villa table, the camera does not move |
| 5·13 | London, already threaded at its own entry (shot 146) |
| 6·15 | the closing table, same room as 6·14 |

## C4 · Scale split

| bucket | shots | share |
|---|---|---|
| `person_present` (silhouette, hand, back, limb, shadow) | **37** | 19.9 % |
| `domestic_space` (room, table, road, weather — no body) | **86** | 46.2 % |
| `graphic_space` (map, board, data, doc, thread, end card) | **63** | 33.9 % |

The 7 shots you named were all `human` in v2 and none of them contained a person: 18, 36, 43, 62, 78, 81, 132. All seven are now `domestic_space`. The real person count is **37, not 51**.

## C5 · Close-up share
MACRO + DETAIL went **39/190 = 20.5 % → 31/186 = 16.7 %**. Seventeen close-ups that were not on a narration close-up beat were re-framed wider (list in `build_v21.py`, `PROMOTE`); every one still serves its line. MACRO is now 3 shots — the ones the script actually calls for.

## C6 · Rhythm

**Frankenstein vision, lines 88–90 (19.94 s measured):** six shots → **three**, at **4.33 / 5.75 / 8.94 s**. The 8.94 s frame is the deliberate long hold of the night: the pale student on the floor, uncut.

**Scene 4·10, the ghost-story challenge (10.43 s measured):** six shots of 1.1–2.1 s → **three shots at 3.41 / 2.33 / 3.46 s**.

**Per-chapter rhythm map (measured):**

| Chapter | Shots | Seconds | Mean | Median | Max | >5 s | Text | Person |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 34 | 94.7 | 2.79 | 2.62 | 6.31 | 1 | 29% | 6 |
| 2 | 31 | 93.9 | 3.03 | 3.15 | 5.48 | 1 | 29% | 6 |
| 3 | 34 | 98.8 | 2.90 | 2.67 | 7.21 | 1 | 29% | 8 |
| 4 | 38 | 102.2 | 2.69 | 2.50 | 8.94 | 3 | 24% | 9 |
| 5 | 31 | 82.6 | 2.66 | 2.54 | 4.88 | 0 | 35% | 5 |
| 6 | 18 | 53.2 | 2.96 | 3.44 | 4.40 | 0 | 28% | 3 |

Shot-type distribution per chapter is in `QA_PHASE1_v2.1.md`.

## C7 · Kept
Zero duplicates (literal and thread-stripped, 186/186 distinct) · text 29.0 % · no production labels · no shot labelled static · the three motif wipes are now named in a `transition` column (ink ×4, smoke ×4, thread ×3) · the NOAA date «8 يونيو» untouched · line 84 kept as recorded.

## Wipes
A `transition` column now names the three motif wipes instead of leaving them implicit: **ink ×4**, **smoke ×4**, **thread ×3**. Every other cut is a hard cut.

## Defect found and fixed while publishing this version
The breathing holds were absorbing the **whole** of the following line, leaving 0.05–0.9 s stubs that the sub-1 s pass then deleted. **Four narration lines (15, 34, 105, 136) had no shot at all in v2** and would have been silent over black. The hold now leaves the next line at least 1.3 s; all **137/137** lines are covered and the arithmetic is asserted in the builder.
