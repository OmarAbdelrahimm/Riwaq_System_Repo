// thumbs.mjs — يرندر الصور المصغّرة الثلاث (1280×720 PNG) من تكوين Thumbnail
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import fs from "node:fs";
import path from "node:path";
const brand = JSON.parse(fs.readFileSync("data/brand.json", "utf8"));
const I = "projects/WHAT_IF_BAGHDAD_NEVER_FELL/img/";
const out = process.argv[2] || "exports/WHAT_IF_BAGHDAD_NEVER_FELL/publish/thumbnails";
fs.mkdirSync(out, { recursive: true });
const T = [
  { file: "thumb_A_face.png", variant: "face", title: "لو قَبِل\nالخليفة؟", img_a: I + "pd03_hulagu_portrait.jpg", tag: "خيال تاريخي" },
  { file: "thumb_B_puzzle.png", variant: "puzzle", title: "بغداد\nلم تسقط؟", img_a: I + "img02_baghdad_dusk.jpg", tag: "خيال تاريخي" },
  { file: "thumb_C_before_after.png", variant: "before_after", title: "بغداد… في عالمين", img_a: I + "pd01_bagdad1258_siege.jpg", img_b: I + "img02_baghdad_dusk.jpg", tag: "خيال تاريخي" },
];
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts"), publicDir: path.resolve("public") });
const opts = { browserExecutable: "/tmp/chromium", chromiumOptions: { gl: "swiftshader" } };
for (const t of T) {
  const inputProps = { brand, ...t };
  const comp = await selectComposition({ serveUrl, id: "Thumbnail", inputProps, ...opts });
  await renderStill({ composition: comp, serveUrl, output: path.join(out, t.file), frame: 0, inputProps, imageFormat: "png", ...opts });
  console.log("✔", t.file);
}
