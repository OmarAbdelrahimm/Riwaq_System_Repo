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
      <BigTitle text="٢٥ يناير ٢٠١٣" from={4} size={96} color={C.parch} y={420} glow />
      <BigTitle text="مكتبة أحمد بابا" from={16} size={64} color={`${C.parch}d0`} y={560} />
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
    <BigTitle text="كبّوا بنزين." from={4} size={118} color={C.parch} y={700} glow />
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
      <Plate src="projects/TMB_001/plates/tmb_smoke.jpg" from={0} w={960} h={760} y={1420} kb={[1.14, 1.02]} grad={0.6} />
      <Grain />
      <Vignette />
      <BigNumber value="٤٢٠٣" from={4} size={330} y={520} />
      <KeyLine text="مخطوطة. راحت." from={34} size={68} color={C.parch} y={1000} />
      <Seam at={86} />
    </AbsoluteFill>
  );
};

/* ── 7.0–11.5 · لكن المدينة خبّت ─────────────────────────────────────────── */
const S04: React.FC = () => {
  return (
    <AbsoluteFill>
      <Backdrop tint="warm" />
      <Plate src="projects/TMB_001/plates/tmb_drums.jpg" from={0} w={W - 80} h={1120} y={900} kb={[1.02, 1.12]} grad={0.55} />
      <Grain />
      <Vignette />
      <BigTitle text="لكن المدينة" from={4} size={88} color={C.parch} y={360} />
      <BigTitle text="خبّت الكتب." from={22} size={112} color={C.goldLight} y={470} glow />
      <KeyLine text="في صناديق زيت" from={70} size={58} color={`${C.parch}cc`} y={1330} />
      <KeyLine text="وعربيات دفع" from={92} size={58} color={`${C.parch}cc`} y={1390} />
    </AbsoluteFill>
  );
};

/* ── 11.5–16.0 · ٤٠٠ ميل ─────────────────────────────────────────────────── */
const S05: React.FC = () => {
  return (
    <AbsoluteFill>
      <Backdrop tint="cold" />
      <Plate src="projects/TMB_001/plates/tmb_route.jpg" from={0} w={W} h={980} y={760} kb={[1.0, 1.14]} grad={0.6} />
      <Grain />
      <Vignette />
      <BigNumber value="٤٠٠" from={6} size={290} y={380} label="ميل جنوبًا" labelColor={C.parch} />
      <KeyLine text="عربيات · مراكب · قوافل" from={80} size={54} color={`${C.parch}cc`} y={1330} />
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
      <BigTitle text="وصلت." from={6} size={188} color={C.parch} y={760} glow />
    </AbsoluteFill>
  );
};

/* ── 19.0–24.5 · الثمن ──────────────────────────────────────────────────── */
const S07: React.FC = () => {
  return (
    <AbsoluteFill>
      <Backdrop tint="deep" />
      <Plate src="projects/TMB_001/plates/tmb_hands.jpg" from={0} w={880} h={860} y={1440} kb={[1.0, 1.10]} grad={0.6} />
      <Grain />
      <Vignette />
      <KeyLine text="الخسارة؟" from={4} size={76} color={`${C.parch}c8`} y={430} />
      <BigNumber value="١٪" from={22} size={340} color={C.goldLight} y={700} />
      <KeyLine text="واحد في المية." from={70} size={66} color={C.parch} y={1120} />
    </AbsoluteFill>
  );
};

/* ── ٢٠.٨–٢٥.٠ · ٣٥٠ ألف ──────────────────────────────────────────────── */
const S08: React.FC = () => (
  <AbsoluteFill>
    <Backdrop tint="warm" />
    <Plate src="projects/TMB_001/plates/tmb_boat.jpg" from={0} w={900} h={720} y={960} kb={[1.04, 1.14]} grad={0.62} />
    <Grain />
    <Vignette />
    <BigNumber value="٣٥٠" from={4} size={270} y={380} label="ألف مخطوطة نجت" labelColor={C.parch} />
  </AbsoluteFill>
);

/* ── ٢٥.٠–٣٠.٠ · CTA ───────────────────────────────────────────────────── */
const S09: React.FC = () => (
  <AbsoluteFill>
    <Backdrop tint="deep" />
    <Plate src="projects/TMB_001/plates/tmb_hands.jpg" from={0} w={860} h={700} y={920} kb={[1.06, 1.0]} grad={0.66} />
    <Grain />
    <Vignette />
    <BigTitle text="الحكاية كلها" from={4} size={86} color={C.parch} y={340} />
    <CTA from={22} />
  </AbsoluteFill>
);

/* ═══════════════════════════════════════════════════════════════════════════
   البناء
   ═══════════════════════════════════════════════════════════════════════════ */
type Beat = { at: number; dur: number; Comp: React.FC };

const BEATS: Beat[] = [
  { at: 0, dur: 48, Comp: S01 }, //   0.0–1.6
  { at: 48, dur: 39, Comp: S02 }, //  1.6–2.9
  { at: 87, dur: 33, Comp: S02b }, // 2.9–4.0
  { at: 120, dur: 90, Comp: S03 }, //  4.0–7.0
  { at: 210, dur: 108, Comp: S04 }, //  7.0–10.6
  { at: 318, dur: 108, Comp: S05 }, // 10.6–14.2
  { at: 426, dur: 84, Comp: S06 }, // 14.2–17.0
  { at: 510, dur: 114, Comp: S07 }, // 17.0–20.8
  { at: 624, dur: 126, Comp: S08 }, // 20.8–25.0
  { at: 750, dur: 150, Comp: S09 }, // 25.0–30.0
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
      <Audio src={staticFile("projects/TMB_001/audio/music.wav")} volume={0.10} loop />
      <Audio src={staticFile("projects/TMB_001/audio/stinger_in.wav")} volume={0.5} />
    </AbsoluteFill>
  );
};

export const SHORT_A_FRAMES = TOTAL;
