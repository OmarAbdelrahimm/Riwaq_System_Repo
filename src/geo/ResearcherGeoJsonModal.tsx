/**
 * RUWAQ Historical Geography: Researcher GeoJSON Editor & Hypothesis Switcher
 * Addresses the strict academic guideline:
 * "Do not invent polygon coordinates for the ancient walls. If verified historical geometry
 * is unavailable, implement a clearly labeled placeholder and an editable import mechanism
 * for a researcher-approved GeoJSON overlay."
 */

import React, { useState } from 'react';
import {
  FileCode,
  Upload,
  Download,
  RotateCcw,
  CheckCircle,
  AlertTriangle,
  BookOpen,
  Check,
} from 'lucide-react';
import {
  RESEARCHER_HYPOTHESIS_PRESETS,
  DEFAULT_APPROXIMATE_FATIMID_ENCLOSURE_GEOJSON,
} from './cairoHistoricalGeoJSON.ts';

interface ResearcherGeoJsonModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentGeoJson: GeoJSON.FeatureCollection;
  onApplyGeoJson: (data: GeoJSON.FeatureCollection, hypothesisTitle: string) => void;
}

export const ResearcherGeoJsonModal: React.FC<ResearcherGeoJsonModalProps> = ({
  isOpen,
  onClose,
  currentGeoJson,
  onApplyGeoJson,
}) => {
  const [activeTab, setActiveTab] = useState<'presets' | 'editor' | 'guidelines'>('presets');
  const [selectedPresetId, setSelectedPresetId] = useState<string>('creswell_1952');
  const [rawText, setRawText] = useState<string>(() =>
    JSON.stringify(currentGeoJson, null, 2)
  );
  const [validationError, setValidationError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  // Validate and parse raw GeoJSON
  const handleValidateAndApply = () => {
    try {
      const parsed = JSON.parse(rawText);
      if (!parsed || parsed.type !== 'FeatureCollection' || !Array.isArray(parsed.features)) {
        throw new Error('Root must be a GeoJSON FeatureCollection with an array of features.');
      }
      setValidationError(null);
      onApplyGeoJson(parsed, 'Custom Researcher GeoJSON Overlay');
      setSuccessMessage('GeoJSON successfully parsed and applied to map!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      setValidationError(err.message || 'Invalid GeoJSON syntax');
    }
  };

  // Handle file drop / file input
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const content = event.target?.result as string;
        const parsed = JSON.parse(content);
        if (parsed.type === 'FeatureCollection' || parsed.type === 'Feature') {
          const fc = parsed.type === 'FeatureCollection' ? parsed : {
            type: 'FeatureCollection',
            features: [parsed],
          };
          setRawText(JSON.stringify(fc, null, 2));
          setValidationError(null);
          onApplyGeoJson(fc, `Imported: ${file.name}`);
          setSuccessMessage(`Imported ${file.name} successfully!`);
          setTimeout(() => setSuccessMessage(null), 3000);
        } else {
          throw new Error('File must be a GeoJSON Feature or FeatureCollection');
        }
      } catch (err: any) {
        setValidationError(`Import error: ${err.message}`);
      }
    };
    reader.readAsText(file);
  };

  // Apply a scholarly preset
  const handleSelectPreset = (presetId: string) => {
    const preset = RESEARCHER_HYPOTHESIS_PRESETS.find((p) => p.id === presetId);
    if (!preset) return;
    setSelectedPresetId(presetId);
    setRawText(JSON.stringify(preset.geojsonData, null, 2));
    onApplyGeoJson(preset.geojsonData, preset.title);
    setSuccessMessage(`Applied: ${preset.title}`);
    setTimeout(() => setSuccessMessage(null), 3000);
  };

  // Export current GeoJSON as downloadable file
  const handleDownloadGeoJson = () => {
    const blob = new Blob([rawText], { type: 'application/geo+json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `fatimid_cairo_enclosure_researcher_${Date.now()}.geojson`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#1C1B19]/80 backdrop-blur-sm">
      <div className="w-full max-w-4xl bg-[#F3EBDB] text-[#1C1B19] border-2 border-[#A98A4B] rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="bg-[#1C1B19] text-[#F3EBDB] p-4 flex items-center justify-between border-b border-[#A98A4B]/40">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-[#A98A4B]/20 text-[#A98A4B]">
              <FileCode className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-serif-doc text-base font-bold text-[#F3EBDB] tracking-wide flex items-center gap-2">
                RESEARCHER GEOJSON OVERLAY MANAGER
                <span className="font-arabic text-[#A98A4B] text-sm">محرر خرائط الباحثين</span>
              </h2>
              <p className="text-xs text-[#D8CEBC]/70 font-mono-doc">
                Academic Geometry Provenance & Hypothesis Alignment Mechanism
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

        {/* Academic Caution Banner */}
        <div className="bg-[#8C4729]/15 border-b border-[#8C4729]/30 px-6 py-3 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-[#8C4729] shrink-0 mt-0.5" />
          <div className="text-xs leading-relaxed font-sans text-[#1C1B19]">
            <strong className="text-[#8C4729] font-mono-doc uppercase tracking-wider block">
              Cartographic Integrity Principle:
            </strong>
            Ancient wall coordinates must never be arbitrarily fabricated. This interface allows historians and archaeologists to replace approximate reconstructions with verified cadastral, excavation, or archival polygon data.
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 px-6 pt-3 border-b border-[#A98A4B]/30 bg-[#E8DCBF]">
          <button
            onClick={() => setActiveTab('presets')}
            className={`px-4 py-2 text-xs font-mono-doc font-bold transition-all border-b-2 ${
              activeTab === 'presets'
                ? 'border-[#8C4729] text-[#8C4729]'
                : 'border-transparent text-[#1C1B19]/70 hover:text-[#1C1B19]'
            }`}
          >
            Scholarly Hypotheses ({RESEARCHER_HYPOTHESIS_PRESETS.length})
          </button>
          <button
            onClick={() => setActiveTab('editor')}
            className={`px-4 py-2 text-xs font-mono-doc font-bold transition-all border-b-2 ${
              activeTab === 'editor'
                ? 'border-[#8C4729] text-[#8C4729]'
                : 'border-transparent text-[#1C1B19]/70 hover:text-[#1C1B19]'
            }`}
          >
            GeoJSON Code Editor & Import
          </button>
          <button
            onClick={() => setActiveTab('guidelines')}
            className={`px-4 py-2 text-xs font-mono-doc font-bold transition-all border-b-2 ${
              activeTab === 'guidelines'
                ? 'border-[#8C4729] text-[#8C4729]'
                : 'border-transparent text-[#1C1B19]/70 hover:text-[#1C1B19]'
            }`}
          >
            Academic Provenance & Citations
          </button>
        </div>

        {/* Tab Content */}
        <div className="p-6 overflow-y-auto flex-1 font-mono-doc text-xs scrollbar-thin">
          {/* TAB 1: Scholarly Presets */}
          {activeTab === 'presets' && (
            <div className="space-y-4">
              <p className="text-xs font-sans text-[#1C1B19]/80">
                Select from published archaeological reconstructions of the 1092 CE Badr al-Jamali enclosure:
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {RESEARCHER_HYPOTHESIS_PRESETS.map((preset) => {
                  const isSelected = selectedPresetId === preset.id;
                  return (
                    <div
                      key={preset.id}
                      onClick={() => handleSelectPreset(preset.id)}
                      className={`p-4 rounded-xl border-2 transition-all cursor-pointer flex flex-col justify-between ${
                        isSelected
                          ? 'border-[#8C4729] bg-[#FDF9F0] shadow-md ring-2 ring-[#8C4729]/20'
                          : 'border-[#A98A4B]/40 bg-[#ECE2CE] hover:border-[#A98A4B]'
                      }`}
                    >
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-[10px] text-[#A98A4B] font-bold uppercase tracking-wider">
                            {preset.year} CE
                          </span>
                          {isSelected && (
                            <span className="p-1 rounded-full bg-[#8C4729] text-white">
                              <Check className="w-3 h-3" />
                            </span>
                          )}
                        </div>
                        <h3 className="font-serif-doc text-sm font-bold text-[#1C1B19] mb-1">
                          {preset.title}
                        </h3>
                        <p className="text-[11px] font-sans text-[#1C1B19]/70 mb-2">
                          {preset.author} ({preset.institution})
                        </p>
                      </div>

                      <div className="mt-3 pt-2 border-t border-[#A98A4B]/20 text-[10px] flex items-center justify-between text-[#8C4729]">
                        <span>Tolerance: ±{preset.uncertaintyMarginMeters}m</span>
                        <span className="underline font-bold">Select Hypothesis</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TAB 2: GeoJSON Code Editor & File Drop */}
          {activeTab === 'editor' && (
            <div className="flex flex-col gap-3 h-full">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <label className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#1C1B19] text-[#F3EBDB] hover:bg-[#A98A4B] hover:text-[#1C1B19] transition-all cursor-pointer shadow-sm">
                    <Upload className="w-3.5 h-3.5" />
                    <span>Upload .geojson / .json</span>
                    <input
                      type="file"
                      accept=".geojson,.json"
                      onChange={handleFileUpload}
                      className="hidden"
                    />
                  </label>

                  <button
                    onClick={handleDownloadGeoJson}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#ECE2CE] border border-[#A98A4B]/40 hover:bg-[#FDF9F0] text-[#1C1B19] transition-all"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Export GeoJSON</span>
                  </button>

                  <button
                    onClick={() => {
                      setRawText(
                        JSON.stringify(DEFAULT_APPROXIMATE_FATIMID_ENCLOSURE_GEOJSON, null, 2)
                      );
                      setValidationError(null);
                    }}
                    className="flex items-center gap-1 px-2.5 py-1.5 text-xs text-[#8C4729] hover:underline"
                  >
                    <RotateCcw className="w-3 h-3" />
                    <span>Reset Default</span>
                  </button>
                </div>

                <button
                  onClick={handleValidateAndApply}
                  className="px-4 py-2 rounded-lg bg-[#8C4729] text-[#F3EBDB] font-bold hover:bg-[#a35330] transition-all shadow-md flex items-center gap-1.5"
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>Validate & Apply to Map</span>
                </button>
              </div>

              {/* Validation Status Feedback */}
              {validationError && (
                <div className="p-2.5 rounded bg-red-100 text-red-900 border border-red-300 flex items-center gap-2 text-xs">
                  <AlertTriangle className="w-4 h-4 text-red-600 shrink-0" />
                  <span>{validationError}</span>
                </div>
              )}
              {successMessage && (
                <div className="p-2.5 rounded bg-emerald-100 text-emerald-900 border border-emerald-300 flex items-center gap-2 text-xs">
                  <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>{successMessage}</span>
                </div>
              )}

              {/* Code Textarea */}
              <textarea
                value={rawText}
                onChange={(e) => {
                  setRawText(e.target.value);
                  setValidationError(null);
                }}
                className="w-full flex-1 min-h-[300px] p-3 rounded-lg bg-[#1C1B19] text-[#A98A4B] font-mono-doc text-[11px] leading-relaxed border border-[#A98A4B]/40 focus:outline-none focus:ring-2 focus:ring-[#A98A4B] resize-none"
                spellCheck={false}
              />
            </div>
          )}

          {/* TAB 3: Academic Guidelines */}
          {activeTab === 'guidelines' && (
            <div className="space-y-4 font-sans text-xs leading-relaxed text-[#1C1B19]">
              <div className="bg-[#ECE2CE] p-4 rounded-xl border border-[#A98A4B]/40">
                <h4 className="font-serif-doc text-sm font-bold text-[#8C4729] mb-2 flex items-center gap-2">
                  <BookOpen className="w-4 h-4" />
                  Archaeological Basis of Fatimid Cairo Fortifications
                </h4>
                <ul className="list-disc pl-5 space-y-1.5">
                  <li>
                    <strong>Northern Sector:</strong> Bab al-Futuh (1087 CE) and Bab al-Nasr (1087 CE) survive in intact stone masonry with the curtain wall between them along Galal Street.
                  </li>
                  <li>
                    <strong>Southern Sector:</strong> Bab Zuwayla (1092 CE) stands as the only preserved gate on the southern boundary.
                  </li>
                  <li>
                    <strong>Eastern Sector:</strong> Excavations by the Aga Khan Trust for Culture (AKTC) during Al-Azhar Park restoration (1999–2004) uncovered substantial Ayyubid and late Fatimid stone curtain walls and Bab al-Barqiyya.
                  </li>
                  <li>
                    <strong>Western Sector:</strong> The ancient canal <em>Al-Khalij al-Misri</em> served as Cairo's natural western defense line until filled in 1898 to create modern Port Said Street.
                  </li>
                </ul>
              </div>

              <div className="text-[11px] text-[#1C1B19]/70 space-y-1 font-mono-doc">
                <p><strong>Primary Citation:</strong> Creswell, K.A.C. (1952). <em>The Muslim Architecture of Egypt</em>, Volume I: Ikhshids and Fatimids. Oxford: Clarendon Press.</p>
                <p><strong>Legal Boundary:</strong> UNESCO World Heritage Centre (1979). <em>Historic Cairo</em> (Ref 89). Paris: UNESCO.</p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-[#E8DCBF] p-3 px-6 border-t border-[#A98A4B]/30 flex items-center justify-between text-xs font-mono-doc">
          <span className="text-[#1C1B19]/70">
            Current Layer: Approximate Fatimid Cairo Enclosure (1092 CE)
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
