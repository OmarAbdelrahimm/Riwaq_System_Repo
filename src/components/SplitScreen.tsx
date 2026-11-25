import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { useTheme } from "../engine/theme";
import { inOut, progress, unit } from "../engine/motion";

type Panel = { src?: string; title: string; sub?: string; tag: string; world: "real" | "fiction"; at?: number };

/** شاشة منقسمة RTL: اليمين = الواقع (ذهبي)، اليسار = الخيال (عنابي). تنفتح ببطء من المنتصف. */
export const SplitScreen: React.FC<{ right: Panel; left: Panel; openAt?: number; durFrames: number }> = ({ right, left, openAt = 0, durFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { color, bodyFont, headlineFont, width, height, safe } = useTheme();
  const u = unit(width, height);
  const t = inOut(frame, durFrames, fps, 0);
  const k = progress(frame, fps, openAt, openAt + 1.2);
  const vertical = height > width;

  const panel = (p: Panel, side: "right" | "left") => {
    const real = p.world === "real";
    const tk = progress(frame, fps, p.at ?? openAt + 0.4, (p.at ?? openAt + 0.4) + 0.38);
    const clip = vertical
      ? side === "right"
        ? `inset(${50 - 50 * k}% 0 50% 0)`
        : `inset(50% 0 ${50 - 50 * k}% 0)`
      : side === "right"
      ? `inset(0 ${50 - 50 * k}% 0 50%)`
      : `inset(0 50% 0 ${50 - 50 * k}%)`;
    return (
      <AbsoluteFill style={{ clipPath: clip }}>
        {p.src ? (
          <Img
            src={staticFile(p.src)}
            style={{
              position: "absolute",
              ...(vertical
                ? { left: 0, width: "100%", top: side === "right" ? 0 : "50%", height: "50%" }
                : { top: 0, height: "100%", left: side === "right" ? "50%" : 0, width: "50%" }),
              objectFit: "cover",
              filter: real ? "sepia(0.2)" : "saturate(0.6) brightness(0.8)",
            }}
          />
        ) : null}
        <div
          style={{
            position: "absolute",
            ...(vertical
              ? { left: 0, width: "100%", top: side === "right" ? 0 : "50%", height: "50%" }
              : { top: 0, height: "100%", left: side === "right" ? "50%" : 0, width: "50%" }),
            background: real ? `${color("ink_deep")}88` : `${color("burgundy")}99`,
          }}
        />
        <div
          style={{
            position: "absolute",
            ...(vertical
              ? { left: safe.side, right: safe.side, top: side === "right" ? safe.top + 60 * u : height / 2 + 60 * u }
              : { bottom: safe.bottom + 40 * u, ...(side === "right" ? { right: safe.side + 20 * u, left: width / 2 + 40 * u } : { left: safe.side + 20 * u, right: width / 2 + 40 * u }) }),
            textAlign: "right",
            direction: "rtl",
            opacity: tk,
            transform: `translateY(${(1 - tk) * 12 * u}px)`,
          }}
        >
          <span
            style={{
              fontFamily: bodyFont,
              fontWeight: 700,
              fontSize: 26 * u,
              color: real ? color("ink_deep") : color("parchment"),
              background: real ? color("gold_light") : color("burgundy"),
              border: real ? "none" : `1px solid ${color("parchment")}66`,
              padding: `${4 * u}px ${14 * u}px`,
              borderRadius: 4 * u,
            }}
          >
            {p.tag}
          </span>
          <div style={{ fontFamily: headlineFont, fontWeight: 700, fontSize: 54 * u, color: color("parchment"), marginTop: 16 * u, lineHeight: 1.4 }}>{p.title}</div>
          {p.sub ? <div style={{ fontFamily: bodyFont, fontSize: 28 * u, color: color("stone_light"), marginTop: 8 * u }}>{p.sub}</div> : null}
        </div>
      </AbsoluteFill>
    );
  };

  return (
    <AbsoluteFill style={{ opacity: t.opacity }}>
      {panel(right, "right")}
      {panel(left, "left")}
      <div
        style={{
          position: "absolute",
          background: color("gold"),
          ...(vertical ? { left: 0, right: 0, top: height / 2 - u, height: 2 * u } : { top: 0, bottom: 0, left: width / 2 - u, width: 2 * u }),
        }}
      />
    </AbsoluteFill>
  );
};
