/**
 * RUWAQ: Bab Zuwayla Historical Geography & 3D Architectural Reconstruction
 * Main Application Component
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { BabZuwaylaScene } from './three/BabZuwaylaScene.ts';
import {
  ViewerState,
  ComponentVisibility,
  MaterialSettings,
  AnnotationItem,
  RemotionTimelineState,
} from './types.ts';

import { Header } from './components/Header.tsx';
import { ControlDock } from './components/ControlDock.tsx';
import { ViewportDraftingOverlay } from './components/ViewportDraftingOverlay.tsx';
import { ComponentInfoModal } from './components/ComponentInfoModal.tsx';
import { RemotionModal } from './components/RemotionModal.tsx';
import { AssetManifestModal } from './components/AssetManifestModal.tsx';
import { ProductionHandoffModal } from './components/ProductionHandoffModal.tsx';

// Historical Geography & MapLibre GL Components
import { RuwaqMaplibreView } from './geo/RuwaqMaplibreView.tsx';
import { HistoricalStoryTimeline } from './geo/HistoricalStoryTimeline.tsx';
import { GeoLayerToggles } from './geo/GeoLayerToggles.tsx';
import { ResearcherGeoJsonModal } from './geo/ResearcherGeoJsonModal.tsx';
import { GeoExportModal } from './geo/GeoExportModal.tsx';
import { FeatureInspectorModal } from './geo/FeatureInspectorModal.tsx';
import {
  DEFAULT_APPROXIMATE_FATIMID_ENCLOSURE_GEOJSON,
  FEATURE_METADATA_DIRECTORY,
} from './geo/cairoHistoricalGeoJSON.ts';
import { LayerVisibilityState, GeoFeatureMetadata, StoryActId } from './geo/types.ts';
import { STORY_ACTS } from './geo/storyChoreography.ts';

export default function App() {
  const canvasMountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<BabZuwaylaScene | null>(null);

  // Active View: 'map' (Historical Geography) | '3d' (Bab Zuwayla Model) | 'split' (Synchronized)
  const [activeView, setActiveView] = useState<'map' | '3d' | 'split'>('map');

  // Application States (3D Architecture)
  const [currentState, setCurrentState] = useState<ViewerState>('FULLY_ASSEMBLED');
  const [cameraMode, setCameraMode] = useState<'perspective' | 'orthographic'>('perspective');
  const [explodedProgress, setExplodedProgress] = useState<number>(0);
  const [minaretElevation, setMinaretElevation] = useState<number>(0);
  const [towerSeparation, setTowerSeparation] = useState<number>(0);
  const [doorAngleDeg, setDoorAngleDeg] = useState<number>(35);

  const [visibility, setVisibility] = useState<ComponentVisibility>({
    leftTower: true,
    rightTower: true,
    centralArch: true,
    gatePassage: true,
    leftDoor: true,
    rightDoor: true,
    leftMinaret: true,
    rightMinaret: true,
    crenellations: true,
    ground: true,
  });

  const [materialSettings, setMaterialSettings] = useState<MaterialSettings>({
    stoneRoughness: 0.82,
    stoneWarmth: 0.55,
    wireframe: false,
    blueprintMode: false,
    shadowIntensity: 0.45,
    aoIntensity: 1.0,
  });

  const [timeline, setTimeline] = useState<RemotionTimelineState>({
    frame: 285,
    totalFrames: 300,
    fps: 30,
    isPlaying: false,
    loop: true,
    speed: 1.0,
  });

  // Historical Geography (MapLibre GL & Deterministic Story) States
  const [mapFrame, setMapFrame] = useState<number>(0);
  const totalMapFrames = 600; // 20 seconds at 30 fps across 7 acts
  const [isMapPlaying, setIsMapPlaying] = useState<boolean>(false);
  const [mapPlaybackSpeed, setMapPlaybackSpeed] = useState<number>(1.0);
  const [isInteractiveMap, setIsInteractiveMap] = useState<boolean>(false);

  const [geoLayerVisibility, setGeoLayerVisibility] = useState<LayerVisibilityState>({
    modernStreets: true,
    nileWater: true,
    historicCairoUnesco: true,
    fatimidApproximateExtent: true,
    uncertaintyBuffer: true,
    alMuizzAxis: true,
    northernGates: true,
    babZuwaylaSouthernAnchor: true,
    secondaryGateTraces: true,
    historicKhalijCanal: true,
    threeDOverlay: true,
    topographicContours: false,
  });

  const [fatimidEnclosureData, setFatimidEnclosureData] = useState<GeoJSON.FeatureCollection>(
    DEFAULT_APPROXIMATE_FATIMID_ENCLOSURE_GEOJSON
  );
  const [selectedGeoFeature, setSelectedGeoFeature] = useState<GeoFeatureMetadata | null>(null);
  const [showResearcherModal, setShowResearcherModal] = useState<boolean>(false);
  const [showGeoExportModal, setShowGeoExportModal] = useState<boolean>(false);
  const [showLayerPanel, setShowLayerPanel] = useState<boolean>(false);

  // UI Modals & Inspection
  const [selectedComponent, setSelectedComponent] = useState<{
    id: string;
    nameEn: string;
    nameAr: string;
    descriptionEn?: string;
    descriptionAr?: string;
    era?: string;
    certainty?: string;
  } | null>(null);

  const [selectedAnnotation, setSelectedAnnotation] = useState<AnnotationItem | null>(null);
  const [isCollapsed, setIsCollapsed] = useState<boolean>(false);
  const [cinemaMode, setCinemaMode] = useState<boolean>(false);
  const [showRemotionModal, setShowRemotionModal] = useState<boolean>(false);
  const [showManifestModal, setShowManifestModal] = useState<boolean>(false);
  const [showHandoffModal, setShowHandoffModal] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3200);
  };

  // 1. Initialize Scene Lifecycle inside isolated ref container
  useEffect(() => {
    if (!canvasMountRef.current) return;

    const scene = new BabZuwaylaScene(canvasMountRef.current, {
      onSelectComponent: (comp) => {
        setSelectedComponent(comp);
        setSelectedAnnotation(null);
      },
      onSelectAnnotation: (annot) => {
        setSelectedAnnotation(annot);
        setSelectedComponent(null);
      },
    });

    sceneRef.current = scene;

    return () => {
      scene.dispose();
      sceneRef.current = null;
    };
  }, []);

  // 2. Map Deterministic Playback Animation Loop
  useEffect(() => {
    if (!isMapPlaying || isInteractiveMap) return;

    const intervalMs = 1000 / (30 * mapPlaybackSpeed);
    const interval = setInterval(() => {
      setMapFrame((prev) => {
        if (prev >= totalMapFrames) {
          return 0; // loop
        }
        return prev + 1;
      });
    }, intervalMs);

    return () => clearInterval(interval);
  }, [isMapPlaying, isInteractiveMap, mapPlaybackSpeed, totalMapFrames]);

  // Synchronize 3D scene when map frame enters Act 7 (3D plunge)
  useEffect(() => {
    if (mapFrame >= 481 && sceneRef.current) {
      const progressInAct7 = (mapFrame - 481) / (totalMapFrames - 481);
      const frame3D = Math.min(300, Math.floor(progressInAct7 * 300));
      sceneRef.current.seekFrame(frame3D, 300);
    }
  }, [mapFrame, totalMapFrames]);

  // 3. Select Architectural State
  const handleSelectState = useCallback((state: ViewerState) => {
    setCurrentState(state);
    if (!sceneRef.current) return;

    sceneRef.current.setState(state);
    setCameraMode(sceneRef.current.activeCamera === sceneRef.current.orthographicCamera ? 'orthographic' : 'perspective');

    if (state === 'FATIMID_ORIGINAL') {
      setVisibility((prev) => ({ ...prev, leftMinaret: false, rightMinaret: false }));
      setExplodedProgress(0);
    } else if (state === 'EXPLODED_VIEW') {
      setExplodedProgress(0.75);
      setDoorAngleDeg(70);
    } else {
      setVisibility((prev) => ({ ...prev, leftMinaret: true, rightMinaret: true }));
      setExplodedProgress(0);
    }
  }, []);

  // 4. Toggle Camera Mode
  const handleToggleCameraMode = () => {
    if (!sceneRef.current) return;
    const nextMode = cameraMode === 'perspective' ? 'orthographic' : 'perspective';
    sceneRef.current.switchCameraMode(nextMode);
    setCameraMode(nextMode);
  };

  // 5. Update Exploded Progress
  const handleExplodedProgress = (val: number) => {
    setExplodedProgress(val);
    if (sceneRef.current) {
      sceneRef.current.setExplodedProgress(val);
    }
  };

  const handleMinaretElevation = (val: number) => {
    setMinaretElevation(val);
    if (sceneRef.current) {
      sceneRef.current.setMinaretElevation(val);
    }
  };

  const handleTowerSeparation = (val: number) => {
    setTowerSeparation(val);
    if (sceneRef.current) {
      sceneRef.current.setTowerSeparation(val);
    }
  };

  const handleDoorAngle = (val: number) => {
    setDoorAngleDeg(val);
    if (sceneRef.current) {
      sceneRef.current.setDoorAngle(val);
    }
  };

  // 6. Component Visibility Update
  const handleVisibility = (updater: Partial<ComponentVisibility>) => {
    const updated = { ...visibility, ...updater };
    setVisibility(updated);
    if (sceneRef.current) {
      sceneRef.current.setComponentVisibility(updated);
    }
  };

  // 7. Material Settings Update
  const handleMaterialSettings = (updater: Partial<MaterialSettings>) => {
    const updated = { ...materialSettings, ...updater };
    setMaterialSettings(updated);
    if (sceneRef.current) {
      sceneRef.current.setMaterialSettings(updated);
    }
  };

  // 8. Timeline / Remotion Seek for 3D Viewer
  const handleSeekFrame = useCallback((frame: number) => {
    setTimeline((prev) => ({ ...prev, frame }));
    if (sceneRef.current) {
      sceneRef.current.seekFrame(frame, timeline.totalFrames);
      setCurrentState(sceneRef.current.currentState);
      setCameraMode(
        sceneRef.current.activeCamera === sceneRef.current.orthographicCamera
          ? 'orthographic'
          : 'perspective'
      );
      setExplodedProgress(sceneRef.current.explodedProgress);
    }
  }, [timeline.totalFrames]);

  // 9. Jump to Story Act
  const handleJumpToAct = (actId: StoryActId) => {
    const targetAct = STORY_ACTS.find((a) => a.id === actId);
    if (targetAct) {
      setMapFrame(targetAct.startFrame);
      showToast(`Jumped to Act ${targetAct.actNumber}: ${targetAct.titleEn}`);
    }
  };

  // 10. Reset Scene and Map
  const handleReset = () => {
    setMapFrame(0);
    setIsMapPlaying(false);
    setIsInteractiveMap(false);
    handleSelectState('FULLY_ASSEMBLED');
    setExplodedProgress(0);
    setMinaretElevation(0);
    setTowerSeparation(0);
    setDoorAngleDeg(35);
    setTimeline((prev) => ({ ...prev, frame: 285, isPlaying: false }));
    showToast('Reset documentary view to Act 1: Modern Cairo');
  };

  // 11. GLB Export
  const handleExportGLB = () => {
    if (!sceneRef.current) return;
    showToast('Exporting GLB with preserved named hierarchy...');
    sceneRef.current.exportGLB();
  };

  // 12. High-Res Snapshot
  const handleSnapshot = () => {
    if (activeView === '3d' && sceneRef.current) {
      const dataUrl = sceneRef.current.captureSnapshot();
      const link = document.createElement('a');
      link.href = dataUrl;
      link.download = `RUWAQ_Bab_Zuwayla_${currentState}_${Date.now()}.png`;
      link.click();
      showToast(`Captured high-res 3D plate: ${currentState}`);
    } else {
      // Map screenshot
      showToast('Capturing documentary cartographic plate...');
      const mapCanvas = document.querySelector('.maplibregl-canvas') as HTMLCanvasElement;
      if (mapCanvas) {
        const link = document.createElement('a');
        link.href = mapCanvas.toDataURL('image/png');
        link.download = `RUWAQ_Cairo_Historical_Map_Frame_${mapFrame}_${Date.now()}.png`;
        link.click();
      }
    }
  };

  // 13. Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      if (e.key === ' ' || e.code === 'Space') {
        e.preventDefault();
        if (activeView === 'map') {
          setIsMapPlaying((prev) => !prev);
        } else {
          setTimeline((prev) => ({ ...prev, isPlaying: !prev.isPlaying }));
        }
      } else if (e.key === 'm' || e.key === 'M') {
        setActiveView('map');
      } else if (e.key === 'b' || e.key === 'B') {
        setActiveView('3d');
      } else if (e.key === 's' || e.key === 'S') {
        setActiveView('split');
      } else if (e.key === 'h' || e.key === 'H') {
        setCinemaMode((prev) => !prev);
      } else if (e.key === 'Escape') {
        setSelectedComponent(null);
        setSelectedAnnotation(null);
        setSelectedGeoFeature(null);
        setShowRemotionModal(false);
        setShowManifestModal(false);
        setShowResearcherModal(false);
        setShowGeoExportModal(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeView]);

  return (
    <main className="relative w-screen h-screen overflow-hidden bg-[#F3EBDB] select-none">
      {/* VIEW LAYER 1: 3D Architectural Scene Container */}
      <div
        ref={canvasMountRef}
        className={`w-full h-full absolute inset-0 z-0 cursor-grab active:cursor-grabbing transition-all duration-500 ${
          activeView === '3d'
            ? 'opacity-100 pointer-events-auto'
            : activeView === 'split'
            ? 'left-1/2 w-1/2 opacity-100 pointer-events-auto border-l-2 border-[#A98A4B]'
            : 'opacity-0 pointer-events-none'
        }`}
      />

      {/* VIEW LAYER 2: MapLibre GL Historical Geography Map */}
      <div
        className={`w-full h-full absolute inset-0 z-10 transition-all duration-500 ${
          activeView === 'map'
            ? 'opacity-100 pointer-events-auto'
            : activeView === 'split'
            ? 'right-1/2 w-1/2 opacity-100 pointer-events-auto border-r-2 border-[#A98A4B]'
            : 'opacity-0 pointer-events-none'
        }`}
      >
        <RuwaqMaplibreView
          frame={mapFrame}
          totalFrames={totalMapFrames}
          isInteractiveMode={isInteractiveMap}
          layerVisibility={geoLayerVisibility}
          fatimidEnclosureData={fatimidEnclosureData}
          onSelectFeature={(feat) => setSelectedGeoFeature(feat)}
          onOpenResearcherModal={() => setShowResearcherModal(true)}
        />
      </div>

      {/* VIEWPORT DRAFTING OVERLAY (In 3D View) */}
      {!cinemaMode && activeView === '3d' && (
        <ViewportDraftingOverlay
          currentState={currentState}
          cameraMode={cameraMode}
        />
      )}

      {/* HEADER BAR (Visible in all views) */}
      {!cinemaMode && (
        <Header
          currentState={currentState}
          activeView={activeView}
          onChangeView={(v) => {
            setActiveView(v);
            showToast(`Switched view to ${v.toUpperCase()}`);
          }}
          onReset={handleReset}
          onExportGLB={handleExportGLB}
          onSnapshot={handleSnapshot}
          onOpenRemotion={() => setShowRemotionModal(true)}
          onOpenManifest={() => setShowManifestModal(true)}
          onOpenHandoff={() => setShowHandoffModal(true)}
          onOpenGeoExport={() => setShowGeoExportModal(true)}
          onOpenResearcherGeoJson={() => setShowResearcherModal(true)}
          cinemaMode={cinemaMode}
          onToggleCinemaMode={() => setCinemaMode(!cinemaMode)}
        />
      )}

      {/* FLOATING LAYER & PROVENANCE INSPECTOR (When in Map or Split View) */}
      {!cinemaMode && (activeView === 'map' || activeView === 'split') && (
        <GeoLayerToggles
          visibility={geoLayerVisibility}
          onChangeVisibility={(updater) =>
            setGeoLayerVisibility((prev) => ({ ...prev, ...updater }))
          }
          isOpen={showLayerPanel}
          onToggleOpen={() => setShowLayerPanel((prev) => !prev)}
          onOpenResearcherModal={() => setShowResearcherModal(true)}
        />
      )}

      {/* HISTORICAL STORY TIMELINE CONTROLLER (When in Map View) */}
      {!cinemaMode && activeView === 'map' && (
        <HistoricalStoryTimeline
          frame={mapFrame}
          totalFrames={totalMapFrames}
          isPlaying={isMapPlaying}
          playbackSpeed={mapPlaybackSpeed}
          isInteractiveMode={isInteractiveMap}
          onSeekFrame={(f) => setMapFrame(f)}
          onTogglePlay={() => setIsMapPlaying((prev) => !prev)}
          onChangeSpeed={(spd) => setMapPlaybackSpeed(spd)}
          onToggleInteractiveMode={() => {
            setIsInteractiveMap((prev) => {
              const next = !prev;
              showToast(next ? 'Free GIS Explorer enabled' : 'Remotion Story Mode enabled');
              return next;
            });
          }}
          onJumpToAct={handleJumpToAct}
        />
      )}

      {/* 3D ARCHITECTURAL CONTROL DOCK (When in 3D View) */}
      {!cinemaMode && activeView === '3d' && (
        <ControlDock
          currentState={currentState}
          onSelectState={handleSelectState}
          cameraMode={cameraMode}
          onToggleCameraMode={handleToggleCameraMode}
          explodedProgress={explodedProgress}
          onChangeExplodedProgress={handleExplodedProgress}
          minaretElevation={minaretElevation}
          onChangeMinaretElevation={handleMinaretElevation}
          towerSeparation={towerSeparation}
          onChangeTowerSeparation={handleTowerSeparation}
          doorAngleDeg={doorAngleDeg}
          onChangeDoorAngle={handleDoorAngle}
          visibility={visibility}
          onChangeVisibility={handleVisibility}
          materialSettings={materialSettings}
          onChangeMaterialSettings={handleMaterialSettings}
          timeline={timeline}
          onUpdateTimeline={(updater) => setTimeline((prev) => ({ ...prev, ...updater }))}
          onSeekFrame={handleSeekFrame}
          onSelectAnnotation={(annot) => {
            setSelectedAnnotation(annot);
            setSelectedComponent(null);
          }}
          isCollapsed={isCollapsed}
          onToggleCollapse={() => setIsCollapsed(!isCollapsed)}
        />
      )}

      {/* CINEMA RESTORE BUTTON */}
      {cinemaMode && (
        <button
          onClick={() => setCinemaMode(false)}
          className="absolute top-4 right-4 z-50 px-3 py-1.5 rounded-lg bg-[#1C1B19]/90 text-[#A98A4B] text-xs font-mono-doc border border-[#A98A4B]/50 hover:bg-[#1C1B19] transition-all shadow-xl"
        >
          Exit Cinema Mode (H)
        </button>
      )}

      {/* RESEARCHER GEOJSON OVERLAY MANAGER MODAL */}
      <ResearcherGeoJsonModal
        isOpen={showResearcherModal}
        onClose={() => setShowResearcherModal(false)}
        currentGeoJson={fatimidEnclosureData}
        onApplyGeoJson={(data, hypothesisTitle) => {
          setFatimidEnclosureData(data);
          showToast(`Applied ${hypothesisTitle}`);
        }}
      />

      {/* PRODUCTION EXPORT & PROVENANCE HUB MODAL */}
      <GeoExportModal
        isOpen={showGeoExportModal}
        onClose={() => setShowGeoExportModal(false)}
        currentFatimidEnclosure={fatimidEnclosureData}
      />

      {/* CLICKED FEATURE PROVENANCE CARD */}
      <FeatureInspectorModal
        feature={selectedGeoFeature}
        onClose={() => setSelectedGeoFeature(null)}
      />

      {/* 3D COMPONENT INFO CARD */}
      <ComponentInfoModal
        selectedComponent={selectedComponent}
        selectedAnnotation={selectedAnnotation}
        onClose={() => {
          setSelectedComponent(null);
          setSelectedAnnotation(null);
        }}
      />

      {/* REMOTION INTEGRATION GUIDE MODAL */}
      <RemotionModal
        isOpen={showRemotionModal}
        onClose={() => setShowRemotionModal(false)}
      />

      {/* ASSET MANIFEST MODAL */}
      <AssetManifestModal
        isOpen={showManifestModal}
        onClose={() => setShowManifestModal(false)}
      />

      {/* PRODUCTION HANDOFF MODAL */}
      <ProductionHandoffModal
        isOpen={showHandoffModal}
        onClose={() => setShowHandoffModal(false)}
      />

      {/* NOTIFICATION TOAST */}
      {toastMessage && (
        <div className="absolute top-24 left-1/2 -translate-x-1/2 z-50 bg-[#1C1B19]/95 text-[#F3EBDB] border border-[#A98A4B] px-4 py-2 rounded-lg shadow-xl text-xs font-mono-doc flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#A98A4B]" />
          <span>{toastMessage}</span>
        </div>
      )}
    </main>
  );
}
