/**
 * Remotion Documentary Animation Driver & Timeline Scrubber
 * Externally controls frame number, fps, and continuous camera choreography
 */

import React, { useEffect, useRef } from 'react';
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  RotateCw,
  Clock,
  Film
} from 'lucide-react';
import { RemotionTimelineState } from '../types.ts';

interface TimelineControllerProps {
  timeline: RemotionTimelineState;
  onUpdateTimeline: (updater: Partial<RemotionTimelineState>) => void;
  onSeekFrame: (frame: number) => void;
}

export const TimelineController: React.FC<TimelineControllerProps> = ({
  timeline,
  onUpdateTimeline,
  onSeekFrame,
}) => {
  const { frame, totalFrames, fps, isPlaying, loop, speed } = timeline;
  const playTimerRef = useRef<number | null>(null);

  // Animation frame loop for playback
  useEffect(() => {
    if (!isPlaying) {
      if (playTimerRef.current) cancelAnimationFrame(playTimerRef.current);
      return;
    }

    let lastTime = performance.now();
    const intervalMs = 1000 / (fps * speed);

    const step = (time: number) => {
      const elapsed = time - lastTime;
      if (elapsed >= intervalMs) {
        lastTime = time - (elapsed % intervalMs);

        let nextFrame = frame + 1;
        if (nextFrame >= totalFrames) {
          if (loop) {
            nextFrame = 0;
          } else {
            onUpdateTimeline({ isPlaying: false });
            return;
          }
        }
        onSeekFrame(nextFrame);
      }
      playTimerRef.current = requestAnimationFrame(step);
    };

    playTimerRef.current = requestAnimationFrame(step);

    return () => {
      if (playTimerRef.current) cancelAnimationFrame(playTimerRef.current);
    };
  }, [isPlaying, frame, totalFrames, fps, speed, loop, onSeekFrame, onUpdateTimeline]);

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseInt(e.target.value, 10);
    onSeekFrame(val);
  };

  const togglePlay = () => {
    onUpdateTimeline({ isPlaying: !isPlaying });
  };

  const handleStep = (stepCount: number) => {
    let next = frame + stepCount;
    if (next < 0) next = 0;
    if (next >= totalFrames) next = totalFrames - 1;
    onSeekFrame(next);
  };

  const formatTime = (f: number, rate: number) => {
    const totalSecs = f / rate;
    const mins = Math.floor(totalSecs / 60);
    const secs = Math.floor(totalSecs % 60);
    const sub = Math.floor((totalSecs % 1) * 10);
    return `${mins.toString().padStart(2, '0')}:${secs
      .toString()
      .padStart(2, '0')}.${sub}`;
  };

  // Timeline segment markers
  const progressRatio = frame / totalFrames;

  return (
    <div className="flex flex-col gap-2 w-full bg-[#1C1B19]/90 border border-[#A98A4B]/40 rounded-lg p-3 text-[#F3EBDB]">
      {/* Top Scrubber & Timecode Info */}
      <div className="flex items-center justify-between text-xs font-mono-doc">
        <div className="flex items-center gap-2">
          <Film className="w-3.5 h-3.5 text-[#A98A4B]" />
          <span className="text-[#A98A4B] font-semibold">REMOTION CHOREOGRAPHY</span>
          <span className="text-white/40">|</span>
          <span className="text-[#F3EBDB]">
            FRAME <strong className="text-[#A98A4B]">{frame.toString().padStart(3, '0')}</strong> / {totalFrames}
          </span>
        </div>

        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5 text-[#F3EBDB]/80">
            <Clock className="w-3.5 h-3.5 text-[#A98A4B]" />
            <span>{formatTime(frame, fps)}</span>
          </div>

          <span className="px-2 py-0.5 rounded bg-[#A98A4B]/20 text-[#A98A4B] text-[10px] font-bold">
            {fps} FPS
          </span>
        </div>
      </div>

      {/* Scrubber Track with Sequence Acts */}
      <div className="relative w-full flex flex-col gap-1">
        {/* Scrubber input */}
        <input
          type="range"
          min="0"
          max={totalFrames - 1}
          value={frame}
          onChange={handleSliderChange}
          className="w-full accent-[#A98A4B] cursor-pointer h-2 bg-[#2D2A26] rounded-lg appearance-none"
        />

        {/* Documentary Sequence Act Markers */}
        <div className="grid grid-cols-6 gap-1 text-[9px] font-mono-doc text-center text-[#F3EBDB]/60 pt-1">
          <div
            onClick={() => onSeekFrame(15)}
            className={`cursor-pointer hover:text-[#A98A4B] p-0.5 rounded ${
              progressRatio < 0.18 ? 'text-[#A98A4B] font-bold bg-[#A98A4B]/15' : ''
            }`}
          >
            I. Top Plan
          </div>
          <div
            onClick={() => onSeekFrame(75)}
            className={`cursor-pointer hover:text-[#A98A4B] p-0.5 rounded ${
              progressRatio >= 0.18 && progressRatio < 0.35
                ? 'text-[#A98A4B] font-bold bg-[#A98A4B]/15'
                : ''
            }`}
          >
            II. Side Elevation
          </div>
          <div
            onClick={() => onSeekFrame(125)}
            className={`cursor-pointer hover:text-[#A98A4B] p-0.5 rounded ${
              progressRatio >= 0.35 && progressRatio < 0.52
                ? 'text-[#A98A4B] font-bold bg-[#A98A4B]/15'
                : ''
            }`}
          >
            III. 1092 Gate
          </div>
          <div
            onClick={() => onSeekFrame(180)}
            className={`cursor-pointer hover:text-[#A98A4B] p-0.5 rounded ${
              progressRatio >= 0.52 && progressRatio < 0.68
                ? 'text-[#A98A4B] font-bold bg-[#A98A4B]/15'
                : ''
            }`}
          >
            IV. Minarets 1421
          </div>
          <div
            onClick={() => onSeekFrame(230)}
            className={`cursor-pointer hover:text-[#A98A4B] p-0.5 rounded ${
              progressRatio >= 0.68 && progressRatio < 0.85
                ? 'text-[#A98A4B] font-bold bg-[#A98A4B]/15'
                : ''
            }`}
          >
            V. Exploded View
          </div>
          <div
            onClick={() => onSeekFrame(285)}
            className={`cursor-pointer hover:text-[#A98A4B] p-0.5 rounded ${
              progressRatio >= 0.85 ? 'text-[#A98A4B] font-bold bg-[#A98A4B]/15' : ''
            }`}
          >
            VI. Final Assembled
          </div>
        </div>
      </div>

      {/* Control Buttons Bar */}
      <div className="flex items-center justify-between pt-1 flex-wrap gap-2">
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => onSeekFrame(0)}
            title="Jump to Start (Frame 0)"
            className="p-1.5 rounded hover:bg-[#A98A4B]/20 text-[#F3EBDB] transition-colors"
          >
            <SkipBack className="w-4 h-4" />
          </button>

          <button
            onClick={() => handleStep(-15)}
            title="Step Back 15 Frames"
            className="px-2 py-1 text-[11px] font-mono-doc rounded hover:bg-[#A98A4B]/20 text-[#F3EBDB] transition-colors"
          >
            -15f
          </button>

          <button
            onClick={() => handleStep(-1)}
            title="Step Back 1 Frame"
            className="px-2 py-1 text-[11px] font-mono-doc rounded hover:bg-[#A98A4B]/20 text-[#F3EBDB] transition-colors"
          >
            -1f
          </button>

          {/* Primary Play/Pause Button */}
          <button
            onClick={togglePlay}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-md bg-[#A98A4B] text-[#1C1B19] font-semibold text-xs hover:bg-[#c4a45e] transition-colors shadow-md"
          >
            {isPlaying ? (
              <>
                <Pause className="w-3.5 h-3.5 fill-current" />
                <span>Pause</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Play Choreography</span>
              </>
            )}
          </button>

          <button
            onClick={() => handleStep(1)}
            title="Step Forward 1 Frame"
            className="px-2 py-1 text-[11px] font-mono-doc rounded hover:bg-[#A98A4B]/20 text-[#F3EBDB] transition-colors"
          >
            +1f
          </button>

          <button
            onClick={() => handleStep(15)}
            title="Step Forward 15 Frames"
            className="px-2 py-1 text-[11px] font-mono-doc rounded hover:bg-[#A98A4B]/20 text-[#F3EBDB] transition-colors"
          >
            +15f
          </button>

          <button
            onClick={() => onSeekFrame(totalFrames - 1)}
            title="Jump to End (Frame 300)"
            className="p-1.5 rounded hover:bg-[#A98A4B]/20 text-[#F3EBDB] transition-colors"
          >
            <SkipForward className="w-4 h-4" />
          </button>
        </div>

        {/* Playback Options */}
        <div className="flex items-center gap-3 text-xs font-mono-doc">
          <label className="flex items-center gap-1.5 cursor-pointer text-[#F3EBDB]/80 hover:text-[#F3EBDB]">
            <input
              type="checkbox"
              checked={loop}
              onChange={(e) => onUpdateTimeline({ loop: e.target.checked })}
              className="accent-[#A98A4B] w-3.5 h-3.5"
            />
            <RotateCw className="w-3 h-3 text-[#A98A4B]" />
            <span>Loop</span>
          </label>

          <div className="flex items-center gap-1">
            <span className="text-[#F3EBDB]/60">Speed:</span>
            {[0.5, 1.0, 1.5].map((s) => (
              <button
                key={s}
                onClick={() => onUpdateTimeline({ speed: s })}
                className={`px-1.5 py-0.5 rounded text-[10px] ${
                  speed === s
                    ? 'bg-[#A98A4B] text-[#1C1B19] font-bold'
                    : 'bg-[#2D2A26] text-[#F3EBDB]/70 hover:text-white'
                }`}
              >
                {s}x
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
