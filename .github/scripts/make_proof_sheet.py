"""يبنى لوحة مراجعة من إطارات البرهان ويحفظها base64 في reports/proof_sheet.json"""
import base64, io, json
from pathlib import Path

rv = Path("_review")
out = Path("reports")
out.mkdir(parents=True, exist_ok=True)

try:
    from PIL import Image, ImageDraw
except Exception as e:
    print("PIL missing:", e)
    raise SystemExit(0)

fr = sorted(rv.glob("p_*.png"), key=lambda p: float(p.stem.split("_")[1]))
if not fr:
    print("no frames")
    raise SystemExit(0)

ims = [(p.stem.split("_")[1] + "s", Image.open(p).convert("RGB")) for p in fr]
tw, th = ims[0][1].size
cols, pad, lab = 4, 5, 18
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw + (cols + 1) * pad, rows * (th + lab) + (rows + 1) * pad), (14, 13, 12))
d = ImageDraw.Draw(sheet)
for i, (lbl, im) in enumerate(ims):
    c, r = i % cols, i // cols
    x, y = pad + c * (tw + pad), pad + r * (th + lab + pad)
    sheet.paste(im, (x, y + lab))
    d.text((x + 2, y + 3), lbl, fill=(205, 172, 110))

buf = io.BytesIO()
sheet.save(buf, format="JPEG", quality=88, optimize=True)
(out / "proof_sheet.json").write_text(
    json.dumps({"frames": len(ims), "jpeg_b64": base64.b64encode(buf.getvalue()).decode()})
)
print("sheet ok", len(ims), sheet.size)
