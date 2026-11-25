/**
 * RUWAQ Documentary Header Component
 */

import React from 'react';
import { Camera, Download, Film, Layers, Maximize2, RotateCcw, Map, Box, Columns, FileCode } from 'lucide-react';
import { ViewerState } from '../types.ts';

interface HeaderProps {
  currentState: ViewerState;
  activeView: 'map' | '3d' | 'split';
  onChangeView: (view: 'map' | '3d' | 'split') => void;
  onReset: () => void;
  onExportGLB: () => void;
  onSnapshot: () => void;
  onOpenRemotion: () => void;
  onOpenManifest: () => void;
  onOpenHandoff: () => void;
  onOpenGeoExport: () => void;
  onOpenResearcherGeoJson: () => void;
  cinemaMode: boolean;
  onToggleCinemaMode: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentState,
  activeView,
  onChangeView,
  onReset,
  onExportGLB,
  onSnapshot,
  onOpenRemotion,
  onOpenManifest,
  onOpenHandoff,
  onOpenGeoExport,
  onOpenResearcherGeoJson,
  cinemaMode,
  onToggleCinemaMode,
}) => {
  return (
    <header className="absolute top-0 left-0 right-0 z-20 pointer-events-none p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
      {/* Brand & Documentary Title */}
      <div className="pointer-events-auto flex items-center gap-3 bg-[#1C1B19]/90 text-[#F3EBDB] px-4 py-2 rounded-lg border border-[#A98A4B]/40 shadow-xl backdrop-blur-none">
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="font-serif-doc text-xs tracking-[0.25em] text-[#A98A4B] font-bold uppercase">
              RUWAQ
            </span>
            <span className="text-[#A98A4B]/50 text-xs">•</span>
            <span className="font-arabic text-sm text-[#F3EBDB]/90">
              رواق للتوثيق المعماري والجغرافي
            </span>
          </div>
          <h1 className="font-serif-doc text-base font-bold text-[#F3EBDB] tracking-wide flex items-center gap-2">
            BAB ZUWAYLA
            <span className="font-arabic text-[#A98A4B] font-normal text-sm">باب زويلة</span>
          </h1>
        </div>

        <div className="h-7 w-[1px] bg-[#A98A4B]/30 mx-1 hidden sm:block" />

        {/* Chronological State Badge */}
        <div className="hidden sm:flex flex-col text-left">
          <span className="text-[10px] tracking-wider text-[#A98A4B] font-mono-doc uppercase">
            CHRONOLOGY
          </span>
          <span className="text-xs text-[#F3EBDB]/90 font-medium font-mono-doc">
            {currentState === 'FATIMID_ORIGINAL' ? (
              <span className="text-[#F3EBDB]">1092 CE (Fatimid)</span>
            ) : (
              <span>1092 ➔ 1421 CE</span>
            )}
          </span>
        </div>
      </div>

      {/* Center: Documentary View Switcher */}
      <div className="pointer-events-auto flex items-center bg-[#1C1B19]/90 p-1 rounded-lg border border-[#A98A4B]/40 shadow-lg text-xs font-mono-doc">
        <button
          onClick={() => onChangeView('map')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
            activeView === 'map'
              ? 'bg-[#A98A4B] text-[#1C1B19] font-bold shadow-md'
              : 'text-[#D8CEBC]/80 hover:text-[#F3EBDB] hover:bg-[#A98A4B]/20'
          }`}
          title="Historical Geography: MapLibre GL 7-Act Story"
        >
          <Map className="w-3.5 h-3.5" />
          <span>Historical Map</span>
        </button>

        <button
          onClick={() => onChangeView('3d')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
            activeView === '3d'
              ? 'bg-[#A98A4B] text-[#1C1B19] font-bold shadow-md'
              : 'text-[#D8CEBC]/80 hover:text-[#F3EBDB] hover:bg-[#A98A4B]/20'
          }`}
          title="3D Architectural Reconstruction of Bab Zuwayla"
        >
          <Box className="w-3.5 h-3.5" />
          <span>3D Gate Model</span>
        </button>

        <button
          onClick={() => onChangeView('split')}
          className={`hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
            activeView === 'split'
              ? 'bg-[#A98A4B] text-[#1C1B19] font-bold shadow-md'
              : 'text-[#D8CEBC]/80 hover:text-[#F3EBDB] hover:bg-[#A98A4B]/20'
          }`}
          title="Synchronized Split View: Historical Map + 3D Gateway"
        >
          <Columns className="w-3.5 h-3.5" />
          <span>Split View</span>
        </button>
      </div>

      {/* Right: Deliverables, Export & Toolbar */}
      <div className="pointer-events-auto flex items-center gap-1.5 flex-wrap">
        <div className="flex items-center gap-1 bg-[#1C1B19]/90 border border-[#A98A4B]/40 p-1 rounded-lg shadow-lg">
          <button
            onClick={onOpenGeoExport}
            title="Export Working GeoJSON Layers, Map Style, Provenance Manifest & Offline Guide"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs text-[#1C1B19] bg-[#A98A4B] hover:bg-[#c4a45e] transition-colors font-bold shadow-md"
          >
            <Download className="w-3.5 h-3.5" />
            <span>GIS Export</span>
          </button>

          <button
            onClick={onOpenResearcherGeoJson}
            title="Open Researcher GeoJSON Editor & Hypothesis Selector"
            className="flex items-center gap-1 px-2.5 py-1.5 rounded text-xs text-[#F3EBDB] bg-[#8C4729]/80 hover:bg-[#8C4729] transition-colors font-medium"
          >
            <FileCode className="w-3.5 h-3.5 text-[#F3EBDB]" />
            <span className="hidden sm:inline">Researcher</span>
          </button>

          <button
            onClick={onOpenHandoff}
            title="Open 3D Production Deliverables Hub"
            className="flex items-center gap-1 px-2 py-1.5 rounded text-xs text-[#F3EBDB] hover:bg-[#A98A4B]/20 transition-colors"
          >
            <Layers className="w-3.5 h-3.5 text-[#A98A4B]" />
            <span className="hidden sm:inline">3D Assets</span>
          </button>

          <button
            onClick={onSnapshot}
            title="Capture High-Res Documentary Plate"
            className="p-1.5 rounded text-xs text-[#F3EBDB] hover:bg-[#A98A4B]/20 hover:text-[#A98A4B] transition-colors"
          >
            <Camera className="w-3.5 h-3.5 text-[#A98A4B]" />
          </button>

          <button
            onClick={onOpenRemotion}
            title="Remotion Integration Code & Offline Configuration"
            className="flex items-center gap-1 px-2 py-1.5 rounded text-xs text-[#A98A4B] bg-[#A98A4B]/15 hover:bg-[#A98A4B]/30 transition-colors font-medium"
          >
            <Film className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Remotion</span>
          </button>

          <button
            onClick={onReset}
            title="Reset Map and 3D Camera"
            className="p-1.5 rounded text-xs text-[#F3EBDB]/80 hover:text-[#F3EBDB] hover:bg-[#F3EBDB]/10 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={onToggleCinemaMode}
            title={cinemaMode ? 'Show Controls (H)' : 'Cinema Fullscreen View (H)'}
            className="p-1.5 rounded text-xs text-[#A98A4B] hover:bg-[#A98A4B]/20 transition-colors"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </header>
  );
};

