/**
 * Debugging logs in BabZuwaylaRemotion
 */

import React, { useEffect, useRef, useState, useLayoutEffect } from 'react';
import { useCurrentFrame, useVideoConfig, delayRender, continueRender, interpolate } from 'remotion';
import * as THREE from 'three';

import { ViewerState } from './types.ts';
import { createMaterialPalette, MaterialPalette } from './three/materials.ts';
import { createSemicircularTower, TowerResult } from './three/geometry/tower.ts';
import { createCentralPortal, PortalResult } from './three/geometry/portal.ts';
import { createGateDoors, GateDoorsResult } from './three/geometry/doors.ts';
import { createMamlukMinaret, MinaretTiers } from './three/geometry/minaret.ts';

export interface BabZuwaylaRemotionProps {
  frame?: number;
  durationInFrames?: number;
  historicalState?: ViewerState;
  cameraMode?: 'orthographic' | 'perspective';
  assemblyProgress?: number;
  explodedProgress?: number;
  showAnnotations?: boolean;
  width?: number;
  height?: number;
}

export const BabZuwaylaRemotion: React.FC<BabZuwaylaRemotionProps> = ({
  frame: propFrame,
  durationInFrames: propDuration,
  historicalState: propHistoricalState,
  explodedProgress: propExplodedProgress,
  width: propWidth,
  height: propHeight,
}) => {
  const remotionFrame = useCurrentFrame();
  const videoConfig = useVideoConfig();

  const currentFrame = propFrame !== undefined ? propFrame : remotionFrame;
  const totalFrames = propDuration !== undefined ? propDuration : videoConfig.durationInFrames || 300;
  const canvasWidth = propWidth || videoConfig.width || 1920;
  const canvasHeight = propHeight || videoConfig.height || 1080;

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const leftTowerRef = useRef<TowerResult | null>(null);
  const rightTowerRef = useRef<TowerResult | null>(null);
  const portalRef = useRef<PortalResult | null>(null);
  const doorsRef = useRef<GateDoorsResult | null>(null);
  const leftMinaretRef = useRef<MinaretTiers | null>(null);
  const rightMinaretRef = useRef<MinaretTiers | null>(null);
  const orthoCamRef = useRef<THREE.OrthographicCamera | null>(null);
  const perspCamRef = useRef<THREE.PerspectiveCamera | null>(null);

  const handleRef = useRef<number | null>(null);
  if (handleRef.current === null) {
    handleRef.current = delayRender('BabZuwaylaRemotion Init');
  }

  useLayoutEffect(() => {
    if (!canvasRef.current) return;
    const canvas = canvasRef.current;
    const aspect = canvasWidth / canvasHeight;

    if (!rendererRef.current) {
      try {
        const renderer = new THREE.WebGLRenderer({
          canvas,
          antialias: true,
          powerPreference: 'high-performance',
          preserveDrawingBuffer: true,
        });
        renderer.setSize(canvasWidth, canvasHeight);
        renderer.setPixelRatio(1);
        renderer.outputColorSpace = THREE.SRGBColorSpace;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.15;
        rendererRef.current = renderer;

        const scene = new THREE.Scene();
        scene.background = new THREE.Color('#F3EBDB');
        sceneRef.current = scene;

        const frustumSize = 34;
        const orthoCam = new THREE.OrthographicCamera(
          (-frustumSize * aspect) / 2,
          (frustumSize * aspect) / 2,
          frustumSize / 2,
          -frustumSize / 2,
          0.1,
          800
        );
        orthoCamRef.current = orthoCam;

        const perspCam = new THREE.PerspectiveCamera(38, aspect, 0.5, 600);
        perspCamRef.current = perspCam;

        // Lights
        const keyLight = new THREE.DirectionalLight('#fff2d4', 2.3);
        keyLight.position.set(24, 42, 28);
        scene.add(keyLight);

        const hemiLight = new THREE.HemisphereLight('#fbf7ed', '#8e8271', 1.05);
        scene.add(hemiLight);

        const rimLight = new THREE.DirectionalLight('#e6dcce', 0.9);
        rimLight.position.set(-30, 28, -25);
        scene.add(rimLight);

        const materials: MaterialPalette = createMaterialPalette({
          stoneRoughness: 0.82,
          stoneWarmth: 0.55,
          wireframe: false,
          blueprintMode: false,
          shadowIntensity: 0.45,
          aoIntensity: 1.0,
        });

        const masterRoot = new THREE.Group();
        masterRoot.name = 'bab_zuwayla_remotion_root';

        const leftTower = createSemicircularTower(
          { side: 'left', radius: 4.8, height: 17.8, wallDepth: 10.0 },
          materials
        );
        leftTower.group.position.set(-7.2, 0, 0);
        masterRoot.add(leftTower.group);
        leftTowerRef.current = leftTower;

        const rightTower = createSemicircularTower(
          { side: 'right', radius: 4.8, height: 17.8, wallDepth: 10.0 },
          materials
        );
        rightTower.group.position.set(7.2, 0, 0);
        masterRoot.add(rightTower.group);
        rightTowerRef.current = rightTower;

        const centralPortal = createCentralPortal(
          { passageWidth: 4.8, portalHeight: 7.8, passageDepth: 11.4, towerDistance: 14.4 },
          materials
        );
        masterRoot.add(centralPortal.group);
        portalRef.current = centralPortal;

        const doors = createGateDoors(4.8, 6.2, materials);
        masterRoot.add(doors.group);
        doorsRef.current = doors;

        const leftMinaret = createMamlukMinaret({ side: 'left', baseY: 17.8 }, materials);
        leftMinaret.root.position.set(-7.2, 17.8, -1.2);
        masterRoot.add(leftMinaret.root);
        leftMinaretRef.current = leftMinaret;

        const rightMinaret = createMamlukMinaret({ side: 'right', baseY: 17.8 }, materials);
        rightMinaret.root.position.set(7.2, 17.8, -1.2);
        masterRoot.add(rightMinaret.root);
        rightMinaretRef.current = rightMinaret;

        const groundGeom = new THREE.PlaneGeometry(90, 90);
        groundGeom.rotateX(-Math.PI / 2);
        const ground = new THREE.Mesh(groundGeom, materials.groundPaving);
        ground.position.y = -0.01;
        masterRoot.add(ground);

        scene.add(masterRoot);
      } catch (err) {
        console.error('Init error:', err);
      }
    }

    const renderer = rendererRef.current;
    const scene = sceneRef.current;
    const leftTower = leftTowerRef.current;
    const rightTower = rightTowerRef.current;
    const portal = portalRef.current;
    const doors = doorsRef.current;
    const leftMinaret = leftMinaretRef.current;
    const rightMinaret = rightMinaretRef.current;
    const orthoCam = orthoCamRef.current;
    const perspCam = perspCamRef.current;

    if (!renderer || !scene || !leftTower || !rightTower || !portal || !doors || !leftMinaret || !rightMinaret || !orthoCam || !perspCam) {
      return;
    }


    let isOrtho = true;
    let minaretsVisible = false;
    let sectionCut = false;
    let explodeVal = 0;
    let doorAngle = 35;
    let minaretElevation = 0;
    let camPos = new THREE.Vector3();
    let lookAt = new THREE.Vector3();
    let upVec = new THREE.Vector3(0, 1, 0);
    let frustumSize = 34;

    // Check if explicit propHistoricalState was passed
    if (propHistoricalState) {
      if (propHistoricalState === 'TOP_PLAN') {
        isOrtho = true;
        minaretsVisible = false;
        sectionCut = true;
        camPos.set(0, 60, -2.5);
        lookAt.set(0, 0, -2.5);
        upVec.set(0, 0, -1);
        frustumSize = 34;
      } else if (propHistoricalState === 'SIDE_ELEVATION') {
        isOrtho = true;
        minaretsVisible = false;
        sectionCut = false;
        camPos.set(-65, 9.0, -1.9);
        lookAt.set(0, 9.0, -1.9);
        upVec.set(0, 1, 0);
        frustumSize = 28;
      } else if (propHistoricalState === 'FATIMID_ORIGINAL' || propHistoricalState === 'FRONT_ELEVATION') {
        isOrtho = true;
        minaretsVisible = false;
        sectionCut = false;
        camPos.set(0, 9.0, 65);
        lookAt.set(0, 9.0, 0);
        upVec.set(0, 1, 0);
        frustumSize = 28;
      } else if (propHistoricalState === 'MAMLUK_ADDITIONS') {
        isOrtho = true;
        minaretsVisible = true;
        sectionCut = false;
        minaretElevation = 0;
        camPos.set(0, 20.0, 75);
        lookAt.set(0, 20.0, 0);
        upVec.set(0, 1, 0);
        frustumSize = 46;
      } else if (propHistoricalState === 'EXPLODED_VIEW') {
        isOrtho = false;
        minaretsVisible = true;
        sectionCut = false;
        explodeVal = 0.75;
        doorAngle = 55;
        camPos.set(-32, 24, 40);
        lookAt.set(0, 18, 0);
        upVec.set(0, 1, 0);
      } else {
        // FULLY_ASSEMBLED / PERSPECTIVE_3Q
        isOrtho = false;
        minaretsVisible = true;
        sectionCut = false;
        camPos.set(-28, 22, 38);
        lookAt.set(0, 15, -1.0);
        upVec.set(0, 1, 0);
      }
    } else {
      // Continuous 300-frame animation timeline with stable viewing plateaus:
      // Frames 000-049: Top architectural plan
      // Frames 050-089: Smooth transition to side elevation
      // Frames 090-119: Side elevation held stable
      // Frames 120-159: Smooth transition to front elevation
      // Frames 160-189: Front elevation 1092 held stable
      // Frames 190-229: Reveal of Mamluk minarets descending into place
      // Frames 230-244: Front elevation 1421 held stable
      // Frames 245-274: Exploded architectural view
      // Frames 275-299: Assembling into fully assembled 3/4 perspective
      if (currentFrame < 50) {
        // TOP_PLAN PLATEAU
        isOrtho = true;
        minaretsVisible = false;
        sectionCut = true;
        camPos.set(0, 60, -2.5);
        lookAt.set(0, 0, -2.5);
        upVec.set(0, 0, -1);
        frustumSize = 34;
      } else if (currentFrame < 90) {
        // TRANSITION: TOP PLAN -> SIDE ELEVATION
        const t = (currentFrame - 50) / 40;
        isOrtho = true;
        minaretsVisible = false;
        sectionCut = t < 0.2;
        camPos.set(
          interpolate(t, [0, 1], [0, -65]),
          interpolate(t, [0, 1], [60, 9.0]),
          interpolate(t, [0, 1], [-2.5, -1.9])
        );
        lookAt.set(0, interpolate(t, [0, 1], [0, 9.0]), interpolate(t, [0, 1], [-2.5, -1.9]));
        upVec = new THREE.Vector3(0, 0, -1).lerp(new THREE.Vector3(0, 1, 0), t).normalize();
        frustumSize = interpolate(t, [0, 1], [34, 28]);
      } else if (currentFrame < 120) {
        // SIDE ELEVATION PLATEAU
        isOrtho = true;
        minaretsVisible = false;
        sectionCut = false;
        camPos.set(-65, 9.0, -1.9);
        lookAt.set(0, 9.0, -1.9);
        upVec.set(0, 1, 0);
        frustumSize = 28;
      } else if (currentFrame < 160) {
        // TRANSITION: SIDE ELEVATION -> FRONT ELEVATION (orbital arc around origin)
        const t = (currentFrame - 120) / 40;
        isOrtho = true;
        minaretsVisible = false;
        sectionCut = false;
        const radius = 65;
        const angle = interpolate(t, [0, 1], [-Math.PI / 2, 0]);
        camPos.set(radius * Math.sin(angle), 9.0, radius * Math.cos(angle));
        lookAt.set(0, 9.0, interpolate(t, [0, 1], [-1.9, 0]));
        upVec.set(0, 1, 0);
        frustumSize = 28;
      } else if (currentFrame < 190) {
        // FRONT ELEVATION 1092 PLATEAU
        isOrtho = true;
        minaretsVisible = false;
        sectionCut = false;
        camPos.set(0, 9.0, 65);
        lookAt.set(0, 9.0, 0);
        upVec.set(0, 1, 0);
        frustumSize = 28;
      } else if (currentFrame < 230) {
        // MAMLUK MINARETS REVEAL & VERTICAL EXPANSION
        const t = (currentFrame - 190) / 40;
        isOrtho = true;
        minaretsVisible = true;
        sectionCut = false;
        minaretElevation = interpolate(t, [0, 0.8], [1.0, 0.0], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
        camPos.set(0, interpolate(t, [0, 1], [9.0, 20.0]), interpolate(t, [0, 1], [65, 75]));
        lookAt.set(0, interpolate(t, [0, 1], [9.0, 20.0]), 0);
        upVec.set(0, 1, 0);
        frustumSize = interpolate(t, [0, 1], [28, 46]);
      } else if (currentFrame < 245) {
        // FRONT ELEVATION 1421 PLATEAU
        isOrtho = true;
        minaretsVisible = true;
        sectionCut = false;
        minaretElevation = 0;
        camPos.set(0, 20.0, 75);
        lookAt.set(0, 20.0, 0);
        upVec.set(0, 1, 0);
        frustumSize = 46;
      } else if (currentFrame < 275) {
        // EXPLODED VIEW TRANSITION & PEAK
        const t = (currentFrame - 245) / 30;
        isOrtho = false;
        minaretsVisible = true;
        sectionCut = false;
        explodeVal = Math.sin(t * Math.PI) * 0.75;
        doorAngle = interpolate(t, [0, 0.5, 1], [35, 60, 35]);
        camPos.set(
          interpolate(t, [0, 0.5, 1], [0, -32, -30]),
          interpolate(t, [0, 0.5, 1], [20, 24, 23]),
          interpolate(t, [0, 0.5, 1], [75, 40, 39])
        );
        lookAt.set(0, interpolate(t, [0, 1], [20, 17]), 0);
        upVec.set(0, 1, 0);
      } else {
        // ASSEMBLED PERSPECTIVE 3Q
        const t = (currentFrame - 275) / 25;
        isOrtho = false;
        minaretsVisible = true;
        sectionCut = false;
        explodeVal = 0;
        doorAngle = 35;
        camPos.set(
          interpolate(t, [0, 1], [-30, -28]),
          interpolate(t, [0, 1], [23, 22]),
          interpolate(t, [0, 1], [39, 38])
        );
        lookAt.set(0, interpolate(t, [0, 1], [17, 15]), -1.0);
        upVec.set(0, 1, 0);
      }
    }

    const towerLateralShift = explodeVal * 5.2;
    leftTower.group.position.x = -7.2 - towerLateralShift;
    rightTower.group.position.x = 7.2 + towerLateralShift;

    leftTower.setSectionCut(sectionCut);
    rightTower.setSectionCut(sectionCut);
    portal.setSectionCut(sectionCut);

    const minaretY = 17.8 + explodeVal * 6.5 + minaretElevation * 12.0;
    leftMinaret.root.position.x = leftTower.group.position.x;
    leftMinaret.root.position.y = minaretY;
    leftMinaret.root.visible = minaretsVisible;

    rightMinaret.root.position.x = rightTower.group.position.x;
    rightMinaret.root.position.y = minaretY;
    rightMinaret.root.visible = minaretsVisible;

    leftMinaret.setTierExplosion(explodeVal * 0.7);
    rightMinaret.setTierExplosion(explodeVal * 0.7);

    portal.group.position.z = explodeVal * 3.5;
    doors.setDoorAngle(THREE.MathUtils.degToRad(doorAngle));

    let activeCamera: THREE.Camera;
    if (isOrtho) {
      orthoCam.left = (-frustumSize * aspect) / 2;
      orthoCam.right = (frustumSize * aspect) / 2;
      orthoCam.top = frustumSize / 2;
      orthoCam.bottom = -frustumSize / 2;
      orthoCam.position.copy(camPos);
      orthoCam.up.copy(upVec);
      orthoCam.lookAt(lookAt);
      orthoCam.updateProjectionMatrix();
      activeCamera = orthoCam;
    } else {
      perspCam.position.copy(camPos);
      perspCam.up.copy(upVec);
      perspCam.lookAt(lookAt);
      perspCam.updateProjectionMatrix();
      activeCamera = perspCam;
    }

    renderer.render(scene, activeCamera);

    if (handleRef.current !== null) {
      continueRender(handleRef.current);
      handleRef.current = null;
    }
  }, [currentFrame, canvasWidth, canvasHeight, propHistoricalState]);

  const actState = propHistoricalState || (
    currentFrame < 50 ? 'TOP_PLAN'
    : currentFrame < 120 ? 'SIDE_ELEVATION'
    : currentFrame < 190 ? 'FRONT_ELEVATION'
    : currentFrame < 245 ? 'MAMLUK_ADDITIONS'
    : currentFrame < 275 ? 'EXPLODED_VIEW'
    : 'FULLY_ASSEMBLED'
  );

  return (
    <div
      style={{
        width: canvasWidth,
        height: canvasHeight,
        position: 'relative',
        backgroundColor: '#F3EBDB',
        overflow: 'hidden',
      }}
    >
      <canvas
        ref={canvasRef}
        width={canvasWidth}
        height={canvasHeight}
        style={{
          width: canvasWidth,
          height: canvasHeight,
          display: 'block',
        }}
      />

      {/* Editorial Lower-Third */}
      <div
        style={{
          position: 'absolute',
          bottom: 48,
          left: 56,
          pointerEvents: 'none',
          fontFamily: 'Cinzel, serif',
          color: '#1C1B19',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span
            style={{
              fontSize: 14,
              letterSpacing: '0.25em',
              fontWeight: 'bold',
              color: '#A98A4B',
            }}
          >
            RUWAQ | رواق
          </span>
          <span style={{ color: '#A98A4B', opacity: 0.5 }}>•</span>
          <span style={{ fontSize: 13, fontFamily: 'monospace', color: '#1C1B19' }}>
            FRAME {currentFrame.toString().padStart(3, '0')} / {totalFrames}
          </span>
        </div>

        <h1
          style={{
            fontSize: 32,
            margin: '4px 0 0 0',
            fontWeight: 'bold',
            letterSpacing: '0.05em',
          }}
        >
          BAB ZUWAYLA
        </h1>

        <p
          style={{
            fontSize: 14,
            margin: '2px 0 0 0',
            fontFamily: 'monospace',
            color: '#8C4729',
            fontWeight: 500,
          }}
        >
          {actState === 'TOP_PLAN' && 'TOP ARCHITECTURAL PLAN (SECTION CUT & PASSAGE)'}
          {actState === 'SIDE_ELEVATION' && 'SIDE ELEVATION (ORTHOGRAPHIC BASTION PROJECTION)'}
          {actState === 'FRONT_ELEVATION' && 'FRONT ELEVATION • ORIGINAL FATIMID GATE (1092 CE)'}
          {actState === 'MAMLUK_ADDITIONS' && 'MAMLUK MINARETS ADDITION • SULTAN AL-MU\'AYYAD (1415–1421 CE)'}
          {actState === 'EXPLODED_VIEW' && 'EXPLODED ARCHITECTURAL ASSEMBLY'}
          {actState === 'FULLY_ASSEMBLED' && 'FINAL ASSEMBLED MONUMENT (PERSPECTIVE 3Q)'}
        </p>

        <p
          style={{
            fontSize: 11,
            margin: '4px 0 0 0',
            fontFamily: 'monospace',
            color: '#1C1B19',
            opacity: 0.7,
          }}
        >
          APPROXIMATE EDUCATIONAL RECONSTRUCTION • RUWAQ DOCUMENTARY SERIES V04
        </p>
      </div>
    </div>
  );
};
