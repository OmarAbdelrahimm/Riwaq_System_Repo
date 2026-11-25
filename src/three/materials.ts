/**
 * PBR Materials Library for Bab Zuwayla
 * High-fidelity architectural materials adhering to Three.js PBR standards
 */

import * as THREE from 'three';
import {
  createAshlarStoneTexture,
  createAshlarNormalTexture,
  createIronStuddedDoorTexture,
  createChevronReliefTexture,
  createContactShadowTexture,
  createBlueprintGridTexture
} from './textures.ts';
import { MaterialSettings } from '../types.ts';

export interface MaterialPalette {
  fatimidStone: THREE.MeshStandardMaterial;
  fatimidDarkStone: THREE.MeshStandardMaterial;
  mamlukStone: THREE.MeshStandardMaterial;
  mamlukChevron: THREE.MeshStandardMaterial;
  doorStuddedIron: THREE.MeshStandardMaterial;
  doorTimberEdge: THREE.MeshStandardMaterial;
  bronzeFinial: THREE.MeshStandardMaterial;
  groundPaving: THREE.MeshStandardMaterial;
  blueprintGrid: THREE.MeshBasicMaterial;
  contactShadow: THREE.MeshBasicMaterial;
  highlightOverlay: THREE.MeshBasicMaterial;
}

export function createMaterialPalette(settings: MaterialSettings): MaterialPalette {
  const stoneTexture = createAshlarStoneTexture(settings.stoneWarmth);
  stoneTexture.repeat.set(2, 3);

  const stoneNormal = createAshlarNormalTexture();
  stoneNormal.repeat.set(2, 3);

  const doorTexture = createIronStuddedDoorTexture();
  const chevronTexture = createChevronReliefTexture();
  const shadowTexture = createContactShadowTexture();
  const gridTexture = createBlueprintGridTexture();

  // Fatimid 1092 CE stone: Weathered Mokattam limestone
  const fatimidStone = new THREE.MeshStandardMaterial({
    color: new THREE.Color('#d4c6b0'),
    map: stoneTexture,
    normalMap: stoneNormal,
    normalScale: new THREE.Vector2(0.35, 0.35),
    roughness: settings.stoneRoughness,
    metalness: 0.04,
    wireframe: settings.wireframe,
  });

  // Fatimid recessed shadow stone (jambs, inner passages)
  const fatimidDarkStone = new THREE.MeshStandardMaterial({
    color: new THREE.Color('#b8a994'),
    map: stoneTexture,
    roughness: Math.min(1.0, settings.stoneRoughness + 0.1),
    metalness: 0.05,
    wireframe: settings.wireframe,
  });

  // Mamluk 1415–1421 CE stone: Sultan al-Mu'ayyad minarets (distinct, crisp limestone carving)
  const mamlukStone = new THREE.MeshStandardMaterial({
    color: new THREE.Color('#dfd1bc'),
    map: stoneTexture,
    roughness: Math.max(0.4, settings.stoneRoughness - 0.08),
    metalness: 0.05,
    wireframe: settings.wireframe,
  });

  // Mamluk chevron tier
  const mamlukChevron = new THREE.MeshStandardMaterial({
    color: new THREE.Color('#d9cbba'),
    map: chevronTexture,
    roughness: 0.75,
    metalness: 0.03,
    wireframe: settings.wireframe,
  });

  // Fortified iron-studded doors (matching image_191b72fb.png)
  const doorStuddedIron = new THREE.MeshStandardMaterial({
    color: new THREE.Color('#38332d'),
    map: doorTexture,
    roughness: 0.45,
    metalness: 0.65,
    wireframe: settings.wireframe,
  });

  const doorTimberEdge = new THREE.MeshStandardMaterial({
    color: new THREE.Color('#28211b'),
    roughness: 0.85,
    metalness: 0.05,
    wireframe: settings.wireframe,
  });

  // Bronze crescents / finials
  const bronzeFinial = new THREE.MeshStandardMaterial({
    color: new THREE.Color('#c59b48'),
    roughness: 0.28,
    metalness: 0.85,
    wireframe: settings.wireframe,
  });

  // Ground apron / Cairo foundation stratum
  const groundPaving = new THREE.MeshStandardMaterial({
    color: new THREE.Color('#e0d5c1'),
    roughness: 0.95,
    metalness: 0.02,
  });

  // Technical blueprint floor grid
  const blueprintGrid = new THREE.MeshBasicMaterial({
    map: gridTexture,
    transparent: true,
    opacity: 0.7,
    depthWrite: false,
  });
  blueprintGrid.polygonOffset = true;
  blueprintGrid.polygonOffsetFactor = -1;
  blueprintGrid.polygonOffsetUnits = -1;

  // Contact shadow
  const contactShadow = new THREE.MeshBasicMaterial({
    map: shadowTexture,
    transparent: true,
    opacity: settings.shadowIntensity,
    depthWrite: false,
  });

  // Component selection highlight
  const highlightOverlay = new THREE.MeshBasicMaterial({
    color: new THREE.Color('#a98a4b'),
    transparent: true,
    opacity: 0.35,
    wireframe: true,
    depthTest: true,
  });

  return {
    fatimidStone,
    fatimidDarkStone,
    mamlukStone,
    mamlukChevron,
    doorStuddedIron,
    doorTimberEdge,
    bronzeFinial,
    groundPaving,
    blueprintGrid,
    contactShadow,
    highlightOverlay,
  };
}

export function updateMaterialsWithSettings(
  palette: MaterialPalette,
  settings: MaterialSettings
) {
  palette.fatimidStone.wireframe = settings.wireframe;
  palette.fatimidDarkStone.wireframe = settings.wireframe;
  palette.mamlukStone.wireframe = settings.wireframe;
  palette.mamlukChevron.wireframe = settings.wireframe;
  palette.doorStuddedIron.wireframe = settings.wireframe;

  palette.fatimidStone.roughness = settings.stoneRoughness;
  palette.mamlukStone.roughness = Math.max(0.4, settings.stoneRoughness - 0.08);

  if (settings.blueprintMode) {
    palette.fatimidStone.color.set('#d8d1c2');
    palette.mamlukStone.color.set('#dcd5c7');
    palette.blueprintGrid.opacity = 0.9;
  } else {
    palette.fatimidStone.color.set('#d4c6b0');
    palette.mamlukStone.color.set('#dfd1bc');
    palette.blueprintGrid.opacity = 0.35;
  }

  palette.contactShadow.opacity = settings.shadowIntensity;
}
