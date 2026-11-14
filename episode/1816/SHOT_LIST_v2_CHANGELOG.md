# CHANGELOG — SHOT_LIST v1 → v2

Everything below is counted from the two CSVs. v1 = 164 shots (approved baseline), v2 = 190 shots.

| Measure | v1 | v2 | Why it changed |
|---|---|---|---|
| Shots | 164 | **190** | +26, to break repeats and add human scale |
| Mean duration | 3.19 s | **2.79 s** | shorter because shots are now time-balanced, not word-balanced |
| Median | — | **2.66 s** | |
| Range | 1.11–4.87 s | **1.02–7.21 s** | the ceiling had to rise to buy the 5–8 s breathing beats |
| Shots 5–8 s | 0 | **5** | new: 6.55 / 6.31 / 5.48 / 7.21 / 6.35 s |
| Shots > 8 s | 0 | **0** | held |
| Literal duplicate visuals | 54 shots / 27 strings | **0** | every v2 string is unique, enforced by an assert |
| Duplicates after stripping the thread prefix | 69 | **0** | same assert, second pass |
| On-screen text | 81.7 % | **27.9 %** (53/190) | one text event per narration line instead of per shot |
| MACRO | 25.6 % | **3.8 %** (7/190) | macro was the default cutaway; now it is a deliberate accent |
| SILHOUETTE + HUMAN + MEDIUM | 16 | **48** | the single biggest visual gain: the film has people-shaped space |
| Shots tagged `static` | 19 | **0** | every shot has a move, a rack, a drift or a pause the edit can breathe on |
| Max consecutive same shot type | 4 | **2** | three type breaks applied by `fix_beats.py` |
| Numbers on screen | 5+ | **3** | only sourced numbers survive |
| Quote cards | 0 | **2** | EN + AR + «ترجمة» + source |
| Golden thread | 13 shots / 3 scenes | **14 shots / 9 of 15 scenes** | 6 scenes declared intentionally bare — QA note 1 |
| Lightning / thunder | 0 | **4 shots** | the storm now has weather, not just candlelight |
| Rain / wet texture (ch4) | 3 | **10 shots** | |
| Atmosphere cutaway | 53.0 s / 15 shots | **29.5 s / 9 shots** | 45 % shorter, every shot a different mechanism |
| Ghost-story challenge | 3 shots | **6 shots + 23 in the same night** | the pivot earns its screen time |

## What did not change
Locked VO (626.37 s), the 137-line word grid, the 15 scenes, the chapter split, the brand palette, Amiri + Plex Arabic, 16:9, the 512 px corner mark, no burned-in captions.
