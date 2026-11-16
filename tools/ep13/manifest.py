"""Rebuild docs/ep13/ASSET_MANIFEST_UPDATED.json from what is on disk.

    .venv/bin/python tools/ep13/manifest.py

Every hash below is computed at run time — nothing is transcribed by hand.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# (path, role, provenance, license, status)
ENTRIES = [
    ("public/ep13/audio/chapter01.mp3", "audio",
     "Original S01 narration take, supplied by the client (Drive). Voice of truth for timing.",
     "Client-owned recording. Not for redistribution.", "PRESENT — VOICE_OF_TRUTH"),
    ("public/ep13/brand/logo.svg", "brand",
     "Official RUWAQ emblem from 01-BRAND, copied unchanged.",
     "RUWAQ brand asset (client-owned).", "PRESENT — UNCHANGED"),
    ("public/fonts/Amiri-Bold.ttf", "font", "Amiri by Khaled Hosny (Google Fonts).",
     "SIL Open Font License 1.1.", "PRESENT"),
    ("public/fonts/Amiri-Regular.ttf", "font", "Amiri by Khaled Hosny (Google Fonts).",
     "SIL Open Font License 1.1.", "PRESENT"),
    ("public/fonts/IBMPlexSansArabic-Regular.ttf", "font", "IBM Plex Sans Arabic (IBM).",
     "SIL Open Font License 1.1.", "PRESENT"),
    ("public/fonts/IBMPlexSansArabic-Medium.ttf", "font", "IBM Plex Sans Arabic (IBM).",
     "SIL Open Font License 1.1.", "PRESENT"),
    ("public/fonts/IBMPlexSansArabic-Bold.ttf", "font", "IBM Plex Sans Arabic (IBM).",
     "SIL Open Font License 1.1.", "PRESENT"),
    ("public/ep13/assets/approved/A01_DINING_ESTABLISHING_CLEAN.png", "plate",
     "Handoff asset A01 (flattened still).", "Client-supplied; reference/plate use only.",
     "PRESENT — NOT USED IN 0–6 s PROOF"),
    ("public/ep13/assets/approved/A02_SPEECH_BUBBLE_LAYER.svg", "layer",
     "Handoff asset A02 (vector).", "Client-supplied.", "PRESENT — NOT USED IN 0–6 s PROOF"),
    ("public/ep13/assets/approved/A03_CAUSALITY_QUESTION_LAYER.svg", "layer",
     "Handoff asset A03 (vector).", "Client-supplied.", "PRESENT — SHAPE LANGUAGE REFERENCE ONLY"),
    ("public/ep13/assets/approved/A04_EVIDENCE_PANELS_BLANK.svg", "layer",
     "Handoff asset A04 (blank template).", "Client-supplied.", "PRESENT — SHAPE LANGUAGE REFERENCE ONLY"),
    ("public/ep13/assets/approved/A05_QUESTION_MARK_LAYER.svg", "layer",
     "Handoff asset A05 (vector).", "Client-supplied.", "PRESENT — SHAPE LANGUAGE REFERENCE ONLY"),
    ("public/ep13/assets/approved/A06_CONCEPT_FISH_MILK_REFERENCE_ONLY.png", "reference",
     "Handoff asset A06 concept frame.", "Client-supplied; reference only, never composited.",
     "PRESENT — REFERENCE_ONLY"),
    ("episode/ep13/measured_audio.json", "measurement",
     "Measured from chapter01.mp3 with tools/ep13/audio_analysis.py (speech-run detection).",
     "Generated.", "PRESENT — MEASURED"),
    ("episode/ep13/spec/SHA256SUMS.txt", "spec",
     "Handoff checksum list; all 37 listed files verify against it.", "Handoff.", "PRESENT — 37/37 VERIFIED"),
    ("render/ep13/PROOF_0_6_v2.mp4", "deliverable",
     "Rendered by tools/ep13/render.py; video frames from tools/ep13/scene.py, audio = 0–6.00 s of chapter01.mp3.",
     "Derived from client assets.", "DELIVERED — PENDING VISUAL APPROVAL"),
    ("render/ep13/PROOF_CONTACT.jpg", "deliverable",
     "Contact sheet, frames 0/20/40/60/90/120/150/179.", "Derived.", "DELIVERED"),
    ("render/ep13/STYLEFRAME_A_1920.png", "deliverable",
     "G1 styleframe A (hook), 1920x1080, frame 54 of the same renderer.", "Derived.", "DELIVERED"),
    ("render/ep13/STYLEFRAME_B_1920.png", "deliverable",
     "G1 styleframe B (claim), 1920x1080, frame 150.", "Derived.", "DELIVERED"),
    ("render/ep13/QC_REPORT.json", "measurement",
     "Measured frame-difference QC (tools/ep13/qc.py), camera on vs camera off.", "Generated.", "DELIVERED"),
    ("docs/ep13/QC_REFERENCE_COMPARISON.jpg", "deliverable",
     "Side-by-side: our frames vs the supplied reference at matching moments.", "Derived.", "DELIVERED"),
]

CODE = [
    "tools/ep13/tokens.py", "tools/ep13/text.py", "tools/ep13/gfx.py",
    "tools/ep13/heroes.py", "tools/ep13/stage.py", "tools/ep13/scene.py",
    "tools/ep13/timeline.py", "tools/ep13/audio_analysis.py",
    "tools/ep13/render.py", "tools/ep13/qc.py", "tools/ep13/manifest.py",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def entry(path: str, role: str, provenance: str, license_: str, status: str) -> dict:
    p = ROOT / path
    rec = {"path": path, "role": role, "provenance": provenance,
           "license": license_, "status": status}
    if p.exists():
        rec.update({"present": True, "bytes": p.stat().st_size, "sha256": sha256(p)})
    else:
        rec.update({"present": False, "sha256": None})
    return rec


def main() -> int:
    manifest = {
        "project": "RUWAQ — episode 13, ‘fish and milk’ claim episode",
        "stage": "G2 — 0–6 s motion-quality proof",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "resolution_policy": "design 1920x1080; proof rendered 1280x720 @2x supersample; "
                             "styleframes 1920x1080",
        "declared_limitations": [
            "No separate fish or glass 3-D asset exists and none was generated from the "
            "reference: both heroes are procedural 2.5-D vector sprites (tools/ep13/heroes.py). "
            "They are not a 3-D model and cannot be orbited.",
            "Word-level Arabic/Arabic-English sync is not claimed: only phrase onsets are "
            "measured from the audio file; a native listen is still required.",
            "The proof uses no footage from the Pinterest reference video; the video informed "
            "design grammar only.",
        ],
        "assets": [entry(*e) for e in ENTRIES],
        "code": [entry(c, "code", "Authored in this repository for this render.",
                       "Client project code.", "PRESENT") for c in CODE],
    }
    out = ROOT / "docs/ep13/ASSET_MANIFEST_UPDATED.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    missing = [a["path"] for a in manifest["assets"] if not a["present"]]
    print(f"wrote {out.relative_to(ROOT)} — {len(manifest['assets'])} assets, "
          f"{len(manifest['code'])} code files, missing: {missing or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
