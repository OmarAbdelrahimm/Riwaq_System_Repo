# RUWAQ — BRAND.md (single source of truth)

**Status:** 2026-11-23. OMAR chose **A AND C** from the v2 proposal
(`workspace/your_files/ruwaq-brand-v2/BRAND-KIT-v2.md`). **B Plum/Rose Gold
is dropped.** The live YouTube profile still shows V1 gold/charcoal and must
NOT be replaced until OMAR confirms the swap. This file governs the *new
motion system* (code in `src/brand/tokens.ts` mirrors it exactly).

## Positioning

"رواق | قصص الأفكار والتحولات الكبرى" — transformations, not "تاريخ وتراث".
The arch is a portal: you walk through it dark, you come out changed.
One clean arch line, light inside it. No carvings, no filigree, no geometric
pattern background.

## A — PRIMARY: Petrol Teal Portal

| Role | Colour | Hex |
|---|---|---|
| Primary background | Deep Petrol Teal | `#0E2A2E` |
| Shadows / lower-thirds | Deep Teal Dark | `#081C1F` |
| Arch line | Champagne | `#D8C3A5` |
| Wordmark / text on dark | Warm Ivory | `#F5EFE6` |
| Motion accent (sparingly) | Aqua Light | `#7FB5A8` |

Use A for everything by default: titles, lower-thirds, demo, channel art.

## C — SECONDARY: Ink Navy + Amber (episode accent)

| Role | Colour | Hex |
|---|---|---|
| Episode background | Ink Navy | `#0B1F3A` |
| CTA / highlight | Amber | `#E8A33D` |
| Wordmark on navy | Sand | `#E9DFCE` |
| Accent | Steel Blue | `#3A5A7A` |

Use C for military / night episodes (e.g. Ghost Army) and for the physics
chips / accent frames inside an A composition. Never mix A and C backgrounds
in one frame — one background, one accent.

## Legacy V1 (do not use for new work)

Gold `#C2A469` on charcoal `#1C1B19`, Amiri/IBM Plex. It is the live channel
identity until the swap is confirmed. It stays in `tokens.ts` as
`paletteV1Legacy` for reference only. Drive also has a navy/blue + Cairo
Bible V2 — Direction C above is the closest to it, and C was chosen instead.

## Type

- Headlines: **Cairo Bold** (geometric Kufi feel). Tagline in Cairo.
- Body: **IBM Plex Sans Arabic**.
- **Amiri only for historical quotes inside a video, never for the logo.**
- Text on dark: Ivory / Sand only. Never pure white `#FFFFFF`.

## Motion (the fingerprint)

- Hero motion is **spring, never linear** (`src/motion/presets.ts`).
  Reference slot from the video: hero 0.00s–1.88s, spring timing.
- Music is the rhythm: read the track's BPM, drop the title on an exact
  beat (beat #8 at 128 BPM = frame 98). See `src/audio/beatgrid.ts`.
- Accent colour is for motion and ONE highlight per frame only.
- A reference motion is applied by copying its **timing + structure** and
  re-skinning it with Ruwaq colours/shapes — never by copying its look.
