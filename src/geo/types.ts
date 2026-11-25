/**
 * RUWAQ Historical Geography: TypeScript Types
 * Data structures for MapLibre GL, GeoJSON, Provenance, and Deterministic Story Sequence
 */

export type StoryActId =
  | 'MODERN_CAIRO'      // Act 1: Greater Cairo geographical context & Nile
  | 'HISTORIC_CAIRO'    // Act 2: UNESCO World Heritage boundary
  | 'FATIMID_EXTENT'    // Act 3: Explicitly approximate Fatimid Cairo enclosure (1092 CE)
  | 'AL_MUIZZ_AXIS'     // Act 4: Historic north-south spine (Al-Mu'izz St)
  | 'NORTHERN_GATES'    // Act 5: Documented northern gates (Bab al-Futuh & Bab al-Nasr)
  | 'BAB_ZUWAYLA_GATE'  // Act 6: Bab Zuwayla at the southern frontier
  | 'TRANSITION_TO_3D'  // Act 7: Camera plunge & morph from map to 3D architectural model
  | 'INSPECTION_3D';    // Act 8: 3D Architectural examination

export interface StoryActDefinition {
  id: StoryActId;
  actNumber: number;
  startFrame: number;
  endFrame: number;
  titleEn: string;
  titleAr: string;
  subtitleEn: string;
  historicalContextEn: string;
  cartographicNoteEn: string;
  targetCenter: [number, number]; // [lng, lat]
  targetZoom: number;
  targetPitch: number;
  targetBearing: number;
  activeLayers: string[];
}

export interface LayerVisibilityState {
  modernStreets: boolean;
  nileWater: boolean;
  historicCairoUnesco: boolean;
  fatimidApproximateExtent: boolean;
  uncertaintyBuffer: boolean;
  alMuizzAxis: boolean;
  northernGates: boolean;
  babZuwaylaSouthernAnchor: boolean;
  secondaryGateTraces: boolean;
  historicKhalijCanal: boolean;
  threeDOverlay: boolean;
  topographicContours: boolean;
}

export type ProvenanceClassification =
  | 'VERIFIED_CONTEMPORARY_SURVEY'       // OSM, official government surveys, GPS
  | 'IN_SITU_ARCHAEOLOGICAL_EVIDENCE'    // Standing monuments, excavated foundations
  | 'HISTORICAL_TEXTUAL_ATTESTATION'     // Al-Maqrizi, Ibn Duqmaq, Al-Qalqashandi
  | 'HYPOTHETICAL_RECONSTRUCTION_APPROX' // Interpolated ancient wall boundaries
  | 'EDUCATIONAL_SYNTHESIS'              // Schematic pedagogical markers
  | 'VERIFIED_CONTEMPORARY_SURVEY & HISTORICAL_RECORD';

export interface GeoFeatureMetadata {
  id: string;
  nameEn: string;
  nameAr: string;
  era: string;
  dateAttested: string;
  patron?: string;
  architectMaster?: string;
  provenance: ProvenanceClassification;
  citation: string;
  osmReference?: string;
  archaeologicalCertainty: 'Absolute (Standing)' | 'High (Excavated)' | 'Moderate (Textual)' | 'Approximate (Hypothetical ±50m)';
  coordinates: [number, number] | [number, number][] | [number, number][][];
  descriptionEn: string;
  descriptionAr: string;
}

export interface ResearcherGeoJsonOverride {
  id: string;
  title: string;
  author: string;
  institution: string;
  year: number;
  uncertaintyMarginMeters: number;
  geojsonData: GeoJSON.FeatureCollection;
}
