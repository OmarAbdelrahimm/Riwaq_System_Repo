import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { useTheme } from "../engine/theme";
import { inOut, progress, unit } from "../engine/motion";

/** أعمدة مقارنة رقمية — ترتفع تتابعيًا (rise 12px، 380ms). الترتيب RTL. */
export const Bars: React.FC<{
  items: { label: string; value: number; display: string; at?: number }[];
  title?: string;
  note?: string;
  noteAt?: number;
  durFrames: number;
}> = ({ items, title, note, noteAt = 0, durFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { color, bodyFont, headlineFont, width, height, safe } = useTheme();
  const u = unit(width, height);
  const t = inOut(frame, durFrames, fps, 0);
  const max = Math.max(...items.map((i) => i.value));
  const baseY = height - safe.bottom - 160 * u;
  const maxH = height * 0.48;
  const colW = Math.min(170 * u, (width - safe.side * 2) / (items.length * 2));
  const gap = colW * 0.9;
  const total = items.length * colW + (items.length - 1) * gap;
  const x0 = (width + total) / 2; // نبدأ من اليمين
  return (
    <AbsoluteFill style={{ opacity: t.opacity }}>
      {title ? (
        <div style={{ position: "absolute", top: safe.top + 150 * u, width: "100%", textAlign: "center", fontFamily: headlineFont, fontWeight: 700, fontSize: 56 * u, color: color("parchment") }}>
          {title}
        </div>
      ) : null}
      <svg width={width} height={height} style={{ position: "absolute", inset: 0 }}>
        <line x1={x0 - total - 40 * u} x2={x0 + 40 * u} y1={baseY} y2={baseY} stroke={color("stone")} strokeWidth={2 * u} />
        {items.map((it, i) => {
          const k = progress(frame, fps, it.at ?? i * 0.6, (it.at ?? i * 0.6) + 0.38 + 0.5);
          const h = Math.max(10 * u, (it.value / max) * maxH) * k;
          const x = x0 - (i + 1) * colW - i * gap;
          return (
            <g key={i} opacity={k > 0 ? 1 : 0}>
              <rect x={x} y={baseY - h} width={colW} height={h} fill={color("gold")} />
              <text x={x + colW / 2} y={baseY - h - 22 * u} fill={color("gold_light")} fontFamily={bodyFont} fontWeight={700} fontSize={36 * u} textAnchor="middle" opacity={k}>
                {it.display}
              </text>
              <text x={x + colW / 2} y={baseY + 46 * u} fill={color("parchment")} fontFamily={bodyFont} fontSize={30 * u} textAnchor="middle" opacity={k}>
                {it.label}
              </text>
            </g>
          );
        })}
      </svg>
      {note ? (
        <div
          style={{
            position: "absolute",
            bottom: safe.bottom + 40 * u,
            width: "100%",
            textAlign: "center",
            fontFamily: bodyFont,
            fontWeight: 700,
            fontSize: 34 * u,
            color: color("stone_light"),
            opacity: progress(frame, fps, noteAt, noteAt + 0.38),
          }}
        >
          {note}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
