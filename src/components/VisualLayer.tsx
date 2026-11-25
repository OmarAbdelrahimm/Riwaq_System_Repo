import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { useTheme } from "../engine/theme";
import { unit } from "../engine/motion";

export interface VisualSpec {
  src: string;
  t_in: number;
  t_out: number;
  kind: "ai" | "archival";
  fit?: "cover" | "card" | "contain_blur";
  kb?: { from?: number; to?: number; fx0?: number; fy0?: number; fx1?: number; fy1?: number };
  tint?: "none" | "cold" | "burgundy" | "dark" | "warm";
  dim?: number;
  credit?: string;
  fade_in?: boolean;
}

/**
 * طبقة الصور: Ken Burns 1.00→1.06 (brand.json) + وسم إلزامي:
 *  - مولّد بالذكاء الاصطناعي → «إعادة تصوّر» (المعيار التحريري)
 *  - أرشيفي → سطر المصدر والترخيص
 */
export const VisualLayer: React.FC<{ v: VisualSpec; durFrames: number }> = ({ v, durFrames }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const { color, bodyFont, safe, brand } = useTheme();
  const u = unit(width, height);
  const kbFrom = v.kb?.from ?? brand.theme.motion.ken_burns.from;
  const kbTo = v.kb?.to ?? brand.theme.motion.ken_burns.to;
  const p = interpolate(frame, [0, durFrames], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const s = kbFrom + (kbTo - kbFrom) * p;
  const fx = (v.kb?.fx0 ?? 0.5) + ((v.kb?.fx1 ?? v.kb?.fx0 ?? 0.5) - (v.kb?.fx0 ?? 0.5)) * p;
  const fy = (v.kb?.fy0 ?? 0.5) + ((v.kb?.fy1 ?? v.kb?.fy0 ?? 0.5) - (v.kb?.fy0 ?? 0.5)) * p;
  const fadeIn = v.fade_in ? interpolate(frame, [0, Math.round(0.38 * fps)], [0, 1], { extrapolateRight: "clamp" }) : 1;

  const filter =
    v.tint === "cold"
      ? "saturate(0.45) brightness(0.82) contrast(1.05)"
      : v.tint === "dark"
      ? "brightness(0.62) saturate(0.85)"
      : v.tint === "burgundy"
      ? "saturate(0.6) brightness(0.85)"
      : v.tint === "warm"
      ? "sepia(0.2) saturate(1.05)"
      : "none";

  const label =
    v.kind === "ai" ? (
      <div
        style={{
          position: "absolute",
          top: Math.max(safe.top * 0.5, width * 0.028 + 24 * u),
          left: safe.side + 10 * u,
          fontFamily: bodyFont,
          fontWeight: 500,
          fontSize: 22 * u,
          color: color("parchment"),
          background: `${color("ink_deep")}B3`,
          border: `1px solid ${color("stone")}88`,
          padding: `${4 * u}px ${12 * u}px`,
          borderRadius: 4 * u,
          direction: "rtl",
        }}
      >
        إعادة تصوّر · ذكاء اصطناعي
      </div>
    ) : v.credit ? (
      <div
        style={{
          position: "absolute",
          top: Math.max(safe.top * 0.5, width * 0.028 + 24 * u),
          left: safe.side + 10 * u,
          fontFamily: bodyFont,
          fontSize: 22 * u,
          color: color("stone_light"),
          background: `${color("ink_deep")}B3`,
          padding: `${4 * u}px ${12 * u}px`,
          borderRadius: 4 * u,
          direction: "rtl",
          maxWidth: width * 0.5,
        }}
      >
        {v.credit}
      </div>
    ) : null;

  if (v.fit === "card") {
    const maxH = height * 0.62;
    return (
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", opacity: fadeIn }}>
        <div
          style={{
            transform: `scale(${s})`,
            border: `${Math.max(1, 2 * u)}px solid ${color("gold")}`,
            padding: 10 * u,
            background: color("ink_second"),
            boxShadow: `0 ${10 * u}px ${40 * u}px #000000AA`,
          }}
        >
          <Img src={staticFile(v.src)} style={{ display: "block", maxHeight: maxH, maxWidth: width * 0.7 }} />
        </div>
        {label}
      </AbsoluteFill>
    );
  }

  const imgStyle: React.CSSProperties = {
    width: "100%",
    height: "100%",
    objectFit: "cover",
    objectPosition: `${fx * 100}% ${fy * 100}%`,
    transform: `scale(${s})`,
    transformOrigin: `${fx * 100}% ${fy * 100}%`,
    filter,
  };

  return (
    <AbsoluteFill style={{ opacity: fadeIn, backgroundColor: color("ink_deep") }}>
      {v.fit === "contain_blur" ? (
        <>
          <Img src={staticFile(v.src)} style={{ ...imgStyle, transform: "scale(1.15)", filter: `${filter === "none" ? "" : filter} blur(${28 * u}px) brightness(0.45)` }} />
          <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
            <div style={{ width: "100%", overflow: "hidden", marginTop: -height * 0.12 }}>
              <Img
                src={staticFile(v.src)}
                style={{ width: "100%", display: "block", transform: `scale(${s})`, transformOrigin: `${fx * 100}% ${fy * 100}%`, filter }}
              />
            </div>
          </AbsoluteFill>
        </>
      ) : (
        <Img src={staticFile(v.src)} style={imgStyle} />
      )}
      {v.tint === "burgundy" ? (
        <AbsoluteFill style={{ background: color("burgundy"), mixBlendMode: "multiply" as any, opacity: 0.5 }} />
      ) : null}
      <AbsoluteFill
        style={{
          background: `linear-gradient(180deg, ${color("ink_deep")}66 0%, transparent 22%, transparent 62%, ${color("ink_deep")}CC 100%)`,
        }}
      />
      {v.dim ? <AbsoluteFill style={{ background: color("ink_deep"), opacity: v.dim }} /> : null}
      {label}
    </AbsoluteFill>
  );
};
