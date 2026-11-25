import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import type { Brand } from "../engine/types";
import { ThemeProvider, useTheme } from "../engine/theme";
import { Paper } from "../components/Paper";
import { BrandMark } from "../components/BrandMark";

/**
 * صور مصغّرة 1280×720 — ثلاثة أنماط: face (وجه/تعبير)، puzzle (لغز بصري)، before_after (قبل/بعد).
 * القواعد: ≤4 كلمات، ألوان الهوية فقط، الشعار، وسم «خيال تاريخي» حين يكون الطرح افتراضيًا.
 */
export interface ThumbProps {
  variant: "face" | "puzzle" | "before_after";
  title: string;
  img_a: string;
  img_b?: string;
  tag?: string;
}

const Tag: React.FC<{ text: string; tone: "burgundy" | "gold"; style?: React.CSSProperties }> = ({ text, tone, style }) => {
  const { color, bodyFont } = useTheme();
  return (
    <div
      style={{
        position: "absolute",
        fontFamily: bodyFont,
        fontWeight: 700,
        fontSize: 34,
        padding: "6px 20px",
        borderRadius: 6,
        background: tone === "burgundy" ? color("burgundy") : color("gold_light"),
        color: tone === "burgundy" ? color("parchment") : color("ink_deep"),
        direction: "rtl",
        ...style,
      }}
    >
      {text}
    </div>
  );
};

const Inner: React.FC<ThumbProps> = ({ variant, title, img_a, img_b, tag }) => {
  const { color, headlineFont } = useTheme();
  const titleStyle: React.CSSProperties = {
    position: "absolute",
    fontFamily: headlineFont,
    fontWeight: 700,
    color: color("parchment"),
    lineHeight: 1.25,
    direction: "rtl",
    textShadow: `0 4px 24px ${color("ink_deep")}, 0 0 2px ${color("ink_deep")}`,
    whiteSpace: "pre-line",
  };
  return (
    <AbsoluteFill style={{ direction: "rtl" }}>
      <Paper />
      {variant === "face" ? (
        <>
          <Img src={staticFile(img_a)} style={{ position: "absolute", right: 0, top: 0, height: 720, width: 560, objectFit: "cover", objectPosition: "50% 22%" }} />
          <AbsoluteFill style={{ background: `linear-gradient(270deg, transparent 0%, transparent 30%, ${color("ink_deep")} 46%)` }} />
          <div style={{ ...titleStyle, left: 60, top: 170, width: 700, fontSize: 132, textAlign: "center" }}>{title}</div>
          <div style={{ position: "absolute", left: 300, top: 560, width: 220, height: 4, background: color("gold") }} />
        </>
      ) : null}
      {variant === "puzzle" ? (
        <>
          <Img src={staticFile(img_a)} style={{ position: "absolute", inset: 0, width: 1280, height: 720, objectFit: "cover", filter: "brightness(0.55)" }} />
          <div style={{ position: "absolute", right: 70, top: 40, fontFamily: headlineFont, fontWeight: 700, fontSize: 470, lineHeight: 1, color: color("gold_light"), opacity: 0.92, textShadow: `0 8px 40px ${color("ink_deep")}` }}>؟</div>
          <div style={{ ...titleStyle, left: 60, top: 300, width: 820, fontSize: 124, textAlign: "left" }}>{title}</div>
          <div style={{ position: "absolute", left: 80, top: 120, fontFamily: headlineFont, fontWeight: 700, fontSize: 110, color: color("stone_light") }}>
            <span style={{ position: "relative" }}>
              1258
              <span style={{ position: "absolute", left: -10, right: -10, top: "52%", height: 10, background: color("burgundy"), transform: "rotate(-8deg)" }} />
            </span>
          </div>
        </>
      ) : null}
      {variant === "before_after" ? (
        <>
          <Img src={staticFile(img_a)} style={{ position: "absolute", right: 0, top: 0, width: 640, height: 720, objectFit: "cover", objectPosition: "60% 50%", filter: "brightness(0.8)" }} />
          <Img src={staticFile(img_b ?? img_a)} style={{ position: "absolute", left: 0, top: 0, width: 640, height: 720, objectFit: "cover", filter: "brightness(0.8)" }} />
          <div style={{ position: "absolute", left: 638, top: 0, width: 4, height: 720, background: color("gold_light") }} />
          <AbsoluteFill style={{ background: `linear-gradient(0deg, ${color("ink_deep")} 0%, transparent 45%)` }} />
          <div style={{ position: "absolute", left: 0, top: 0, width: 640, height: 720, background: color("burgundy"), mixBlendMode: "multiply", opacity: 0.45 }} />
          <Tag text="1258" tone="gold" style={{ right: 40, top: 40 }} />
          <div style={{ ...titleStyle, left: 0, right: 0, bottom: 60, fontSize: 118, textAlign: "center" }}>{title}</div>
        </>
      ) : null}
      {tag ? <Tag text={tag} tone="burgundy" style={{ left: 40, top: 40 }} /> : null}
      <div style={{ position: "absolute", left: variant === "face" ? 40 : undefined, right: variant === "face" ? undefined : 40, bottom: 34, opacity: 0.9 }}>
        <BrandMark sizePx={58} color={color("gold_light")} />
      </div>
    </AbsoluteFill>
  );
};

export const Thumbnail: React.FC<ThumbProps & { brand: Brand }> = ({ brand, ...p }) => (
  <ThemeProvider brand={brand} width={1280} height={720} aspect="16x9">
    <Inner {...p} />
  </ThemeProvider>
);
