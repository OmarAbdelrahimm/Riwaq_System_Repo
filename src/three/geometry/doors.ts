/**
 * Fortified Colossal Gate Doors & Pivot Points
 * Based directly on reference photograph image_191b72fb.png
 * Heavy cedar wood clad with horizontal iron bands and hemispherical iron rivets
 */

import * as THREE from 'three';
import { MaterialPalette } from '../materials.ts';

export interface GateDoorsResult {
  group: THREE.Group;
  leftPivot: THREE.Group;
  rightPivot: THREE.Group;
  setDoorAngle: (angleRadians: number) => void;
}

export function createGateDoors(
  passageWidth = 5.2,
  doorHeight = 6.8,
  materials: MaterialPalette
): GateDoorsResult {
  const doorsGroup = new THREE.Group();
  doorsGroup.name = 'fortified_gate_doors_assembly';
  doorsGroup.userData = {
    id: 'gate_doors',
    nameEn: 'Iron-Studded Fortified Gate Leaves',
    nameAr: 'مصراعا البوابة الفاطمية المصفحة بالحديد',
    era: 'Fatimid (1092 CE / 485 AH)',
    descriptionEn:
      'Massive timber leaves clad with heavy wrought iron plates studded with hundreds of hemispherical bolts, hung on massive stone pivot sockets.',
    descriptionAr:
      'مصراعان خشبيان ضخمان مصفحان بصفائح الحديد المشغول ومثبتان بمئات المسامير القبابية الحديدية الضخمة، يدوران على مفاصل حجرية عملاقة.',
    certainty: 'Historical Record & In Situ Surviving Original Door',
  };

  const leafWidth = (passageWidth / 2) + 0.15; // slight overlap at center
  const leafThickness = 0.28;
  const jambZ = -1.2; // recessed inside the portal

  // 1. Left Door Pivot Assembly
  const leftPivot = new THREE.Group();
  leftPivot.name = 'left_door_pivot';
  leftPivot.position.set(-passageWidth / 2, 0, jambZ);

  // Left leaf mesh (offset so pivot edge is at x=0 of the pivot group)
  const leftLeafGeom = new THREE.BoxGeometry(leafWidth, doorHeight, leafThickness);
  // Shift center so (0,0,0) of geometry is at the hinge edge
  leftLeafGeom.translate(leafWidth / 2, doorHeight / 2, 0);

  const leftLeafMesh = new THREE.Mesh(leftLeafGeom, materials.doorStuddedIron);
  leftLeafMesh.name = 'left_door_leaf';
  leftLeafMesh.castShadow = true;
  leftLeafMesh.receiveShadow = true;
  leftPivot.add(leftLeafMesh);

  // Hinge pintle pin socket in stone
  const pintleGeom = new THREE.CylinderGeometry(0.12, 0.12, 0.45, 16);
  const leftPintleTop = new THREE.Mesh(pintleGeom, materials.doorTimberEdge);
  leftPintleTop.position.set(0, doorHeight + 0.1, 0);
  leftPivot.add(leftPintleTop);

  const leftPintleBottom = new THREE.Mesh(pintleGeom, materials.doorTimberEdge);
  leftPintleBottom.position.set(0, 0.2, 0);
  leftPivot.add(leftPintleBottom);

  doorsGroup.add(leftPivot);

  // 2. Right Door Pivot Assembly
  const rightPivot = new THREE.Group();
  rightPivot.name = 'right_door_pivot';
  rightPivot.position.set(passageWidth / 2, 0, jambZ);

  // Right leaf mesh (offset towards negative X from the right hinge edge)
  const rightLeafGeom = new THREE.BoxGeometry(leafWidth, doorHeight, leafThickness);
  rightLeafGeom.translate(-leafWidth / 2, doorHeight / 2, 0);

  const rightLeafMesh = new THREE.Mesh(rightLeafGeom, materials.doorStuddedIron);
  rightLeafMesh.name = 'right_door_leaf';
  rightLeafMesh.castShadow = true;
  rightLeafMesh.receiveShadow = true;
  rightPivot.add(rightLeafMesh);

  const rightPintleTop = new THREE.Mesh(pintleGeom, materials.doorTimberEdge);
  rightPintleTop.position.set(0, doorHeight + 0.1, 0);
  rightPivot.add(rightPintleTop);

  const rightPintleBottom = new THREE.Mesh(pintleGeom, materials.doorTimberEdge);
  rightPintleBottom.position.set(0, 0.2, 0);
  rightPivot.add(rightPintleBottom);

  doorsGroup.add(rightPivot);

  // Function to set rotation angle for both leaves (0 rad = closed, ~1.4 rad = opened inwards)
  const setDoorAngle = (angleRad: number) => {
    // Open inwards towards the city (negative Z)
    leftPivot.rotation.y = -angleRad;
    rightPivot.rotation.y = angleRad;
  };

  // Default initial angle: partially open (35 degrees) to show depth and internal passage
  setDoorAngle(THREE.MathUtils.degToRad(35));

  return {
    group: doorsGroup,
    leftPivot,
    rightPivot,
    setDoorAngle,
  };
}
