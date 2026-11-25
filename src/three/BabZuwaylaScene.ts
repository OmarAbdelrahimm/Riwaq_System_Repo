/**
 * Bab Zuwayla 3D Architectural Scene Engine - V04
 * Adheres to Three.js PBR standards, stable dual camera projection,
 * quaternion-based orientation interpolation, and architectural plan section cut.
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';

import {
  ViewerState,
  ComponentVisibility,
  MaterialSettings,
  AnnotationItem,
} from '../types.ts';
import {
  createMaterialPalette,
  updateMaterialsWithSettings,
  MaterialPalette,
} from './materials.ts';
import { createSemicircularTower, TowerResult } from './geometry/tower.ts';
import { createCentralPortal, PortalResult } from './geometry/portal.ts';
import { createGateDoors, GateDoorsResult } from './geometry/doors.ts';
import { createMamlukMinaret, MinaretTiers } from './geometry/minaret.ts';
import { BAB_ZUWAYLA_ANNOTATIONS } from './geometry/annotations.ts';

export interface SceneCallbacks {
  onSelectComponent?: (info: {
    id: string;
    nameEn: string;
    nameAr: string;
    descriptionEn?: string;
    descriptionAr?: string;
    era?: string;
    certainty?: string;
  } | null) => void;
  onSelectAnnotation?: (annotation: AnnotationItem | null) => void;
}

export class BabZuwaylaScene {
  private container: HTMLElement;
  private renderer: THREE.WebGLRenderer;
  private scene: THREE.Scene;
  private animFrameId: number = 0;
  private isDisposed: boolean = false;
  private isSoftwareGl: boolean = false;

  // Cameras & Controls
  public perspectiveCamera: THREE.PerspectiveCamera;
  public orthographicCamera: THREE.OrthographicCamera;
  public activeCamera: THREE.Camera;
  public controls: OrbitControls;

  // Camera animation interpolation targets
  private camCurrentPos = new THREE.Vector3(-26, 18, 36);
  private camTargetPos = new THREE.Vector3(-26, 18, 36);
  private camCurrentLook = new THREE.Vector3(0, 14, -1.0);
  private camTargetLook = new THREE.Vector3(0, 14, -1.0);
  private camTargetUp = new THREE.Vector3(0, 1, 0);
  private targetOrthoZoom: number = 16;
  private currentOrthoZoom: number = 16;
  private cameraTransitionSpeed: number = 4.5; // damping factor

  // Materials & Geometry
  private materials: MaterialPalette;
  private modelRoot: THREE.Group;
  private leftTowerObj: TowerResult;
  private rightTowerObj: TowerResult;
  private portalObj: PortalResult;
  private doorsAssembly: GateDoorsResult;
  private leftMinaret: MinaretTiers;
  private rightMinaret: MinaretTiers;
  private groundApron: THREE.Mesh;
  private blueprintFloorGrid: THREE.Mesh;

  // Annotations in 3D
  private annotationGroup: THREE.Group;
  private annotationSprites: Map<string, THREE.Sprite> = new Map();

  // Raycasting & Interaction
  private raycaster = new THREE.Raycaster();
  private mouse = new THREE.Vector2();
  private callbacks: SceneCallbacks;

  // Active configuration
  public currentState: ViewerState = 'FULLY_ASSEMBLED';
  public explodedProgress: number = 0;
  public minaretElevation: number = 0;
  public towerSeparation: number = 0;
  public doorAngleDeg: number = 35;
  public minaretsVisible: boolean = true;
  public isPlanCutActive: boolean = false;
  private isUserInteracting: boolean = false;

  // Default component visibility
  public visibility: ComponentVisibility = {
    leftTower: true,
    rightTower: true,
    centralArch: true,
    gatePassage: true,
    leftDoor: true,
    rightDoor: true,
    leftMinaret: true,
    rightMinaret: true,
    crenellations: true,
    ground: true,
  };

  constructor(container: HTMLElement, callbacks: SceneCallbacks = {}) {
    this.container = container;
    this.callbacks = callbacks;

    // 1. Detect Software WebGL
    this.isSoftwareGl = (() => {
      const gl = document.createElement('canvas').getContext('webgl2');
      if (!gl) return true;
      const ext = gl.getExtension('WEBGL_debug_renderer_info');
      const param = ext ? ext.UNMASKED_RENDERER_WEBGL : gl.RENDERER;
      const gpu = String(gl.getParameter(param));
      gl.getExtension('WEBGL_lose_context')?.loseContext();
      return /SwiftShader|llvmpipe|softpipe|Software|Basic Render/i.test(gpu);
    })();

    // 2. Initialize Three.js WebGLRenderer
    this.renderer = new THREE.WebGLRenderer({
      antialias: !this.isSoftwareGl,
      powerPreference: 'high-performance',
      preserveDrawingBuffer: true,
    });
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.12;
    this.renderer.setPixelRatio(
      this.isSoftwareGl ? 1 : Math.min(window.devicePixelRatio, 2)
    );
    this.renderer.shadowMap.enabled = !this.isSoftwareGl;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    this.container.appendChild(this.renderer.domElement);

    // 3. Scene & Studio PBR Environment
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color('#F3EBDB'); // RUWAQ Cream
    this.scene.fog = new THREE.FogExp2('#F3EBDB', 0.0075);

    const pmremGenerator = new THREE.PMREMGenerator(this.renderer);
    this.scene.environment = pmremGenerator.fromScene(
      new RoomEnvironment(),
      0.04
    ).texture;
    pmremGenerator.dispose();

    // 4. Cameras & OrbitControls
    const aspect = this.container.clientWidth / this.container.clientHeight;
    this.perspectiveCamera = new THREE.PerspectiveCamera(40, aspect, 0.5, 450);
    this.perspectiveCamera.position.copy(this.camCurrentPos);

    const frustumSize = 42;
    this.orthographicCamera = new THREE.OrthographicCamera(
      (-frustumSize * aspect) / 2,
      (frustumSize * aspect) / 2,
      frustumSize / 2,
      -frustumSize / 2,
      0.1,
      600
    );
    this.orthographicCamera.zoom = this.currentOrthoZoom;
    this.orthographicCamera.position.copy(this.camCurrentPos);

    this.activeCamera = this.perspectiveCamera;

    this.controls = new OrbitControls(
      this.perspectiveCamera,
      this.renderer.domElement
    );
    this.controls.enableDamping = !this.isSoftwareGl;
    this.controls.dampingFactor = 0.08;
    this.controls.maxPolarAngle = Math.PI / 2 + 0.02;
    this.controls.minDistance = 6;
    this.controls.maxDistance = 140;
    this.controls.target.copy(this.camCurrentLook);

    this.controls.addEventListener('start', () => {
      this.isUserInteracting = true;
    });

    // 5. Lighting Rig
    this.setupLighting();

    // 6. Materials
    const defaultMaterialSettings: MaterialSettings = {
      stoneRoughness: 0.82,
      stoneWarmth: 0.55,
      wireframe: false,
      blueprintMode: false,
      shadowIntensity: 0.45,
      aoIntensity: 1.0,
    };
    this.materials = createMaterialPalette(defaultMaterialSettings);

    // 7. Assemble Architectural Model
    this.modelRoot = new THREE.Group();
    this.modelRoot.name = 'bab_zuwayla_monument_root';

    // Left Semicircular Tower (West Bastion) at x = -7.2
    this.leftTowerObj = createSemicircularTower(
      { side: 'left', radius: 5.2, height: 17.8, wallDepth: 9.0 },
      this.materials
    );
    this.leftTowerObj.group.position.set(-7.2, 0, 0);
    this.modelRoot.add(this.leftTowerObj.group);

    // Right Semicircular Tower (East Bastion) at x = +7.2
    this.rightTowerObj = createSemicircularTower(
      { side: 'right', radius: 5.2, height: 17.8, wallDepth: 9.0 },
      this.materials
    );
    this.rightTowerObj.group.position.set(7.2, 0, 0);
    this.modelRoot.add(this.rightTowerObj.group);

    // Central Entrance Arch & Continuous 11.4m Deep Passage
    this.portalObj = createCentralPortal(
      { passageWidth: 4.8, portalHeight: 7.8, passageDepth: 11.4, towerDistance: 14.4 },
      this.materials
    );
    this.portalObj.group.position.set(0, 0, 0);
    this.modelRoot.add(this.portalObj.group);

    // Fortified Studded Doors (Inside Central Archway)
    this.doorsAssembly = createGateDoors(4.8, 6.2, this.materials);
    this.modelRoot.add(this.doorsAssembly.group);

    // Left Minaret (West Tower Addition)
    this.leftMinaret = createMamlukMinaret({ side: 'left', baseY: 17.8 }, this.materials);
    this.leftMinaret.root.position.set(-7.2, 17.8, -1.2);
    this.modelRoot.add(this.leftMinaret.root);

    // Right Minaret (East Tower Addition)
    this.rightMinaret = createMamlukMinaret({ side: 'right', baseY: 17.8 }, this.materials);
    this.rightMinaret.root.position.set(7.2, 17.8, -1.2);
    this.modelRoot.add(this.rightMinaret.root);

    // Ground Paving / Historic Cairo Apron
    const groundGeom = new THREE.PlaneGeometry(90, 90);
    groundGeom.rotateX(-Math.PI / 2);
    this.groundApron = new THREE.Mesh(groundGeom, this.materials.groundPaving);
    this.groundApron.name = 'historic_cairo_ground_apron';
    this.groundApron.position.y = -0.01;
    this.groundApron.receiveShadow = true;
    this.modelRoot.add(this.groundApron);

    // Blueprint floor drafting grid overlay
    const gridGeom = new THREE.PlaneGeometry(60, 60);
    gridGeom.rotateX(-Math.PI / 2);
    this.blueprintFloorGrid = new THREE.Mesh(gridGeom, this.materials.blueprintGrid);
    this.blueprintFloorGrid.name = 'architectural_blueprint_grid';
    this.blueprintFloorGrid.position.y = 0.01;
    this.modelRoot.add(this.blueprintFloorGrid);

    this.scene.add(this.modelRoot);

    // 8. 3D Annotation Anchors
    this.annotationGroup = new THREE.Group();
    this.annotationGroup.name = 'documentary_annotations_layer';
    this.setupAnnotations();
    this.scene.add(this.annotationGroup);

    // 9. Resize & Event Listeners
    this.handleResize = this.handleResize.bind(this);
    this.handlePointerDown = this.handlePointerDown.bind(this);
    window.addEventListener('resize', this.handleResize);
    this.renderer.domElement.addEventListener('pointerdown', this.handlePointerDown);

    this.handleResize();

    // 10. Start Animation Loop
    this.tick = this.tick.bind(this);
    this.tick();
  }

  private setupLighting() {
    const keyLight = new THREE.DirectionalLight('#fff2d4', 2.3);
    keyLight.position.set(24, 42, 28);
    keyLight.castShadow = !this.isSoftwareGl;
    keyLight.shadow.mapSize.width = 2048;
    keyLight.shadow.mapSize.height = 2048;
    keyLight.shadow.bias = -0.0003;
    keyLight.shadow.normalBias = 0.02;

    const d = 32;
    keyLight.shadow.camera.left = -d;
    keyLight.shadow.camera.right = d;
    keyLight.shadow.camera.top = d;
    keyLight.shadow.camera.bottom = -d;
    keyLight.shadow.camera.near = 0.5;
    keyLight.shadow.camera.far = 140;
    this.scene.add(keyLight);

    const hemiLight = new THREE.HemisphereLight('#fbf7ed', '#8e8271', 1.05);
    this.scene.add(hemiLight);

    const rimLight = new THREE.DirectionalLight('#e6dcce', 0.9);
    rimLight.position.set(-30, 28, -25);
    this.scene.add(rimLight);
  }

  private setupAnnotations() {
    BAB_ZUWAYLA_ANNOTATIONS.forEach((item) => {
      const canvas = document.createElement('canvas');
      canvas.width = 128;
      canvas.height = 128;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.strokeStyle = '#A98A4B';
        ctx.lineWidth = 6;
        ctx.fillStyle = '#1C1B19';
        ctx.beginPath();
        ctx.arc(64, 64, 52, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = '#A98A4B';
        ctx.beginPath();
        ctx.arc(64, 64, 26, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = '#F3EBDB';
        ctx.beginPath();
        ctx.arc(64, 64, 10, 0, Math.PI * 2);
        ctx.fill();
      }

      const texture = new THREE.CanvasTexture(canvas);
      const spriteMat = new THREE.SpriteMaterial({
        map: texture,
        transparent: true,
        depthTest: false,
      });
      const sprite = new THREE.Sprite(spriteMat);
      sprite.position.set(item.position[0], item.position[1], item.position[2]);
      sprite.scale.set(1.5, 1.5, 1.5);
      sprite.userData = { annotation: item };

      this.annotationSprites.set(item.id, sprite);
      this.annotationGroup.add(sprite);
    });
  }

  /**
   * Set Architectural Section Cut (Horizontal plan cut revealing interior & open passage)
   */
  public setPlanCut(enabled: boolean) {
    this.isPlanCutActive = enabled;
    this.leftTowerObj.setSectionCut(enabled);
    this.rightTowerObj.setSectionCut(enabled);
    this.portalObj.setSectionCut(enabled);
  }

  // Set camera view according to architectural requirements
  public setState(state: ViewerState) {
    this.currentState = state;
    this.isUserInteracting = false;

    // Reset temporary explosion if switching away
    if (state !== 'EXPLODED_VIEW') {
      this.setExplodedProgress(0);
    }

    switch (state) {
      case 'FATIMID_ORIGINAL':
        // Original Fatimid gate in 1092 CE (NO minarets)
        this.setPlanCut(false);
        this.setMinaretsVisible(false);
        this.switchCameraMode('perspective');
        this.camTargetPos.set(0, 12, 38);
        this.camTargetLook.set(0, 11, 0);
        this.camTargetUp.set(0, 1, 0);
        this.setDoorAngle(35);
        break;

      case 'TOP_PLAN':
        // Orthographic plan view with Section Cut active (showing open passage & tower footprints)
        this.setMinaretsVisible(false);
        this.setPlanCut(true);
        this.switchCameraMode('orthographic');
        this.targetOrthoZoom = 17;
        this.camTargetPos.set(0, 70, -3.3);
        this.camTargetLook.set(0, 0, -3.3);
        this.camTargetUp.set(0, 0, -1); // North points up on screen
        this.setDoorAngle(35);
        break;

      case 'SIDE_ELEVATION':
        // True side orthographic projection - upright vertical geometry
        this.setPlanCut(false);
        this.setMinaretsVisible(true);
        this.switchCameraMode('orthographic');
        this.targetOrthoZoom = 14.5;
        this.camTargetPos.set(-70, 16, -3.3);
        this.camTargetLook.set(0, 16, -3.3);
        this.camTargetUp.set(0, 1, 0);
        break;

      case 'FRONT_ELEVATION':
        // Front orthographic elevation view (Original 1092 CE gate without minarets)
        this.setPlanCut(false);
        this.setMinaretsVisible(false);
        this.switchCameraMode('orthographic');
        this.targetOrthoZoom = 14;
        this.camTargetPos.set(0, 14, 70);
        this.camTargetLook.set(0, 14, 0);
        this.camTargetUp.set(0, 1, 0);
        this.setDoorAngle(35);
        break;

      case 'PERSPECTIVE_3Q':
        // Three-quarter documentary camera angle with minarets
        this.setPlanCut(false);
        this.setMinaretsVisible(true);
        this.switchCameraMode('perspective');
        this.camTargetPos.set(-28, 20, 36);
        this.camTargetLook.set(0, 15, -1.0);
        this.camTargetUp.set(0, 1, 0);
        break;

      case 'MAMLUK_ADDITIONS':
        // Highlighting the 1415–1421 CE minaret additions
        this.setPlanCut(false);
        this.setMinaretsVisible(true);
        this.switchCameraMode('perspective');
        this.camTargetPos.set(22, 28, 32);
        this.camTargetLook.set(0, 22, 0);
        this.camTargetUp.set(0, 1, 0);
        this.setMinaretElevation(0);
        break;

      case 'EXPLODED_VIEW':
        // Separated architectural components
        this.setPlanCut(false);
        this.setMinaretsVisible(true);
        this.switchCameraMode('perspective');
        this.camTargetPos.set(-34, 24, 38);
        this.camTargetLook.set(0, 18, 0);
        this.camTargetUp.set(0, 1, 0);
        this.setExplodedProgress(0.75);
        this.setDoorAngle(70);
        break;

      case 'FULLY_ASSEMBLED':
      default:
        this.setPlanCut(false);
        this.setMinaretsVisible(true);
        this.switchCameraMode('perspective');
        this.camTargetPos.set(-26, 18, 36);
        this.camTargetLook.set(0, 15, -1.0);
        this.camTargetUp.set(0, 1, 0);
        this.setExplodedProgress(0);
        this.setDoorAngle(35);
        break;
    }
  }

  public switchCameraMode(mode: 'perspective' | 'orthographic') {
    const isOrtho = mode === 'orthographic';
    const oldCam = this.activeCamera;
    const newCam = isOrtho ? this.orthographicCamera : this.perspectiveCamera;

    if (oldCam !== newCam) {
      newCam.position.copy(oldCam.position);
      newCam.up.copy(oldCam.up);
      this.activeCamera = newCam;
      this.controls.object = newCam;
      this.controls.update();
    }
  }

  /**
   * Continuous animation driver for Remotion & timeline scrubber (V04 6-Act sequence)
   */
  public seekFrame(frame: number, totalFrames = 300) {
    const progress = Math.min(1.0, Math.max(0.0, frame / totalFrames));

    // Frames 000–059 (0.00 - 0.20): Top architectural plan
    // Frames 060–119 (0.20 - 0.40): Controlled transition into side elevation
    // Frames 120–179 (0.40 - 0.60): Transition into original front elevation without minarets
    // Frames 180–239 (0.60 - 0.80): Reveal later minarets in separate structural components
    // Frames 240–269 (0.80 - 0.90): Controlled exploded view
    // Frames 270–299 (0.90 - 1.00): Reassembly into clear three-quarter perspective

    if (progress < 0.20) {
      // Act 1: Top Plan (Plan Cut Active)
      this.currentState = 'TOP_PLAN';
      this.switchCameraMode('orthographic');
      this.setMinaretsVisible(false);
      this.setPlanCut(true);
      this.setExplodedProgress(0);

      this.camTargetPos.set(0, 70, -3.3);
      this.camTargetLook.set(0, 0, -3.3);
      this.camTargetUp.set(0, 0, -1);
      this.targetOrthoZoom = 17;
    } else if (progress < 0.40) {
      // Act 2: Transition into Side Elevation
      this.currentState = 'SIDE_ELEVATION';
      this.switchCameraMode('orthographic');
      this.setMinaretsVisible(false);
      this.setPlanCut(false);
      this.setExplodedProgress(0);

      const t = (progress - 0.20) / (0.40 - 0.20);
      this.camTargetPos.lerpVectors(
        new THREE.Vector3(0, 70, -3.3),
        new THREE.Vector3(-70, 16, -3.3),
        t
      );
      this.camTargetLook.lerpVectors(
        new THREE.Vector3(0, 0, -3.3),
        new THREE.Vector3(0, 16, -3.3),
        t
      );
      this.camTargetUp.lerpVectors(
        new THREE.Vector3(0, 0, -1),
        new THREE.Vector3(0, 1, 0),
        t
      ).normalize();
      this.targetOrthoZoom = THREE.MathUtils.lerp(17, 14.5, t);
    } else if (progress < 0.60) {
      // Act 3: Transition into Front Elevation 1092 CE (No Minarets)
      this.currentState = 'FRONT_ELEVATION';
      this.switchCameraMode('orthographic');
      this.setMinaretsVisible(false);
      this.setPlanCut(false);
      this.setExplodedProgress(0);

      const t = (progress - 0.40) / (0.60 - 0.40);
      this.camTargetPos.lerpVectors(
        new THREE.Vector3(-70, 16, -3.3),
        new THREE.Vector3(0, 14, 70),
        t
      );
      this.camTargetLook.lerpVectors(
        new THREE.Vector3(0, 16, -3.3),
        new THREE.Vector3(0, 14, 0),
        t
      );
      this.camTargetUp.set(0, 1, 0);
      this.targetOrthoZoom = THREE.MathUtils.lerp(14.5, 14, t);
    } else if (progress < 0.80) {
      // Act 4: Reveal Later Minarets (1415–1421 CE)
      this.currentState = 'MAMLUK_ADDITIONS';
      this.switchCameraMode('perspective');
      this.setMinaretsVisible(true);
      this.setPlanCut(false);
      this.setExplodedProgress(0);

      const t = (progress - 0.60) / (0.80 - 0.60);
      // Minarets descend into place
      const elev = (1.0 - t) * 12.0;
      this.setMinaretElevation(elev / 12.0);

      this.camTargetPos.lerpVectors(
        new THREE.Vector3(0, 16, 60),
        new THREE.Vector3(22, 28, 32),
        t
      );
      this.camTargetLook.set(0, 20, 0);
      this.camTargetUp.set(0, 1, 0);
    } else if (progress < 0.90) {
      // Act 5: Controlled Exploded View
      this.currentState = 'EXPLODED_VIEW';
      this.switchCameraMode('perspective');
      this.setMinaretsVisible(true);
      this.setPlanCut(false);

      const t = (progress - 0.80) / (0.90 - 0.80);
      const explodeVal = Math.sin(t * Math.PI) * 0.75;
      this.setExplodedProgress(explodeVal);

      this.camTargetPos.lerpVectors(
        new THREE.Vector3(22, 28, 32),
        new THREE.Vector3(-34, 24, 38),
        t
      );
      this.camTargetLook.set(0, 18, 0);
      this.camTargetUp.set(0, 1, 0);
    } else {
      // Act 6: Reassembly into Three-Quarter Perspective
      this.currentState = 'FULLY_ASSEMBLED';
      this.switchCameraMode('perspective');
      this.setMinaretsVisible(true);
      this.setPlanCut(false);
      this.setExplodedProgress(0);

      const t = (progress - 0.90) / (1.0 - 0.90);
      this.camTargetPos.lerpVectors(
        new THREE.Vector3(-34, 24, 38),
        new THREE.Vector3(-26, 18, 36),
        t
      );
      this.camTargetLook.set(0, 15, -1.0);
      this.camTargetUp.set(0, 1, 0);
    }
  }

  // Adjust exploded-view progress
  public setExplodedProgress(val: number) {
    this.explodedProgress = THREE.MathUtils.clamp(val, 0, 1);

    const towerLateralShift = this.explodedProgress * 5.2;
    this.leftTowerObj.group.position.x = -7.2 - towerLateralShift;
    this.rightTowerObj.group.position.x = 7.2 + towerLateralShift;

    const minaretExtraY = this.explodedProgress * 6.5;
    this.leftMinaret.root.position.x = this.leftTowerObj.group.position.x;
    this.leftMinaret.root.position.y = 17.8 + minaretExtraY + this.minaretElevation * 12.0;

    this.rightMinaret.root.position.x = this.rightTowerObj.group.position.x;
    this.rightMinaret.root.position.y = 17.8 + minaretExtraY + this.minaretElevation * 12.0;

    this.leftMinaret.setTierExplosion(this.explodedProgress * 0.7);
    this.rightMinaret.setTierExplosion(this.explodedProgress * 0.7);

    this.portalObj.group.position.z = this.explodedProgress * 3.5;
  }

  public setMinaretElevation(val: number) {
    this.minaretElevation = THREE.MathUtils.clamp(val, 0, 1);
    const elev = this.minaretElevation * 12.0;
    this.leftMinaret.root.position.y = 17.8 + elev + this.explodedProgress * 6.5;
    this.rightMinaret.root.position.y = 17.8 + elev + this.explodedProgress * 6.5;
  }

  public setTowerSeparation(val: number) {
    this.towerSeparation = THREE.MathUtils.clamp(val, 0, 1);
    const shift = this.towerSeparation * 5.5;
    this.leftTowerObj.group.position.x = -7.2 - shift;
    this.rightTowerObj.group.position.x = 7.2 + shift;
    this.leftMinaret.root.position.x = this.leftTowerObj.group.position.x;
    this.rightMinaret.root.position.x = this.rightTowerObj.group.position.x;
  }

  public setDoorAngle(angleDeg: number) {
    this.doorAngleDeg = THREE.MathUtils.clamp(angleDeg, 0, 90);
    this.doorsAssembly.setDoorAngle(THREE.MathUtils.degToRad(this.doorAngleDeg));
  }

  public setMinaretsVisible(visible: boolean) {
    this.minaretsVisible = visible;
    this.leftMinaret.root.visible = visible && this.visibility.leftMinaret;
    this.rightMinaret.root.visible = visible && this.visibility.rightMinaret;
  }

  public setComponentVisibility(vis: Partial<ComponentVisibility>) {
    this.visibility = { ...this.visibility, ...vis };
    this.leftTowerObj.group.visible = this.visibility.leftTower;
    this.rightTowerObj.group.visible = this.visibility.rightTower;
    this.portalObj.group.visible = this.visibility.centralArch;
    this.doorsAssembly.leftPivot.visible = this.visibility.leftDoor;
    this.doorsAssembly.rightPivot.visible = this.visibility.rightDoor;
    this.leftMinaret.root.visible = this.minaretsVisible && this.visibility.leftMinaret;
    this.rightMinaret.root.visible = this.minaretsVisible && this.visibility.rightMinaret;
    this.groundApron.visible = this.visibility.ground;
  }

  public setMaterialSettings(settings: MaterialSettings) {
    updateMaterialsWithSettings(this.materials, settings);
  }

  public setAnnotationsVisible(visible: boolean) {
    this.annotationGroup.visible = visible;
  }

  // Handle Raycasting Pointer Down
  private handlePointerDown(e: MouseEvent) {
    const rect = this.renderer.domElement.getBoundingClientRect();
    this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

    this.raycaster.setFromCamera(this.mouse, this.activeCamera);

    const spriteHits = this.raycaster.intersectObjects(
      this.annotationGroup.children,
      false
    );
    if (spriteHits.length > 0) {
      const hitSprite = spriteHits[0].object as THREE.Sprite;
      const annotation = hitSprite.userData?.annotation as AnnotationItem;
      if (annotation && this.callbacks.onSelectAnnotation) {
        this.callbacks.onSelectAnnotation(annotation);
        return;
      }
    }

    const hits = this.raycaster.intersectObjects(this.modelRoot.children, true);
    if (hits.length > 0) {
      let currentObj: THREE.Object3D | null = hits[0].object;
      while (currentObj && currentObj !== this.modelRoot) {
        if (currentObj.userData && currentObj.userData.nameEn) {
          if (this.callbacks.onSelectComponent) {
            this.callbacks.onSelectComponent({
              id: currentObj.userData.id || currentObj.name,
              nameEn: currentObj.userData.nameEn,
              nameAr: currentObj.userData.nameAr || '',
              descriptionEn: currentObj.userData.descriptionEn || currentObj.userData.description,
              descriptionAr: currentObj.userData.descriptionAr,
              era: currentObj.userData.era,
              certainty: currentObj.userData.certainty,
            });
          }
          return;
        }
        currentObj = currentObj.parent;
      }
    }

    if (this.callbacks.onSelectComponent) {
      this.callbacks.onSelectComponent(null);
    }
  }

  /**
   * Export fully named 3D model hierarchy to V04 Master GLB file
   */
  public exportGLB() {
    const exporter = new GLTFExporter();
    exporter.parse(
      this.modelRoot,
      (gltf) => {
        const output = gltf instanceof ArrayBuffer ? gltf : JSON.stringify(gltf, null, 2);
        const blob = new Blob([output], {
          type: gltf instanceof ArrayBuffer ? 'application/octet-stream' : 'application/json',
        });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `RUWAQ_BAB_ZUWAYLA_V04_MASTER.glb`;
        link.click();
        URL.revokeObjectURL(url);
      },
      (error) => {
        console.error('An error occurred during GLB export:', error);
      },
      { binary: true }
    );
  }

  public captureSnapshot(): string {
    this.renderer.render(this.scene, this.activeCamera);
    return this.renderer.domElement.toDataURL('image/png');
  }

  private handleResize() {
    if (!this.container || this.isDisposed) return;
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;
    if (width === 0 || height === 0) return;

    const aspect = width / height;

    this.perspectiveCamera.aspect = aspect;
    this.perspectiveCamera.updateProjectionMatrix();

    const frustumSize = 42;
    this.orthographicCamera.left = (-frustumSize * aspect) / 2;
    this.orthographicCamera.right = (frustumSize * aspect) / 2;
    this.orthographicCamera.top = frustumSize / 2;
    this.orthographicCamera.bottom = -frustumSize / 2;
    this.orthographicCamera.updateProjectionMatrix();

    this.renderer.setSize(width, height);
  }

  // Animation render loop
  private tick() {
    if (this.isDisposed) return;

    if (!this.isUserInteracting) {
      const delta = 0.045;
      const k = this.cameraTransitionSpeed;
      const factor = 1.0 - Math.exp(-k * delta);

      this.activeCamera.position.lerp(this.camTargetPos, factor);
      this.controls.target.lerp(this.camTargetLook, factor);
      this.activeCamera.up.lerp(this.camTargetUp, factor).normalize();

      if (this.activeCamera === this.orthographicCamera) {
        this.currentOrthoZoom += (this.targetOrthoZoom - this.currentOrthoZoom) * factor;
        this.orthographicCamera.zoom = this.currentOrthoZoom;
        this.orthographicCamera.updateProjectionMatrix();
      }
    }

    this.controls.update();
    this.renderer.render(this.scene, this.activeCamera);

    this.animFrameId = requestAnimationFrame(this.tick);
  }

  public dispose() {
    this.isDisposed = true;
    cancelAnimationFrame(this.animFrameId);
    window.removeEventListener('resize', this.handleResize);
    this.renderer.domElement.removeEventListener('pointerdown', this.handlePointerDown);

    this.controls.dispose();
    this.renderer.dispose();

    if (this.renderer.domElement.parentElement) {
      this.renderer.domElement.parentElement.removeChild(this.renderer.domElement);
    }
  }
}
