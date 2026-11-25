# RUWAQ — Bab Zuwayla 3D + Motion System

Remotion + React Three Fiber reconstruction of Bab Zuwayla, Cairo
(1092 CE Fatimid + 1415–1421 Mamluk minarets), plus the Ruwaq motion system
(brand, springs, hand-drawn / watercolour / physics, BPM-synced audio).

## Quick start

```bash
npm install          # clean install now works (esbuild conflict fixed, see below)
npm run dev          # Vite web app (interactive 3D viewer + map)
npm run build        # Vite production build
npm run typecheck    # tsc --noEmit
npm run compositions # list Remotion compositions
npm run render:demo  # render the 10s motion-system demo (1920x1080)
npm run smoke        # build + typecheck + short renders (gates, safe)
```

## Compositions (`src/remotion-index.ts`)

| ID | What | Size / length |
|---|---|---|
| `RuwaqMotionDemo` | Motion-system demo (spring title on beat 8, Rough.js arch, watercolour, Matter.js chips) | 1920×1080, 300f, 10s |
| `RuwaqMotionDemoShorts` | Same demo, vertical | 1080×1920, 270f, 9s |
| `RuwaqBabZuwayla` | 3D reconstruction, 6 chapters | 1920×1080, 300f, 10s |
| `RuwaqHistoricalMap` | Cairo historical geography (MapLibre) | 1920×1080, 600f, 20s |

## Structure

```
src/
  brand/tokens.ts        # colours/fonts — mirrors BRAND.md (A primary, C secondary)
  motion/presets.ts      # spring configs only for hero motion
  motion/rough.ts        # Rough.js hand-drawn paths (fixed seed, deterministic)
  motion/watercolor.tsx  # watercolour wash (SVG turbulence, fixed seed)
  motion/physics.ts      # Matter.js deterministic physics stepper
  audio/beatgrid.ts      # BPM -> frame map (title on beat #8 @128 BPM = frame 98)
  audio/sfx.ts           # SFX cues on frames (placeholders, no files bundled)
  compositions/RuwaqMotionDemo.tsx
  BabZuwaylaRemotion.tsx # canonical 3D composition (523 lines)
  geo/                   # Cairo historical geography (MapLibre/GeoJSON)
  three/                 # procedural Bab Zuwayla geometry
  components/            # web viewer UI
public/
  RUWAQ_BAB_ZUWAYLA_MASTER.glb   # master model (728 KB, 300 nodes, validated)
  cairo_historical_geography.geojson
  provenance_manifest.json
docs/
  PRODUCTION.md          # how to make a new episode/scene
  legacy/                # root re-export + V04 files, moved not deleted
BRAND.md                 # single source of truth for brand
```

## What was fixed (2026-11-23, branch `ruwaq/repo-fix-motion-system`)

- `npm install` failed with ERESOLVE (vite 8.3.8 needs esbuild
  ^0.27/0.28, repo pinned ^0.25.0) — fixed by pinning esbuild ^0.28.0.
  Clean `npm ci` now works.
- Package was `react-example` 0.0.0 — now `ruwaq-3d-shape` 0.1.0.
- No README, no `remotion.config.ts`, no render scripts — all added.
- Wrong import in `src/components/RemotionModal.tsx`
  (`./three/BabZuwaylaScene` → `../three/BabZuwaylaScene`).
- Duplicate GLB removed (`RUWAQ_BAB_ZUWAYLA_V04_MASTER.glb` was a
  byte-identical copy of the master, md5 aff350ff). Master preserved.
- Root 5-state PNGs were byte-identical to `public/` copies — moved to
  `docs/legacy/`, public copies kept.
- Three competing `BabZuwaylaRemotion` files (root, `src/`, V04) — root
  re-export + V04 moved to `docs/legacy/`; `src/BabZuwaylaRemotion.tsx`
  is the single canonical file.

## Known limits (honest)

- `RuwaqHistoricalMap` uses MapLibre GL (live map tiles / WebGL). It
  registers as a composition, but a headless render depends on network
  tiles — see `docs/PRODUCTION.md` "gates" section. The smoke script
  renders the demo + Bab Zuwayla, not the map, for this reason.
- `test.mp4` (29 KB) and `RUWAQ_ARCHITECTURAL_300_FRAMES.mp4` (80 KB) at
  the repo root / in `public/` are suspiciously small for 300 frames —
  kept, not trusted as deliverables.
- `scripts/export_and_validate_glb.ts` needs a browser `FileReader`
  polyfill and is not wired into any npm script — it is a manual tool.
- No tests yet beyond the smoke render. No CI had existed — added
  `.github/workflows/ci.yml` (install + typecheck + build + smoke).
