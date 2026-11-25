# RUWAQ — BAB ZUWAYLA: REMOTION PRODUCTION INTEGRATION GUIDE

## 1. Overview & Handoff Objectives

This package delivers the production-ready 3D architectural asset of **Bab Zuwayla (Cairo, Egypt)** configured specifically for the **RUWAQ** historical documentary series.

The asset is engineered for deterministic, frame-driven rendering in [Remotion](https://remotion.dev) with `@remotion/three` and React Three Fiber, guaranteeing 100% reproducible frames without real-time clock drift or out-of-order frame rendering glitches.

---

## 2. Deliverables Manifest

| File | Path / URL | Purpose |
| :--- | :--- | :--- |
| **Master Architectural 3D Model** | `public/RUWAQ_BAB_ZUWAYLA_MASTER.glb` | Complete binary GLB with all named components (Towers, Portals, Minarets, Doors) |
| **Validation Report** | `public/GLB_VALIDATION_REPORT.json` | Automated Three.js audit verifying all 21+ named objects and parent-child transforms |
| **Complete Source Code Archive** | `public/RUWAQ_BAB_ZUWAYLA_3D_SOURCE.zip` | Complete working source code, geometries, shaders, materials, and documentation |
| **10-Second 30fps Video Test** | `public/RUWAQ_ARCHITECTURAL_300_FRAMES.mp4` | 1920×1080 30fps H.264 video rendered directly with Remotion |
| **8 Architectural State Previews** | `public/RUWAQ_8_STATES_PREVIEW/` | High-resolution 1920×1080 still frames of all eight canonical viewing states |
| **Direct Remotion Component** | `src/BabZuwaylaRemotion.tsx` | Production Remotion React component using `@remotion/three` |
| **Historical Limitations Document** | `GEOMETRY_LIMITATIONS_AND_SOURCES.md` | Verification of historical accuracy and educational reconstruction boundaries |

---

## 3. The 6-Act Remotion Choreography Sequence (300 Frames @ 30fps = 10.00s)

All continuous camera movement and component transitions are derived from a single normalized progress curve `progress = frame / durationInFrames`:

1. **Frames 0–45 (Act 1: Top Orthographic Plan)**:
   - Orthographic top-down camera (`zoom: 18`)
   - Highlights bilateral symmetry of the Fatimid semicircular bastions, defensive passage depth, and Cairo entry vector (`إلى داخل القاهرة`).
   - Mamluk minarets are strictly hidden (1092 CE state).

2. **Frames 45–90 (Act 2: Transition to Side Elevation)**:
   - Smooth continuous camera rotation from top plan to lateral side elevation.
   - Reveals the bastion projection and defensive wall thickness.

3. **Frames 90–135 (Act 3: Front Elevation - Original 1092 CE Fatimid Gate)**:
   - Front orthographic elevation (`zoom: 14`).
   - Showcases the joggled cushion voussoirs, arched machicolation bridge, and stepped battlements.
   - Absolutely no Mamluk minarets in this state.

4. **Frames 135–190 (Act 4: Mamluk Minaret Additions, 1415–1421 CE)**:
   - Smooth transition into perspective camera.
   - Twin Mamluk minarets of Sultan al-Mu'ayyad Shaykh descend smoothly and mount directly atop the solid tower terrace platforms.

5. **Frames 190–245 (Act 5: Controlled Multi-Axis Exploded View)**:
   - Bastion towers move outward laterally along X (`±5.5m`).
   - Central entrance arch projects forward along Z (`+3.5m`).
   - Heavy iron-studded door leaves swing open on their hinge pivots.
   - Minarets elevate vertically and decouple into their 6 major tiers along Y.

6. **Frames 245–300 (Act 6: Full Reassembly & 3/4 Perspective View)**:
   - Controlled physical reassembly into the iconic documentary three-quarter perspective angle.
   - Heroic warm golden hour lighting matching Cairo Mokattam limestone patina.

---

## 4. How to Use `BabZuwaylaRemotion.tsx` in an Existing Remotion Project

### Step 1: Install Required Peer Dependencies
```bash
npm install three @types/three remotion @remotion/three @react-three/fiber
```

### Step 2: Register Composition in your `Root.tsx`
```tsx
import React from 'react';
import { Composition } from 'remotion';
import { BabZuwaylaRemotion } from './BabZuwaylaRemotion';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="RuwaqBabZuwayla"
      component={BabZuwaylaRemotion}
      durationInFrames={300}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{
        showAnnotations: false,
      }}
    />
  );
};
```

### Step 3: Integrate into your Main Documentary Timeline (`Sequence`)
```tsx
import { Sequence } from 'remotion';
import { BabZuwaylaRemotion } from './BabZuwaylaRemotion';

export const DocumentaryMaster = () => {
  return (
    <>
      {/* Intro narration: 0 to 450 frames */}
      <Sequence from={0} durationInFrames={450}>
        <IntroNarration />
      </Sequence>

      {/* 3D Architectural Deep Dive: 450 to 750 frames (10 seconds) */}
      <Sequence from={450} durationInFrames={300}>
        <BabZuwaylaRemotion width={1920} height={1080} />
      </Sequence>
    </>
  );
};
```

### Step 4: Render to Video via CLI
```bash
npx remotion render src/remotion-index.ts RuwaqBabZuwayla output/bab_zuwayla.mp4 --concurrency=2
```

---

## 5. Visual Identity & Editorial Standards
- **Background Color**: `#F3EBDB` (RUWAQ Cream / Parchment)
- **Primary Ink**: `#1C1B19` (Dark Carbon Ink)
- **Editorial Gold**: `#A98A4B` (Mamluk Gold Leaf)
- **Rust / Ochre Accent**: `#8C4729` (Terracotta / Cairo Sunstone)
- **Typography**: Cinzel, Amiri, IBM Plex Mono
- **Zero UI in Film Renders**: Renders exclude all interactive buttons, docks, and browser HUDs, displaying only clean documentary lower-thirds.
