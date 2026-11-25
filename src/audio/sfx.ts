// SFX cue system — every sound is a cue on a frame, with a named slot.
// No audio files are bundled in this repo. Add licensed files under
// public/audio/ (see src/audio/README.md) and point a cue at the file.
// A cue with no file is a silent placeholder — it never breaks a render.

export interface SfxCue {
  atFrame: number;
  name: string;
  /** Path under public/, e.g. 'audio/whoosh.mp3'. Leave empty = placeholder. */
  file?: string;
  volume?: number;
  note: string;
}

/** Demo cues, synced to the RuwaqMotionDemo beat grid (128 BPM). */
export const demoCues: SfxCue[] = [
  { atFrame: 0, name: 'wash-in', note: 'Soft swell as the watercolour wash appears' },
  { atFrame: 98, name: 'title-thud', note: 'Low thud exactly on beat #8, with the hero title' },
  { atFrame: 120, name: 'chip-drop', note: 'Light tick as the first physics chip lands' },
  { atFrame: 240, name: 'outro-chime', note: 'Single chime under the Ruwaq wordmark' },
];

export function cuesAtFrame(cues: SfxCue[], frame: number): SfxCue[] {
  return cues.filter((c) => c.atFrame === frame);
}
