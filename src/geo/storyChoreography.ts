/**
 * RUWAQ Historical Geography: Deterministic Frame Choreography Engine
 * Remotion-compatible frame-by-frame interpolation across the 7 story acts.
 */

import { StoryActDefinition, StoryActId } from './types.ts';

export const STORY_ACTS: StoryActDefinition[] = [
  {
    id: 'MODERN_CAIRO',
    actNumber: 1,
    startFrame: 0,
    endFrame: 80,
    titleEn: 'Modern Cairo & The Nile Valley',
    titleAr: 'سياق القاهرة المعاصرة ووادي النيل',
    subtitleEn: 'Geographical Setting between the Nile River and the Eastern Muqattam Hills',
    historicalContextEn:
      'Greater Cairo lies along the Nile flood plain at the apex of the Delta. In the 10th century CE, the Nile flowed further east than its modern course, bounded by the ancient canal of Al-Khalij al-Misri.',
    cartographicNoteEn: 'Verified contemporary hydrography and arterial roads (OpenStreetMap / ODbL)',
    targetCenter: [31.2380, 30.0450],
    targetZoom: 11.8,
    targetPitch: 0,
    targetBearing: 0,
    activeLayers: ['nileWater', 'modernStreets'],
  },
  {
    id: 'HISTORIC_CAIRO',
    actNumber: 2,
    startFrame: 81,
    endFrame: 160,
    titleEn: 'Historic Cairo World Heritage Site',
    titleAr: 'حدود القاهرة التاريخية (اليونسكو)',
    subtitleEn: 'UNESCO World Heritage Property (Ref 89, Inscribed 1979)',
    historicalContextEn:
      'Inscribed on the World Heritage List in 1979, Historic Cairo covers 523 hectares containing over 600 registered Islamic monuments spanning Fatimid, Ayyubid, Mamluk, and Ottoman epochs.',
    cartographicNoteEn: 'Official UNESCO World Heritage Centre boundary survey & buffer zone',
    targetCenter: [31.2610, 30.0460],
    targetZoom: 13.8,
    targetPitch: 12,
    targetBearing: 0,
    activeLayers: ['nileWater', 'modernStreets', 'historicCairoUnesco'],
  },
  {
    id: 'FATIMID_EXTENT',
    actNumber: 3,
    startFrame: 161,
    endFrame: 240,
    titleEn: 'Approximate Fatimid Enclosure (1092 CE)',
    titleAr: 'حرم القاهرة الفاطمية التقريبي (١٠٩٢ م)',
    subtitleEn: 'Fortified Perimeter Built by Armenian Vizier Badr al-Jamali',
    historicalContextEn:
      'Following economic crises and military rebellions, Caliph al-Mustansir summoned Badr al-Jamali to reconstruct the city walls in stone (1087–1092 CE), replacing Jawhar al-Siqilli’s crumbling 969 CE sun-dried brick circuit.',
    cartographicNoteEn:
      'APPROXIMATE HISTORICAL RECONSTRUCTION: Western and southern segments interpolated along historical records and street lines (±50m archaeological uncertainty buffer).',
    targetCenter: [31.2612, 30.0485],
    targetZoom: 14.8,
    targetPitch: 22,
    targetBearing: 8,
    activeLayers: [
      'nileWater',
      'modernStreets',
      'historicCairoUnesco',
      'fatimidApproximateExtent',
      'uncertaintyBuffer',
    ],
  },
  {
    id: 'AL_MUIZZ_AXIS',
    actNumber: 4,
    startFrame: 241,
    endFrame: 320,
    titleEn: 'The Historic North-South Al-Mu‘izz Spine',
    titleAr: 'محور قصبة القاهرة (شارع المعز)',
    subtitleEn: 'Ceremonial Axis Connecting North and South Enclosure Gates (1.2 km)',
    historicalContextEn:
      'Known historically as the Qasaba, this grand thoroughfare divided the Fatimid royal enclosure into eastern and western sectors. Between the two imperial palaces lay Bayn al-Qasrayn, the public ceremonial heart of the caliphate.',
    cartographicNoteEn: 'Verified OpenStreetMap Way geometry (OSM 24905187) following active street alignment',
    targetCenter: [31.2612, 30.0485],
    targetZoom: 15.4,
    targetPitch: 32,
    targetBearing: 355,
    activeLayers: [
      'nileWater',
      'modernStreets',
      'fatimidApproximateExtent',
      'alMuizzAxis',
      'uncertaintyBuffer',
    ],
  },
  {
    id: 'NORTHERN_GATES',
    actNumber: 5,
    startFrame: 321,
    endFrame: 400,
    titleEn: 'Documented Northern Gates: Bab al-Futuh & Bab al-Nasr',
    titleAr: 'البوابات الشمالية الموثقة: باب الفتوح وباب النصر',
    subtitleEn: 'In-Situ Standing Stone Fortifications Commissioned 1087 CE (480 AH)',
    historicalContextEn:
      'Bab al-Futuh (Gate of Conquests) and Bab al-Nasr (Gate of Victory) survive in intact stone masonry. Built by architects from northern Syria/Armenia, they introduced Byzantine-influenced stereotomy, splayed embrasures, and machicolations.',
    cartographicNoteEn: 'In-situ physical monuments surveyed by K.A.C. Creswell (OSM Nodes 482591653 & 293370335)',
    targetCenter: [31.2645, 30.0543],
    targetZoom: 16.7,
    targetPitch: 42,
    targetBearing: 25,
    activeLayers: [
      'fatimidApproximateExtent',
      'alMuizzAxis',
      'northernGates',
      'secondaryGateTraces',
    ],
  },
  {
    id: 'BAB_ZUWAYLA_GATE',
    actNumber: 6,
    startFrame: 401,
    endFrame: 480,
    titleEn: 'Bab Zuwayla at the Southern Frontier',
    titleAr: 'باب زويلة عند الطرف الجنوبي للمدينة',
    subtitleEn: 'Sole Surviving Southern Gate of Fatimid Cairo (1092 CE / 485 AH)',
    historicalContextEn:
      'Named after the Berber Zuwayla cavalry regiment, this massive portal guarded the southern route toward Fustat. Its solid semicircular stone bastions later served as foundations for Sultan al-Mu‘ayyad’s twin minarets in 1415–1421 CE.',
    cartographicNoteEn: 'Standing monument (OSM Node 293370334, 30.04278° N, 31.25895° E)',
    targetCenter: [31.25895, 30.04278],
    targetZoom: 17.5,
    targetPitch: 50,
    targetBearing: 345,
    activeLayers: [
      'fatimidApproximateExtent',
      'alMuizzAxis',
      'northernGates',
      'babZuwaylaSouthernAnchor',
    ],
  },
  {
    id: 'TRANSITION_TO_3D',
    actNumber: 7,
    startFrame: 481,
    endFrame: 600,
    titleEn: 'From Map to Monument: 3D Architectural Reconstruction',
    titleAr: 'الانتقال إلى البنية ثلاثية الأبعاد لباب زويلة',
    subtitleEn: 'Choreographed Descent into the 3D Reconstructed Gateway & Mamluk Minarets',
    historicalContextEn:
      'Transitioning from macro-geography to micro-architectural stereotomy: examining the semicircular bastions, defensive inner passage, and Sultan al-Mu‘ayyad’s octagonal minarets.',
    cartographicNoteEn: 'Frame-synchronized blend between MapLibre GL 3D perspective and Three.js architectural model',
    targetCenter: [31.25895, 30.04278],
    targetZoom: 18.8,
    targetPitch: 62,
    targetBearing: 330,
    activeLayers: [
      'alMuizzAxis',
      'babZuwaylaSouthernAnchor',
      'threeDOverlay',
    ],
  },
];

// Helper: Linear & Smoothstep Interpolation
function smoothstep(edge0: number, edge1: number, x: number): number {
  const t = Math.min(Math.max((x - edge0) / (edge1 - edge0), 0), 1);
  return t * t * (3 - 2 * t);
}

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

export interface MapCameraState {
  center: [number, number];
  zoom: number;
  pitch: number;
  bearing: number;
  currentAct: StoryActDefinition;
  nextAct: StoryActDefinition | null;
  actProgress: number; // 0 to 1 within the current act
  globalProgress: number; // 0 to 1
  threeDBlend: number; // 0 (pure map) to 1 (full 3D model)
  alMuizzProgress: number; // 0 (hidden) to 1 (fully drawn)
}

/**
 * Returns deterministic map camera position and layer blend values for any frame number
 */
export function getInterpolatedMapCamera(
  frame: number,
  totalFrames: number = 600
): MapCameraState {
  const clampedFrame = Math.max(0, Math.min(frame, totalFrames));
  const globalProgress = clampedFrame / totalFrames;

  // Find which act this frame belongs to
  let actIndex = 0;
  for (let i = 0; i < STORY_ACTS.length; i++) {
    if (
      clampedFrame >= STORY_ACTS[i].startFrame &&
      clampedFrame <= STORY_ACTS[i].endFrame
    ) {
      actIndex = i;
      break;
    }
  }

  const currentAct = STORY_ACTS[actIndex];
  const nextAct =
    actIndex < STORY_ACTS.length - 1 ? STORY_ACTS[actIndex + 1] : currentAct;

  const actDuration = currentAct.endFrame - currentAct.startFrame;
  const rawActProgress = actDuration > 0
    ? (clampedFrame - currentAct.startFrame) / actDuration
    : 1;
  const t = smoothstep(0, 1, rawActProgress);

  // If transitioning near end of act, smooth blend to next act camera
  const centerLng = lerp(currentAct.targetCenter[0], nextAct.targetCenter[0], t * 0.7);
  const centerLat = lerp(currentAct.targetCenter[1], nextAct.targetCenter[1], t * 0.7);
  const zoom = lerp(currentAct.targetZoom, nextAct.targetZoom, t * 0.7);
  const pitch = lerp(currentAct.targetPitch, nextAct.targetPitch, t * 0.7);
  const bearing = lerp(currentAct.targetBearing, nextAct.targetBearing, t * 0.7);

  // Al-Mu'izz Axis line drawing progress
  let alMuizzProgress = 0;
  if (clampedFrame < 240) {
    alMuizzProgress = 0;
  } else if (clampedFrame >= 240 && clampedFrame <= 320) {
    alMuizzProgress = smoothstep(240, 320, clampedFrame);
  } else {
    alMuizzProgress = 1;
  }

  // 3D Model blend factor (Act 7: frames 481 to 600)
  let threeDBlend = 0;
  if (clampedFrame >= 481) {
    threeDBlend = smoothstep(481, 570, clampedFrame);
  }

  return {
    center: [centerLng, centerLat],
    zoom,
    pitch,
    bearing,
    currentAct,
    nextAct,
    actProgress: rawActProgress,
    globalProgress,
    threeDBlend,
    alMuizzProgress,
  };
}
