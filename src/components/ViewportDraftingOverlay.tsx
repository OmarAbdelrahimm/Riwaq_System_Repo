/**
 * Architectural Drafting Viewport Overlay
 * Displays compass rose, scale bar, dimension datum, and educational stamps
 * Matching the storyboard panel download_8973e9ca.png
 */

import React from 'react';
import { Compass } from 'lucide-react';
import { ViewerState } from '../types.ts';

interface ViewportDraftingOverlayProps {
  currentState: ViewerState;
  cameraMode: 'orthographic' | 'perspective';
}

export const ViewportDraftingOverlay: React.FC<ViewportDraftingOverlayProps> = ({
  currentState,
  cameraMode,
}) => {
  const isOrtho = cameraMode === 'orthographic';

  return (
    <div className="absolute inset-0 pointer-events-none z-10 overflow-hidden">
      {/* 1. Compass Rose (Top-Left) - Especially active in Top Plan */}
      <div className="absolute top-20 left-4 sm:left-6 flex flex-col items-center gap-1 font-mono-doc text-[#1C1B19]">
        <div className="bg-[#1C1B19]/80 text-[#F3EBDB] px-2.5 py-1 rounded border border-[#A98A4B]/40 shadow-sm flex items-center gap-1.5 text-xs">
          <Compass className="w-3.5 h-3.5 text-[#A98A4B]" />
          <span className="font-bold text-[#A98A4B]">N</span>
          <span className="text-[10px] text-[#F3EBDB]/80 font-arabic">شمال</span>
        </div>

        {currentState === 'TOP_PLAN' && (
          <div className="flex flex-col items-center text-[10px] text-[#1C1B19]/70 bg-[#F3EBDB]/90 px-2 py-1 rounded border border-[#A98A4B]/30 shadow-sm mt-1">
            <span className="font-arabic font-bold text-[#8C4729]">إلى داخل القاهرة ⬆</span>
            <span className="text-[9px] uppercase tracking-wider">Towards Al-Mu'izz St</span>
          </div>
        )}
      </div>

      {/* 2. Top-Right Architectural Plate Identifier */}
      <div className="absolute top-20 right-4 sm:right-6 text-right font-mono-doc">
        <div className="bg-[#1C1B19]/85 text-[#F3EBDB] px-3.5 py-2 rounded-lg border border-[#A98A4B]/40 shadow-md">
          <div className="text-[10px] text-[#A98A4B] font-bold tracking-widest uppercase">
            {currentState === 'TOP_PLAN' && 'PLATE 01 • ARCHITECTURAL PLAN'}
            {currentState === 'SIDE_ELEVATION' && 'PLATE 02 • SIDE ELEVATION'}
            {currentState === 'FRONT_ELEVATION' && 'PLATE 03 • FRONT ELEVATION'}
            {currentState === 'FATIMID_ORIGINAL' && 'PLATE 04 • FATIMID MONUMENT (1092 CE)'}
            {currentState === 'MAMLUK_ADDITIONS' && 'PLATE 05 • MAMLUK MINARETS (1415–1421 CE)'}
            {currentState === 'EXPLODED_VIEW' && 'PLATE 06 • EXPLODED DECONSTRUCTION'}
            {currentState === 'PERSPECTIVE_3Q' && 'PLATE 07 • 3/4 CINEMATIC PERSPECTIVE'}
            {currentState === 'FULLY_ASSEMBLED' && 'PLATE 08 • FINAL COMPOSITION'}
          </div>

          <div className="font-serif-doc text-sm font-bold text-[#F3EBDB] mt-0.5">
            {currentState === 'TOP_PLAN' && 'المسقط الأفقي لباب زويلة'}
            {currentState === 'SIDE_ELEVATION' && 'المسقط الجانبي التاريخي'}
            {currentState === 'FRONT_ELEVATION' && 'الواجهة المعمارية الجنوبية'}
            {currentState === 'FATIMID_ORIGINAL' && 'البوابة الفاطمية الأصلية دون مآذن'}
            {currentState === 'MAMLUK_ADDITIONS' && 'إضافات مئذنتي السلطان المؤيد شيخ'}
            {currentState === 'EXPLODED_VIEW' && 'المخطط التفكيكي للمكونات المعمارية'}
            {currentState === 'PERSPECTIVE_3Q' && 'منظور عين الطائر الوثائقي'}
            {currentState === 'FULLY_ASSEMBLED' && 'التكوين المعماري النهائي الكامل'}
          </div>
        </div>
      </div>

      {/* 3. Qualitative Proportional Scale Bar (No unverified numbers) */}
      <div className="absolute bottom-28 left-4 sm:left-6 flex flex-col gap-1 font-mono-doc text-[#1C1B19]">
        <div className="bg-[#F3EBDB]/95 text-[#1C1B19] px-3 py-1.5 rounded border border-[#A98A4B]/50 shadow-sm flex flex-col max-w-[220px]">
          <div className="flex justify-between text-[8px] text-[#1C1B19] font-bold px-0.5 uppercase tracking-wider">
            <span>Datum A</span>
            <span>Relative Span</span>
            <span>Datum B</span>
          </div>

          {/* Proportional Segmented Bar without unverified metric units */}
          <div className="w-full h-1.5 bg-[#1C1B19] border border-[#1C1B19] flex mt-0.5">
            <div className="w-1/4 h-full bg-[#1C1B19]" />
            <div className="w-1/4 h-full bg-[#A98A4B]" />
            <div className="w-1/4 h-full bg-[#F3EBDB]" />
            <div className="w-1/4 h-full bg-[#1C1B19]" />
          </div>

          <span className="text-[7.5px] text-[#8C4729] font-bold text-center mt-1 uppercase tracking-tight">
            PROPORTIONAL STUDY • UNVERIFIED METRICS REMOVED
          </span>
        </div>
      </div>

      {/* 4. Qualitative Structural Datum Levels (No unverified exact meter figures) */}
      {isOrtho && (currentState === 'FRONT_ELEVATION' || currentState === 'SIDE_ELEVATION') && (
        <div className="absolute left-4 top-1/2 -translate-y-1/2 flex flex-col gap-9 font-mono-doc text-[9px] text-[#1C1B19]/80 hidden sm:flex">
          <div className="flex items-center gap-2">
            <span className="w-6 h-[1px] bg-[#A98A4B]" />
            <span className="bg-[#F3EBDB]/95 px-1.5 py-0.5 rounded border border-[#A98A4B]/40">
              Finial Apex Level (Mamluk 1421)
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-6 h-[1px] bg-[#A98A4B]" />
            <span className="bg-[#F3EBDB]/95 px-1.5 py-0.5 rounded border border-[#A98A4B]/40">
              Tower Parapet Crest (Fatimid 1092)
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-6 h-[1px] bg-[#A98A4B]" />
            <span className="bg-[#F3EBDB]/95 px-1.5 py-0.5 rounded border border-[#A98A4B]/40">
              Portal Arch Springing Line
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-6 h-[1px] bg-[#1C1B19]" />
            <span className="bg-[#1C1B19] text-[#F3EBDB] px-1.5 py-0.5 rounded">
              Cairo Street Datum Level
            </span>
          </div>
        </div>
      )}

      {/* 5. Historical Reconstruction Disclaimer (Bottom-Right) */}
      <div className="absolute bottom-28 right-4 sm:right-6 hidden sm:flex flex-col items-end font-mono-doc text-[9px] text-[#1C1B19]/70">
        <div className="bg-[#F3EBDB]/95 px-2.5 py-1.5 rounded border border-[#A98A4B]/40 shadow-sm text-right max-w-xs">
          <span className="text-[#8C4729] font-bold">APPROXIMATE EDUCATIONAL RECONSTRUCTION</span>
          <div className="text-[8px] text-[#1C1B19]/80 mt-0.5 leading-tight">
            Geometric proportions derived from visible architectural surveys. Precise metric measurements omitted pending laser photogrammetry.
          </div>
          <div className="font-arabic text-[10px] text-[#1C1B19] mt-0.5">
            إعادة بناء تعليمية تقريبية — وثائقي رواق
          </div>
        </div>
      </div>
    </div>
  );
};
