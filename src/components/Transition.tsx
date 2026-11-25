import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { useTheme } from "../engine/theme";

/**
 * Transition — الانتقالات المسموحة فقط في brand.json: hard_cut (لا شيء يُرسم) و fade_black_200ms.
 * يوضع العنصر بحيث يكون منتصفه على نقطة القطع: 100ms إلى الأسود ثم 100ms منه.
 */
export const Transition: React.FC<{ type: "fade_black_200ms" | "hard_cut"; durFrames: number }> = ({ type, durFrames }) => {
  const frame = useCurrentFrame();
  const { color } = useTheme();
  useVideoConfig();
  if (type !== "fade_black_200ms") return null;
  const mid = durFrames / 2;
  const o = interpolate(frame, [0, mid, durFrames], [0, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return <AbsoluteFill style={{ background: color("ink_deep"), opacity: o }} />;
};
