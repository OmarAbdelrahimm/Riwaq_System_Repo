// Ruwaq brand tokens — SINGLE SOURCE OF TRUTH for colour / type in code.
// Mirrors BRAND.md. Decision (2026-11-23, OMAR): A Petrol Teal is PRIMARY,
// C Ink Navy + Amber is SECONDARY / episode accent (military / night episodes).
// B Plum/Rose Gold was DROPPED — it is not in these tokens.
// V1 gold/charcoal is kept below as LEGACY only — do not use it for new work.
// The live YouTube profile still shows V1 until OMAR confirms the swap.

export const brand = {
  name: 'Ruwaq',
  tagline: 'قصص الأفكار والتحولات الكبرى',
  taglineLatin: 'Stories of Ideas and Great Transformations',
} as const;

export const paletteA = {
  // PRIMARY — Petrol Teal Portal
  deepPetrolTeal: '#0E2A2E',
  tealDark: '#081C1F',
  champagne: '#D8C3A5',
  warmIvory: '#F5EFE6',
  aquaLight: '#7FB5A8',
} as const;

export const paletteC = {
  // SECONDARY — Ink Navy + Amber (episode accent)
  inkNavy: '#0B1F3A',
  amber: '#E8A33D',
  sand: '#E9DFCE',
  steelBlue: '#3A5A7A',
} as const;

export const paletteV1Legacy = {
  // LEGACY — gold/charcoal, live on the channel until the swap is confirmed.
  // New compositions must NOT use these.
  gold: '#C2A469',
  charcoal: '#1C1B19',
} as const;

export const colors = {
  bg: paletteA.deepPetrolTeal,
  bgDark: paletteA.tealDark,
  text: paletteA.warmIvory,
  line: paletteA.champagne,
  accent: paletteA.aquaLight,
  accentAlt: paletteC.amber,
  navy: paletteC.inkNavy,
  sand: paletteC.sand,
  steel: paletteC.steelBlue,
} as const;

export const fonts = {
  // Headlines: Cairo Bold / geometric Kufi feel. Body: IBM Plex Sans Arabic.
  // Amiri is reserved for historical quotes inside a video, never for the logo.
  headline: "'Cairo', 'IBM Plex Sans Arabic', sans-serif",
  body: "'IBM Plex Sans Arabic', 'Cairo', sans-serif",
  quote: "'Amiri', serif",
} as const;

export const spacing = {
  pad: 96,
  padShorts: 72,
} as const;
