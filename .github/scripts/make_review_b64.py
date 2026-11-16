#!/usr/bin/env python3
"""يحوّل إطارات المراجعة إلى base64 داخل JSON صغير يمكن الالتزام به في المستودع.

السبب: تنزيل Artifacts من داخل بيئة معزولة يفشل أحيانًا (EOF من blob storage)،
بينما دفع المستودع يعمل دائمًا. هذا الملف يجعل مراجعة الإطارات ممكنة بدون artifact.
"""
import base64
import glob
import json
import pathlib

OUT_DIR = pathlib.Path("_review")
OUT_DIR.mkdir(exist_ok=True)

frames = {}
for f in sorted(glob.glob(str(OUT_DIR / "*.png"))):
    frames[pathlib.Path(f).stem] = base64.b64encode(pathlib.Path(f).read_bytes()).decode()

probe = OUT_DIR / "probe.json"
payload = {
    "frames": frames,
    "probe": probe.read_text(encoding="utf-8") if probe.exists() else None,
}

(OUT_DIR / "b64.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
(OUT_DIR / "b64.txt").write_text(
    f"frames={len(frames)} bytes={len(json.dumps(payload))}\n", encoding="utf-8"
)
print(f"encoded {len(frames)} frames")
