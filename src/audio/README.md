# Audio — how to add a real track

Music is the rhythm of a Ruwaq episode. Do not prompt an AI for "exciting
music". Use a real, licensed track and sync to its BPM (see `beatgrid.ts`).

## Adding a track (licensed only)

1. Get a licensed track (production library, licensed stock, or original
   composition). **Do not download unlicensed music into this repo.**
2. Put the file in `public/audio/`, e.g. `public/audio/ghost-army-bed.mp3`.
3. Note its BPM (read it in your DAW or a BPM tool — do not guess).
4. In the composition, register it in `src/audio/beatgrid.ts`:
   `myTrack: { bpm: 128, titleBeat: 8, label: 'Ghost Army bed' }`
5. Add SFX cues in `src/audio/sfx.ts` with `file: 'audio/whoosh.mp3'`.

## Current state

- No audio files are bundled. All SFX cues in `sfx.ts` are placeholders
  (no `file`) and render silently — by design, so a missing file can never
  break a render.
- Demo composition uses `drive128` (128 BPM): hero title on beat #8,
  frame 98. Calm alternative: `calm72` (72 BPM), title on beat #4.
