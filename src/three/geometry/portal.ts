/**
 * Central Entrance Arch & Continuous Gate Passage Geometry
 * Fatimid Era (1092 CE / 485 AH) - Vizier Badr al-Jamali
 * Architectural V04: Open continuous passage with cushion voussoirs and section cut
 */

import * as THREE from 'three';
import { MaterialPalette } from '../materials.ts';

export interface PortalOptions {
  passageWidth?: number;
  portalHeight?: number;
  passageDepth?: number;
  towerDistance?: number;
}

export interface PortalResult {
  group: THREE.Group;
  lowerStructure: THREE.Group;
  upperStructure: THREE.Group;
  setSectionCut: (enabled: boolean) => void;
}

export function createCentralPortal(
  options: PortalOptions,
  materials: MaterialPalette
): PortalResult {
  const {
    passageWidth = 4.8,
    portalHeight = 7.8,
    passageDepth = 11.4,
    towerDistance = 14.4,
  } = options;

  const portalGroup = new THREE.Group();
  portalGroup.name = 'central_entrance_arch';
  portalGroup.userData = {
    id: 'central_portal',
    nameEn: 'Central Entrance Portal & Continuous Gate Passage',
    nameAr: 'المدخل الأوسط وممر البوابة الفاطمية المستمر',
    era: 'Fatimid (1092 CE / 485 AH)',
    patron: 'Badr al-Jamali (أمير الجيوش بدر الجمالي)',
    descriptionEn:
      'Fortified portal featuring a slightly pointed arch with 17 joggled cushion voussoirs, leading into a continuous 11.4m deep open defensive passage.',
    descriptionAr:
      'عقد المدخل المدبب المزين بـ 17 صنجة وسادية منحوتة، يفتح على ممر دفاعي مفتوح ومستمر بطول 11.4 متراً.',
    certainty: 'Historical Record & Archaeological In Situ',
  };

  const lowerStructure = new THREE.Group();
  lowerStructure.name = 'portal_lower_structure';

  const upperStructure = new THREE.Group();
  upperStructure.name = 'portal_upper_structure';

  const planCutHeight = 5.0; // Cut level for top architectural plan
  const entranceZ = 1.6; // Z position of front entrance arch
  const pierDepth = 2.4;
  const halfPassage = passageWidth / 2;
  const halfTowerDist = towerDistance / 2;
  const pierWidth = halfTowerDist - halfPassage;

  // ==========================================
  // LOWER STRUCTURE (Y = 0 to Y = 5.0m)
  // Visible in Top Architectural Plan Cut
  // ==========================================

  // 1. Archway Jamb Piers (Left and Right framing the opening)
  const pierHeight = 4.8;

  const leftPierGeom = new THREE.BoxGeometry(pierWidth, pierHeight, pierDepth);
  const leftPier = new THREE.Mesh(leftPierGeom, materials.fatimidStone);
  leftPier.name = 'left_arch_jamb_pier';
  leftPier.position.set(-halfPassage - pierWidth / 2, pierHeight / 2, entranceZ - pierDepth / 2);
  leftPier.castShadow = true;
  leftPier.receiveShadow = true;
  lowerStructure.add(leftPier);

  const rightPierGeom = new THREE.BoxGeometry(pierWidth, pierHeight, pierDepth);
  const rightPier = new THREE.Mesh(rightPierGeom, materials.fatimidStone);
  rightPier.name = 'right_arch_jamb_pier';
  rightPier.position.set(halfPassage + pierWidth / 2, pierHeight / 2, entranceZ - pierDepth / 2);
  rightPier.castShadow = true;
  rightPier.receiveShadow = true;
  lowerStructure.add(rightPier);

  // 2. Continuous Passage Floor (Extending from southern facade all the way to Cairo interior)
  const passageCenterZ = entranceZ - passageDepth / 2;
  const floorGeom = new THREE.BoxGeometry(passageWidth, 0.2, passageDepth);
  const floorMesh = new THREE.Mesh(floorGeom, materials.fatimidDarkStone);
  floorMesh.name = 'gate_passage_floor_paving';
  floorMesh.position.set(0, 0.1, passageCenterZ);
  floorMesh.receiveShadow = true;
  lowerStructure.add(floorMesh);

  // 3. Lower Lateral Passage Walls (Bonding to tower inner flanks)
  const flankWallThickness = 0.55;
  const passageWallH = planCutHeight;

  const leftFlank = new THREE.Mesh(
    new THREE.BoxGeometry(flankWallThickness, passageWallH, passageDepth),
    materials.fatimidStone
  );
  leftFlank.name = 'gate_passage_wall_left_lower';
  leftFlank.position.set(-halfPassage - flankWallThickness / 2, passageWallH / 2, passageCenterZ);
  leftFlank.castShadow = true;
  leftFlank.receiveShadow = true;
  lowerStructure.add(leftFlank);

  const rightFlank = new THREE.Mesh(
    new THREE.BoxGeometry(flankWallThickness, passageWallH, passageDepth),
    materials.fatimidStone
  );
  rightFlank.name = 'gate_passage_wall_right_lower';
  rightFlank.position.set(halfPassage + flankWallThickness / 2, passageWallH / 2, passageCenterZ);
  rightFlank.castShadow = true;
  rightFlank.receiveShadow = true;
  lowerStructure.add(rightFlank);

  // ==========================================
  // UPPER STRUCTURE (Y = 4.8m to Y = 17.8m)
  // Hidden during Top Plan Cut
  // ==========================================

  // 4. Impost Capital Moldings
  const impostGeom = new THREE.BoxGeometry(pierWidth + 0.3, 0.35, pierDepth + 0.3);
  const leftImpost = new THREE.Mesh(impostGeom, materials.fatimidDarkStone);
  leftImpost.position.set(-halfPassage - pierWidth / 2, pierHeight + 0.175, entranceZ - pierDepth / 2);
  leftImpost.castShadow = true;
  upperStructure.add(leftImpost);

  const rightImpost = new THREE.Mesh(impostGeom, materials.fatimidDarkStone);
  rightImpost.position.set(halfPassage + pierWidth / 2, pierHeight + 0.175, entranceZ - pierDepth / 2);
  rightImpost.castShadow = true;
  upperStructure.add(rightImpost);

  // 5. Pointed Arch Ring with 17 Cushion Voussoirs (al-Sanjat al-Wisadiyyah)
  const archRingGroup = new THREE.Group();
  archRingGroup.name = 'pointed_arch_cushion_voussoirs';
  archRingGroup.userData = {
    nameEn: 'Fatimid Cushion Voussoirs (الصنجات الوسادية)',
    nameAr: 'الصنجات الوسادية ذات الواجهات المحدبة',
    description: 'Iconic cushion voussoirs introduced to Cairo during the Fatimid fortification of 1092 CE.',
  };

  const voussoirCount = 17;
  const archRadius = halfPassage;
  const archCenterY = pierHeight + 0.35;
  const voussoirThickness = 0.95;

  for (let v = 0; v < voussoirCount; v++) {
    const angleFraction = (v + 0.5) / voussoirCount;
    const angle = Math.PI - angleFraction * Math.PI;

    // Cushion voussoir block with rounded pillow form
    const vWidth = ((Math.PI * archRadius) / voussoirCount) * 0.95;
    const vGeom = new THREE.BoxGeometry(vWidth, voussoirThickness, pierDepth);
    const vMesh = new THREE.Mesh(vGeom, materials.fatimidStone);

    const rMid = archRadius + voussoirThickness / 2;
    vMesh.position.set(
      Math.cos(angle) * rMid,
      archCenterY + Math.sin(angle) * rMid * 1.08, // slightly pointed vertical elongation
      entranceZ - pierDepth / 2
    );
    vMesh.rotation.z = angle - Math.PI / 2;
    vMesh.castShadow = true;
    vMesh.receiveShadow = true;
    vMesh.name = `voussoir_${v}`;
    archRingGroup.add(vMesh);
  }
  upperStructure.add(archRingGroup);

  // 6. Arch Spandrel Masonry above the pointed arch
  const spandrelH = 3.6;
  const spandrelGeom = new THREE.BoxGeometry(towerDistance, spandrelH, pierDepth);
  const spandrelMesh = new THREE.Mesh(spandrelGeom, materials.fatimidStone);
  spandrelMesh.name = 'arch_spandrel_masonry';
  spandrelMesh.position.set(0, 7.5 + spandrelH / 2, entranceZ - pierDepth / 2);
  spandrelMesh.castShadow = true;
  spandrelMesh.receiveShadow = true;
  upperStructure.add(spandrelMesh);

  // 7. Defensive Machicolation Slits Arcade
  const slitRowGroup = new THREE.Group();
  slitRowGroup.name = 'machicolation_slits_row';
  const slitCount = 5;
  const slitSpacing = 1.1;

  for (let s = 0; s < slitCount; s++) {
    const sx = (s - 2) * slitSpacing;
    const sGeom = new THREE.BoxGeometry(0.35, 1.2, pierDepth + 0.1);
    const sMesh = new THREE.Mesh(sGeom, materials.fatimidDarkStone);
    sMesh.position.set(sx, 11.2, entranceZ - pierDepth / 2);
    slitRowGroup.add(sMesh);
  }
  upperStructure.add(slitRowGroup);

  // 8. High Open Machicolation Bridge Arch (Saqqatah / السقاطة)
  // Framed open arch linking bastions high above entrance through which sky is visible
  const upperArchGroup = new THREE.Group();
  upperArchGroup.name = 'upper_machicolation_gallery_arch';
  upperArchGroup.userData = {
    nameEn: 'Upper Machicolation Bridge Arch (Saqqatah)',
    nameAr: 'العقد العلوي لسقاطة الدفاع بين البرجين',
    description: 'Monumental spanning arch linking the two bastions high above the entrance.',
  };

  const upperArchY = 12.4;
  const upperArchSpan = passageWidth + 0.6;
  const upperArchDepth = 1.6;

  const pillarW = (towerDistance - upperArchSpan) / 2;
  const pillarH = 4.2;
  const pillarGeom = new THREE.BoxGeometry(pillarW, pillarH, upperArchDepth);

  const leftPillar = new THREE.Mesh(pillarGeom, materials.fatimidStone);
  leftPillar.position.set(-halfTowerDist + pillarW / 2, upperArchY + pillarH / 2, entranceZ - 1.2);
  leftPillar.castShadow = true;
  upperArchGroup.add(leftPillar);

  const rightPillar = new THREE.Mesh(pillarGeom, materials.fatimidStone);
  rightPillar.position.set(halfTowerDist - pillarW / 2, upperArchY + pillarH / 2, entranceZ - 1.2);
  rightPillar.castShadow = true;
  upperArchGroup.add(rightPillar);

  // Upper arch curve (open semicircular arch framing the sky!)
  const upperArchGeom = new THREE.CylinderGeometry(
    upperArchSpan / 2 + 0.55,
    upperArchSpan / 2 + 0.55,
    upperArchDepth,
    28,
    1,
    true,
    0,
    Math.PI
  );
  upperArchGeom.rotateZ(Math.PI / 2);
  upperArchGeom.rotateY(Math.PI / 2);
  const upperArchMesh = new THREE.Mesh(upperArchGeom, materials.fatimidDarkStone);
  upperArchMesh.position.set(0, upperArchY + 3.8, entranceZ - 1.2);
  upperArchMesh.castShadow = true;
  upperArchGroup.add(upperArchMesh);

  upperStructure.add(upperArchGroup);

  // 9. Central Parapet & Stepped Merlons between Towers
  const parapetY = 17.5;
  const parapetMesh = new THREE.Mesh(
    new THREE.BoxGeometry(towerDistance - 0.8, 0.65, 1.6),
    materials.fatimidDarkStone
  );
  parapetMesh.name = 'central_curtain_parapet';
  parapetMesh.position.set(0, parapetY, entranceZ - 1.2);
  parapetMesh.castShadow = true;
  upperStructure.add(parapetMesh);

  const centralMerlonCount = 7;
  const cMerlonW = 0.72;
  const cMerlonH = 1.35;
  const cSpacing = (towerDistance - 1.8) / centralMerlonCount;

  for (let cm = 0; cm < centralMerlonCount; cm++) {
    const cmX = -((towerDistance - 1.8) / 2) + (cm + 0.5) * cSpacing;
    const cMerlon = new THREE.Group();
    const cmBase = new THREE.Mesh(
      new THREE.BoxGeometry(cMerlonW, cMerlonH * 0.7, 0.45),
      materials.fatimidStone
    );
    cmBase.position.y = (cMerlonH * 0.7) / 2;
    cmBase.castShadow = true;
    cMerlon.add(cmBase);

    const cmCap = new THREE.Mesh(
      new THREE.CylinderGeometry(cMerlonW * 0.44, cMerlonW * 0.44, 0.45, 14, 1, false, 0, Math.PI),
      materials.fatimidStone
    );
    cmCap.rotateZ(Math.PI / 2);
    cmCap.rotateY(Math.PI / 2);
    cmCap.position.y = cMerlonH * 0.7;
    cmCap.castShadow = true;
    cMerlon.add(cmCap);

    cMerlon.position.set(cmX, parapetY + 0.325, entranceZ - 1.2);
    cMerlon.name = `central_merlon_${cm}`;
    upperStructure.add(cMerlon);
  }

  // 10. Continuous Barrel Vault Ceiling of the Passage
  const passageVault = new THREE.Group();
  passageVault.name = 'gate_passage_vault';
  passageVault.userData = {
    id: 'passage_vault',
    nameEn: 'Fortified Gate Passage & Vault',
    nameAr: 'ممر البوابة المقبى',
    descriptionEn: 'Deep vaulted tunnel connecting the outer southern approach to al-Mu\'izz street inside Cairo.',
    descriptionAr: 'الممر المقبى العميق الممتد من البوابة الجنوبية إلى شارع المعز لدين الله الفاطمي.',
  };

  const vaultGeom = new THREE.CylinderGeometry(
    halfPassage,
    halfPassage,
    passageDepth,
    32,
    1,
    true,
    0,
    Math.PI
  );
  vaultGeom.rotateZ(Math.PI / 2);
  vaultGeom.rotateY(Math.PI / 2);
  const vaultMesh = new THREE.Mesh(vaultGeom, materials.fatimidDarkStone);
  vaultMesh.position.set(0, 4.8, passageCenterZ - 0.5);
  vaultMesh.scale.set(1, 1.14, 1);
  vaultMesh.castShadow = true;
  passageVault.add(vaultMesh);

  // Upper flank walls above plan cut
  const upperFlankH = 3.6;
  const upperLeftFlank = new THREE.Mesh(
    new THREE.BoxGeometry(flankWallThickness, upperFlankH, passageDepth),
    materials.fatimidStone
  );
  upperLeftFlank.position.set(-halfPassage - flankWallThickness / 2, planCutHeight + upperFlankH / 2, passageCenterZ);
  passageVault.add(upperLeftFlank);

  const upperRightFlank = new THREE.Mesh(
    new THREE.BoxGeometry(flankWallThickness, upperFlankH, passageDepth),
    materials.fatimidStone
  );
  upperRightFlank.position.set(halfPassage + flankWallThickness / 2, planCutHeight + upperFlankH / 2, passageCenterZ);
  passageVault.add(upperRightFlank);

  upperStructure.add(passageVault);

  // Add lower and upper structures to portal group
  portalGroup.add(lowerStructure);
  portalGroup.add(upperStructure);

  const setSectionCut = (enabled: boolean) => {
    upperStructure.visible = !enabled;
  };

  return {
    group: portalGroup,
    lowerStructure,
    upperStructure,
    setSectionCut,
  };
}
