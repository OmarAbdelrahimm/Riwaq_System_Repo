# Ruwaq production — how to make a new episode / scene

## 1. Start from the demo, not from zero

Copy `src/compositions/RuwaqMotionDemo.tsx` to a new file in
`src/compositions/`, rename the component, register it in
`src/RemotionRoot.tsx` with its own `id`, duration and size. Never edit
`RuwaqBabZuwayla` or `RuwaqHistoricalMap` in place for a new episode.

## 2. Pick the palette first

- Default: **A Petrol Teal** (`colors` in `src/brand/tokens.ts`).
- Military / night episode: **C Ink Navy + Amber** as the background,
  with A as the secondary. One background per frame, one accent.
- Never use V1 gold/charcoal for new work. Never invent a new hex —
  if a colour is not in `tokens.ts`, add it to `BRAND.md` first.

## 3. Sync to the music (BPM), don't prompt a vibe

1. Choose a real, licensed track. Put it in `public/audio/` (see
   `src/audio/README.md` — no unlicensed music in the repo).
2. Read its BPM. Register it in `src/audio/beatgrid.ts`.
3. Put the hero title on an exact beat: `beatToFrame(bpm, 8, fps)`.
   At 128 BPM beat #8 = frame 98. At 72 BPM beat #4 = frame 75.
4. Add SFX cues in `src/audio/sfx.ts` — one cue per frame, named.

## 4. Motion rules

- Hero title / arch / anything that must feel alive: **spring**
  (`springs.hero` / `springs.monumental` in `src/motion/presets.ts`).
- Opacity fades and progress bars: `interpolate` (linear) is fine.
- Hand-drawn frame: `roughPaths()` / `roughArchPath()` — fixed seed,
  never `Math.random()`.
- Watercolour: `<WatercolorWash>` — fixed seed. Do not run p5.brush
  live inside a composition (see `src/motion/watercolor.tsx`).
- Physics: `simulatePhysics()` — fresh engine per frame, fixed steps.
  Never keep a Matter engine in React state.

## 5. Add a reference motion (the Agent workflow from the video)

1. Find a reference motion video. Write down ONLY its timing + structure:
   e.g. "hero 0.00–1.88s, spring, 2-column grid".
2. Rebuild that timing in a new composition with Ruwaq colours, shapes
   and type. Same timing, your skin = 100% original.
3. Put the timing in `src/motion/presets.ts` (named slot), not hardcoded
   in one scene, so the next episode reuses it.

## 6. Gates — how to run them WITHOUT breaking the render

The repo's old pain ("gates break the render") came from validation
running inside the render path. Rules now:

- **Never** call validation / network / MapLibre tile loading inside a
  composition's render. Compositions must be pure functions of `frame`.
- Gates live in `scripts/` and in `npm run smoke` — they run BEFORE the
  render, not during it:
  `npm run smoke` = typecheck + vite build + demo render (30f) +
  Bab Zuwayla render (30f) + historical-map stills at frames 15, 200, 440.
- The historical map (`RuwaqHistoricalMap`) IS smoke-tested: its Remotion
  path is deterministic SVG, not MapLibre — MapLibre lives only in the
  web viewer (`src/geo/RuwaqMaplibreView.tsx`), never in the render.
  The stills must show map features, not bare parchment. A near-empty
  still means the projection scale regressed: `projectCoord` in
  `src/geo/RuwaqGeoRemotion.tsx` must be `2^zoom * 256 / 360` px/deg
  (Web-Mercator). The old factor `* 35` was ~49x too large and made the
  Nile fall off-screen and the Fatimid enclosure render ~12,000 px wide
  (fixed 23 Nov 2026).
- A gate that fails must fail the script with a non-zero exit and a
  named file — never silently skip, never `continueRender` past it.
