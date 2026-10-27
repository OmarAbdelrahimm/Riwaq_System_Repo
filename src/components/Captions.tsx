import React from "react";
import { AbsoluteFill } from "remotion";
import { useTheme, scalePx } from "../engine/theme";
import type { CaptionLine } from "../engine/types";

/**
 * كابشنز بثلاثة أنماط:
 *  - clean_bottom      : نظيف أسفل الشاشة
 *  - keyword_highlight : إبراز الكلمات المؤثرة والأرقام بالذهبي (النمط الافتراضي)
 *  - bilingual_stack   : عربي فوق (Plex Bold) + إنجليزي تحته (Plex Regular 60%)
 * الموضع دائمًا داخل نطاق الكابشنز الآمن من الثيم.
 */
export const Captions: React.FC<{
  line: CaptionLine;
  style: "clean_bottom" | "keyword_highlight" | "bilingual_stack";
}> = ({ line, style }) => {
  const { brand, color, bodyFont, safe, width } = useTheme();
  const [y0, y1] = safe.captionY;
  const fontSize = scalePx(56, width);
  const enSize = fontSize * 0.6;

  /**
   * لوحة السطوع التكيفية (استثناء مضبوط في الثيم: theme.captions.scrim).
   * القرار يأتي من `scrim_map.json` (لكل مشهد) عبر `line.luma`/`line.scrim`،
   * وليس من كود ثابت: الكادر اللي مفيهوش قياس ولا تجاوز ⇒ بلا لوحة.
   * اللوحة مسطّحة دائمًا (لا تدرّج)، والشفافية تتدرّج من القراءة لا من الجمال.
   */
  const scrimCfg = (brand.theme.captions && brand.theme.captions.scrim) || {};
  const threshold = typeof scrimCfg.threshold === "number" ? scrimCfg.threshold : 0.46;
  const opacityMax = typeof scrimCfg.opacity_max === "number" ? scrimCfg.opacity_max : 0.72;
  const opacityMin = typeof scrimCfg.opacity_min === "number" ? scrimCfg.opacity_min : 0.35;
  const scrimOn =
    line.scrim === true ||
    (line.scrim === undefined && typeof line.luma === "number" && line.luma > threshold);

  const scrimAlpha = (() => {
    if (!scrimOn) return 0;
    if (typeof line.luma !== "number") return opacityMax;
    const t = Math.min(1, Math.max(0, (line.luma - threshold) / (1 - threshold)));
    return Math.min(opacityMax, opacityMin + t * (opacityMax - opacityMin));
  })();

  const renderAr = () => {
    if (style !== "keyword_highlight" || !line.keywords?.length) return line.ar;
    const parts: React.ReactNode[] = [];
    let rest = line.ar;
    line.keywords.forEach((kw, i) => {
      const idx = rest.indexOf(kw);
      if (idx === -1) return;
      parts.push(rest.slice(0, idx));
      parts.push(
        <span key={i} style={{ color: color("gold_light") }}>
          {kw}
        </span>
      );
      rest = rest.slice(idx + kw.length);
    });
    parts.push(rest);
    return parts;
  };

  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start" }}>
      <div
        style={{
          position: "absolute",
          top: (y0 + y1) / 2,
          transform: "translateY(-50%)",
          maxWidth: width - safe.side * 2,
          textAlign: "center",
        }}
      >
        <div
          style={{
            display: "inline-block",
            background: scrimOn ? `rgba(15, 14, 12, ${scrimAlpha})` : "transparent",
            border: scrimOn ? `1px solid ${color("gold")}22` : "1px solid transparent",
            borderRadius: width * 0.009,
            padding: `${width * 0.012}px ${width * 0.02}px`,
          }}
        >
          <div
            style={{
              fontFamily: bodyFont,
              fontWeight: 700,
              fontSize,
              color: color("parchment"),
              lineHeight: 1.42,
            }}
          >
            {renderAr()}
          </div>
          {style === "bilingual_stack" && line.en ? (
            <div
              style={{
                fontFamily: bodyFont,
                fontWeight: 400,
                fontSize: enSize,
                color: color("stone_light"),
                marginTop: width * 0.006,
                direction: "ltr",
              }}
            >
              {line.en}
            </div>
          ) : null}
        </div>
      </div>
    </AbsoluteFill>
  );
};
