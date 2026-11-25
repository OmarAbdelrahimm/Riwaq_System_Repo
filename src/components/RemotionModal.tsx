/**
 * Remotion Integration Instructions & Ready-to-Use Code
 * Explains how to integrate this 3D Bab Zuwayla reconstruction into a Remotion documentary sequence
 */

import React, { useState } from 'react';
import { X, Copy, Check, Film, Code, Sparkles, BookOpen } from 'lucide-react';

interface RemotionModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const RemotionModal: React.FC<RemotionModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const remotionCodeSnippet = `// Remotion Documentary Sequence: BabZuwaylaReconstruction.tsx
// Install in your Remotion project:
// npm install three @types/three remotion

import React, { useEffect, useRef } from 'react';
import {
  Composition,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from 'remotion';
import { BabZuwaylaScene } from '../three/BabZuwaylaScene';

export interface BabZuwaylaRemotionProps {
  totalFrames?: number;
}

export const BabZuwaylaRemotionScene: React.FC<BabZuwaylaRemotionProps> = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames, width, height } = useVideoConfig();
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<BabZuwaylaScene | null>(null);

  // Initialize Three.js scene once
  useEffect(() => {
    if (!containerRef.current) return;

    const scene = new BabZuwaylaScene(containerRef.current, {
      onSelectComponent: () => {},
      onSelectAnnotation: () => {},
    });
    sceneRef.current = scene;

    return () => {
      scene.dispose();
      sceneRef.current = null;
    };
  }, []);

  // Synchronously drive animation through externally supplied frame number
  // Remotion renders frame-by-frame headlessly, so we advance deterministically:
  useEffect(() => {
    if (sceneRef.current) {
      sceneRef.current.seekFrame(frame, durationInFrames);
    }
  }, [frame, durationInFrames]);

  return (
    <div
      ref={containerRef}
      style={{
        width: '100%',
        height: '100%',
        position: 'relative',
        backgroundColor: '#F3EBDB',
      }}
    >
      {/* RUWAQ Documentary Lower-Third Plate */}
      <div
        style={{
          position: 'absolute',
          bottom: 60,
          left: 80,
          fontFamily: 'serif',
          color: '#1C1B19',
          pointerEvents: 'none',
        }}
      >
        <h1 style={{ fontSize: 36, margin: 0, fontWeight: 'bold' }}>
          BAB ZUWAYLA
        </h1>
        <p style={{ fontSize: 18, margin: '4px 0', color: '#A98A4B' }}>
          {frame < 156 ? '1092 CE • Fatimid Gate' : '1415–1421 CE • Mamluk Minarets'}
        </p>
      </div>
    </div>
  );
};

// Remotion Root Entry:
export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="BabZuwaylaDocumentary"
      component={BabZuwaylaRemotionScene}
      durationInFrames={300}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
`;

  const handleCopy = () => {
    navigator.clipboard.writeText(remotionCodeSnippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 pointer-events-auto">
      <div className="bg-[#1C1B19] border-2 border-[#A98A4B] text-[#F3EBDB] rounded-xl max-w-3xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden font-sans">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#A98A4B]/30 bg-[#151413]">
          <div className="flex items-center gap-2.5">
            <Film className="w-5 h-5 text-[#A98A4B]" />
            <div>
              <h2 className="font-serif-doc text-base font-bold text-[#F3EBDB]">
                REMOTION INTEGRATION GUIDE
              </h2>
              <p className="text-xs text-[#A98A4B] font-mono-doc">
                Deterministic Frame-Driven Three.js Rendering for RUWAQ
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#F3EBDB]/70 hover:text-white hover:bg-white/10"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-4 overflow-y-auto flex flex-col gap-4 text-xs scrollbar-thin">
          {/* Key Architectural Principle */}
          <div className="bg-[#A98A4B]/15 border border-[#A98A4B]/40 rounded-lg p-3 text-xs leading-relaxed flex flex-col gap-1.5">
            <div className="flex items-center gap-2 font-bold text-[#A98A4B]">
              <Sparkles className="w-4 h-4" />
              <span>DETERMINISTIC NON-REALTIME RENDERING</span>
            </div>
            <p className="text-[#F3EBDB]/90">
              Per documentary guidelines, <strong>all animations are driven through externally supplied frame numbers (<code className="font-mono-doc text-[#A98A4B]">seekFrame(frame, totalFrames)</code>)</strong> rather than wall-clock time (<code className="font-mono-doc text-[#A98A4B]">performance.now()</code> or <code className="font-mono-doc text-[#A98A4B]">requestAnimationFrame</code> deltas). This guarantees 100% frame-perfect synchronization during headless MP4 / ProRes video exports in Remotion.
            </p>
          </div>

          {/* Choreography Sequence Breakdown */}
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2 font-bold text-[#A98A4B] font-mono-doc uppercase text-xs">
              <BookOpen className="w-4 h-4" />
              <span>Continuous Camera Choreography Breakdown (300 Frames @ 30fps = 10s):</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 font-mono-doc text-[11px]">
              <div className="p-2.5 bg-[#151413] rounded border border-[#A98A4B]/20">
                <span className="text-[#A98A4B] font-bold">Act 1 (Frames 0–45):</span>
                <p className="text-[#F3EBDB]/80 mt-1">Top Orthographic Plan: Highlights geometric symmetry, wall thickness, and Cairo entry vector.</p>
              </div>

              <div className="p-2.5 bg-[#151413] rounded border border-[#A98A4B]/20">
                <span className="text-[#A98A4B] font-bold">Act 2 (Frames 45–90):</span>
                <p className="text-[#F3EBDB]/80 mt-1">Side Orthographic Elevation: Displays bastion projection and southern curtain wall profile.</p>
              </div>

              <div className="p-2.5 bg-[#151413] rounded border border-[#A98A4B]/20">
                <span className="text-[#A98A4B] font-bold">Act 3 (Frames 90–135):</span>
                <p className="text-[#F3EBDB]/80 mt-1">Front Elevation (1092 CE): Pure Fatimid gate without minarets, showing cushion voussoirs.</p>
              </div>

              <div className="p-2.5 bg-[#151413] rounded border border-[#A98A4B]/20">
                <span className="text-[#A98A4B] font-bold">Act 4 (Frames 135–190):</span>
                <p className="text-[#F3EBDB]/80 mt-1">Mamluk Minarets Added (1415–1421 CE): Twin minarets descend and mount atop the bastions.</p>
              </div>

              <div className="p-2.5 bg-[#151413] rounded border border-[#A98A4B]/20">
                <span className="text-[#A98A4B] font-bold">Act 5 (Frames 190–245):</span>
                <p className="text-[#F3EBDB]/80 mt-1">Exploded View: Separates semicircular towers, gate passage, doors, and minaret tiers along 3 axes.</p>
              </div>

              <div className="p-2.5 bg-[#151413] rounded border border-[#A98A4B]/20">
                <span className="text-[#A98A4B] font-bold">Act 6 (Frames 245–300):</span>
                <p className="text-[#F3EBDB]/80 mt-1">Final Reassembly: Smooth interpolation into heroic 3/4 documentary perspective view.</p>
              </div>
            </div>
          </div>

          {/* Code Snippet */}
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-[#A98A4B] font-mono-doc flex items-center gap-1.5">
                <Code className="w-4 h-4" />
                <span>REMOTION REACT SOURCE CODE:</span>
              </span>

              <button
                onClick={handleCopy}
                className="flex items-center gap-1.5 px-3 py-1 bg-[#A98A4B] text-[#1C1B19] rounded font-semibold text-xs hover:bg-[#c4a45e] transition-colors"
              >
                {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Copied!' : 'Copy Code'}</span>
              </button>
            </div>

            <pre className="bg-[#100f0e] border border-[#A98A4B]/30 p-3 rounded-lg overflow-x-auto text-[11px] font-mono-doc text-[#F3EBDB]/90 leading-relaxed max-h-56">
              {remotionCodeSnippet}
            </pre>
          </div>
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-[#A98A4B]/30 bg-[#151413] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded bg-[#A98A4B] text-[#1C1B19] font-bold hover:bg-[#c4a45e] transition-colors text-xs"
          >
            Close Guide
          </button>
        </div>
      </div>
    </div>
  );
};
