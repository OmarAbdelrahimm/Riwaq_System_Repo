# RUWAQ: Offline Rendering & Remotion Production Pipeline

This document details how to run deterministic headless rendering of the **Bab Zuwayla Historical Geography Visualization** without any active internet connection or live API dependencies.

---

## 1. Zero Live Network Dependencies Architecture

The application has been engineered to run 100% offline:
1. **Embedded Vector GIS Geometry**:
   - `cairo_historical_geography.geojson` embeds all physical and reconstructed spatial geometries:
     - Nile river hydrography & islands
     - Modern Cairo arterial network
     - UNESCO Historic Cairo boundary (Ref 89)
     - Al-Mu'izz Grand Ceremonial Axis (OSM Way 24905187)
     - In-situ northern stone gates (Bab al-Futuh & Bab al-Nasr) and northern curtain wall
     - Bab Zuwayla southern gate anchor (OSM Node 293370334)
     - Approximate Fatimid Cairo enclosure (1092 CE) with ±50m uncertainty corridor
2. **Local Vector Styling**:
   - `ruwaq_maplibre_style.json` specifies client-side WebGL rendering with no external font or tile service dependencies.
3. **Deterministic Frame Interpolation**:
   - `storyChoreography.ts` computes the exact camera coordinates `[lng, lat]`, `zoom`, `pitch`, `bearing`, and layer opacities for every integer frame (0 to 600 at 30 fps).

---

## 2. Headless CLI Rendering with Remotion

### A. Prerequisites
- Node.js 18+ or 20+
- Chrome or Chromium installed for Puppeteer
- FFMPEG installed

### B. Render Master Documentary Composition (4K ProRes / MP4)
To render the 20-second (600 frames at 30fps) historical map sequence:

```bash
# Render to H.264 MP4 (Broadcast Master)
npx remotion render RuwaqHistoricalMap out/ruwaq_cairo_geography_master.mp4 \
  --gl=angle \
  --concurrency=4 \
  --width=3840 \
  --height=2160

# Render to Apple ProRes 422 HQ (Archival Master)
npx remotion render RuwaqHistoricalMap out/ruwaq_cairo_geography_prores.mov \
  --codec=prores \
  --prores-profile=hq \
  --gl=angle
```

### C. Render Frame Sequence for Post-Production (DaVinci Resolve / After Effects)
```bash
npx remotion render RuwaqHistoricalMap out/frames/frame_%04d.png \
  --sequence \
  --image-format=png \
  --gl=angle
```

---

## 3. The 7-Act Documentary Storyboard Progression

| Act | Frames | Time | Geographical Focus | Cartographic Elements |
|---|---|---|---|---|
| **Act 1** | 0 – 80 | 0.0s – 2.6s | Modern Cairo & Nile Valley | Nile river, Gezira/Roda islands, arterial bridges |
| **Act 2** | 81 – 160 | 2.7s – 5.3s | Historic Cairo Zone | UNESCO Ref 89 boundary (1979) in antique parchment wash |
| **Act 3** | 161 – 240 | 5.4s – 8.0s | Approximate Fatimid Enclosure | 1092 CE Badr al-Jamali perimeter with ±50m uncertainty buffer |
| **Act 4** | 241 – 320 | 8.0s – 10.6s | Al-Mu‘izz Grand Axis | Animated gold spine drawing from north to south (1.2 km) |
| **Act 5** | 321 – 400 | 10.7s – 13.3s | Documented Northern Gates | Bab al-Futuh & Bab al-Nasr standing stone bastions (1087 CE) |
| **Act 6** | 401 – 480 | 13.4s – 16.0s | Bab Zuwayla at Southern Frontier | Southern gate portal, Suq al-Khiyamiyya exit toward Fustat |
| **Act 7** | 481 – 600 | 16.0s – 20.0s | 3D Architectural Plunge | Camera pitches down 62°, dissolving into 3D gateway model |

---

## 4. Researcher GeoJSON Modification Workflow

To test alternative scholarly hypotheses without recompiling:
1. Open the applet UI and click **Researcher GeoJSON ⚙** in the top bar.
2. Select between:
   - **K.A.C. Creswell (1952 Consensus)**
   - **AKTC (2004 In-situ Findings)**
   - **Al-Maqrizi Historic Chronicle (Khitat)**
3. Alternatively, paste or drag-and-drop any verified `.geojson` polygon into the editor and click **Validate & Apply to Map**.
4. Click **Download GeoJSON** to export the updated research boundary.

---

## 5. Offline Linux / Docker CI Rendering Setup

When running in headless container environments without an X11 server:
```bash
# Run with virtual framebuffer
xvfb-run -s "-screen 0 3840x2160x24" npx remotion render RuwaqHistoricalMap out/ruwaq_cairo_geography.mp4 \
  --gl=angle \
  --chromium-options="--no-sandbox,--disable-setuid-sandbox"
```
