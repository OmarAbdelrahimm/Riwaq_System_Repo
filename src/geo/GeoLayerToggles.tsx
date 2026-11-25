/**
 * RUWAQ Historical Geography: Layer Visibility & Provenance Inspector
 * Allows independent toggling of every modern and historical cartographic layer,
 * with clear badges distinguishing modern verified survey from archaeological reconstructions.
 */

import React from 'react';
import { Layers, Eye, EyeOff, ShieldAlert, CheckCircle2, MapPin, Sparkles } from 'lucide-react';
import { LayerVisibilityState } from './types.ts';

interface GeoLayerTogglesProps {
  visibility: LayerVisibilityState;
  onChangeVisibility: (updater: Partial<LayerVisibilityState>) => void;
  isOpen: boolean;
  onToggleOpen: () => void;
  onOpenResearcherModal: () => void;
}

export const GeoLayerToggles: React.FC<GeoLayerTogglesProps> = ({
  visibility,
  onChangeVisibility,
  isOpen,
  onToggleOpen,
  onOpenResearcherModal,
}) => {
  if (!isOpen) {
    return (
      <button
        onClick={onToggleOpen}
        className="absolute top-20 right-6 z-20 pointer-events-auto bg-[#1C1B19]/90 text-[#F3EBDB] border border-[#A98A4B]/50 px-3 py-2 rounded-lg shadow-xl text-xs font-mono-doc flex items-center gap-2 hover:bg-[#1C1B19] transition-all cursor-pointer"
      >
        <Layers className="w-4 h-4 text-[#A98A4B]" />
        <span>Layers & Provenance</span>
      </button>
    );
  }

  return (
    <div className="absolute top-20 right-6 z-20 pointer-events-auto w-80 bg-[#1C1B19]/95 text-[#F3EBDB] border border-[#A98A4B] rounded-xl shadow-2xl backdrop-blur-none flex flex-col max-h-[75vh] overflow-hidden">
      {/* Panel Header */}
      <div className="p-3 border-b border-[#A98A4B]/30 flex items-center justify-between bg-[#2A2824]">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-[#A98A4B]" />
          <span className="font-serif-doc text-xs font-bold text-[#F3EBDB] tracking-wider uppercase">
            Cartographic Layers
          </span>
        </div>
        <button
          onClick={onToggleOpen}
          className="text-[#D8CEBC]/70 hover:text-[#F3EBDB] text-xs font-mono-doc p-1"
        >
          ✕
        </button>
      </div>

      {/* Layer List Scroll Area */}
      <div className="p-3 overflow-y-auto space-y-4 text-xs font-mono-doc scrollbar-thin">
        {/* Section: Modern Survey Data */}
        <div>
          <div className="text-[10px] text-[#A98A4B] font-bold uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            <span>Modern Verified Data (OSM)</span>
          </div>

          <div className="space-y-1">
            <label className="flex items-center justify-between p-1.5 rounded hover:bg-[#2A2824] cursor-pointer">
              <span className="text-[#F3EBDB]/90">Modern Streets & Bridges</span>
              <input
                type="checkbox"
                checked={visibility.modernStreets}
                onChange={(e) => onChangeVisibility({ modernStreets: e.target.checked })}
                className="accent-[#A98A4B]"
              />
            </label>

            <label className="flex items-center justify-between p-1.5 rounded hover:bg-[#2A2824] cursor-pointer">
              <span className="text-[#F3EBDB]/90">River Nile & Islands</span>
              <input
                type="checkbox"
                checked={visibility.nileWater}
                onChange={(e) => onChangeVisibility({ nileWater: e.target.checked })}
                className="accent-[#A98A4B]"
              />
            </label>
          </div>
        </div>

        {/* Section: UNESCO Historic Cairo Boundary */}
        <div>
          <div className="text-[10px] text-[#A98A4B] font-bold uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            <span>Legal Monument Boundaries</span>
          </div>

          <label className="flex items-center justify-between p-1.5 rounded hover:bg-[#2A2824] cursor-pointer">
            <div>
              <span className="text-[#F3EBDB]/90">Historic Cairo (UNESCO Ref 89)</span>
              <p className="text-[9px] text-[#D8CEBC]/60 font-sans">Official World Heritage Boundary (1979)</p>
            </div>
            <input
              type="checkbox"
              checked={visibility.historicCairoUnesco}
              onChange={(e) => onChangeVisibility({ historicCairoUnesco: e.target.checked })}
              className="accent-[#A98A4B]"
            />
          </label>
        </div>

        {/* Section: Historical Reconstruction & Approximations */}
        <div>
          <div className="text-[10px] text-[#8C4729] font-bold uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
            <ShieldAlert className="w-3 h-3 text-amber-500" />
            <span>Archaeological Reconstruction</span>
          </div>

          <div className="space-y-1.5">
            <label className="flex items-center justify-between p-1.5 rounded hover:bg-[#2A2824] cursor-pointer">
              <div>
                <span className="text-[#F3EBDB]/90">Approx. Fatimid Enclosure (1092)</span>
                <span className="inline-block ml-1 px-1 py-0.2 bg-[#8C4729] text-[8px] text-[#F3EBDB] rounded">
                  Approx.
                </span>
              </div>
              <input
                type="checkbox"
                checked={visibility.fatimidApproximateExtent}
                onChange={(e) => onChangeVisibility({ fatimidApproximateExtent: e.target.checked })}
                className="accent-[#8C4729]"
              />
            </label>

            <label className="flex items-center justify-between p-1.5 rounded hover:bg-[#2A2824] cursor-pointer">
              <div>
                <span className="text-[#F3EBDB]/90">Uncertainty Buffer (±50m)</span>
                <p className="text-[9px] text-[#D8CEBC]/60 font-sans">Archaeological tolerance margin</p>
              </div>
              <input
                type="checkbox"
                checked={visibility.uncertaintyBuffer}
                onChange={(e) => onChangeVisibility({ uncertaintyBuffer: e.target.checked })}
                className="accent-[#8C4729]"
              />
            </label>

            <label className="flex items-center justify-between p-1.5 rounded hover:bg-[#2A2824] cursor-pointer">
              <span className="text-[#F3EBDB]/90">Al-Mu‘izz Ceremonial Spine</span>
              <input
                type="checkbox"
                checked={visibility.alMuizzAxis}
                onChange={(e) => onChangeVisibility({ alMuizzAxis: e.target.checked })}
                className="accent-[#A98A4B]"
              />
            </label>

            <label className="flex items-center justify-between p-1.5 rounded hover:bg-[#2A2824] cursor-pointer">
              <span className="text-[#F3EBDB]/90">Northern Gates (al-Futuh / al-Nasr)</span>
              <input
                type="checkbox"
                checked={visibility.northernGates}
                onChange={(e) => onChangeVisibility({ northernGates: e.target.checked })}
                className="accent-[#A98A4B]"
              />
            </label>

            <label className="flex items-center justify-between p-1.5 rounded hover:bg-[#2A2824] cursor-pointer">
              <div>
                <span className="text-[#A98A4B] font-bold">★ Bab Zuwayla (Southern Anchor)</span>
                <p className="text-[9px] text-[#D8CEBC]/60 font-sans">1092 CE gate & 1415 CE minarets</p>
              </div>
              <input
                type="checkbox"
                checked={visibility.babZuwaylaSouthernAnchor}
                onChange={(e) => onChangeVisibility({ babZuwaylaSouthernAnchor: e.target.checked })}
                className="accent-[#A98A4B]"
              />
            </label>
          </div>
        </div>

        {/* Section: 3D Model Transition */}
        <div className="pt-2 border-t border-[#A98A4B]/20">
          <label className="flex items-center justify-between p-1.5 rounded hover:bg-[#2A2824] cursor-pointer">
            <span className="text-[#A98A4B] font-bold flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" />
              <span>3D Model Overlay</span>
            </span>
            <input
              type="checkbox"
              checked={visibility.threeDOverlay}
              onChange={(e) => onChangeVisibility({ threeDOverlay: e.target.checked })}
              className="accent-[#A98A4B]"
            />
          </label>
        </div>
      </div>

      {/* Panel Footer: Researcher GeoJSON Hook */}
      <div className="p-3 border-t border-[#A98A4B]/30 bg-[#2A2824] flex items-center justify-between">
        <button
          onClick={onOpenResearcherModal}
          className="w-full py-1.5 px-2 bg-[#8C4729] hover:bg-[#a35330] text-[#F3EBDB] rounded text-[11px] font-bold font-mono-doc transition-all text-center shadow-sm"
        >
          Researcher GeoJSON Editor ⚙
        </button>
      </div>
    </div>
  );
};
