import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { useTheme } from "../engine/theme";
import { EASE, inOut, progress, unit } from "../engine/motion";

type Key = { t: number; year: number }; // t بالثواني نسبةً لبداية العنصر

const keyed = (keys: Key[], sec: number) => {
  if (!keys.length) return 0;
  if (keys.length === 1 || sec <= keys[0].t) return keys[0].year;
  for (let i = 1; i < keys.length; i++) {
    if (sec <= keys[i].t) {
      const a = keys[i - 1];
      const b = keys[i];
      return interpolate(sec, [a.t, b.t], [a.year, b.year], { easing: EASE });
    }
  }
  return keys[keys.length - 1].year;
};

/**
 * TimelineBar — خط زمني RTL (السنوات تتقدّم من اليمين إلى اليسار).
 *  - cursor: مفاتيح حركة المؤشر (الواقع، ذهبي)
 *  - branch: تفرّع خط الخيال (عنابي) من سنة معيّنة، يتقدّم بمفاتيح alt
 *  - merge: نقطة التقاء الخطين (حدث مشترك بين العالمين)
 */
export const TimelineBar: React.FC<{
  from: number;
  to: number;
  marks?: { year: number; label: string; tone?: "gold" | "burgundy" | "stone" }[];
  cursor?: Key[];
  branch?: { year: number; at: number; alt: Key[]; label?: string };
  merge?: { year: number; at: number; label?: string };
  position?: "center" | "lower";
  durFrames: number;
}> = ({ from, to, marks = [], cursor = [], branch, merge, position = "lower", durFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { color, bodyFont, width, height, safe } = useTheme();
  const u = unit(width, height);
  const sec = frame / fps;
  const t = inOut(frame, durFrames, fps, 0);

  const L = safe.side + 60 * u;
  const R = width - safe.side - 60 * u;
  const y = position === "center" ? height * 0.5 : height - safe.bottom - 150 * u;
  const x = (yr: number) => R - ((yr - from) / (to - from)) * (R - L);
  const cy = cursor.length ? keyed(cursor, sec) : from;
  const draw = progress(frame, fps, 0, 0.8);
  const fs = 30 * u;

  let alt: React.ReactNode = null;
  if (branch) {
    const k = progress(frame, fps, branch.at, branch.at + 0.6);
    const ay = keyed(branch.alt, sec);
    const off = 70 * u * k;
    const bx = x(branch.year);
    const ax = x(Math.max(branch.year, ay));
    let mergeK = 0;
    if (merge) mergeK = progress(frame, fps, merge.at, merge.at + 0.8);
    const yAlt = y + off * (1 - mergeK);
    alt = (
      <g opacity={k}>
        <path
          d={`M ${bx} ${y} C ${bx - 40 * u} ${y}, ${bx - 40 * u} ${yAlt}, ${bx - 80 * u} ${yAlt} L ${Math.min(ax, bx - 80 * u)} ${yAlt}`}
          stroke={color("burgundy")}
          strokeWidth={4 * u}
          fill="none"
        />
        <circle cx={Math.min(ax, bx - 80 * u)} cy={yAlt} r={8 * u} fill={color("burgundy")} stroke={color("parchment")} strokeWidth={1.5 * u} />
        {branch.label ? (
          <text x={bx - 90 * u} y={yAlt + 46 * u} fill={color("parchment")} fontFamily={bodyFont} fontSize={fs * 0.9} textAnchor="start">
            {branch.label}
          </text>
        ) : null}
      </g>
    );
  }

  return (
    <AbsoluteFill style={{ opacity: t.opacity }}>
      <svg width={width} height={height} style={{ position: "absolute", inset: 0 }}>
        <line x1={R - (R - L) * draw} x2={R} y1={y} y2={y} stroke={color("stone")} strokeOpacity={0.6} strokeWidth={2 * u} />
        <line x1={x(cy)} x2={R} y1={y} y2={y} stroke={color("gold")} strokeWidth={4 * u} />
        {[from, to].map((yr) => (
          <text key={yr} x={x(yr)} y={y + 52 * u} fill={color("stone_light")} fontFamily={bodyFont} fontSize={fs * 0.85} textAnchor="middle">
            {yr}
          </text>
        ))}
        {marks.map((m, i) => {
          const mx = x(m.year);
          const c = m.tone === "burgundy" ? color("burgundy") : m.tone === "stone" ? color("stone_light") : color("gold_light");
          return (
            <g key={i}>
              <line x1={mx} x2={mx} y1={y - 14 * u} y2={y + 14 * u} stroke={c} strokeWidth={2 * u} />
              <text x={mx} y={y - 30 * u} fill={c} fontFamily={bodyFont} fontWeight={700} fontSize={fs} textAnchor="middle">
                {m.year}
              </text>
              <text x={mx} y={y - 70 * u} fill={color("parchment")} fontFamily={bodyFont} fontSize={fs * 0.8} textAnchor="middle">
                {m.label}
              </text>
            </g>
          );
        })}
        {alt}
        <circle cx={x(cy)} cy={y} r={9 * u} fill={color("gold_light")} />
        {marks.some((m) => Math.abs(m.year - cy) < 0.35) ? null : <text x={x(cy)} y={y + 52 * u} fill={color("gold_light")} fontFamily={bodyFont} fontWeight={700} fontSize={fs} textAnchor="middle">
          {Math.round(cy)}
        </text>}
        {merge ? (
          (() => {
            const k = progress(frame, fps, merge.at + 0.6, merge.at + 1.2);
            return (
              <g opacity={k}>
                <circle cx={x(merge.year)} cy={y} r={16 * u} fill="none" stroke={color("gold_light")} strokeWidth={2 * u} />
                {merge.label ? (
                  <text x={x(merge.year)} y={y + 100 * u} fill={color("parchment")} fontFamily={bodyFont} fontSize={fs * 0.9} textAnchor="middle">
                    {merge.label}
                  </text>
                ) : null}
              </g>
            );
          })()
        ) : null}
      </svg>
    </AbsoluteFill>
  );
};
