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
   ProofStyle v2 — برهان الستايل (6ث · 1920×1080 · 60fps)

   v1 فشل في 3 حاجات: الكروت كلها ضبابية (DOF غلط)، المشهد ساكن (مفيش كاميرا)،
   والزجاج شفاف على خلفية سودا (مفيش glass look).
   v2: ريج كاميرا حقيقي · DOF من مسافة بؤرية · كروت UI + صور · تقاطع في العمق.
   ═══════════════════════════════════════════════════════════════════════════ */

const GOLD = "#C2A469";
const GOLD_DEEP = "#A98A4B";
const PARCH = "#F3EBDB";
const BURGUNDY = "#5E2230";
const INK = "#0E0D0C";

const FPS = 60;
const DUR = 360;

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** مسافة بؤرة الكاميرا من المستوى z=0، ونطاق الوضوح */
const FOCUS = 0;
const SHARP_RANGE = 150;
const BLUR_K = 46;

/* ── ريج الكاميرا: كل المشهد يتحرك داخلها ────────────────────────────────── */
const cameraAt = (frame: number) => {
  const t = frame / DUR;
  // دفع للأمام + انحراف جانبي + ميل بسيط (كاميرا سينمائية لا خطية)
  const push = interpolate(t, [0, 1], [-210, 95]);
  const panX = interpolate(t, [0, 1], [70, -95]);
  const panY = interpolate(t, [0, 1], [34, -26]);
  const yaw = interpolate(t, [0, 1], [7.4, -8.2]);
  const pitch = interpolate(t, [0, 1], [-1.8, 2.4]);
  return { push, panX, panY, yaw, pitch };
};

/* ── الخلفية ─────────────────────────────────────────────────────────────── */
const Backdrop: React.FC<{ camX: number }> = ({ camX }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: INK, overflow: "hidden" }}>
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 62% 54% at 50% 44%, #332a1b 0%, #1b1814 46%, #0b0a09 100%)",
        }}
      />
      {/* كتلة إضاءة ذهبية ضخمة خلف الكروت — الزجاج محتاج حاجة يضببها */}
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
      {/* لمسة نبيذية عمق */}
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
      {/* شريط أرضي فاتح يعكس الضوء */}
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
};

/* ── غلاف 3D: يحسب العمق والضبابية من الكاميرا ──────────────────────────── */
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
  children: React.ReactNode;
}> = ({ x, y, z, rotY, rotX = 0, w, h, delay, idx, camZ, children }) => {
  const frame = useCurrentFrame();

  const s = spring({
    frame: frame - delay,
    fps: FPS,
    config: { damping: 17, mass: 0.85, stiffness: 74 },
  });
  const enter = interpolate(s, [0, 1], [0, 1], CLAMP);

  // انجراف حيّ
  const bobY = Math.sin(frame / 52 + idx * 1.9) * 7;
  const bobX = Math.cos(frame / 68 + idx * 1.3) * 5;

  // ✅ DOF الصحيح: المسافة الفعلية من الكاميرا، لا |z|
  const effZ = camZ + z;
  const blur = Math.max(0, (Math.abs(effZ - FOCUS) - SHARP_RANGE) / BLUR_K);
  const sharpen = Math.min(1, blur / 3.2); // أثناء الدخول يبدأ حادًا ثم يستقر

  return (
    <div
      style={{
        position: "absolute",
        left: x - w / 2,
        top: y - h / 2 + (1 - enter) * 130 + bobY,
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

/* ── سطح زجاجي مشترك ─────────────────────────────────────────────────────── */
const Glass: React.FC<{
  radius: number;
  tint?: string;
  sheen?: number;
  frame: number;
  idx: number;
  children?: React.ReactNode;
}> = ({ radius, tint = "255,255,255", sheen = 1, frame, idx, children }) => (
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
        border: "1px solid rgba(255,255,255,.26)",
      }}
    >
      {children}
      {/* لمعة متحركة */}
      <div
        style={{
          position: "absolute",
          top: "-40%",
          left: `${-60 + ((frame * 0.85 + idx * 91) % 230)}%`,
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
    {/* حرف مضيء */}
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

/* ── كارت UI: رقم/إحصائية ───────────────────────────────────────────────── */
const StatCard: React.FC<{ w: number; h: number; frame: number; idx: number }> = ({
  w,
  h,
  frame,
  idx,
}) => {
  const r = w * 0.055;
  const rise = spring({ frame: frame - 34, fps: FPS, config: { damping: 18, stiffness: 90 } });
  const bars = [0.42, 0.68, 0.5, 0.92, 0.74];
  return (
    <>
      <Glass radius={r} frame={frame} idx={idx} />
      {/* شبكة خلفية دقيقة تعطي الزجاج نسيجًا */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: r,
          opacity: 0.5,
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

        {/* رسم أعمدة صغير */}
        <svg viewBox="0 0 100 34" style={{ width: "100%", marginTop: "auto" }}>
          {bars.map((v, i) => {
            const grow = interpolate(frame, [44 + i * 6, 78 + i * 6], [0, v], CLAMP);
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

/* ── كارت UI: مسار ──────────────────────────────────────────────────────── */
const RouteCard: React.FC<{ w: number; h: number; frame: number; idx: number }> = ({
  w,
  h,
  frame,
  idx,
}) => {
  const r = w * 0.055;
  const draw = interpolate(frame, [42, 116], [0, 1], CLAMP);
  const dotOn = interpolate(frame, [108, 126], [0, 1], CLAMP);

  return (
    <>
      <Glass radius={r} frame={frame} idx={idx} />
      <div style={{ position: "absolute", inset: 0, padding: w * 0.075, direction: "rtl" }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
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
          {/* نقاط شبكة = إحساس خريطة */}
          {Array.from({ length: 24 }).map((_, i) => {
            const cx = 8 + (i % 6) * 16.8;
            const cy = 8 + Math.floor(i / 6) * 18;
            return <circle key={i} cx={cx} cy={cy} r={0.55} fill={`${PARCH}30`} />;
          })}
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
            r={(7 + Math.sin(frame / 12) * 1.6)}
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
          <span
            style={{
              color: GOLD,
              fontWeight: 700,
              fontFamily: "Amiri",
              fontSize: w * 0.115,
            }}
          >
            ٤٠٠ ميل
          </span>
        </div>
      </div>
    </>
  );
};

/* ── كارت UI: اقتباس ────────────────────────────────────────────────────── */
const QuoteCard: React.FC<{ w: number; h: number; frame: number; idx: number }> = ({
  w,
  h,
  frame,
  idx,
}) => {
  const r = w * 0.055;
  const o = interpolate(frame, [58, 92], [0, 1], CLAMP);
  const ruleH = interpolate(frame, [70, 108], [0, 1], CLAMP);
  return (
    <>
      <Glass radius={r} frame={frame} idx={idx} tint="255,244,222" sheen={0.65} />
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
          style={{
            fontFamily: "IBM Plex Sans Arabic",
            fontSize: w * 0.070,
            color: `${PARCH}a0`,
          }}
        >
          ليو أفريكانوس
        </div>
      </div>
    </>
  );
};

/* ── كارت صورة ──────────────────────────────────────────────────────────── */
const PhotoCard: React.FC<{ src: string; w: number; h: number; frame: number }> = ({
  src,
  w,
  h,
  frame,
}) => {
  const r = w * 0.05;
  const kb = interpolate(frame, [0, DUR], [1.0, 1.09], CLAMP);
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
        <Img
          src={staticFile(src)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${kb})`,
          }}
        />
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "linear-gradient(180deg, rgba(14,13,12,.05) 0%, rgba(14,13,12,.30) 58%, rgba(14,13,12,.80) 100%)",
          }}
        />
      </div>
      {/* زجاج خفيف فوق الصورة */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: r,
          border: "1px solid rgba(255,255,255,.22)",
          background:
            "linear-gradient(158deg, rgba(255,255,255,.16) 0%, rgba(255,255,255,.03) 42%, rgba(255,255,255,.01) 70%, rgba(255,255,255,.10) 100%)",
          boxShadow: "inset 0 1px 0 rgba(255,255,255,.44)",
          pointerEvents: "none",
        }}
      />
    </>
  );
};

/* ── كلمة حركية ─────────────────────────────────────────────────────────── */
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

  return (
    <AbsoluteFill style={{ backgroundColor: INK }}>
      <Backdrop camX={cam.panX} />

      {/* ═══ عالم 3D ═══ */}
      <AbsoluteFill
        style={{
          perspective: 1500,
          perspectiveOrigin: "50% 46%",
          overflow: "hidden",
        }}
      >
        <AbsoluteFill
          style={{
            transformStyle: "preserve-3d",
            transform: `translate3d(${cam.panX}px, ${cam.panY}px, ${cam.push}px) rotateY(${cam.yaw}deg) rotateX(${cam.pitch}deg)`,
          }}
        >
          {/* الخلفي: اقتباس (يسار) + إحصائية (يمين) */}
          <DepthBox x={392} y={452} z={-330} rotY={36} w={228} h={404} delay={34} idx={0} camZ={cam.push}>
            <QuoteCard w={228} h={404} frame={frame} idx={0} />
          </DepthBox>

          <DepthBox x={1528} y={452} z={-330} rotY={-36} w={228} h={404} delay={40} idx={1} camZ={cam.push}>
            <StatCard w={228} h={404} frame={frame} idx={1} />
          </DepthBox>

          {/* الأوسط: صورة (يسار) + مسار (يمين) */}
          <DepthBox x={640} y={492} z={-150} rotY={27} w={272} h={482} delay={22} idx={2} camZ={cam.push}>
            <PhotoCard src="projects/TMB_001/plates/tmb_drums.jpg" w={272} h={482} frame={frame} />
          </DepthBox>

          <DepthBox x={1282} y={492} z={-150} rotY={-27} w={272} h={482} delay={28} idx={3} camZ={cam.push}>
            <RouteCard w={272} h={482} frame={frame} idx={3} />
          </DepthBox>

          {/* البطل — في البؤرة */}
          <DepthBox x={960} y={458} z={-15} rotY={0} w={374} h={664} delay={8} idx={4} camZ={cam.push}>
            <PhotoCard src="projects/TMB_001/plates/tmb_map.jpg" w={374} h={664} frame={frame} />
          </DepthBox>
        </AbsoluteFill>
      </AbsoluteFill>

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
        <div
          style={{
            width: 3,
            height: 38,
            borderRadius: 2,
            background: GOLD,
            boxShadow: `0 0 22px ${GOLD}`,
          }}
        />
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
        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            flexWrap: "wrap",
            gap: "0 0.25em",
          }}
        >
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
