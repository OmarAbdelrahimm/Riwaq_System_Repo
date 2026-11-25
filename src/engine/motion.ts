import { interpolate, Easing } from "remotion";

/** وحدة قياس موحّدة: 1 = 1px على ضلع 1080 الأقصر (تعمل لـ16x9 و9x16 معًا) */
export const unit = (width: number, height: number) => Math.min(width, height) / 1080;

export const EASE = Easing.bezier(0.2, 0.8, 0.2, 1);

/** دخول 380ms / خروج 280ms من brand.json motion (rise 12px) — بلا ارتداد */
export function inOut(frame: number, durFrames: number, fps: number, risePx = 12) {
  const inF = Math.max(1, Math.round(0.38 * fps));
  const outF = Math.max(1, Math.round(0.28 * fps));
  const a = interpolate(frame, [0, inF], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE });
  const b = interpolate(frame, [Math.max(inF, durFrames - outF), Math.max(inF + 1, durFrames)], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: EASE,
  });
  return { opacity: Math.min(a, b), y: (1 - a) * risePx };
}

export const clamp01 = (v: number) => Math.max(0, Math.min(1, v));

/** تقدّم 0→1 بين لحظتين (بالثواني) مع منحنى الهوية */
export function progress(frame: number, fps: number, t0: number, t1: number) {
  if (t1 <= t0) return frame / fps >= t0 ? 1 : 0;
  return interpolate(frame / fps, [t0, t1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE });
}

/** خلط لونين HEX */
export function mixHex(a: string, b: string, t: number) {
  const p = (h: string) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  const [r1, g1, b1] = p(a);
  const [r2, g2, b2] = p(b);
  const m = (x: number, y: number) => Math.round(x + (y - x) * t).toString(16).padStart(2, "0");
  return `#${m(r1, r2)}${m(g1, g2)}${m(b1, b2)}`;
}
