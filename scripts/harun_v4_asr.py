"""HARUN v4 — كلمات الصوت بتوقيت مفرد (Whisper small عبر faster-whisper).

المخرج: /home/user/words_raw.json  — 52 مقطعًا / 241 كلمة
"""
from __future__ import annotations

import json
import subprocess
import wave

from faster_whisper import WhisperModel

FF = ("/home/user/.venv_tools/lib/python3.11/site-packages/imageio_ffmpeg/binaries/"
      "ffmpeg-linux-x86_64-v7.0.2")
VO = ("/home/user/Riwaq_System_Repo/google_drive/"
      "‎⁨الصوت قصة هارون الرشيد والرجل الحكيم 2⁩.wav")
WAV16 = "/tmp/vo16k.wav"
OUT = "/home/user/words_raw.json"

subprocess.run([FF, "-v", "error", "-i", VO, "-ac", "1", "-ar", "16000",
                "-c:a", "pcm_s16le", "-y", WAV16], check=True)

model = WhisperModel("/home/user/mdl/x/package", device="cpu", compute_type="int8")
segs, info = model.transcribe(WAV16, language="ar", beam_size=5, word_timestamps=True,
                              condition_on_previous_text=False, vad_filter=False)

data = {"language": info.language, "duration": None, "segments": []}
for s in segs:
    data["segments"].append({
        "start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip(),
        "words": [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3),
                   "p": round(w.probability, 3)} for w in (s.words or [])],
    })
with wave.open(WAV16) as f:
    data["duration"] = f.getnframes() / f.getframerate()

json.dump(data, open(OUT, "w"), ensure_ascii=False, indent=1)
print("segments", len(data["segments"]),
      "words", sum(len(s["words"]) for s in data["segments"]),
      "dur", round(data["duration"], 3))
