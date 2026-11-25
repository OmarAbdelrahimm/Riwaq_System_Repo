/**
 * RUWAQ Historical Geography: Feature Provenance Inspector Card
 * Detailed documentary card for clicked archaeological & geographic features.
 */

import React from 'react';
import { MapPin, Calendar, User, BookOpen, ExternalLink, ShieldCheck, AlertCircle } from 'lucide-react';
import { GeoFeatureMetadata } from './types.ts';

interface FeatureInspectorModalProps {
  feature: GeoFeatureMetadata | null;
  onClose: () => void;
  onJumpToCoordinates?: (coords: [number, number]) => void;
}

export const FeatureInspectorModal: React.FC<FeatureInspectorModalProps> = ({
  feature,
  onClose,
  onJumpToCoordinates,
}) => {
  if (!feature) return null;

  const isPoint =
    Array.isArray(feature.coordinates) &&
    feature.coordinates.length === 2 &&
    typeof feature.coordinates[0] === 'number';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#1C1B19]/70 backdrop-blur-sm">
      <div className="w-full max-w-xl bg-[#F3EBDB] text-[#1C1B19] border-2 border-[#A98A4B] rounded-2xl shadow-2xl overflow-hidden flex flex-col">
        {/* Card Header */}
        <div className="bg-[#1C1B19] text-[#F3EBDB] p-4 flex items-center justify-between border-b border-[#A98A4B]/40">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-[#A98A4B]/20 text-[#A98A4B]">
              <MapPin className="w-4 h-4" />
            </span>
            <span className="text-xs font-mono-doc uppercase tracking-widest text-[#A98A4B]">
              HISTORICAL FEATURE PROVENANCE
            </span>
          </div>

          <button
            onClick={onClose}
            className="text-[#D8CEBC]/70 hover:text-[#F3EBDB] p-1 rounded font-mono-doc text-xs"
          >
            ✕ Close
          </button>
        </div>

        {/* Feature Titles */}
        <div className="p-6 border-b border-[#A98A4B]/20 bg-[#ECE2CE]">
          <div className="flex items-center justify-between gap-2 mb-1">
            <h2 className="font-serif-doc text-lg font-bold text-[#1C1B19]">
              {feature.nameEn}
            </h2>
            <span className="font-arabic text-base font-bold text-[#8C4729]">
              {feature.nameAr}
            </span>
          </div>

          <div className="flex items-center gap-2 flex-wrap text-xs font-mono-doc mt-2">
            <span className="px-2 py-0.5 rounded bg-[#1C1B19] text-[#A98A4B]">
              {feature.era}
            </span>
            <span className="px-2 py-0.5 rounded bg-[#A98A4B]/30 text-[#1C1B19] font-medium">
              {feature.dateAttested}
            </span>
            <span
              className={`px-2 py-0.5 rounded font-bold ${
                feature.archaeologicalCertainty.includes('Absolute')
                  ? 'bg-emerald-200 text-emerald-950'
                  : 'bg-amber-200 text-amber-950'
              }`}
            >
              Certainty: {feature.archaeologicalCertainty}
            </span>
          </div>
        </div>

        {/* Detailed Metadata Grid */}
        <div className="p-6 space-y-4 text-xs font-mono-doc overflow-y-auto max-h-[50vh] scrollbar-thin">
          {/* Narrative */}
          <div>
            <span className="text-[10px] text-[#8C4729] font-bold uppercase tracking-wider block mb-1">
              ARCHITECTURAL & HISTORICAL OVERVIEW
            </span>
            <p className="text-xs font-sans text-[#1C1B19]/90 leading-relaxed">
              {feature.descriptionEn}
            </p>
            <p className="text-xs font-arabic text-[#1C1B19]/80 leading-relaxed mt-2 text-right">
              {feature.descriptionAr}
            </p>
          </div>

          {/* Builder / Patron */}
          {(feature.patron || feature.architectMaster) && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-3 border-t border-[#A98A4B]/20">
              {feature.patron && (
                <div>
                  <span className="text-[10px] text-[#A98A4B] font-bold uppercase">PATRON</span>
                  <p className="text-xs text-[#1C1B19]">{feature.patron}</p>
                </div>
              )}
              {feature.architectMaster && (
                <div>
                  <span className="text-[10px] text-[#A98A4B] font-bold uppercase">MASTER BUILDERS</span>
                  <p className="text-xs text-[#1C1B19]">{feature.architectMaster}</p>
                </div>
              )}
            </div>
          )}

          {/* Coordinates & Source */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-3 border-t border-[#A98A4B]/20">
            <div>
              <span className="text-[10px] text-[#A98A4B] font-bold uppercase">GEOGRAPHIC COORDS</span>
              <p className="text-xs text-[#1C1B19]">
                {isPoint
                  ? `${(feature.coordinates as [number, number])[1].toFixed(5)}° N, ${(feature.coordinates as [number, number])[0].toFixed(5)}° E`
                  : 'Polyline / Boundary Coordinates'}
              </p>
            </div>
            {feature.osmReference && (
              <div>
                <span className="text-[10px] text-[#A98A4B] font-bold uppercase">OSM IDENTIFIER</span>
                <p className="text-xs text-[#1C1B19]">{feature.osmReference}</p>
              </div>
            )}
          </div>

          {/* Academic Citation */}
          <div className="pt-3 border-t border-[#A98A4B]/20 bg-[#ECE2CE] p-3 rounded-lg">
            <span className="text-[10px] text-[#8C4729] font-bold uppercase block mb-1 flex items-center gap-1.5">
              <BookOpen className="w-3.5 h-3.5" />
              SCHOLARLY CITATION
            </span>
            <p className="text-[11px] font-sans italic text-[#1C1B19]/90">
              {feature.citation}
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="p-3 px-6 bg-[#E8DCBF] border-t border-[#A98A4B]/30 flex items-center justify-between text-xs font-mono-doc">
          <span className="text-[#1C1B19]/70">RUWAQ Documentary Provenance Archive</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-[#1C1B19] text-[#F3EBDB] hover:bg-[#A98A4B] hover:text-[#1C1B19] transition-all font-bold"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
