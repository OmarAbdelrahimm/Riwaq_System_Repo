import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

/* ═══════════════════════════════════════════════════════════════════════════
   ProofStyle v4 — برهان الستايل (6ث · 1920×1080 · 60fps)

   v3 كان ناقص: إضاءة حواف · أشكال خلفية · motion blur.
   v4:
     · ريج كاميرا أسرع (يخلي الـmotion blur يبان فعلًا)
     · rim light متدرّج على حواف كل كارت (ذهبي ← نبيذي)
     · أشكال هندسية طايفة في العمق بـparallax
     · ghosting حقيقي: العالم يُرسم 3 مرات عند tf, tf-1, tf-2
   ═══════════════════════════════════════════════════════════════════════════ */

const GOLD = "#C2A469";
const GOLD_DEEP = "#A98A4B";
const PARCH = "#F3EBDB";
const BURGUNDY = "#5E2230";
const OLIVE = "#6B6A3E";
const INK = "#0E0D0C";

const FPS = 60;
const DUR = 360;
const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const FOCUS = 0;
const SHARP_RANGE = 150;
const BLUR_K = 46;

/* ── ريج الكاميرا ────────────────────────────────────────────────────────── */
const cameraAt = (frame: number) => {
  const t = Math.max(0, Math.min(1, frame / DUR));
  // easing هادئ في البداية وسريع في النص (كاميرا «تسحب»)
  const e = t < 0.28 ? (t / 0.28) ** 2 * 0.28 : t;
  const push = interpolate(e, [0, 1], [-300, 190]);
  const panX = interpolate(e, [0, 1], [130, -210]);
  const panY = interpolate(e, [0, 1], [48, -40]);
  const yaw = interpolate(e, [0, 1], [10.5, -11.5]);
  const pitch = interpolate(e, [0, 1], [-2.6, 3.2]);
  return { push, panX, panY, yaw, pitch };
};

/* ═══ الخلفية + الأشكال الطايفة ════════════════════════════════════════════ */
const Shape: React.FC<{
  kind: "ring" | "dot" | "arc" | "blob";
  x: number;
  y: number;
  size: number;
  z: number;
  color: string;
  op: number;
  speed: number;
  seed: number;
  tf: number;
  camZ: number;
}> = ({ kind, x, y, size, z, color, op, speed, seed, tf, camZ }) => {
  const driftX = Math.sin(tf / (58 + seed * 9) + seed) * speed;
  const driftY = Math.cos(tf / (72 + seed * 7) + seed * 1.4) * speed * 0.8;
  const spin = Math.sin(tf / (90 + seed * 11) + seed) * 12;

  const effZ = camZ + z;
  const blur = Math.max(0, (Math.abs(effZ - FOCUS) - SHARP_RANGE) / 52);

  const base: React.CSSProperties = {
    position: "absolute",
    left: x - size / 2 + driftX,
    top: y - size / 2 + driftY,
    width: size,
    height: size,
    opacity: op,
    filter: blur > 0.05 ? `blur(${blur.toFixed(1)}px)` : undefined,
    transform: `translateZ(${z}px) rotate(${spin}deg)`,
    willChange: "transform, filter",
  };

  if (kind === "ring")
    return <div style={{ ...base, borderRadius: "50%", border: `1.5px solid ${color}` }} />;

  if (kind === "dot")
    return (
      <div
        style={{
          ...base,
          borderRadius: "50%",
          background: color,
          boxShadow: `0 0 ${size}px ${color}`,
        }}
      />
    );

  if (kind === "arc")
    return (
      <div
        style={{
          ...base,
          borderRadius: "50%",
          border: `1.5px solid transparent`,
          borderTopColor: color,
          borderRightColor: `${color}55`,
        }}
      />
    );

  return (
    <div
      style={{
        ...base,
        borderRadius: "46% 54% 58% 42% / 52% 44% 56% 48%",
        background: `radial-gradient(circle at 40% 35%, ${color}, ${color}00 72%)`,
        filter: `blur(${(blur + 22).toFixed(1)}px)`,
      }}
    />
  );
};

const Shapes: React.FC<{ tf: number; camZ: number }> = ({ tf, camZ }) => {
  const defs: Array<{
    kind: "ring" | "dot" | "arc" | "blob";
    x: number;
    y: number;
    size: number;
    z: number;
    color: string;
    op: number;
    speed: number;
    seed: number;
  }> = [
    { kind: "ring", x: 250, y: 210, size: 210, z: -520, color: `${GOLD}55`, op: 0.5, speed: 26, seed: 1 },
    { kind: "blob", x: 1660, y: 860, size: 520, z: -700, color: `${BURGUNDY}66`, op: 0.42, speed: 34, seed: 2 },
    { kind: "arc", x: 1520, y: 200, size: 300, z: -420, color: `${PARCH}30`, op: 0.55, speed: 22, seed: 3 },
    { kind: "dot", x: 1680, y: 320, size: 9, z: -230, color: GOLD, op: 0.7, speed: 18, seed: 4 },
    { kind: "dot", x: 322, y: 742, size: 7, z: -180, color: `${GOLD}cc`, op: 0.55, speed: 20, seed: 5 },
    { kind: "ring", x: 880, y: 960, size: 130, z: -300, color: `${GOLD_DEEP}44`, op: 0.45, speed: 24, seed: 6 },
    { kind: "blob", x: 380, y: 940, size: 420, z: -640, color: `${OLIVE}55`, op: 0.3, speed: 30, seed: 7 },
    { kind: "arc", x: 1128, y: 140, size: 230, z: -500, color: `${GOLD}33`, op: 0.4, speed: 27, seed: 8 },
    { kind: "dot", x: 1090, y: 900, size: 6, z: -120, color: `${PARCH}aa`, op: 0.5, speed: 16, seed: 9 },
  ];

  return (
    <AbsoluteFill style={{ transformStyle: "preserve-3d" }}>
      {defs.map((d, i) => (
        <Shape key={i} {...d} tf={tf} camZ={camZ} />
      ))}
    </AbsoluteFill>
  );
};

/* ═══ الخلفية ═════════════════════════════════════════════════════════════ */
const Backdrop: React.FC<{ camX: number }> = ({ camX }) => (
  <AbsoluteFill style={{ backgroundColor: INK, overflow: "hidden" }}>
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(ellipse 62% 54% at 50% 44%, #332a1b 0%, #1b1814 46%, #0b0a09 100%)",
      }}
    />
    <div
      style={{
        position: "absolute",
        left: 430 + camX * 0.5,
        top: 90,
        width: 1150,
        height: 780,
        background: `radial-gradient(ellipse at 50% 50%, ${GOLD}5c 0%, ${GOLD_DEEP}2a 44%, ${GOLD_DEEP}00 76%)`,
        filter: "blur(26px)",
      }}
    />
    <div
      style={{
        position: "absolute",
        right: -180 - camX * 0.35,
        bottom: -260,
        width: 900,
        height: 900,
        borderRadius: "50%",
        background: `radial-gradient(circle, ${BURGUNDY}66 0%, ${BURGUNDY}00 70%)`,
        filter: "blur(50px)",
      }}
    />
    <div
      style={{
        position: "absolute",
        left: 0,
        bottom: 0,
        width: "100%",
        height: 210,
        background: `linear-gradient(180deg, ${GOLD_DEEP}00, ${GOLD_DEEP}1f)`,
      }}
    />
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(ellipse 74% 68% at 50% 46%, rgba(0,0,0,0) 34%, rgba(0,0,0,.82) 100%)",
      }}
    />
  </AbsoluteFill>
);

/* ═══ غلاف العمق ══════════════════════════════════════════════════════════ */
const DepthBox: React.FC<{
  x: number;
  y: number;
  z: number;
  rotY: number;
  rotX?: number;
  w: number;
  h: number;
  delay: number;
  idx: number;
  camZ: number;
  tf: number;
  children: React.ReactNode;
}> = ({ x, y, z, rotY, rotX = 0, w, h, delay, idx, camZ, tf, children }) => {
  const s = spring({
    frame: tf - delay,
    fps: FPS,
    config: { damping: 17, mass: 0.85, stiffness: 74 },
  });
  const enter = interpolate(s, [0, 1], [0, 1], CLAMP);

  const bobY = Math.sin(tf / 52 + idx * 1.9) * 7;
  const bobX = Math.cos(tf / 68 + idx * 1.3) * 5;

  const effZ = camZ + z;
  const blur = Math.max(0, (Math.abs(effZ - FOCUS) - SHARP_RANGE) / BLUR_K);
  const sharpen = Math.min(1, blur / 3.2);

  return (
    <div
      style={{
        position: "absolute",
        left: x - w / 2,
        top: y - h / 2 + (1 - enter) * 160 + bobY,
        width: w,
        height: h,
        transformStyle: "preserve-3d",
        transform: `translate3d(${bobX}px, 0px, ${z * enter}px) rotateY(${rotY}deg) rotateX(${rotX}deg) scale(${0.9 + enter * 0.1})`,
        opacity: enter,
        filter: blur > 0.05 ? `blur(${(blur + sharpen).toFixed(2)}px)` : undefined,
        willChange: "transform, filter",
      }}
    >
      {children}
    </div>
  );
};

/* ═══ الزجاج + rim light ══════════════════════════════════════════════════ */
const Glass: React.FC<{
  radius: number;
  tint?: string;
  sheen?: number;
  tf: number;
  idx: number;
  children?: React.ReactNode;
}> = ({ radius, tint = "255,255,255", sheen = 1, tf, idx, children }) => (
  <>
    <div
      style={{
        position: "absolute",
        inset: 0,
        borderRadius: radius,
        overflow: "hidden",
        boxShadow:
          "0 48px 110px rgba(0,0,0,.86), 0 0 0 1px rgba(243,235,219,.12), 0 0 90px rgba(194,164,105,.14)",
        background: `linear-gradient(158deg, rgba(${tint},.20) 0%, rgba(${tint},.05) 40%, rgba(${tint},.02) 66%, rgba(${tint},.14) 100%)`,
        backdropFilter: "blur(18px) saturate(165%)",
        WebkitBackdropFilter: "blur(18px) saturate(165%)",
      }}
    >
      {children}
      <div
        style={{
          position: "absolute",
          top: "-40%",
          left: `${-60 + ((tf * 0.85 + idx * 91) % 230)}%`,
          width: "46%",
          height: "180%",
          background:
            "linear-gradient(100deg, rgba(255,255,255,0) 0%, rgba(255,255,255,.20) 50%, rgba(255,255,255,0) 100%)",
          transform: "rotate(13deg)",
          filter: "blur(8px)",
          opacity: sheen,
        }}
      />
    </div>

    {/* rim light: حافة مضيئة متدرّجة — ذهبي أعلى-يسار ← نبيذي أسفل-يمين */}
    <div
      style={{
        position: "absolute",
        inset: 0,
        borderRadius: radius,
        padding: 1.6,
        background: `linear-gradient(128deg, ${GOLD}f2 0%, ${GOLD}44 18%, rgba(255,255,255,.12) 46%, ${BURGUNDY}88 74%, ${GOLD}66 100%)`,
        WebkitMask: "linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0)",
        WebkitMaskComposite: "xor",
        maskComposite: "exclude",
        pointerEvents: "none",
      }}
    />

    {/* حرف داخلي مضيء */}
    <div
      style={{
        position: "absolute",
        inset: 0,
        borderRadius: radius,
        boxShadow:
          "inset 0 1px 0 rgba(255,255,255,.52), inset 0 -1px 0 rgba(255,255,255,.09), inset 1px 0 0 rgba(255,255,255,.16), inset -1px 0 0 rgba(255,255,255,.16)",
        pointerEvents: "none",
      }}
    />
  </>
);

/* ═══ كارت إحصائية ════════════════════════════════════════════════════════ */
const StatCard: React.FC<{ w: number; h: number; tf: number; idx: number }> = ({
  w,
  h,
  tf,
  idx,
}) => {
  const r = w * 0.055;
  const rise = spring({ frame: tf - 34, fps: FPS, config: { damping: 18, stiffness: 90 } });
  const bars = [0.42, 0.68, 0.5, 0.92, 0.74];
  return (
    <>
      <Glass radius={r} tf={tf} idx={idx} />
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: r,
          opacity: 0.45,
          backgroundImage: `linear-gradient(${GOLD}1c 1px, transparent 1px), linear-gradient(90deg, ${GOLD}1c 1px, transparent 1px)`,
          backgroundSize: `${w * 0.16}px ${w * 0.16}px`,
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          padding: w * 0.085,
          display: "flex",
          flexDirection: "column",
          direction: "rtl",
        }}
      >
        <div
          style={{
            fontFamily: "IBM Plex Sans Arabic",
            fontWeight: 500,
            fontSize: w * 0.082,
            color: `${PARCH}a8`,
            letterSpacing: "0.07em",
          }}
        >
          المخطوطات
        </div>
        <div
          style={{
            fontFamily: "Amiri",
            fontWeight: 700,
            fontSize: w * 0.34,
            color: GOLD,
            lineHeight: 0.92,
            marginTop: h * 0.035,
            textShadow: `0 0 50px ${GOLD_DEEP}99`,
            opacity: rise,
            transform: `translateY(${(1 - rise) * 18}px)`,
          }}
        >
          ٣٥٠
        </div>
        <div
          style={{
            fontFamily: "IBM Plex Sans Arabic",
            fontWeight: 700,
            fontSize: w * 0.10,
            color: PARCH,
            marginTop: -h * 0.012,
          }}
        >
          ألف مخطوطة
        </div>
        <svg viewBox="0 0 100 34" style={{ width: "100%", marginTop: "auto" }}>
          {bars.map((v, i) => {
            const grow = interpolate(tf, [44 + i * 6, 78 + i * 6], [0, v], CLAMP);
            return (
              <rect
                key={i}
                x={6 + i * 19}
                y={34 - grow * 32}
                width={11}
                height={grow * 32}
                rx={2.5}
                fill={i === 3 ? GOLD : `${GOLD}66`}
              />
            );
          })}
        </svg>
        <div
          style={{
            marginTop: h * 0.038,
            fontFamily: "IBM Plex Sans Arabic",
            fontSize: w * 0.070,
            color: `${PARCH}6e`,
          }}
        >
          نُقلت خارج المدينة
        </div>
      </div>
    </>
  );
};

/* ═══ كارت مسار ═══════════════════════════════════════════════════════════ */
const RouteCard: React.FC<{ w: number; h: number; tf: number; idx: number }> = ({
  w,
  h,
  tf,
  idx,
}) => {
  const r = w * 0.055;
  const draw = interpolate(tf, [42, 116], [0, 1], CLAMP);
  const dotOn = interpolate(tf, [108, 126], [0, 1], CLAMP);
  return (
    <>
      <Glass radius={r} tf={tf} idx={idx} />
      <div style={{ position: "absolute", inset: 0, padding: w * 0.075, direction: "rtl" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span
            style={{
              fontFamily: "IBM Plex Sans Arabic",
              fontWeight: 500,
              fontSize: w * 0.080,
              color: `${PARCH}a8`,
              letterSpacing: "0.07em",
            }}
          >
            المسار
          </span>
          <span
            style={{
              fontFamily: "IBM Plex Sans Arabic",
              fontSize: w * 0.058,
              color: `${PARCH}66`,
              border: `1px solid ${PARCH}2e`,
              borderRadius: 999,
              padding: `${w * 0.012}px ${w * 0.038}px`,
            }}
          >
            ٢٠١٣
          </span>
        </div>
        <svg viewBox="0 0 100 72" style={{ width: "100%", marginTop: h * 0.045 }}>
          {Array.from({ length: 24 }).map((_, i) => (
            <circle
              key={i}
              cx={8 + (i % 6) * 16.8}
              cy={8 + Math.floor(i / 6) * 18}
              r={0.55}
              fill={`${PARCH}30`}
            />
          ))}
          <path
            d="M12 56 C 32 54, 40 24, 58 22 S 84 34, 92 12"
            fill="none"
            stroke={`${GOLD}33`}
            strokeWidth={2.1}
            strokeLinecap="round"
          />
          <path
            d="M12 56 C 32 54, 40 24, 58 22 S 84 34, 92 12"
            fill="none"
            stroke={GOLD}
            strokeWidth={2.1}
            strokeLinecap="round"
            pathLength={1}
            strokeDasharray={1}
            strokeDashoffset={1 - draw}
            style={{ filter: `drop-shadow(0 0 4px ${GOLD})` }}
          />
          <circle cx={12} cy={56} r={2.8} fill={PARCH} opacity={0.92} />
          <circle cx={12} cy={56} r={5.6} fill="none" stroke={`${PARCH}44`} strokeWidth={0.7} />
          <circle
            cx={92}
            cy={12}
            r={3.6}
            fill={GOLD}
            opacity={dotOn}
            style={{ filter: `drop-shadow(0 0 8px ${GOLD})` }}
          />
          <circle
            cx={92}
            cy={12}
            r={7 + Math.sin(tf / 12) * 1.6}
            fill="none"
            stroke={GOLD}
            strokeWidth={0.7}
            opacity={dotOn * 0.6}
          />
        </svg>
        <div
          style={{
            marginTop: "auto",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-end",
            fontFamily: "IBM Plex Sans Arabic",
            fontSize: w * 0.066,
            color: `${PARCH}72`,
          }}
        >
          <span>تمبكتو</span>
          <span style={{ color: GOLD, fontWeight: 700, fontFamily: "Amiri", fontSize: w * 0.115 }}>
            ٤٠٠ ميل
          </span>
        </div>
      </div>
    </>
  );
};

/* ═══ كارت اقتباس ═════════════════════════════════════════════════════════ */
const QuoteCardG: React.FC<{ w: number; h: number; tf: number; idx: number }> = ({
  w,
  h,
  tf,
  idx,
}) => {
  const r = w * 0.055;
  const o = interpolate(tf, [58, 92], [0, 1], CLAMP);
  const ruleH = interpolate(tf, [70, 108], [0, 1], CLAMP);
  return (
    <>
      <Glass radius={r} tf={tf} idx={idx} tint="255,244,222" sheen={0.65} />
      <div
        style={{
          position: "absolute",
          inset: 0,
          padding: w * 0.085,
          display: "flex",
          flexDirection: "column",
          direction: "rtl",
          opacity: o,
        }}
      >
        <div
          style={{
            fontFamily: "IBM Plex Sans Arabic",
            fontWeight: 500,
            fontSize: w * 0.075,
            color: `${GOLD}cc`,
            letterSpacing: "0.10em",
          }}
        >
          ١٥٢٦
        </div>
        <div
          style={{
            fontFamily: "Amiri",
            fontWeight: 700,
            fontSize: w * 0.42,
            color: `${GOLD}55`,
            lineHeight: 0.62,
            marginTop: h * 0.012,
          }}
        >
          ﴾
        </div>
        <div
          style={{
            fontFamily: "Amiri",
            fontWeight: 400,
            fontSize: w * 0.135,
            lineHeight: 1.66,
            color: PARCH,
            marginTop: h * 0.018,
          }}
        >
          تجارة الكتب أربح من تجارة الذهب
        </div>
        <div
          style={{
            marginTop: "auto",
            width: `${ruleH * 42}%`,
            height: 1.2,
            background: `linear-gradient(90deg, ${GOLD}, ${GOLD_DEEP}00)`,
            marginBottom: h * 0.030,
          }}
        />
        <div
          style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: w * 0.070, color: `${PARCH}a0` }}
        >
          ليو أفريكانوس
        </div>
      </div>
    </>
  );
};

/* ═══ كارت صورة ═══════════════════════════════════════════════════════════ */
const PhotoCard: React.FC<{ src: string; w: number; h: number; tf: number }> = ({
  src,
  w,
  h,
  tf,
}) => {
  const r = w * 0.05;
  const kb = interpolate(tf, [0, DUR], [1.0, 1.09], CLAMP);
  return (
    <>
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: r,
          overflow: "hidden",
          boxShadow:
            "0 54px 120px rgba(0,0,0,.9), 0 0 0 1px rgba(243,235,219,.16), 0 0 110px rgba(194,164,105,.20)",
        }}
      >
        <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${kb})` }} />
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "linear-gradient(180deg, rgba(14,13,12,.05) 0%, rgba(14,13,12,.30) 58%, rgba(14,13,12,.80) 100%)",
          }}
        />
      </div>
      {/* rim light على الصورة */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: r,
          padding: 1.6,
          background: `linear-gradient(128deg, ${GOLD}e8 0%, ${GOLD}44 20%, rgba(255,255,255,.10) 48%, ${BURGUNDY}77 76%, ${GOLD}55 100%)`,
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
          boxShadow: "inset 0 1px 0 rgba(255,255,255,.44)",
          pointerEvents: "none",
        }}
      />
    </>
  );
};

/* ═══ العالم 3D (يُرسم عند أي tf — ده اللي يخلي الـghosting ممكن) ══════════ */
const World: React.FC<{ tf: number }> = ({ tf }) => {
  const cam = cameraAt(tf);
  return (
    <AbsoluteFill style={{ perspective: 1500, perspectiveOrigin: "50% 46%", overflow: "hidden" }}>
      <AbsoluteFill
        style={{
          transformStyle: "preserve-3d",
          transform: `translate3d(${cam.panX}px, ${cam.panY}px, ${cam.push}px) rotateY(${cam.yaw}deg) rotateX(${cam.pitch}deg)`,
        }}
      >
        <Shapes tf={tf} camZ={cam.push} />

        <DepthBox x={392} y={452} z={-330} rotY={36} w={228} h={404} delay={34} idx={0} camZ={cam.push} tf={tf}>
          <QuoteCardG w={228} h={404} tf={tf} idx={0} />
        </DepthBox>

        <DepthBox x={1528} y={452} z={-330} rotY={-36} w={228} h={404} delay={40} idx={1} camZ={cam.push} tf={tf}>
          <StatCard w={228} h={404} tf={tf} idx={1} />
        </DepthBox>

        <DepthBox x={640} y={492} z={-150} rotY={27} w={272} h={482} delay={22} idx={2} camZ={cam.push} tf={tf}>
          <PhotoCard src="projects/TMB_001/plates/tmb_drums.jpg" w={272} h={482} tf={tf} />
        </DepthBox>

        <DepthBox x={1282} y={492} z={-150} rotY={-27} w={272} h={482} delay={28} idx={3} camZ={cam.push} tf={tf}>
          <RouteCard w={272} h={482} tf={tf} idx={3} />
        </DepthBox>

        <DepthBox x={960} y={458} z={-15} rotY={0} w={374} h={664} delay={8} idx={4} camZ={cam.push} tf={tf}>
          <PhotoCard src="projects/TMB_001/plates/tmb_map.jpg" w={374} h={664} tf={tf} />
        </DepthBox>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ═══ كلمة حركية ══════════════════════════════════════════════════════════ */
const Word: React.FC<{ children: React.ReactNode; start: number; size: number }> = ({
  children,
  start,
  size,
}) => {
  const frame = useCurrentFrame();
  const p = spring({
    frame: frame - start,
    fps: FPS,
    config: { damping: 19, mass: 0.7, stiffness: 122 },
  });
  return (
    <span
      style={{
        display: "inline-block",
        fontFamily: "Amiri",
        fontWeight: 700,
        fontSize: size,
        lineHeight: 1.24,
        color: PARCH,
        opacity: interpolate(p, [0, 1], [0, 1], CLAMP),
        filter: `blur(${interpolate(p, [0, 1], [13, 0], CLAMP)}px)`,
        transform: `perspective(820px) translateY(${interpolate(p, [0, 1], [52, 0], CLAMP)}px) rotateX(${interpolate(p, [0, 1], [-64, 0], CLAMP)}deg)`,
        transformOrigin: "50% 100%",
        letterSpacing: `${interpolate(p, [0, 1], [0.12, 0], CLAMP)}em`,
        textShadow: "0 4px 34px rgba(0,0,0,.9)",
      }}
    >
      {children}
    </span>
  );
};

/* ═══════════════════════════════════════════════════════════════════════════ */
export const ProofStyle: React.FC = () => {
  const frame = useCurrentFrame();
  const cam = cameraAt(frame);

  const words = ["الكتب", "كانت", "أغلى", "من", "الأرض"];
  const wordStart = 96;

  const subIn = spring({ frame: frame - 236, fps: FPS, config: { damping: 20, stiffness: 92 } });
  const ruleW = interpolate(frame, [222, 258], [0, 300], CLAMP);
  const logoOp = interpolate(frame, [30, 62], [0, 1], CLAMP);

  // سرعة الكاميرا px/frame — تُقاس على محورين
  const v = (f: number) => {
    const a = cameraAt(f);
    const b = cameraAt(f - 1);
    return Math.hypot(a.push - b.push, a.panX - b.panX, a.panY - b.panY);
  };
  const vel = v(frame);
  // 0 → لا blur · 6px/frame → blur كامل (0.30)
  const ghostAmt = Math.min(0.30, Math.max(0, (vel - 0.9) * 0.058));
  const ghost1 = ghostAmt * 0.66;
  const ghost2 = ghostAmt * 0.34;

  return (
    <AbsoluteFill style={{ backgroundColor: INK }}>
      <Backdrop camX={cam.panX} />

      {/* ═══ ghosting = motion blur: شدته تتناسب مع سرعة الكاميرا فقط ═══
          كاميرا ساكنة → صفر ghosting. كاميرا بتتسارع → blur حقيقي.
          القيم مقاسة بـpx/frame على محور الضغط. */}
      <AbsoluteFill style={{ opacity: ghost2 }}>
        <World tf={frame - 2} />
      </AbsoluteFill>
      <AbsoluteFill style={{ opacity: ghost1 }}>
        <World tf={frame - 1} />
      </AbsoluteFill>
      <World tf={frame} />

      {/* ═══ شعار ═══ */}
      <div
        style={{
          position: "absolute",
          left: 92,
          top: 70,
          display: "flex",
          alignItems: "center",
          gap: 15,
          opacity: logoOp,
          direction: "rtl",
        }}
      >
        <div style={{ width: 3, height: 38, borderRadius: 2, background: GOLD, boxShadow: `0 0 22px ${GOLD}` }} />
        <div style={{ fontFamily: "Amiri", fontWeight: 700, fontSize: 44, color: PARCH }}>رِواق</div>
      </div>

      {/* ═══ النص ═══ */}
      <div
        style={{
          position: "absolute",
          right: 88,
          bottom: 56,
          width: 1000,
          direction: "rtl",
          textAlign: "right",
          transform: `translateX(${cam.panX * -0.14}px)`,
        }}
      >
        <div style={{ display: "flex", justifyContent: "flex-end", flexWrap: "wrap", gap: "0 0.25em" }}>
          {words.map((w, i) => (
            <Word key={w} start={wordStart + i * 7} size={88}>
              {w}
            </Word>
          ))}
        </div>
        <div
          style={{
            marginTop: 24,
            marginRight: 5,
            width: ruleW,
            height: 1.5,
            background: `linear-gradient(270deg, ${GOLD}, ${GOLD_DEEP}00)`,
            opacity: subIn,
            boxShadow: `0 0 20px ${GOLD}99`,
          }}
        />
        <div
          style={{
            marginTop: 20,
            opacity: subIn,
            transform: `translateY(${interpolate(subIn, [0, 1], [20, 0], CLAMP)}px)`,
            fontFamily: "IBM Plex Sans Arabic",
            fontWeight: 500,
            fontSize: 38,
            color: `${PARCH}cf`,
          }}
        >
          في مدينة الكتب… تمبكتو
        </div>
      </div>

      <Audio src={staticFile("projects/TMB_001/audio/music.wav")} volume={0.22} />
    </AbsoluteFill>
  );
};
