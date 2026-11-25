import { Config } from '@remotion/cli/config';

// Remotion config — entry point is src/remotion-index.ts (see package.json
// scripts render:*). Chromium is downloaded on first render by the CLI.
Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
