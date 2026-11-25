// Music is the rhythm — a beat grid, not a vibe prompt.
// From the reference video: pick a REAL track, read its BPM, sync the hero
// title to an exact beat (beat #8). Never prompt "make it exciting".
// BPM 72 = calm (0.833s / beat = 25 frames @30fps). BPM 128 = driving
// (0.469s / beat = 14.06 frames @30fps).

export const FPS = 30;

export const secondsPerBeat = (bpm: number): number => 60 / bpm;

export const framesPerBeat = (bpm: number, fps = FPS): number =>
  secondsPerBeat(bpm) * fps;

/** Frame on which beat N (1-based) STARTS. Beat 8 @128 BPM = frame 98. */
export const beatToFrame = (bpm: number, beatNumber: number, fps = FPS): number =>
  Math.round((beatNumber - 1) * framesPerBeat(bpm, fps));

export const frameToBeat = (bpm: number, frame: number, fps = FPS): number =>
  frame / framesPerBeat(bpm, fps) + 1;

export const tracks = {
  /** Calm documentary bed — title lands gently. */
  calm72: { bpm: 72, titleBeat: 4, label: 'Calm 72 BPM' },
  /** Driving bed — hero title drops on beat #8, as in the reference video. */
  drive128: { bpm: 128, titleBeat: 8, label: 'Driving 128 BPM' },
} as const;

export type TrackId = keyof typeof tracks;
