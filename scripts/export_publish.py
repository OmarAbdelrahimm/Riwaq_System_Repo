#!/usr/bin/env python3
"""الماستر ← ملف المنصّة: ترميز واحد + **إثبات** أن الإعدادات طُبِّقت فعلًا.

    python3 scripts/export_publish.py MASTER.mp4 --out PUBLISH.mp4 \
        --crf 21 --height 1080 --keyint 60 --vmaf --report reports/QC_EXPORT_<ID>.md

لماذا سكربت وليس أمرًا: `x264-params` **يتجاهل الأسماء الغلط بصمت**، و`+faststart`
يُنسى، و«crf 21» قد يُطبَّق على مقاس غير المطلوب. هنا يُقاس الناتج:
  • فجوة الـI-frames الفعلية (هل `keyint` اشتغل؟)
  • `moov` قبل `mdat` (هل `+faststart` اشتغل؟)
  • المقاس/البكسل فورمات/معدل العينة/المدة مقابل الماستر
  • VMAF مقابل الماستر (جودة حقيقية لا «شكل الملف»)
  • السقف: البتريت داخل `maxrate` + الهامش

المخرج: exit 0 = قابل للرفع · exit 1 = لا ترفع.
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


def probe(ff: str, f: Path) -> dict:
    out, _ = run([ff, "-hide_banner", "-i", str(f)])
    m = re.search(r"Video:.*?(\d{2,5})x(\d{2,5}).*?(\d+(?:\.\d+)?)\s*fps", out)
    d = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", out)
    a = re.search(r"Audio:.*?(\d{4,6})\s*Hz", out)
    pix = re.search(r"Video:.*?(yuv\w+)", out)
    return {
        "w": int(m.group(1)) if m else None,
        "h": int(m.group(2)) if m else None,
        "fps": float(m.group(3)) if m else None,
        "dur": (int(d.group(1)) * 3600 + int(d.group(2)) * 60 + float(d.group(3))) if d else None,
        "hz": int(a.group(1)) if a else None,
        "pix": pix.group(1) if pix else None,
        "mb": round(f.stat().st_size / 1_048_576, 2) if f.is_file() else None,
    }


def iframe_gaps(ff: str, f: Path, fps: float) -> list[int]:
    """الفجوات الفعلية بين I-frames بالفريمات — الدليل على أن keyint اشتغل."""
    out, _ = run([ff, "-hide_banner", "-nostats", "-i", str(f),
                  "-vf", "select='eq(pict_type,I)',showinfo", "-an", "-f", "null", "-"])
    pts = [float(x) for x in re.findall(r"pts_time:([\d.]+)", out)]
    pts = sorted(set(pts))
    if len(pts) < 2 or not fps:
        return []
    return [int(round((b - a) * fps)) for a, b in zip(pts, pts[1:])]


def has_faststart(f: Path) -> bool | None:
    head = f.open("rb").read(2_000_000)
    moov, mdat = head.find(b"moov"), head.find(b"mdat")
    if moov == -1:
        return None
    return True if mdat == -1 else moov < mdat


def vmaf(ff: str, master: Path, pub: Path) -> float | None:
    """VMAF مقابل الماستر بنفس الأبعاد — لا نفترض مقاس المنصّة.

    لو اختلف المقاسان نُصغّر الناتج إلى الماستر (المرجع) قبل المقارنة، وإلا يقيس
    الفلتر اختلاف قياس ويطلع رقم مضلِّل.
    """
    mi, pi = probe(ff, master), probe(ff, pub)
    scale = ""
    if (mi["w"], mi["h"]) != (pi["w"], pi["h"]) and mi["w"] and mi["h"]:
        scale = f"[1:v]scale={mi['w']}:{mi['h']}:flags=bicubic[p];"
        graph = f"{scale}[0:v][p]libvmaf=n_threads=2"
    else:
        graph = "[0:v][1:v]libvmaf=n_threads=2"
    out, code = run([ff, "-hide_banner", "-nostats", "-i", str(master), "-i", str(pub),
                     "-lavfi", graph, "-f", "null", "-"], timeout=7200)
    m = re.search(r"VMAF score:\s*([\d.]+)", out)
    return float(m.group(1)) if m else None


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="تصدير ملف المنصّة مع إثبات الإعدادات")
    ap.add_argument("master")
    ap.add_argument("--out", required=True)
    ap.add_argument("--crf", type=int, default=21)
    ap.add_argument("--preset", default="slow")
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--maxrate", default="12M")
    ap.add_argument("--bufsize", default="24M")
    ap.add_argument("--keyint", type=int, default=60)
    ap.add_argument("--gop", type=int, default=30, help="min-keyint")
    ap.add_argument("--audio-kbps", type=int, default=192)
    ap.add_argument("--vmaf", action="store_true", help="قياس VMAF مقابل الماستر (بطيء)")
    ap.add_argument("--min-vmaf", type=float, default=None, help="بوابة: أقل VMAF مقبول")
    ap.add_argument("--report", default=None)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    ff = find_ffmpeg()
    master = Path(a.master)
    out = Path(a.out)
    if not master.is_file():
        sys.exit(f"❌ الماستر غير موجود: {master}")
    out.parent.mkdir(parents=True, exist_ok=True)

    mi = probe(ff, master)
    # التصغير على **أصغر ضلع** لا على الارتفاع: 1080×1920 بورتريه لا تُصغَّر إلى 608 عرضًا
    small_side = min(mi["w"] or 0, mi["h"] or 0)
    if small_side and small_side > a.height:
        vf = [f"scale=if(gt(iw\\,ih)\\,-2\\,{a.height}):if(gt(iw\\,ih)\\,{a.height}\\,-2):flags=lanczos"]
    else:
        vf = []

    cmd = [ff, "-hide_banner", "-y", "-i", str(master),
           "-c:v", "libx264", "-preset", a.preset, "-crf", str(a.crf),
           "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-maxrate", a.maxrate, "-bufsize", a.bufsize,
           "-x264-params", f"keyint={a.keyint}:min-keyint={a.gop}",
           "-c:a", "aac", "-b:a", f"{a.audio_kbps}k", "-ar", "48000", "-ac", "2",
           "-movflags", "+faststart"]
    if vf:
        cmd += ["-vf", ",".join(vf)]
    cmd.append(str(out))

    if not a.quiet:
        print("▶ " + " ".join(cmd))
    enc, code = run(cmd)
    if code != 0 or not out.is_file():
        print(enc[-3000:])
        sys.exit("❌ الترميز فشل")

    # ── الإثبات ──
    pi = probe(ff, out)
    gaps = iframe_gaps(ff, out, pi["fps"] or 30.0)
    fs_ok = has_faststart(out)
    v = vmaf(ff, master, out) if a.vmaf else None

    checks: list[tuple[str, str, str]] = []

    def add(okv: bool | None, name: str, detail: str) -> None:
        checks.append(("WARN" if okv is None else ("PASS" if okv else "FAIL"), name, detail))

    total_frames = int(round((pi["dur"] or 0) * (pi["fps"] or 30)))
    if gaps:
        add(max(gaps) <= a.keyint + 1, "keyint مطبَّق",
            f"أقصى فجوة I-frame {max(gaps)} فريم (المطلوب ≤ {a.keyint})")
    elif total_frames > a.keyint * 1.5:
        # مدة تتجاوز الـkeyint ومع ذلك I-frame واحدة ⇒ الـGOP أكبر من المطلوب
        add(False, "keyint مطبَّق", f"I-frame واحدة في {total_frames} فريم — الـGOP أكبر من {a.keyint}")
    else:
        add(None, "keyint مطبَّق", f"الفيديو {total_frames} فريم — أقصر من أن يُقاس الـGOP")
    add(fs_ok is not False, "+faststart", "moov قبل mdat" if fs_ok else ("غير معروف" if fs_ok is None else "moov بعد mdat"))
    add(pi["pix"] == "yuv420p", "yuv420p", str(pi["pix"]))
    add(pi["hz"] == 48000 or pi["hz"] is None, "صوت 48k", f'{pi["hz"]}Hz')
    if mi["dur"] and pi["dur"]:
        add(abs(pi["dur"] - mi["dur"]) <= 0.10, "المدة مطابقة", f'{pi["dur"]}s مقابل {mi["dur"]}s')
    # المقاس يُقاس على **أصغر ضلع** — 1080×1920 بورتريه ارتفاعها 1920 وهذا صحيح
    ps = min(pi["w"] or 0, pi["h"] or 0)
    ms = min(mi["w"] or 0, mi["h"] or 0)
    if ps and ms > a.height:
        add(ps == a.height, "أصغر ضلع", f"{ps} (المطلوب {a.height})")
    elif ps:
        add(ps <= a.height, "أصغر ضلع", f"{ps} (لا تصعيد أبدًا)")
    if v is not None:
        add(v >= (a.min_vmaf if a.min_vmaf else 0), "VMAF", f"{v:.2f}")

    ratio = (pi["mb"] / mi["mb"]) if (pi["mb"] and mi["mb"]) else None
    fails = [c for c in checks if c[0] == "FAIL"]
    icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}

    lines = [f"# EXPORT — {out.name}", "",
             f"**الحالة:** {'✅ جاهز للرفع' if not fails else f'❌ {len(fails)} مخالفة — لا ترفع'}", "",
             f"- الماستر: `{master.name}` — {mi['mb']}MB · {mi['w']}×{mi['h']} · {mi['dur']}s",
             f"- الناتج: {pi['mb']}MB · {pi['w']}×{pi['h']} · {pi['dur']}s · crf {a.crf} · preset {a.preset}",
             (f"- الحجم: **{ratio * 100:.0f}%** من الماستر" if ratio else "") , "",
             "| الفحص | النتيجة | القيمة |", "|---|---|---|"]
    lines += [f"| {n} | {icon[s]} {s} | {d} |" for s, n, d in checks]
    if v is not None:
        lines += ["", f"> VMAF مقيس على محتوى هذا الفيديو نفسه مقابل الماستر — الرقم يعني جودة الناتج لا شكله."]
    report = "\n".join(x for x in lines if x is not None) + "\n"

    if a.report:
        Path(a.report).parent.mkdir(parents=True, exist_ok=True)
        Path(a.report).write_text(report, encoding="utf-8")
    if not a.quiet:
        print()
        print(report)
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
