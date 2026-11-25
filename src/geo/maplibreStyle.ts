/**
 * RUWAQ Custom MapLibre GL Style Specification
 * Authentic cream, gold, and deep-ink cartographic design.
 * Designed to work 100% offline from embedded GeoJSON layers,
 * with optional CARTO/OSM raster tiles when online.
 */

import {
  NILE_RIVER_GEOJSON,
  MODERN_CAIRO_NETWORK_GEOJSON,
  UNESCO_HISTORIC_CAIRO_GEOJSON,
  AL_MUIZZ_AXIS_GEOJSON,
  FATIMID_GATES_GEOJSON,
  VERIFIED_NORTHERN_WALL_GEOJSON,
  DEFAULT_APPROXIMATE_FATIMID_ENCLOSURE_GEOJSON,
  FATIMID_UNCERTAINTY_BUFFER_GEOJSON,
} from './cairoHistoricalGeoJSON.ts';

export function createRuwaqMapStyle(
  fatimidEnclosureData: GeoJSON.FeatureCollection = DEFAULT_APPROXIMATE_FATIMID_ENCLOSURE_GEOJSON,
  enableRasterTiles: boolean = true
): any {
  const sources: Record<string, any> = {
    'nile-river': {
      type: 'geojson',
      data: NILE_RIVER_GEOJSON,
    },
    'modern-network': {
      type: 'geojson',
      data: MODERN_CAIRO_NETWORK_GEOJSON,
    },
    'unesco-zone': {
      type: 'geojson',
      data: UNESCO_HISTORIC_CAIRO_GEOJSON,
    },
    'al-muizz-axis': {
      type: 'geojson',
      data: AL_MUIZZ_AXIS_GEOJSON,
    },
    'fatimid-gates': {
      type: 'geojson',
      data: FATIMID_GATES_GEOJSON,
    },
    'northern-wall': {
      type: 'geojson',
      data: VERIFIED_NORTHERN_WALL_GEOJSON,
    },
    'fatimid-enclosure': {
      type: 'geojson',
      data: fatimidEnclosureData,
    },
    'uncertainty-buffer': {
      type: 'geojson',
      data: FATIMID_UNCERTAINTY_BUFFER_GEOJSON,
    },
  };

  if (enableRasterTiles) {
    sources['carto-positron'] = {
      type: 'raster',
      tiles: [
        'https://a.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png',
        'https://b.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png',
      ],
      tileSize: 256,
      attribution: '&copy; OpenStreetMap contributors, &copy; CARTO',
    };
  }

  const layers: any[] = [
    // 1. Base Cream Background
    {
      id: 'ruwaq-background',
      type: 'background',
      paint: {
        'background-color': '#F3EBDB', // RUWAQ Approved Cream
      },
    },
  ];

  if (enableRasterTiles) {
    layers.push({
      id: 'carto-raster-layer',
      type: 'raster',
      source: 'carto-positron',
      paint: {
        'raster-opacity': 0.35,
        'raster-saturation': -0.85,
        'raster-contrast': 0.1,
      },
    });
  }

  layers.push(
    // 2. Nile River & Waterway Fill
    {
      id: 'nile-water-fill',
      type: 'fill',
      source: 'nile-river',
      paint: {
        'fill-color': '#2C3E42', // Deep Slate / Ancient River Nile Ink
        'fill-opacity': 0.85,
      },
    },
    {
      id: 'nile-water-outline',
      type: 'line',
      source: 'nile-river',
      paint: {
        'line-color': '#A98A4B', // Gold shore boundary
        'line-width': 1.2,
        'line-opacity': 0.6,
      },
    },

    // 3. Modern Cairo Streets Linework
    {
      id: 'modern-roads-line',
      type: 'line',
      source: 'modern-network',
      paint: {
        'line-color': '#9E9282',
        'line-width': [
          'interpolate',
          ['linear'],
          ['zoom'],
          10, 1.0,
          14, 2.0,
          17, 3.5,
        ],
        'line-opacity': 0.65,
      },
    },

    // 4. UNESCO Historic Cairo Boundary (1979)
    {
      id: 'unesco-zone-fill',
      type: 'fill',
      source: 'unesco-zone',
      paint: {
        'fill-color': '#E4D5BE',
        'fill-opacity': 0.45,
      },
    },
    {
      id: 'unesco-zone-casing',
      type: 'line',
      source: 'unesco-zone',
      paint: {
        'line-color': '#A98A4B',
        'line-width': 2.0,
        'line-dasharray': [4, 2],
        'line-opacity': 0.8,
      },
    },

    // 5. Archaeological Uncertainty Buffer (±50m)
    {
      id: 'fatimid-uncertainty-buffer-fill',
      type: 'fill',
      source: 'uncertainty-buffer',
      paint: {
        'fill-color': '#8C4729',
        'fill-opacity': 0.12,
      },
    },
    {
      id: 'fatimid-uncertainty-buffer-outline',
      type: 'line',
      source: 'uncertainty-buffer',
      paint: {
        'line-color': '#8C4729',
        'line-width': 1.0,
        'line-dasharray': [2, 3],
        'line-opacity': 0.45,
      },
    },

    // 6. Explicitly Approximate Fatimid Enclosure (1092 CE)
    {
      id: 'fatimid-enclosure-fill',
      type: 'fill',
      source: 'fatimid-enclosure',
      paint: {
        'fill-color': '#8C4729', // RUWAQ Terracotta Rust
        'fill-opacity': 0.22,
      },
    },
    {
      id: 'fatimid-enclosure-outline',
      type: 'line',
      source: 'fatimid-enclosure',
      paint: {
        'line-color': '#8C4729',
        'line-width': 2.8,
        'line-opacity': 0.9,
      },
    },

    // 7. Standing Northern Wall Curtain (Stone 1087 CE - Preserved Ground Truth)
    {
      id: 'northern-wall-solid',
      type: 'line',
      source: 'northern-wall',
      paint: {
        'line-color': '#1C1B19', // Deep Ink
        'line-width': 5.0,
        'line-opacity': 0.95,
      },
    },
    {
      id: 'northern-wall-gold-crest',
      type: 'line',
      source: 'northern-wall',
      paint: {
        'line-color': '#A98A4B',
        'line-width': 2.0,
        'line-opacity': 0.9,
      },
    },

    // 8. Al-Mu'izz Grand Ceremonial Axis (North-to-South Spine)
    {
      id: 'al-muizz-axis-glow',
      type: 'line',
      source: 'al-muizz-axis',
      paint: {
        'line-color': '#A98A4B',
        'line-width': 7.0,
        'line-opacity': 0.45,
        'line-blur': 3.0,
      },
    },
    {
      id: 'al-muizz-axis-core',
      type: 'line',
      source: 'al-muizz-axis',
      paint: {
        'line-color': '#1C1B19',
        'line-width': 3.2,
        'line-opacity': 0.95,
      },
    },
    {
      id: 'al-muizz-axis-dashed',
      type: 'line',
      source: 'al-muizz-axis',
      paint: {
        'line-color': '#D4AF37', // Gold highlight
        'line-width': 1.6,
        'line-dasharray': [3, 2],
        'line-opacity': 0.9,
      },
    },

    // 9. Fatimid Gates Circle Markers
    {
      id: 'fatimid-gates-outer-circle',
      type: 'circle',
      source: 'fatimid-gates',
      paint: {
        'circle-radius': [
          'match',
          ['get', 'roleInStory'],
          'PRIMARY_FOCUS', 12,
          'NORTHERN_DEFENSIVE_ANCHOR', 9,
          7,
        ],
        'circle-color': '#1C1B19',
        'circle-stroke-width': 2.5,
        'circle-stroke-color': '#A98A4B',
        'circle-opacity': 0.95,
      },
    },
    {
      id: 'fatimid-gates-inner-circle',
      type: 'circle',
      source: 'fatimid-gates',
      paint: {
        'circle-radius': [
          'match',
          ['get', 'roleInStory'],
          'PRIMARY_FOCUS', 6,
          'NORTHERN_DEFENSIVE_ANCHOR', 4,
          3,
        ],
        'circle-color': [
          'match',
          ['get', 'roleInStory'],
          'PRIMARY_FOCUS', '#A98A4B',
          'NORTHERN_DEFENSIVE_ANCHOR', '#8C4729',
          '#D8CEBC',
        ],
        'circle-opacity': 1.0,
      },
    }
  );

  return {
    version: 8,
    name: 'RUWAQ Historical Cartography',
    glyphs: 'https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf',
    sources,
    layers,
  };
}
