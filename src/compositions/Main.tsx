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
import { getTextContainerStyle, backgroundImageStyle } from "../styles";

// ── الأصول البصرية للمشاهد الثلاثة (من Drive: Premium Trend Shorts Series) ──
import imgScene1 from "../../public/projects/PARADOX_012/assets/scene1_foggy_tower.jpg";
import imgScene2 from "../../public/projects/PARADOX_012/assets/scene2_golden_triad.jpg";
import imgScene3 from "../../public/projects/PARADOX_012/assets/scene3_oasis.jpg";

/**
 * 🎬 الحلقة 12 — «مفارقة الفلاح والنجاح» (PARADOX_012) — النسخة الأفقية 4K
 * المقاس: 3840×2160 (16:9) @ 30fps — المدة الفعلية 177.0s (5310 إطارات)
 *
 * 🔊 الصوت الحقيقي: مقصوص من المصدر على Google Drive (الأجزاء 20+21 من 27)
 *    القطاع 02:38:16.00 → 02:41:13.00 من بودكاست «بدون ورق — ياسر الحزيمي»
 *    (audio/voice.wav — مونو 48kHz، مُطبَّع ‎-16 LUFS وفق مستهدفات العلامة)
 *
 * 📝 مزامنة حقيقية: نص الترجمات العربية المدمجة في ملفات المصدر + محاذاة كلمات
 *    مضبوطة على موجة الصوت الفعلية — انظر meta.sync_method في ملف الطوابع.
 *
 * البنية السردية (حدود مثبّتة على محتوى الكلام الفعلي):
 *  - المشهد 1 (0.00–86.36)   [The Foggy Tower]         : سؤال الفلاح وأزمة معيار النجاح الغامض
 *  - المشهد 2 (86.36–127.52) [The Golden Triad]        : التعاريف اللغوية + «لديك سعي ووعي ووحي» (111.51s)
 *  - المشهد 3 (127.52–177.0) [The Oasis of Contentment]: «تعريف النجاح تحقيق ما تريده أنت، والفلاح ما يريده الله منك»
 *                                                        + الصدمة + فردوس عمر بن عبد العزيز الأرضي
 *
 * 🎵 الموسيقى: مسار خفيف مولّد بهوية العلامة الصوتية (عود + درون D + وسادة، حجاز على D)
 *    في audio/music.mp3 — يُخلط عند 10% تحت الصوت كما في القالب الأصلي.
 */
const ENABLE_MUSIC = true;

// حدود المشاهد بالثواني (مثبّتة على الكلام الفعلي — انظر meta في ملف الطوابع)
const S1_END_S = 86.36;
const S2_END_S = 127.52;

// ألوان هوية رِواق (brand.json — theme v1.4.0)
const INK = "#1C1B19";
const GOLD = "#A98A4B";
const GOLD_LIGHT = "#C2A469";

export const Main: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, durationInFrames } = useVideoConfig();

  const S1_END = Math.round(S1_END_S * fps);
  const S2_END = Math.round(S2_END_S * fps);
  const TOTAL = durationInFrames;
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
  // البان يُقاس نسبة إلى العرض (أساس تصميم 3840) ليبقى متناسبًا على أي دقة
  const u = width / 3840;
  const kenBurns = (from: number, to: number, scaleFrom: number, scaleTo: number, panX = -90, panY = -50) => {
    const t = interpolate(frame, [from, to], [0, 1], clamp);
    const scale = scaleFrom + (scaleTo - scaleFrom) * t;
    return `scale(${scale}) translate(${panX * u * t}px, ${panY * u * t}px)`;
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
      transform: kenBurns(S1_END - FADE_HALF, S2_END, 1.08, 1.0, 70, -36),
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

  // 🔊 منحنى مستوى الصوت: دخول ناعم 0.25s وخروج ناعم 0.4s على الصمت النهائي
  const fadeIn = Math.round(0.25 * fps);
  const fadeOut = Math.round(0.4 * fps);
  const voiceVolume = (f: number) =>
    interpolate(f, [0, fadeIn, TOTAL - fadeOut, TOTAL], [0, 1, 1, 0], clamp);
  const musicVolume = (f: number) => voiceVolume(f) * 0.1;

  // مقياس عناصر الهوية (مرجعية النظام: عرض 1080)
  const ui = width / 1080;

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
      <div style={getTextContainerStyle(width / 3840)}>
        {currentWords.map((w, index) => (
          <KineticWord
            key={`${activeFragment?.segment_id}_${index}`}
            word={w.word}
            startFrame={w.start_frame}
            endFrame={w.end_frame}
          />
        ))}
      </div>

      {/* 🔊 الصوت الأصلي للشيخ — بكامل القوة (مُطبَّع مسبقًا عند ‎-16 LUFS) */}
      <Audio src={staticFile("projects/PARADOX_012/audio/voice.wav")} volume={voiceVolume} />
      {/* 🎵 موسيقى تصويرية عند 10% — فعّلها عند توفر الملف */}
      {ENABLE_MUSIC ? (
        <Audio src={staticFile("projects/PARADOX_012/audio/music.mp3")} volume={musicVolume} />
      ) : null}

      {/* إطار رِواق الذهبي الرفيع — من الهوية */}
      <AbsoluteFill style={{ pointerEvents: "none" }}>
        <div
          style={{
            position: "absolute",
            inset: 18 * ui,
            border: `${Math.max(2, Math.round(0.75 * ui))}px solid ${GOLD}55`,
            boxSizing: "border-box",
          }}
        />
      </AbsoluteFill>

      {/* العلامة المائية الرسمية — مركيزة رِواق أعلى الوسط */}
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start", pointerEvents: "none" }}>
        <div style={{ marginTop: 60 * ui, opacity: 0.8 }}>
          <BrandMark sizePx={72 * ui} color={GOLD_LIGHT} />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
