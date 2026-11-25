// stills.mjs — يحزم مرة واحدة ثم يلتقط عدة إطارات للمراجعة البصرية
// node stills.mjs <props.json> <outDir> <sec1,sec2,...>
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import fs from "node:fs";
import path from "node:path";

const [, , propsPath, outDir, secs] = process.argv;
const inputProps = JSON.parse(fs.readFileSync(propsPath, "utf8"));
fs.mkdirSync(outDir, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts"), publicDir: path.resolve("public") });
const opts = { browserExecutable: process.env.CHROME || "/tmp/chromium", chromiumOptions: { gl: "swiftshader" } };
const comp = await selectComposition({ serveUrl, id: "Episode", inputProps, ...opts });
for (const s of secs.split(",").map(Number)) {
  const frame = Math.min(comp.durationInFrames - 1, Math.round(s * comp.fps));
  const out = path.join(outDir, `f_${String(s).replace(".", "_")}.jpg`);
  const t0 = Date.now();
  await renderStill({ composition: comp, serveUrl, output: out, frame, inputProps, imageFormat: "jpeg", jpegQuality: 70, scale: 0.5, ...opts });
  console.log(out, Date.now() - t0, "ms");
}
