import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { SCENES, SCENE_DUR } from "./scenes";
import { C } from "./kit";

/* ═══════════════════════════════════════════════════════════════════════════
   Longform — تركيب الحلقة الطويلة (1920×1080 · 30fps · 4:48)

   كل مشهد في <Sequence> مستقلة. الفيلم مقطوع من الأقسام مباشرة،
   والصوت ملف واحد (V3_full.wav) عشان التوقيت يبقى مرجع واحد.
   ═══════════════════════════════════════════════════════════════════════════ */

const FPS = 30;

export const SCENE_START: Record<number, number> = (() => {
  const out: Record<number, number> = {};
  let acc = 0;
  for (const { i } of SCENES) {
    out[i] = acc;
    acc += Math.round(SCENE_DUR[i] * FPS);
  }
  return out;
})();

export const TOTAL_FRAMES = (() => {
  let acc = 0;
  for (const { i } of SCENES) acc += Math.round(SCENE_DUR[i] * FPS);
  return acc;
})();

export const Longform: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: C.ink }}>
      {SCENES.map(({ i, Comp }) => {
        const dur = Math.round(SCENE_DUR[i] * FPS);
        return (
          <Sequence
            key={i}
            from={SCENE_START[i]}
            durationInFrames={dur}
            name={`S${String(i).padStart(2, "0")}`}
          >
            <Comp />
          </Sequence>
        );
      })}

      {/* ═══ الصوت V2 — ماستر ستيريو واحد ═══════════════════════════════════
          السرد (24 kHz) + موسيقى بـducking + SFX + ليمتر −1.5 dBTP
          اتخلط مسبقًا في scripts/audio_mix.py → −14 LUFS مدمج.
          ممنوع نضيف music.wav هنا تاني — هي مخلوطة جوه الملف.        */}
      <Audio src={staticFile("projects/TMB_001/audio/MIX_V2_full.mp4")} volume={1} />
    </AbsoluteFill>
  );
};
