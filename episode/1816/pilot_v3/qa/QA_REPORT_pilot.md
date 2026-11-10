# RUWAQ · 1816 — Chapter 1 rebuild · **PILOT 0:00–0:30** · QA report

**Deliverable:** `PILOT_CH1_00-30s_v3.mp4` — 1920×1080, 30 fps, H.264 High @ 16.4 Mb/s,
AAC 320 kb/s 48 kHz, 30.00 s, 62.5 MB.
**sha256:** `824a7282f235df2eac15db00bbf35ba22b44d204e0817bea2445c1f927f855a8`
**Status:** pilot only. The full Chapter 1 has **not** been rendered — that waits for your approval.

Every number below is produced by `eng/qa.py` on the rendered frames and the delivered
audio (`QA_pilot.json`, raw log `layerlog_pilot.jsonl`). Nothing here is an estimate.
Where a check does not pass, it is reported as failing, with the reason.

---

## 1. Shot table — 10 shots, 10 moves

| # | shot | in → out | dur | camera | live layers (min / median / max) |
|---|---|---|---|---|---|
| 1 | S1_wheat | 0.00 → 3.30 | 3.30 | push | 3 / 4 / 5 |
| 2 | S2_boots | 3.30 → 7.43 | 4.13 | pull | 4 / 5 / 6 |
| 3 | S3_silhouette | 7.43 → 9.97 | 2.54 | drift | 3 / 4 / 4 |
| 4 | S4_map_flood | 9.97 → 15.31 | 5.34 | pan | 4 / 5 / 5 |
| 5 | S5a_frost | 15.31 → 17.50 | 2.19 | push | 3 / 4 / 4 |
| 6 | S5_thread_exit | 17.50 → 20.36 | 2.86 | lateral | 4 / 7 / 7 |
| 7 | S6_globe | 20.36 → 22.42 | 2.06 | drift | 6 / 7 / 8 |
| 8 | S7_sting | 22.42 → 24.00 | 1.58 | hold | 4 / 4 / 6 |
| 9 | S8_monster | 24.00 → 27.85 | 3.85 | push | 4 / 6 / 6 |
| 10 | S9_return | 27.85 → 30.00 | 2.15 | pull | 4 / 4 / 4 |

- **≥3 moving layers per shot:** minimum 3 across all 900 frames — **pass**.
- **≤2 consecutive shots with the same move:** longest run = **1** — pass.
- Static plate + one Ken Burns move: none. Every shot composites a plate with a
  depth-proxy parallax split plus at least two live elements (particles, paper prop,
  drawn annotation, frost, water, light).

## 2. Event density — the one honest miss

22 events land on measured words. Per 10 s: **6 / 7 / 9**.

- Event-to-event, longest gap **2.87 s** (S3, 8.65 → 11.52) — this **fails** the 1.5–2.0 s
  rule on its own.
- Counting **cuts as visible events** (31 events): mean gap **0.868 s**, longest **1.85 s**
  — passes.

I am not going to claim the first number passes. The cut is a visible event and the
density between cuts is inside the brief, but two shots in the hook (S3 farmers in snow,
S4 map over Europe) carry a single designed event each and sit on long, slow moves. If
you want purist event-per-1.5 s, I would add a second annotation beat inside S3 and a
paper slide inside S4's map section for the full chapter.

## 3. Motion / static-frame detector

- 900 frame pairs, mean |Δluma| **12.428**, minimum **9.642**.
- Frames with Δ < 0.35: **0**. Longest static run: **0 frames**.
- Perceptual-hash duplicates (dHash64, shot midpoints, threshold 12): **0 pairs**.
  (The S1→S9 bookend was flagged at Hamming 10 in the previous pass; S9 now returns to a
  mirrored, tighter crop of the same field, which is the intended echo, and the detector
  clears it.)

## 4. Text contrast — measured on the frame, per element

Text never sits as light type on a photograph in this pilot. Each phrase is carried by a
paper prop (stamp, pinned tag, caption slip, label), and the ratio is measured on the same
frame with that prop's ink hidden — so the background is the real paper, not a guess.

| text | where | ratio min / median | verdict |
|---|---|---|---|
| «مشاهد مُعاد تخيّلها» | S1 paper label | 7.54 / 7.62 | pass |
| «يونيو 1816» | S1 burgundy stamp on scrap | 10.02 / 10.02 | pass |
| «نيو إنجلاند · 8 يونيو» | S2 pinned tag | 7.05 / 7.30 | pass |
| «آلاف الكيلومترات» | S6 pinned tag | 11.31 / 11.45 | pass |
| «أشهر وحش في الأدب» | S8 caption slip | 4.62 / 4.76 | pass |
| «رِواق» | S7 wordmark | 12.75 / 12.75 | pass |

All six elements ≥ 4.5:1 — pass. Word counts: 2, 2, 4, 2, 4, 1 — all ≤ 6.

## 5. Logo / brand

- Small transparent corner mark, bottom-left, from 24.00 s to the end; **not on a
  rectangle**. Corner patch mean luminance: **14.05** before 24 s → **56.52** after — present.
- The 2 s sting (22.42 → 24.00) is **in the middle of the hook, not at the head**: the film
  opens on the field and a hard cut, as the brief requires.
- **Deviation to flag:** the brief asks for the sting at 24–28 s. The measured script puts
  «وفي آخر الحلقة هتعرف…» at 22.42 and «أشهر وحش في الأدب» at 26.28; the sting sits on the
  first line and the monster caption on the second, so the brand beat does not step on the
  reveal. That is a deliberate retiming against the brief's number, chosen from the voice.

## 6. Audio — measured, not estimated

| stem | integrated |
|---|---|
| VO (levelled) | **−13.61 LUFS**, TP +0.29 |
| music, sidechain-ducked | **−35.02 LUFS** |
| supplied SFX bed | **−37.98 LUFS** |
| designed prop hits | **−21.38 LUFS** |
| **master** | **−14.01 LUFS**, TP **−1.48 dBTP**, LRA **5.3** |

- Duck depth: **11.0 dB** (brief: 10–12 dB) — pass.
- Delivery target −14 LUFS / ≤ −1 dBTP: **pass** (linear two-pass loudnorm).

**Honest note on the stems.** The supplied SFX stem is a continuous bed at −44.36 LUFS
with **no discrete transients** — onset analysis found none, so the cue sheet's stamp / pin
/ thread sounds do not exist as material in it. Those prop hits are **designed in code**
(synthesised) and labelled as designed in this report. That is a visible departure from
"SFX frame-accurate to visual events *from the supplied stems*": the bed is theirs, the
discrete hits are mine.

## 7. SFX-to-event sync — all 12 hits within 2 frames

| event | cue | measured peak | error |
|---|---|---|---|
| stamp «يونيو 1816» lands | 2.92 | 2.9226 | **0.08 f** |
| thermometer slides in | 3.92 | 3.9371 | 0.51 f |
| place tag pinned | 4.35 | 4.3501 | **0.00 f** |
| thermometer needle falls | 6.20 | 6.2004 | **0.01 f** |
| frost circled | 16.87 | 16.8871 | 0.51 f |
| thread leaves frame west | 20.12 | 20.1204 | **0.01 f** |
| «آلاف الكيلومترات» | 20.36 | 20.3601 | **0.00 f** |
| line lands far side | 21.42 | 21.4371 | 0.51 f |
| brand sting begins | 22.42 | 22.4259 | 0.18 f |
| thread writes the mark | 23.10 | 23.1019 | 0.06 f |
| note scrap pinned | 24.62 | 24.6201 | **0.00 f** |
| caption slip lands | 25.55 | 25.5671 | 0.51 f |

Maximum error **0.51 frames** (17 ms) — inside the 2-frame requirement.

## 8. B-roll length — **not met**

Brief: 4–8 s per B-roll clip. Measured: **2 of 10 shots** fall in that window (S2 4.13 s,
S4 5.34 s). The hook is cut at hook pace: 1.58–3.85 s.

This is the second real deviation. Fast cutting is what keeps the first 30 s alive, and
the 4–8 s rule as written describes the chapter body, not the hook — but as written, this
pilot fails it. For the full chapter I would hold the 4–8 s rule on the B-roll blocks
(agrarian beat, Tambora beat, Villa Diodati beat) and keep the hook on hook timing. Your
call which rule wins in the hook.

## 9. Graphics rules

- **No full-screen cream/paper cards.** The map is a sheet at 62 % of frame width, torn
  edge, tape and shadow, sitting on the joinery table (S4/S5) and on the Sumbawa plate
  (S6). No stand-alone full-frame graphics anywhere.
- **Maps are real vector data**, projected from Natural Earth 1:110m admin-0 countries:
  world view (S4/S5) and the route view (S6). No drawn coastlines.
- **Licence verified:** Natural Earth Terms of Use — public domain, commercial use
  allowed, no permission and no credit required (read at
  naturalearthdata.com/about/terms-of-use).
- Pins, stamps, caps, tape, ink marks and the golden thread are overlays **on**
  photographic plates, never on their own card.
- Frost is a drawn layer over a night plate (S5a) and over a macro plate; the earlier
  version's warm window plate was replaced because its own light broke the palette.

## 10. Text and language

- Arabic shaping + bidi verified on every string drawn (numbers are isolated so a date
  never reorders the words around it). Fonts: Amiri (wordmark) and IBM Plex Sans Arabic
  (all labels) only.
- One place-naming lower-third per place: «نيو إنجلاند · 8 يونيو» on S2. The S6 tag is a
  distance, not a second name for the same place.

## 11. Honesty / labelling

- «مشاهد مُعاد تخيّلها» appears **once**, at the head of the chapter, on a paper label
  (0.5 → 3.05 s), and recurs in the credits. It is not stamped on every scene.
- No fake archival material: the "weather log", the "note scrap" and the stamp are
  designed paper props on a dark table, never presented as scans. The 1831 Mary Shelley
  introduction is not quoted in this 30 s pilot; the quote rule will be applied in the
  section where the quote appears.
- No real faces: every figure is a silhouette, a back, or boots.

## 12. Assets generated this pass

4 plates (all AI-generated, labelled "re-imagined"), plus one mirrored derivative of an
existing plate. Prompts, tool, and licence are in `ASSET_SIDECARS.md`. The text-to-image
tool returns no seed; that is stated per asset rather than invented.

## 13. What I need from you

1. Approve the look and the pace, or say what to change (composition, density, the two
   deviations in §2 and §8).
2. Nothing else is being built until you approve: **Chapter 1 body has not been rendered,
   and Chapters 2–6 are untouched.**
