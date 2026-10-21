# Riwaq YouTube publishing-bundle builder

This script generates the tracked publishing sources for the 12 finalized RELATIONSHIP episode cuts and Shorts. It does **not** download, alter, or store any MP4. Every photo used in a cover is cropped from an existing project thumbnail that contains a real frame from the source cut; no face is generated.

## Regenerate

1. Create an isolated Python environment and install `python -m pip install -r scripts/youtube_bundle/requirements.txt` from the repository root.
2. Run `python scripts/youtube_bundle/build.py` from the repository root.
3. Keep the bilingual SRTs in each `youtube_packages/<ID>/CAPTIONS_AR_EN.srt` directory; English-only SRTs are extracted from their existing English cue lines without changing indices or timecodes.
4. Source stills are stored under `youtube_packages/source_frames/`, so cover generation is reproducible without the MP4s or Drive access.

The builder checks the 70-character Arabic title target, three-to-five-word cover hooks, 400–500-character YouTube tag fields, exactly three hashtags per language description, expected image dimensions, and the empty final 240 pixels of each vertical cover. It writes byte sizes and SHA-256 hashes to each `ASSET_MANIFEST.json`. The vector Riwaq mark is kept in `assets/riwaq-mark.svg` as a brand reference. The generated lock-up uses a lightweight Pillow-only arch-and-jewel rendition, avoiding a system Cairo dependency.

## Delivery convention

Each local package contains `SEO.md`, `CAPTIONS_AR_EN.srt`, `CAPTIONS_EN.srt`, and four cover exports (`1280x720` and `1080x1920`, each as JPG and PNG), plus a non-video asset manifest. The corresponding final MP4s are copied server-side within Google Drive so their original bytes remain unchanged; they are intentionally excluded from Git.

## Verified project inputs

The metadata, clip source ranges, source Drive file IDs, and original caption timing are recorded in `youtube_packages/package_manifest.json`. The only external link in the SEO descriptions is the full episode link already verified in the project context; `&t=` deep links are derived from the recorded source offsets. No chapter timestamps are invented: the three long-cut chapter boundaries are mapped to actual cuts and checked against the final timed captions; Shorts have no chapter list.
