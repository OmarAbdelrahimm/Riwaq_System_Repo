import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { useTheme } from "../engine/theme";
import { inOut, unit } from "../engine/motion";

/** عنوان مشهد: Amiri عريض + كيكر + مسطرة ذهبية. لا ارتداد ولا تكبير مفاجئ. */
export const SceneTitle: React.FC<{
  title: string;
  kicker?: string;
  sub?: string;
  tone?: "gold" | "burgundy" | "parchment";
  position?: "center" | "upper" | "lower";
  size?: number;
  scrim?: boolean;
  durFrames: number;
}> = ({ title, kicker, sub, tone = "parchment", position = "center", size = 92, scrim = false, durFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { color, headlineFont, bodyFont, width, height, safe } = useTheme();
  const u = unit(width, height);
  const t = inOut(frame, durFrames, fps, 12 * u);
  const ruleW = Math.min(1, frame / Math.round(0.6 * fps)) * 160 * u;
  const titleColor = tone === "gold" ? color("gold_light") : color("parchment");
  const justify = position === "center" ? "center" : position === "upper" ? "flex-start" : "flex-end";

  return (
    <AbsoluteFill
      style={{
        alignItems: "center",
        justifyContent: justify,
        paddingTop: position === "upper" ? safe.top + 60 * u : 0,
        paddingBottom: position === "lower" ? safe.bottom + 40 * u : 0,
        paddingLeft: safe.side,
        paddingRight: safe.side,
      }}
    >
      {scrim ? (
        <AbsoluteFill style={{ background: `${color("ink_deep")}`, opacity: 0.55 * t.opacity }} />
      ) : null}
      <div style={{ opacity: t.opacity, transform: `translateY(${t.y}px)`, textAlign: "center", direction: "rtl" }}>
        {kicker ? (
          <div
            style={{
              fontFamily: bodyFont,
              fontWeight: 700,
              fontSize: 34 * u,
              letterSpacing: 0,
              color: tone === "burgundy" ? color("parchment") : color("gold_light"),
              background: tone === "burgundy" ? color("burgundy") : "transparent",
              display: "inline-block",
              padding: tone === "burgundy" ? `${6 * u}px ${18 * u}px` : 0,
              borderRadius: 4 * u,
              marginBottom: 30 * u,
            }}
          >
            {kicker}
          </div>
        ) : null}
        <div
          style={{
            fontFamily: headlineFont,
            fontWeight: 700,
            fontSize: size * u,
            lineHeight: 1.45,
            color: titleColor,
            whiteSpace: "pre-line",
            textShadow: `0 ${2 * u}px ${18 * u}px ${color("ink_deep")}`,
          }}
        >
          {title}
        </div>
        <div
          style={{
            height: Math.max(2, 2 * u),
            width: ruleW,
            margin: `${18 * u}px auto 0`,
            background: tone === "burgundy" ? color("burgundy") : color("gold"),
          }}
        />
        {sub ? (
          <div style={{ fontFamily: bodyFont, fontSize: 30 * u, color: color("stone_light"), marginTop: 16 * u }}>{sub}</div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
