import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";

/* ═══════════════════════════════════════════════════════════════════════════
   shortKit — لغة الحركة الرأسية 1080×1920
   نفس هوية الرِواق، لكن إيقاع أسرع: القطع كل 1.5–2.2 ثانية،
   النص أقرب للكادر، والشاشة مليانة — مفيش فراغات سينمائية زي الطويل.
   ═══════════════════════════════════════════════════════════════════════════ */

export const W = 1080;
export const H = 1920;

/** مناطق الأمان من brand.json — 9x16_1080x1920 */
export const SAFE = {
  top: 220,
  bottom: 480,
  side: 64,
  captionY: [1210, 1360] as [number, number],
};

export const C = {
  gold: "#C2A469",
  goldLight: "#C2A469",
  goldDeep: "#A98A4B",
  parch: "#F3EBDB",
  parch2: "#EDE6D6",
  ink: "#1C1B19",
  burgundy: "#5E2230",
  stone: "#8A7F6B",
  stoneLight: "#B9AE94",
};

export const ip = (f: number, a: number, b: number, v1: number, v2: number) =>
  interpolate(f, [a, b], [v1, v2], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

/* ── الخلفية الداكنة ────────────────────────────────────────────────────── */
export const Backdrop: React.FC<{ tint?: "warm" | "cold" | "deep" }> = ({ tint = "warm" }) => {
  const g =
    tint === "cold"
      ? "radial-gradient(ellipse 70% 44% at 50% 34%, #23262a 0%, #14161a 52%, #08090b 100%)"
      : tint === "deep"
      ? "radial-gradient(ellipse 66% 42% at 50% 36%, #1a1512 0%, #12100e 54%, #060505 100%)"
      : "radial-gradient(ellipse 68% 46% at 50% 38%, #332a1b 0%, #1b1814 52%, #0b0a09 100%)";
  return (
    <AbsoluteFill style={{ backgroundColor: C.ink, overflow: "hidden" }}>
      <AbsoluteFill style={{ background: g }} />
      <div
        style={{
          position: "absolute",
          left: "-14%",
          top: "6%",
          width: 900,
          height: 900,
          background: `radial-gradient(ellipse, ${C.gold}42 0%, ${C.goldDeep}18 48%, ${C.goldDeep}00 74%)`,
          filter: "blur(42px)",
        }}
      />
      <div
        style={{
          position: "absolute",
          right: "-20%",
          bottom: "8%",
          width: 760,
          height: 760,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${C.burgundy}50 0%, ${C.burgundy}00 72%)`,
          filter: "blur(54px)",
        }}
      />
    </AbsoluteFill>
  );
};

/* ── حبيبات الفيلم ──────────────────────────────────────────────────────── */
export const Grain: React.FC<{ amt?: number }> = ({ amt = 0.11 }) => {
  const f = useCurrentFrame();
  // بذرة تتغير كل فريم — حبيبات متحركة بدون صور
  let seed = (f * 9301 + 49297) % 233280;
  const rnd = () => (seed = (seed * 9301 + 49297) % 233280) / 233280;
  const dots = Array.from({ length: 220 }, () => ({
    x: rnd() * 100,
    y: rnd() * 100,
    s: 0.7 + rnd() * 1.5,
    o: 0.15 + rnd() * 0.5,
  }));
  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity: amt }}>
      {dots.map((d, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: `${d.x}%`,
            top: `${d.y}%`,
            width: d.s,
            height: d.s,
            borderRadius: "50%",
            background: "#fff",
            opacity: d.o,
          }}
        />
      ))}
    </AbsoluteFill>
  );
};

/* ── فينييت ─────────────────────────────────────────────────────────────── */
export const Vignette: React.FC = () => (
  <AbsoluteFill
    style={{
      pointerEvents: "none",
      background: "radial-gradient(ellipse 76% 62% at 50% 46%, transparent 34%, rgba(0,0,0,.82) 100%)",
    }}
  />
);

/* ── شريط ترقيم زمني (إيقاع الشورت) ─────────────────────────────────────── */
export const TimeBar: React.FC<{ total: number; accent?: string }> = ({ total, accent = C.gold }) => {
  const f = useCurrentFrame();
  const p = Math.max(0, Math.min(1, f / Math.max(1, total)));
  return (
    <div
      style={{
        position: "absolute",
        top: 132,
        left: SAFE.side,
        right: SAFE.side,
        height: 3,
        borderRadius: 2,
        background: "rgba(255,255,255,.09)",
        overflow: "hidden",
      }}
    >
      <div style={{ width: `${p * 100}%`, height: "100%", background: accent, boxShadow: `0 0 12px ${accent}` }} />
    </div>
  );
};

/* ── شعار رِواق ─────────────────────────────────────────────────────────── */
export const Logo: React.FC<{ delay?: number; small?: boolean }> = ({ delay = 6, small }) => {
  const f = useCurrentFrame();
  const o = ip(f, delay, delay + 26, 0, 1);
  const y = ip(f, delay, delay + 26, 10, 0);
  const s = small ? 0.72 : 1;
  return (
    <div
      style={{
        position: "absolute",
        top: SAFE.top - 96,
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        gap: 12 * s,
        opacity: o,
        transform: `translateY(${y}px) scale(${s})`,
      }}
    >
      <div style={{ fontFamily: "Amiri", fontWeight: 700, fontSize: 44, color: C.parch, letterSpacing: "0.02em" }}>
        رِواق
      </div>
      <div
        style={{
          width: 7,
          height: 7,
          borderRadius: "50%",
          background: C.goldLight,
          boxShadow: `0 0 12px ${C.goldLight}`,
        }}
      />
    </div>
  );
};

/* ── كارت صورة يدخل من تحت ──────────────────────────────────────────────── */
export const Plate: React.FC<{
  src: string;
  from: number;
  w?: number;
  h?: number;
  x?: number;
  y?: number;
  kb?: [number, number];
  rot?: number;
  radius?: number;
  grad?: number;
}> = ({ src, from, w = W, h = H, x, y, kb = [1.02, 1.10], rot = 0, radius = 0, grad = 0.5 }) => {
  const f = useCurrentFrame();
  const t = Math.max(0, f - from);
  const inO = ip(f, from, from + 14, 0, 1);
  const inY = ip(f, from, from + 20, 46, 0);
  const inS = ip(f, from, from + 22, 0.94, 1);
  // ken burns خطي على طول ظهور المشهد
  const live = Math.min(1, t / 90);
  const scale = kb[0] + (kb[1] - kb[0]) * live;
  const cx = x ?? W / 2;
  const cy = y ?? H / 2;
  return (
    <div
      style={{
        position: "absolute",
        left: cx - w / 2,
        top: cy - h / 2,
        width: w,
        height: h,
        borderRadius: radius,
        overflow: "hidden",
        opacity: inO,
        transform: `translateY(${inY}px) scale(${inS}) rotate(${rot}deg)`,
        boxShadow: "0 40px 120px rgba(0,0,0,.72)",
        border: "1px solid rgba(255,255,255,.10)",
      }}
    >
      <Img
        src={staticFile(src)}
        style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${scale})` }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `linear-gradient(180deg, rgba(0,0,0,${grad * 0.32}) 0%, transparent 38%, rgba(0,0,0,${grad}) 100%)`,
        }}
      />
    </div>
  );
};

/* ── عنوان ضخم — سطرين كحد أقصى ─────────────────────────────────────────── */
export const BigTitle: React.FC<{
  text: string;
  from: number;
  size?: number;
  color?: string;
  align?: "right" | "center";
  y?: number;
  weight?: number;
  glow?: boolean;
}> = ({ text, from, size = 92, color = C.parch, align = "center", y, weight = 700, glow = false }) => {
  const f = useCurrentFrame();
  const o = ip(f, from, from + 12, 0, 1);
  const rise = ip(f, from, from + 16, 34, 0);
  const sc = ip(f, from, from + 18, 0.97, 1);
  return (
    <div
      style={{
        position: "absolute",
        ...(y !== undefined ? { top: y } : { top: 500, left: 0, right: 0 }),
        ...(y === undefined ? {} : { left: 0, right: 0 }),
        display: "flex",
        justifyContent: align === "center" ? "center" : "flex-end",
        paddingLeft: align === "right" ? 0 : 0,
        paddingRight: align === "right" ? SAFE.side : 0,
        direction: "rtl",
        opacity: o,
        transform: `translateY(${rise}px) scale(${sc})`,
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          fontFamily: "Amiri",
          fontWeight: weight,
          fontSize: size,
          lineHeight: 1.14,
          color,
          textAlign: align,
          maxWidth: W - SAFE.side * 2,
          textShadow: glow
            ? `0 0 90px ${C.goldDeep}cc, 0 10px 60px rgba(0,0,0,1)`
            : "0 4px 30px rgba(0,0,0,.92)",
          whiteSpace: "pre-line",
        }}
      >
        {text}
      </div>
    </div>
  );
};

/* ── رقم عملاق ──────────────────────────────────────────────────────────── */
export const BigNumber: React.FC<{
  value: string;
  from: number;
  size?: number;
  color?: string;
  label?: string;
  labelColor?: string;
  y?: number;
}> = ({ value, from, size = 300, color = C.gold, label, labelColor = C.parch, y }) => {
  const f = useCurrentFrame();
  const o = ip(f, from, from + 10, 0, 1);
  const sc = ip(f, from, from + 20, 0.82, 1);
  const boost = ip(f, from, from + 9, 1.12, 1);
  return (
    <div
      style={{
        position: "absolute",
        ...(y !== undefined ? { top: y } : { top: 0, bottom: 0 }),
        left: 0,
        right: 0,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        opacity: o,
        transform: `scale(${sc * boost})`,
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          fontFamily: "Amiri",
          fontWeight: 700,
          fontSize: size,
          lineHeight: 0.92,
          color,
          textShadow: `0 0 130px ${C.goldDeep}dd, 0 0 60px rgba(0,0,0,.9), 0 12px 70px rgba(0,0,0,1)`,
        }}
      >
        {value}
      </div>
      {label && (
        <div
          style={{
            fontFamily: "IBM Plex Sans Arabic",
            fontWeight: 700,
            fontSize: 52,
            color: labelColor,
            marginTop: 12,
            textShadow: "0 2px 20px rgba(0,0,0,.95)",
          }}
        >
          {label}
        </div>
      )}
    </div>
  );
};

/* ── سطر مفتاحي (زي كابشن لكن أثقل) ────────────────────────────────────── */
export const KeyLine: React.FC<{
  text: string;
  from: number;
  to?: number;
  size?: number;
  color?: string;
  y?: number;
  align?: "right" | "center";
}> = ({ text, from, to, size = 62, color = C.parch, y, align = "center" }) => {
  const f = useCurrentFrame();
  const o = to === undefined ? ip(f, from, from + 10, 0, 1) : ip(f, from, from + 10, 0, 1) * ip(f, to - 8, to, 1, 0);
  const rise = ip(f, from, from + 16, 26, 0);
  return (
    <div
      style={{
        position: "absolute",
        ...(y !== undefined ? { top: y } : { bottom: SAFE.bottom + 40 }),
        left: SAFE.side,
        right: SAFE.side,
        direction: "rtl",
        display: "flex",
        justifyContent: align === "center" ? "center" : "flex-end",
        opacity: o,
        transform: `translateY(${rise}px)`,
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          fontFamily: "IBM Plex Sans Arabic",
          fontWeight: 700,
          fontSize: size,
          lineHeight: 1.35,
          color,
          textAlign: align,
          maxWidth: W - SAFE.side * 2,
          textShadow: "0 3px 24px rgba(0,0,0,.95)",
        }}
      >
        {text}
      </div>
    </div>
  );
};

/* ── نقطة ذهبية فاصلة ───────────────────────────────────────────────────── */
export const Dot: React.FC<{ from: number }> = ({ from }) => {
  const f = useCurrentFrame();
  const o = ip(f, from, from + 8, 0, 1);
  const s = ip(f, from, from + 14, 0.4, 1);
  return (
    <div style={{ position: "absolute", top: 1180, left: 0, right: 0, display: "flex", justifyContent: "center", opacity: o }}>
      <div
        style={{
          width: 12,
          height: 12,
          borderRadius: "50%",
          background: C.goldLight,
          transform: `scale(${s})`,
          boxShadow: `0 0 22px ${C.goldLight}`,
        }}
      />
    </div>
  );
};

/* ── لقطة قطع سريع: فلاش ذهبي رفيع بدل الوميض الممنوع ──────────────────── */
export const Seam: React.FC<{ at: number; strong?: boolean }> = ({ at, strong }) => {
  const f = useCurrentFrame();
  const o = ip(f, at, at + 2, strong ? 0.5 : 0.28, 0) + ip(f, at - 2, at, 0, strong ? 0.5 : 0.28);
  if (f < at - 2 || f > at + 3) return null;
  return <AbsoluteFill style={{ background: C.goldLight, opacity: o, pointerEvents: "none" }} />;
};

/* ── CTA نهائي: يشير للحلقة الطويلة ─────────────────────────────────────── */
export const CTA: React.FC<{ from: number }> = ({ from }) => {
  const f = useCurrentFrame();
  const o = ip(f, from, from + 16, 0, 1);
  const rise = ip(f, from, from + 20, 30, 0);
  const glow = 0.55 + 0.45 * Math.sin((f - from) / 9);
  return (
    <div
      style={{
        position: "absolute",
        bottom: SAFE.bottom - 40,
        left: SAFE.side,
        right: SAFE.side,
        display: "flex",
        justifyContent: "center",
        opacity: o,
        transform: `translateY(${rise}px)`,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 18,
          padding: "22px 46px",
          borderRadius: 999,
          border: `1.5px solid ${C.goldLight}${Math.round(120 + glow * 90).toString(16)}`,
          background: `linear-gradient(140deg, ${C.goldLight}1f, ${C.goldDeep}08)`,
          boxShadow: `0 0 ${28 + glow * 26}px ${C.goldLight}55`,
        }}
      >
        <div style={{ fontFamily: "IBM Plex Sans Arabic", fontWeight: 700, fontSize: 44, color: C.parch }}>
          الحلقة كاملة · ٤:٤٨
        </div>
        <div style={{ fontFamily: "IBM Plex Sans Arabic", fontWeight: 700, fontSize: 44, color: C.goldLight }}>
          ▶
        </div>
      </div>
    </div>
  );
};
