// Real physics via Matter.js — deterministic by construction.
// Every call rebuilds a FRESH engine from the same initial state and steps
// it a fixed number of fixed-size steps. No React state, no Math.random,
// no wall-clock. Frame N therefore always produces the same bodies, in
// preview and in render. Words/shapes collide, fall and settle — the
// "physics" look from the reference video, as real code, not a preset.

import Matter from 'matter-js';

export interface PhysicsBodyDef {
  id: string;
  label: string;
  x: number;
  y: number;
  w: number;
  h: number;
  angle?: number;
}

export interface PhysicsBodyState extends PhysicsBodyDef {
  angleRad: number;
}

export function simulatePhysics(
  defs: PhysicsBodyDef[],
  frame: number,
  width: number,
  height: number,
): PhysicsBodyState[] {
  const engine = Matter.Engine.create({ enableSleeping: false });
  engine.gravity.y = 1.6;
  const ground = Matter.Bodies.rectangle(width / 2, height + 40, width * 2, 80, {
    isStatic: true,
  });
  const leftWall = Matter.Bodies.rectangle(-40, height / 2, 80, height * 2, {
    isStatic: true,
  });
  const rightWall = Matter.Bodies.rectangle(width + 40, height / 2, 80, height * 2, {
    isStatic: true,
  });
  const bodies = defs.map((d) =>
    Matter.Bodies.rectangle(d.x, d.y, d.w, d.h, {
      angle: d.angle ?? 0,
      restitution: 0.25,
      friction: 0.4,
    }),
  );
  Matter.Composite.add(engine.world, [ground, leftWall, rightWall, ...bodies]);
  const stepMs = 1000 / 30;
  for (let i = 0; i < Math.max(0, frame); i++) {
    Matter.Engine.update(engine, stepMs);
  }
  return defs.map((d, i) => ({
    ...d,
    x: bodies[i].position.x,
    y: bodies[i].position.y,
    angleRad: bodies[i].angle,
  }));
}
