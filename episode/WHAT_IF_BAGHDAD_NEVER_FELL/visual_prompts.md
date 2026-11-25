# Visual prompts — WHAT_IF_BAGHDAD_NEVER_FELL

Every AI-generated image gets the on-screen label **«إعادة تصوّر · ذكاء اصطناعي»** (shown by VisualLayer whenever `kind: "ai"`).

Rules applied to every image:
- no living persons and no identifiable faces (silhouettes and figures seen from behind only)
- no gore
- no text, lettering or logos
- 16:9

Shared style suffix: *cinematic painterly historical illustration, muted palette of ink black, parchment cream, antique gold (+ deep burgundy where noted), subtle film grain, no text, no lettering, no logos, 16:9 widescreen composition*. These values are the colors from style_brief.json.

| File | Prompt (main part) |
|---|---|
| img01_gate_night.jpg | Massive arched wooden city gate of medieval Baghdad (13th c.) slowly opening at night, warm torchlight spilling through the gap, mist rising from the Tigris, geometric brickwork, no people close up |
| img02_baghdad_dusk.jpg | High aerial establishing view of medieval Baghdad on the Tigris at dusk, brick domes, minarets, palm groves, boats, city walls, warm golden last light |
| img03_library_candle.jpg | Interior of a medieval Islamic library in Baghdad, tall shelves of manuscripts, a single oil lamp on a reading table with an open illuminated manuscript, chiaroscuro, no people |
| img04_mongol_cavalry.jpg | Long ranks of 13th-century Mongol horse archers as silhouettes across a dusty plain at golden hour, banners, dust clouds, distant and anonymous, no gore |
| img05_alamut.jpg | Medieval stone fortress on a sheer rocky peak in northern Iran wrapped in fog, cold dawn light with faint gold rim, no people |
| img06_throne_empty.jpg | Empty carved caliph's throne in a vast dark Abbasid hall, candles and oil lamps, arches and tile patterns, burgundy fabric, no people |
| img07_sealed_letter.jpg | Folded medieval letter with a broken dark-red wax seal, inkwell and reed pen, candlelight, writing blurred and illegible |
| img08_council_shadows.jpg | Abbasid council hall at night, two groups of robed men facing each other as dark silhouettes, faces not visible, hanging lamps |
| img09_flood_camp.jpg | Medieval army camp flooded at dawn on a flat Mesopotamian plain, tents half-submerged, distant wading silhouettes, mist, no gore |
| img10_river_night.jpg | The Tigris at night in 1258, small boats as silhouettes, distant orange glow of fire reflected on the water, pontoon bridge in mist, no gore |

## Planned but not generated (platform limit of 10 images per turn)

- smoke over walls (sc.12)
- morning market (sc.15)
- madrasa class (sc.17)
- banner shadow on throne (sc.17)
- Cairo citadel (sc.20)
- frozen river (sc.22)
- observatory (sc.11)
- Tigris at dawn (sc.26)

These were replaced by re-using the images above with a different crop, Ken Burns move or tint (dark / cold / burgundy), or by graphic components (MapSchematic, SplitScreen). They can be generated in a later turn and swapped in through `tools/build_meta.py` alone; no component code needs to change.
