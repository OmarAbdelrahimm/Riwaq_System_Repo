# Legacy files — moved here on 2026-11-23, not deleted

- `BabZuwaylaRemotion.root-reexport.tsx` — was the repo-root
  `BabZuwaylaRemotion.tsx`, a 6-line re-export of
  `src/BabZuwaylaRemotion.tsx`. Moved so the root stays clean; nothing
  imported the root file (RemotionRoot imports from `src/`).
- `BabZuwaylaRemotion_V04.tsx` — was the repo-root V04 variant (7 lines,
  re-export of the V04 component). The V04 geometry itself lives in
  `src/three/geometry/` and in the validated master GLB.
- `RUWAQ_BAB_ZUWAYLA_V04_5_STATES/` — the 5 state preview PNGs. They are
  byte-identical to the copies in `public/RUWAQ_BAB_ZUWAYLA_V04_5_STATES/`
  (md5-verified), which are the ones actually used. Kept here for provenance.
