/**
 * RUWAQ Historical Geography: Remotion Production Composition
 * Deterministic, frame-accurate rendering of the 7-Act Historical Geography
 * Story Sequence for Bab Zuwayla.
 */

import React, { useMemo } from 'react';
import { useCurrentFrame, useVideoConfig } from 'remotion';
import { getInterpolatedMapCamera, MapCameraState } from './storyChoreography.ts';
import { BabZuwaylaRemotion } from '../BabZuwaylaRemotion.tsx';
import { DEFAULT_APPROXIMATE_FATIMID_ENCLOSURE_GEOJSON } from './cairoHistoricalGeoJSON.ts';

export interface RuwaqGeoRemotionProps {
  frame?: number;
  durationInFrames?: number;
  width?: number;
  height?: number;
  fatimidEnclosureData?: GeoJSON.FeatureCollection;
}

export const RuwaqGeoRemotion: React.FC<RuwaqGeoRemotionProps> = ({
  frame: propFrame,
  durationInFrames: propDuration,
  width: propWidth,
  height: propHeight,
  fatimidEnclosureData = DEFAULT_APPROXIMATE_FATIMID_ENCLOSURE_GEOJSON,
}) => {
  const remotionFrame = useCurrentFrame();
  const videoConfig = useVideoConfig();

  const currentFrame = propFrame !== undefined ? propFrame : remotionFrame;
  const totalFrames = propDuration !== undefined ? propDuration : (videoConfig?.durationInFrames || 600);
  const canvasWidth = propWidth || videoConfig?.width || 1920;
  const canvasHeight = propHeight || videoConfig?.height || 1080;

  const cameraState: MapCameraState = useMemo(() => {
    return getInterpolatedMapCamera(currentFrame, totalFrames);
  }, [currentFrame, totalFrames]);

  const act = cameraState.currentAct;

  // Coordinate projections for schematic SVG documentary map layer
  // Cairo bounds roughly: [31.20 to 31.28, 30.01 to 30.07]
  const projectCoord = (lng: number, lat: number) => {
    // Relative to current camera center and zoom.
    // Web-Mercator scale: a 256px tile spans 360 / 2^zoom degrees, so
    // pixels-per-degree = 2^zoom * 256 / 360 (~0.711 * 2^zoom).
    // The old factor (2^zoom * 35) was ~49x too large: at zoom 11.8 the
    // frame showed only 0.015 deg (~1.5 km) of ground, so the Nile fell
    // off-screen and the Fatimid enclosure rendered ~12,000 px wide.
    // The 1.15 latitude factor is the Mercator y-stretch at Cairo's
    // latitude (1 / cos(30 deg) = 1.155).
    const centerLng = cameraState.center[0];
    const centerLat = cameraState.center[1];
    const scale = Math.pow(2, cameraState.zoom) * (256 / 360);

    const x = canvasWidth / 2 + (lng - centerLng) * scale;
    const y = canvasHeight / 2 - (lat - centerLat) * scale * 1.15; // Mercator aspect
    return [x, y];
  };

  return (
    <div
      style={{
        width: canvasWidth,
        height: canvasHeight,
        position: 'relative',
        backgroundColor: '#F3EBDB', // RUWAQ Cream
        overflow: 'hidden',
        fontFamily: "'Plus Jakarta Sans', sans-serif",
      }}
    >
      {/* 1. Vector Map Canvas (Offline Deterministic Cartography) */}
      <svg
        width={canvasWidth}
        height={canvasHeight}
        style={{ position: 'absolute', inset: 0 }}
      >
        <defs>
          <radialGradient id="vignette" cx="50%" cy="50%" r="60%">
            <stop offset="60%" stopColor="#000000" stopOpacity="0" />
            <stop offset="100%" stopColor="#1C1B19" stopOpacity="0.25" />
          </radialGradient>
          <filter id="gold-glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Parchment Base */}
        <rect width={canvasWidth} height={canvasHeight} fill="#F3EBDB" />

        {/* Nile River Polygon Course */}
        <path
          d={`M ${projectCoord(31.214, 30.01).join(',')} 
             L ${projectCoord(31.218, 30.04).join(',')} 
             L ${projectCoord(31.226, 30.07).join(',')} 
             L ${projectCoord(31.240, 30.10).join(',')} 
             L ${projectCoord(31.252, 30.10).join(',')} 
             L ${projectCoord(31.238, 30.07).join(',')} 
             L ${projectCoord(31.230, 30.04).join(',')} 
             L ${projectCoord(31.227, 30.01).join(',')} Z`}
          fill="#2C3E42"
          opacity={0.88}
          stroke="#A98A4B"
          strokeWidth={1.5}
        />

        {/* Gezira Island */}
        <path
          d={`M ${projectCoord(31.219, 30.04).join(',')} 
             L ${projectCoord(31.223, 30.065).join(',')} 
             L ${projectCoord(31.218, 30.05).join(',')} Z`}
          fill="#F3EBDB"
          stroke="#A98A4B"
          strokeWidth={1}
        />

        {/* Modern Cairo Arterials (Subtle Umber) */}
        <line
          x1={projectCoord(31.246, 30.0485)[0]}
          y1={projectCoord(31.246, 30.0485)[1]}
          x2={projectCoord(31.272, 30.0462)[0]}
          y2={projectCoord(31.272, 30.0462)[1]}
          stroke="#9E9282"
          strokeWidth={2}
          opacity={0.65}
        />
        <line
          x1={projectCoord(31.2542, 30.034)[0]}
          y1={projectCoord(31.2542, 30.034)[1]}
          x2={projectCoord(31.2575, 30.064)[0]}
          y2={projectCoord(31.2575, 30.064)[1]}
          stroke="#9E9282"
          strokeWidth={2}
          opacity={0.65}
        />

        {/* UNESCO Historic Cairo Boundary (If Act >= 2) */}
        {currentFrame >= 81 && (
          <polygon
            points={`
              ${projectCoord(31.252, 30.0585).join(',')}
              ${projectCoord(31.268, 30.058).join(',')}
              ${projectCoord(31.274, 30.050).join(',')}
              ${projectCoord(31.272, 30.038).join(',')}
              ${projectCoord(31.266, 30.025).join(',')}
              ${projectCoord(31.258, 30.023).join(',')}
              ${projectCoord(31.251, 30.032).join(',')}
              ${projectCoord(31.253, 30.045).join(',')}
            `}
            fill="#E4D5BE"
            fillOpacity={0.4}
            stroke="#A98A4B"
            strokeWidth={2}
            strokeDasharray="6,4"
          />
        )}

        {/* Approximate Fatimid Cairo Enclosure (If Act >= 3) */}
        {currentFrame >= 161 && (
          <g>
            {/* Uncertainty Buffer (±50m) */}
            <polygon
              points={`
                ${projectCoord(31.2633, 30.0548).join(',')}
                ${projectCoord(31.2667, 30.0544).join(',')}
                ${projectCoord(31.2673, 30.0500).join(',')}
                ${projectCoord(31.2665, 30.0430).join(',')}
                ${projectCoord(31.25895, 30.0422).join(',')}
                ${projectCoord(31.2549, 30.0450).join(',')}
                ${projectCoord(31.2570, 30.0545).join(',')}
              `}
              fill="#8C4729"
              fillOpacity={0.12}
              stroke="#8C4729"
              strokeWidth={1}
              strokeDasharray="3,3"
            />

            {/* Approximate Wall Polygon */}
            <polygon
              points={`
                ${projectCoord(31.26348, 30.05435).join(',')}
                ${projectCoord(31.26555, 30.05417).join(',')}
                ${projectCoord(31.26620, 30.05400).join(',')}
                ${projectCoord(31.26680, 30.05000).join(',')}
                ${projectCoord(31.26600, 30.04350).join(',')}
                ${projectCoord(31.25895, 30.04278).join(',')}
                ${projectCoord(31.25650, 30.04200).join(',')}
                ${projectCoord(31.25550, 30.04500).join(',')}
                ${projectCoord(31.25750, 30.05400).join(',')}
              `}
              fill="#8C4729"
              fillOpacity={0.25}
              stroke="#8C4729"
              strokeWidth={3}
            />

            {/* Northern Standing In-Situ Wall Segment (Stone 1087 CE) */}
            <line
              x1={projectCoord(31.26348, 30.05435)[0]}
              y1={projectCoord(31.26348, 30.05435)[1]}
              x2={projectCoord(31.26555, 30.05417)[0]}
              y2={projectCoord(31.26555, 30.05417)[1]}
              stroke="#1C1B19"
              strokeWidth={5}
            />
            <line
              x1={projectCoord(31.26348, 30.05435)[0]}
              y1={projectCoord(31.26348, 30.05435)[1]}
              x2={projectCoord(31.26555, 30.05417)[0]}
              y2={projectCoord(31.26555, 30.05417)[1]}
              stroke="#A98A4B"
              strokeWidth={2}
            />
          </g>
        )}

        {/* Al-Mu'izz Grand Axis Line (If Act >= 4) */}
        {currentFrame >= 241 && (
          <g filter="url(#gold-glow)">
            <line
              x1={projectCoord(31.26348, 30.05435)[0]}
              y1={projectCoord(31.26348, 30.05435)[1]}
              x2={projectCoord(31.25895, 30.04278)[0]}
              y2={projectCoord(31.25895, 30.04278)[1]}
              stroke="#A98A4B"
              strokeWidth={7}
              strokeOpacity={0.4}
            />
            <line
              x1={projectCoord(31.26348, 30.05435)[0]}
              y1={projectCoord(31.26348, 30.05435)[1]}
              x2={projectCoord(31.25895, 30.04278)[0]}
              y2={projectCoord(31.25895, 30.04278)[1]}
              stroke="#1C1B19"
              strokeWidth={3}
            />
            <line
              x1={projectCoord(31.26348, 30.05435)[0]}
              y1={projectCoord(31.26348, 30.05435)[1]}
              x2={projectCoord(31.25895, 30.04278)[0]}
              y2={projectCoord(31.25895, 30.04278)[1]}
              stroke="#D4AF37"
              strokeWidth={1.8}
              strokeDasharray="4,2"
            />
          </g>
        )}

        {/* Northern Gates (Bab al-Futuh & Bab al-Nasr) */}
        {currentFrame >= 321 && (
          <g>
            <circle
              cx={projectCoord(31.26348, 30.05435)[0]}
              cy={projectCoord(31.26348, 30.05435)[1]}
              r={9}
              fill="#1C1B19"
              stroke="#A98A4B"
              strokeWidth={2}
            />
            <circle
              cx={projectCoord(31.26555, 30.05417)[0]}
              cy={projectCoord(31.26555, 30.05417)[1]}
              r={9}
              fill="#1C1B19"
              stroke="#A98A4B"
              strokeWidth={2}
            />
          </g>
        )}

        {/* Bab Zuwayla (Southern Anchor) */}
        {currentFrame >= 401 && (
          <g>
            <circle
              cx={projectCoord(31.25895, 30.04278)[0]}
              cy={projectCoord(31.25895, 30.04278)[1]}
              r={14}
              fill="#1C1B19"
              stroke="#A98A4B"
              strokeWidth={3}
            />
            <circle
              cx={projectCoord(31.25895, 30.04278)[0]}
              cy={projectCoord(31.25895, 30.04278)[1]}
              r={7}
              fill="#A98A4B"
            />
          </g>
        )}

        {/* Vignette */}
        <rect width={canvasWidth} height={canvasHeight} fill="url(#vignette)" pointerEvents="none" />
      </svg>

      {/* 2. Act 7 3D Model Transition */}
      {cameraState.threeDBlend > 0 && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            opacity: cameraState.threeDBlend,
            transition: 'opacity 0.2s linear',
          }}
        >
          <BabZuwaylaRemotion
            frame={Math.round(cameraState.threeDBlend * 300)}
            durationInFrames={300}
            width={canvasWidth}
            height={canvasHeight}
          />
        </div>
      )}

      {/* 3. Cinematic Documentary Editorial Lower-Third.
          Hidden as soon as the 3D model starts blending in (Act 7):
          BabZuwaylaRemotion renders its own lower-third at the same
          position, and two stacked titles are unreadable — a 50/50
          cross-fade is still two legible titles on top of each other
          mid-blend, so this is a hard cut, not a fade. Map-side only;
          the 3D composition itself is untouched. */}
      <div
        style={{
          position: 'absolute',
          bottom: 50,
          left: 60,
          pointerEvents: 'none',
          fontFamily: "'Cinzel', serif",
          color: '#1C1B19',
          opacity: cameraState.threeDBlend > 0 ? 0 : 1,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span
            style={{
              fontSize: 14,
              letterSpacing: '0.25em',
              fontWeight: 'bold',
              color: '#A98A4B',
            }}
          >
            RUWAQ | رواق
          </span>
          <span style={{ color: '#A98A4B', opacity: 0.5 }}>•</span>
          <span style={{ fontSize: 13, fontFamily: 'monospace', color: '#1C1B19' }}>
            ACT {act.actNumber} OF 7 • FRAME {currentFrame.toString().padStart(3, '0')} / {totalFrames}
          </span>
        </div>

        <h1
          style={{
            fontSize: 32,
            margin: '4px 0 0 0',
            fontWeight: 'bold',
            letterSpacing: '0.04em',
          }}
        >
          {act.titleEn.toUpperCase()}
        </h1>

        <p
          style={{
            fontSize: 15,
            margin: '2px 0 0 0',
            fontFamily: 'monospace',
            color: '#8C4729',
            fontWeight: 500,
          }}
        >
          {act.subtitleEn}
        </p>

        <p
          style={{
            fontSize: 11,
            margin: '4px 0 0 0',
            fontFamily: 'monospace',
            color: '#1C1B19',
            opacity: 0.75,
            maxWidth: 800,
          }}
        >
          {act.cartographicNoteEn}
        </p>
      </div>

      {/* Historical Disclaimer Badge */}
      <div
        style={{
          position: 'absolute',
          top: 40,
          left: 60,
          backgroundColor: 'rgba(28, 27, 25, 0.9)',
          border: '1px solid #A98A4B',
          padding: '6px 14px',
          borderRadius: 6,
          color: '#F3EBDB',
          fontFamily: 'monospace',
          fontSize: 11,
          display: 'flex',
          alignItems: 'center',
          gap: 8,
        }}
      >
        <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#A98A4B' }} />
        <span>HISTORICAL CARTOGRAPHY • WGS-84 / OPENSTREETMAP / CRESWELL SURVEY</span>
      </div>
    </div>
  );
};
