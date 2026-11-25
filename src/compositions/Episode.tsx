import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile, useVideoConfig } from "remotion";
import type { Brand, EpisodeMeta, Scene } from "../engine/types";
import { ThemeProvider, aspectOf, useTheme } from "../engine/theme";
import { secToFrames } from "../engine/timing";
import { Paper, GoldFrame } from "../components/Paper";
import { Watermark } from "../components/Watermark";
import { Captions } from "../components/Captions";
import { HookFrame } from "../components/HookFrame";
import { ChapterCard } from "../components/ChapterCard";
import { QuoteCard } from "../components/QuoteCard";
import { StatCard } from "../components/StatCard";
import { LowerThird } from "../components/LowerThird";
import { SourceCard } from "../components/SourceCard";
import { EndScreen } from "../components/EndScreen";
import { VisualLayer } from "../components/VisualLayer";
import { SceneTitle } from "../components/SceneTitle";
import { KeywordPop } from "../components/KeywordPop";
import { TimelineBar } from "../components/TimelineBar";
import { Transition } from "../components/Transition";
import { ProgressBar } from "../components/ProgressBar";
import { ConceptFrame, ConceptMorph } from "../components/ConceptMorph";
import { MapSchematic } from "../components/MapSchematic";
import { Bars } from "../components/Bars";
import { SplitScreen } from "../components/SplitScreen";
import type { Overlay } from "../engine/types";

const dbToVol = (db = 0) => Math.pow(10, db / 20);

const SceneRenderer: React.FC<{ scene: Scene; durFrames: number }> = ({ scene, durFrames }) => {
  switch (scene.type) {
    case "hook":
      return <HookFrame kicker={scene.kicker} title={scene.title ?? ""} durFrames={durFrames} />;
    case "chapter":
      return <ChapterCard kicker={scene.kicker} title={scene.title ?? ""} durFrames={durFrames} />;
    case "quote":
      return <QuoteCard text={scene.text ?? ""} source={scene.source} durFrames={durFrames} />;
    case "stat":
      return <StatCard number={scene.number ?? ""} label={scene.label ?? ""} durFrames={durFrames} />;
    case "lower_third":
      return <LowerThird name={scene.name ?? ""} role={scene.role} durFrames={durFrames} />;
    case "source":
      return <SourceCard label={scene.value ? scene.label : undefined} value={scene.value ?? ""} durFrames={durFrames} />;
    case "end":
      return <EndScreen durFrames={durFrames} />;
    default:
      return null;
  }
};

const Scrim: React.FC<{ on?: boolean; children: React.ReactNode }> = ({ on, children }) => {
  const { color } = useTheme();
  return (
    <AbsoluteFill>
      {on ? <AbsoluteFill style={{ background: color("ink_deep"), opacity: 0.62 }} /> : null}
      {children}
    </AbsoluteFill>
  );
};

/** عناصر الطبقة الرسومية — كلها من البيانات */
const OverlayRenderer: React.FC<{ o: Overlay; durFrames: number }> = ({ o, durFrames }) => {
  const { type, t_in, t_out, scrim, ...p } = o;
  switch (type) {
    case "scene_title":
      return <SceneTitle {...(p as any)} scrim={scrim} durFrames={durFrames} />;
    case "keyword":
      return <KeywordPop {...(p as any)} scrim={scrim} durFrames={durFrames} />;
    case "timeline":
      return <Scrim on={scrim}><TimelineBar {...(p as any)} durFrames={durFrames} /></Scrim>;
    case "map":
      return <MapSchematic {...(p as any)} durFrames={durFrames} />;
    case "bars":
      return <Bars {...(p as any)} durFrames={durFrames} />;
    case "split":
      return <SplitScreen {...(p as any)} durFrames={durFrames} />;
    case "morph":
      return <ConceptMorph {...(p as any)} durFrames={durFrames} />;
    case "quote":
      return <Scrim on={scrim}><QuoteCard text={p.text} source={p.source} durFrames={durFrames} /></Scrim>;
    case "stat":
      return <Scrim on={scrim}><StatCard number={p.number} label={p.label} durFrames={durFrames} /></Scrim>;
    case "lower_third":
      return <LowerThird name={p.name} role={p.role} durFrames={durFrames} />;
    case "source":
      return <Scrim on={scrim}><SourceCard label={p.label} value={p.value} durFrames={durFrames} /></Scrim>;
    case "end":
      return <EndScreen tease={p.tease} durFrames={durFrames} />;
    default:
      return null;
  }
};

const Timeline: React.FC<{ meta: EpisodeMeta }> = ({ meta }) => {
  const { fps } = useVideoConfig();
  const { safe, brand } = useTheme();
  const scenes = meta.story?.scenes ?? [];
  const total = Math.round((meta.edit?.duration_s ?? 30) * fps);

  return (
    <AbsoluteFill style={{ direction: "rtl" }}>
      {/* طبقة الـLook: ثابتة خلف كل المشاهد */}
      <Paper />

      {/* طبقة الصور (أرشيف + إعادة تصوّر) */}
      {(meta.visuals ?? []).map((v, i) => {
        const from = secToFrames(v.t_in, fps);
        const dur = Math.max(1, secToFrames(v.t_out, fps) - from);
        return (
          <Sequence key={`v${i}`} from={from} durationInFrames={dur} name={`img ${v.src.split("/").pop()}`}>
            <VisualLayer v={v} durFrames={dur} />
          </Sequence>
        );
      })}

      {/* المشاهد A–G */}
      {scenes.map((s, i) => {
        const from = secToFrames(s.t_in, fps);
        const dur = secToFrames(s.t_out - s.t_in, fps);
        return (
          <Sequence key={i} from={from} durationInFrames={dur} name={`${s.type}@${s.t_in}s`}>
            <SceneRenderer scene={s} durFrames={dur} />
          </Sequence>
        );
      })}

      {/* الطبقة الرسومية */}
      {(meta.overlays ?? []).map((o, i) => {
        const from = secToFrames(o.t_in, fps);
        const dur = Math.max(1, secToFrames(o.t_out, fps) - from);
        return (
          <Sequence key={`o${i}`} from={from} durationInFrames={dur} name={`${o.type}@${o.t_in.toFixed(1)}s`}>
            <OverlayRenderer o={o} durFrames={dur} />
          </Sequence>
        );
      })}

      {/* الكابشنز — مستقلة عن المشاهد، من البيانات (burn_in=false → SRT فقط) */}
      {(meta.captions?.burn_in === false ? [] : meta.captions?.data ?? []).map((line, i) => {
        const from = secToFrames(line.t_in, fps);
        const dur = secToFrames(line.t_out - line.t_in, fps);
        return (
          <Sequence key={`c${i}`} from={from} durationInFrames={dur} name={`caption ${i + 1}`}>
            <Captions line={line} style={(meta.captions?.styles?.[0] as any) ?? "keyword_highlight"} />
          </Sequence>
        );
      })}

      {/* الإطار الذهبي + العلامة المائية */}
      {meta.fiction ? <ConceptFrame ranges={meta.fiction} /> : <GoldFrame />}
      {meta.progress ? (
        <ProgressBar chapters={meta.progress.chapters} total_s={meta.edit?.duration_s ?? total / fps} fictionRanges={meta.fiction ?? []} />
      ) : null}
      {(meta.transitions ?? []).map((tr, i) => {
        const len = Math.max(2, Math.round(0.2 * fps));
        return (
          <Sequence key={`tr${i}`} from={Math.max(0, secToFrames(tr.t, fps) - Math.round(len / 2))} durationInFrames={len} name={`transition ${tr.type}`}>
            <Transition type={tr.type} durFrames={len} />
          </Sequence>
        );
      })}
      {meta.brand_ref.watermark === "on" ? (
        (() => {
          // العلامة المائية تختفي خلال شاشة النهاية (الشعار الرسمي ظاهر فيها) لتجنّب تكرار الشعار
          const end = (meta.overlays ?? []).find((o) => o.type === "end");
          const until = end ? secToFrames(end.t_in, fps) : total;
          return (
            <Sequence from={0} durationInFrames={Math.max(1, until)} name="watermark">
              <Watermark />
            </Sequence>
          );
        })()
      ) : null}

      {/* الصوت: التعليق الرسمي + الموسيقى + النغمات (من الإعدادات) */}
      {(meta.audio?.vo ?? []).map((v, i) => (
        <Sequence key={`vo${i}`} from={secToFrames(v.t_in, fps)} name={`VO ${i + 1}`}>
          <Audio src={staticFile(v.src)} volume={dbToVol(v.volume_db)} />
        </Sequence>
      ))}
      {meta.audio?.music ? (
        <Audio
          src={staticFile(meta.audio.music.src)}
          volume={dbToVol(meta.audio.music.volume_db)}
          startFrom={0}
        />
      ) : null}
      {(meta.audio?.stingers ?? []).map((s, i) => (
        <Sequence key={`st${i}`} from={secToFrames(s.t_in, fps)} name={`stinger ${i + 1}`}>
          <Audio src={staticFile(s.src)} volume={dbToVol(s.volume_db)} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

export const Episode: React.FC<{ meta: EpisodeMeta; brand: Brand }> = ({ meta, brand }) => {
  const { width, height } = useVideoConfig();
  const aspect = aspectOf(width, height, meta.project.aspect_ratios);
  return (
    <ThemeProvider brand={brand} width={width} height={height} aspect={aspect}>
      <Timeline meta={meta} />
    </ThemeProvider>
  );
};
