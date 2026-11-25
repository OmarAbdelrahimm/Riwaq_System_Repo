import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { useTheme } from "../engine/theme";
import { inOut, progress, unit } from "../engine/motion";

type LL = [number, number]; // [lon, lat]
type Tone = "gold" | "burgundy" | "stone" | "parchment";

const TIGRIS: LL[] = [[42.6, 37.2], [43.1, 36.35], [43.5, 35.4], [43.87, 34.2], [44.4, 33.33], [45.0, 32.7], [45.8, 32.2], [46.6, 31.6], [47.2, 31.05], [47.8, 30.6], [48.4, 30.0]];
const EUPHRATES: LL[] = [[38.4, 37.0], [38.9, 36.2], [39.6, 35.8], [40.5, 35.0], [41.4, 34.4], [42.4, 34.1], [43.4, 33.45], [44.0, 32.9], [44.42, 32.47], [44.4, 32.0], [45.2, 31.4], [46.3, 31.0], [47.3, 31.0], [47.9, 30.6]];

/**
 * خريطة توضيحية مبسّطة (إسقاط متساوي المسافات مصحّح بخط العرض) — بلا سواحل، رمزية فقط.
 * الخطوط تُرسم تدريجيًا (MapDraw)، والماء انتشار دائري بلون حجري شفاف (ضمن الباليت).
 */
export const MapSchematic: React.FC<{
  bbox: [number, number, number, number]; // lon0, lat0, lon1, lat1
  points?: { label: string; lon: number; lat: number; tone?: Tone; at?: number; anchor?: "r" | "l" | "t" | "b"; big?: boolean }[];
  lines?: { path: LL[]; tone?: Tone; at?: number; dur?: number; dashed?: boolean; width?: number; arrow?: boolean }[];
  rivers?: boolean;
  water?: { lon: number; lat: number; r: number; at: number; dur: number; freeze?: number };
  title?: string;
  durFrames: number;
}> = ({ bbox, points = [], lines = [], rivers = true, water, title, durFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { color, bodyFont, headlineFont, width, height, safe } = useTheme();
  const u = unit(width, height);
  const t = inOut(frame, durFrames, fps, 0);
  const sec = frame / fps;
  const [lon0, lat0, lon1, lat1] = bbox;
  const midLat = ((lat0 + lat1) / 2) * (Math.PI / 180);
  const kx = Math.cos(midLat);
  const padT = safe.top + 190 * u;
  const padB = safe.bottom + 90 * u;
  const W = width - safe.side * 2 - 80 * u;
  const H = height - padT - padB;
  const sw = (lon1 - lon0) * kx;
  const sh = lat1 - lat0;
  const sc = Math.min(W / sw, H / sh);
  const ox = (width - sw * sc) / 2;
  const oy = padT + (H - sh * sc) / 2;
  const P = ([lon, lat]: LL) => [ox + (lon - lon0) * kx * sc, oy + (lat1 - lat) * sc] as [number, number];
  const tone = (tn: Tone = "gold") =>
    tn === "burgundy" ? color("burgundy") : tn === "stone" ? color("stone_light") : tn === "parchment" ? color("parchment") : color("gold_light");

  const pathD = (pts: LL[]) => pts.map((p, i) => `${i ? "L" : "M"} ${P(p)[0].toFixed(1)} ${P(p)[1].toFixed(1)}`).join(" ");
  const plen = (pts: LL[]) => {
    let L = 0;
    for (let i = 1; i < pts.length; i++) {
      const a = P(pts[i - 1]);
      const b = P(pts[i]);
      L += Math.hypot(b[0] - a[0], b[1] - a[1]);
    }
    return L;
  };

  const grat: React.ReactNode[] = [];
  for (let lo = Math.ceil(lon0 / 5) * 5; lo <= lon1; lo += 5) {
    const [x] = P([lo, lat0]);
    grat.push(<line key={`lo${lo}`} x1={x} x2={x} y1={oy} y2={oy + sh * sc} stroke={color("stone")} strokeOpacity={0.12} strokeWidth={1} />);
  }
  for (let la = Math.ceil(lat0 / 5) * 5; la <= lat1; la += 5) {
    const [, y] = P([lon0, la]);
    grat.push(<line key={`la${la}`} x1={ox} x2={ox + sw * sc} y1={y} y2={y} stroke={color("stone")} strokeOpacity={0.12} strokeWidth={1} />);
  }

  let waterEl: React.ReactNode = null;
  if (water) {
    const k0 = progress(frame, fps, water.at, water.at + water.dur);
    const k = water.freeze !== undefined ? Math.min(k0, water.freeze) : k0; // freeze = نسبة 0..1 يتجمّد عندها الماء
    const [cx, cy] = P([water.lon, water.lat]);
    waterEl = <circle cx={cx} cy={cy} r={water.r * sc * k} fill={color("stone_light")} fillOpacity={0.28} stroke={color("stone_light")} strokeOpacity={0.5} />;
  }

  return (
    <AbsoluteFill style={{ opacity: t.opacity }}>
      <svg width={width} height={height} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <marker id="arrowG" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill={color("gold_light")} />
          </marker>
          <marker id="arrowB" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill={color("burgundy")} />
          </marker>
        </defs>
        {grat}
        {rivers ? (
          <g opacity={progress(frame, fps, 0, 1)}>
            <path d={pathD(TIGRIS)} stroke={color("stone_light")} strokeOpacity={0.55} strokeWidth={2.5 * u} fill="none" />
            <path d={pathD(EUPHRATES)} stroke={color("stone_light")} strokeOpacity={0.55} strokeWidth={2.5 * u} fill="none" />
          </g>
        ) : null}
        {waterEl}
        {lines.map((ln, i) => {
          const L = plen(ln.path);
          const k = progress(frame, fps, ln.at ?? 0.4, (ln.at ?? 0.4) + (ln.dur ?? 1.6));
          const c = tone(ln.tone);
          return (
            <path
              key={i}
              d={pathD(ln.path)}
              stroke={c}
              strokeWidth={(ln.width ?? 3) * u}
              fill="none"
              strokeLinecap="round"
              strokeDasharray={ln.dashed ? `${10 * u} ${8 * u}` : `${L} ${L}`}
              strokeDashoffset={ln.dashed ? 0 : L * (1 - k)}
              opacity={ln.dashed ? k : 1}
              markerEnd={ln.arrow && k > 0.98 ? (ln.tone === "burgundy" ? "url(#arrowB)" : "url(#arrowG)") : undefined}
            />
          );
        })}
        {points.map((p, i) => {
          const k = progress(frame, fps, p.at ?? 0.2, (p.at ?? 0.2) + 0.38);
          const [x, y] = P([p.lon, p.lat]);
          const a = p.anchor ?? "l";
          const dx = a === "l" ? -18 * u : a === "r" ? 18 * u : 0;
          const dy = a === "t" ? -22 * u : a === "b" ? 40 * u : 10 * u;
          const anchor = a === "l" ? "start" : a === "r" ? "end" : "middle"; // RTL: start = الحافة اليمنى للنص
          const c = tone(p.tone);
          return (
            <g key={i} opacity={k} transform={`translate(0 ${(1 - k) * 12 * u})`}>
              <circle cx={x} cy={y} r={(p.big ? 11 : 7) * u} fill={c} />
              {p.big ? <circle cx={x} cy={y} r={20 * u} fill="none" stroke={c} strokeOpacity={0.6} strokeWidth={1.5 * u} /> : null}
              <text
                x={x + dx}
                y={y + dy}
                fill={color("parchment")}
                fontFamily={bodyFont}
                fontWeight={p.big ? 700 : 500}
                fontSize={(p.big ? 38 : 30) * u}
                textAnchor={anchor}
                style={{ paintOrder: "stroke", stroke: color("ink_deep"), strokeWidth: 6 * u } as any}
              >
                {p.label}
              </text>
            </g>
          );
        })}
      </svg>
      {title ? (
        <div
          style={{
            position: "absolute",
            top: safe.top + 110 * u,
            right: safe.side + 30 * u,
            fontFamily: headlineFont,
            fontWeight: 700,
            fontSize: 48 * u,
            color: color("gold_light"),
            direction: "rtl",
          }}
        >
          {title}
        </div>
      ) : null}
      <div
        style={{
          position: "absolute",
          bottom: safe.bottom + 20 * u,
          left: safe.side + 20 * u,
          fontFamily: bodyFont,
          fontSize: 20 * u,
          color: color("stone"),
          direction: "rtl",
        }}
      >
        خريطة توضيحية تقريبية
      </div>
    </AbsoluteFill>
  );
};
