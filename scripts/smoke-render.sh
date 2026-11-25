#!/usr/bin/env bash
# Ruwaq smoke gates — run BEFORE any render, never inside a render.
# Fails fast (set -e) with a named step. The historical map IS included
# (gate 5): its Remotion path is deterministic offline SVG — MapLibre
# lives only in the web viewer, not in the render path.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== gate 1: typecheck =="
npx tsc --noEmit
echo "== gate 2: vite build =="
npm run build
echo "== gate 3: demo render (30 frames) =="
npx remotion render src/remotion-index.ts RuwaqMotionDemo /tmp/ruwaq-smoke-demo.mp4 --frames=0-29
echo "== gate 4: Bab Zuwayla render (30 frames) =="
npx remotion render src/remotion-index.ts RuwaqBabZuwayla /tmp/ruwaq-smoke-babzuwayla.mp4 --frames=0-29
echo "== gate 5: historical map stills (one per act group) =="
# The map is deterministic SVG in the render path (MapLibre lives only in
# the web viewer, not in Remotion), so it CAN be smoke-tested offline.
# These stills must show map features, not bare parchment — if they come
# back near-empty, the projection scale regressed (see RuwaqGeoRemotion
# projectCoord: 2^zoom * 256/360 px/deg, never *35).
npx remotion still src/remotion-index.ts RuwaqHistoricalMap /tmp/ruwaq-smoke-map-f015.png --frame=15
npx remotion still src/remotion-index.ts RuwaqHistoricalMap /tmp/ruwaq-smoke-map-f200.png --frame=200
npx remotion still src/remotion-index.ts RuwaqHistoricalMap /tmp/ruwaq-smoke-map-f440.png --frame=440
echo "SMOKE OK"
