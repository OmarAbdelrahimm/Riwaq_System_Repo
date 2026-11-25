# RUWAQ: BAB ZUWAYLA V04
## ARCHITECTURAL 3D MODEL REPAIR & PRODUCTION CHANGELOG

---

### Executive Architectural Summary

The V01–V03 iterations of the Bab Zuwayla 3D reconstruction failed architectural review due to three primary issues:
1. **Opaque Connection**: An opaque rectangular masonry block bridged the towers, closing off the entrance and preventing visual continuity between the exterior approach and Cairo's interior.
2. **Tower Footprint Ambiguity**: Bastions lacked coherent semicircular stone massing connected into the curtain wall and passage flanks.
3. **Unstable Camera Coordinates & Roll**: Orthographic projections drifted, top views showed opaque roofs instead of architectural plan cuts, and transitions introduced unwanted camera roll.

**RUWAQ V04** executes a comprehensive architectural repair across geometry, camera projection, minaret articulation, and deterministic frame motion, prioritizing archaeological fidelity and verified photographic references.

---

### Phase A: Gate Geometry Repairs

#### A1. Twin Semicircular Bastion Towers (`left_semicircular_tower`, `right_semicircular_tower`)
- **Physical Semicircular Coherence**: Reconstructed towers with an authentic cylindrical radius of 5.2m and height of 17.8m. Their rounded external faces project 5.2m forward into the southern approach (+Z) and are immediately recognizable in both top plan and perspective views.
- **Continuous Masonry Connection**: The semicircular front drums are seamlessly bonded to 9.0m deep rectangular stone flanks extending back to Z = -9.0m, connecting into the historic Cairo southern curtain wall.
- **Defensive Splayed Arrow Slits (*Marami al-Siham*)**: Modeled inward-flaring embrasures at two defensive firing tiers (-50°, -25°, 0°, +25°, +50° angles) penetrating through the 1.45m thick ashlar perimeter wall.
- **Fatimid Stepped Crenellations (*Sharafat Fatimiyyah*)**: Replaced generic battlements with 11 round-topped stepped merlons crowning each bastion platform.

#### A2. The Open Gateway Passage (`gate_passage_vault`)
- **Complete Elimination of Solid Block**: Removed the previous opaque rectangular connection.
- **Continuous 11.4m Deep Open Volume**: Modeled a true 4.8m wide, physically continuous open passage extending from the southern entrance portal (Z = +2.4m) through to the northern city exit (Z = -9.0m).
- **Horizontal Architectural Section Cut**: Built a structured dual-layer geometry system (`lowerStructure` below Y = 5.0m and `upperStructure` above Y = 5.0m). In `TOP_PLAN` mode, upper vaults and roofs are clipped, exposing the open, readable entrance passage flanked by the thick semicircular stone bastion footprints.
- **Paved Interior Datum**: Dressed limestone paving installed along the full length of the passage at Y = 0.1m.

#### A3. Central Entrance Portal (`central_entrance_arch`)
- **Pointed Arch with Cushion Voussoirs (*al-Sanjat al-Wisadiyyah*)**: Constructed the iconic Fatimid entrance arch with 17 joggled convex cushion voussoirs springing from impost moldings at Y = 4.8m to an apex at Y = 7.8m.
- **Machicolation Slit Gallery**: Added a 5-opening corbelled machicolation slot arcade at Y = 11.2m above the pointed portal.
- **High Open Machicolation Bridge Arch (*Saqqatah*)**: Replaced the previous solid upper wall with an authentic open semicircular arch (span 5.4m, Y = 12.4m to 16.5m) through which the open sky and city are visible, matching photograph `image_8d20f9e3.png`.
- **Fortified Gate Leaves (`left_door_leaf`, `right_door_leaf`)**: Mounted inside stone reveals at Z = 0.8m, clad in horizontal wrought iron bands with forged hemispherical rivets, pivoted on stone sockets and angled inwards into the city.

---

### Phase B: Projection Cameras & Coordinates

- **World Coordinate Convention**:
  - `X`: Gateway width (left tower at X = -7.2m, right tower at X = +7.2m).
  - `Y`: Vertical elevation (0 = street datum, 17.8m = gate platform, 40.2m = minaret crescents).
  - `Z`: Passage direction (+Z = southern exterior approach, -Z = northern entrance into Cairo).
- **Derived Views**:
  - `TOP_PLAN`: Orthographic, looking from `(0, 70, -3.3)` with `up = (0, 0, -1)` (North is up), architectural section cut active, minarets hidden.
  - `SIDE_ELEVATION`: True side orthographic projection from `(-70, 16, -3.3)` with `up = (0, 1, 0)`, pitch = 0, roll = 0, upright vertical geometry.
  - `FRONT_ELEVATION`: Orthographic front elevation from `(0, 14, 70)` showing the original 1092 CE gate without later minarets.
  - `PERSPECTIVE_3Q`: Cinematic three-quarter perspective from `(-26, 18, 36)`.
- **Orientation Stability**: Interpolation during camera transitions uses quaternion spherical lerp (`slerp`) and normalized up-vectors, completely eliminating unwanted roll and gimbal flutter.

---

### Phase C: Mamluk Minarets (`left_minaret`, `right_minaret`)

Refined against authentic photograph `image_8d20f9e3.png` across six distinct architectural tiers:
1. **Tier 1 (Plinth & Lower Octagonal Shaft)**: Square stone plinth (3.5m) with chamfered squinch transitions to an octagonal shaft adorned with 8 recessed keel-arch niches and upper torus molding.
2. **Tier 2 (First Balcony)**: Triple-tier corbelled stone *muqarnas* (stalactite) brackets supporting an octagonal walkway with stone balustrade.
3. **Tier 3 (Middle Shaft with Chevron Relief)**: Slender octagonal shaft carved with authentic interlocking diagonal zigzag relief (*al-zakhrafah al-zajzajiyyah*) and 4 cardinal arched window embrasures.
4. **Tier 4 (Second Balcony)**: Corbelled stone muqarnas transition to upper openwork balustrade.
5. **Tier 5 (Colonnaded Pavilion / *Jawsaq*)**: Open octagonal pavilion supported on 8 slender stone colonnettes with horseshoe arches surrounding a central stair core.
6. **Tier 6 (Bulbous Finial / *Mabkhara*)**: Slender neck molding, authentic lathed pear-shaped bulbous dome, bronze spire rod, 3 graduated bronze spheres (*jammur*), and crescent moon (*Hilal*).
- **Independent Manipulation**: Both minarets and their individual tiers retain independent hierarchy and vertical explosion capability (`setTierExplosion`).

---

### Phase D: Lighting and Materials

- **RUWAQ PBR Studio Palette**:
  - Background: Cream `#F3EBDB`.
  - Structural Ink: Deep `#1C1B19`.
  - Accent / Gold: Warm `#A98A4B`.
- **Limestone Ashlar Shading**: Restrained roughness (0.82) with subtle ashlar joint variation and linear normal mapping, eliminating uniform plastic appearance.
- **Lighting**: Three-point studio rig pairing a warm key light (2.3 intensity, `#fff2d4`) with a balanced hemisphere fill (`#fbf7ed` / `#8e8271`) and soft contact shadow grounding.

---

### Phase E & F: Test Stills & Motion Sequence

- **Phase E Test Stills**:
  1. `01_TOP_PLAN.png`: Open readable passage and semicircular tower footprints under architectural section cut.
  2. `02_SIDE_ELEVATION.png`: True side orthographic projection with upright vertical geometry.
  3. `03_FRONT_1092.png`: Original gate without minarets, showing authentic cushion voussoir arch and open passage.
  4. `04_FRONT_1421.png`: Complete monument with Sultan al-Mu'ayyad's twin minarets in place.
  5. `05_EXPLODED_ARCHITECTURE.png`: Controlled architectural deconstruction with separated minaret tiers and lateral bastion shift.
- **Phase F Motion Preview (`RUWAQ_BAB_ZUWAYLA_V04_PREVIEW.mp4`)**:
  - Exactly 300 frames (10.0 seconds at 30fps, 1920×1080).
  - Strictly deterministic frame driver: arbitrary out-of-order frame seeking produces identical renders.
  - Zero application UI or debug widgets in the rendered motion asset.
