# QA Table — RIW_001_v2 (BAB_ZUWEILA visual-fix build)

## Visual-fix programmatic checks (all PASS)
| # | Check | Method | Result |
|---|-------|--------|--------|
| 1 | Compact pill card law | `card_w == text_w + 64`, `card_h == text_h + 36` asserted for all 18 segments; widths measured by rendered mask bbox | **PASS** — widths 336–1211 px (dynamic per content) |
| 2 | Zero empty ghost rectangles | `card_state()` at 9 gap times (6.0, 16.5, 42.5, 113.5, 143, 170, 187, 216.65, 0.4 s) → `alpha == 0` and `rows is None`; `draw_card` early-returns before any paint at `alpha <= 0.02`; `card_alpha = text_alpha` | **PASS** — 0 empty rectangles |
| 3 | Logo exactly once | source scan: 1× `_load("02-logo…")`; drawn at (56, 44), width 145, alpha 0.80 | **PASS** |
| 4 | Zero Latin letters in Arabic cards | regex `[A-Za-z]` over all 18 segment texts + overlay/label strings | **PASS** — 0 matches |
| 5 | Contrast (ivory vs 0.85 BG + 0.15 bright board) | WCAG relative luminance | **PASS** — 10.44:1 (≥ 4.5) |
| 6 | No static frames | frame deltas at t=2/40/99/160/231 s (t+1/30) | **PASS** — means 0.63–8.16 (> 0.05) |
| 7 | No black frames | mean luminance over 18 samples | **PASS** — min 18.0 (v2) / 80.9 (spot check) |
| 8 | Zero empty guard in code | source inspection | **PASS** |

## State asset usage (v2 fix law)
| State | Time | Background |
|-------|------|-----------|
| S01 | 0.000–6.420 | **Real photo** Bab_Zuwayla_Cairo_12_0864.jpg, tilt-down minarets→towers + zoom-in |
| S02 | 6.420–16.280 | door_front.png — blurred darkened self-fill (25%) + blueprint grid, no sidebars |
| S03 | 16.280–21.230 | **Dramatic photo** Cairo,_bab_zuweila_02.jpeg, slow zoom |
| S04 | 21.230–35.940 | Fatimid Cairo map + Bab Zuwayla marker |
| S05 | 35.940–55.590 | architectural board + historical sightlines |
| S06 | 55.590–71.050 | Fatimid Cairo map, route sweep to gate |
| S07 | 71.050–101.367 | cutout_door.png — blurred fill + engineering dimensions + bearing circles |
| S08 | 101.367–142.933 | **Comparison board** with smart zoom/pan between Fatimid (right) and Mamluk (left) halves |
| S09 | 142.933–158.190 | Wellcome street scene + TIMEA 1906 inset |
| S10 | 158.190–178.360 | David Roberts etching, somber 1517 treatment (burgundy < 5%) |
| S11 | 178.360–216.700 | restoration board + 1998–2003 timeline |
| S12 | 216.700–237.820 | ruwaq_paper_art + Qasr Masmak vector silhouette + Q&A |
Banned: flat beige 3D renders (media_1794277907948 / media_1794277920804) — **never drawn**.

## Card texts (Arabic only, script-exact)
18 cue-merged segments (see `scripts/rv_engine.py SEGMENTS`); S7 replaced `توثيق ARCE: …` with
`توثيق مركز الأبحاث الأمريكي: 6م ارتفاع × 3م عرض × 4 أطنان` — 0 Latin letters anywhere.

## Spec compliance (standing)
- Pure stateless `draw(t)` ✅ · float32 math → `np.clip(...).astype(np.uint8)` ✅ · 1920×1080 30 fps ✅
- Whips at state boundaries (0.35 s, 3-sample), morph margins ≥ 0.35 s ✅
- Audio: MASTER_FINAL bed −14.0 LUFS / −1.4 dBTP, mapped 1:1 with visuals ✅
- HUD: logo (56,44) w145 α0.8 + 2 px gold progress bar only — no watermark/caption/counter ✅
