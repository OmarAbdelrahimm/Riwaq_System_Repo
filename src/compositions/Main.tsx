import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import subtitleData from "../../public/projects/PARADOX_012/timestamps_paradox.json";
import { KineticWord } from "../components/KineticWord";
import { BrandMark } from "../components/BrandMark";
import { textContainerStyle, backgroundImageStyle } from "../styles";

// ── الأصول البصرية للمشاهد الثلاثة (من Drive: Premium Trend Shorts Series) ──
import imgScene1 from "../../public/projects/PARADOX_012/assets/scene1_foggy_tower.jpg";
import imgScene2 from "../../public/projects/PARADOX_012/assets/scene2_golden_triad.jpg";
import imgScene3 from "../../public/projects/PARADOX_012/assets/scene3_oasis.jpg";

/**
 * 🎬 الحلقة 12 — «مفارقة الفلاح والنجاح» (PARADOX_012)
 * المدة المستهدفة: 3:20 (6000 إطار @ 30fps) — مقاس 1080×1920 (شورتس 9:16)
 * المصدر الصوتي: المقطع الأصلي 02:38:16 → 02:41:11 من بودكاست «بدون ورق — ياسر الحزيمي»
 *
 * البنية السردية:
 *  - المشهد 1 (0:00–1:10) [The Foggy Tower]        : أزمة معايير النجاح الحديثة
 *  - المشهد 2 (1:10–2:10) [The Golden Triad]        : ثلاثية التحقق — سعي، وعي، وحي
 *  - المشهد 3 (2:10–3:20) [The Oasis of Contentment]: الصدمة — النجاح الدنيوي قمة الفشل + فردوس عمر بن عبد العزيز
 *
 * 🔊 الصوت: ضع الملفات في public/projects/PARADOX_012/audio/ (انظر README.md هناك)
 *    ثم فعّل ENABLE_AUDIO. الصوت النقي 1.0 والموسيقى 0.10 لمنع التداخل.
 */
const ENABLE_AUDIO = false;

// ألوان هوية رِواق (brand.json — theme v1.4.0)
const INK = "#1C1B19";
const GOLD = "#A98A4B";
const GOLD_LIGHT = "#C2A469";

export const Main: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // حدود المشاهد بالفريمات (مشتقة من fps)
  const S1_END = Math.round(70 * fps); // 1:10 → 2100
  const S2_END = Math.round(130 * fps); // 2:10 → 3900
  const TOTAL = Math.round(200 * fps); // 3:20 → 6000
  const FADE_HALF = Math.round(1.5 * fps); // نافذة تقاطع 3 ثوانٍ حول كل حد

  // ── شفافية المشاهد (تقاطع ناعم — الـ Sequences متداخلة بنفس النوافذ) ──
  const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
  const scene1Opacity = interpolate(frame, [S1_END - FADE_HALF, S1_END + FADE_HALF], [1, 0], clamp);
  const scene2Opacity = Math.min(
    interpolate(frame, [S1_END - FADE_HALF, S1_END + FADE_HALF], [0, 1], clamp),
    interpolate(frame, [S2_END - FADE_HALF, S2_END + FADE_HALF], [1, 0], clamp)
  );
  const scene3Opacity = interpolate(frame, [S2_END - FADE_HALF, S2_END + FADE_HALF], [0, 1], clamp);

  // ── كاميرا كين بيرنز مستقلة لكل مشهد (زووم بطيء + بان خفيف) ──
  const kenBurns = (from: number, to: number, scaleFrom: number, scaleTo: number, panX = -24, panY = -14) => {
    const t = interpolate(frame, [from, to], [0, 1], clamp);
    const scale = scaleFrom + (scaleTo - scaleFrom) * t;
    return `scale(${scale}) translate(${panX * t}px, ${panY * t}px)`;
  };

  // 📝 الفقرة النشطة وكلماتها من ملف الطوابع الزمنية (مزامنة على مستوى الكلمة)
  const activeFragment = subtitleData.fragments.find(
    (f) => frame >= f.start_frame && frame <= f.end_frame
  );
  const currentWords = activeFragment ? activeFragment.words : [];

  // طبقات تدرّج لقراءة النصوص فوق كل مشهد
  const overlays = [
    `linear-gradient(180deg, rgba(28,27,25,0.25) 0%, rgba(28,27,25,0.45) 55%, rgba(28,27,25,0.82) 100%)`,
    `linear-gradient(180deg, rgba(28,27,25,0.15) 0%, rgba(28,27,25,0) 35%, rgba(28,27,25,0.55) 72%, rgba(28,27,25,0.85) 100%), radial-gradient(ellipse at center, rgba(194,164,105,0.08) 0%, rgba(28,27,25,0.45) 75%)`,
    `linear-gradient(180deg, rgba(194,164,105,0.10) 0%, rgba(94,34,48,0.15) 50%, rgba(28,27,25,0.65) 100%)`,
  ];

  const scenes = [
    {
      img: imgScene1,
      name: "Scene1_FoggyTower",
      alt: "Scene 1: The Foggy Tower — برج زجاجي يختفي في السحاب",
      from: 0,
      duration: S1_END + FADE_HALF,
      opacity: scene1Opacity,
      transform: kenBurns(0, S1_END, 1.0, 1.08),
      overlay: overlays[0],
    },
    {
      img: imgScene2,
      name: "Scene2_GoldenTriad",
      alt: "Scene 2: The Golden Triad — سعي، وعي، وحي",
      from: S1_END - FADE_HALF,
      duration: S2_END + FADE_HALF - (S1_END - FADE_HALF),
      opacity: scene2Opacity,
      transform: kenBurns(S1_END - FADE_HALF, S2_END, 1.08, 1.0, 20, -10),
      overlay: overlays[1],
    },
    {
      img: imgScene3,
      name: "Scene3_Oasis",
      alt: "Scene 3: The Oasis of Contentment — واحة مخفية في الصحراء",
      from: S2_END - FADE_HALF,
      duration: TOTAL - (S2_END - FADE_HALF),
      opacity: scene3Opacity,
      transform: kenBurns(S2_END - FADE_HALF, TOTAL, 1.0, 1.1),
      overlay: overlays[2],
    },
  ];

  return (
    <AbsoluteFill style={{ backgroundColor: INK, overflow: "hidden" }}>
      {/* 🖼️ المشاهد الثلاثة — خلفيات متحركة بتقاطع ناعم */}
      {scenes.map((s) => (
        <Sequence key={s.name} from={s.from} durationInFrames={s.duration} name={s.name}>
          <AbsoluteFill style={{ opacity: s.opacity }}>
            <div style={{ width: "100%", height: "100%", transform: s.transform, transformOrigin: "center center" }}>
              <img src={s.img} style={backgroundImageStyle} alt={s.alt} />
            </div>
            <AbsoluteFill style={{ background: s.overlay, pointerEvents: "none" }} />
          </AbsoluteFill>
        </Sequence>
      ))}

      {/* 📝 طبقة النصوص الكينتيكية المتزامنة كلمةً بكلمة */}
      <div style={textContainerStyle}>
        {currentWords.map((w, index) => (
          <KineticWord
            key={`${activeFragment?.segment_id}_${index}`}
            word={w.word}
            startFrame={w.start_frame}
            endFrame={w.end_frame}
          />
        ))}
      </div>

      {/* 🔊 الصوت — التعليق الرسمي بكامل القوة + موسيقى 10% (فعّل عند جاهزية الملفات) */}
      {ENABLE_AUDIO ? (
        <>
          <Audio src={staticFile("projects/PARADOX_012/audio/voice.wav")} volume={1.0} />
          <Audio src={staticFile("projects/PARADOX_012/audio/music.mp3")} volume={0.1} />
        </>
      ) : null}

      {/* إطار رِواق الذهبي الرفيع — من الهوية */}
      <AbsoluteFill style={{ pointerEvents: "none" }}>
        <div
          style={{
            position: "absolute",
            inset: 18,
            border: `2px solid ${GOLD}55`,
            boxSizing: "border-box",
          }}
        />
      </AbsoluteFill>

      {/* العلامة المائية الرسمية — مركيزة رِواق أعلى الوسط */}
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start", pointerEvents: "none" }}>
        <div style={{ marginTop: 60, opacity: 0.8 }}>
          <BrandMark sizePx={72} color={GOLD_LIGHT} />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
