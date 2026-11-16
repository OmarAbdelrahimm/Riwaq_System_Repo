# Architecture — real editable motion, not camera-over-PNG

## Recommended stack
- React + TypeScript + the **existing** Remotion version; install dependencies from its lockfile (no re-scaffolding of whole project).
- `@remotion/three`, `three`, `@react-three/fiber` for limited 3D objects if environment can render WebGL ANGLE reliably; see https://www.remotion.dev/docs/three . Test rendering one 15-frame scene first. If WebGL/VRAM unavailable, **pre-render 3D passes from an external 3D tool that is already authorized/installed** OR build legitimate 2.5D layer parallax (do not claim 3D rotation).
- Remotion deterministic frame animations via `useCurrentFrame`, `interpolate`, `spring`; no browser timers, `Math.random`, external live fetch or CSS animation time in render.
- Frame-based SVG paths and masks for trim trajectories, data card connectors, shapes, kinetic typography.
- Font loaded before render: Amiri title, IBM Plex Sans Arabic body if found from RUWAQ brand asset set. Verify RTL shaping and punctuation with rendered screenshots.
- Only original gold vector RUWAQ logo, provided as `01-BRAND/logo.svg` from approved brand project.

## Filesystem within Codex repository
```
project/
  AGENTS.md                     # copied from handoff
  src/episode13/Root.tsx
  src/episode13/scenes/S01_Hero.tsx ... S10_TissueReveal.tsx
  src/episode13/components/GlassPanel.tsx, SourceCard.tsx, KineticArabic.tsx
  src/episode13/components/CameraRig.tsx, FoodStage.tsx, ArcConnector.tsx
  src/episode13/data/timeline.ts
  src/episode13/style/tokens.ts
  public/ep13/assets/{approved,generated,wip}
  public/ep13/audio/chapter01.mp3
  public/ep13/brand/logo.svg
  out/ep13/STYLEFRAME_A.png, STYLEFRAME_B.png, PROOF_0_6_v1.mp4
  docs/STATUS.md, QC.md, LICENSES.md
```
Never overwrite older episode sources. Use exact versioned output names and Git commits.

## Motion component contract
Each scene gets these parameters:
```
scene = {
 id, startFrame, endFrameExclusive, voiceCue, sourceAudioFile,
 assets: [{path, role, zIndex, license, hash}],
 entries: [{target, property, from, to, frames, easing}],
 contentAction: {whatActuallyChangesInScene},
 camera: {x,y,z,fov|scale,lookAt},
 textEvents: [{copy, firstFrame, lastFrame, importance}],
 transition: {outAction, destination},
 qa: {expectedAtFrames, knownRisk}
}
```
**Rule**: global timeline frames are absolute, while `Sequence` may use local frames; never mix them silently. Use a pure `absoluteFrame` helper or pass offset explicitly to protect synchronized transformations.

## Rendering and performance
- Start with `npx tsc --noEmit`, unit smoke tests and 15-frame still renders.
- Review sample 0–6s at 960×540 / 30fps; after style approval render chosen shots at 1080p. Never use full 30s to test one new motion.
- Use one browser/renderer worker under tight RAM; Cap 3D geometry complexity, texture resolution and cards. Prefer cached passes and static pre-baked grain/DOF.
- Prebake diffuse glow backgrounds into images, not a full frame runtime `filter: blur(...)` which caused prior stalls. Do not composite costly CSS drop-shadow per frame.
- Verify video `ffprobe` duration/resolution/fps/audio, `ffmpeg -v error -i ... -f null -`, still/transition review; no QC success without viewing frames.
- Export clean final MP4 with source assets separately. Keep overlays editable.

## Why Codex not only Work
Codex can inspect & change the project repo, implement deterministic components, run tests and save commits. Work is more suitable for research/licensing and asset orchestration, and can execute longer multi-step processes, but it isn't inherently a professional motion designer. Neither guarantees premium 3D assets. No split repo ownership; Work returns assets to shared folder and Codex handles implementation.
