import json, subprocess, glob, os
from pathlib import Path
out = Path("_tmp/ref/out")
wav = out / "audio_16k_mono.wav"
res = {}
try:
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    segs, info = m.transcribe(str(wav), beam_size=5)
    segs = list(segs)
    res["language"] = info.language
    res["prob"] = round(info.language_probability, 3)
    res["segments"] = [{"start": round(s.start,2), "end": round(s.end,2), "text": s.text.strip()} for s in segs]
except Exception as e:
    res["error"] = f"{type(e).__name__}: {e}"[:400]
print(json.dumps(res, ensure_ascii=False, indent=2))

# OCR across frames
ocr = []
for p in sorted(glob.glob("_tmp/ref/out/hero_*.png")):
    r = subprocess.run(["tesseract", p, "-", "--psm", "6"], capture_output=True, text=True)
    txt = " ".join(r.stdout.split())
    if txt:
        ocr.append({"frame": os.path.basename(p), "text": txt})
res["ocr"] = ocr
print(json.dumps(ocr, ensure_ascii=False, indent=2)[:3000])
(out / "asr.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
