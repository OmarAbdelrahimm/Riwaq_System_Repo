import React from "react";
import {
  AbsoluteFill,
  Audio,
  Loop,
  OffthreadVideo,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type { Brand, CaptionLine, EpisodeMeta } from "../engine/types";
import { ThemeProvider, useTheme } from "../engine/theme";
import { secToFrames } from "../engine/timing";
import { BrandMark } from "../components/BrandMark";
import { GoldFrame, Paper } from "../components/Paper";

export type RiwaqMotif = "exchange" | "shared_canvas" | "five_factors" | "context";

export interface NarrativeSection {
  id: string;
  t_in: number;
  t_out: number;
  kicker?: string;
  title: string;
  subtitle?: string;
  background?: string;
  motif?: RiwaqMotif;
}

export type NarrativeMeta = Omit<EpisodeMeta, "story"> & {
  story: NonNullable<EpisodeMeta["story"]> & {
    sections: NarrativeSection[];
  };
};

type Props = { meta: NarrativeMeta; brand: Brand };

const dbToVol = (db = 0) => Math.pow(10, db / 20);
const clamp = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };

const BrandAtmosphere: React.FC = () => {
  const { width, height } = useVideoConfig();
  const { color } = useTheme();
  const frame = useCurrentFrame();
  const glow = 0.05 + (Math.sin(frame * 0.018) + 1) * 0.012;

  return (
    <>
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse at 50% 49%, ${color("gold")}14 0%, transparent 60%)`,
          opacity: 0.8,
        }}
      />
      <div
        style={{
          position: "absolute",
          right: -width * 0.018,
          bottom: height * 0.11,
          opacity: glow,
          pointerEvents: "none",
        }}
      >
        <BrandMark sizePx={width * 0.24} color={color("gold_light")} />
      </div>
      <div
        style={{
          position: "absolute",
          left: width * 0.03,
          top: height * 0.18,
          width: width * 0.14,
          height: height * 0.64,
          borderLeft: `1px solid ${color("gold")}1a`,
          borderRight: `1px solid ${color("gold")}1a`,
          opacity: 0.45,
          pointerEvents: "none",
        }}
      />
    </>
  );
};

const ConceptGlyph: React.FC<{ motif?: RiwaqMotif; mirror?: boolean }> = ({ motif, mirror = false }) => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  const { color } = useTheme();
  const pulse = 0.78 + Math.sin(frame * 0.055) * 0.1;
  const gold = color("gold_light");
  const pale = color("parchment2");

  return (
    <svg
      width={width * 0.074}
      height={width * 0.074}
      viewBox="0 0 140 140"
      style={{
        display: "block",
        overflow: "visible",
        opacity: mirror ? 0.72 : 1,
        transform: mirror ? "scaleX(-1)" : undefined,
      }}
      aria-hidden="true"
    >
      <g fill="none" stroke={gold} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        {motif === "shared_canvas" ? (
          <>
            <path d="M25 91 C43 67, 53 73, 68 54 S97 42, 116 25" strokeDasharray="4 7" opacity="0.72" />
            <path d="M24 111 C43 88, 62 94, 80 72 S106 62, 118 49" opacity="0.55" />
            <circle cx="27" cy="91" r="6" fill={gold} opacity={pulse} />
            <circle cx="116" cy="25" r="6" fill={pale} opacity={pulse} />
            <circle cx="80" cy="72" r="4" fill={gold} opacity="0.8" />
          </>
        ) : motif === "five_factors" ? (
          <>
            <circle cx="70" cy="70" r="27" strokeDasharray="3 6" opacity="0.75" />
            <path d="M70 22 L111 52 L96 105 L44 105 L29 52 Z" opacity="0.72" />
            <path d="M70 43 L70 22 M95 62 L111 52 M87 92 L96 105 M53 92 L44 105 M45 62 L29 52" opacity="0.7" />
            <circle cx="70" cy="22" r="5" fill={gold} opacity={pulse} />
            <circle cx="111" cy="52" r="5" fill={pale} opacity="0.9" />
            <circle cx="96" cy="105" r="5" fill={gold} opacity="0.8" />
            <circle cx="44" cy="105" r="5" fill={pale} opacity="0.9" />
            <circle cx="29" cy="52" r="5" fill={gold} opacity={pulse} />
            <circle cx="70" cy="70" r="4" fill={gold} stroke="none" />
          </>
        ) : motif === "context" ? (
          <>
            <path d="M31 112 C34 83, 48 66, 70 66 C92 66, 106 83, 109 112" opacity="0.68" />
            <path d="M43 54 C43 34, 55 23, 70 23 C85 23, 97 34, 97 54 C97 68, 85 77, 70 77 C55 77, 43 68, 43 54 Z" opacity="0.8" />
            <path d="M20 119 C26 78, 42 50, 70 42 C98 50, 114 78, 120 119" strokeDasharray="3 7" opacity={pulse} />
            <circle cx="70" cy="24" r="4" fill={gold} stroke="none" />
          </>
        ) : (
          <>
            <path d="M30 48 H72 Q82 48 82 58 V69 Q82 79 72 79 H51 L38 91 V79 H30 Q20 79 20 69 V58 Q20 48 30 48 Z" opacity="0.7" />
            <path d="M68 73 H107 Q117 73 117 83 V95 Q117 105 107 105 H97 L110 117 V105 H68 Q58 105 58 95 V83 Q58 73 68 73 Z" opacity="0.86" />
            <circle cx="40" cy="64" r="2.8" fill={gold} stroke="none" />
            <circle cx="51" cy="64" r="2.8" fill={gold} stroke="none" opacity={pulse} />
            <circle cx="81" cy="89" r="2.8" fill={pale} stroke="none" />
            <circle cx="92" cy="89" r="2.8" fill={pale} stroke="none" opacity={pulse} />
          </>
        )}
      </g>
      <circle cx="70" cy="70" r="61" fill="none" stroke={gold} strokeWidth="0.8" strokeDasharray="1 9" opacity="0.25" />
    </svg>
  );
};

const SideMotifs: React.FC<{ section: NarrativeSection }> = ({ section }) => {
  const { width, height } = useVideoConfig();

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          left: width * 0.036,
          top: height * 0.49,
          transform: "translateY(-50%)",
        }}
      >
        <ConceptGlyph motif={section.motif} />
      </div>
      <div
        style={{
          position: "absolute",
          right: width * 0.036,
          top: height * 0.49,
          transform: "translateY(-50%)",
        }}
      >
        <ConceptGlyph motif={section.motif} mirror />
      </div>
    </AbsoluteFill>
  );
};

const VideoFrameCorners: React.FC = () => {
  const { width } = useVideoConfig();
  const { color } = useTheme();
  const length = width * 0.016;
  const thickness = Math.max(2, width * 0.0014);
  const base: React.CSSProperties = {
    position: "absolute",
    width: length,
    height: length,
    pointerEvents: "none",
  };
  const corners: React.CSSProperties[] = [
    { top: 11, left: 11, borderTop: `${thickness}px solid ${color("gold_light")}`, borderLeft: `${thickness}px solid ${color("gold_light")}` },
    { top: 11, right: 11, borderTop: `${thickness}px solid ${color("gold_light")}`, borderRight: `${thickness}px solid ${color("gold_light")}` },
    { bottom: 11, left: 11, borderBottom: `${thickness}px solid ${color("gold_light")}`, borderLeft: `${thickness}px solid ${color("gold_light")}` },
    { bottom: 11, right: 11, borderBottom: `${thickness}px solid ${color("gold_light")}`, borderRight: `${thickness}px solid ${color("gold_light")}` },
  ];

  return (
    <>
      {corners.map((style, index) => (
        <div key={index} style={{ ...base, ...style }} />
      ))}
    </>
  );
};

const SourceVideo: React.FC<{ src: string }> = ({ src }) => {
  const { width, height } = useVideoConfig();
  const { color } = useTheme();
  const border = Math.max(2, width * 0.00125);

  return (
    <div
      style={{
        position: "absolute",
        left: width * 0.125,
        top: height * 0.1,
        width: width * 0.75,
        height: height * 0.75,
        boxSizing: "border-box",
        overflow: "hidden",
        border: `${border}px solid ${color("gold")}cc`,
        borderRadius: width * 0.006,
        backgroundColor: color("ink_deep"),
        boxShadow: "0 26px 64px rgba(0,0,0,.48), 0 0 0 6px rgba(28,27,25,.76)",
      }}
    >
      <OffthreadVideo
        src={staticFile(src)}
        muted
        startFrom={0}
        style={{
          display: "block",
          width: "100%",
          height: "100%",
          objectFit: "cover",
          objectPosition: "center",
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 7,
          border: `1px solid ${color("parchment2")}33`,
          borderRadius: width * 0.003,
          pointerEvents: "none",
        }}
      />
      <VideoFrameCorners />
    </div>
  );
};

const BrandHeader: React.FC<{
  meta: NarrativeMeta;
  section: NarrativeSection;
  sectionIndex: number;
}> = ({ meta, section, sectionIndex }) => {
  const frame = useCurrentFrame();
  const { width, durationInFrames } = useVideoConfig();
  const { color, headlineFont, bodyFont, brand } = useTheme();
  const progress = interpolate(frame, [0, Math.max(1, durationInFrames)], [0, 100], clamp);
  const sourceParts = String(meta.source?.title ?? "مركزية العلاقة مع الله | ياسر الحزيمي | بودكاست بدون ورق").split("|");
  const sourceTitle = sourceParts[0]?.trim() || "مركزية العلاقة مع الله";
  const sourceCredit = sourceParts.slice(1).map((part) => part.trim()).filter(Boolean).join(" · ") || "ياسر الحزيمي · بودكاست بدون ورق";
  const sectionNumber = String(sectionIndex + 1).padStart(2, "0");
  const totalSections = String(meta.story.sections.length).padStart(2, "0");
  const sourceBadge = "الصوت الأصلي";

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          top: width * 0.028,
          left: width * 0.045,
          right: width * 0.045,
          display: "grid",
          gridTemplateColumns: "1fr 1.2fr 1fr",
          alignItems: "center",
          direction: "rtl",
          minHeight: width * 0.025,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: width * 0.008, justifySelf: "start", direction: "rtl" }}>
          <BrandMark sizePx={width * 0.022} color={color("gold_light")} />
          <div>
            <div style={{ color: color("parchment"), fontFamily: headlineFont, fontSize: width * 0.014, fontWeight: 700, lineHeight: 1 }}>
              {brand.name_ar}
            </div>
            <div style={{ color: color("parchment2"), fontFamily: bodyFont, fontSize: width * 0.0075, opacity: 0.72, marginTop: 4 }}>
              {brand.tagline_ar}
            </div>
          </div>
        </div>

        <div style={{ textAlign: "center", lineHeight: 1.15 }}>
          <div style={{ color: color("gold_light"), fontFamily: bodyFont, fontSize: width * 0.0075, fontWeight: 700, marginBottom: 3 }}>
            {section.kicker ?? `الفصل ${sectionNumber} · ${sectionNumber}/${totalSections}`}
          </div>
          <div style={{ color: color("parchment"), fontFamily: headlineFont, fontSize: width * 0.0155, fontWeight: 700 }}>
            {section.title}
          </div>
        </div>

        <div style={{ textAlign: "left", direction: "rtl", lineHeight: 1.15 }}>
          <div style={{ color: color("parchment"), fontFamily: headlineFont, fontSize: width * 0.0135, fontWeight: 700 }}>
            {sourceTitle}
          </div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "flex-start", gap: width * 0.008, marginTop: 4 }}>
            <span style={{ color: color("parchment2"), fontFamily: bodyFont, fontSize: width * 0.0072, opacity: 0.72 }}>{sourceCredit}</span>
            <span
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 5,
                border: `1px solid ${color("gold")}88`,
                padding: `2px ${width * 0.004}px`,
                color: color("gold_light"),
                fontFamily: bodyFont,
                fontSize: width * 0.0068,
                whiteSpace: "nowrap",
              }}
            >
              <span style={{ display: "inline-block", width: 5, height: 5, borderRadius: 99, background: color("gold_light") }} />
              {sourceBadge}
            </span>
          </div>
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          top: width * 0.054,
          left: width * 0.045,
          right: width * 0.045,
          height: Math.max(2, width * 0.001),
          background: `linear-gradient(to left, ${color("gold_light")} ${progress}%, ${color("gold")}22 ${progress}%)`,
          opacity: 0.85,
        }}
      />
    </AbsoluteFill>
  );
};

const wrapWords = (text: string, maxChars = 44): string[][] => {
  const words = text.trim().split(/\s+/).filter(Boolean);
  const lines: string[][] = [];
  let line: string[] = [];
  let length = 0;

  for (const word of words) {
    const nextLength = length + (line.length ? 1 : 0) + word.length;
    if (line.length && nextLength > maxChars) {
      lines.push(line);
      line = [word];
      length = word.length;
    } else {
      line.push(word);
      length = nextLength;
    }
  }
  if (line.length) lines.push(line);

  if (lines.length <= 2) return lines;
  return [lines[0], lines.slice(1).flat()];
};

const KineticCaption: React.FC<{ line: CaptionLine }> = ({ line }) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const { color, bodyFont } = useTheme();
  const lines = wrapWords(line.ar);
  const words = lines.flat();
  const totalFrames = Math.max(1, secToFrames(line.t_out - line.t_in, fps));
  const framesPerWord = totalFrames / Math.max(1, words.length);
  const activeIndex = Math.min(words.length - 1, Math.floor(frame / framesPerWord));
  const activeStart = activeIndex * framesPerWord;
  const activeProgress = interpolate(frame, [activeStart, activeStart + Math.max(3, fps * 0.12)], [0, 1], clamp);
  const fadeIn = interpolate(frame, [0, Math.min(6, totalFrames)], [0, 1], clamp);
  const fadeOut = interpolate(frame, [Math.max(0, totalFrames - 6), totalFrames], [1, 0], clamp);
  const opacity = Math.min(fadeIn, fadeOut);

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          left: width * 0.125,
          right: width * 0.125,
          bottom: width * 0.036,
          minHeight: width * 0.042,
          boxSizing: "border-box",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          padding: `${width * 0.004}px ${width * 0.012}px`,
          border: `1px solid ${color("gold")}bb`,
          borderRadius: width * 0.004,
          background: "rgba(28,27,25,.94)",
          boxShadow: "0 10px 28px rgba(0,0,0,.36)",
          opacity,
          textAlign: "center",
          direction: "rtl",
        }}
      >
        <div
          style={{
            position: "absolute",
            top: 0,
            left: "18%",
            right: "18%",
            height: 1,
            background: `linear-gradient(90deg, transparent, ${color("gold_light")}99, transparent)`,
          }}
        />
        {lines.map((wordsInLine, lineIndex) => {
          let wordOffset = lines.slice(0, lineIndex).reduce((sum, current) => sum + current.length, 0);
          return (
            <div
              key={lineIndex}
              dir="rtl"
              style={{
                display: "flex",
                flexWrap: "nowrap",
                alignItems: "center",
                justifyContent: "center",
                minHeight: width * 0.017,
                fontFamily: bodyFont,
                fontSize: width * 0.016,
                lineHeight: 1.16,
                fontWeight: 700,
                whiteSpace: "nowrap",
              }}
            >
              {wordsInLine.map((word) => {
                const wordIndex = wordOffset++;
                const isActive = wordIndex === activeIndex;
                const scale = isActive ? 1 + activeProgress * 0.035 : 1;
                return (
                  <span
                    key={`${wordIndex}-${word}`}
                    style={{
                      display: "inline-block",
                      margin: `0 ${width * 0.0024}px`,
                      color: isActive ? color("gold_light") : color("parchment"),
                      opacity: isActive ? 1 : 0.82,
                      transform: `scale(${scale})`,
                      transformOrigin: "center",
                    }}
                  >
                    {word}
                  </span>
                );
              })}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const NarrativeAudio: React.FC<{ meta: NarrativeMeta }> = ({ meta }) => {
  const { fps } = useVideoConfig();
  const totalFrames = secToFrames(meta.edit?.duration_s ?? 270, fps);
  const sourceAudio = meta.audio?.source_audio;
  const music = meta.audio?.music;

  const sourceFrom = secToFrames(sourceAudio?.t_in ?? 0, fps);
  const sourceEnd = sourceAudio?.t_out ? secToFrames(sourceAudio.t_out, fps) : totalFrames;
  const sourceDuration = Math.max(1, Math.min(totalFrames - sourceFrom, sourceEnd - sourceFrom));

  const musicFrom = secToFrames(music?.t_in ?? 0, fps);
  const musicEnd = music?.t_out ? secToFrames(music.t_out, fps) : totalFrames;
  const musicDuration = Math.max(1, Math.min(totalFrames - musicFrom, musicEnd - musicFrom));

  return (
    <>
      {sourceAudio ? (
        <Sequence from={sourceFrom} durationInFrames={sourceDuration} name="Original source audio">
          <Audio src={staticFile(sourceAudio.src)} volume={dbToVol(sourceAudio.volume_db ?? 0)} />
        </Sequence>
      ) : null}
      {music ? (
        <Sequence from={musicFrom} durationInFrames={musicDuration} name="Quiet background music">
          <Loop durationInFrames={musicDuration}>
            <Audio src={staticFile(music.src)} volume={dbToVol(music.volume_db ?? -27)} />
          </Loop>
        </Sequence>
      ) : null}
    </>
  );
};

const NarrativeTimeline: React.FC<{ meta: NarrativeMeta }> = ({ meta }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sections = meta.story.sections;
  const seconds = frame / fps;
  const sectionIndex = Math.max(0, sections.findIndex((section) => seconds >= section.t_in && seconds < section.t_out));
  const activeSection = sections[sectionIndex] ?? sections[0];
  const sourcePath = meta.source?.local_path ?? "projects/RELATIONSHIP_001/source/relationship_source.mp4";

  return (
    <AbsoluteFill style={{ backgroundColor: "#1C1B19", overflow: "hidden" }}>
      <Paper grain={false}>
        <BrandAtmosphere />
        <SideMotifs section={activeSection} />
        <SourceVideo src={sourcePath} />
        <BrandHeader meta={meta} section={activeSection} sectionIndex={sectionIndex} />

        {(meta.captions?.data ?? []).map((line, index) => (
          <Sequence
            key={`caption-${index}`}
            from={secToFrames(line.t_in, fps)}
            durationInFrames={Math.max(1, secToFrames(line.t_out - line.t_in, fps))}
            name={`Arabic source caption ${index + 1}`}
          >
            <KineticCaption line={line} />
          </Sequence>
        ))}

        <GoldFrame />
        <NarrativeAudio meta={meta} />
      </Paper>
    </AbsoluteFill>
  );
};

export const MainNarrative: React.FC<Props> = ({ meta, brand }) => {
  const { width, height } = useVideoConfig();
  return (
    <ThemeProvider brand={brand} width={width} height={height} aspect="16x9">
      <NarrativeTimeline meta={meta} />
    </ThemeProvider>
  );
};
