import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { useTheme } from "../engine/theme";
import { unit } from "../engine/motion";

/** ProgressBar — خيط ذهبي رفيع أسفل الإطار يتقدّم من اليمين إلى اليسار (RTL) مع علامات الفصول */
export const ProgressBar: React.FC<{ chapters: { t: number }[]; total_s: number; fictionRanges?: { t_in: number; t_out: number }[] }> = ({
  chapters,
  total_s,
  fictionRanges = [],
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const { color } = useTheme();
  const u = unit(width, height);
  const inset = width * 0.028;
  const w = width - inset * 2;
  const p = Math.min(1, frame / fps / total_s);
  const y = height - inset - 6 * u;
  const x = (t: number) => inset + w - (t / total_s) * w;
  return (
    <AbsoluteFill>
      <svg width={width} height={height} style={{ position: "absolute", inset: 0 }}>
        <line x1={inset} x2={inset + w} y1={y} y2={y} stroke={color("stone")} strokeOpacity={0.35} strokeWidth={2 * u} />
        <line x1={inset + w - p * w} x2={inset + w} y1={y} y2={y} stroke={color("gold")} strokeWidth={2.5 * u} />
        {fictionRanges.map((r, i) => {
          const now = frame / fps;
          const a = x(r.t_in);
          const b = x(Math.min(r.t_out, now));
          return (
            <g key={i}>
              <line x1={x(r.t_out)} x2={a} y1={y} y2={y} stroke={color("burgundy")} strokeOpacity={0.45} strokeWidth={2 * u} />
              {now > r.t_in ? <line x1={b} x2={a} y1={y} y2={y} stroke={color("burgundy")} strokeWidth={2.5 * u} /> : null}
            </g>
          );
        })}
        {chapters.map((c, i) => (
          <circle key={i} cx={x(c.t)} cy={y} r={3 * u} fill={c.t <= frame / fps ? color("gold_light") : color("stone")} />
        ))}
      </svg>
    </AbsoluteFill>
  );
};
