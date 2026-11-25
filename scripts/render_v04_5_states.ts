/**
 * Renders the 5 required V04 architectural test stills from Remotion:
 * 01_TOP_PLAN.png
 * 02_SIDE_ELEVATION.png
 * 03_FRONT_1092.png
 * 04_FRONT_1421.png
 * 05_EXPLODED_ARCHITECTURE.png
 */

import { execSync } from 'node:child_process';
import path from 'node:path';
import fs from 'node:fs';

const states = [
  { file: '01_TOP_PLAN.png', frame: 25, label: '01_TOP_PLAN: Open readable passage & semicircular footprints' },
  { file: '02_SIDE_ELEVATION.png', frame: 105, label: '02_SIDE_ELEVATION: True side orthographic projection' },
  { file: '03_FRONT_1092.png', frame: 175, label: '03_FRONT_1092: Original 1092 CE gate, no minarets' },
  { file: '04_FRONT_1421.png', frame: 235, label: '04_FRONT_1421: Complete gate with Mamluk minarets' },
  { file: '05_EXPLODED_ARCHITECTURE.png', frame: 260, label: '05_EXPLODED_ARCHITECTURE: Exploded structural components' },
];

const outDirs = [
  path.resolve(process.cwd(), 'public/RUWAQ_BAB_ZUWAYLA_V04_5_STATES'),
  path.resolve(process.cwd(), 'RUWAQ_BAB_ZUWAYLA_V04_5_STATES'),
];

outDirs.forEach((dir) => {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
});

console.log('📸 Rendering Phase E 5 V04 architectural test stills via Remotion CLI...');

for (const s of states) {
  const targetPath = path.join(outDirs[0], s.file);
  console.log(`\n▶ Rendering [${s.label}] at frame ${s.frame} -> ${s.file}...`);
  execSync(
    `npx remotion still src/remotion-index.ts RuwaqBabZuwayla "${targetPath}" --frame=${s.frame}`,
    { stdio: 'inherit' }
  );
  // Also copy to root folder
  fs.copyFileSync(targetPath, path.join(outDirs[1], s.file));
}

console.log('\n✅ All 5 V04 architectural stills successfully rendered into RUWAQ_BAB_ZUWAYLA_V04_5_STATES/!');
