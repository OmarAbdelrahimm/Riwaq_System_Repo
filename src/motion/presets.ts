// Ruwaq motion presets — springs only for hero motion, never linear easing.
// Rule from the reference video: motion is what separates amateur from
// professional. A hero title must spring; a linear slide reads like a template.
// Linear (interpolate) is allowed ONLY for opacity fades and progress bars.

import type { SpringConfig } from 'remotion';

export const springs = {
  /** Hero title: fast attack, one small overshoot, settles cleanly. */
  hero: { damping: 16, mass: 0.5, stiffness: 170, overshootClamping: false } satisfies SpringConfig,
  /** Gentle entrance for subtitles / captions. */
  gentle: { damping: 20, mass: 0.6, stiffness: 80, overshootClamping: false } satisfies SpringConfig,
  /** Playful, for chips / physics-adjacent elements. One visible bounce. */
  bouncy: { damping: 10, mass: 0.5, stiffness: 120, overshootClamping: false } satisfies SpringConfig,
  /** Heavy / monumental — for the arch, the gate, the map. */
  monumental: { damping: 22, mass: 1.2, stiffness: 90, overshootClamping: true } satisfies SpringConfig,
} as const;

/** Standard beat-aligned slot: a hero element lives in one beat window. */
export const slots = {
  /** Reference-motion hero slot from the video: 0.00s – 1.88s. */
  heroIn: { startFrame: 0, durationFrames: 56 },
} as const;
