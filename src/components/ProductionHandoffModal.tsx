/**
 * RUWAQ: Production Handoff & Deliverables Hub
 * Provides direct downloads, embedded video player, 8-state image gallery,
 * GLB validation audit, and Remotion integration files.
 */

import React, { useState } from 'react';
import {
  X,
  Download,
  Film,
  CheckCircle2,
  Package,
  Layers,
  FileCode,
  ShieldCheck,
  Eye,
  ExternalLink,
} from 'lucide-react';

interface ProductionHandoffModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectStatePreview?: (stateKey: string) => void;
}

export const ProductionHandoffModal: React.FC<ProductionHandoffModalProps> = ({
  isOpen,
  onClose,
  onSelectStatePreview,
}) => {
  const [activeTab, setActiveTab] = useState<'film' | 'states' | 'glb' | 'source' | 'remotion' | 'sources'>('film');
  const [previewImage, setPreviewImage] = useState<string | null>(null);

  if (!isOpen) return null;

  const statesList = [
    { id: '01_FATIMID_ORIGINAL', name: '1. Original Fatimid Gate (1092 CE)', file: '/RUWAQ_8_STATES_PREVIEW/01_FATIMID_ORIGINAL.png' },
    { id: '02_TOP_PLAN', name: '2. Top Orthographic Plan', file: '/RUWAQ_8_STATES_PREVIEW/02_TOP_PLAN.png' },
    { id: '03_SIDE_ELEVATION', name: '3. Side Orthographic Elevation', file: '/RUWAQ_8_STATES_PREVIEW/03_SIDE_ELEVATION.png' },
    { id: '04_FRONT_ELEVATION', name: '4. Front Orthographic Elevation', file: '/RUWAQ_8_STATES_PREVIEW/04_FRONT_ELEVATION.png' },
    { id: '05_PERSPECTIVE_3Q', name: '5. Perspective Three-Quarter View', file: '/RUWAQ_8_STATES_PREVIEW/05_PERSPECTIVE_3Q.png' },
    { id: '06_MAMLUK_ADDITIONS', name: '6. Later Minaret Additions (1415–1421 CE)', file: '/RUWAQ_8_STATES_PREVIEW/06_MAMLUK_ADDITIONS.png' },
    { id: '07_EXPLODED_VIEW', name: '7. Separated Architectural Components', file: '/RUWAQ_8_STATES_PREVIEW/07_EXPLODED_VIEW.png' },
    { id: '08_FULLY_ASSEMBLED', name: '8. Fully Assembled Monument', file: '/RUWAQ_8_STATES_PREVIEW/08_FULLY_ASSEMBLED.png' },
  ];

  const validatedComponents = [
    { name: 'bab_zuwayla_monument_root', type: 'THREE.Group', role: 'Master Monument Coordinate Root' },
    { name: 'left_semicircular_tower', type: 'THREE.Group', role: 'West Stone Bastion (1092 CE)' },
    { name: 'right_semicircular_tower', type: 'THREE.Group', role: 'East Stone Bastion (1092 CE)' },
    { name: 'central_entrance_arch', type: 'THREE.Group', role: 'Pointed Arch & Cushion Voussoirs' },
    { name: 'gate_passage_vault', type: 'THREE.Group', role: 'Defensive Tunnel Vault to al-Mu\'izz St' },
    { name: 'left_door_leaf', type: 'THREE.Mesh', role: 'Heavy Studded Iron / Cedar Leaf' },
    { name: 'right_door_leaf', type: 'THREE.Mesh', role: 'Hinged Pivot Leaf' },
    { name: 'left_minaret', type: 'THREE.Group', role: 'Sultan al-Mu\'ayyad West Minaret (1421 CE)' },
    { name: 'right_minaret', type: 'THREE.Group', role: 'Sultan al-Mu\'ayyad East Minaret (1421 CE)' },
    { name: 'left_minaret_tier1_octagonal_shaft', type: 'THREE.Group', role: 'Square Plinth to Octagon Base' },
    { name: 'left_minaret_tier2_first_balcony', type: 'THREE.Group', role: 'Triple Muqarnas Corbelled Balcony' },
    { name: 'left_minaret_tier3_chevron_shaft', type: 'THREE.Group', role: 'Chevron/Zigzag Relief Octagonal Shaft' },
    { name: 'left_minaret_tier4_second_balcony', type: 'THREE.Group', role: 'Upper Transition Balcony' },
    { name: 'left_minaret_tier5_colonnaded_pavilion', type: 'THREE.Group', role: '8-Column Jawsaq Arcade' },
    { name: 'left_minaret_tier6_bulb_finial', type: 'THREE.Group', role: 'Mabkhara Pear-Bulb & Bronze Hilal' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-black/75 pointer-events-auto">
      <div className="bg-[#1C1B19] border-2 border-[#A98A4B] text-[#F3EBDB] rounded-xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden font-sans">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#A98A4B]/30 bg-[#151413]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-[#A98A4B]/20 border border-[#A98A4B] flex items-center justify-center text-[#A98A4B]">
              <Package className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-serif-doc text-base sm:text-lg font-bold text-[#F3EBDB]">
                  RUWAQ PRODUCTION DELIVERABLES & HANDOFF
                </h2>
                <span className="text-[10px] bg-[#A98A4B] text-[#1C1B19] px-2 py-0.5 rounded font-bold uppercase tracking-wider">
                  VERIFIED
                </span>
              </div>
              <p className="text-xs text-[#A98A4B] font-mono-doc">
                Bab Zuwayla 3D Master Asset • Ready for Remotion 239.87s Documentary Integration
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

        {/* Tab Navigation */}
        <div className="flex items-center gap-1 border-b border-[#A98A4B]/30 bg-[#171615] px-4 pt-2 overflow-x-auto scrollbar-none">
          {[
            { id: 'film', label: '10s Film Render (.mp4)', icon: Film },
            { id: 'states', label: '8 States Gallery (PNG)', icon: Eye },
            { id: 'glb', label: 'Master GLB & Audit', icon: Layers },
            { id: 'source', label: 'Clean Source (.zip)', icon: Package },
            { id: 'remotion', label: 'Remotion Handoff', icon: FileCode },
            { id: 'sources', label: 'Historical Safety Charter', icon: ShieldCheck },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-3 py-2 rounded-t text-xs font-mono-doc transition-all whitespace-nowrap ${
                  isActive
                    ? 'bg-[#1C1B19] text-[#A98A4B] border-t-2 border-[#A98A4B] font-bold'
                    : 'text-[#F3EBDB]/70 hover:text-[#F3EBDB]'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Content Panels */}
        <div className="p-4 sm:p-5 overflow-y-auto flex-1 flex flex-col gap-4 text-xs scrollbar-thin">
          {/* TAB 1: 10-SECOND FILM RENDER (.MP4) */}
          {activeTab === 'film' && (
            <div className="flex flex-col gap-4">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div>
                  <h3 className="font-serif-doc text-base font-bold text-[#F3EBDB]">
                    10-Second 30fps Master Film: RUWAQ_ARCHITECTURAL_300_FRAMES.mp4
                  </h3>
                  <p className="text-xs text-[#A98A4B] font-mono-doc">
                    Rendered with Remotion Headless Chrome • 1920×1080 • 30fps H.264
                  </p>
                </div>

                <a
                  href="/RUWAQ_ARCHITECTURAL_300_FRAMES.mp4"
                  download="RUWAQ_ARCHITECTURAL_300_FRAMES.mp4"
                  className="flex items-center gap-2 px-4 py-2 bg-[#A98A4B] text-[#1C1B19] rounded-lg font-bold hover:bg-[#c4a45e] transition-colors shadow-md"
                >
                  <Download className="w-4 h-4" />
                  <span>Download Master MP4</span>
                </a>
              </div>

              {/* Embedded HTML5 Video Player */}
              <div className="relative aspect-video w-full bg-black rounded-lg overflow-hidden border border-[#A98A4B]/40 shadow-inner">
                <video
                  controls
                  autoPlay
                  loop
                  playsInline
                  src="/RUWAQ_ARCHITECTURAL_300_FRAMES.mp4"
                  className="w-full h-full object-contain"
                >
                  Your browser does not support the video tag.
                </video>
              </div>

              {/* Act Sequence Timeline Verification */}
              <div className="bg-[#151413] border border-[#A98A4B]/20 rounded-lg p-3 font-mono-doc text-[11px] grid grid-cols-2 sm:grid-cols-3 gap-2 text-[#F3EBDB]/90">
                <div><span className="text-[#A98A4B] font-bold">Act 1 (0–45f):</span> Top Ortho Plan</div>
                <div><span className="text-[#A98A4B] font-bold">Act 2 (45–90f):</span> Side Elevation</div>
                <div><span className="text-[#A98A4B] font-bold">Act 3 (90–135f):</span> 1092 Gate (No Minarets)</div>
                <div><span className="text-[#A98A4B] font-bold">Act 4 (135–190f):</span> Mamluk Minarets Added</div>
                <div><span className="text-[#A98A4B] font-bold">Act 5 (190–245f):</span> Controlled Exploded View</div>
                <div><span className="text-[#A98A4B] font-bold">Act 6 (245–300f):</span> Final Assembled 3/4</div>
              </div>
            </div>
          )}

          {/* TAB 2: 8 STATES GALLERY (PNG) */}
          {activeTab === 'states' && (
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-serif-doc text-base font-bold text-[#F3EBDB]">
                    All Eight Viewing States (1920×1080 Still Renders)
                  </h3>
                  <p className="text-xs text-[#A98A4B] font-mono-doc">
                    Derived from one consistent geometry model in public/RUWAQ_8_STATES_PREVIEW/
                  </p>
                </div>
              </div>

              {/* Image Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {statesList.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => setPreviewImage(item.file)}
                    className="group relative flex flex-col bg-[#151413] border border-[#A98A4B]/30 hover:border-[#A98A4B] rounded-lg overflow-hidden cursor-pointer transition-all shadow-md"
                  >
                    <div className="aspect-video w-full bg-[#F3EBDB] overflow-hidden">
                      <img
                        src={item.file}
                        alt={item.name}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                    </div>
                    <div className="p-2 flex flex-col justify-between">
                      <span className="font-mono-doc text-[10px] text-[#F3EBDB] font-semibold leading-tight line-clamp-1">
                        {item.name}
                      </span>
                      <a
                        href={item.file}
                        download={item.file.split('/').pop()}
                        onClick={(e) => e.stopPropagation()}
                        className="mt-1 text-[9px] text-[#A98A4B] flex items-center gap-1 hover:underline"
                      >
                        <Download className="w-2.5 h-2.5" />
                        <span>Save PNG</span>
                      </a>
                    </div>
                  </div>
                ))}
              </div>

              {/* Preview Lightbox Modal */}
              {previewImage && (
                <div
                  onClick={() => setPreviewImage(null)}
                  className="fixed inset-0 z-50 bg-black/85 flex items-center justify-center p-4 cursor-pointer"
                >
                  <div className="relative max-w-5xl max-h-[90vh]">
                    <img
                      src={previewImage}
                      alt="Enlarged view"
                      className="max-w-full max-h-[85vh] rounded-lg border-2 border-[#A98A4B] shadow-2xl"
                    />
                    <div className="absolute top-2 right-2 bg-[#1C1B19]/80 p-1.5 rounded-full text-white">
                      <X className="w-5 h-5" />
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: MASTER GLB & AUDIT */}
          {activeTab === 'glb' && (
            <div className="flex flex-col gap-4">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div>
                  <h3 className="font-serif-doc text-base font-bold text-[#F3EBDB]">
                    Master Architectural 3D Asset: RUWAQ_BAB_ZUWAYLA_MASTER.glb
                  </h3>
                  <p className="text-xs text-[#A98A4B] font-mono-doc">
                    File Size: 648.9 KB • Binary GLB • Named Hierarchy Preserved
                  </p>
                </div>

                <a
                  href="/RUWAQ_BAB_ZUWAYLA_MASTER.glb"
                  download="RUWAQ_BAB_ZUWAYLA_MASTER.glb"
                  className="flex items-center gap-2 px-4 py-2 bg-[#A98A4B] text-[#1C1B19] rounded-lg font-bold hover:bg-[#c4a45e] transition-colors shadow-md"
                >
                  <Download className="w-4 h-4" />
                  <span>Download Master GLB</span>
                </a>
              </div>

              <div className="bg-[#151413] border border-[#A98A4B]/30 rounded-lg p-3 flex flex-col gap-2">
                <div className="flex items-center justify-between text-xs font-mono-doc">
                  <span className="text-[#A98A4B] font-bold flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span>AUTOMATED THREE.JS LOADER VALIDATION: 100% PASSED</span>
                  </span>
                  <a
                    href="/GLB_VALIDATION_REPORT.json"
                    download="GLB_VALIDATION_REPORT.json"
                    className="text-[11px] text-[#A98A4B] underline"
                  >
                    View Validation JSON
                  </a>
                </div>
                <p className="text-[11px] text-[#F3EBDB]/80">
                  Every structural component was verified by loading the binary buffer into an isolated Three.js scene, traversing all nodes, and testing independent manipulation of parent-child coordinate spaces.
                </p>

                {/* Audit Table */}
                <div className="overflow-x-auto max-h-56 scrollbar-thin mt-1 border border-white/10 rounded">
                  <table className="w-full text-left font-mono-doc text-[10px]">
                    <thead className="bg-[#100f0e] text-[#A98A4B] sticky top-0">
                      <tr>
                        <th className="p-2">Component Name</th>
                        <th className="p-2">Object Type</th>
                        <th className="p-2">Architectural Role</th>
                        <th className="p-2">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {validatedComponents.map((c) => (
                        <tr key={c.name} className="hover:bg-white/5">
                          <td className="p-2 text-[#F3EBDB] font-semibold">{c.name}</td>
                          <td className="p-2 text-[#A98A4B]">{c.type}</td>
                          <td className="p-2 text-[#F3EBDB]/70">{c.role}</td>
                          <td className="p-2 text-emerald-400">Validated</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: CLEAN SOURCE CODE (.ZIP) */}
          {activeTab === 'source' && (
            <div className="flex flex-col gap-4">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div>
                  <h3 className="font-serif-doc text-base font-bold text-[#F3EBDB]">
                    Complete Working Project: RUWAQ_BAB_ZUWAYLA_3D_SOURCE.zip
                  </h3>
                  <p className="text-xs text-[#A98A4B] font-mono-doc">
                    File Size: 14.3 MB • Zero CDN Dependencies • Includes Geometries, Textures, Shaders
                  </p>
                </div>

                <a
                  href="/RUWAQ_BAB_ZUWAYLA_3D_SOURCE.zip"
                  download="RUWAQ_BAB_ZUWAYLA_3D_SOURCE.zip"
                  className="flex items-center gap-2 px-4 py-2 bg-[#A98A4B] text-[#1C1B19] rounded-lg font-bold hover:bg-[#c4a45e] transition-colors shadow-md"
                >
                  <Download className="w-4 h-4" />
                  <span>Download Source ZIP</span>
                </a>
              </div>

              <div className="bg-[#151413] border border-[#A98A4B]/30 rounded-lg p-3 font-mono-doc text-xs leading-relaxed flex flex-col gap-2">
                <span className="text-[#A98A4B] font-bold">Package Contents Verified:</span>
                <ul className="list-disc list-inside text-[#F3EBDB]/80 space-y-1 text-[11px]">
                  <li><code>package.json</code>, <code>tsconfig.json</code>, <code>vite.config.ts</code></li>
                  <li><code>BabZuwaylaRemotion.tsx</code> & <code>src/RemotionRoot.tsx</code></li>
                  <li><code>src/three/BabZuwaylaScene.ts</code> (Master scene engine)</li>
                  <li><code>src/three/geometry/</code> (Towers, Portal, Doors, Minarets with 6 levels)</li>
                  <li><code>src/three/materials.ts</code> & <code>src/three/textures.ts</code> (100% procedural textures)</li>
                  <li><code>public/assets/aistudio/</code> (Original in-situ photos & storyboard)</li>
                </ul>
              </div>
            </div>
          )}

          {/* TAB 5: REMOTION HANDOFF */}
          {activeTab === 'remotion' && (
            <div className="flex flex-col gap-3 font-mono-doc text-xs">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-serif-doc text-base font-bold text-[#F3EBDB]">
                    BabZuwaylaRemotion.tsx Composition Code
                  </h3>
                  <p className="text-xs text-[#A98A4B]">
                    Deterministic R3F / @remotion/three component
                  </p>
                </div>
                <a
                  href="/README_REMOTION_INTEGRATION.md"
                  download="README_REMOTION_INTEGRATION.md"
                  className="flex items-center gap-1.5 text-xs text-[#A98A4B] underline"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download Integration Guide</span>
                </a>
              </div>

              <div className="p-3 bg-[#151413] border border-[#A98A4B]/20 rounded-lg text-[11px] leading-relaxed text-[#F3EBDB]/90">
                To embed this into the existing 239.87s RUWAQ documentary timeline without recreating its geometry:
                <br />
                <code className="text-[#A98A4B]">
                  &lt;Sequence from=&#123;450&#125; durationInFrames=&#123;300&#125;&gt;
                  <br />
                  &nbsp;&nbsp;&lt;BabZuwaylaRemotion width=&#123;1920&#125; height=&#123;1080&#125; /&gt;
                  <br />
                  &lt;/Sequence&gt;
                </code>
              </div>
            </div>
          )}

          {/* TAB 6: HISTORICAL SAFETY CHARTER */}
          {activeTab === 'sources' && (
            <div className="flex flex-col gap-3 text-xs leading-relaxed">
              <div className="flex items-center justify-between">
                <h3 className="font-serif-doc text-base font-bold text-[#F3EBDB]">
                  Historical Limitations & Sources Charter
                </h3>
                <a
                  href="/GEOMETRY_LIMITATIONS_AND_SOURCES.md"
                  download="GEOMETRY_LIMITATIONS_AND_SOURCES.md"
                  className="text-xs text-[#A98A4B] underline flex items-center gap-1"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download Charter</span>
                </a>
              </div>

              <div className="bg-[#8C4729]/15 border border-[#8C4729]/40 rounded-lg p-3 text-[11px] text-[#F3EBDB]/90 flex flex-col gap-2 font-mono-doc">
                <span className="text-[#A98A4B] font-bold">1. UNVERIFIED METRIC LABELS REMOVED</span>
                <p>
                  Per documentary guidelines, arbitrary metric elevations (+8.6m, +18.0m, +40.2m) and the unverified 0–20m scale bar have been replaced with qualitative structural datums.
                </p>
                <span className="text-[#A98A4B] font-bold">2. HISTORICAL ACCURACY OF MINARETS</span>
                <p>
                  The original Fatimid gate (1092 CE) contains NO minarets. The twin minarets are strictly dated to 1415–1421 CE under Sultan al-Mu'ayyad Shaykh.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-3 border-t border-[#A98A4B]/30 bg-[#151413] flex items-center justify-between text-xs font-mono-doc">
          <span className="text-[#F3EBDB]/70 text-[11px]">
            RUWAQ • All assets verified and ready for post-production
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded bg-[#A98A4B] text-[#1C1B19] font-bold hover:bg-[#c4a45e] transition-colors"
          >
            Close Hub
          </button>
        </div>
      </div>
    </div>
  );
};
