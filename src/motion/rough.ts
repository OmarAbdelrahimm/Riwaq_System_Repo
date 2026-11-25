// Hand-drawn look via Rough.js — deterministic, DOM-free.
// We use rough.generator with a FIXED seed and convert its draw ops to SVG
// path data ourselves, so every frame renders identically (no Math.random,
// no live canvas). The same seed + same shape = the same wobble, every render.

import rough from 'roughjs';

type Op = { op: string; data: number[] };

function opsToPathData(ops: Op[]): string {
  let d = '';
  for (const { op, data } of ops) {
    if (op === 'move') d += `M ${data[0].toFixed(2)} ${data[1].toFixed(2)} `;
    else if (op === 'lineTo') d += `L ${data[0].toFixed(2)} ${data[1].toFixed(2)} `;
    else if (op === 'bcurveTo')
      d += `C ${data[0].toFixed(2)} ${data[1].toFixed(2)}, ${data[2].toFixed(2)} ${data[3].toFixed(2)}, ${data[4].toFixed(2)} ${data[5].toFixed(2)} `;
  }
  return d.trim();
}

export function roughPaths(
  kind: 'rectangle' | 'ellipse' | 'line',
  x: number,
  y: number,
  w: number,
  h: number,
  seed = 7,
): string[] {
  const gen = rough.generator();
  const drawable =
    kind === 'rectangle'
      ? gen.rectangle(x, y, w, h, { seed, roughness: 1.4, bowing: 2 })
      : kind === 'ellipse'
        ? gen.ellipse(x + w / 2, y + h / 2, w, h, { seed, roughness: 1.4, bowing: 2 })
        : gen.line(x, y, x + w, y + h, { seed, roughness: 1.4, bowing: 2 });
  return drawable.sets.map((set) => opsToPathData(set.ops as Op[]));
}

/** An arch (the Ruwaq portal) as a hand-drawn SVG path — the brand mark. */
export function roughArchPath(
  x: number,
  y: number,
  w: number,
  h: number,
  seed = 7,
): string[] {
  const gen = rough.generator();
  // Arch = two verticals + a semicircular top, drawn as one path.
  const r = w / 2;
  const d = gen.path(
    `M ${x} ${y + h} L ${x} ${y + r} A ${r} ${r} 0 0 1 ${x + w} ${y + r} L ${x + w} ${y + h}`,
    { seed, roughness: 1.2, bowing: 1.5 },
  );
  return d.sets.map((set) => opsToPathData(set.ops as Op[]));
}
