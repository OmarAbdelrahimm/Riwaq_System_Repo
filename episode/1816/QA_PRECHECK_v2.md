# QA PRECHECK — SHOT_LIST v2

Measured on the list, not on rendered frames. Scope: **190 shots · 0.07 → 626.25 s** of the 626.37 s locked master · **15 scenes** · 6 chapters.
Source: `build_v2.py` → `qa_v2.txt`. Every figure below is produced by code from `SHOT_LIST_v2.csv`; none is an estimate.

> These are *list* gates. Frame-audit gates (pHashes on real frames, text-only frames, Arabic shaping on pixels, loudness) belong to Phase 4+ and are **not** claimed here.

| # | Gate | Target | Measured v2 | Verdict |
|---|---|---|---|---|
| 1 | Duplicate visuals — literal | 0 | **0 / 190** | ✅ PASS |
| 2 | Duplicate visuals — thread prefix stripped | 0 | **0 / 190** | ✅ PASS |
| 3 | Distinct visual strings | 190 | **190 / 190** | ✅ PASS |
| 4 | On-screen text overall | ≤ 40 % | **27.9 %** (53/190) | ✅ PASS |
| 5 | On-screen text per chapter | ≤ 40 % | 30.3 · 30.0 · 29.4 · 19.6 · 36.7 · 23.5 % | ✅ PASS |
| 6 | Key-phrase length | ≤ 6 words | max **5** (43 key phrases) | ✅ PASS |
| 7 | Quote cards | 2, EN + AR + «ترجمة» + source | **2** — shot 99, shot 109 | ✅ PASS ⚠ note 1 |
| 8 | MACRO share | ≤ 18 % | **3.7 %** (7/190) | ✅ PASS |
| 9 | Consecutive shots of one type | < 3 | max **2** | ✅ PASS |
| 10 | Consecutive graphic shots | ≤ 5 | max **4** | ✅ PASS |
| 11 | Shot length floor | ≥ 1.0 s | **1.02 s** | ✅ PASS |
| 12 | Shot length ceiling | ≤ 8 s | **7.21 s** | ✅ PASS |
| 13 | Breathing shots 5–8 s | present | **5** — 24 (6.55), 33 (6.31), 56 (5.48), 97 (7.21), 190 (6.35) s | ✅ PASS |
| 14 | Static / locked-off shots | 0 | **0** | ✅ PASS |
| 15 | Overlapping timecodes | 0 | **0** | ✅ PASS |
| 16 | Unexplained gaps | 0 | max **1.379 s**, sits on a real VO pause | ✅ PASS |
| 17 | Numbers on screen | ≤ 3, sourced | **3** — «8 يونيو» (S3 NOAA), «إبريل 1815», «1818» | ✅ PASS ⚠ note 2 |
| 18 | Honesty label «مشاهد مُعاد تخيّلها» | once, early | **1** — shot 4 at 00:09.97 | ✅ PASS |
| 19 | Production labels / counters / timecodes on screen | 0 | **0** | ✅ PASS |
| 20 | Quote translation rule | Arabic must be labelled «ترجمة» | both cards carry it + the source line | ✅ PASS |
| 21 | Golden thread | at every location change | **14 shots across 9 of 15 scenes** | ⚠ PARTIAL — note 3 |
| 22 | Storm at Villa Diodati | rain + lightning + candles + shadow | **4 lightning/thunder**, **10 rain/wet**, **6 candle/interior**; scene 9 = 23.0 s / 11 shots | ✅ PASS |
| 23 | Ghost-story challenge weight | expanded beyond v1's 3 shots | **6 shots (9.2 s)** at the table + **scene 11 = 70.1 s / 29 shots** for the night itself | ✅ PASS |
| 24 | Atmosphere cutaway | 20–30 s, causal, no repeats | **29.49 s / 9 shots** gas → aerosol → winds → condensation → reflection → cooler surface → gauge falls → cold ground | ✅ PASS |
| 25 | Human-scale, no faces | present in every chapter but 2 | hands/backs/silhouettes 52, market 2, bare table 4, stove 11, road blocked 1 | ✅ PASS |
| 26 | Word-anchored cuts | every boundary on a measured word | **190/190** | ✅ PASS |
| 27 | Line 84 / C11a | kept as recorded, flagged | kept — shots 118–119 | ⚠ WARNING — note 4 |

**Composition:** WIDE 20.0 % · DETAIL 16.8 % · SILHOUETTE 11.1 % · MEDIUM 11.1 % · THREAD 7.4 % · BOARD 7.4 % · DATA 7.4 % · DOC 5.3 % · MAP 4.7 % · HUMAN 4.7 % · MACRO 3.7 % · END 1 shot.
**Text mix:** key_phrase 43 · lower_third 4 · stamp_motif 3 · quote_card 2 · honesty_label 1.
**Duration:** mean 2.79 s · median 2.66 s · mean dwell (dur + following pause) 3.30 s.

## Notes on the four items that are not a clean PASS

1. **Note 1 — the second quote is 7 words.** "We will each write a ghost story" is the primary quotation (S6/S7, public domain). The ≤6-word rule was written for key phrases; a quotation cannot be clipped without misquoting. Card carries EN, AR, «ترجمة» and the source. *Say the word and I cut a different 5-word line from the same paragraph instead.*
2. **Note 2 — what counts as a "number".** «8 يونيو» is the only figure with a primary source (NOAA NCEI). «إبريل 1815» and «1818» are date stamps on lower-thirds, both VERIFIED in `FACT_CHECK_SHEET.csv`. If the rule means *any digit at all*, then it is 3 and still inside the cap; if it means *quantities*, it is 0.
3. **Note 3 — the six bare scenes are a decision, not an oversight.** Thread appears at: field (1·1), New England (1·2), Tambora (1·3), eruption (2·4), the mechanism (2·5), cold world (3·7), the question of place (3·8), the villa (4·11), London (5·12). It is deliberately absent at **3·6** (survivable cold — no travel), **4·9** (the storm is where travel stops), **4·10** (the challenge — a thread would trivialise it), **5·13** (no location), **6·14** and **6·15** (the present day — the thread belongs to 1816). Adding 6 more thread shots is possible; each costs one human-scale shot. **Your call — I did not choose.**
4. **Note 4 — line 84.** Stills kept at the recorded wording; it names four people in one breath. Re-recording that line would change the read, not the cut. Noted as a delivery warning, not a defect.

## Still owed at frame level (Phase 4+)
pHash duplicate detector · text-only-frame detector · Arabic shaping/spelling on every rendered text frame · style consistency across 190 stills · loudness (LUFS-I, true peak, unintended silence) · thread continuity on the rendered timeline. Each will ship with a contact sheet.

## Files
`SHOT_LIST_v2.md` (readable, per-scene) · `SHOT_LIST_v2.csv` (machine) · `SHOT_LIST_v2_CHANGELOG.md` (v1 → v2) · `beats.json` (content source of truth) · `build_v2.py` (reproducible) · `qa_v2.txt` (raw output).
