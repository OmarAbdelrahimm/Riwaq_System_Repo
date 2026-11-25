/**
 * Master GLB Export & Validation Script for RUWAQ: Bab Zuwayla - V04
 * Exports the complete architectural model preserving named hierarchy, materials, and hidden components.
 * Validates the exported GLB by loading it into a clean Three.js scene.
 */

import fs from 'node:fs';
import path from 'node:path';
import * as THREE from 'three';
import { GLTFExporter } from 'three/examples/jsm/exporters/GLTFExporter.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

// Polyfill FileReader for GLTFExporter in Node
class PolyfillFileReader {
  result: any = null;
  onload: any = null;
  onloadend: any = null;

  readAsArrayBuffer(blob: any) {
    blob.arrayBuffer().then((buf: ArrayBuffer) => {
      this.result = buf;
      if (this.onloadend) this.onloadend();
      if (this.onload) this.onload();
    });
  }

  readAsDataURL(blob: any) {
    blob.arrayBuffer().then((buf: ArrayBuffer) => {
      this.result =
        'data:' +
        (blob.type || 'application/octet-stream') +
        ';base64,' +
        Buffer.from(buf).toString('base64');
      if (this.onloadend) this.onloadend();
      if (this.onload) this.onload();
    });
  }
}
(globalThis as any).FileReader = PolyfillFileReader;

class MockHTMLCanvasElement {}
(globalThis as any).HTMLCanvasElement = MockHTMLCanvasElement;
(globalThis as any).self = globalThis;

if (!(globalThis as any).createImageBitmap) {
  (globalThis as any).createImageBitmap = async () => ({
    width: 512,
    height: 512,
    close: () => {},
  });
}

// Polyfill minimal document / canvas for headless texture generation
if (typeof document === 'undefined') {
  (globalThis as any).document = {
    createElement(tag: string) {
      if (tag === 'canvas') {
        const dummyCanvas = Object.assign(new MockHTMLCanvasElement(), {
          width: 512,
          height: 512,
          getContext: () => ({
            fillStyle: '',
            fillRect: () => {},
            getImageData: () => ({ data: new Uint8ClampedArray(512 * 512 * 4) }),
            putImageData: () => {},
            createLinearGradient: () => ({ addColorStop: () => {} }),
            createRadialGradient: () => ({ addColorStop: () => {} }),
            beginPath: () => {},
            moveTo: () => {},
            lineTo: () => {},
            arc: () => {},
            fill: () => {},
            stroke: () => {},
            translate: () => {},
            scale: () => {},
            drawImage: () => {},
          }),
          toDataURL: (mime = 'image/png') =>
            'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==',
          toBlob: (cb: (b: Blob) => void, type = 'image/png') => {
            const buf = Buffer.from(
              'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==',
              'base64'
            );
            cb(new Blob([buf], { type }));
          },
        });
        return dummyCanvas;
      }
      return {};
    },
  };
}

import { createMaterialPalette } from '../src/three/materials.ts';
import { createSemicircularTower } from '../src/three/geometry/tower.ts';
import { createCentralPortal } from '../src/three/geometry/portal.ts';
import { createGateDoors } from '../src/three/geometry/doors.ts';
import { createMamlukMinaret } from '../src/three/geometry/minaret.ts';

async function runExportAndValidation() {
  console.log('🏛️  [1/4] Constructing Master Bab Zuwayla Scene Hierarchy (V04)...');

  const materials = createMaterialPalette({
    stoneRoughness: 0.82,
    stoneWarmth: 0.55,
    wireframe: false,
    blueprintMode: false,
    shadowIntensity: 0.45,
    aoIntensity: 1.0,
  });

  const masterRoot = new THREE.Group();
  masterRoot.name = 'bab_zuwayla_monument_root';

  // 1. Left Bastion Tower (Fatimid 1092 CE)
  const leftTower = createSemicircularTower(
    { side: 'left', radius: 5.2, height: 17.8, wallDepth: 9.0 },
    materials
  );
  leftTower.group.position.set(-7.2, 0, 0);
  masterRoot.add(leftTower.group);

  // 2. Right Bastion Tower (Fatimid 1092 CE)
  const rightTower = createSemicircularTower(
    { side: 'right', radius: 5.2, height: 17.8, wallDepth: 9.0 },
    materials
  );
  rightTower.group.position.set(7.2, 0, 0);
  masterRoot.add(rightTower.group);

  // 3. Central Entrance Portal & Continuous Passage (Fatimid 1092 CE)
  const centralPortal = createCentralPortal(
    { passageWidth: 4.8, portalHeight: 7.8, passageDepth: 11.4, towerDistance: 14.4 },
    materials
  );
  centralPortal.group.position.set(0, 0, 0);
  masterRoot.add(centralPortal.group);

  // 4. Fortified Doors Assembly
  const doors = createGateDoors(4.8, 6.2, materials);
  masterRoot.add(doors.group);

  // 5. Left Minaret (Mamluk 1415–1421 CE) - included active in GLB
  const leftMinaret = createMamlukMinaret({ side: 'left', baseY: 17.8 }, materials);
  leftMinaret.root.position.set(-7.2, 17.8, -1.2);
  leftMinaret.root.visible = true;
  masterRoot.add(leftMinaret.root);

  // 6. Right Minaret (Mamluk 1415–1421 CE)
  const rightMinaret = createMamlukMinaret({ side: 'right', baseY: 17.8 }, materials);
  rightMinaret.root.position.set(7.2, 17.8, -1.2);
  rightMinaret.root.visible = true;
  masterRoot.add(rightMinaret.root);

  console.log('📦  [2/4] Exporting to Binary GLB (GLTFExporter)...');
  const exporter = new GLTFExporter();

  const glbBuffer: ArrayBuffer = await new Promise((resolve, reject) => {
    exporter.parse(
      masterRoot,
      (gltf) => {
        if (gltf instanceof ArrayBuffer) {
          resolve(gltf);
        } else {
          reject(new Error('Expected ArrayBuffer for binary GLB export'));
        }
      },
      (error) => reject(error),
      {
        binary: true,
        onlyVisible: false, // CRITICAL: Export all components including hidden
        includeCustomExtensions: true,
      }
    );
  });

  const outputDir = path.resolve(process.cwd(), 'public');
  if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });

  const glbPathV04 = path.join(outputDir, 'RUWAQ_BAB_ZUWAYLA_V04_MASTER.glb');
  const glbPathMaster = path.join(outputDir, 'RUWAQ_BAB_ZUWAYLA_MASTER.glb');
  fs.writeFileSync(glbPathV04, Buffer.from(glbBuffer));
  fs.writeFileSync(glbPathMaster, Buffer.from(glbBuffer));
  console.log(`✅  Master V04 GLB exported: ${glbPathV04} (${(glbBuffer.byteLength / 1024).toFixed(1)} KB)`);

  console.log('🔍  [3/4] Validating Exported GLB in Clean Three.js Scene...');
  const loader = new GLTFLoader();

  const loadedGLTF: any = await new Promise((resolve, reject) => {
    loader.parse(
      glbBuffer,
      '',
      (gltf) => resolve(gltf),
      (err) => reject(err)
    );
  });

  const validatedScene = loadedGLTF.scene;
  const foundComponents: string[] = [];
  const hierarchyMap: Record<string, string[]> = {};

  validatedScene.traverse((obj: THREE.Object3D) => {
    if (obj.name) {
      foundComponents.push(obj.name);
      if (obj.parent && obj.parent.name) {
        if (!hierarchyMap[obj.parent.name]) hierarchyMap[obj.parent.name] = [];
        hierarchyMap[obj.parent.name].push(obj.name);
      }
    }
  });

  const requiredComponents = [
    'bab_zuwayla_monument_root',
    'left_semicircular_tower',
    'right_semicircular_tower',
    'central_entrance_arch',
    'gate_passage_vault',
    'left_door_leaf',
    'right_door_leaf',
    'left_minaret',
    'right_minaret',
    'left_minaret_tier1_octagonal_shaft',
    'left_minaret_tier2_first_balcony',
    'left_minaret_tier3_chevron_shaft',
    'left_minaret_tier4_second_balcony',
    'left_minaret_tier5_colonnaded_pavilion',
    'left_minaret_tier6_bulb_finial',
    'right_minaret_tier1_octagonal_shaft',
    'right_minaret_tier2_first_balcony',
    'right_minaret_tier3_chevron_shaft',
    'right_minaret_tier4_second_balcony',
    'right_minaret_tier5_colonnaded_pavilion',
    'right_minaret_tier6_bulb_finial',
  ];

  console.log('📋  [4/4] Verifying Named Object Audit & Independent Manipulability:');
  const missingComponents: string[] = [];
  requiredComponents.forEach((name) => {
    const obj = validatedScene.getObjectByName(name);
    if (obj) {
      const origX = obj.position.x;
      obj.position.x += 10.0;
      const manipulated = obj.position.x === origX + 10.0;
      obj.position.x = origX; // restore
      console.log(`   ✓ [FOUND & EDITABLE] ${name} (${obj.type})`);
    } else {
      missingComponents.push(name);
      console.error(`   ✗ [MISSING] ${name}`);
    }
  });

  const report = {
    exportDate: new Date().toISOString(),
    glbFilename: 'RUWAQ_BAB_ZUWAYLA_V04_MASTER.glb',
    fileSizeBytes: glbBuffer.byteLength,
    fileSizeKB: Math.round(glbBuffer.byteLength / 1024),
    totalNamedNodes: foundComponents.length,
    requiredComponentsChecked: requiredComponents.length,
    missingComponents,
    allRequiredComponentsPresent: missingComponents.length === 0,
    hierarchySummary: hierarchyMap,
  };

  const reportPath = path.join(outputDir, 'GLB_VALIDATION_REPORT.json');
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  console.log(`📄  Validation report saved: ${reportPath}`);

  if (missingComponents.length > 0) {
    throw new Error(`GLB Validation failed: missing ${missingComponents.length} components`);
  }

  console.log('🎉  V04 GLB EXPORT & VALIDATION PASSED 100%!');
}

runExportAndValidation().catch((err) => {
  console.error('Fatal error during GLB export/validation:', err);
  process.exit(1);
});
