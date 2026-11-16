import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { useTheme, scalePx } from "../engine/theme";
import { textTiming, kenBurns } from "../engine/timing";

/**
 * H — إطار الخلفية البصرية (`broll`).
 *
 * لوح فوتوغرافي مولَّد خصيصًا لهذا الفيلم (موسوم «إعادة تخيّل»، لا أرشيف — راجع
 * `public/projects/TMB_001/plates/PLATES.md`) + طبقة تظليل + طبقة نصية.
 *
 * القيود (من brand.json و STYLE_BLOCK.md):
 *  - الحركة الوحيدة: ken_burns 1.0→1.06 من الثيم. لا وميض/دوران/parallax.
 *  - scrim إلزامي ≥0.18 فوق الصورة إذا وُضع نص.
 *  - لا وجوه مواجهة للكاميرا (أصلًا في البرومبت).
 */
export const BrollFrame: React.FC<{
  plate?: string;
  title?: string;
  label?: string;
  kicker?: string;
  durFrames: number;
  scrim?: number;
  textPos?: "top" | "bottom";
}> = ({ plate, title, label, kicker, durFrames, scrim = 0.34, textPos = "top" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { color, bodyFont, headlineFont, width, safe, brand } = useTheme();

  const t = textTiming(frame, fps, 14, durFrames - 10, width * 0.012);
  const kb = kenBurns(
    frame,
    durFrames,
    brand.theme.motion.ken_burns.from,
    brand.theme.motion.ken_burns.to
  );

  const src = plate ? staticFile(`projects/TMB_001/plates/${plate}`) : null;
  const s = typeof scrim === "number" ? scrim : 0.34;

  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: color("ink_deep") }}>
      {src ? (
        <AbsoluteFill style={{ transform: `scale(${kb})`, transformOrigin: "50% 45%" }}>
          <Img src={src} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        </AbsoluteFill>
      ) : null}

      {/* scrim: يضمن نسبة تباين القراءة فوق الصورة (قاعدة الثيم) */}
      <AbsoluteFill
        style={{
          background: `linear-gradient(180deg,
            rgba(16,15,13,${Math.min(0.92, s + 0.30)}) 0%,
            rgba(16,15,13,${s * 0.30}) 42%,
            rgba(16,15,13,${s * 0.95}) 100%)`,
        }}
      />

      <AbsoluteFill
        style={{
          justifyContent: textPos === "bottom" ? "flex-end" : "flex-start",
          alignItems: "center",
          paddingTop: safe.top + width * 0.05,
          paddingBottom: textPos === "bottom" ? safe.bottom + width * 0.30 : 0,
          paddingLeft: safe.side,
          paddingRight: safe.side,
        }}
      >
        <div style={{ opacity: t.opacity, transform: `translateY(${t.translateY}px)`, textAlign: "center" }}>
          {kicker && kicker.trim() ? (
            <div
              style={{
                fontFamily: bodyFont,
                fontWeight: 700,
                fontSize: scalePx(28, width),
                letterSpacing: "0.16em",
                color: color("gold_light"),
                marginBottom: width * 0.01,
                textShadow: "0 2px 18px rgba(0,0,0,.85)",
              }}
            >
              {kicker}
            </div>
          ) : null}
          <div
            style={{
              fontFamily: headlineFont,
              fontWeight: 700,
              fontSize: scalePx(64, width),
              lineHeight: 1.45,
              color: color("parchment"),
              whiteSpace: "pre-line",
              textShadow: "0 2px 10px rgba(0,0,0,.98), 0 6px 40px rgba(0,0,0,.9)",
              paintOrder: "stroke",
              WebkitTextStroke: "0.6px rgba(0,0,0,.55)",
            }}
          >
            {title ?? ""}
          </div>
          {label ? (
            <div
              style={{
                fontFamily: bodyFont,
                fontWeight: 500,
                fontSize: scalePx(32, width),
                color: color("parchment2"),
                marginTop: width * 0.012,
                textShadow: "0 2px 14px rgba(0,0,0,.9)",
              }}
            >
              {label}
            </div>
          ) : null}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
