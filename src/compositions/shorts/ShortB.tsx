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
      <KeyLine text="قوارب على النيجر" from={104} size={52} color={`${C.parch}c8`} y={1390} />
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
      <KeyLine text="واللي راح؟" from={4} size={68} color={`${C.parch}c0`} y={380} />
      <BigNumber value="٤٢٠٣" from={20} size={230} color={`${C.burgundy}`} y={660} />
      <KeyLine text="مخطوطة." from={58} size={76} color={C.parch} y={1000} />
      <KeyLine text="مش أكتر." from={80} size={64} color={`${C.goldLight}d8`} y={1120} />
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

/* ── ٢٢.٧٧–٢٥.٥ · الرقم ──────────────────────────────────────────────── */
const S09: React.FC = () => (
  <AbsoluteFill>
    <Backdrop tint="warm" />
    <Plate src="projects/TMB_001/plates/tmb_hands.jpg" from={0} kb={[1.04, 1.06]} grad={0.64} />
    <Grain />
    <Vignette />
    <BigNumber value="٣٥٠" from={2} size={250} color={C.goldLight} y={400} label="ألف مخطوطة" labelColor={C.parch} />
  </AbsoluteFill>
);

/* ── ٢٥.٥–٢٨.٥ · المعنى ──────────────────────────────────────────────── */
const S09b: React.FC = () => (
  <AbsoluteFill>
    <Backdrop tint="deep" />
    <Plate src="projects/TMB_001/plates/tmb_route.jpg" from={0} kb={[1.0, 1.10]} grad={0.64} />
    <Grain />
    <Vignette />
    <BigTitle text="نجت." from={2} size={190} color={C.goldLight} y={520} glow />
    <KeyLine text="والتاريخ فضل." from={26} size={64} color={`${C.parch}d8`} y={800} />
  </AbsoluteFill>
);

/* ── ٢٨.٥–٣٢.٠ · CTA ─────────────────────────────────────────────────── */
const S09c: React.FC = () => (
  <AbsoluteFill>
    <Backdrop tint="deep" />
    <Plate src="projects/TMB_001/plates/tmb_empty.jpg" from={0} kb={[1.06, 1.0]} grad={0.68} />
    <Grain />
    <Vignette />
    <BigTitle text="الحكاية كلها" from={2} size={86} color={C.parch} y={340} />
    <BigTitle text="في الحلقة الكاملة" from={14} size={56} color={`${C.goldLight}d8`} y={470} />
    <CTA from={26} />
  </AbsoluteFill>
);

const BEATS: { at: number; dur: number; Comp: React.FC }[] = [
  // التوقيت مقاس من silencedetect على shortB_vo.mp3
  { at: 0, dur: 82, Comp: S01 }, // 0.00–2.73
  { at: 82, dur: 66, Comp: S02 }, // 2.73–4.93
  { at: 148, dur: 72, Comp: S02b }, // 4.93–7.33
  { at: 220, dur: 65, Comp: S03 }, // 7.33–9.50
  { at: 285, dur: 80, Comp: S03b }, // 9.50–12.17
  { at: 365, dur: 172, Comp: S04 }, // 12.17–17.90
  { at: 537, dur: 30, Comp: S05 }, // 17.90–18.90
  { at: 567, dur: 30, Comp: S06 }, // 18.90–19.90
  { at: 597, dur: 46, Comp: S07 }, // 19.90–21.43
  { at: 643, dur: 40, Comp: S08 }, // 21.43–22.77
  { at: 683, dur: 82, Comp: S09 }, // 22.77–25.50 (الصوت ساكت — موسيقى)
  { at: 765, dur: 90, Comp: S09b }, // 25.50–28.50
  { at: 855, dur: 105, Comp: S09c }, // 28.50–32.00 CTA
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
      {/* مكس V2: سرد معالج + موسيقى بـducking + −14 LUFS · −1.5 dBTP */}
      <Audio src={staticFile("projects/TMB_001/audio/SHORT_B_MIX_V2.mp4")} volume={1} />
    </AbsoluteFill>
  );
};

export const SHORT_B_FRAMES = TOTAL;
