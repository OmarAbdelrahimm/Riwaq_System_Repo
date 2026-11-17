import React from "react";
import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame } from "remotion";

/* ═══════════════════════════════════════════════════════════════════════════
   kit — لغة الحركة المشتركة للنموذج الطويل والشورتات
   نفس مفردات برهان v5: عمق 3D · زجاج · rim light · كاميرا سينمائية.
   ═══════════════════════════════════════════════════════════════════════════ */

export const C = {
  gold: "#C2A469",
  goldDeep: "#A98A4B",
  parch: "#F3EBDB",
  parch2: "#EDE6D6",
  ink: "#0E0D0C",
  burgundy: "#5E2230",
  olive: "#6B6A3E",
  stone: "#8A7F6B",
};

export const ip = (f: number, a: number, b: number, v1: number, v2: number) =>
  interpolate(f, [a, b], [v1, v2], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

/* ── الخلفية ─────────────────────────────────────────────────────────────── */
export const Backdrop: React.FC<{ tint?: "warm" | "cold" | "deep" }> = ({ tint = "warm" }) => {
  const g =
    tint === "cold"
      ? "radial-gradient(ellipse 64% 56% at 50% 42%, #23262a 0%, #14161a 46%, #08090b 100%)"
      : tint === "deep"
      ? "radial-gradient(ellipse 60% 52% at 50% 40%, #1a1512 0%, #12100e 48%, #060505 100%)"
      : "radial-gradient(ellipse 62% 54% at 50% 44%, #332a1b 0%, #1b1814 46%, #0b0a09 100%)";
  return (
    <AbsoluteFill style={{ backgroundColor: C.ink, overflow: "hidden" }}>
      <AbsoluteFill style={{ background: g }} />
      <div
        style={{
          position: "absolute",
          left: "22%",
          top: "2%",
          width: 1150,
          height: 760,
          background: `radial-gradient(ellipse, ${C.gold}4a 0%, ${C.goldDeep}22 46%, ${C.goldDeep}00 76%)`,
          filter: "blur(30px)",
        }}
      />
      <div
        style={{
          position: "absolute",
          right: "-16%",
          bottom: "-20%",
          width: 940,
          height: 940,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${C.burgundy}5a 0%, ${C.burgundy}00 70%)`,
          filter: "blur(48px)",
        }}
      />
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 76% 70% at 50% 46%, rgba(0,0,0,0) 32%, rgba(0,0,0,.84) 100%)",
        }}
      />
    </AbsoluteFill>
  );
};

/* ── حقل أشكال طايفة ────────────────────────────────────────────────────── */
type ShapeDef = {
  k: "ring" | "dot" | "arc" | "blob";
  x: number;
  y: number;
  s: number;
  z: number;
  c: string;
  o: number;
  sp: number;
};

export const ShapeField: React.FC<{ seed?: number; camZ?: number; amt?: number }> = ({
  seed = 0,
  camZ = 0,
  amt = 1,
}) => {
  const f = useCurrentFrame();
  const defs: ShapeDef[] = [
    { k: "ring", x: 250, y: 200, s: 200, z: -520, c: `${C.gold}44`, o: 0.5, sp: 26 },
    { k: "blob", x: 1650, y: 860, s: 500, z: -680, c: `${C.burgundy}55`, o: 0.4, sp: 34 },
    { k: "arc", x: 1520, y: 190, s: 290, z: -420, c: `${C.parch}2a`, o: 0.5, sp: 22 },
    { k: "dot", x: 1680, y: 320, s: 8, z: -230, c: C.gold, o: 0.7, sp: 18 },
    { k: "dot", x: 322, y: 742, s: 6, z: -180, c: `${C.gold}bb`, o: 0.5, sp: 20 },
    { k: "ring", x: 880, y: 950, s: 120, z: -300, c: `${C.goldDeep}3a`, o: 0.42, sp: 24 },
    { k: "blob", x: 380, y: 930, s: 400, z: -620, c: `${C.olive}44`, o: 0.28, sp: 30 },
  ];

  return (
    <AbsoluteFill style={{ transformStyle: "preserve-3d", opacity: amt }}>
      {defs.map((d, i) => {
        const s = seed + i;
        const dx = Math.sin(f / (58 + s * 9) + s) * d.sp;
        const dy = Math.cos(f / (72 + s * 7) + s * 1.4) * d.sp * 0.8;
        const sp = Math.sin(f / (90 + s * 11) + s) * 12;
        const blur = Math.max(0, (Math.abs(camZ + d.z) - 150) / 52);
        const base: React.CSSProperties = {
          position: "absolute",
          left: d.x - d.s / 2 + dx,
          top: d.y - d.s / 2 + dy,
          width: d.s,
          height: d.s,
          opacity: d.o,
          filter: blur > 0.05 ? `blur(${blur.toFixed(1)}px)` : undefined,
          transform: `translateZ(${d.z}px) rotate(${sp}deg)`,
        };
        if (d.k === "ring")
          return <div key={i} style={{ ...base, borderRadius: "50%", border: `1.5px solid ${d.c}` }} />;
        if (d.k === "dot")
          return (
            <div
              key={i}
              style={{ ...base, borderRadius: "50%", background: d.c, boxShadow: `0 0 ${d.s * 2}px ${d.c}` }}
            />
          );
        if (d.k === "arc")
          return (
            <div
              key={i}
              style={{
                ...base,
                borderRadius: "50%",
                border: "1.5px solid transparent",
                borderTopColor: d.c,
                borderRightColor: `${d.c}55`,
              }}
            />
          );
        return (
          <div
            key={i}
            style={{
              ...base,
              borderRadius: "46% 54% 58% 42% / 52% 44% 56% 48%",
              background: `radial-gradient(circle at 40% 35%, ${d.c}, ${d.c}00 72%)`,
              filter: `blur(${(blur + 22).toFixed(1)}px)`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

/* ── الزجاج ─────────────────────────────────────────────────────────────── */
export const Glass: React.FC<{
  r?: number;
  tint?: string;
  sheen?: number;
  sheenSpeed?: number;
  idx?: number;
  children?: React.ReactNode;
}> = ({ r = 22, tint = "255,255,255", sheen = 1, sheenSpeed = 0.8, idx = 0, children }) => {
  const f = useCurrentFrame();
  return (
    <>
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: r,
          overflow: "hidden",
          boxShadow:
            "0 46px 104px rgba(0,0,0,.86), 0 0 0 1px rgba(243,235,219,.10), 0 0 84px rgba(194,164,105,.13)",
          background: `linear-gradient(158deg, rgba(${tint},.19) 0%, rgba(${tint},.05) 40%, rgba(${tint},.02) 66%, rgba(${tint},.13) 100%)`,
          backdropFilter: "blur(17px) saturate(160%)",
          WebkitBackdropFilter: "blur(17px) saturate(160%)",
        }}
      >
        {children}
        <div
          style={{
            position: "absolute",
            top: "-40%",
            left: `${-60 + ((f * sheenSpeed + idx * 91) % 230)}%`,
            width: "44%",
            height: "180%",
            background:
              "linear-gradient(100deg, rgba(255,255,255,0) 0%, rgba(255,255,255,.18) 50%, rgba(255,255,255,0) 100%)",
            transform: "rotate(13deg)",
            filter: "blur(8px)",
            opacity: sheen,
          }}
        />
      </div>
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: r,
          padding: 1.5,
          background: `linear-gradient(128deg, ${C.gold}f0 0%, ${C.gold}44 18%, rgba(255,255,255,.10) 46%, ${C.burgundy}77 74%, ${C.gold}55 100%)`,
          WebkitMask: "linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0)",
          WebkitMaskComposite: "xor",
          maskComposite: "exclude",
          pointerEvents: "none",
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: r,
          boxShadow:
            "inset 0 1px 0 rgba(255,255,255,.46), inset 0 -1px 0 rgba(255,255,255,.08), inset 1px 0 0 rgba(255,255,255,.13), inset -1px 0 0 rgba(255,255,255,.13)",
          pointerEvents: "none",
        }}
      />
    </>
  );
};

/* ── غلاف عمق ───────────────────────────────────────────────────────────── */
export const DepthBox: React.FC<{
  x: number;
  y: number;
  z?: number;
  ry?: number;
  rx?: number;
  w: number;
  h: number;
  delay?: number;
  idx?: number;
  camZ?: number;
  keepSharp?: boolean;
  children: React.ReactNode;
}> = ({ x, y, z = 0, ry = 0, rx = 0, w, h, delay = 0, idx = 0, camZ = 0, keepSharp, children }) => {
  const f = useCurrentFrame();
  const s = spring({ frame: f - delay, fps: 30, config: { damping: 17, mass: 0.85, stiffness: 74 } });
  const e = ip(s, 0, 1, 0, 1);
  const bobY = Math.sin(f / 52 + idx * 1.9) * 7;
  const bobX = Math.cos(f / 68 + idx * 1.3) * 5;
  const blur = keepSharp ? 0 : Math.max(0, (Math.abs(camZ + z) - 170) / 54);

  return (
    <div
      style={{
        position: "absolute",
        left: x - w / 2,
        top: y - h / 2 + (1 - e) * 130 + bobY,
        width: w,
        height: h,
        transformStyle: "preserve-3d",
        transform: `translate3d(${bobX}px, 0px, ${z * e}px) rotateY(${ry}deg) rotateX(${rx}deg) scale(${0.92 + e * 0.08})`,
        opacity: e,
        filter: blur > 0.05 ? `blur(${blur.toFixed(2)}px)` : undefined,
      }}
    >
      {children}
    </div>
  );
};

/* ── صورة في إطار ════════════════════════════════════════════════════════ */
export const PhotoCard: React.FC<{
  src: string;
  w: number;
  h: number;
  kb?: [number, number];
  grad?: number;
  r?: number;
}> = ({ src, w, h, kb = [1.0, 1.08], grad = 0.8, r }) => {
  const f = useCurrentFrame();
  const radius = r ?? w * 0.05;
  const sc = ip(f, 0, 240, kb[0], kb[1]);
  return (
    <>
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: radius,
          overflow: "hidden",
          boxShadow: `0 50px 116px rgba(0,0,0,.9), 0 0 0 1px rgba(243,235,219,.14), 0 0 100px ${C.goldDeep}30`,
        }}
      >
        <Img
          src={staticFile(src)}
          style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${sc})` }}
        />
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: `linear-gradient(180deg, rgba(14,13,12,.04) 0%, rgba(14,13,12,${grad * 0.4}) 56%, rgba(14,13,12,${grad}) 100%)`,
          }}
        />
      </div>
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: radius,
          padding: 1.5,
          background: `linear-gradient(128deg, ${C.gold}e6 0%, ${C.gold}44 20%, rgba(255,255,255,.10) 48%, ${C.burgundy}70 76%, ${C.gold}55 100%)`,
          WebkitMask: "linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0)",
          WebkitMaskComposite: "xor",
          maskComposite: "exclude",
          pointerEvents: "none",
        }}
      />
    </>
  );
};

/* ── خط ذهبي ═════════════════════════════════════════════════════════════ */
export const Rule: React.FC<{ w: number; delay?: number; dur?: number; flip?: boolean }> = ({
  w,
  delay = 0,
  dur = 26,
  flip,
}) => {
  const f = useCurrentFrame();
  const p = ip(f, delay, delay + dur, 0, 1);
  return (
    <div
      style={{
        width: w * p,
        height: 1.5,
        background: flip
          ? `linear-gradient(90deg, ${C.goldDeep}00, ${C.gold})`
          : `linear-gradient(90deg, ${C.gold}, ${C.goldDeep}00)`,
        boxShadow: `0 0 18px ${C.gold}88`,
      }}
    />
  );
};

/* ── ظهور كلمة حركية ───────────────────────────────────────────────────── */
export const KWord: React.FC<{
  children: React.ReactNode;
  start: number;
  size: number;
  color?: string;
  weight?: number;
  family?: "Amiri" | "IBM Plex Sans Arabic";
  glow?: boolean;
}> = ({ children, start, size, color = C.parch, weight = 700, family = "Amiri", glow }) => {
  const f = useCurrentFrame();
  const p = spring({ frame: f - start, fps: 30, config: { damping: 19, mass: 0.7, stiffness: 122 } });
  return (
    <span
      style={{
        display: "inline-block",
        fontFamily: family,
        fontWeight: weight,
        fontSize: size,
        lineHeight: 1.28,
        color,
        opacity: ip(p, 0, 1, 0, 1),
        filter: `blur(${ip(p, 0, 1, 12, 0)}px)`,
        transform: `perspective(820px) translateY(${ip(p, 0, 1, 46, 0)}px) rotateX(${ip(
          p,
          0,
          1,
          -62,
          0
        )}deg)`,
        transformOrigin: "50% 100%",
        letterSpacing: `${ip(p, 0, 1, 0.11, 0)}em`,
        textShadow: glow ? `0 0 44px ${C.goldDeep}66, 0 4px 30px rgba(0,0,0,.9)` : "0 4px 30px rgba(0,0,0,.9)",
      }}
    >
      {children}
    </span>
  );
};

/* ── صف كلمات (يكسر السطر تلقائيًا RTL) ─────────────────────────────────── */
export const WordRow: React.FC<{
  words: string[];
  size: number;
  start?: number;
  gap?: number;
  color?: string;
}> = ({ words, size, start = 6, gap = 6, color }) => (
  <div style={{ display: "flex", justifyContent: "flex-end", flexWrap: "wrap", gap: `0 ${size * 0.22}px` }}>
    {words.map((w, i) => (
      <KWord key={`${w}-${i}`} start={start + i * gap} size={size} color={color}>
        {w}
      </KWord>
    ))}
  </div>
);

/* ═══ ريج المشهد: كاميرا لكل مشهد، تبدأ من الصفر ═════════════════════════ */
type CamKind = "push" | "pan" | "drift" | "orbit" | "static";

export const SceneShell: React.FC<{
  dur: number;
  kind?: CamKind;
  tint?: "warm" | "cold" | "deep";
  perspective?: number;
  children?: React.ReactNode;
  world?: React.ReactNode;
  overlay?: React.ReactNode;
  camStart?: number;
}> = ({ dur, kind = "push", tint, perspective = 1500, children, world, overlay, camStart = 0 }) => {
  const f = useCurrentFrame();
  const p = Math.max(0, Math.min(1, (f - camStart) / Math.max(1, dur - camStart)));

  let tx = 0,
    ty = 0,
    tz = 0,
    ry = 0,
    rx = 0;
  if (kind === "push") {
    tz = -120 + p * 190;
  } else if (kind === "pan") {
    tx = 90 - p * 190;
    ry = 3.4 - p * 6.2;
  } else if (kind === "drift") {
    tx = -34 + p * 68;
    ty = 18 - p * 34;
    tz = -50 + p * 70;
  } else if (kind === "orbit") {
    ry = -7 + p * 14;
    tz = -70 + p * 110;
  }
  // easing ناعم في الطرفين
  const ease = (v: number) => v * (0.78 + 0.22 * Math.sin((p * Math.PI) / 2));

  return (
    <AbsoluteFill style={{ backgroundColor: C.ink }}>
      <Backdrop tint={tint} />
      <AbsoluteFill style={{ perspective, perspectiveOrigin: "50% 46%", overflow: "hidden" }}>
        <AbsoluteFill
          style={{
            transformStyle: "preserve-3d",
            transform: `translate3d(${ease(tx)}px, ${ty}px, ${tz}px) rotateY(${ry}deg) rotateX(${rx}deg)`,
          }}
        >
          {children ?? world}
        </AbsoluteFill>
      </AbsoluteFill>
      {overlay}
    </AbsoluteFill>
  );
};

/* ── شعار رِواق ─────────────────────────────────────────────────────────── */
export const Logo: React.FC<{ delay?: number }> = ({ delay = 10 }) => {
  const f = useCurrentFrame();
  const o = ip(f, delay, delay + 30, 0, 1);
  return (
    <div style={{ position: "absolute", left: 88, top: 62, display: "flex", alignItems: "center", gap: 14, opacity: o, direction: "rtl" }}>
      <div style={{ width: 3, height: 36, borderRadius: 2, background: C.gold, boxShadow: `0 0 20px ${C.gold}` }} />
      <div style={{ fontFamily: "Amiri", fontWeight: 700, fontSize: 40, color: C.parch }}>رِواق</div>
    </div>
  );
};

/* ── توقيت مشهد (ثانية) ─────────────────────────────────────────────────── */
export type Beat = { from: number; dur: number; node: React.ReactNode };
