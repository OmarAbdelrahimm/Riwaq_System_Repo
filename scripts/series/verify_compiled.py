"""فحص الماستر المجمّع: المدة، الوصلات، الصوت، وتطابق الترجمة.

    python3 scripts/series/verify_compiled.py [path/to/master.mp4]
"""
from __future__ import annotations

import os
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import compile as C  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else f"{C.OUTDIR}/MASTER_COMPILED.mp4"


def probe(path: str) -> tuple[float, str]:
    r = subprocess.run([C.FF, "-hide_banner", "-i", path], capture_output=True, text=True)
    dur = 0.0
    for line in r.stderr.splitlines():
        if "Duration:" in line:
            h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
            dur = int(h) * 3600 + int(m) * 60 + float(s)
        if line.strip().startswith("Stream #0:0"):
            return dur, line.strip()
    return dur, ""


def audio(path: str):
    wav = "/tmp/_verify.wav"
    subprocess.run([C.FF, "-y", "-hide_banner", "-nostdin", "-loglevel", "error",
                    "-i", path, "-ac", "1", "-ar", "8000", "-f", "wav", wav], check=True)
    w = wave.open(wav)
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return a, w.getframerate()


def main() -> None:
    dur, vstream = probe(OUT)
    rows, total = C.timeline()
    print(f"file      {OUT}")
    print(f"duration  {dur:.2f}s   expected {total:.2f}s")
    print(f"video     {vstream}")
    print(f"size      {os.path.getsize(OUT) / 1024 / 1024:.1f} MB")

    a, sr = audio(OUT)
    print(f"audio     {len(a) / sr:.2f}s")

    # جهارة كل فصل في الفيلم النهائي
    print("\nper-chapter loudness (RMS dBFS)")
    for i, (start, name) in enumerate(rows):
        end = rows[i + 1][0] if i + 1 < len(rows) else total
        seg = a[int(start * sr):int((end - 0.6) * sr)]
        if len(seg) < sr:
            continue
        rms = 20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9)
        print(f"  {start:7.2f}s  {name:<28} {rms:6.1f}")

    # الفراغات غير المقصودة
    win = sr // 2
    sil = []
    for i in range(0, len(a) - win, win):
        if 20 * np.log10(np.sqrt((a[i:i + win] ** 2).mean()) + 1e-9) < -55:
            sil.append(i / sr)
    groups = []
    for t in sil:
        if groups and t - groups[-1][1] <= 0.6:
            groups[-1][1] = t
        else:
            groups.append([t, t])
    long_sil = [(round(s, 1), round(e - s + 0.5, 1)) for s, e in groups if e - s >= 1.5]
    print(f"\nsilences >=1.5s: {long_sil if long_sil else 'none'}")

    # ترجمة: آخر مقطع يجب أن ينتهي قبل بطاقة الختام
    srt = f"{C.OUTDIR}/CAPTIONS_EN.srt"
    if os.path.exists(srt):
        txt = open(srt, encoding="utf-8").read().strip().split("\n\n")
        last = txt[-1].split("\n")[1]
        print(f"srt cues  {len(txt)}  last: {last}  (end card starts {rows[-1][0]:.2f}s)")

    print("\nOK" if abs(dur - total) < 1.0 and os.path.getsize(OUT) < 100 * 1024 * 1024
          else "\nCHECK NEEDED")


if __name__ == "__main__":
    main()
