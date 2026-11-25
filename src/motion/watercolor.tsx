// Watercolour wash — deterministic SVG turbulence, no live paint loop.
//
// Why not p5.brush: p5.brush (npm 3.0.0) exists, but it needs a live p5
// sketch loop — an imperative, stateful draw loop. Remotion renders each
// frame as a pure function, so a live loop is non-deterministic and can
// desync between preview and render. The SVG feTurbulence wash below gives
// the same watercolour edge with a FIXED seed, so frame N is identical on
// every render. If a future episode genuinely needs p5.brush, it must be
// pre-rendered to a still/sequence first — never run live inside a composition.

import React from 'react';

export const WatercolorWash: React.FC<{
  color: string;
  opacity?: number;
  seed?: number;
  style?: React.CSSProperties;
}> = ({ color, opacity = 0.55, seed = 11, style }) => {
  const id = `wash-${seed}`;
  return (
    <svg
      width="100%"
      height="100%"
      style={{ position: 'absolute', inset: 0, ...style }}
      aria-hidden
    >
      <defs>
        <filter id={id}>
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.012 0.02"
            numOctaves={3}
            seed={seed}
          />
          <feDisplacementMap in="SourceGraphic" scale={90} />
        </filter>
      </defs>
      <ellipse
        cx="50%"
        cy="46%"
        rx="42%"
        ry="34%"
        fill={color}
        opacity={opacity}
        filter={`url(#${id})`}
      />
    </svg>
  );
};
