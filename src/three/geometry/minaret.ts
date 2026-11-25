/**
 * Mamluk Minarets of Sultan al-Mu'ayyad Shaykh (1415–1421 CE / 818–824 AH)
 * Added atop the Fatimid towers of Bab Zuwayla
 * Master Architect: Muhammad ibn al-Qazzaz (Mu'allim al-Mi'mariyya)
 * Architectural V04: Authentic six-tier vertical articulation based on photo image_8d20f9e3.png
 */

import * as THREE from 'three';
import { MaterialPalette } from '../materials.ts';

export interface MinaretOptions {
  side: 'left' | 'right';
  baseY?: number;
}

export interface MinaretTiers {
  root: THREE.Group;
  tier1: THREE.Group; // Square/Octagonal Lower Shaft
  tier2: THREE.Group; // First Muqarnas Balcony
  tier3: THREE.Group; // Middle Chevron Shaft
  tier4: THREE.Group; // Second Balcony
  tier5: THREE.Group; // Colonnaded Pavilion (Jawsaq)
  tier6: THREE.Group; // Bulbous Finial (Mabkhara & Crescent)
  setTierExplosion: (progress: number) => void;
}

export function createMamlukMinaret(
  options: MinaretOptions,
  materials: MaterialPalette
): MinaretTiers {
  const { side, baseY = 17.8 } = options;
  const namePrefix = side === 'left' ? 'left' : 'right';

  const root = new THREE.Group();
  root.name = `${namePrefix}_minaret`;
  root.position.y = baseY;
  root.userData = {
    id: `${namePrefix}_minaret`,
    nameEn: `${side === 'left' ? 'West (Left)' : 'East (Right)'} Mamluk Minaret`,
    nameAr: side === 'left' ? 'المئذنة الغربية المملوكية' : 'المئذنة الشرقية المملوكية',
    era: 'Burji Mamluk (1415–1421 CE / 818–824 AH)',
    patron: 'Sultan al-Mu\'ayyad Shaykh (السلطان المؤيد شيخ)',
    architect: 'Muhammad ibn al-Qazzaz (محمد بن القزاز)',
    descriptionEn:
      'Masterpiece of Mamluk stone minaret architecture erected directly upon the Fatimid bastion as the twin visual minarets for the adjacent Mosque of Sultan al-Mu\'ayyad Shaykh.',
    descriptionAr:
      'إحدى قمتي العمارة المملوكية شيدهما السلطان المؤيد شيخ فوق برجي البوابة الفاطمية ليكونا مئذنتين لمسجده الملاصق للبوابة، من تصميم المعمار محمد بن القزاز.',
    certainty: 'Historical Record & In Situ Surviving Monument',
  };

  // ==========================================
  // TIER 1: Square Plinth & Lower Octagonal Shaft
  // Height: ~ 7.2m
  // ==========================================
  const tier1 = new THREE.Group();
  tier1.name = `${namePrefix}_minaret_tier1_octagonal_shaft`;
  tier1.userData = {
    nameEn: 'Tier 1: Square Plinth to Octagonal Shaft',
    nameAr: 'المستوى الأول: القاعدة المربعة والجذع المثمن السفلي',
    description: 'Transition from square base to high octagonal shaft decorated with carved blind niches.',
  };

  // Base square transition plinth (resting on tower terrace)
  const plinthW = 3.5;
  const plinthH = 1.1;
  const plinthGeom = new THREE.BoxGeometry(plinthW, plinthH, plinthW);
  const plinth = new THREE.Mesh(plinthGeom, materials.mamlukStone);
  plinth.position.y = plinthH / 2;
  plinth.castShadow = true;
  tier1.add(plinth);

  // Chamfered squinches (square to octagon transition)
  const chamferH = 0.75;
  const chamferGeom = new THREE.CylinderGeometry(1.65, 1.82, chamferH, 8);
  const chamfer = new THREE.Mesh(chamferGeom, materials.mamlukStone);
  chamfer.position.y = plinthH + chamferH / 2;
  chamfer.castShadow = true;
  tier1.add(chamfer);

  // Main lower octagonal shaft
  const octShaftH = 4.8;
  const octRadius = 1.58;
  const octShaftGeom = new THREE.CylinderGeometry(octRadius, octRadius, octShaftH, 8);
  const octShaft = new THREE.Mesh(octShaftGeom, materials.mamlukStone);
  octShaft.position.y = plinthH + chamferH + octShaftH / 2;
  octShaft.castShadow = true;
  octShaft.receiveShadow = true;
  tier1.add(octShaft);

  // Recessed keel-arch panel niches on the 8 faces
  for (let face = 0; face < 8; face++) {
    const ang = (face / 8) * Math.PI * 2;
    const nicheW = 0.52;
    const nicheH = 2.4;
    const nicheGeom = new THREE.BoxGeometry(nicheW, nicheH, 0.12);
    const niche = new THREE.Mesh(nicheGeom, materials.fatimidDarkStone);
    const nDist = octRadius * 0.94;
    niche.position.set(
      Math.sin(ang) * nDist,
      octShaft.position.y,
      Math.cos(ang) * nDist
    );
    niche.rotation.y = ang;
    tier1.add(niche);
  }

  // Upper molding on tier 1
  const t1MoldingH = 0.35;
  const t1MoldingGeom = new THREE.CylinderGeometry(octRadius + 0.14, octRadius, t1MoldingH, 8);
  const t1Molding = new THREE.Mesh(t1MoldingGeom, materials.mamlukStone);
  t1Molding.position.y = plinthH + chamferH + octShaftH + t1MoldingH / 2;
  t1Molding.castShadow = true;
  tier1.add(t1Molding);

  root.add(tier1);

  // Base Y offset for Tier 2: 7.1m
  const tier2BaseY = plinthH + chamferH + octShaftH + t1MoldingH;

  // ==========================================
  // TIER 2: First Balcony & Muqarnas Corbeling
  // Height: ~ 2.1m
  // ==========================================
  const tier2 = new THREE.Group();
  tier2.name = `${namePrefix}_minaret_tier2_first_balcony`;
  tier2.position.y = tier2BaseY;
  tier2.userData = {
    nameEn: 'Tier 2: Lower Muqarnas Balcony',
    nameAr: 'المستوى الثاني: شرفة المؤذن السفلية ومقرنصاتها الحجرية',
    description: 'Triple tier of cantilevered stone muqarnas stalactite corbels supporting an octagonal walkway.',
  };

  // Muqarnas corbel layers (3 cascading tiers)
  const muqarnas1Geom = new THREE.CylinderGeometry(octRadius + 0.32, octRadius, 0.42, 16);
  const muqarnas1 = new THREE.Mesh(muqarnas1Geom, materials.mamlukStone);
  muqarnas1.position.y = 0.21;
  muqarnas1.castShadow = true;
  tier2.add(muqarnas1);

  const muqarnas2Geom = new THREE.CylinderGeometry(octRadius + 0.72, octRadius + 0.32, 0.48, 16);
  const muqarnas2 = new THREE.Mesh(muqarnas2Geom, materials.mamlukStone);
  muqarnas2.position.y = 0.42 + 0.24;
  muqarnas2.castShadow = true;
  tier2.add(muqarnas2);

  // Balcony floor platform
  const balconyRadius = octRadius + 0.82;
  const bFloorGeom = new THREE.CylinderGeometry(balconyRadius, balconyRadius, 0.25, 16);
  const bFloor = new THREE.Mesh(bFloorGeom, materials.mamlukStone);
  bFloor.position.y = 0.9 + 0.125;
  bFloor.castShadow = true;
  tier2.add(bFloor);

  // Stone openwork balustrade around balcony
  const balustradeGeom = new THREE.CylinderGeometry(
    balconyRadius + 0.04,
    balconyRadius + 0.04,
    0.92,
    16,
    1,
    true
  );
  const balustrade = new THREE.Mesh(balustradeGeom, materials.mamlukStone);
  balustrade.position.y = 1.025 + 0.46;
  balustrade.castShadow = true;
  tier2.add(balustrade);

  root.add(tier2);

  // Base Y offset for Tier 3: tier2BaseY + 1.15
  const tier3BaseY = tier2BaseY + 1.15;

  // ==========================================
  // TIER 3: Middle Shaft with Chevron Zigzag Relief
  // Height: ~ 5.2m
  // ==========================================
  const tier3 = new THREE.Group();
  tier3.name = `${namePrefix}_minaret_tier3_chevron_shaft`;
  tier3.position.y = tier3BaseY;
  tier3.userData = {
    nameEn: 'Tier 3: Chevron Relief Octagonal Shaft',
    nameAr: 'المستوى الثالث: الجذع المثمن المزخرف بالزخرفة الزجزاجية (السمكية)',
    description: 'Slender octagonal shaft carved with interlocking diagonal chevron masonry relief bands.',
  };

  const midRadius = 1.22;
  const midHeight = 5.0;
  const midGeom = new THREE.CylinderGeometry(midRadius, midRadius * 1.04, midHeight, 8);
  const midShaft = new THREE.Mesh(midGeom, materials.mamlukChevron);
  midShaft.position.y = midHeight / 2;
  midShaft.castShadow = true;
  midShaft.receiveShadow = true;
  tier3.add(midShaft);

  // Arched window openings on 4 cardinal faces
  for (let w = 0; w < 4; w++) {
    const wAng = (w / 4) * Math.PI * 2;
    const windowGeom = new THREE.BoxGeometry(0.36, 1.35, 0.18);
    const windowMesh = new THREE.Mesh(windowGeom, materials.fatimidDarkStone);
    const wDist = midRadius * 0.95;
    windowMesh.position.set(
      Math.sin(wAng) * wDist,
      midHeight * 0.5,
      Math.cos(wAng) * wDist
    );
    windowMesh.rotation.y = wAng;
    tier3.add(windowMesh);
  }

  root.add(tier3);

  // Base Y offset for Tier 4: tier3BaseY + midHeight
  const tier4BaseY = tier3BaseY + midHeight;

  // ==========================================
  // TIER 4: Second Balcony
  // Height: ~ 1.4m
  // ==========================================
  const tier4 = new THREE.Group();
  tier4.name = `${namePrefix}_minaret_tier4_second_balcony`;
  tier4.position.y = tier4BaseY;
  tier4.userData = {
    nameEn: 'Tier 4: Upper Balcony & Muqarnas Transition',
    nameAr: 'المستوى الرابع: الشرفة العلوية ومقرنصاتها الحجرية',
    description: 'Upper corbelled balcony providing transition to the colonnaded pavilion.',
  };

  const b2CorbelGeom = new THREE.CylinderGeometry(midRadius + 0.42, midRadius, 0.45, 16);
  const b2Corbel = new THREE.Mesh(b2CorbelGeom, materials.mamlukStone);
  b2Corbel.position.y = 0.225;
  b2Corbel.castShadow = true;
  tier4.add(b2Corbel);

  const b2FloorGeom = new THREE.CylinderGeometry(midRadius + 0.52, midRadius + 0.52, 0.2, 16);
  const b2Floor = new THREE.Mesh(b2FloorGeom, materials.mamlukStone);
  b2Floor.position.y = 0.45 + 0.1;
  b2Floor.castShadow = true;
  tier4.add(b2Floor);

  // Second balustrade
  const b2RailGeom = new THREE.CylinderGeometry(midRadius + 0.55, midRadius + 0.55, 0.65, 16, 1, true);
  const b2Rail = new THREE.Mesh(b2RailGeom, materials.mamlukStone);
  b2Rail.position.y = 0.55 + 0.325;
  tier4.add(b2Rail);

  root.add(tier4);

  // Base Y offset for Tier 5: tier4BaseY + 0.65
  const tier5BaseY = tier4BaseY + 0.65;

  // ==========================================
  // TIER 5: Open Colonnaded Pavilion (Jawsaq / الجوسق)
  // Height: ~ 3.0m
  // Visible in photo image_8d20f9e3.png - 8 slender stone colonnettes!
  // ==========================================
  const tier5 = new THREE.Group();
  tier5.name = `${namePrefix}_minaret_tier5_colonnaded_pavilion`;
  tier5.position.y = tier5BaseY;
  tier5.userData = {
    nameEn: 'Tier 5: Colonnaded Pavilion (Jawsaq)',
    nameAr: 'المستوى الخامس: الجوسق ذو الأعمدة الحجرية الرشيقة',
    description: 'Open octagonal arcade supported by 8 slender columns with horseshoe arches.',
  };

  const pavilionRadius = 0.92;
  const columnHeight = 2.3;
  const colRadius = 0.082;

  // Central core cylinder
  const coreGeom = new THREE.CylinderGeometry(0.32, 0.32, columnHeight, 12);
  const coreMesh = new THREE.Mesh(coreGeom, materials.mamlukStone);
  coreMesh.position.y = columnHeight / 2;
  coreMesh.castShadow = true;
  tier5.add(coreMesh);

  // 8 Slender columns around perimeter
  const colGeom = new THREE.CylinderGeometry(colRadius, colRadius * 1.12, columnHeight, 8);
  for (let c = 0; c < 8; c++) {
    const colAng = (c / 8) * Math.PI * 2;
    const colMesh = new THREE.Mesh(colGeom, materials.mamlukStone);
    colMesh.position.set(
      Math.sin(colAng) * pavilionRadius,
      columnHeight / 2,
      Math.cos(colAng) * pavilionRadius
    );
    colMesh.castShadow = true;
    colMesh.name = `${namePrefix}_pavilion_column_${c}`;
    tier5.add(colMesh);
  }

  // Pavilion entablature and arch canopy
  const canopyGeom = new THREE.CylinderGeometry(pavilionRadius + 0.28, pavilionRadius + 0.1, 0.52, 8);
  const canopy = new THREE.Mesh(canopyGeom, materials.mamlukStone);
  canopy.position.y = columnHeight + 0.26;
  canopy.castShadow = true;
  tier5.add(canopy);

  root.add(tier5);

  // Base Y offset for Tier 6: tier5BaseY + columnHeight + 0.52
  const tier6BaseY = tier5BaseY + columnHeight + 0.52;

  // ==========================================
  // TIER 6: Bulbous Finial (Mabkhara) & Bronze Crescent
  // Height: ~ 3.5m
  // ==========================================
  const tier6 = new THREE.Group();
  tier6.name = `${namePrefix}_minaret_tier6_bulb_finial`;
  tier6.position.y = tier6BaseY;
  tier6.userData = {
    nameEn: 'Tier 6: Bulbous Finial (Mabkhara) & Hilal',
    nameAr: 'المستوى السادس: القمة البصلية (المبخرة) والهلال البرونزي',
    description: 'Bulbous pear-shaped dome finial crowned by a bronze crescent (hilal).',
  };

  // Bulb neck
  const neckGeom = new THREE.CylinderGeometry(0.48, 0.62, 0.55, 16);
  const neck = new THREE.Mesh(neckGeom, materials.mamlukStone);
  neck.position.y = 0.275;
  neck.castShadow = true;
  tier6.add(neck);

  // Pear-shaped bulb (Mabkhara) - created via LatheGeometry for authentic silhouette
  const bulbPoints: THREE.Vector2[] = [
    new THREE.Vector2(0.48, 0.0),
    new THREE.Vector2(0.82, 0.38),
    new THREE.Vector2(1.02, 0.78),
    new THREE.Vector2(0.92, 1.25),
    new THREE.Vector2(0.52, 1.65),
    new THREE.Vector2(0.18, 1.95),
    new THREE.Vector2(0.0, 2.15),
  ];
  const bulbGeom = new THREE.LatheGeometry(bulbPoints, 24);
  const bulbMesh = new THREE.Mesh(bulbGeom, materials.mamlukStone);
  bulbMesh.position.y = 0.55;
  bulbMesh.castShadow = true;
  tier6.add(bulbMesh);

  // Bronze Spire rod
  const spireRodGeom = new THREE.CylinderGeometry(0.038, 0.038, 1.35, 8);
  const spireRod = new THREE.Mesh(spireRodGeom, materials.bronzeFinial);
  spireRod.position.y = 2.7 + 0.48;
  tier6.add(spireRod);

  // 3 Bronze Spheres (Jammur)
  const sphereSizes = [0.17, 0.13, 0.09];
  sphereSizes.forEach((rad, sIdx) => {
    const sGeom = new THREE.SphereGeometry(rad, 16, 16);
    const sMesh = new THREE.Mesh(sGeom, materials.bronzeFinial);
    sMesh.position.y = 2.7 + 0.28 + sIdx * 0.26;
    sMesh.castShadow = true;
    tier6.add(sMesh);
  });

  // Top Crescent (Hilal)
  const crescentTorusGeom = new THREE.TorusGeometry(0.22, 0.038, 8, 24, Math.PI * 1.5);
  crescentTorusGeom.rotateZ(Math.PI * 0.25);
  const crescentMesh = new THREE.Mesh(crescentTorusGeom, materials.bronzeFinial);
  crescentMesh.position.y = 3.9;
  crescentMesh.castShadow = true;
  tier6.add(crescentMesh);

  root.add(tier6);

  // Method to animate exploded tiers vertically
  const setTierExplosion = (progress: number) => {
    tier1.position.y = 0;
    tier2.position.y = tier2BaseY + progress * 2.0;
    tier3.position.y = tier3BaseY + progress * 4.5;
    tier4.position.y = tier4BaseY + progress * 7.0;
    tier5.position.y = tier5BaseY + progress * 9.5;
    tier6.position.y = tier6BaseY + progress * 12.0;
  };

  return {
    root,
    tier1,
    tier2,
    tier3,
    tier4,
    tier5,
    tier6,
    setTierExplosion,
  };
}
