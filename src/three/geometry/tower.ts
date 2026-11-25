/**
 * Semicircular Stone Tower Geometry (Left / Right Bastions)
 * Fatimid Era (1092 CE / 485 AH) - Vizier Badr al-Jamali
 * Architectural V04: Physically coherent semicircular towers bonded to entrance passage
 */

import * as THREE from 'three';
import { MaterialPalette } from '../materials.ts';

export interface TowerOptions {
  side: 'left' | 'right';
  radius?: number;
  height?: number;
  wallDepth?: number;
}

export interface TowerResult {
  group: THREE.Group;
  lowerStructure: THREE.Group;
  upperStructure: THREE.Group;
  setSectionCut: (enabled: boolean) => void;
}

export function createSemicircularTower(
  options: TowerOptions,
  materials: MaterialPalette
): TowerResult {
  const {
    side,
    radius = 4.8,
    height = 17.8,
    wallDepth = 10.0,
  } = options;

  const towerGroup = new THREE.Group();
  const namePrefix = side === 'left' ? 'left' : 'right';
  towerGroup.name = `${namePrefix}_semicircular_tower`;
  towerGroup.userData = {
    id: `${namePrefix}_tower`,
    nameEn: `${side === 'left' ? 'West (Left)' : 'East (Right)'} Semicircular Tower`,
    nameAr: side === 'left' ? 'البرج الغربي (الأيسر)' : 'البرج الشرقي (الأيمن)',
    era: 'Fatimid (1092 CE / 485 AH)',
    patron: 'Badr al-Jamali (أمير الجيوش بدر الجمالي)',
    descriptionEn:
      'Massive solid dressed Mokattam limestone semicircular bastion designed to deflect siege catapult projectiles and enfilade attackers.',
    descriptionAr:
      'برج حجري نصف دائري ضخم من الحجر الفص الجيري المصقول، صُمم لحماية مدخل القاهرة وتشتيت مقذوفات الحصار.',
    certainty: 'Historical Record & Archaeological In Situ',
  };

  const lowerStructure = new THREE.Group();
  lowerStructure.name = `${namePrefix}_tower_lower_structure`;

  const upperStructure = new THREE.Group();
  upperStructure.name = `${namePrefix}_tower_upper_structure`;

  const sign = side === 'left' ? -1 : 1;
  const planCutHeight = 5.0; // Cut level for top architectural plan
  const wallThickness = 1.35; // Ashlar perimeter wall thickness
  const innerRadius = radius - wallThickness;

  // ==========================================
  // LOWER STRUCTURE (Y = 0 to Y = 5.0m)
  // Visible in Top Architectural Plan Cut
  // ==========================================

  // 1. Foundation Plinth / Battered Base Course
  const plinthH = 1.2;
  const plinthRadius = radius + 0.3;
  const plinthGeom = new THREE.CylinderGeometry(
    radius,
    plinthRadius,
    plinthH,
    36,
    1,
    false,
    -Math.PI / 2,
    Math.PI
  );
  const plinthMesh = new THREE.Mesh(plinthGeom, materials.fatimidDarkStone);
  plinthMesh.name = `${namePrefix}_tower_foundation_plinth`;
  plinthMesh.position.set(0, plinthH / 2, 0);
  plinthMesh.castShadow = true;
  plinthMesh.receiveShadow = true;
  lowerStructure.add(plinthMesh);

  // Plinth rear rectangular base
  const plinthRearGeom = new THREE.BoxGeometry(plinthRadius * 2, plinthH, wallDepth);
  const plinthRear = new THREE.Mesh(plinthRearGeom, materials.fatimidDarkStone);
  plinthRear.position.set(0, plinthH / 2, -wallDepth / 2);
  plinthRear.castShadow = true;
  plinthRear.receiveShadow = true;
  lowerStructure.add(plinthRear);

  // 2. Lower Semicircular Curved Drum (from plinth up to plan cut height)
  const lowerWallH = planCutHeight - plinthH;
  const lowerWallY = plinthH + lowerWallH / 2;

  const curvedWallGeom = new THREE.CylinderGeometry(
    radius,
    radius,
    lowerWallH,
    36,
    1,
    false,
    -Math.PI / 2,
    Math.PI
  );
  const curvedWallMesh = new THREE.Mesh(curvedWallGeom, materials.fatimidStone);
  curvedWallMesh.name = `${namePrefix}_tower_curved_wall_lower`;
  curvedWallMesh.position.set(0, lowerWallY, 0);
  curvedWallMesh.castShadow = true;
  curvedWallMesh.receiveShadow = true;
  lowerStructure.add(curvedWallMesh);

  // Outer straight flank wall (extending back to city wall)
  const outerFlankW = wallThickness;
  const outerFlankMesh = new THREE.Mesh(
    new THREE.BoxGeometry(outerFlankW, lowerWallH, wallDepth),
    materials.fatimidStone
  );
  outerFlankMesh.name = `${namePrefix}_tower_outer_flank_lower`;
  outerFlankMesh.position.set(sign * (radius - outerFlankW / 2), lowerWallY, -wallDepth / 2);
  outerFlankMesh.castShadow = true;
  outerFlankMesh.receiveShadow = true;
  lowerStructure.add(outerFlankMesh);

  // Rear curtain wall (facing interior Cairo)
  const rearWallMesh = new THREE.Mesh(
    new THREE.BoxGeometry(radius * 2, lowerWallH, wallThickness),
    materials.fatimidStone
  );
  rearWallMesh.name = `${namePrefix}_tower_rear_wall_lower`;
  rearWallMesh.position.set(0, lowerWallY, -wallDepth + wallThickness / 2);
  rearWallMesh.castShadow = true;
  rearWallMesh.receiveShadow = true;
  lowerStructure.add(rearWallMesh);

  // Inner flank wall (forming the defensive side wall of the central gateway passage!)
  const innerFlankMesh = new THREE.Mesh(
    new THREE.BoxGeometry(wallThickness, lowerWallH, wallDepth),
    materials.fatimidStone
  );
  innerFlankMesh.name = `${namePrefix}_tower_passage_flank_lower`;
  innerFlankMesh.position.set(-sign * (radius - wallThickness / 2), lowerWallY, -wallDepth / 2);
  innerFlankMesh.castShadow = true;
  innerFlankMesh.receiveShadow = true;
  lowerStructure.add(innerFlankMesh);

  // Interior chamber floor (guardroom / shooting gallery)
  const floorMesh = new THREE.Mesh(
    new THREE.BoxGeometry(innerRadius * 2, 0.2, wallDepth),
    materials.fatimidDarkStone
  );
  floorMesh.position.set(0, plinthH + 0.1, -wallDepth / 2);
  floorMesh.receiveShadow = true;
  lowerStructure.add(floorMesh);

  // 3. Arrow Slit Embrasures (Recessed into curved drum)
  const angles = [-0.6, -0.3, 0, 0.3, 0.6];
  const lowerSlitY = plinthH + lowerWallH * 0.55;

  angles.forEach((ang, idx) => {
    // Narrow vertical embrasure recessed flush onto drum face
    const slitGeom = new THREE.BoxGeometry(0.2, 1.35, 0.35);
    const slitMesh = new THREE.Mesh(slitGeom, materials.fatimidDarkStone);
    const slitR = radius - 0.12;
    slitMesh.position.set(
      Math.sin(ang) * slitR,
      lowerSlitY,
      Math.cos(ang) * slitR
    );
    slitMesh.rotation.y = ang;
    slitMesh.name = `${namePrefix}_arrow_slit_L1_${idx}`;
    lowerStructure.add(slitMesh);
  });

  // ==========================================
  // UPPER STRUCTURE (Y = 5.0m to Y = 17.8m)
  // Hidden during Top Plan Cut
  // ==========================================

  const upperWallH = height - planCutHeight - 1.6;
  const upperWallY = planCutHeight + upperWallH / 2;

  // Upper semicircular curved drum
  const upperCurvedGeom = new THREE.CylinderGeometry(
    radius,
    radius,
    upperWallH,
    36,
    1,
    false,
    -Math.PI / 2,
    Math.PI
  );
  const upperCurvedMesh = new THREE.Mesh(upperCurvedGeom, materials.fatimidStone);
  upperCurvedMesh.name = `${namePrefix}_tower_curved_wall_upper`;
  upperCurvedMesh.position.set(0, upperWallY, 0);
  upperCurvedMesh.castShadow = true;
  upperCurvedMesh.receiveShadow = true;
  upperStructure.add(upperCurvedMesh);

  // Upper outer flank wall
  const upperOuterFlank = new THREE.Mesh(
    new THREE.BoxGeometry(outerFlankW, upperWallH, wallDepth),
    materials.fatimidStone
  );
  upperOuterFlank.position.set(sign * (radius - outerFlankW / 2), upperWallY, -wallDepth / 2);
  upperOuterFlank.castShadow = true;
  upperOuterFlank.receiveShadow = true;
  upperStructure.add(upperOuterFlank);

  // Upper rear curtain wall
  const upperRearWall = new THREE.Mesh(
    new THREE.BoxGeometry(radius * 2, upperWallH, wallThickness),
    materials.fatimidStone
  );
  upperRearWall.position.set(0, upperWallY, -wallDepth + wallThickness / 2);
  upperRearWall.castShadow = true;
  upperRearWall.receiveShadow = true;
  upperStructure.add(upperRearWall);

  // Upper inner flank wall
  const upperInnerFlank = new THREE.Mesh(
    new THREE.BoxGeometry(wallThickness, upperWallH, wallDepth),
    materials.fatimidStone
  );
  upperInnerFlank.position.set(-sign * (radius - wallThickness / 2), upperWallY, -wallDepth / 2);
  upperInnerFlank.castShadow = true;
  upperInnerFlank.receiveShadow = true;
  upperStructure.add(upperInnerFlank);

  // Solid vaulted ceiling below terrace
  const ceilingGeom = new THREE.CylinderGeometry(
    innerRadius,
    innerRadius,
    1.2,
    32,
    1,
    false,
    -Math.PI / 2,
    Math.PI
  );
  const ceilingMesh = new THREE.Mesh(ceilingGeom, materials.fatimidDarkStone);
  ceilingMesh.position.set(0, height - 2.2, 0);
  upperStructure.add(ceilingMesh);

  // Upper tier arrow slits
  const upperSlitY = planCutHeight + upperWallH * 0.45;
  angles.forEach((ang, idx) => {
    const slitGeom = new THREE.BoxGeometry(0.2, 1.35, 0.35);
    const slitMesh = new THREE.Mesh(slitGeom, materials.fatimidDarkStone);
    const slitR = radius - 0.12;
    slitMesh.position.set(
      Math.sin(ang) * slitR,
      upperSlitY,
      Math.cos(ang) * slitR
    );
    slitMesh.rotation.y = ang;
    slitMesh.name = `${namePrefix}_arrow_slit_L2_${idx}`;
    upperStructure.add(slitMesh);
  });

  // 4. Horizontal Torus / Stringcourse Molding
  const moldingH = 0.4;
  const moldingRadius = radius + 0.2;
  const moldingGeom = new THREE.CylinderGeometry(
    moldingRadius,
    moldingRadius,
    moldingH,
    36,
    1,
    false,
    -Math.PI / 2,
    Math.PI
  );
  const moldingMesh = new THREE.Mesh(moldingGeom, materials.fatimidDarkStone);
  moldingMesh.name = `${namePrefix}_tower_stringcourse`;
  moldingMesh.position.set(0, planCutHeight + upperWallH * 0.72, 0);
  moldingMesh.castShadow = true;
  upperStructure.add(moldingMesh);

  // 5. Corbelled Upper Cornice Platform (Rooftop Terrace)
  const platformH = 0.65;
  const platformRadius = radius + 0.28;
  const platformGeom = new THREE.CylinderGeometry(
    platformRadius,
    radius,
    platformH,
    36,
    1,
    false,
    -Math.PI / 2,
    Math.PI
  );
  const platformMesh = new THREE.Mesh(platformGeom, materials.fatimidDarkStone);
  platformMesh.name = `${namePrefix}_tower_corbelled_cornice`;
  platformMesh.position.set(0, height - 1.6 + platformH / 2, 0);
  platformMesh.castShadow = true;
  upperStructure.add(platformMesh);

  // Flat rooftop terrace (where minaret plinth rests)
  const roofGeom = new THREE.CylinderGeometry(
    platformRadius,
    platformRadius,
    0.35,
    36,
    1,
    false,
    -Math.PI / 2,
    Math.PI
  );
  const roofMesh = new THREE.Mesh(roofGeom, materials.fatimidStone);
  roofMesh.name = `${namePrefix}_tower_terrace`;
  roofMesh.position.set(0, height - 1.6 + platformH + 0.175, 0);
  roofMesh.receiveShadow = true;
  upperStructure.add(roofMesh);

  const rearTerrace = new THREE.Mesh(
    new THREE.BoxGeometry(platformRadius * 2, 0.35, wallDepth),
    materials.fatimidStone
  );
  rearTerrace.position.set(0, height - 1.6 + platformH + 0.175, -wallDepth / 2);
  rearTerrace.receiveShadow = true;
  upperStructure.add(rearTerrace);

  // 6. Stepped Fatimid Battlements (Sharafat)
  const battlementsGroup = new THREE.Group();
  battlementsGroup.name = `${namePrefix}_tower_crenellations`;

  const merlonCount = 11;
  const merlonW = 0.72;
  const merlonH = 1.35;
  const merlonD = 0.48;

  for (let m = 0; m < merlonCount; m++) {
    const fraction = (m + 0.5) / merlonCount;
    const angle = (fraction - 0.5) * Math.PI * 0.94;

    const merlon = new THREE.Group();
    const mBase = new THREE.Mesh(
      new THREE.BoxGeometry(merlonW, merlonH * 0.7, merlonD),
      materials.fatimidStone
    );
    mBase.position.y = (merlonH * 0.7) / 2;
    mBase.castShadow = true;
    merlon.add(mBase);

    const mCapGeom = new THREE.CylinderGeometry(
      merlonW * 0.44,
      merlonW * 0.44,
      merlonD,
      14,
      1,
      false,
      0,
      Math.PI
    );
    mCapGeom.rotateZ(Math.PI / 2);
    mCapGeom.rotateY(Math.PI / 2);
    const mCap = new THREE.Mesh(mCapGeom, materials.fatimidStone);
    mCap.position.y = merlonH * 0.7;
    mCap.castShadow = true;
    merlon.add(mCap);

    const rDist = platformRadius - merlonD / 2 - 0.05;
    merlon.position.set(
      Math.sin(angle) * rDist,
      height - 1.6 + platformH + 0.35,
      Math.cos(angle) * rDist
    );
    merlon.rotation.y = angle;
    merlon.name = `${namePrefix}_merlon_${m}`;
    battlementsGroup.add(merlon);
  }
  upperStructure.add(battlementsGroup);

  towerGroup.add(lowerStructure);
  towerGroup.add(upperStructure);

  // Contact shadow
  const shadowMesh = new THREE.Mesh(
    new THREE.PlaneGeometry(radius * 3.2, radius * 3.2).rotateX(-Math.PI / 2),
    materials.contactShadow
  );
  shadowMesh.name = `${namePrefix}_tower_contact_shadow`;
  shadowMesh.position.set(0, 0.02, 0);
  lowerStructure.add(shadowMesh);

  const setSectionCut = (enabled: boolean) => {
    upperStructure.visible = !enabled;
  };

  return {
    group: towerGroup,
    lowerStructure,
    upperStructure,
    setSectionCut,
  };
}
