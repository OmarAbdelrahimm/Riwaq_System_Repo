/**
 * RUWAQ Historical Geography: MapLibre GL Map Component
 * Handles WebGL cartographic visualization, deterministic camera interpolation,
 * independent layer toggles, and seamless transition into the 3D Bab Zuwayla model.
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import workerCode from 'maplibre-gl/dist/maplibre-gl-worker.mjs?raw';

type MapLibreMap = maplibregl.Map;
type Marker = maplibregl.Marker;

// Initialize MapLibre web worker deterministically via inline Blob URL
// This avoids cross-origin or 404 worker load errors in Vite dev and production
if (typeof window !== 'undefined') {
  try {
    const workerBlob = new Blob([workerCode], { type: 'application/javascript' });
    maplibregl.setWorkerUrl(URL.createObjectURL(workerBlob));
  } catch (err) {
    console.warn('MapLibre inline worker blob setup fallback:', err);
  }
}

import { createRuwaqMapStyle } from './maplibreStyle.ts';
import { LayerVisibilityState, GeoFeatureMetadata } from './types.ts';
import { getInterpolatedMapCamera, MapCameraState } from './storyChoreography.ts';
import { FEATURE_METADATA_DIRECTORY } from './cairoHistoricalGeoJSON.ts';

interface RuwaqMaplibreViewProps {
  frame: number;
  totalFrames: number;
  isInteractiveMode: boolean;
  layerVisibility: LayerVisibilityState;
  fatimidEnclosureData: GeoJSON.FeatureCollection;
  onSelectFeature?: (meta: GeoFeatureMetadata) => void;
  onOpenResearcherModal?: () => void;
  children3DOverlay?: React.ReactNode;
}

export const RuwaqMaplibreView: React.FC<RuwaqMaplibreViewProps> = ({
  frame,
  totalFrames,
  isInteractiveMode,
  layerVisibility,
  fatimidEnclosureData,
  onSelectFeature,
  onOpenResearcherModal,
  children3DOverlay,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const [mapLoaded, setMapLoaded] = useState<boolean>(false);
  const [cursorCoords, setCursorCoords] = useState<{ lng: number; lat: number }>({
    lng: 31.25895,
    lat: 30.04278,
  });
  const markersRef = useRef<Marker[]>([]);

  // Calculate current deterministic camera state
  const cameraState: MapCameraState = getInterpolatedMapCamera(frame, totalFrames);

  // 1. Initialize MapLibre GL Instance
  useEffect(() => {
    if (!mapContainerRef.current) return;

    const initialCamera = getInterpolatedMapCamera(frame, totalFrames);
    const styleSpec = createRuwaqMapStyle(fatimidEnclosureData, true);

    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: styleSpec,
      center: initialCamera.center,
      zoom: initialCamera.zoom,
      pitch: initialCamera.pitch,
      bearing: initialCamera.bearing,
      interactive: isInteractiveMode,
      attributionControl: false,
      maxPitch: 75,
      minZoom: 9,
      maxZoom: 20,
    });

    map.on('load', () => {
      setMapLoaded(true);
    });

    map.on('mousemove', (e: any) => {
      setCursorCoords({
        lng: Number(e.lngLat.lng.toFixed(5)),
        lat: Number(e.lngLat.lat.toFixed(5)),
      });
    });

    // Click handler on vector layers to select feature metadata
    const interactiveLayerIds = [
      'fatimid-gates-outer-circle',
      'al-muizz-axis-core',
      'fatimid-enclosure-fill',
      'unesco-zone-fill',
      'northern-wall-solid',
    ];

    interactiveLayerIds.forEach((layerId) => {
      map.on('click', layerId, (e: any) => {
        if (!e.features || e.features.length === 0) return;
        const feat = e.features[0];
        const featId = (feat.properties as any)?.id;
        if (featId && FEATURE_METADATA_DIRECTORY[featId]) {
          onSelectFeature?.(FEATURE_METADATA_DIRECTORY[featId]);
        }
      });

      map.on('mouseenter', layerId, () => {
        map.getCanvas().style.cursor = 'pointer';
      });
      map.on('mouseleave', layerId, () => {
        map.getCanvas().style.cursor = '';
      });
    });

    mapRef.current = map;

    return () => {
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // 2. Update Map interactivity mode
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    if (isInteractiveMode) {
      map.boxZoom.enable();
      map.scrollZoom.enable();
      map.dragPan.enable();
      map.dragRotate.enable();
      map.keyboard.enable();
      map.doubleClickZoom.enable();
      map.touchZoomRotate.enable();
    } else {
      map.boxZoom.disable();
      map.scrollZoom.disable();
      map.dragPan.disable();
      map.dragRotate.disable();
      map.keyboard.disable();
      map.doubleClickZoom.disable();
      map.touchZoomRotate.disable();
    }
  }, [isInteractiveMode]);

  // 3. Update Camera Deterministically on Frame Change (in Story / Remotion Mode)
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapLoaded || isInteractiveMode) return;

    map.jumpTo({
      center: cameraState.center,
      zoom: cameraState.zoom,
      pitch: cameraState.pitch,
      bearing: cameraState.bearing,
    });
  }, [frame, totalFrames, mapLoaded, isInteractiveMode, cameraState]);

  // 4. Update Layer Visibilities
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapLoaded) return;

    const setVisibility = (layerId: string, visible: boolean) => {
      if (map.getLayer(layerId)) {
        map.setLayoutProperty(layerId, 'visibility', visible ? 'visible' : 'none');
      }
    };

    // Modern Streets
    setVisibility('modern-roads-line', layerVisibility.modernStreets);

    // Nile Water
    setVisibility('nile-water-fill', layerVisibility.nileWater);
    setVisibility('nile-water-outline', layerVisibility.nileWater);

    // UNESCO Zone
    setVisibility('unesco-zone-fill', layerVisibility.historicCairoUnesco);
    setVisibility('unesco-zone-casing', layerVisibility.historicCairoUnesco);

    // Fatimid Enclosure
    setVisibility('fatimid-enclosure-fill', layerVisibility.fatimidApproximateExtent);
    setVisibility('fatimid-enclosure-outline', layerVisibility.fatimidApproximateExtent);

    // Uncertainty Buffer
    setVisibility('fatimid-uncertainty-buffer-fill', layerVisibility.uncertaintyBuffer);
    setVisibility('fatimid-uncertainty-buffer-outline', layerVisibility.uncertaintyBuffer);

    // Al-Mu'izz Axis
    setVisibility('al-muizz-axis-glow', layerVisibility.alMuizzAxis);
    setVisibility('al-muizz-axis-core', layerVisibility.alMuizzAxis);
    setVisibility('al-muizz-axis-dashed', layerVisibility.alMuizzAxis);

    // Northern Gates & Wall
    setVisibility('northern-wall-solid', layerVisibility.northernGates);
    setVisibility('northern-wall-gold-crest', layerVisibility.northernGates);

    // Fatimid Gates
    setVisibility('fatimid-gates-outer-circle', layerVisibility.northernGates || layerVisibility.babZuwaylaSouthernAnchor);
    setVisibility('fatimid-gates-inner-circle', layerVisibility.northernGates || layerVisibility.babZuwaylaSouthernAnchor);
  }, [layerVisibility, mapLoaded]);

  // 5. Update Researcher GeoJSON Data when changed
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapLoaded) return;

    const source = map.getSource('fatimid-enclosure') as any;
    if (source && source.setData) {
      source.setData(fatimidEnclosureData);
    }
  }, [fatimidEnclosureData, mapLoaded]);

  // 6. Architectural Overlay HTML Markers
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapLoaded) return;

    // Clean existing markers
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    // Bab Zuwayla Monumental Pin
    if (layerVisibility.babZuwaylaSouthernAnchor) {
      const bzEl = document.createElement('div');
      bzEl.className = 'ruwaq-map-marker ruwaq-marker-bab-zuwayla';
      bzEl.innerHTML = `
        <div style="
          background: #1C1B19;
          border: 2px solid #A98A4B;
          color: #F3EBDB;
          padding: 4px 8px;
          border-radius: 4px;
          font-family: 'Cinzel', serif;
          font-size: 11px;
          font-weight: bold;
          display: flex;
          align-items: center;
          gap: 6px;
          box-shadow: 0 4px 16px rgba(0,0,0,0.5);
          cursor: pointer;
          white-space: nowrap;
        ">
          <span style="color: #A98A4B;">★</span>
          <span>BAB ZUWAYLA</span>
          <span style="font-family: 'Amiri', serif; font-size: 12px; color: #A98A4B;">باب زويلة</span>
          <span style="font-size: 9px; opacity: 0.7; font-family: monospace;">1092 CE</span>
        </div>
      `;
      bzEl.onclick = () => {
        onSelectFeature?.(FEATURE_METADATA_DIRECTORY['gate_bab_zuwayla']);
      };

      const bzMarker = new maplibregl.Marker({ element: bzEl, anchor: 'bottom' })
        .setLngLat([31.25895, 30.04278])
        .addTo(map);
      markersRef.current.push(bzMarker);
    }

    // Northern Gates Markers
    if (layerVisibility.northernGates) {
      // Bab al-Futuh
      const bfEl = document.createElement('div');
      bfEl.innerHTML = `
        <div style="
          background: #1C1B19/90;
          border: 1px solid #A98A4B;
          color: #F3EBDB;
          padding: 2px 6px;
          border-radius: 3px;
          font-family: 'Cinzel', serif;
          font-size: 10px;
          cursor: pointer;
          white-space: nowrap;
          box-shadow: 0 2px 8px rgba(0,0,0,0.4);
        ">
          <span>BAB AL-FUTUH</span>
          <span style="font-family: 'Amiri', serif; color: #A98A4B;">باب الفتوح</span>
        </div>
      `;
      bfEl.onclick = () => {
        onSelectFeature?.(FEATURE_METADATA_DIRECTORY['gate_bab_al_futuh']);
      };
      const bfMarker = new maplibregl.Marker({ element: bfEl, anchor: 'bottom' })
        .setLngLat([31.26348, 30.05435])
        .addTo(map);
      markersRef.current.push(bfMarker);

      // Bab al-Nasr
      const bnEl = document.createElement('div');
      bnEl.innerHTML = `
        <div style="
          background: #1C1B19/90;
          border: 1px solid #A98A4B;
          color: #F3EBDB;
          padding: 2px 6px;
          border-radius: 3px;
          font-family: 'Cinzel', serif;
          font-size: 10px;
          cursor: pointer;
          white-space: nowrap;
          box-shadow: 0 2px 8px rgba(0,0,0,0.4);
        ">
          <span>BAB AL-NASR</span>
          <span style="font-family: 'Amiri', serif; color: #A98A4B;">باب النصر</span>
        </div>
      `;
      bnEl.onclick = () => {
        onSelectFeature?.(FEATURE_METADATA_DIRECTORY['gate_bab_al_nasr']);
      };
      const bnMarker = new maplibregl.Marker({ element: bnEl, anchor: 'bottom' })
        .setLngLat([31.26555, 30.05417])
        .addTo(map);
      markersRef.current.push(bnMarker);
    }
  }, [mapLoaded, layerVisibility, onSelectFeature]);

  return (
    <div className="relative w-full h-full overflow-hidden select-none bg-[#F3EBDB]">
      {/* 1. MapLibre GL WebGL Canvas */}
      <div
        ref={mapContainerRef}
        className="w-full h-full absolute inset-0 z-0 cursor-crosshair"
      />

      {/* 2. Architectural Drafting Coordinate Crosshairs & Grids */}
      <div className="pointer-events-none absolute inset-0 z-10">
        {/* Subtle drafting border */}
        <div className="absolute inset-4 border border-[#A98A4B]/30 pointer-events-none" />
        <div className="absolute top-4 left-4 w-4 h-4 border-t-2 border-l-2 border-[#A98A4B]" />
        <div className="absolute top-4 right-4 w-4 h-4 border-t-2 border-r-2 border-[#A98A4B]" />
        <div className="absolute bottom-4 left-4 w-4 h-4 border-b-2 border-l-2 border-[#A98A4B]" />
        <div className="absolute bottom-4 right-4 w-4 h-4 border-b-2 border-r-2 border-[#A98A4B]" />

        {/* Real-Time Geodetic Coordinates Readout */}
        <div className="absolute top-6 left-8 bg-[#1C1B19]/85 text-[#F3EBDB] border border-[#A98A4B]/40 px-3 py-1.5 rounded text-[11px] font-mono-doc backdrop-blur-none flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="text-[#A98A4B] font-bold">LAT:</span>
            <span>{cursorCoords.lat.toFixed(5)}° N</span>
          </div>
          <span className="text-[#A98A4B]/40">|</span>
          <div className="flex items-center gap-1.5">
            <span className="text-[#A98A4B] font-bold">LNG:</span>
            <span>{cursorCoords.lng.toFixed(5)}° E</span>
          </div>
          <span className="text-[#A98A4B]/40">|</span>
          <div className="flex items-center gap-1.5">
            <span className="text-[#A98A4B] font-bold">DATUM:</span>
            <span>WGS-84 / OSM</span>
          </div>
        </div>

        {/* Classical Cartographic Compass & North Arrow */}
        <div className="absolute top-6 right-8 bg-[#1C1B19]/85 text-[#F3EBDB] border border-[#A98A4B]/40 px-3 py-1.5 rounded flex items-center gap-2 text-xs font-mono-doc">
          <div
            className="w-4 h-4 flex items-center justify-center transition-transform"
            style={{ transform: `rotate(${-cameraState.bearing}deg)` }}
          >
            <span className="text-[#A98A4B] font-bold">▲</span>
          </div>
          <span className="font-arabic text-[#A98A4B]">شمال</span>
          <span className="text-[10px] opacity-75">N ({Math.round(cameraState.bearing)}°)</span>
        </div>

        {/* Dual Scale Bar: Metric & Historical Egyptian Dhirā‘ (Cubits) */}
        <div className="absolute bottom-24 right-8 bg-[#1C1B19]/85 text-[#F3EBDB] border border-[#A98A4B]/40 px-3 py-2 rounded text-[10px] font-mono-doc flex flex-col gap-1">
          <div className="flex items-center justify-between text-[#A98A4B]">
            <span>0</span>
            <span>200m</span>
            <span>400m</span>
          </div>
          <div className="w-36 h-1.5 bg-[#F3EBDB] flex">
            <div className="w-1/2 h-full bg-[#1C1B19]" />
            <div className="w-1/2 h-full bg-[#A98A4B]" />
          </div>
          <div className="flex items-center justify-between text-[#D8CEBC]/70 text-[9px]">
            <span>0 ذراع</span>
            <span>≈ ٥٣٣ ذراع معماري (Dhirā‘)</span>
          </div>
        </div>

        {/* Explicit Historical Reconstruction Caution Banner */}
        <div className="absolute top-16 left-8 max-w-md pointer-events-auto">
          <div className="bg-[#8C4729]/95 text-[#F3EBDB] border border-[#A98A4B] p-2.5 rounded-lg shadow-xl text-xs flex flex-col gap-1.5 backdrop-blur-none">
            <div className="flex items-center justify-between gap-2">
              <span className="font-bold tracking-wider font-mono-doc text-[10px] text-[#F3EBDB] uppercase flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-[#A98A4B] animate-pulse" />
                HISTORICAL RECONSTRUCTION NOTICE
              </span>
              <button
                onClick={onOpenResearcherModal}
                className="px-2 py-0.5 bg-[#1C1B19] text-[#A98A4B] hover:text-[#F3EBDB] border border-[#A98A4B]/50 rounded text-[10px] font-mono-doc hover:bg-[#A98A4B]/20 transition-all cursor-pointer"
              >
                Researcher GeoJSON ⚙
              </button>
            </div>
            <p className="text-[11px] leading-relaxed text-[#F3EBDB]/90">
              Surviving 1087–1092 CE in-situ stone is restricted to the northern sector (Bab al-Futuh & Bab al-Nasr) and Bab Zuwayla. Western/southern wall outlines are explicitly approximate hypotheses (±50m buffer) and editable via researcher GeoJSON.
            </p>
          </div>
        </div>
      </div>

      {/* 3. Act 7: Seamless 3D Architectural Model Overlay */}
      {cameraState.threeDBlend > 0 && children3DOverlay && (
        <div
          className="absolute inset-0 z-30 transition-opacity duration-300 pointer-events-auto"
          style={{
            opacity: cameraState.threeDBlend,
            background: `radial-gradient(circle at center, transparent 30%, rgba(243, 235, 219, ${cameraState.threeDBlend * 0.85}) 100%)`,
          }}
        >
          {children3DOverlay}
        </div>
      )}
    </div>
  );
};
