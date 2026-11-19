import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame } from "remotion";
import { Backdrop, BigNumber, BigTitle, C, CTA, Dot, Grain, H, ip, KeyLine, Logo, Plate, Seam, TimeBar, Vignette, W } from "./kit";

/* ═══════════════════════════════════════════════════════════════════════════
   Short B — «أغلى من الدهب»  ·  32 ثانية  ·  1080×1920
   ١٥٢٦ · ليو أفريكانوس → الكتب أغلى من الدهب → المدينة راحت → الكتب فضلت
   الإيقاع: أسرع من الطويل، لكن أهدأ من Short A — إعجاب مش صدمة.
   ═══════════════════════════════════════════════════════════════════════════ */

const FPS = 30;
const TOTAL = 32 * FPS; // 960 frames

/* ── 0.0–2.0 · الخطاف: الاقتباس ────────────────────────────────────────── */
const S01: React.FC = () => {
  return (
    <AbsoluteFill>
      <Backdrop tint="warm" />
      <Plate src="projects/TMB_001/plates/tmb_gold.jpg" from={0} w={W} h={H} y={H / 2} radius={0} kb={[1.04, 1.14]} grad={0.7} />
      <Grain />
      <Vignette />
      <BigTitle text="سنة ١٥٢٦" from={4} size={72} color={`${C.parch}c8`} y={430} />
      <BigTitle text="ليو أفريكانوس" from={16} size={64} color={C.goldLight} y={530} />
    </AbsoluteFill>
  );
};

/* ── ١.٨–٤.٠ · السؤال ─────────────────────────────────────────────────── */
const S02: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill>
      <Backdrop tint="deep" />
      <Plate src="projects/TMB_001/plates/tmb_library.jpg" from={0} kb={[1.0, 1.10]} grad={0.62} />
      <Grain />
      <Vignette />
      <div
        style={{
          position: "absolute",
          top: 340,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
          opacity: ip(f, 6, 20, 0, 1),
          transform: `translateY(${ip(f, 6, 24, 28, 0)}px)`,
        }}
      >
        <div style={{ fontFamily: "Amiri", fontWeight: 400, fontSize: 120, color: `${C.goldLight}70`, lineHeight: 0.5 }}>
          ﴾
        </div>
      </div>
      <BigTitle text={"تجارة الكتب\nأربح من الدهب."} from={14} size={94} color={C.parch} y={520} glow />
      <KeyLine text="— ليو أفريكانوس" from={80} size={46} color={`${C.goldLight}d0`} y={1010} />
    </AbsoluteFill>
  );
};

/* ── ٤.٠–٥.٨ · الاقتباس كامل ──────────────────────────────────────────── */
const S02b: React.FC = () => (
  <AbsoluteFill>
    <Backdrop tint="deep" />
    <Plate src="projects/TMB_001/plates/tmb_library.jpg" from={0} kb={[1.06, 1.0]} grad={0.66} />
    <Grain />
    <Vignette />
    <BigTitle text={"تجارة الكتب\nأربح من الدهب."} from={2} size={90} color={C.parch} y={620} glow />
  </AbsoluteFill>
);

/* ── 6.5–11.0 · تخيل ────────────────────────────────────────────────────── */
const S03: React.FC = () => {
  return (
    <AbsoluteFill>
      <Backdrop tint="warm" />
      <Plate src="projects/TMB_001/plates/tmb_close.jpg" from={0} kb={[1.02, 1.14]} grad={0.56} />
      <Grain />
      <Vignette />
      <BigTitle text="الدهب كان أرخص" from={4} size={100} color={C.parch} y={380} glow />
      <KeyLine text="٣٥٠ ألف مخطوطة" from={28} size={58} color={C.parch} y={1330} />
    </AbsoluteFill>
  );
};

/* ── ٧.٦–٩.٤ · الورق ───────────────────────────────────────────────────── */
const S03b: React.FC = () => (
  <AbsoluteFill>
    <Backdrop tint="deep" />
    <Plate src="projects/TMB_001/plates/tmb_close.jpg" from={0} kb={[1.10, 1.0]} grad={0.6} />
    <Grain />
    <Vignette />
    <BigTitle text="من الورق." from={2} size={128} color={C.goldLight} y={760} glow />
  </AbsoluteFill>
);

/* ── 11.0–15.0 · المدينة راحت ───────────────────────────────────────────── */
const S04: React.FC = () => {
  return (
    <AbsoluteFill>
      <Backdrop tint="cold" />
      <Plate src="projects/TMB_001/plates/tmb_night.jpg" from={0} kb={[1.08, 1.0]} grad={0.64} />
      <Grain />
      <Vignette />
      <BigTitle text="المدينة راحت" from={6} size={92} color={`${C.parch}d8`} y={320} />
      <BigTitle text="أكتر من مرة." from={28} size={86} color={C.burgundy} y={432} />
      <Seam at={108} />
    </AbsoluteFill>
  );
};

/* ── 15.0–19.5 · لكن الكتب فضلت ─────────────────────────────────────────── */
const S05: React.FC = () => {
  return (
    <AbsoluteFill>
      <Backdrop tint="warm" />
      <Plate src="projects/TMB_001/plates/tmb_drums.jpg" from={0} kb={[1.0, 1.12]} grad={0.58} />
      <Grain />
      <Vignette />
      <BigTitle text="الكتب فضلت." from={8} size={132} color={C.goldLight} y={340} glow />
      <KeyLine text="صناديق زيت · عربيات دفع" from={80} size={52} color={`${C.parch}c8`} y={1330} />
      <KeyLine text="٤٠٠ ميل على النيجر" from={104} size={52} color={`${C.parch}c8`} y={1390} />
    </AbsoluteFill>
  );
};

/* ── 19.5–24.0 · واحد في المية ──────────────────────────────────────────── */
const S06: React.FC = () => {
  return (
    <AbsoluteFill>
      <Backdrop tint="deep" />
      <Plate src="projects/TMB_001/plates/tmb_empty.jpg" from={0} kb={[1.06, 1.0]} grad={0.66} />
      <Grain />
      <Vignette />
      <KeyLine text="اللي راح؟" from={4} size={68} color={`${C.parch}c0`} y={380} />
      <BigNumber value="١٪" from={20} size={330} color={C.goldLight} y={660} />
      <KeyLine text="بس." from={76} size={80} color={C.parch} y={1140} />
    </AbsoluteFill>
  );
};

/* ── 24.0–28.0 · الجملة اللي تفضل ───────────────────────────────────────── */
const S07: React.FC = () => {
  return (
    <AbsoluteFill>
      <Backdrop tint="warm" />
      <Plate src="projects/TMB_001/plates/tmb_hands.jpg" from={0} kb={[1.0, 1.10]} grad={0.6} />
      <Grain />
      <Vignette />
      <BigTitle text="حد لقى حاجة مهمة،" from={4} size={80} color={C.parch} y={420} />
      <BigTitle text="ومكانش عايز يسيبها تروح." from={26} size={72} color={C.goldLight} y={540} glow />
    </AbsoluteFill>
  );
};

/* ── ٢٣.٠–٢٧.٥ · الخاتمة ──────────────────────────────────────────────── */
const S08: React.FC = () => (
  <AbsoluteFill>
    <Backdrop tint="deep" />
    <Plate src="projects/TMB_001/plates/tmb_boat.jpg" from={0} kb={[1.06, 1.0]} grad={0.6} />
    <Grain />
    <Vignette />
    <BigTitle text="و دي رِواق .. سلاام" from={8} size={80} color={C.parch} y={400} glow />
    <Logo delay={12} small />
  </AbsoluteFill>
);

/* ── ٢٧.٥–٣٢.٠ · CTA ──────────────────────────────────────────────────── */
const S09: React.FC = () => (
  <AbsoluteFill>
    <Backdrop tint="warm" />
    <Plate src="projects/TMB_001/plates/tmb_hands.jpg" from={0} kb={[1.04, 1.0]} grad={0.64} />
    <Grain />
    <Vignette />
    <BigTitle text="٣٥٠ ألف" from={4} size={150} color={C.goldLight} y={330} glow />
    <BigTitle text="مخطوطة نجت" from={16} size={76} color={C.parch} y={520} />
    <CTA from={24} />
  </AbsoluteFill>
);

const BEATS: { at: number; dur: number; Comp: React.FC }[] = [
  { at: 0, dur: 54, Comp: S01 }, //    0.0–1.8
  { at: 54, dur: 66, Comp: S02 }, //   1.8–4.0
  { at: 120, dur: 54, Comp: S02b }, //  4.0–5.8
  { at: 174, dur: 54, Comp: S03 }, //   5.8–7.6
  { at: 228, dur: 54, Comp: S03b }, //  7.6–9.4
  { at: 282, dur: 96, Comp: S04 }, //  9.4–12.6
  { at: 378, dur: 102, Comp: S05 }, // 12.6–16.0
  { at: 480, dur: 108, Comp: S06 }, // 16.0–19.6
  { at: 588, dur: 102, Comp: S07 }, // 19.6–23.0
  { at: 690, dur: 135, Comp: S08 }, // 23.0–27.5
  { at: 825, dur: 135, Comp: S09 }, // 27.5–32.0
];

export const ShortB: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: C.ink }}>
      {BEATS.map((b, i) => (
        <Sequence key={i} from={b.at} durationInFrames={b.dur} name={`B${i + 1}`}>
          <b.Comp />
        </Sequence>
      ))}
      <TimeBar total={TOTAL} />
      <Audio src={staticFile("projects/TMB_001/audio/music.wav")} volume={0.09} loop />
    </AbsoluteFill>
  );
};

export const SHORT_B_FRAMES = TOTAL;
