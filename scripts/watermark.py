#!/usr/bin/env python3
"""خطوة العلامة المائية — على ملف المنصّة، من أول فريم لآخر فريم.

    python3 scripts/watermark.py PUBLISH.mp4 \\
        --out PUBLISH_WM.mp4 \\
        --asset assets/riwaq-watermark-gold.svg \\
        --aspect 16x9 --size 72 --opacity 0.80

لماذا على ملف المنصّة لا على الماستر: الماستر يجب أن يبقى **بلا حرق** (قابل
لإعادة الاستخدام والتعديل)، والعلامة تُعاد بناؤها من SVG في أي وقت.

الأمانة في القياس: `+faststart` و`keyint` لا يُدَّعى أنهما محفوظان — يُقاسان بعد
الخطوة (نفس فحص `export_publish.py`)، لأن `-c:v copy` مع فلتر إجباري يعني
إعادة ترميز صامتة لو نُسي `-filter_complex` الصحيح.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# (top_px, side_px) للمنطقة الآمنة لكل اتجاه — من data/brand.json
SAFE = {
    "16x9": (80, 90),
    "9x16": (220, 64),
    "1x1": (120, 80),
    "4x5": (160, 72),
}


def find_ffmpeg() -> str:
    env = os.environ.get("FFMPEG")
    if env and Path(env).exists():
        return env
    try:
        import imageio_ffmpeg  # type: ignore
        p = imageio_ffmpeg.get_ffmpeg_exe()
        if p and Path(p).exists():
            return p
    except Exception:
        pass
    p = shutil.which("ffmpeg")
    if p:
        return p
    sys.exit("❌ ffmpeg غير متاح — $FFMPEG أو: pip install imageio-ffmpeg")


def run(cmd: list[str], timeout: int = 3600) -> tuple[str, int]:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return (r.stdout or "") + (r.stderr or ""), r.returncode


def rasterize(svg: Path, width_px: int = 512) -> Path:
    """SVG → PNG بخلفية شفافة. resvg أولًا (دقيق مع `stroke-linecap`)، ثم cairosvg."""
    out = Path("/tmp") / f"wm_{svg.stem}_{width_px}.png"
    if out.is_file():
        return out
    node = shutil.which("node")
    if node:
        js = Path("/tmp/svgtool/node_modules/@resvg/resvg-js")
        if js.is_dir():
            script = f"""
const {{Resvg}} = require({json.dumps(str(js))});
const fs = require('fs');
const r = new Resvg(fs.readFileSync({json.dumps(str(svg))}, 'utf8'),
                    {{fitTo: {{mode: 'width', value: {width_px}}}}});
fs.writeFileSync({json.dumps(str(out))}, r.render().asPng());
"""
            r = subprocess.run([node, "-e", script], capture_output=True, text=True)
            if out.is_file():
                return out
            print(r.stderr[-500:], file=sys.stderr)
    try:
        import cairosvg  # type: ignore
        cairosvg.svg2png(url=str(svg), write_to=str(out), output_width=width_px)
        if out.is_file():
            return out
    except Exception:
        pass
    sys.exit("❌ لم أستطع تحويل الـSVG — مرّر PNG جاهزًا بـ--png "
             "(أو: cd /tmp && npm i @resvg/resvg-js)")


def add_halo(png: Path, strength: float = 0.50, radius: int = 5) -> Path:
    """هالة داكنة ناعمة حول العلامة — قرار مقيس لا ذوق.

    القياس (2026-10-27، مشهد 1280×720 من حلقة هارون): سطوع الزاوية العليا اليسرى
    0.384 في البداية و0.509 في مشهد الشجرة. عند 0.509 الذهبي على أوراق فاتحة
    بيفقد حدّه، والهالة تعيد الفصل بلا صندوق. نفس عتبة لوحة الكابشن (0.46).
    """
    try:
        from PIL import Image, ImageFilter
    except Exception:
        return png
    src = Image.open(png).convert("RGBA")
    alpha = src.split()[3]
    dilated = alpha.filter(ImageFilter.MaxFilter(radius)).filter(ImageFilter.GaussianBlur(1.0))
    halo = Image.new("RGBA", src.size, (26, 23, 20, 0))
    halo.putalpha(dilated.point(lambda v: int(v * strength)))
    out = Path("/tmp") / f"{png.stem}_halo{int(strength * 100)}.png"
    Image.alpha_composite(halo, src).save(out)
    return out


def probe_size(ff: str, f: Path) -> tuple[int, int]:
    out, _ = run([ff, "-hide_banner", "-i", str(f)])
    m = re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", out)
    if not m:
        sys.exit("❌ لم أقرأ أبعاد الفيديو")
    return int(m.group(1)), int(m.group(2))


def iframe_gap(ff: str, f: Path, fps: float) -> int | None:
    out, _ = run([ff, "-hide_banner", "-nostats", "-i", str(f),
                  "-vf", "select='eq(pict_type,I)',showinfo", "-an", "-f", "null", "-"])
    pts = sorted({float(x) for x in re.findall(r"pts_time:([\d.]+)", out)})
    if len(pts) < 2 or not fps:
        return None
    return max(int(round((b - a) * fps)) for a, b in zip(pts, pts[1:]))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="حرق العلامة المائية من أول فريم")
    ap.add_argument("video")
    ap.add_argument("--out", required=True)
    ap.add_argument("--asset", default="assets/riwaq-watermark-gold.svg")
    ap.add_argument("--png", default=None, help="PNG بديل (لو الـSVG غير مقروء)")
    ap.add_argument("--aspect", default="16x9", choices=sorted(SAFE))
    ap.add_argument("--size", type=int, default=72, help="العرض بالبكسل عند 1080 (من الثيم)")
    ap.add_argument("--opacity", type=float, default=0.80)
    ap.add_argument("--position", default="top-left",
                    choices=["top-left", "top-center", "top-right", "bottom-right"])
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--preset", default="slow")
    ap.add_argument("--keyint", type=int, default=60)
    ap.add_argument("--halo", type=float, default=0.50,
                    help="قوة الهالة الداكنة حول العلامة (0 = بلا هالة، من الثيم 0.5)")
    ap.add_argument("--halo-radius", type=int, default=5)
    ap.add_argument("--qc", default=None, help="تقرير md للتحقق")
    ap.add_argument("--verify-only", action="store_true",
                    help="تحقق من ملف ناتج موجود بلا إعادة ترميز")
    a = ap.parse_args(argv)

    ff = find_ffmpeg()
    src = Path(a.video)
    out = Path(a.out)
    if not src.is_file():
        sys.exit(f"❌ الملف غير موجود: {src}")

    ref = a.png or a.asset
    if not Path(ref).is_file():
        sys.exit(f"❌ أصل العلامة غير موجود: {ref}")

    # هذه النسخة من ffmpeg تُعلن svg بلا decoder ⇒ الـSVG يُرسم أولًا إلى PNG.
    # (المسار الوحيد البديل هو إدخال SVG عبر librsvg، وهو غير مبني هنا.)
    if Path(ref).suffix.lower() == ".svg":
        ref = str(rasterize(Path(ref)))

    if a.halo > 0:
        ref = str(add_halo(Path(ref), a.halo, a.halo_radius))

    w, h = probe_size(ff, src)
    size = round(a.size * w / 1080)          # الثيم مضبوط على 1080
    top, side = SAFE[a.aspect]

    # الموضع داخل المنطقة الآمنة، والعلامة لا تُمدَّد (keep aspect)
    if a.position == "top-left":
        x, y = side, top
    elif a.position == "top-center":
        x, y = f"(main_w-overlay_w)/2", top
    elif a.position == "top-right":
        x, y = f"main_w-overlay_w-{side}", top
    else:
        x, y = f"main_w-overlay_w-{side}", f"main_h-overlay_h-{SAFE[a.aspect][0]}"

    graph = (
        f"[1:v]scale={size}:-1:flags=lanczos,format=rgba,"
        f"colorchannelmixer=aa={a.opacity}[wm];"
        f"[0:v][wm]overlay={x}:{y}:format=auto[v]"
    )
    cmd = [ff, "-hide_banner", "-y", "-i", str(src), "-i", ref,
           "-filter_complex", graph, "-map", "[v]", "-map", "0:a?",
           "-c:v", "libx264", "-preset", a.preset, "-crf", str(a.crf),
           "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-x264-params", f"keyint={a.keyint}:min-keyint=30",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
           "-movflags", "+faststart", str(out)]

    if a.verify_only:
        if not out.is_file():
            sys.exit(f"❌ ملف التحقق غير موجود: {out}")
    else:
        print("▶ سحب العلامة:", Path(a.asset).name,
              f"→ {size}px بعرض {w} · موضع {a.position} · شفافية {a.opacity}")
        log, code = run(cmd)
        if code != 0 or not out.is_file():
            print(log[-3000:])
            sys.exit("❌ فشل الحرق")

    # ── تحقق ──
    gap = iframe_gap(ff, out, 30.0)
    head = out.open("rb").read(2_000_000)
    moov, mdat = head.find(b"moov"), head.find(b"mdat")
    faststart = moov != -1 and (mdat == -1 or moov < mdat)
    def secs(txt: str) -> float | None:
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", txt)
        return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else None

    d_in = secs(run([ff, "-hide_banner", "-i", str(src)])[0])
    d_out = secs(run([ff, "-hide_banner", "-i", str(out)])[0])

    ok_gap = gap is not None and gap <= a.keyint + 1
    ok_fs = bool(faststart)
    # ±0.10s: إعادة الترميز قد تُزيح الإطار الأخير، لا تُغيّر المدة
    ok_dur = bool(d_in and d_out and abs(d_in - d_out) <= 0.10)
    lines = [f"# WATERMARK — {out.name}", "",
             f"- الأصل: `{Path(a.asset).name}` · {size}px · {a.position} · شفافية {a.opacity}"
             + (f" · هالة {a.halo}" if a.halo else " · بلا هالة"),
             f"- الناتج: {out.stat().st_size / 1_048_576:.2f}MB · crf {a.crf}",
             "", "| الفحص | النتيجة | القيمة |", "|---|---|---|",
             f"| keyint | {'✅' if ok_gap else '❌'} | أقصى فجوة {gap} (≤ {a.keyint}) |",
             f"| +faststart | {'✅' if ok_fs else '❌'} | {'moov قبل mdat' if ok_fs else 'moov بعد mdat'} |",
             f"| المدة | {'✅' if ok_dur else '❌'} | {d_out:.2f}s مقابل {d_in:.2f}s |" if (d_in and d_out) else "| المدة | ⚠️ | غير مقيسة |"]
    report = "\n".join(lines) + "\n"
    if a.qc:
        Path(a.qc).parent.mkdir(parents=True, exist_ok=True)
        Path(a.qc).write_text(report, encoding="utf-8")
    print(report)
    return 0 if (ok_gap and ok_fs and ok_dur) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
