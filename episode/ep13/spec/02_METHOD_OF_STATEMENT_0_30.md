# METHODS OF STATEMENT — RUWAQ EP13 / opening 0–30s

**Authority:** Original S01 audio, not script or ASR, determines cuts and word timing. Times below are GUIDES from earlier editorial cut, NOT verified word alignments. Confirm with the actual S01 first. Do not fake audio. Scene naming S01–S10 and 30fps frame ranges in `config/scenes_0_30.json`.

## Overarching progression
**Question (0–3)** → **memory of warning (3–9)** → **popular certainty (9–14)** → **where is the source? (14–18)** → **test implied causal link (18–22)** → **real medical evidence (22–30)**. Audio does not change; objects move to narrate ideas.

### Shot 01 — 00.00–01.80 [HOOK, ~54f]
- **Voice anchor**: «إوعى تشرب لبن بعد السمك» (verify exact split).
- **Create assets**: a true independent fish hero plate and transparent glass of milk; background and lights separate; original still `assets/A06_CONCEPT_FISH_MILK_REFERENCE_ONLY.png` is a COLOR/TONE reference, NOT geometry or finished footage.
- **Layout**: fish plate camera-left (x≈550,y≈650), glass right (x≈1380,y≈575). Center gap holds causal question. Camera is low ¾ oblique, visual stage occupies bottom ~65%, text upper center/right.
- **Motion instruction**: first 6 frames start slightly occluded by an out-of-focus foreground rim/light arc; 6–20f fish glides 70px into its locked position with true independent cast shadow; 12–32f glass glides 95px on a separate depth plane with a delayed spring; reveal actual glass rim reflections on its side; a small arc traces the gap 26–48f.
- **Camera**: subtle x push 0→25px and scale 1→1.035 ONLY after objects establish; no fish hidden by 3.3× milk crop.
- **Type**: one short Arabic warning quote, shown only if identical to original audio. Use `Amiri` or `IBM Plex Sans Arabic` (depending on approved hierarchy), no text baked into art.
- **Pass**: when camera is frozen, fish/glass still exhibit independent believable motion. If only flattened art is available, stop and request layer extraction or geometry before labeling 3D.

### Shot 02 — 01.80–03.04 [MYTH CLAIM, ~37f]
- **Voice anchor**: «هيجيلك بهاق» = *an alleged quote*, not factual disease explanation.
- **Visual**: segmented golden question-mark signal draws between the two objects. Glow build on question then disintegrates into 3–4 points, not a reaction between foods.
- **Motion**: tracked bezier/3D tube spline animates via trim; claim card with gold keyline slides 90px + opacity, 4 frame settle, holds; do not imply disease develops because food is consumed.
- **Transition**: question bubble becomes the first repeat-quote card.

### Shot 03 — 03.04–05.42 [FAMILIAR PHRASE, ~72f]
- **Voice**: «الجملة دي غالبًا سمعتها قبل كده».
- **Visual**: first warning card detaches and travels on Z axis, 2 more similar anonymous cards echo behind it; warm lantern bokeh remains behind text.
- **Motion**: 3 cards appear serially, scale 0.84→1 and z -120→0, capped opacity with clean damping; use varying size and perspective, not three duplicate paper sheets.
- **No identity drift**: anonymous text cards rather than 3 new generated humans.

### Shot 04 — 05.42–09.00 [ON THE TABLE, ~107f]
- **Voice**: «ويمكن تكون اتقالت لك وإنت لسه قاعد على سفرة» (actual audio controls).
- **Visual**: elegant warm Egyptian dining room as an emotional cutaway, NOT a talking head. Reuse approved warm illustrated A01 as B-roll for 1.5–2.5 s maximum, then transition into dark 3D network card.
- **Motion**: doorway/parallax > table at separate rates only if technically separated; if not, use motivated wipes/light to avoid false geometry claims. One highlighted memory quote travels to the next shot.

### Shot 05 — 09.00–12.10 [CONFIDENT REPEAT, ~93f]
- **Voice**: *UNVERIFIED after 9.0; listen and mark exact Arabic*.
- **Visual**: 3 ghosted cards arrive, enlarge certainty word with brief emphatic light; a thin dotted trail connects cards.
- **Motion**: real card positions/rotation/z change, 2-stage diagonal camera move. No real named people, no fake citations.

### Shot 06 — 12.10–14.00 [PAUSE + DOUBT, ~57f]
- **Voice**: *UNVERIFIED*.
- **Visual**: network movement settles and reverses slightly into single suspended question dot. Freeze previous noisy UI for 4–6f then clear it.
- **Motion**: soft trails exit via correct masks, wipe from a real card edge; avoid empty screen for the entire shot.

### Shot 07 — 14.00–17.50 [WHO SAID IT?, ~105f]
- **Voice**: «مين قال أصلًا؟» *verify wording*.
- **Visual**: attribution network with dotted paths that end at unknown nodes (?), not fictional ancient documents or a purported origin story.
- **Motion**: search ring moves through 3 cards, no match returns. The '?' remains without pretending to prove a particular historical origin.

### Shot 08 — 17.50–22.10 [CAUSALITY, ~138f]
- **Voice**: wording must be checked; prior render visually asked whether fish and milk cause vitiligo.
- **Visual**: hero fish/glass return, now with suspended dotted proposed-causality route. A clean magnifier/schematic selector traces the food objects; alleged arrow breaks into a question mark. This expresses insufficient evidence, not a definitive chemical impossibility.
- **Motion**: focus shifts among fish, glass and center track; actual object movement OR layered light rotation on real silhouettes. Restrict label to 1 primary phrase.

### Shot 09 — 22.10–26.60 [SOURCE CARD 1, ~135f]
- **Voice**: «مفيش دليل علمي موثوق» or nearest exact original statement, must verify.
- **Visual**: factual RUWAQ-designed translucent evidence card. Text from verified Saudi MOH source, proper attribution and canonical link in notes; card is NOT a screenshot or fake official UI.
- **Motion**: card originates from middle distance, comes front, a bold *summary sentence* appears along real VO; one source pill becomes legible, with enough dwell time.
- **Danger**: no fake '100% safe' blanket claim. This is about vitiligo, not all possible food reactions.

### Shot 10 — 26.60–30.00 [SOURCE CARD 2 / TISSUE REVEAL, ~102f]
- **Voice**: VERIFY; don't auto-subtitle without actual listen.
- **Visual**: second small source card from NIAMS and warm backlit transition into a *clearly labeled simplified skin model*; label explicitly that illustration is explanatory not a microscope photograph.
- **Motion**: camera passes through the evidence card outline into skin section, 2.5D if medically credible static illustration exists; a medically accurate 3D model requires separate expert-checked geometry.
- **End**: open cut into 30–60. NO outro logo.

## Production methods, not just prompts
A. **Gather** authoritatively sourced audio and official brand → `config/asset_contract.json` statuses; create missing assets with separate fore/mid/back layers or explicit geometry; reject AI text inside image.
B. **Previsualize** storyframes before final asset creation; use black-and-white boxes for composition geometry only, never deliver box art as final.
C. **Animate** objects and data: for each scene define `entry`, `interaction`, `reveal`, `hold`, `exit`, `camera` keyframes. Actual local motion must remain when global camera animation is disabled.
D. **Integrate** typography as Remotion text layers, data cards from trustworthy copy, sound effects only on visually motivated actions, low music under intelligible narration.
E. **Test** contact sheets on frames for first appearance, peak, exit and shot boundaries; run mobile legibility check; no blank/dark drift or off-canvas crops.
F. **Compare** against reference **style grammar** at timestamp archetypes: opening product hero, floating context cards, mystery ring, dashboard reveal; never compare Luminovo logos/actual copy.
G. **Freeze** approved assets. Do not regen them because one unrelated part fails.

## Two editorial traps to avoid
- The separate 2026 editorial script includes a longer 13-topic episode and isn't necessarily the same wording as current S01. Never overwrite the S01 approved recorded take to make the storyboard easier.
- 'Fish + milk cause vitiligo' is the myth being challenged, not an established causal effect. Audio text and on-screen design must preserve this distinction.
