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
   ProofStyle — برهان الستايل (6 ثوانٍ · 1920×1080 · 60fps)

   الهدف: إثبات أن لغة حركة المرجع (Premium 3D Motion + Kinetic Typography +
   Glassmorphism + Cinematic Product Animation) ممكنة داخل رِواق.

   التنفيذ: CSS 3D حقيقي (perspective + preserve-3d + translateZ)، لا three.js.
   الهوية: فحمي/عاجي/ذهبي من brand.json — لا نيون ولا ألوان خارج اللوحة.
   ═══════════════════════════════════════════════════════════════════════════ */

const GOLD = "#C2A469";
const GOLD_DEEP = "#A98A4B";
const PARCH = "#F3EBDB";
const BURGUNDY = "#5E2230";
const INK = "#111010";

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/* ── الخلفية: تدرّج + هالات دافئة + فينييت ───────────────────────────────── */
const Backdrop: React.FC = () => {
  const frame = useCurrentFrame();
  const breathe = 1 + Math.sin(frame / 55) * 0.028;

  return (
    <AbsoluteFill style={{ backgroundColor: INK, overflow: "hidden" }}>
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 68% 58% at 50% 40%, #2b2519 0%, #1a1815 44%, #0f0e0d 100%)",
          transform: `scale(${breathe})`,
        }}
      />

      {/* هالة ذهبية يسار-أعلى */}
      <div
        style={{
          position: "absolute",
          left: "-12%",
          top: "-6%",
          width: 900,
          height: 900,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${GOLD_DEEP}38 0%, ${GOLD_DEEP}00 68%)`,
          filter: "blur(34px)",
        }}
      />
      {/* هالة نبيذية يمين-أسفل (عمق لوني من غير نيون) */}
      <div
        style={{
          position: "absolute",
          right: "-14%",
          bottom: "-14%",
          width: 980,
          height: 980,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${BURGUNDY}55 0%, ${BURGUNDY}00 70%)`,
          filter: "blur(44px)",
        }}
      />
      {/* ضوء خلفي للكروت */}
      <div
        style={{
          position: "absolute",
          left: "26%",
          top: "8%",
          width: 980,
          height: 620,
          background: `radial-gradient(ellipse, ${GOLD}2e 0%, ${GOLD}00 72%)`,
          filter: "blur(40px)",
        }}
      />

      {/* فينييت سينمائي */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 70% 64% at 50% 44%, rgba(0,0,0,0) 38%, rgba(0,0,0,.78) 100%)",
        }}
      />
    </AbsoluteFill>
  );
};

/* ── كارت زجاجي في فضاء 3D ───────────────────────────────────────────────── */
type CardSpec = {
  src: string;
  x: number;
  y: number;
  z: number;
  ry: number;
  rx: number;
  w: number;
  h: number;
  delay: number;
};

const GlassCard: React.FC<CardSpec & { idx: number }> = ({
  src,
  x,
  y,
  z,
  ry,
  rx,
  w,
  h,
  delay,
  idx,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // دخول بنابض (overshoot خفيف = إحساس فخم)
  const s = spring({
    frame: frame - delay,
    fps,
    config: { damping: 16, mass: 0.9, stiffness: 78 },
  });
  const enter = interpolate(s, [0, 1], [0, 1], CLAMP);

  // انجراف مستمر (parallax + floating)
  const driftY = Math.sin(frame / 44 + idx * 1.7) * 8;
  const driftX = Math.cos(frame / 61 + idx * 1.1) * 6;
  const spin = Math.sin(frame / 74 + idx * 0.9) * 3.4;

  // عمق ميدان (كل ما بعد، كل ما ضبابه أكتر)
  const dof = Math.max(0, (Math.abs(z) * enter - 100) / 42);
  const radius = w * 0.055;

  return (
    <div
      style={{
        position: "absolute",
        left: x - w / 2,
        top: y - h / 2,
        width: w,
        height: h,
        transformStyle: "preserve-3d",
        transform: `translate3d(${driftX}px, ${driftY + (1 - enter) * 150}px, ${
          z * enter
        }px) rotateY(${ry + spin}deg) rotateX(${rx}deg)`,
        opacity: enter,
        filter: `blur(${dof}px)`,
      }}
    >
      {/* الصورة */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: radius,
          overflow: "hidden",
          boxShadow: "0 44px 100px rgba(0,0,0,.82), 0 0 0 1px rgba(243,235,219,.10)",
        }}
      >
        <Img
          src={staticFile(src)}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "linear-gradient(180deg, rgba(17,16,16,.06) 0%, rgba(17,16,16,.62) 100%)",
          }}
        />
      </div>

      {/* طبقة الزجاج */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: radius,
          background:
            "linear-gradient(154deg, rgba(255,255,255,.22) 0%, rgba(255,255,255,.045) 36%, rgba(255,255,255,.015) 62%, rgba(255,255,255,.13) 100%)",
          backdropFilter: "blur(16px) saturate(155%)",
          WebkitBackdropFilter: "blur(16px) saturate(155%)",
          border: "1px solid rgba(255,255,255,.24)",
          boxShadow: `inset 0 1px 0 rgba(255,255,255,.46), inset 0 -1px 0 rgba(255,255,255,.10), 0 0 70px ${GOLD_DEEP}22`,
        }}
      />

      {/* لمعة متحركة على الحرف */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: radius,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            position: "absolute",
            top: "-30%",
            left: `${-45 + ((frame * 1.05 + idx * 74) % 210)}%`,
            width: "52%",
            height: "160%",
            background:
              "linear-gradient(100deg, rgba(255,255,255,0) 0%, rgba(255,255,255,.22) 50%, rgba(255,255,255,0) 100%)",
            transform: "rotate(12deg)",
            filter: "blur(7px)",
          }}
        />
      </div>
    </div>
  );
};

/* ── كلمة حركية (Kinetic Typography) ─────────────────────────────────────── */
const KineticWord: React.FC<{
  children: React.ReactNode;
  start: number;
  size: number;
  glow?: boolean;
}> = ({ children, start, size, glow }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const p = spring({
    frame: frame - start,
    fps,
    config: { damping: 19, mass: 0.72, stiffness: 118 },
  });

  const opacity = interpolate(p, [0, 1], [0, 1], CLAMP);
  const y = interpolate(p, [0, 1], [58, 0], CLAMP);
  const rx = interpolate(p, [0, 1], [-68, 0], CLAMP);
  const blur = interpolate(p, [0, 1], [16, 0], CLAMP);
  const tracking = interpolate(p, [0, 1], [0.14, 0], CLAMP);

  return (
    <span
      style={{
        display: "inline-block",
        fontFamily: "Amiri",
        fontWeight: 700,
        fontSize: size,
        lineHeight: 1.28,
        color: PARCH,
        letterSpacing: `${tracking}em`,
        opacity,
        filter: `blur(${blur}px)`,
        transform: `perspective(760px) translateY(${y}px) rotateX(${rx}deg)`,
        transformOrigin: "50% 100%",
        textShadow: glow
          ? `0 0 46px ${GOLD_DEEP}66, 0 4px 30px rgba(0,0,0,.85)`
          : "0 4px 30px rgba(0,0,0,.85)",
      }}
    >
      {children}
    </span>
  );
};

/* ═══════════════════════════════════════════════════════════════════════════
   التركيب
   ═══════════════════════════════════════════════════════════════════════════ */
export const ProofStyle: React.FC = () => {
  const frame = useCurrentFrame();

  const cards: CardSpec[] = [
    { src: "projects/TMB_001/plates/tmb_drums.jpg", x: 215, y: 452, z: -380, ry: 47, rx: 0, w: 152, h: 270, delay: 26 },
    { src: "projects/TMB_001/plates/tmb_route.jpg", x: 528, y: 420, z: -165, ry: 31, rx: 0, w: 226, h: 402, delay: 15 },
    { src: "projects/TMB_001/plates/tmb_map.jpg",   x: 960, y: 398, z: 115,  ry: 0,  rx: 0, w: 312, h: 555, delay: 4  },
    { src: "projects/TMB_001/plates/tmb_fall.jpg",  x: 1392, y: 420, z: -165, ry: -31, rx: 0, w: 226, h: 402, delay: 20 },
    { src: "projects/TMB_001/plates/tmb_gold.jpg",  x: 1706, y: 452, z: -380, ry: -47, rx: 0, w: 152, h: 270, delay: 32 },
  ];

  // توقيتات الكلمات (60fps)
  const words = ["الكتب", "كانت", "أغلى", "من", "الأرض"];
  const wordStart = 82;
  const wordGap = 7;

  // خط ذهبي يفتح الفيلم
  const lineW = interpolate(frame, [0, 30], [0, 460], CLAMP);
  const lineOp = interpolate(frame, [0, 8, 52, 72], [0, 1, 1, 0], CLAMP);

  // شعار رِواق
  const logoOp = interpolate(frame, [40, 66], [0, 1], CLAMP);
  const logoY = interpolate(frame, [40, 66], [18, 0], CLAMP);

  // السطر الثاني
  const subOp = spring({
    frame: frame - 208,
    fps: 60,
    config: { damping: 20, mass: 0.8, stiffness: 96 },
  });
  const ruleW = interpolate(frame, [198, 232], [0, 330], CLAMP);

  return (
    <AbsoluteFill style={{ backgroundColor: INK }}>
      <Backdrop />

      {/* فضاء 3D */}
      <AbsoluteFill style={{ perspective: 1600, perspectiveOrigin: "50% 42%" }}>
        <AbsoluteFill style={{ transformStyle: "preserve-3d" }}>
          {cards.map((c, i) => (
            <GlassCard key={c.src} {...c} idx={i} />
          ))}
        </AbsoluteFill>
      </AbsoluteFill>

      {/* خط ذهبي افتتاحي */}
      <div
        style={{
          position: "absolute",
          left: 960 - lineW / 2,
          top: 300,
          width: lineW,
          height: 2,
          background: `linear-gradient(90deg, ${GOLD_DEEP}00, ${GOLD} 50%, ${GOLD_DEEP}00)`,
          opacity: lineOp,
          boxShadow: `0 0 26px ${GOLD}aa`,
        }}
      />

      {/* شعار رِواق */}
      <div
        style={{
          position: "absolute",
          left: 96,
          top: 76,
          display: "flex",
          alignItems: "center",
          gap: 16,
          opacity: logoOp,
          transform: `translateY(${logoY}px)`,
          direction: "rtl",
        }}
      >
        <div
          style={{
            width: 3,
            height: 40,
            borderRadius: 2,
            background: GOLD,
            boxShadow: `0 0 20px ${GOLD}`,
          }}
        />
        <div
          style={{
            fontFamily: "Amiri",
            fontWeight: 700,
            fontSize: 46,
            color: PARCH,
            letterSpacing: "0.02em",
          }}
        >
          رِواق
        </div>
      </div>

      {/* الكتلة النصية */}
      <div
        style={{
          position: "absolute",
          right: 96,
          bottom: 92,
          width: 1080,
          direction: "rtl",
          textAlign: "right",
        }}
      >
        <div style={{ display: "flex", justifyContent: "flex-end", flexWrap: "wrap", gap: "0 0.26em" }}>
          {words.map((w, i) => (
            <KineticWord
              key={w}
              start={wordStart + i * wordGap}
              size={98}
              glow={i === words.length - 1}
            >
              {w}
            </KineticWord>
          ))}
        </div>

        {/* فاصل ذهبي */}
        <div
          style={{
            marginTop: 26,
            marginRight: 4,
            width: ruleW,
            height: 1.5,
            background: `linear-gradient(270deg, ${GOLD}, ${GOLD_DEEP}00)`,
            opacity: subOp,
            boxShadow: `0 0 18px ${GOLD}88`,
          }}
        />

        {/* السطر الثاني */}
        <div
          style={{
            marginTop: 22,
            opacity: subOp,
            transform: `translateY(${interpolate(subOp, [0, 1], [22, 0], CLAMP)}px)`,
            fontFamily: "IBM Plex Sans Arabic",
            fontWeight: 500,
            fontSize: 40,
            color: `${PARCH}D9`,
            letterSpacing: "0.01em",
          }}
        >
          في مدينة الكتب… تمبكتو
        </div>
      </div>

      {/* موسيقى */}
      <Audio src={staticFile("projects/TMB_001/audio/music.wav")} volume={0.22} />
    </AbsoluteFill>
  );
};
