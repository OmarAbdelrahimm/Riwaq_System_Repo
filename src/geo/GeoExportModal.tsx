/**
 * RUWAQ Historical Geography: Production Export & Provenance Manifest Hub
 * Generates and downloads:
 * 1. Complete GeoJSON Layers
 * 2. MapLibre GL Style Specification (Cream/Gold/Deep-Ink)
 * 3. Provenance Manifest (Academic Citations & Spatial Metadata)
 * 4. Offline Rendering Instructions (Remotion & Headless Pipeline)
 */

import React, { useState } from 'react';
import {
  Download,
  Copy,
  Check,
  FileCode,
  FileText,
  Map,
  Layers,
  Terminal,
  ShieldCheck,
} from 'lucide-react';
import {
  NILE_RIVER_GEOJSON,
  MODERN_CAIRO_NETWORK_GEOJSON,
  UNESCO_HISTORIC_CAIRO_GEOJSON,
  AL_MUIZZ_AXIS_GEOJSON,
  FATIMID_GATES_GEOJSON,
  VERIFIED_NORTHERN_WALL_GEOJSON,
  FATIMID_UNCERTAINTY_BUFFER_GEOJSON,
} from './cairoHistoricalGeoJSON.ts';
import { createRuwaqMapStyle } from './maplibreStyle.ts';

interface GeoExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentFatimidEnclosure: GeoJSON.FeatureCollection;
}

export const GeoExportModal: React.FC<GeoExportModalProps> = ({
  isOpen,
  onClose,
  currentFatimidEnclosure,
}) => {
  const [activeTab, setActiveTab] = useState<'all_geojson' | 'style' | 'manifest' | 'offline_guide'>('all_geojson');
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  if (!isOpen) return null;

  // Build Unified GeoJSON FeatureCollection
  const unifiedGeoJSON: GeoJSON.FeatureCollection = {
    type: 'FeatureCollection',
    features: [
      ...NILE_RIVER_GEOJSON.features,
      ...MODERN_CAIRO_NETWORK_GEOJSON.features,
      ...UNESCO_HISTORIC_CAIRO_GEOJSON.features,
      ...AL_MUIZZ_AXIS_GEOJSON.features,
      ...FATIMID_GATES_GEOJSON.features,
      ...VERIFIED_NORTHERN_WALL_GEOJSON.features,
      ...currentFatimidEnclosure.features,
      ...FATIMID_UNCERTAINTY_BUFFER_GEOJSON.features,
    ],
  };

  // Build MapLibre GL Style JSON
  const mapStyleJson = createRuwaqMapStyle(currentFatimidEnclosure, false);

  // Build Academic Provenance Manifest
  const provenanceManifest = {
    project: 'RUWAQ: Bab Zuwayla Historical Geography Documentary Visualization',
    version: '1.0.0',
    dateGenerated: new Date().toISOString(),
    geodeticDatum: 'WGS-84 (EPSG:4326)',
    focalPoint: {
      name: 'Bab Zuwayla (Bab al-Mutawalli)',
      coordinates: [31.25895, 30.04278],
      elevationMeters: 28.5,
      era: 'Fatimid Gate (1092 CE) & Mamluk Minarets (1415–1421 CE)',
    },
    sources: [
      {
        dataset: 'Modern Cairo Hydrography & Arterial Grid',
        license: 'Open Database License (ODbL) 1.0',
        attribution: 'OpenStreetMap Contributors',
        status: 'VERIFIED_CONTEMPORARY_SURVEY',
      },
      {
        dataset: 'Historic Cairo World Heritage Site Boundary',
        authority: 'UNESCO World Heritage Centre / Ministry of Tourism and Antiquities',
        referenceId: 'UNESCO Ref 89 (Inscribed 1979)',
        status: 'OFFICIAL_LEGAL_BOUNDARY',
      },
      {
        dataset: 'Standing Stone Fortifications & In-Situ Northern Gates',
        citations: [
          'Creswell, K.A.C. (1952). The Muslim Architecture of Egypt, Vol. I (Oxford)',
          'Williams, Caroline (2018). Islamic Monuments in Cairo: The Practical Guide (AUC Press)',
        ],
        status: 'IN_SITU_ARCHAEOLOGICAL_EVIDENCE',
      },
      {
        dataset: 'Al-Mu‘izz li-Din Allah Ceremonial Axis',
        citations: ['Al-Maqrizi (Khitat)', 'Survey of Egypt (1922 Cadastral Maps)'],
        status: 'VERIFIED_CONTEMPORARY_ALIGNMENT_AND_HISTORICAL_RECORD',
      },
      {
        dataset: 'Fatimid Enclosure Perimeter (1092 CE Badr al-Jamali stone circuit)',
        status: 'HYPOTHETICAL_RECONSTRUCTION_APPROXIMATE',
        uncertaintyMarginMeters: 50,
        caution:
          'Ancient mudbrick (969 CE) and stone (1092 CE) circuits survive only intermittently. Southern and western walls are historical hypotheses following historic streets and canals.',
      },
    ],
  };

  // Offline Rendering Guide Markdown
  const offlineInstructionsMd = `# RUWAQ: Offline Rendering & Remotion Production Pipeline

## 1. Zero Live Network Dependencies
The visualizer is designed to render without internet connectivity:
- All GIS geometry (Nile, roads, UNESCO boundary, Al-Mu'izz axis, gates, and walls) is embedded as local GeoJSON.
- The MapLibre GL style (\`ruwaq_maplibre_style.json\`) defines self-contained vector rendering without requiring external tile endpoints.

## 2. Rendering Frames Headlessly via Remotion CLI
To render the 600-frame (20-second at 30fps) sequence offline to high-bitrate ProRes or MP4:

\`\`\`bash
# 1. Install dependencies offline from local npm cache
npm install

# 2. Render Remotion Historical Map Composition
npx remotion render RuwaqHistoricalMap out/ruwaq_historical_geography_4k.mp4 --props='{"enableRasterTiles":false}' --concurrency=4 --gl=angle

# 3. Render High-Resolution Architectural Frame Sequence (PNG)
npx remotion render RuwaqHistoricalMap out/frames/frame_%04d.png --sequence --image-format=png
\`\`\`

## 3. MapLibre Headless Node & Docker Setup
For headless continuous integration on Linux GPU nodes:
- Uses Puppeteer with software WebGL (\`--use-gl=angle\` or \`--use-gl=swiftshader\`).
- Ensure \`XVFB\` is active if running on non-display servers:
  \`xvfb-run -s "-screen 0 3840x2160x24" npx remotion render ...\`
`;

  // Download Trigger
  const triggerDownload = (filename: string, content: string, contentType: string) => {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const copyToClipboard = (key: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2500);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#1C1B19]/80 backdrop-blur-sm">
      <div className="w-full max-w-4xl bg-[#F3EBDB] text-[#1C1B19] border-2 border-[#A98A4B] rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="bg-[#1C1B19] text-[#F3EBDB] p-4 flex items-center justify-between border-b border-[#A98A4B]/40">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-[#A98A4B]/20 text-[#A98A4B]">
              <Download className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-serif-doc text-base font-bold text-[#F3EBDB] tracking-wide flex items-center gap-2">
                RUWAQ PRODUCTION EXPORT & PROVENANCE HUB
                <span className="font-arabic text-[#A98A4B] text-sm">مستودع التصدير والمصادر</span>
              </h2>
              <p className="text-xs text-[#D8CEBC]/70 font-mono-doc">
                Full Working Project Layers, Vector Map Style, Academic Manifest & Offline Guide
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-[#D8CEBC]/70 hover:text-[#F3EBDB] p-1.5 rounded-lg text-sm font-mono-doc"
          >
            ✕ Close
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 px-6 pt-3 border-b border-[#A98A4B]/30 bg-[#E8DCBF]">
          <button
            onClick={() => setActiveTab('all_geojson')}
            className={`px-4 py-2 text-xs font-mono-doc font-bold transition-all border-b-2 flex items-center gap-1.5 ${
              activeTab === 'all_geojson'
                ? 'border-[#8C4729] text-[#8C4729]'
                : 'border-transparent text-[#1C1B19]/70 hover:text-[#1C1B19]'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>1. GeoJSON Layers (All)</span>
          </button>
          <button
            onClick={() => setActiveTab('style')}
            className={`px-4 py-2 text-xs font-mono-doc font-bold transition-all border-b-2 flex items-center gap-1.5 ${
              activeTab === 'style'
                ? 'border-[#8C4729] text-[#8C4729]'
                : 'border-transparent text-[#1C1B19]/70 hover:text-[#1C1B19]'
            }`}
          >
            <Map className="w-3.5 h-3.5" />
            <span>2. Map Style Configuration</span>
          </button>
          <button
            onClick={() => setActiveTab('manifest')}
            className={`px-4 py-2 text-xs font-mono-doc font-bold transition-all border-b-2 flex items-center gap-1.5 ${
              activeTab === 'manifest'
                ? 'border-[#8C4729] text-[#8C4729]'
                : 'border-transparent text-[#1C1B19]/70 hover:text-[#1C1B19]'
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>3. Provenance Manifest</span>
          </button>
          <button
            onClick={() => setActiveTab('offline_guide')}
            className={`px-4 py-2 text-xs font-mono-doc font-bold transition-all border-b-2 flex items-center gap-1.5 ${
              activeTab === 'offline_guide'
                ? 'border-[#8C4729] text-[#8C4729]'
                : 'border-transparent text-[#1C1B19]/70 hover:text-[#1C1B19]'
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>4. Offline Rendering Guide</span>
          </button>
        </div>

        {/* Tab Body */}
        <div className="p-6 overflow-y-auto flex-1 font-mono-doc text-xs scrollbar-thin">
          {activeTab === 'all_geojson' && (
            <div className="flex flex-col gap-3 h-full">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-serif-doc text-sm font-bold text-[#1C1B19]">
                    fatimid_cairo_geography.geojson
                  </h3>
                  <p className="text-[11px] text-[#1C1B19]/70 font-sans">
                    Contains all verified hydrography, UNESCO boundary, Al-Mu'izz axis, gates, and approximate 1092 CE enclosure.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() =>
                      copyToClipboard('geojson', JSON.stringify(unifiedGeoJSON, null, 2))
                    }
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#ECE2CE] border border-[#A98A4B]/40 hover:bg-[#FDF9F0] text-[#1C1B19] transition-all"
                  >
                    {copiedKey === 'geojson' ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedKey === 'geojson' ? 'Copied!' : 'Copy'}</span>
                  </button>
                  <button
                    onClick={() =>
                      triggerDownload(
                        'fatimid_cairo_geography.geojson',
                        JSON.stringify(unifiedGeoJSON, null, 2),
                        'application/geo+json'
                      )
                    }
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#A98A4B] text-[#1C1B19] font-bold hover:bg-[#c4a45e] transition-all shadow-sm"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download GeoJSON</span>
                  </button>
                </div>
              </div>

              <textarea
                readOnly
                value={JSON.stringify(unifiedGeoJSON, null, 2)}
                className="w-full flex-1 min-h-[320px] p-3 rounded-lg bg-[#1C1B19] text-[#A98A4B] font-mono-doc text-[11px] leading-relaxed border border-[#A98A4B]/40 focus:outline-none resize-none"
              />
            </div>
          )}

          {activeTab === 'style' && (
            <div className="flex flex-col gap-3 h-full">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-serif-doc text-sm font-bold text-[#1C1B19]">
                    ruwaq_maplibre_style.json
                  </h3>
                  <p className="text-[11px] text-[#1C1B19]/70 font-sans">
                    Official RUWAQ Cream, Gold, and Deep-Ink MapLibre GL vector styling. Fully offline compliant.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() =>
                      copyToClipboard('style', JSON.stringify(mapStyleJson, null, 2))
                    }
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#ECE2CE] border border-[#A98A4B]/40 hover:bg-[#FDF9F0] text-[#1C1B19] transition-all"
                  >
                    {copiedKey === 'style' ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedKey === 'style' ? 'Copied!' : 'Copy'}</span>
                  </button>
                  <button
                    onClick={() =>
                      triggerDownload(
                        'ruwaq_maplibre_style.json',
                        JSON.stringify(mapStyleJson, null, 2),
                        'application/json'
                      )
                    }
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#A98A4B] text-[#1C1B19] font-bold hover:bg-[#c4a45e] transition-all shadow-sm"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download Style JSON</span>
                  </button>
                </div>
              </div>

              <textarea
                readOnly
                value={JSON.stringify(mapStyleJson, null, 2)}
                className="w-full flex-1 min-h-[320px] p-3 rounded-lg bg-[#1C1B19] text-[#A98A4B] font-mono-doc text-[11px] leading-relaxed border border-[#A98A4B]/40 focus:outline-none resize-none"
              />
            </div>
          )}

          {activeTab === 'manifest' && (
            <div className="flex flex-col gap-3 h-full">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-serif-doc text-sm font-bold text-[#1C1B19]">
                    provenance_manifest.json
                  </h3>
                  <p className="text-[11px] text-[#1C1B19]/70 font-sans">
                    Academic citations, licensing, coordinates datum, and archaeological certainty indexes.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() =>
                      copyToClipboard('manifest', JSON.stringify(provenanceManifest, null, 2))
                    }
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#ECE2CE] border border-[#A98A4B]/40 hover:bg-[#FDF9F0] text-[#1C1B19] transition-all"
                  >
                    {copiedKey === 'manifest' ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedKey === 'manifest' ? 'Copied!' : 'Copy'}</span>
                  </button>
                  <button
                    onClick={() =>
                      triggerDownload(
                        'provenance_manifest.json',
                        JSON.stringify(provenanceManifest, null, 2),
                        'application/json'
                      )
                    }
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#A98A4B] text-[#1C1B19] font-bold hover:bg-[#c4a45e] transition-all shadow-sm"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download Manifest</span>
                  </button>
                </div>
              </div>

              <textarea
                readOnly
                value={JSON.stringify(provenanceManifest, null, 2)}
                className="w-full flex-1 min-h-[320px] p-3 rounded-lg bg-[#1C1B19] text-[#A98A4B] font-mono-doc text-[11px] leading-relaxed border border-[#A98A4B]/40 focus:outline-none resize-none"
              />
            </div>
          )}

          {activeTab === 'offline_guide' && (
            <div className="flex flex-col gap-3 h-full">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-serif-doc text-sm font-bold text-[#1C1B19]">
                    OFFLINE_RENDERING_INSTRUCTIONS.md
                  </h3>
                  <p className="text-[11px] text-[#1C1B19]/70 font-sans">
                    Instructions for headless Remotion frame rendering without internet or live API calls.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => copyToClipboard('offline', offlineInstructionsMd)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#ECE2CE] border border-[#A98A4B]/40 hover:bg-[#FDF9F0] text-[#1C1B19] transition-all"
                  >
                    {copiedKey === 'offline' ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedKey === 'offline' ? 'Copied!' : 'Copy'}</span>
                  </button>
                  <button
                    onClick={() =>
                      triggerDownload(
                        'OFFLINE_RENDERING_INSTRUCTIONS.md',
                        offlineInstructionsMd,
                        'text/markdown'
                      )
                    }
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#A98A4B] text-[#1C1B19] font-bold hover:bg-[#c4a45e] transition-all shadow-sm"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download Markdown</span>
                  </button>
                </div>
              </div>

              <textarea
                readOnly
                value={offlineInstructionsMd}
                className="w-full flex-1 min-h-[320px] p-3 rounded-lg bg-[#1C1B19] text-[#F3EBDB] font-mono-doc text-[11px] leading-relaxed border border-[#A98A4B]/40 focus:outline-none resize-none"
              />
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-[#E8DCBF] p-3 px-6 border-t border-[#A98A4B]/30 flex items-center justify-between text-xs font-mono-doc">
          <span className="text-[#1C1B19]/70">
            Export Package: 4 Deliverables (GeoJSON + Style + Manifest + Offline Guide)
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-[#1C1B19] text-[#F3EBDB] hover:bg-[#A98A4B] hover:text-[#1C1B19] transition-all font-bold"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
