import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { useTheme, scalePx } from "../engine/theme";
import { textTiming, kenBurns } from "../engine/timing";

/**
 * H — إطار الخلفية البصرية (`broll`).
 *
 * قرار تصميمي: لا نستخدم صورًا خارجية (تكلفة حقوق + خطر أسلوب دخيل).
 * كل «لوحة» هنا تُبنى من عناصر المتجهات داخل اللوحة العشرية للهوية:
 * ذهبي رفيع + عاجي + فحمي، بلا تدرّجات لونية جديدة.
 *
 * الحركة الوحيدة المسموحة: ken_burns من الثيم + تلاشٍ. لا وميض، لا دوران، لا bounce.
 */
export type BrollMotif = "map" | "fall" | "drums" | "route";

export const BrollFrame: React.FC<{
  title?: string;
  label?: string;
  kicker?: string;
  motif?: BrollMotif;
  durFrames: number;
}> = ({ title, label, kicker, motif = "map", durFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { color, bodyFont, headlineFont, width, height, safe, brand } = useTheme();

  const t = textTiming(frame, fps, 12, durFrames - 10, width * 0.012);
  const kb = kenBurns(
    frame,
    durFrames,
    brand.theme.motion.ken_burns.from,
    brand.theme.motion.ken_burns.to
  );
  const gold = color("gold");
  const goldLight = color("gold_light");
  const parchment = color("parchment");
  const stone = color("stone_light");

  // مساحة الرسم: بين المنطقة الآمنة أعلى وأسفل
  const artTop = safe.top + width * 0.02;
  const artH = height - safe.top - safe.bottom - width * 0.08;

  const progress = Math.min(1, frame / Math.max(1, durFrames));

  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <AbsoluteFill style={{ transform: `scale(${kb})`, transformOrigin: "50% 45%" }}>
        <svg
          width={width}
          height={height}
          viewBox={`0 0 ${width} ${height}`}
          style={{ position: "absolute", inset: 0 }}
        >
          {/* قاعدة: شبكة رملية خفيفة = «ورق» لا خلفية فوتوغرافية */}
          {motif === "map" && (
            <>
              <rect x={0} y={0} width={width} height={height} fill="transparent" />
              {Array.from({ length: 14 }).map((_, r) =>
                Array.from({ length: 9 }).map((__, c) => (
                  <circle
                    key={`${r}-${c}`}
                    cx={safe.side + c * ((width - safe.side * 2) / 8)}
                    cy={artTop + r * (artH / 13)}
                    r={1.6}
                    fill={stone}
                    opacity={0.16}
                  />
                ))
              )}
              {/* دبوس ذهبي + حلقة تتنفّس (لا وميض) */}
              <g>
                <circle cx={width / 2} cy={artTop + artH * 0.42} r={width * 0.055}
                  fill="none" stroke={gold} strokeWidth={1.5}
                  opacity={0.12 + 0.22 * Math.min(1, progress * 1.6)} />
                <circle cx={width / 2} cy={artTop + artH * 0.42} r={width * 0.012} fill={goldLight} />
                <line x1={width / 2 - width * 0.18} y1={artTop + artH * 0.42}
                  x2={width / 2 + width * 0.18} y2={artTop + artH * 0.42}
                  stroke={gold} strokeWidth={1} opacity={0.5} />
              </g>
            </>
          )}

          {motif === "fall" && (
            <>
              {/* أشرطة عمودية = ظلّ سقوط، وخيط ذهبي ينحدر بلا دوران */}
              {[0.22, 0.42, 0.62, 0.8].map((p, i) => (
                <rect key={i} x={width * p - 1} y={artTop} width={2}
                  height={artH} fill={stone} opacity={0.08} />
              ))}
              <line
                x1={width * 0.3}
                y1={artTop + artH * (0.12 + 0.55 * Math.min(1, progress * 1.4))}
                x2={width * 0.7}
                y2={artTop + artH * (0.06 + 0.55 * Math.min(1, progress * 1.4))}
                stroke={gold}
                strokeWidth={2}
                opacity={0.75}
              />
              <circle cx={width * 0.7} cy={artTop + artH * (0.06 + 0.55 * Math.min(1, progress * 1.4))}
                r={4} fill={goldLight} />
            </>
          )}

          {motif === "drums" && (
            <>
              {[0, 1, 2].map((i) => {
                const w = width * 0.2;
                const h = width * 0.085;
                const x = width / 2 - w * 1.55 + i * (w + width * 0.05);
                const rise = (1 - Math.min(1, Math.max(0, progress * 1.8 - i * 0.18))) * 26;
                return (
                  <g key={i} transform={`translate(0, ${rise})`} opacity={1 - i * 0.08}>
                    <rect x={x} y={artTop + artH * 0.5} width={w} height={h} rx={w * 0.06}
                      fill="none" stroke={gold} strokeWidth={1.5} opacity={0.85} />
                    <line x1={x + w * 0.12} y1={artTop + artH * 0.5 + h * 0.34}
                      x2={x + w * 0.88} y2={artTop + artH * 0.5 + h * 0.34}
                      stroke={stone} strokeWidth={1} opacity={0.4} />
                  </g>
                );
              })}
            </>
          )}

          {motif === "route" && (
            <>
              {/* مسار ذهبي متحرك: نقطة تسير على خط مكسور */}
              <polyline
                points={[
                  [width * 0.26, artTop + artH * 0.22],
                  [width * 0.44, artTop + artH * 0.4],
                  [width * 0.5, artTop + artH * 0.58],
                  [width * 0.66, artTop + artH * 0.76],
                ]
                  .map((p) => p.join(","))
                  .join(" ")}
                fill="none"
                stroke={gold}
                strokeWidth={2}
                opacity={0.55}
              />
              {[
                [0.26, 0.22],
                [0.66, 0.76],
              ].map(([px, py], i) => (
                <circle key={i} cx={width * px} cy={artTop + artH * py} r={5}
                  fill={i === 0 ? stone : goldLight} />
              ))}
              <circle
                cx={width * (0.26 + 0.4 * Math.min(1, progress * 1.15))}
                cy={artTop + artH * (0.22 + 0.54 * Math.min(1, progress * 1.15))}
                r={6}
                fill={goldLight}
              />
            </>
          )}
        </svg>
      </AbsoluteFill>

      {/* الطبقة النصية: كيكر صغير + عنوان Amiri + سطر شرح */}
      <AbsoluteFill
        style={{
          justifyContent: "flex-start",
          alignItems: "center",
          paddingTop: safe.top + width * 0.06,
          paddingLeft: safe.side,
          paddingRight: safe.side,
        }}
      >
        <div
          style={{
            opacity: t.opacity,
            transform: `translateY(${t.translateY}px)`,
            textAlign: "center",
          }}
        >
          {kicker ? (
            <div
              style={{
                fontFamily: bodyFont,
                fontWeight: 700,
                fontSize: scalePx(28, width),
                letterSpacing: "0.16em",
                color: goldLight,
                marginBottom: width * 0.012,
              }}
            >
              {kicker}
            </div>
          ) : null}
          <div
            style={{
              fontFamily: headlineFont,
              fontWeight: 700,
              fontSize: scalePx(62, width),
              lineHeight: 1.5,
              color: parchment,
              whiteSpace: "pre-line",
            }}
          >
            {title ?? ""}
          </div>
          {label ? (
            <div
              style={{
                fontFamily: bodyFont,
                fontWeight: 500,
                fontSize: scalePx(34, width),
                color: stone,
                marginTop: width * 0.014,
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
