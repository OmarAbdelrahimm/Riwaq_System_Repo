/**
 * Consolidated Collapsible Bottom Control Dock
 * Follows Three.js architectural guidelines: zero viewport occlusion, collapsible, solid/rgba styling
 */

import React, { useState } from 'react';
import {
  ChevronDown,
  ChevronUp,
  Layers,
  Sliders,
  Eye,
  Palette,
  MapPin,
  Film,
  Compass,
} from 'lucide-react';
import {
  ViewerState,
  ComponentVisibility,
  MaterialSettings,
  AnnotationItem,
  RemotionTimelineState,
} from '../types.ts';
import { StateBar } from './StateBar.tsx';
import { TimelineController } from './TimelineController.tsx';
import { BAB_ZUWAYLA_ANNOTATIONS } from '../three/geometry/annotations.ts';

interface ControlDockProps {
  currentState: ViewerState;
  onSelectState: (state: ViewerState) => void;
  cameraMode: 'orthographic' | 'perspective';
  onToggleCameraMode: () => void;
  explodedProgress: number;
  onChangeExplodedProgress: (val: number) => void;
  minaretElevation: number;
  onChangeMinaretElevation: (val: number) => void;
  towerSeparation: number;
  onChangeTowerSeparation: (val: number) => void;
  doorAngleDeg: number;
  onChangeDoorAngle: (val: number) => void;
  visibility: ComponentVisibility;
  onChangeVisibility: (updater: Partial<ComponentVisibility>) => void;
  materialSettings: MaterialSettings;
  onChangeMaterialSettings: (updater: Partial<MaterialSettings>) => void;
  timeline: RemotionTimelineState;
  onUpdateTimeline: (updater: Partial<RemotionTimelineState>) => void;
  onSeekFrame: (frame: number) => void;
  onSelectAnnotation: (item: AnnotationItem) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

type TabType = 'states' | 'editor' | 'deconstruct' | 'components' | 'materials' | 'hotspots' | 'timeline';

export const ControlDock: React.FC<ControlDockProps> = ({
  currentState,
  onSelectState,
  cameraMode,
  onToggleCameraMode,
  explodedProgress,
  onChangeExplodedProgress,
  minaretElevation,
  onChangeMinaretElevation,
  towerSeparation,
  onChangeTowerSeparation,
  doorAngleDeg,
  onChangeDoorAngle,
  visibility,
  onChangeVisibility,
  materialSettings,
  onChangeMaterialSettings,
  timeline,
  onUpdateTimeline,
  onSeekFrame,
  onSelectAnnotation,
  isCollapsed,
  onToggleCollapse,
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('states');

  return (
    <div
      className={`fixed left-1/2 -translate-x-1/2 z-30 w-full max-w-[940px] px-3 sm:px-4 transition-all duration-300 ease-in-out ${
        isCollapsed ? 'bottom-2' : 'bottom-4'
      }`}
    >
      {/* Drawer Toggle Header Button */}
      <div className="flex justify-center mb-1">
        <button
          onClick={onToggleCollapse}
          className="flex items-center gap-1.5 px-4 py-1 rounded-t-lg bg-[#1C1B19]/95 text-[#A98A4B] text-xs font-mono-doc border-t border-x border-[#A98A4B]/40 hover:bg-[#1C1B19] hover:text-[#c4a45e] transition-colors shadow-lg"
        >
          {isCollapsed ? (
            <>
              <ChevronUp className="w-3.5 h-3.5" />
              <span>SHOW DOCK CONTROLS (H)</span>
            </>
          ) : (
            <>
              <ChevronDown className="w-3.5 h-3.5" />
              <span>COLLAPSE DOCK (H)</span>
            </>
          )}
        </button>
      </div>

      {/* Main Dock Container */}
      {!isCollapsed && (
        <div className="w-full bg-[#1C1B19]/95 border border-[#A98A4B]/40 rounded-xl shadow-2xl overflow-hidden flex flex-col text-[#F3EBDB]">
          {/* Dock Navigation Tabs */}
          <div className="flex items-center justify-between border-b border-[#A98A4B]/30 px-3 pt-2 pb-1 bg-[#151413] flex-wrap gap-1">
            <div className="flex items-center gap-1 overflow-x-auto scrollbar-none">
              <button
                onClick={() => setActiveTab('states')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-t text-xs font-medium transition-all ${
                  activeTab === 'states'
                    ? 'bg-[#1C1B19] text-[#A98A4B] border-t-2 border-[#A98A4B]'
                    : 'text-[#F3EBDB]/70 hover:text-[#F3EBDB]'
                }`}
              >
                <Compass className="w-3.5 h-3.5" />
                <span>8 States</span>
              </button>

              <button
                onClick={() => setActiveTab('timeline')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-t text-xs font-medium transition-all ${
                  activeTab === 'timeline'
                    ? 'bg-[#1C1B19] text-[#A98A4B] border-t-2 border-[#A98A4B]'
                    : 'text-[#F3EBDB]/70 hover:text-[#F3EBDB]'
                }`}
              >
                <Film className="w-3.5 h-3.5" />
                <span>Remotion Timeline</span>
              </button>

              <button
                onClick={() => setActiveTab('editor')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-t text-xs font-medium transition-all ${
                  activeTab === 'editor'
                    ? 'bg-[#1C1B19] text-[#A98A4B] border-t-2 border-[#A98A4B]'
                    : 'text-[#F3EBDB]/70 hover:text-[#F3EBDB]'
                }`}
              >
                <Sliders className="w-3.5 h-3.5" />
                <span>Component Editor</span>
              </button>

              <button
                onClick={() => setActiveTab('deconstruct')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-t text-xs font-medium transition-all ${
                  activeTab === 'deconstruct'
                    ? 'bg-[#1C1B19] text-[#A98A4B] border-t-2 border-[#A98A4B]'
                    : 'text-[#F3EBDB]/70 hover:text-[#F3EBDB]'
                }`}
              >
                <Layers className="w-3.5 h-3.5" />
                <span>Exploded View</span>
              </button>

              <button
                onClick={() => setActiveTab('components')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-t text-xs font-medium transition-all ${
                  activeTab === 'components'
                    ? 'bg-[#1C1B19] text-[#A98A4B] border-t-2 border-[#A98A4B]'
                    : 'text-[#F3EBDB]/70 hover:text-[#F3EBDB]'
                }`}
              >
                <Eye className="w-3.5 h-3.5" />
                <span>Components</span>
              </button>

              <button
                onClick={() => setActiveTab('materials')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-t text-xs font-medium transition-all ${
                  activeTab === 'materials'
                    ? 'bg-[#1C1B19] text-[#A98A4B] border-t-2 border-[#A98A4B]'
                    : 'text-[#F3EBDB]/70 hover:text-[#F3EBDB]'
                }`}
              >
                <Palette className="w-3.5 h-3.5" />
                <span>Materials & Drafting</span>
              </button>

              <button
                onClick={() => setActiveTab('hotspots')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-t text-xs font-medium transition-all ${
                  activeTab === 'hotspots'
                    ? 'bg-[#1C1B19] text-[#A98A4B] border-t-2 border-[#A98A4B]'
                    : 'text-[#F3EBDB]/70 hover:text-[#F3EBDB]'
                }`}
              >
                <MapPin className="w-3.5 h-3.5" />
                <span>Historical Hotspots</span>
              </button>
            </div>

            {/* Quick Camera Mode Switch */}
            <div className="flex items-center gap-2 text-xs font-mono-doc py-1">
              <span className="text-[#A98A4B] text-[11px]">CAM:</span>
              <button
                onClick={onToggleCameraMode}
                className="px-2 py-0.5 rounded bg-[#A98A4B]/20 text-[#A98A4B] hover:bg-[#A98A4B]/30 transition-colors uppercase text-[11px] font-bold"
              >
                {cameraMode}
              </button>
            </div>
          </div>

          {/* Active Tab Panel */}
          <div className="p-3 max-h-[220px] overflow-y-auto scrollbar-thin">
            {/* TAB 1: 8 ARCHITECTURAL STATES */}
            {activeTab === 'states' && (
              <div className="flex flex-col gap-2">
                <div className="flex items-center justify-between text-xs text-[#F3EBDB]/80 font-mono-doc">
                  <span>DOCUMENTARY REQUIRED STATES (DERIVED FROM ONE GEOMETRY MODEL):</span>
                  <span className="text-[#A98A4B]">STATE: {currentState}</span>
                </div>
                <StateBar currentState={currentState} onSelectState={onSelectState} />
              </div>
            )}

            {/* TAB: COMPONENT EDITOR */}
            {activeTab === 'editor' && (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono-doc">
                {/* Bastion Lateral Offset */}
                <div className="flex flex-col gap-1.5 bg-[#151413] p-2.5 rounded-lg border border-[#A98A4B]/20">
                  <div className="flex justify-between items-center">
                    <span className="text-[#A98A4B]">Towers Lateral (X):</span>
                    <span>{(towerSeparation * 6).toFixed(1)} m</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={towerSeparation}
                    onChange={(e) => onChangeTowerSeparation(parseFloat(e.target.value))}
                    className="accent-[#A98A4B] cursor-pointer"
                  />
                  <span className="text-[10px] text-[#F3EBDB]/50">
                    Left/Right 1092 bastions lateral spread
                  </span>
                </div>

                {/* Central Arch Forward Z */}
                <div className="flex flex-col gap-1.5 bg-[#151413] p-2.5 rounded-lg border border-[#A98A4B]/20">
                  <div className="flex justify-between items-center">
                    <span className="text-[#A98A4B]">Arch & Vault (Z):</span>
                    <span>{(explodedProgress * 3.5).toFixed(1)} m</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={explodedProgress}
                    onChange={(e) => onChangeExplodedProgress(parseFloat(e.target.value))}
                    className="accent-[#A98A4B] cursor-pointer"
                  />
                  <span className="text-[10px] text-[#F3EBDB]/50">
                    Central portal & cushion voussoir translation
                  </span>
                </div>

                {/* Minaret Vertical Lift */}
                <div className="flex flex-col gap-1.5 bg-[#151413] p-2.5 rounded-lg border border-[#A98A4B]/20">
                  <div className="flex justify-between items-center">
                    <span className="text-[#A98A4B]">Minarets Height (Y):</span>
                    <span>{(minaretElevation * 14).toFixed(1)} m</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={minaretElevation}
                    onChange={(e) => onChangeMinaretElevation(parseFloat(e.target.value))}
                    className="accent-[#A98A4B] cursor-pointer"
                  />
                  <span className="text-[10px] text-[#F3EBDB]/50">
                    1421 Mamluk additions vertical offset
                  </span>
                </div>

                {/* Door Leaves Rotation */}
                <div className="flex flex-col gap-1.5 bg-[#151413] p-2.5 rounded-lg border border-[#A98A4B]/20">
                  <div className="flex justify-between items-center">
                    <span className="text-[#A98A4B]">Door Leaves Angle:</span>
                    <span>{Math.round(doorAngleDeg)}°</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="90"
                    step="1"
                    value={doorAngleDeg}
                    onChange={(e) => onChangeDoorAngle(parseInt(e.target.value, 10))}
                    className="accent-[#A98A4B] cursor-pointer"
                  />
                  <span className="text-[10px] text-[#F3EBDB]/50">
                    Hinged cedar & studded iron leaf pivot
                  </span>
                </div>
              </div>
            )}

            {/* TAB 2: REMOTION TIMELINE */}
            {activeTab === 'timeline' && (
              <TimelineController
                timeline={timeline}
                onUpdateTimeline={onUpdateTimeline}
                onSeekFrame={onSeekFrame}
              />
            )}

            {/* TAB 3: DECONSTRUCTION / EXPLODED VIEW */}
            {activeTab === 'deconstruct' && (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono-doc">
                {/* Exploded Progress */}
                <div className="flex flex-col gap-1.5 bg-[#151413] p-2.5 rounded-lg border border-[#A98A4B]/20">
                  <div className="flex justify-between items-center">
                    <span className="text-[#A98A4B]">Overall Explosion:</span>
                    <span>{Math.round(explodedProgress * 100)}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={explodedProgress}
                    onChange={(e) => onChangeExplodedProgress(parseFloat(e.target.value))}
                    className="accent-[#A98A4B] cursor-pointer"
                  />
                  <span className="text-[10px] text-[#F3EBDB]/50">
                    Separates towers, minarets, and portals
                  </span>
                </div>

                {/* Minaret Vertical Elevation */}
                <div className="flex flex-col gap-1.5 bg-[#151413] p-2.5 rounded-lg border border-[#A98A4B]/20">
                  <div className="flex justify-between items-center">
                    <span className="text-[#A98A4B]">Minaret Lift (Y):</span>
                    <span>{(minaretElevation * 12).toFixed(1)} m</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={minaretElevation}
                    onChange={(e) => onChangeMinaretElevation(parseFloat(e.target.value))}
                    className="accent-[#A98A4B] cursor-pointer"
                  />
                  <span className="text-[10px] text-[#F3EBDB]/50">
                    Raises Mamluk minarets above towers
                  </span>
                </div>

                {/* Lateral Bastion Separation */}
                <div className="flex flex-col gap-1.5 bg-[#151413] p-2.5 rounded-lg border border-[#A98A4B]/20">
                  <div className="flex justify-between items-center">
                    <span className="text-[#A98A4B]">Tower Spread (X):</span>
                    <span>{(towerSeparation * 6).toFixed(1)} m</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={towerSeparation}
                    onChange={(e) => onChangeTowerSeparation(parseFloat(e.target.value))}
                    className="accent-[#A98A4B] cursor-pointer"
                  />
                  <span className="text-[10px] text-[#F3EBDB]/50">
                    Shifts semicircular bastions laterally
                  </span>
                </div>

                {/* Fortified Door Opening Angle */}
                <div className="flex flex-col gap-1.5 bg-[#151413] p-2.5 rounded-lg border border-[#A98A4B]/20">
                  <div className="flex justify-between items-center">
                    <span className="text-[#A98A4B]">Door Pivot:</span>
                    <span>{Math.round(doorAngleDeg)}°</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="90"
                    step="1"
                    value={doorAngleDeg}
                    onChange={(e) => onChangeDoorAngle(parseInt(e.target.value, 10))}
                    className="accent-[#A98A4B] cursor-pointer"
                  />
                  <span className="text-[10px] text-[#F3EBDB]/50">
                    Rotates iron-clad timber door leaves
                  </span>
                </div>
              </div>
            )}

            {/* TAB 4: COMPONENT VISIBILITY */}
            {activeTab === 'components' && (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2 text-xs font-mono-doc">
                {[
                  { key: 'leftTower', label: 'West Bastion (Left)' },
                  { key: 'rightTower', label: 'East Bastion (Right)' },
                  { key: 'centralArch', label: 'Entrance Portal' },
                  { key: 'leftDoor', label: 'Left Iron Door' },
                  { key: 'rightDoor', label: 'Right Iron Door' },
                  { key: 'leftMinaret', label: 'West Minaret (1421)' },
                  { key: 'rightMinaret', label: 'East Minaret (1421)' },
                  { key: 'crenellations', label: 'Stepped Crenellations' },
                  { key: 'ground', label: 'Cairo Ground Apron' },
                ].map(({ key, label }) => {
                  const isChecked = visibility[key as keyof ComponentVisibility];
                  return (
                    <label
                      key={key}
                      className={`flex items-center gap-2 p-2 rounded border cursor-pointer transition-colors ${
                        isChecked
                          ? 'bg-[#151413] border-[#A98A4B]/40 text-[#F3EBDB]'
                          : 'bg-[#151413]/40 border-white/10 text-[#F3EBDB]/40'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={(e) =>
                          onChangeVisibility({ [key]: e.target.checked })
                        }
                        className="accent-[#A98A4B] w-3.5 h-3.5"
                      />
                      <span className="truncate">{label}</span>
                    </label>
                  );
                })}
              </div>
            )}

            {/* TAB 5: MATERIALS & DRAFTING */}
            {activeTab === 'materials' && (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono-doc">
                {/* Stone Roughness */}
                <div className="flex flex-col gap-1.5 bg-[#151413] p-2.5 rounded-lg border border-[#A98A4B]/20">
                  <div className="flex justify-between items-center">
                    <span className="text-[#A98A4B]">Stone Roughness:</span>
                    <span>{materialSettings.stoneRoughness.toFixed(2)}</span>
                  </div>
                  <input
                    type="range"
                    min="0.2"
                    max="1.0"
                    step="0.05"
                    value={materialSettings.stoneRoughness}
                    onChange={(e) =>
                      onChangeMaterialSettings({ stoneRoughness: parseFloat(e.target.value) })
                    }
                    className="accent-[#A98A4B] cursor-pointer"
                  />
                  <span className="text-[10px] text-[#F3EBDB]/50">
                    Mokattam limestone surface micro-roughness
                  </span>
                </div>

                {/* Stone Warmth */}
                <div className="flex flex-col gap-1.5 bg-[#151413] p-2.5 rounded-lg border border-[#A98A4B]/20">
                  <div className="flex justify-between items-center">
                    <span className="text-[#A98A4B]">Limestone Patina Warmth:</span>
                    <span>{Math.round(materialSettings.stoneWarmth * 100)}%</span>
                  </div>
                  <input
                    type="range"
                    min="0.0"
                    max="1.0"
                    step="0.05"
                    value={materialSettings.stoneWarmth}
                    onChange={(e) =>
                      onChangeMaterialSettings({ stoneWarmth: parseFloat(e.target.value) })
                    }
                    className="accent-[#A98A4B] cursor-pointer"
                  />
                  <span className="text-[10px] text-[#F3EBDB]/50">
                    Aged desert sand & sun oxidation
                  </span>
                </div>

                {/* Wireframe Mode */}
                <div className="flex flex-col justify-between bg-[#151413] p-2.5 rounded-lg border border-[#A98A4B]/20">
                  <span className="text-[#A98A4B]">Geometry Wireframe:</span>
                  <button
                    onClick={() =>
                      onChangeMaterialSettings({ wireframe: !materialSettings.wireframe })
                    }
                    className={`mt-2 py-1.5 px-3 rounded text-center transition-colors font-bold ${
                      materialSettings.wireframe
                        ? 'bg-[#A98A4B] text-[#1C1B19]'
                        : 'bg-[#2D2A26] text-[#F3EBDB]/80 hover:text-white'
                    }`}
                  >
                    {materialSettings.wireframe ? 'WIREFRAME ON' : 'WIREFRAME OFF'}
                  </button>
                  <span className="text-[10px] text-[#F3EBDB]/50 mt-1">
                    Reveals polygonal subdivision
                  </span>
                </div>

                {/* Blueprint Ink Mode */}
                <div className="flex flex-col justify-between bg-[#151413] p-2.5 rounded-lg border border-[#A98A4B]/20">
                  <span className="text-[#A98A4B]">Blueprint Sketch Mode:</span>
                  <button
                    onClick={() =>
                      onChangeMaterialSettings({ blueprintMode: !materialSettings.blueprintMode })
                    }
                    className={`mt-2 py-1.5 px-3 rounded text-center transition-colors font-bold ${
                      materialSettings.blueprintMode
                        ? 'bg-[#A98A4B] text-[#1C1B19]'
                        : 'bg-[#2D2A26] text-[#F3EBDB]/80 hover:text-white'
                    }`}
                  >
                    {materialSettings.blueprintMode ? 'BLUEPRINT ON' : 'PBR REALISTIC'}
                  </button>
                  <span className="text-[10px] text-[#F3EBDB]/50 mt-1">
                    Editorial architectural drafting plate
                  </span>
                </div>
              </div>
            )}

            {/* TAB 6: HISTORICAL HOTSPOTS */}
            {activeTab === 'hotspots' && (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2 text-xs font-mono-doc">
                {BAB_ZUWAYLA_ANNOTATIONS.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => onSelectAnnotation(item)}
                    className="flex flex-col items-start p-2 rounded bg-[#151413] border border-[#A98A4B]/20 hover:border-[#A98A4B] hover:bg-[#A98A4B]/10 transition-all text-left"
                  >
                    <div className="flex items-center justify-between w-full">
                      <span className="text-[10px] text-[#A98A4B] font-bold">
                        {item.date}
                      </span>
                      <span className="text-[9px] uppercase px-1 rounded bg-[#A98A4B]/20 text-[#A98A4B]">
                        {item.category}
                      </span>
                    </div>
                    <span className="font-semibold text-[#F3EBDB] mt-0.5 leading-tight">
                      {item.titleEn}
                    </span>
                    <span className="font-arabic text-[#A98A4B] text-[10px]">
                      {item.titleAr}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
