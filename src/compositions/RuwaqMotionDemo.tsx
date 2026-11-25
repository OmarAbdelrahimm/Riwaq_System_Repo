// RuwaqMotionDemo — the proof that the Ruwaq motion system works.
// 10s @30fps. Proves, in one composition:
//  1. Spring hero title landing exactly on beat #8 (128 BPM -> frame 98)
//  2. Hand-drawn Rough.js arch + frame (fixed seed, deterministic)
//  3. Watercolour wash (SVG turbulence, fixed seed)
//  4. Matter.js physics collision (word chips fall, collide, settle)
//  5. Brand A (Petrol Teal) with C (Ink Navy/Amber) as the accent
// Kept separate from the Bab Zuwayla composition on purpose.

import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { brand, colors } from '../brand/tokens';
import { springs } from '../motion/presets';
import { roughArchPath, roughPaths } from '../motion/rough';
import { WatercolorWash } from '../motion/watercolor';
import { simulatePhysics, type PhysicsBodyDef } from '../motion/physics';
import { beatToFrame, tracks } from '../audio/beatgrid';

const CHIPS: PhysicsBodyDef[] = [
  { id: 'c1', label: '1105', x: 480, y: -60, w: 170, h: 84 },
  { id: 'c2', label: 'جندي', x: 760, y: -140, w: 170, h: 84, angle: 0.12 },
  { id: 'c3', label: 'خدعة', x: 1040, y: -80, w: 170, h: 84, angle: -0.1 },
  { id: 'c4', label: 'جيش وهمي', x: 1300, y: -180, w: 220, h: 84, angle: 0.08 },
  { id: 'c5', label: '1944', x: 620, y: -220, w: 170, h: 84, angle: -0.06 },
];

export const RuwaqMotionDemo: React.FC<{ variant?: 'wide' | 'shorts' }> = ({
  variant = 'wide',
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const isShorts = variant === 'shorts';
  const titleFrame = beatToFrame(tracks.drive128.bpm, tracks.drive128.titleBeat, fps);

  const titleSpring = spring({
    frame: frame - titleFrame,
    fps,
    config: springs.hero,
  });
  const titleOpacity = interpolate(frame, [titleFrame, titleFrame + 12], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const washOpacity = interpolate(frame, [0, 40], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const outroOpacity = interpolate(frame, [240, 260], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Physics starts when the title lands; chips fall into a pit.
  const physicsFrame = Math.max(0, frame - titleFrame - 10);
  const pitY = isShorts ? height - 420 : height - 260;
  const bodies = simulatePhysics(CHIPS, physicsFrame, width, height);
  const framePaths = roughPaths('rectangle', 48, 48, width - 96, height - 96, 7);
  const archPaths = roughArchPath(
    width / 2 - 130,
    isShorts ? 180 : 120,
    260,
    300,
    7,
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: colors.bg,
        color: colors.text,
        fontFamily: "'Cairo', sans-serif",
        direction: 'rtl',
      }}
    >
      <div style={{ opacity: washOpacity }}>
        <WatercolorWash color={colors.accent} opacity={0.35} seed={11} />
        <WatercolorWash color={colors.accentAlt} opacity={0.22} seed={23} />
      </div>

      {/* Hand-drawn frame */}
      <svg width={width} height={height} style={{ position: 'absolute', inset: 0 }}>
        {framePaths.map((d, i) => (
          <path key={i} d={d} fill="none" stroke={colors.line} strokeWidth={2.5} />
        ))}
        {archPaths.map((d, i) => (
          <path key={i} d={d} fill="none" stroke={colors.line} strokeWidth={3} />
        ))}
      </svg>

      {/* Subtitle */}
      <div
        style={{
          position: 'absolute',
          top: isShorts ? 520 : 470,
          width: '100%',
          textAlign: 'center',
          fontSize: isShorts ? 44 : 40,
          color: colors.sand,
          opacity: interpolate(frame, [10, 40], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          }),
        }}
      >
        {brand.tagline}
      </div>

      {/* Hero title — springs in exactly on beat #8 */}
      <div
        style={{
          position: 'absolute',
          top: isShorts ? 620 : 560,
          width: '100%',
          textAlign: 'center',
          opacity: titleOpacity,
          transform: `translateY(${(1 - titleSpring) * 90}px) scale(${0.82 + titleSpring * 0.18})`,
        }}
      >
        <div style={{ fontSize: isShorts ? 150 : 170, fontWeight: 900, lineHeight: 1.1 }}>
          الجيش الشبح
        </div>
        <div
          style={{
            fontSize: isShorts ? 44 : 40,
            color: colors.accent,
            marginTop: 12,
          }}
        >
          1105 جندي خدعوا جيشًا كاملًا
        </div>
      </div>

      {/* Physics chips — fall, collide, settle in the pit */}
      {frame > titleFrame + 10 &&
        bodies.map((b) => (
          <div
            key={b.id}
            style={{
              position: 'absolute',
              left: b.x - b.w / 2,
              top: Math.min(b.y - b.h / 2, pitY),
              width: b.w,
              height: b.h,
              backgroundColor: colors.navy,
              border: `2px solid ${colors.accentAlt}`,
              borderRadius: 14,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 40,
              fontWeight: 800,
              color: colors.text,
              transform: `rotate(${b.angleRad}rad)`,
            }}
          >
            {b.label}
          </div>
        ))}

      {/* Outro */}
      <div
        style={{
          position: 'absolute',
          bottom: 70,
          width: '100%',
          textAlign: 'center',
          opacity: outroOpacity,
          fontSize: 44,
          fontWeight: 800,
        }}
      >
        رواق — {brand.tagline}
      </div>
    </AbsoluteFill>
  );
};
