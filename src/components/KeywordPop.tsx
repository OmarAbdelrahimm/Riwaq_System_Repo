import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { useTheme } from "../engine/theme";
import { EASE, inOut, unit } from "../engine/motion";

export type KwTone = "gold" | "parchment" | "burgundy" | "stone";
export interface KwItem {
  text: string;
  at?: number; // ثوانٍ نسبةً لبداية العنصر
  tone?: KwTone;
  sub?: string;
}

/**
 * KeywordPop — إبراز كلمة/تاريخ/رقم عند نطقه.
 * الدخول: شفافية + صعود 12px خلال 380ms (منحنى الهوية). ممنوع: bounce / zoom_punch / flash.
 */
export const KeywordPop: React.FC<{
  items: KwItem[];
  layout?: "row" | "stack";
  position?: "center" | "top" | "bottom" | "upper_right" | "lower_right";
  size?: number;
  chip?: boolean;
  font?: "headline" | "body";
  scrim?: boolean;
  durFrames: number;
}> = ({ items, layout = "row", position = "center", size = 54, chip = true, font = "body", scrim = false, durFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { color, headlineFont, bodyFont, width, height, safe } = useTheme();
  const u = unit(width, height);
  const all = inOut(frame, durFrames, fps, 0);
  const inF = Math.round(0.38 * fps);

  const toneColor = (tone: KwTone = "gold") =>
    tone === "gold" ? color("gold_light") : tone === "stone" ? color("stone_light") : color("parchment");

  const pos: React.CSSProperties =
    position === "top"
      ? { justifyContent: "flex-start", alignItems: "center", paddingTop: safe.top + 70 * u }
      : position === "bottom"
      ? { justifyContent: "flex-end", alignItems: "center", paddingBottom: safe.bottom + 30 * u }
      : position === "upper_right"
      ? { justifyContent: "flex-start", alignItems: "flex-start", paddingTop: safe.top + 140 * u, paddingRight: safe.side + 20 * u }
      : position === "lower_right"
      ? { justifyContent: "flex-end", alignItems: "flex-start", paddingBottom: safe.bottom + 40 * u, paddingRight: safe.side + 20 * u }
      : { justifyContent: "center", alignItems: "center" };

  return (
    <AbsoluteFill style={{ ...pos, paddingLeft: safe.side }}>
      {scrim ? <AbsoluteFill style={{ background: color("ink_deep"), opacity: 0.5 * all.opacity }} /> : null}
      <div
        style={{
          display: "flex",
          flexDirection: layout === "row" ? "row" : "column",
          flexWrap: "wrap",
          justifyContent: "center",
          alignItems: position.endsWith("right") ? "flex-start" : "center", // RTL: flex-start = اليمين
          gap: 22 * u,
          direction: "rtl",
          maxWidth: width - safe.side * 2,
          opacity: all.opacity,
        }}
      >
        {items.map((it, i) => {
          const f0 = Math.round((it.at ?? 0) * fps);
          const k = interpolate(frame, [f0, f0 + inF], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: EASE,
          });
          const isB = it.tone === "burgundy";
          return (
            <div
              key={i}
              style={{
                opacity: k,
                transform: `translateY(${(1 - k) * 12 * u}px)`,
                fontFamily: font === "headline" ? headlineFont : bodyFont,
                fontWeight: 700,
                fontSize: size * u,
                lineHeight: 1.35,
                color: toneColor(it.tone),
                background: chip ? (isB ? color("burgundy") : `${color("ink_deep")}E6`) : "transparent",
                border: chip ? `${Math.max(1, 1.5 * u)}px solid ${isB ? color("burgundy") : color("gold")}AA` : "none",
                borderRadius: 6 * u,
                padding: chip ? `${10 * u}px ${26 * u}px` : 0,
                textAlign: "center",
                textShadow: chip ? "none" : `0 ${2 * u}px ${16 * u}px ${color("ink_deep")}`,
              }}
            >
              {it.text}
              {it.sub ? (
                <div style={{ fontFamily: bodyFont, fontWeight: 400, fontSize: size * 0.5 * u, color: color("stone_light"), marginTop: 4 * u }}>
                  {it.sub}
                </div>
              ) : null}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
