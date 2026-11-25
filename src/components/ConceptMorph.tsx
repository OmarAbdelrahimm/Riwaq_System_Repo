import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { useTheme } from "../engine/theme";
import { EASE, mixHex, progress, unit } from "../engine/motion";

export type Range = { t_in: number; t_out: number };

/** درجة «الخيال» الحالية 0..1 — انتقال 600ms عند حدود كل نطاق */
export const fictionAmount = (sec: number, ranges: Range[], ramp = 0.6) => {
  let k = 0;
  for (const r of ranges) {
    const a = interpolate(sec, [r.t_in, r.t_in + ramp], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE });
    const b = interpolate(sec, [r.t_out - ramp, r.t_out], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE });
    k = Math.max(k, Math.min(a, b));
  }
  return k;
};

/**
 * ConceptMorph (الإطار) — الإطار الذهبي للواقع يتحوّل إلى عنابي داخل نطاقات الخيال التاريخي،
 * مع وسم ثابت «خيال تاريخي» (شرط تحريري: لا يُقدَّم الافتراض كحقيقة أبدًا).
 */
export const ConceptFrame: React.FC<{ ranges: Range[]; tag?: string }> = ({ ranges, tag = "خيال تاريخي" }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const { color, bodyFont, safe } = useTheme();
  const u = unit(width, height);
  const k = fictionAmount(frame / fps, ranges);
  const inset = width * 0.028;
  const stroke = mixHex(color("gold"), color("burgundy"), k);
  return (
    <AbsoluteFill>
      <AbsoluteFill
        style={{
          margin: inset,
          border: `${Math.max(1, width * 0.0012) + 3 * u * k}px solid ${stroke}${k > 0.01 ? "" : "55"}`,
          borderRadius: width * 0.006,
        }}
      />
      {k > 0.001 ? (
        <div
          style={{
            position: "absolute",
            top: Math.max(safe.top * 0.5, inset + 24 * u),
            right: safe.side + 10 * u,
            opacity: k,
            background: color("burgundy"),
            color: color("parchment"),
            fontFamily: bodyFont,
            fontWeight: 700,
            fontSize: 28 * u,
            padding: `${6 * u}px ${18 * u}px`,
            borderRadius: 4 * u,
            direction: "rtl",
          }}
        >
          {tag}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

/**
 * ConceptMorph (مشهد) — الصورة نفسها في العالمين: نسخة الواقع (دافئة/ذهبية) تتحوّل بمسح RTL
 * إلى نسخة الخيال (إطار وصبغة عنابية) خلال 600ms عند `at`.
 */
export const ConceptMorph: React.FC<{
  src: string;
  at: number;
  labelA?: string;
  labelB?: string;
  durFrames: number;
}> = ({ src, at, labelA = "الواقع", labelB = "الخيال", durFrames }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const { color, bodyFont, safe } = useTheme();
  const u = unit(width, height);
  const k = progress(frame, fps, at, at + 0.6);
  const scale = 1 + 0.06 * (frame / Math.max(1, durFrames));
  const img: React.CSSProperties = { width: "100%", height: "100%", objectFit: "cover", transform: `scale(${scale})` };
  const chip = (txt: string, bg: string, side: "right" | "left", o: number) => (
    <div
      style={{
        position: "absolute",
        bottom: safe.bottom + 40 * u,
        [side]: safe.side + 20 * u,
        opacity: o,
        background: bg,
        color: color("parchment"),
        fontFamily: bodyFont,
        fontWeight: 700,
        fontSize: 30 * u,
        padding: `${6 * u}px ${18 * u}px`,
        borderRadius: 4 * u,
      } as React.CSSProperties}
    >
      {txt}
    </div>
  );
  return (
    <AbsoluteFill>
      <AbsoluteFill>
        <Img src={staticFile(src)} style={{ ...img, filter: "sepia(0.25) saturate(1.05)" }} />
        <AbsoluteFill style={{ background: color("gold"), mixBlendMode: "soft-light" as any, opacity: 0.35 }} />
      </AbsoluteFill>
      <AbsoluteFill style={{ clipPath: `inset(0 0 0 ${100 - k * 100}%)` }}>
        <Img src={staticFile(src)} style={{ ...img, filter: "saturate(0.6) brightness(0.8)" }} />
        <AbsoluteFill style={{ background: color("burgundy"), mixBlendMode: "multiply" as any, opacity: 0.55 }} />
      </AbsoluteFill>
      {k > 0 && k < 1 ? (
        <div style={{ position: "absolute", top: 0, bottom: 0, right: `${k * 100}%`, width: 2 * u, background: color("gold_light") }} />
      ) : null}
      {chip(labelA, `${color("ink_deep")}E6`, "left", 1 - k * 0.6)}
      {chip(labelB, color("burgundy"), "right", k)}
    </AbsoluteFill>
  );
};
