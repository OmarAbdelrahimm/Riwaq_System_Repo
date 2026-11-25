/**
 * RUWAQ: Bab Zuwayla 3D Architectural Reconstruction
 * Architectural and Documentary Types
 */

export type ViewerState =
  | 'FATIMID_ORIGINAL'   // 1. Original Fatimid gate, without minarets (1092 CE)
  | 'TOP_PLAN'           // 2. Top orthographic plan
  | 'SIDE_ELEVATION'     // 3. Side orthographic elevation
  | 'FRONT_ELEVATION'    // 4. Front orthographic elevation
  | 'PERSPECTIVE_3Q'     // 5. Perspective three-quarter view
  | 'MAMLUK_ADDITIONS'   // 6. Later minaret additions (1415-1421 CE)
  | 'EXPLODED_VIEW'      // 7. Separated architectural components
  | 'FULLY_ASSEMBLED';   // 8. Fully assembled monument

export interface StateDefinition {
  id: ViewerState;
  labelEn: string;
  labelAr: string;
  era: string;
  date: string;
  description: string;
  cameraMode: 'orthographic' | 'perspective';
  targetPos: [number, number, number];
  targetLook: [number, number, number];
  orthoZoom?: number;
  minaretsVisible: boolean;
  explodedProgress: number;
}

export interface ComponentVisibility {
  leftTower: boolean;
  rightTower: boolean;
  centralArch: boolean;
  gatePassage: boolean;
  leftDoor: boolean;
  rightDoor: boolean;
  leftMinaret: boolean;
  rightMinaret: boolean;
  crenellations: boolean;
  ground: boolean;
}

export interface MaterialSettings {
  stoneRoughness: number;
  stoneWarmth: number; // 0 to 1
  wireframe: boolean;
  blueprintMode: boolean;
  shadowIntensity: number;
  aoIntensity: number;
}

export interface AnnotationItem {
  id: string;
  titleEn: string;
  titleAr: string;
  date: string;
  category: 'fatimid' | 'mamluk' | 'defense' | 'detail' | 'masonry';
  position: [number, number, number];
  descriptionEn: string;
  descriptionAr: string;
  certainty: 'Historical Record' | 'Archaeological In Situ' | 'Historical Record & Archaeological In Situ' | 'Educational Reconstruction (Approximate)';
}

export interface RemotionTimelineState {
  frame: number;
  totalFrames: number;
  fps: number;
  isPlaying: boolean;
  loop: boolean;
  speed: number;
}
