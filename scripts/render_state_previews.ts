/**
 * Renders all 8 distinct architectural state previews from Remotion
 */

import { execSync } from 'node:child_process';
import path from 'node:path';
import fs from 'node:fs';

const states = [
  { file: '01_FATIMID_ORIGINAL.png', frame: 120, label: 'State 1: Original Fatimid Gate (1092 CE)' },
  { file: '02_TOP_PLAN.png', frame: 15, label: 'State 2: Top Orthographic Plan' },
  { file: '03_SIDE_ELEVATION.png', frame: 75, label: 'State 3: Side Orthographic Elevation' },
  { file: '04_FRONT_ELEVATION.png', frame: 110, label: 'State 4: Front Orthographic Elevation' },
  { file: '05_PERSPECTIVE_3Q.png', frame: 290, label: 'State 5: Perspective Three-Quarter View' },
  { file: '06_MAMLUK_ADDITIONS.png', frame: 165, label: 'State 6: Mamluk Minaret Additions (1415–1421 CE)' },
  { file: '07_EXPLODED_VIEW.png', frame: 220, label: 'State 7: Separated Architectural Components' },
  { file: '08_FULLY_ASSEMBLED.png', frame: 295, label: 'State 8: Fully Assembled Monument' },
];

const outDir = path.resolve(process.cwd(), 'public/RUWAQ_8_STATES_PREVIEW');
if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

console.log('📸 Rendering all 8 architectural states previews from Remotion composition...');

for (const s of states) {
  const targetPath = path.join(outDir, s.file);
  console.log(`Rendering [${s.label}] at frame ${s.frame} -> ${s.file}...`);
  execSync(
    `npx remotion still src/remotion-index.ts RuwaqBabZuwayla "${targetPath}" --frame=${s.frame}`,
    { stdio: 'inherit' }
  );
}

console.log('✅ All 8 architectural state previews successfully rendered into public/RUWAQ_8_STATES_PREVIEW/');
