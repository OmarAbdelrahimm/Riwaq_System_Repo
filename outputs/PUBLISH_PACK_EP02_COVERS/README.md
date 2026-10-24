# Episode 02 covers — «المقارنة أداة لا معيار»

> Delivered to Drive: folder `الفيديو 02 — المقارنة أداة لا معيار`
> Generator: `scripts/publish/ep02_cover.py` · Rules: `docs/COVER_SYSTEM.md` · Names: `docs/FILE_NAMING.md`

## Files

| File | Purpose |
|---|---|
| `02-CVR-H-A-comparison-is-a-tool-not-a-standard-v1.jpg` | upload cover — variant A (statement) |
| `02-CVR-H-B-upward-or-downward-comparison-v1.jpg` | upload cover — variant B (question) |
| `…-v1.png` | lossless archival master |
| `02-QC-A-thumb-168px-v1.png` / `02-QC-B-thumb-168px-v1.png` | 168px thumb test — the real verdict |

## A ↔ A · B ↔ B

| | Title | Cover |
|---|---|---|
| **A** | المقارنة أداة لا معيار: كيف تسعى للأفضل دون قسوة؟ \| ياسر الحزيمي | `…-A-…` |
| **B** | الصاعدة أم الهابطة؟ المقارنة التي تنفعك وتلك التي تكسرك \| ياسر الحزيمي | `…-B-…` |

**A** = claim + explanation (for people searching the idea). **B** = question splitting two things (for people searching the distinction).
Never mix a cover with the other variant's title.

## What changed from the old cover

| Old | New |
|---|---|
| two-layer frame | **three layers**: 2px champagne → 1px warm-white hairline → 30px corner brackets + bottom-left signature rule |
| big logo + tagline competing with the title | logo same position, smaller (92px) — the text is the hero, not the brand |
| title in one font, one colour | **H1 white (Sans) + H2 champagne (Amiri)** = texture contrast inside one block |
| no rule | 336px rule, shorter than the two words, carrying the eye into the badge |
| no badge | **3D badge** = the quotable claim |
| no bridge | **bridge in a third, lighter face** (Plex Regular) — a different tone that ends the shouting |
| speaker name crammed beside the badge | name on its own line at the bottom — authority without competing |
| dark-filled episode chip | thin outline pill |
| saturated gold | **champagne `#C2AF8F`** only |
| untreated background | directional shading behind a **face-protecting mask** — zero blur on the speaker |

## Layout is measured, not guessed

`CS.ink_size()` measures the **visible ink** of the text (Pillow's `getbbox` returns the font's tallest
ascender/descender — +40% with Amiri). `CS.draw_ink()` draws so the ink edge sits on a given coordinate and
returns the ink bottom, so the next line starts exactly there.
Result: two lines can never collide, and text can never be buried under the badge (both happened in earlier passes).

## 168px thumb test

Both variants pass: **H1 legible, H2 shape understandable**. The badge is borderline — by design.
The system only guarantees H1 + H2 survive at phone size; everything else is texture.
