# SHOT_LIST v2.2 — CHANGELOG

v2.2 is a **correction pass on v2.1**. Nothing is retimed: the 626.37 s clock, the
137-line grid and every `t_in`/`t_out` are byte-identical to v2.1. 186 shots stay 186.

---

## D1 — `person_present`: 37 → 22 (and why the 37 was wrong)

v2.1 found a person by **substring** match on the visual text. Arabic attaches
particles and inflections to the front and back of a word, so the patterns fired
inside unrelated words:

| Pattern | Fired inside | Meaning | Shot affected |
|---|---|---|---|
| يد | **يد**خل | "enters" | 20, 126, 70 |
| يد | وح**يد**ة | "alone" (fem.) | 44 |
| ساق | **ساق**طة / **ساق**ط | "falling light" | 64 |
| وجه | لا **وجوه** — a negation | "no faces" | 10 |
| بشر | لا **بشر** — a negation | "no people" | 18, 19, 37, 41, 43, 70, 88, 95, 103, 155 |

That is how a fireplace chimney (44), a ploughed field (95) and Lake Geneva (100) all
ended up classified as having a person present.

**v2.2 method:** whole-word matching, then a hand-reviewed decision per shot, with
three explicit tables in `build_v22.py`:
`SILHOUETTE_FIGURE` (every SILHOUETTE shot is a human by construction),
`FIRST_PERSON_PART` (a hand, finger, shoulder or body carries the shot),
`NO` (27 shots reviewed and rejected, each with a one-line reason in `NO_NOTE`).

**Measured result: 22 / 186 = 11.8 %.**

```
3   9   15  54  67  71  77  84  85  97  110 111
116 122 123 124 132 138 140 149 161 172
```

Six shots were **added** that v2.1 missed (71 a farmer's back, 85 a shadow leaving a
bag at the door, 107/116/119/175 were added then corrected — see below). Eighteen were
**removed**, among them: 20 (a window), 23 (a shadow at the field edge — kept, see
note), 32 (a shoulder behind frosted glass — kept, see note), 40 (gravel in the air),
42 (a broken plant stem), 44 (a chimney), 64 (shadows cast by objects), 65 (a plough),
74 (hail measured against a hand **out of frame**), 79 (an empty yard), 96 (a
mountain), 100 (a lake), 126 (a door), 135 (a shadow of a head — kept, see note),
176 (a ship), 180 (a shoulder — kept, see note).

Three of my own first-pass calls were wrong and were corrected before delivery:
**107** (tree branches, not a figure), **119** (a hanging coat, no body in it) and
**175** (an aeroplane on a runway). All three now sit in `NO` with a note.

> **Two rows worth your eye:** 23, 32, 135 and 180 are *shadows and partial figures*
> — a farmer's shadow, a shoulder behind frosted glass, the shadow of a bowed head, a
> shoulder in the dark. I count them as person_present because a body casts them and
> the frame is built around that body. If you want a stricter rule ("a body must be
> visible, not implied"), say so and the number drops to 18.

---

## D2 — near-duplicates

| Pair | Problem in v2.1 | v2.2 fix |
|---|---|---|
| **56 / 73** | the same volcanic fissure twice, two chapters apart (Jaccard 0.45 on the text, and visually the same shot) | 73 rewritten: a **hand-width** fissure in ash-covered basalt, a different scale and a different material reading |
| **69** | "a basin of water in a courtyard" dropped into a volcanic beat — it read as a repeat of the window shots and broke the location | rewritten as the beat it was meant to be: a metal spoon in cold water beside the field, steam at first touch — a *heat test*, not a courtyard |
| **12 / 81 / 150** | three condensation windows in three chapters, same idea, same framing | 12 stays (cold light, drops **freezing**); **81** becomes internal frost with a bar-shadow and explicitly no rain; **150** becomes the villa window at night where the standing figure is entirely **outside** the frame and only the reflection is seen |
| **184 / 186** | the investigation table twice, 0.709 text similarity, only the logo sentence differed | **185** rewritten to the room after the light dies (empty chair, table out of depth of field); **186** is now the logo mark alone on black. The table appears once, at 184 |

Re-measured after the rewrites:

- literal duplicate visuals: **0**
- thread-stripped duplicate visuals: **0**
- shot count: **186** (nothing deleted; nothing merged)
- overlaps: **0**, span `00:00:00.070 → 00:10:26.250`

---

## D3 — `space_kind`

Kept as the three-value axis — `person_present` / `domestic_space` / `graphic_space` —
because the plate plan keys off it (see §2 of the review). It is now **derived from
D1**, not from the old regex, so the two columns can never disagree again.

| | v2.1 | **v2.2** |
|---|---:|---:|
| person_present | 37 (19.9 %) | **22 (11.8 %)** |
| domestic_space | 86 (46.2 %) | **101 (54.3 %)** |
| graphic_space | 63 (33.9 %) | **63 (33.9 %)** |

---

## Everything else held

| | v2.1 | v2.2 |
|---|---:|---:|
| Shots | 186 | **186** |
| Mean / median | 2.83 / 2.67 s | **2.83 / 2.67 s** |
| On-screen text | 29.0 % | **29.0 %** |
| Close-ups (MACRO + DETAIL) | 16.7 % | **16.7 %** |
| Duplicates (literal / stripped) | 0 / 0 | **0 / 0** |
| Thread coverage | 11 of 15 scenes | **11 of 15 scenes** |
| Quote cards | 2, verbatim | **2, verbatim** |

File: `SHOT_LIST_v2.2.csv` · UTF-8 with BOM · 186 rows × 26 columns ·
MD5 `47e1a209e9749c1382e4958044576b82` · re-read after writing: 23,220 Arabic
characters, **0** replacement glyphs, **0** empty narration lines.
