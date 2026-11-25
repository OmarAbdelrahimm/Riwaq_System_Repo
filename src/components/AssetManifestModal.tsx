/**
 * RUWAQ Architectural Asset Manifest & Historical Safety Documentation
 */

import React from 'react';
import { X, Layers, FileText, CheckCircle, AlertTriangle, ShieldCheck } from 'lucide-react';

interface AssetManifestModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AssetManifestModal: React.FC<AssetManifestModalProps> = ({
  isOpen,
  onClose,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 pointer-events-auto">
      <div className="bg-[#1C1B19] border-2 border-[#A98A4B] text-[#F3EBDB] rounded-xl max-w-3xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden font-sans">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#A98A4B]/30 bg-[#151413]">
          <div className="flex items-center gap-2.5">
            <Layers className="w-5 h-5 text-[#A98A4B]" />
            <div>
              <h2 className="font-serif-doc text-base font-bold text-[#F3EBDB]">
                ARCHITECTURAL ASSET MANIFEST
              </h2>
              <p className="text-xs text-[#A98A4B] font-mono-doc">
                Bab Zuwayla 3D Model • RUWAQ Production Assets
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

        {/* Content */}
        <div className="p-4 overflow-y-auto flex flex-col gap-4 text-xs scrollbar-thin">
          {/* Historical Safety Statement */}
          <div className="bg-[#8C4729]/15 border border-[#8C4729]/40 rounded-lg p-3 text-xs leading-relaxed flex flex-col gap-1.5">
            <div className="flex items-center gap-2 font-bold text-[#A98A4B]">
              <ShieldCheck className="w-4 h-4 text-[#A98A4B]" />
              <span>HISTORICAL SAFETY & EDUCATIONAL RECONSTRUCTION NOTICE</span>
            </div>
            <p className="text-[#F3EBDB]/90">
              This 3D reconstruction is an <strong>educational reconstruction</strong> developed for the historical documentary <em>RUWAQ</em>. The gate geometry is faithfully modeled upon in-situ archaeological records from 1092 CE (Vizier Badr al-Jamali) and 1415–1421 CE (Sultan al-Mu'ayyad Shaykh). Where precise internal measurements cannot be established from surface documentation, geometry is appropriately simplified to avoid speculative ornamentation.
            </p>
          </div>

          {/* Primary Visual References */}
          <div className="flex flex-col gap-2">
            <h3 className="font-bold text-[#A98A4B] font-mono-doc uppercase flex items-center gap-1.5">
              <FileText className="w-4 h-4" />
              <span>Primary Documentary References Used:</span>
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5 font-mono-doc text-[11px]">
              <div className="bg-[#151413] border border-[#A98A4B]/20 p-2.5 rounded-lg">
                <span className="text-[#A98A4B] font-bold">1. Storyboard Reference:</span>
                <p className="text-[#F3EBDB]/80 mt-1">
                  <code>download_8973e9ca.png</code>
                  <br />
                  Provided presentation layout, top plan orientation, side comparison, front elevation, and exploded component sequencing.
                </p>
              </div>

              <div className="bg-[#151413] border border-[#A98A4B]/20 p-2.5 rounded-lg">
                <span className="text-[#A98A4B] font-bold">2. Real Monument Photo:</span>
                <p className="text-[#F3EBDB]/80 mt-1">
                  <code>image_8d20f9e3.png</code>
                  <br />
                  Primary visual reference for limestone ashlar masonry, semicircular bastion proportions, cushion voussoirs, upper machicolation bridge, and minaret tiers.
                </p>
              </div>

              <div className="bg-[#151413] border border-[#A98A4B]/20 p-2.5 rounded-lg">
                <span className="text-[#A98A4B] font-bold">3. Portal Interior Photo:</span>
                <p className="text-[#F3EBDB]/80 mt-1">
                  <code>image_191b72fb.png</code>
                  <br />
                  Primary reference for colossal timber gate doors with dense horizontal iron plating straps and hemispherical forged rivets.
                </p>
              </div>
            </div>
          </div>

          {/* Explicitly Named 3D Hierarchy */}
          <div className="flex flex-col gap-2">
            <h3 className="font-bold text-[#A98A4B] font-mono-doc uppercase flex items-center gap-1.5">
              <CheckCircle className="w-4 h-4" />
              <span>Scene Graph Hierarchy (Exportable to GLB):</span>
            </h3>

            <div className="bg-[#100f0e] border border-[#A98A4B]/30 p-3 rounded-lg font-mono-doc text-[11px] leading-relaxed text-[#F3EBDB]/90">
              <p className="text-[#A98A4B]">bab_zuwayla_monument_root</p>
              <p className="pl-4">├── left_semicircular_tower (1092 CE)</p>
              <p className="pl-8">│   ├── left_tower_foundation_plinth</p>
              <p className="pl-8">│   ├── left_tower_shaft</p>
              <p className="pl-8">│   ├── left_tower_arrow_slits</p>
              <p className="pl-8">│   └── left_tower_crenellations (merlons 0..10)</p>
              <p className="pl-4">├── right_semicircular_tower (1092 CE)</p>
              <p className="pl-8">│   ├── right_tower_shaft & arrow slits</p>
              <p className="pl-8">│   └── right_tower_crenellations</p>
              <p className="pl-4">├── central_entrance_arch</p>
              <p className="pl-8">│   ├── pointed_arch_cushion_voussoirs (voussoirs 0..16)</p>
              <p className="pl-8">│   ├── upper_machicolation_gallery_arch</p>
              <p className="pl-8">│   └── gate_passage_vault</p>
              <p className="pl-4">├── fortified_gate_doors_assembly</p>
              <p className="pl-8">│   ├── left_door_pivot (left_door_leaf)</p>
              <p className="pl-8">│   └── right_door_pivot (right_door_leaf)</p>
              <p className="pl-4">├── left_minaret (1415–1421 CE - Sultan al-Mu'ayyad)</p>
              <p className="pl-8">│   ├── left_minaret_tier1_octagonal_shaft</p>
              <p className="pl-8">│   ├── left_minaret_tier2_first_balcony (muqarnas)</p>
              <p className="pl-8">│   ├── left_minaret_tier3_chevron_shaft</p>
              <p className="pl-8">│   ├── left_minaret_tier4_second_balcony</p>
              <p className="pl-8">│   ├── left_minaret_tier5_colonnaded_pavilion (jawsaq)</p>
              <p className="pl-8">│   └── left_minaret_tier6_bulb_finial (mabkhara & hilal)</p>
              <p className="pl-4">└── right_minaret (identical 6-tier architecture)</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-[#A98A4B]/30 bg-[#151413] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded bg-[#A98A4B] text-[#1C1B19] font-bold hover:bg-[#c4a45e] transition-colors text-xs"
          >
            Close Manifest
          </button>
        </div>
      </div>
    </div>
  );
};
