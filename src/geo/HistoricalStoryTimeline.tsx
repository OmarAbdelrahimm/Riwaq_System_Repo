/**
 * RUWAQ Historical Geography: Story Timeline Controller
 * Controls deterministic frame playback, act jumping, speed, and mode switching.
 */

import React from 'react';
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  RotateCcw,
  Compass,
  Film,
  Layers,
  Sparkles,
} from 'lucide-react';
import { STORY_ACTS, getInterpolatedMapCamera } from './storyChoreography.ts';
import { StoryActId } from './types.ts';

interface HistoricalStoryTimelineProps {
  frame: number;
  totalFrames: number;
  isPlaying: boolean;
  playbackSpeed: number;
  isInteractiveMode: boolean;
  onSeekFrame: (frame: number) => void;
  onTogglePlay: () => void;
  onChangeSpeed: (speed: number) => void;
  onToggleInteractiveMode: () => void;
  onJumpToAct: (actId: StoryActId) => void;
}

export const HistoricalStoryTimeline: React.FC<HistoricalStoryTimelineProps> = ({
  frame,
  totalFrames,
  isPlaying,
  playbackSpeed,
  isInteractiveMode,
  onSeekFrame,
  onTogglePlay,
  onChangeSpeed,
  onToggleInteractiveMode,
  onJumpToAct,
}) => {
  const cameraState = getInterpolatedMapCamera(frame, totalFrames);
  const currentAct = cameraState.currentAct;

  const formatTime = (f: number) => {
    const totalSecs = f / 30;
    const mins = Math.floor(totalSecs / 60);
    const secs = (totalSecs % 60).toFixed(1);
    return `${mins}:${secs.padStart(4, '0')}`;
  };

  return (
    <div className="absolute bottom-4 left-6 right-6 z-20 pointer-events-none flex flex-col gap-2">
      {/* Editorial Story Header & Act Context (Lower-Third) */}
      <div className="pointer-events-auto bg-[#1C1B19]/95 text-[#F3EBDB] border border-[#A98A4B]/50 p-4 rounded-xl shadow-2xl backdrop-blur-none flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex flex-col gap-1 max-w-2xl">
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded bg-[#A98A4B] text-[#1C1B19] font-bold text-[10px] font-mono-doc">
              ACT {currentAct.actNumber} OF 7
            </span>
            <span className="font-arabic text-[#A98A4B] text-sm font-bold">
              {currentAct.titleAr}
            </span>
            <span className="text-[#A98A4B]/50 text-xs">•</span>
            <span className="text-[11px] font-mono-doc text-[#F3EBDB]/70">
              FRAME {frame.toString().padStart(3, '0')} / {totalFrames} ({formatTime(frame)})
            </span>
          </div>

          <h2 className="font-serif-doc text-lg font-bold text-[#F3EBDB] tracking-wide">
            {currentAct.titleEn}
          </h2>

          <p className="text-xs text-[#D8CEBC]/90 line-clamp-2 leading-relaxed">
            {currentAct.historicalContextEn}
          </p>
        </div>

        {/* Story / Interactive Switcher & Controls */}
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={onToggleInteractiveMode}
            className={`px-3 py-2 rounded-lg text-xs font-mono-doc flex items-center gap-2 transition-all border ${
              isInteractiveMode
                ? 'bg-[#A98A4B] text-[#1C1B19] border-[#A98A4B] font-bold shadow-md'
                : 'bg-[#1C1B19] text-[#F3EBDB] border-[#A98A4B]/40 hover:bg-[#A98A4B]/20'
            }`}
          >
            <Compass className="w-4 h-4" />
            <span>{isInteractiveMode ? 'Free GIS Explorer' : 'Remotion Story Mode'}</span>
          </button>
        </div>
      </div>

      {/* Frame Scrubber & Act Markers Dock */}
      <div className="pointer-events-auto bg-[#1C1B19]/90 border border-[#A98A4B]/40 px-4 py-3 rounded-xl shadow-2xl backdrop-blur-none flex flex-col gap-2">
        {/* Act Quick-Jump Badges */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-thin">
          {STORY_ACTS.map((act) => {
            const isActive = currentAct.id === act.id;
            return (
              <button
                key={act.id}
                onClick={() => onJumpToAct(act.id)}
                className={`px-2.5 py-1 rounded text-[11px] font-mono-doc shrink-0 transition-all border ${
                  isActive
                    ? 'bg-[#A98A4B] text-[#1C1B19] font-bold border-[#A98A4B] shadow-sm'
                    : 'bg-[#2A2824] text-[#D8CEBC]/80 border-transparent hover:border-[#A98A4B]/40 hover:text-[#F3EBDB]'
                }`}
              >
                <span>{act.actNumber}. {act.titleEn.split(':')[0]}</span>
              </button>
            );
          })}
        </div>

        {/* Master Slider & Progress Bar */}
        <div className="flex items-center gap-4">
          {/* Play/Pause & Step Buttons */}
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => onSeekFrame(Math.max(0, frame - 10))}
              title="Step -10 frames"
              className="p-1.5 text-[#F3EBDB]/80 hover:text-[#F3EBDB] hover:bg-[#A98A4B]/20 rounded transition-colors"
            >
              <SkipBack className="w-4 h-4" />
            </button>

            <button
              onClick={onTogglePlay}
              className="p-2 rounded-lg bg-[#A98A4B] text-[#1C1B19] hover:bg-[#c4a45e] transition-colors shadow-md"
              title={isPlaying ? 'Pause (Space)' : 'Play (Space)'}
            >
              {isPlaying ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current" />}
            </button>

            <button
              onClick={() => onSeekFrame(Math.min(totalFrames, frame + 10))}
              title="Step +10 frames"
              className="p-1.5 text-[#F3EBDB]/80 hover:text-[#F3EBDB] hover:bg-[#A98A4B]/20 rounded transition-colors"
            >
              <SkipForward className="w-4 h-4" />
            </button>

            <button
              onClick={() => onSeekFrame(0)}
              title="Reset to frame 0"
              className="p-1.5 text-[#F3EBDB]/60 hover:text-[#F3EBDB] rounded transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Interactive Range Scrubber */}
          <div className="relative flex-1 flex items-center">
            <input
              type="range"
              min={0}
              max={totalFrames}
              value={frame}
              onChange={(e) => onSeekFrame(Number(e.target.value))}
              className="w-full h-2 bg-[#2A2824] rounded-lg appearance-none cursor-pointer accent-[#A98A4B]"
            />
          </div>

          {/* Speed Selector */}
          <div className="flex items-center gap-1 bg-[#2A2824] p-1 rounded-md text-[11px] font-mono-doc">
            {[0.5, 1.0, 2.0].map((spd) => (
              <button
                key={spd}
                onClick={() => onChangeSpeed(spd)}
                className={`px-1.5 py-0.5 rounded transition-all ${
                  playbackSpeed === spd
                    ? 'bg-[#A98A4B] text-[#1C1B19] font-bold'
                    : 'text-[#D8CEBC]/70 hover:text-[#F3EBDB]'
                }`}
              >
                {spd}x
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
