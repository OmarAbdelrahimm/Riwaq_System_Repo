import React from "react";
import { AbsoluteFill, Sequence, staticFile, Audio, useCurrentFrame } from "remotion";
import { Backdrop, BigNumber, BigTitle, C, CTA, Dot, Grain, H, ip, KeyLine, Logo, Plate, Seam, TimeBar, Vignette, W } from "./kit";

/* ═══════════════════════════════════════════════════════════════════════════
   Short A — «الحريق»  ·  30 ثانية  ·  1080×1920
   ٢٥ يناير ٢٠١٣ → ٤٢٠٣ مخطوطة → المدينة خبّت ٣٥٠ ألف → وصلوا
   الإيقاع: قطع كل ١.٥–٢.٢ ثانية، أسرع من الطويل بمرتين.
   ═══════════════════════════════════════════════════════════════════════════ */

const FPS = 30;
const TOTAL = 30 * FPS; // 900 frames

/* ── 0.0–1.6 · الخطاف ───────────────────────────────────────────────────── */
const S01: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill>
      <Backdrop tint="deep" />
      <Plate src="projects/TMB_001/plates/tmb_smoke.jpg" from={0} w={W} h={H} y={H / 2} radius={0} kb={[1.06, 1.16]} grad={0.78} />
      <Grain />
      <Vignette />
      <BigTitle text="٢٥ يناير ٢٠١٣" from={4} size={96} color={C.parch} y={400} glow />
      <BigTitle text="مكتبة أحمد بابا" from={14} size={68} color={`${C.parch}d0`} y={540} />
      <BigTitle text="تمبكتو · مالي" from={24} size={46} color={`${C.stone}e0`} y={630} />
    </AbsoluteFill>
  );
};

/* ── 1.6–2.9 · كبّوا بنزين ──────────────────────────────────────────────── */
const S02: React.FC = () => (
  <AbsoluteFill>
    <Backdrop tint="cold" />
    <Plate src="projects/TMB_001/plates/tmb_empty.jpg" from={0} w={W} h={H} y={H / 2} radius={0} kb={[1.10, 1.02]} grad={0.72} />
    <Grain />
    <Vignette />
    <BigTitle text="مسلحين دخلوا." from={3} size={92} color={`${C.parch}d8`} y={600} />
    <BigTitle text="كبّوا بنزين." from={14} size={112} color={C.parch} y={740} glow />
  </AbsoluteFill>
);

/* ── 2.9–4.0 · وولّعوا ─────────────────────────────────────────────────── */
const S02b: React.FC = () => (
  <AbsoluteFill>
    <Backdrop tint="deep" />
    <Plate src="projects/TMB_001/plates/tmb_smoke.jpg" from={0} w={W} h={H} y={H / 2} radius={0} kb={[1.02, 1.14]} grad={0.66} />
    <Grain />
    <Vignette />
    <BigTitle text="وولّعوا." from={3} size={150} color={C.goldLight} y={700} glow />
  </AbsoluteFill>
);

/* ── 4.0–7.0 · ٤٢٠٣ ─────────────────────────────────────────────────────── */
const S03: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill>
      <Backdrop tint="deep" />
      <Plate src="projects/TMB_001/plates/tmb_smoke.jpg" from={0} kb={[1.14, 1.02]} grad={0.6} />
      <Grain />
      <Vignette />
      <BigNumber value="٤٢٠٣" from={4} size={300} y={470} />
      <KeyLine text="مخطوطة اتحرقت" from={30} size={74} color={C.parch} y={920} />
      <KeyLine text="في ليلة واحدة" from={54} size={52} color={`${C.stone}f0`} y={1010} />
      <Seam at={86} />
    </AbsoluteFill>
  );
};

/* ── 7.0–11.5 · لكن المدينة خبّت ─────────────────────────────────────────── */
const S04: React.FC = () => {
  return (
    <AbsoluteFill>
      <Backdrop tint="warm" />
      <Plate src="projects/TMB_001/plates/tmb_drums.jpg" from={0} kb={[1.02, 1.12]} grad={0.55} />
      <Grain />
      <Vignette />
      <BigTitle text="لكن أهل المدينة" from={4} size={78} color={C.parch} y={330} />
      <BigTitle text="خبّوا الكتب." from={20} size={112} color={C.goldLight} y={444} glow />
      <KeyLine text="في صناديق بنزين فاضية" from={64} size={54} color={`${C.parch}cc`} y={1300} />
      <KeyLine text="وعربيات دفع" from={88} size={54} color={`${C.parch}cc`} y={1374} />
    </AbsoluteFill>
  );
};

/* ── 11.5–16.0 · جنوبًا نحو باماكو ─────────────────────────────────────────────────── */
const S05: React.FC = () => {
  return (
    <AbsoluteFill>
      <Backdrop tint="cold" />
      <Plate src="projects/TMB_001/plates/tmb_route.jpg" from={0} kb={[1.0, 1.14]} grad={0.6} />
      <Grain />
      <Vignette />
      <BigTitle text="جنوبًا" from={6} size={150} color={C.parch} y={360} glow />
      <KeyLine text="نحو باماكو" from={30} size={76} color={C.goldLight} y={520} />
      <KeyLine text="عربيات ومراكب وقوافل" from={72} size={48} color={`${C.parch}cc`} y={1320} />
      <Dot from={112} />
    </AbsoluteFill>
  );
};

/* ── 16.0–19.0 · وصلت ───────────────────────────────────────────────────── */
const S06: React.FC = () => {
  return (
    <AbsoluteFill>
      <Backdrop tint="warm" />
      <Plate src="projects/TMB_001/plates/tmb_door.jpg" from={0} w={W} h={H} y={H / 2} radius={0} kb={[1.04, 1.12]} grad={0.66} />
      <Grain />
      <Vignette />
      <BigTitle text="الكتب وصلت." from={6} size={128} color={C.parch} y={380} glow />
    <BigTitle text="سليمة." from={30} size={168} color={C.goldLight} y={700} />
    </AbsoluteFill>
  );
};

/* ── 19.0–24.5 · الثمن ──────────────────────────────────────────────────── */
const S07: React.FC = () => {
  return (
    <AbsoluteFill>
      <Backdrop tint="deep" />
      <Plate src="projects/TMB_001/plates/tmb_hands.jpg" from={0} kb={[1.0, 1.10]} grad={0.6} />
      <Grain />
      <Vignette />
      <KeyLine text="والتلاتماية والخمسين ألف" from={4} size={54} color={`${C.parch}c8`} y={380} />
      <BigNumber value="٣٥٠" from={22} size={300} color={C.goldLight} y={640} label="ألف مخطوطة" labelColor={C.parch} />
      <KeyLine text="وصلوا باماكو." from={66} size={70} color={C.parch} y={1060} />
      <KeyLine text="واحدة واحدة." from={90} size={54} color={`${C.goldLight}d8`} y={1160} />
    </AbsoluteFill>
  );
};

/* ── ٢٠.٨–٢٥.٠ · ٣٥٠ ألف ──────────────────────────────────────────────── */
const S08: React.FC = () => (
  <AbsoluteFill>
    <Backdrop tint="warm" />
    <Plate src="projects/TMB_001/plates/tmb_boat.jpg" from={0} kb={[1.04, 1.14]} grad={0.62} />
    <Grain />
    <Vignette />
    <BigNumber value="٣٥٠" from={4} size={262} y={350} label="ألف مخطوطة" labelColor={C.parch} />
    <KeyLine text="اتنقلوا في سرية" from={52} size={56} color={`${C.goldLight}d8`} y={1000} />
  </AbsoluteFill>
);

/* ── ٢٢.٦–٢٦.٠ · خرائط الحفظ — يكمل بعد ما الصوت يسكت ─────────────────── */
const S08b: React.FC = () => (
  <AbsoluteFill>
    <Backdrop tint="warm" />
    <Plate src="projects/TMB_001/plates/tmb_route.jpg" from={0} kb={[1.0, 1.10]} grad={0.6} />
    <Grain />
    <Vignette />
    <BigTitle text="من تمبكتو" from={4} size={72} color={`${C.parch}c8`} y={420} />
    <BigTitle text="لباماكو." from={22} size={110} color={C.goldLight} y={540} glow />
    <KeyLine text="مسار النيجر" from={52} size={52} color={`${C.stone}e0`} y={1240} />
  </AbsoluteFill>
);

/* ── ٢٦.٠–٣٠.٠ · CTA ─────────────────────────────────────────────────── */
const S09: React.FC = () => (
  <AbsoluteFill>
    <Backdrop tint="deep" />
    <Plate src="projects/TMB_001/plates/tmb_hands.jpg" from={0} kb={[1.06, 1.0]} grad={0.66} />
    <Grain />
    <Vignette />
    <BigTitle text="الحكاية كلها" from={4} size={88} color={C.parch} y={330} />
    <BigTitle text="في الحلقة الكاملة" from={18} size={58} color={`${C.goldLight}d8`} y={460} />
    <CTA from={34} />
  </AbsoluteFill>
);

/* ═══════════════════════════════════════════════════════════════════════════
   البناء
   ═══════════════════════════════════════════════════════════════════════════ */
type Beat = { at: number; dur: number; Comp: React.FC };

const BEATS: Beat[] = [
  // التوقيت مقاس من silencedetect على shortA_vo.mp3 (9 جمل)
  { at: 0, dur: 70, Comp: S01 }, // 0.00–2.33
  { at: 70, dur: 110, Comp: S02 }, // 2.33–6.00
  { at: 180, dur: 90, Comp: S02b }, // 6.00–9.00
  { at: 270, dur: 145, Comp: S03 }, // 9.00–13.83
  { at: 415, dur: 108, Comp: S04 }, // 13.83–17.43
  { at: 523, dur: 32, Comp: S05 }, // 17.43–18.50
  { at: 555, dur: 28, Comp: S06 }, // 18.50–19.43
  { at: 583, dur: 36, Comp: S07 }, // 19.43–20.63
  { at: 619, dur: 59, Comp: S08 }, // 20.63–22.60 (آخر جملة)
  { at: 678, dur: 102, Comp: S08b }, // 22.60–26.00 (الصوت ساكت — موسيقى بس)
  { at: 780, dur: 120, Comp: S09 }, // 26.00–30.00 CTA
];

export const ShortA: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: C.ink }}>
      {BEATS.map((b, i) => (
        <Sequence key={i} from={b.at} durationInFrames={b.dur} name={`A${i + 1}`}>
          <b.Comp />
        </Sequence>
      ))}
      <TimeBar total={TOTAL} />
      {/* مكس V2: سرد معالج + موسيقى بـducking + −14 LUFS · −1.5 dBTP */}
      <Audio src={staticFile("projects/TMB_001/audio/SHORT_A_MIX_V2.mp4")} volume={1} />
    </AbsoluteFill>
  );
};

export const SHORT_A_FRAMES = TOTAL;
