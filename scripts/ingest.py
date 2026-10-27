#!/usr/bin/env python3
"""استقبال ملف كبير مقسّم إلى أجزاء — بلا إعادة ترميز وبلا فقد.

القيد المقيس: القناة لا تسلّم ملفًا أكبر من 100MB، والخروج الشبكي إلى Drive
مسدود من بيئة العمل. الطريق الوحيد لملف ماستر كبير هو **تقسيمه بايتات** ثم
رفع الأجزاء؛ الضم هنا يعيد الملف الأصلي **مطابقًا بالبايت**.

    # على جهازك (مرة واحدة)
    split -b 90m MASTER.mp4 part_
    # ارفع part_aa part_ab … ثم عندي:
    python3 scripts/ingest.py ~/Downloads/parts --name MASTER.mp4 \
        --out /tmp/ingest/MASTER.mp4

يقبل أيضًا: `zip -s 90m` (.z01/.zip) أو أي أجزاء بترتيب أسمائها.
يتحقق: تتابع الأحجام (كل الأجزاء غير الأخيرة متساوية) · توقيع ftyp/moov ·
`ffmpeg -f null` · ويطبع sha256 للمطابقة على جهازك.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def find_ffmpeg() -> str | None:
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
    return shutil.which("ffmpeg")


def natural_key(p: Path):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", p.name)]


def collect(folder: Path) -> list[Path]:
    """أجزاء الملف بترتيبها الطبيعي، مع تجاهل ما ليس جزءًا.

    - `part_aa…` / `chunk_01…`    → ترتيب أبجدي/رقمي
    - `x.zip.001/002…`            → ترتيب رقمي
    - `x.z01 x.z02 x.zip`         → z01… ثم zip (ترتيب zip -s)
    """
    files = [p for p in folder.iterdir() if p.is_file()]
    zparts = sorted([p for p in files if re.search(r"\.z\d{2}$", p.name, re.I)], key=natural_key)
    zmains = [p for p in files if p.suffix.lower() == ".zip" and zparts]
    if zparts:
        return zparts + zmains
    return sorted(files, key=natural_key)


def sha256(p: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="ضم أجزاء ملف كبير والتحقق منه")
    ap.add_argument("parts_dir")
    ap.add_argument("--name", default="MASTER.mp4", help="اسم الملف الناتج")
    ap.add_argument("--out", default=None)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    folder = Path(a.parts_dir).expanduser()
    if not folder.is_dir():
        sys.exit(f"❌ المجلد غير موجود: {folder}")

    parts = collect(folder)
    if not parts:
        sys.exit("❌ لا أجزاء داخل المجلد")

    sizes = [p.stat().st_size for p in parts]
    out = Path(a.out) if a.out else folder / a.name
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("wb") as w:
        for p in parts:
            with p.open("rb") as r:
                shutil.copyfileobj(r, w, 1 << 20)

    total = out.stat().st_size
    problems = []

    # 1) تتابع الأحجام: كل الأجزاء غير الأخيرة متساوية (علامة تقسيم سليم)
    if len(parts) > 1:
        head = sizes[:-1]
        if len(set(head)) != 1:
            problems.append(f"أحجام الأجزاء غير متساوية: {sorted(set(head))} — الجزء الأخير وحده يُسمح أن يختلف")

    # 2) توقيع الملف: MP4 يبدأ بـftyp داخل أول 64 بايت
    with out.open("rb") as f:
        head = f.read(64)
    is_mp4 = b"ftyp" in head
    if not is_mp4 and out.suffix.lower() in {".mp4", ".mov", ".m4v"}:
        problems.append("التوقيع ليس ftyp — الملف قد يكون تالفًا أو ترتيب الأجزاء خطأ")

    # 3) سلامة الفك
    ff = find_ffmpeg()
    decode = "غير مقيس (ffmpeg غير متاح)"
    dur = None
    if ff:
        r = subprocess.run([ff, "-hide_banner", "-v", "error", "-i", str(out), "-f", "null", "-"],
                           capture_output=True, text=True)
        errs = [ln for ln in (r.stdout + r.stderr).splitlines() if ln.strip()]
        decode = "سليم" if (r.returncode == 0 and not errs) else f"{len(errs)} خطأ"
        if errs:
            problems.append(f"فك الترميز أعطى {len(errs)} خطأ")
        probe = subprocess.run([ff, "-hide_banner", "-i", str(out)], capture_output=True, text=True)
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", probe.stderr)
        if m:
            dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))

    digest = sha256(out)
    if not a.quiet:
        print(f"# INGEST — {out.name}")
        print(f"الأجزاء: {len(parts)} ({', '.join(p.name for p in parts[:6])}{' …' if len(parts) > 6 else ''})")
        print(f"الحجم: {total / 1_048_576:.2f}MB · المدة: {dur if dur else 'غير مقيس'}s · الفك: {decode}")
        print(f"sha256: {digest}")
        print(f"mp4: {'نعم' if is_mp4 else 'لا'}")
        if problems:
            print("\n❌ مشاكل:")
            for p in problems:
                print(f"- {p}")
        else:
            print("\n✅ الضم سليم — قارن sha256 بالقيمة على جهازك قبل أي معالجة")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
