# STYLE BLOCK — RUWAQ | 1816
Fixed text, pasted into **every** generation prompt, unchanged. This is the only
consistency lever the image tool gives us: it has no seed, no reference image and
no version pinning, so the prompt is the whole contract.

## 1. The block (English, appended verbatim after the scene description)

```
STYLE: 1816 documentary-reconstruction still. 19th-century New England and
Lake Geneva. Muted ten-colour palette: bone white, cold ash grey, wet slate,
deep pine black, raw umber, oxidised copper, dried-blood maroon, pale straw,
storm blue, single candle amber. Overcast natural light only; one warm accent
(candle or window) allowed per frame. Fine film grain, soft halation on the
highlight, lifted blacks, no pure white and no pure black. 35 mm anamorphic
character, deep focus, horizon slightly below centre. Real materials: wet wool,
raw wood, rusted iron, slate, ash, condensation on glass. No text, no lettering,
no numbers, no logos, no borders, no frame lines, no watermarks. No faces: figures
appear only as silhouettes, from behind, cropped at the shoulder, or as hands.
Nothing in the frame is a photograph, a document, or an archival image.
Composition leaves the upper third calm for the title layer.
```

Negative block, appended after it:

```
AVOID: modern objects, electric light, plastic, cars, power lines, saturated
colour, teal-and-orange grade, HDR look, lens flare, bokeh balls, cinematic bars,
text of any kind, signatures, faces turned to camera, cartoon, illustration,
3D render look, oversharpened edges.
```

## 2. Why these clauses

| Clause | What it prevents, measured |
|---|---|
| ten-colour palette | the tool drifts warm/saturated between calls; the LUT then has less to correct |
| one warm accent per frame | without it the tool adds several light sources and the frame stops reading as candle-lit 1816 |
| no faces | keeps the film's rule and avoids the uncanny face the tool produces at 1376 px |
| "no text, no lettering" | the tool invents signage; v2.1 QA counts on-screen text as its own layer |
| calm upper third | the title layer needs a quiet zone; otherwise every title fights the plate |
| grain + halation | the plate must survive a 2× upscale; smooth output looks plastic at 2560 |

## 3. What the block cannot fix

- **No seed.** Two calls with identical text still differ. The style block narrows
  the distribution; it does not pin it. The similarity gate in §4 catches the drift.
- **No reference image.** The tool cannot be shown LOOK01 and asked to match it.
- **Native 1376×768 (1.79:1).** Every plate is upscaled 2× and cropped to 2560×1440.

## 4. Similarity gate (run per chapter, after the plates exist)

`simcheck.py` computes, for every plate:
- a 192-bin RGB histogram fingerprint,
- a 16×16 luma grid (standardised).

It flags:
- **repeat** — two plates in the same chapter whose histogram cosine ≥ 0.92 *and*
  luma-grid correlation ≥ 0.90. These are the same photograph twice; regenerate one.
- **outlier** — a plate whose histogram cosine to the chapter centroid is < 0.60.
  These are the plates that will look like they came from another film.

Measured on the three approved LOOK plates as a baseline: no repeats, no outliers,
mean pairwise histogram cosine **0.532**. That is the range the chapters should sit in.

## 5. One unified grade (FFmpeg, applied to every plate)

A single 3D LUT (`.cube`, 33³) is baked once from the palette and applied to every
plate so that the AI drift is pulled back to one look:

```
ffmpeg -i plate.png -vf "lut3d=ruwaq_1816.cube:interp=tetrahedral,format=yuv444p" plate_graded.png
```

The LUT is built only from measured statistics of the approved plates (channel
medians, black lift, highlight roll-off), never from taste. It is applied *after*
the upscale and *before* the grain, so grain is not re-quantised.
