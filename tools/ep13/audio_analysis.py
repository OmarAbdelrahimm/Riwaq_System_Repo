"""Measure the original S01 take instead of trusting the storyboard guides.

Authority: ``public/ep13/audio/chapter01.mp3``
  sha256 83be0fd38793736fede1031067a9594145ece2a45bd92c70e52be4eaa97609e8

The script decodes the file with the ffmpeg binary that ships inside the
``imageio-ffmpeg`` wheel, computes a 20 ms-hop RMS envelope, gates speech
activity and reports phrase onsets/offsets plus the pause lengths between them.

It deliberately does NOT transcribe. Word-level identification needs a human
listen (documented in docs/ep13/QC.md); this file only provides timing.
"""

from __future__ import annotations

import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

SR = 22050
HOP = 0.020
WIN = 0.040


def decode_wav(src: Path, dst: Path) -> None:
    import imageio_ffmpeg

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [ffmpeg, "-v", "error", "-y", "-i", str(src), "-ac", "1", "-ar", str(SR), str(dst)],
        check=True,
    )


def envelope(path: Path) -> tuple[np.ndarray, float]:
    with wave.open(str(path)) as w:
        n = w.getnframes()
        raw = w.readframes(n)
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    hop = int(SR * HOP)
    win = int(SR * WIN)
    frames = max(0, (len(x) - win) // hop)
    env = np.array([np.sqrt(np.mean(x[i * hop : i * hop + win] ** 2)) for i in range(frames)])
    return env, HOP


def runs(env: np.ndarray, hop: float, gate_pct: float = 30.0, min_run: float = 0.12,
         merge_gap: float = 0.14) -> list[dict]:
    thr = np.percentile(env, gate_pct) * 1.05
    active = env > thr
    out: list[dict] = []
    i = 0
    while i < len(active):
        if active[i]:
            j = i
            while j + 1 < len(active) and active[j + 1]:
                j += 1
            out.append({"start": i * hop, "end": (j + 1) * hop})
            i = j + 1
        else:
            i += 1
    # merge tiny gaps, drop tiny runs
    merged: list[dict] = []
    for r in out:
        if merged and r["start"] - merged[-1]["end"] < merge_gap:
            merged[-1]["end"] = r["end"]
        else:
            merged.append(dict(r))
    return [r for r in merged if r["end"] - r["start"] >= min_run]


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    src = root / "public/ep13/audio/chapter01.mp3"
    tmp = Path("/tmp/ep13_s01.wav")
    decode_wav(src, tmp)
    env, hop = envelope(tmp)
    speech = runs(env, hop)
    report = {
        "source": str(src.relative_to(root)),
        "sample_rate": SR,
        "hop_s": HOP,
        "window_s": WIN,
        "duration_s": round(len(env) * hop, 3),
        "gate": "percentile(30) * 1.05, merge gaps < 140 ms, drop runs < 120 ms",
        "speech_runs": [{"start": round(r["start"], 3), "end": round(r["end"], 3),
                         "len": round(r["end"] - r["start"], 3)} for r in speech],
        "note": "Timing only. No transcription and no word-level claim; a native listen is still required.",
    }
    out = root / "episode/ep13/measured_audio.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report["speech_runs"][:10], ensure_ascii=False, indent=1))
    print("duration", report["duration_s"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
