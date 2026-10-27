#!/usr/bin/env python3
"""بوابة الأصول — لا مونتاج قبل `exit 0`. المرجع: docs/ASSET_SOURCING.md

لماذا وُجد: كل مرحلة بعد المونتاج تفترض أن الأصل موجود ومصرَّح وفوق الحد الأدنى
من الدقة. هذا السكربت يجعل الافتراض **قاعدة مفحوصة** بدل أمنية.

    python3 scripts/publish/check_asset.py --dir public/projects/<ID>/assets \
        --min-w 1620 --licenses reports/ASSETS_<ID>.md [--shotlist build/shotlist.json]

الفحوص:
  1) الملف يُفتح فعلًا (صورة: قراءة الأبعاد من الرأس · فيديو: ffprobe إن وُجد)
  2) العرض ≥ min_w  (min_w = عرض المخرج × 1.5 · 1080 ⇒ 1620 · 1920 ⇒ 2880)
  3) لا تكرار (md5) — أصلان بنفس البصمة = واحد
  4) لكل ملف سطر رخصة في سجل الحقوق
  5) النوع موجود في الـshotlist (اختياري)

بلا PIL وبلا ffprobe إلزامي: أبعاد الصور تُقرأ من الرأس (PNG/JPEG/WEBP/GIF).
الفيديو يحتاج ffprobe؛ لو غاب ⇒ WARN لا FAIL (لا تُمنع الشغل بسبب بيئة ناقصة).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
VID_EXT = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}


# ─────────────────────────── أبعاد الصور من الرأس ───────────────────────────
def _png_size(f) -> tuple[int, int] | None:
    f.seek(16)
    w, h = struct.unpack(">II", f.read(8))
    return w, h


def _gif_size(f) -> tuple[int, int] | None:
    f.seek(6)
    w, h = struct.unpack("<HH", f.read(4))
    return w, h


def _jpeg_size(f) -> tuple[int, int] | None:
    f.seek(2)
    while True:
        b = f.read(1)
        while b and b != b"\xff":
            b = f.read(1)
        if not b:
            return None
        marker = f.read(1)
        while marker == b"\xff":
            marker = f.read(1)
        if not marker:
            return None
        m = marker[0]
        if m in (0xD8, 0xD9) or 0xD0 <= m <= 0xD7:
            continue
        seg = f.read(2)
        if len(seg) < 2:
            return None
        length = struct.unpack(">H", seg)[0]
        if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
            data = f.read(5)
            if len(data) < 5:
                return None
            h, w = struct.unpack(">HH", data[1:5])
            return w, h
        f.seek(length - 2, os.SEEK_CUR)


def _webp_size(f) -> tuple[int, int] | None:
    f.seek(12)
    chunk = f.read(4)
    if chunk == b"VP8 ":
        f.seek(6, os.SEEK_CUR)
        w, h = struct.unpack("<HH", f.read(4))
        return w & 0x3FFF, h & 0x3FFF
    if chunk == b"VP8L":
        f.seek(1, os.SEEK_CUR)
        b = f.read(4)
        if len(b) < 4:
            return None
        bits = struct.unpack("<I", b)[0]
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if chunk == b"VP8X":
        f.seek(4, os.SEEK_CUR)
        b = f.read(6)
        if len(b) < 6:
            return None
        w = int.from_bytes(b[0:3], "little") + 1
        h = int.from_bytes(b[3:6], "little") + 1
        return w, h
    return None


def image_size(path: Path) -> tuple[int, int] | None:
    try:
        with open(path, "rb") as f:
            head = f.read(12)
            if head.startswith(b"\x89PNG\r\n\x1a\n"):
                return _png_size(f)
            if head[:3] == b"GIF":
                return _gif_size(f)
            if head[:2] == b"\xff\xd8":
                return _jpeg_size(f)
            if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
                return _webp_size(f)
    except OSError:
        return None
    return None


def video_size(path: Path) -> tuple[int, int, float] | None:
    ff = shutil.which("ffprobe")
    if not ff:
        return None
    try:
        out = subprocess.run(
            [ff, "-v", "error", "-select_streams", "v:0", "-show_entries",
             "stream=width,height,duration", "-of", "json", str(path)],
            capture_output=True, text=True, timeout=30, check=True).stdout
        st = json.loads(out)["streams"][0]
        return int(st["width"]), int(st["height"]), float(st.get("duration") or 0)
    except Exception:
        return None


def md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ─────────────────────────────── الفحص ───────────────────────────────
class Gate:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str]] = []
        self.fails = 0
        self.warns = 0

    def add(self, ok: bool | None, name: str, note: str) -> None:
        if ok is None:
            status, self.warns = "WARN", self.warns + 1
        elif ok:
            status = "PASS"
        else:
            status, self.fails = "FAIL", self.fails + 1
        self.rows.append((status, name, note))

    def report(self, title: str) -> bool:
        icon = {"PASS": "✅", "WARN": "⚠️ ", "FAIL": "❌"}
        print(f"\n=== {title} ===")
        for status, name, note in self.rows:
            print(f"{icon[status]} {name.ljust(34)} | {note}")
        print(f"\n{len(self.rows)} أصلًا · {self.fails} FAIL · {self.warns} WARN")
        print("VERDICT:", "NO EDITING" if self.fails else "OK" + (" (with warnings)" if self.warns else ""))
        return self.fails == 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="بوابة الأصول — لا مونتاج قبل exit 0")
    ap.add_argument("--dir", required=True, help="مجلد الأصول")
    ap.add_argument("--min-w", type=int, default=1620, help="أدنى عرض بالبكسل (افتراضي 1620)")
    ap.add_argument("--licenses", help="ملف سجل الحقوق (md) — يفحص وجود سطر لكل ملف")
    ap.add_argument("--shotlist", help="shotlist.json (اختياري)")
    ap.add_argument("--allow-missing-license", action="store_true",
                    help="تنازل صريح: يسمح بملفات بلا رخصة لكن يطبعها WARN (يُذكر في التسليم)")
    ap.add_argument("--write", help="اكتب تقرير البوابة في هذا المسار (md)")
    a = ap.parse_args(argv)

    root = Path(a.dir)
    if not root.is_dir():
        print(f"❌ المجلد غير موجود: {root}", file=sys.stderr)
        return 2

    lic_text = ""
    if a.licenses:
        lp = Path(a.licenses)
        if lp.is_file():
            lic_text = lp.read_text(encoding="utf-8")
        else:
            print(f"❌ سجل الحقوق غير موجود: {lp}", file=sys.stderr)
            return 2

    shot_types: dict[str, str] = {}
    if a.shotlist and Path(a.shotlist).is_file():
        try:
            sl = json.loads(Path(a.shotlist).read_text(encoding="utf-8"))
            for shot in sl.get("shots", sl if isinstance(sl, list) else []):
                asset = shot.get("asset") or shot.get("file")
                if asset:
                    shot_types[Path(asset).name] = shot.get("type", "")
        except (json.JSONDecodeError, AttributeError):
            print("⚠️  shotlist غير قابل للقراءة — تجاهلته")

    files = sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in (IMG_EXT | VID_EXT))
    gate = Gate()
    if not files:
        print(f"❌ صفر أصل في {root}", file=sys.stderr)
        return 1

    seen: dict[str, str] = {}
    for p in files:
        rel = p.name
        ext = p.suffix.lower()
        if ext in IMG_EXT:
            size = image_size(p)
            if not size:
                gate.add(False, rel, "صورة غير مقروءة أو تالفة")
                continue
            w, h = size
            note = f"{w}×{h}"
        else:
            info = video_size(p)
            if info is None:
                gate.add(None, rel, "فيديو — ffprobe غير متاح (تحقق يدويًا)")
                continue
            w, h, dur = info
            note = f"{w}×{h} · {dur:.1f}s"

        gate.add(w >= a.min_w, f"{rel} · العرض", note + ("" if w >= a.min_w else f" < min_w {a.min_w}"))

        digest = md5(p)
        if digest in seen:
            gate.add(False, f"{rel} · تكرار", f"نفس بصمة {seen[digest]}")
        else:
            seen[digest] = rel
            gate.add(True, f"{rel} · فريد", digest[:10])

        if a.licenses:
            has_row = (rel in lic_text) or (p.stem in lic_text)
            if has_row:
                gate.add(True, f"{rel} · رخصة", "سطر موجود في السجل")
            elif a.allow_missing_license:
                gate.add(None, f"{rel} · رخصة", "مفقودة — تنازل مُعلَن")
            else:
                gate.add(False, f"{rel} · رخصة", "لا سطر في سجل الحقوق")

        if shot_types:
            gate.add(rel in shot_types, f"{rel} · shotlist",
                     shot_types.get(rel, "غير مذكور في الـshotlist"))

    ok = gate.report(f"بوابة الأصول — {root} (min_w={a.min_w})")

    if a.write:
        icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}
        lines = [f"# ASSETS GATE — {root.name}", "",
                 f"**min_w:** {a.min_w} · **الحالة:** {'✅ يمر' if ok else '❌ لا مونتاج'}",
                 "", "| الأصل | الفحص | النتيجة |", "|---|---|---|"]
        lines += [f"| {n} | {d} | {icon[s]} {s} |" for s, n, d in gate.rows]
        out = Path(a.write)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"→ {out}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
