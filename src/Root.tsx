import React from "react";
import { Composition } from "remotion";
import { Episode } from "./compositions/Episode";
import { Main } from "./compositions/Main";
import { Thumbnail, ThumbnailVertical } from "./compositions/Thumbnail";
import type { Brand, EpisodeMeta } from "./engine/types";
import brandJson from "../data/brand.json";
import goldenJson from "../data/projects/GOLDEN_001/episode_meta.json";

const brand = brandJson as unknown as Brand;
const golden = goldenJson as unknown as EpisodeMeta;

const lastSceneEnd = (meta: EpisodeMeta) =>
  Math.max(
    meta.edit?.duration_s ?? 0,
    ...(meta.story?.scenes ?? []).map((s) => s.t_out),
    1
  );

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* التكوين الأصلي للفيديو الذهبي التجريبي */}
      <Composition
        id="Episode"
        component={Episode as React.ComponentType<any>}
        durationInFrames={30 * 42}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ meta: golden, brand }}
        calculateMetadata={({ props }: any) => {
          const meta: EpisodeMeta = props.meta;
          const fps = meta.edit?.fps ?? 30;
          const [w, h] = meta.render?.resolution ?? [1080, 1920];
          return {
            fps,
            width: w,
            height: h,
            durationInFrames: Math.round(lastSceneEnd(meta) * fps),
          };
        }}
      />

      {/* الحلقة 12 - مفارقة الفلاح والنجاح (Main.tsx) — المشروع PARADOX_012 — أفقي 4K */}
      <Composition
        id="PARADOX-012"
        component={Main}
        durationInFrames={5310} // المدة الفعلية للصوت المقصوص: 177.0 ثانية × 30 إطار/ثانية
        fps={30}
        width={3840}
        height={2160}
        defaultProps={{}}
      />

      {/* غلاف يوتيوب للحلقة 12 — نسختان 1280×720 بصورة الشيخ من المصدر الأصلي */}
      <Composition
        id="Thumb-PARADOX-012-A"
        component={Thumbnail}
        durationInFrames={1}
        fps={30}
        width={1280}
        height={720}
        defaultProps={{ variant: "A" as const }}
      />
      <Composition
        id="Thumb-PARADOX-012-B"
        component={Thumbnail}
        durationInFrames={1}
        fps={30}
        width={1280}
        height={720}
        defaultProps={{ variant: "B" as const }}
      />

      {/* غلاف Shorts عمودي للحلقة 12 — نسختان 1080×1920 بنفس الهوية واللقطات */}
      <Composition
        id="Shorts-PARADOX-012-A"
        component={ThumbnailVertical}
        durationInFrames={1}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ variant: "A" as const }}
      />
      <Composition
        id="Shorts-PARADOX-012-B"
        component={ThumbnailVertical}
        durationInFrames={1}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ variant: "B" as const }}
      />

      {/* غلاف مقطع «التواصل والعلاقة» (TAWASUL_001) — أفقي 1280×720 بلقطة من نفس حلقة «مركزية العلاقة مع الله» */}
      <Composition
        id="Thumb-TAWASUL"
        component={Thumbnail}
        durationInFrames={1}
        fps={30}
        width={1280}
        height={720}
        defaultProps={{ variant: "C" as const }}
      />
    </>
  );
};
