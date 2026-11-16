"""يبني صورة مراجعة واحدة (contact sheet) من إطارات الفيديو ويحقنها كـ base64
داخل README الحلقة، فيراها المراجع من المستودع مباشرة بلا تحميل artifacts."""
import base64, io, json, os
from pathlib import Path

ROOT = Path(".").resolve()
REVIEW = ROOT / "_review"
REPORT = Path(os.environ.get("SHEET_OUT", "reports/frames_sheet.json"))

try:
    from PIL import Image, ImageDraw
except Exception as exc:  # noqa: BLE001
    print(f"[sheet] PIL غير متاح: {exc}")
    raise SystemExit(0)

frames = sorted(REVIEW.glob("f_*.png"), key=lambda p: int(p.stem.split("_")[1]))
if not frames:
    print("[sheet] لا إطارات")
    raise SystemExit(0)

ims = [(p.stem.split("_")[1] + "s", Image.open(p).convert("RGB")) for p in frames]
tw, th = ims[0][1].size
cols, pad, lab = 5, 4, 14
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw + (cols + 1) * pad, rows * (th + lab) + (rows + 1) * pad), (14, 13, 11))
d = ImageDraw.Draw(sheet)
for i, (lbl, im) in enumerate(ims):
    c, r = i % cols, i // cols
    x, y = pad + c * (tw + pad), pad + r * (th + lab + pad)
    sheet.paste(im, (x, y + lab))
    d.text((x + 2, y + 2), lbl, fill=(214, 176, 106))

buf = io.BytesIO()
sheet.save(buf, format="JPEG", quality=86, optimize=True)
b64 = base64.b64encode(buf.getvalue()).decode()
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(json.dumps({"frames": len(ims), "jpeg_b64": b64}, ensure_ascii=False))
print(f"[sheet] {len(ims)} إطار → {REPORT} ({len(b64)//1024} KB base64)")
