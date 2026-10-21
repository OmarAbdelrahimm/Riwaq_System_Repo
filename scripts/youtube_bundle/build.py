#!/usr/bin/env python3
"""Build reproducible Riwaq YouTube publishing assets (MP4s are never handled here)."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "youtube_packages" / "package_manifest.json"
OUTPUT_ROOT = ROOT / "youtube_packages"
SOURCE_FRAMES = OUTPUT_ROOT / "source_frames"
SOURCE_THUMBNAILS = ROOT / "google_drive"
DARK = "#1C1B19"
SURFACE = "#242218"
PARCHMENT = "#F3EBDB"
GOLD = "#A98A4B"
GOLD_LIGHT = "#C2A469"
AMIRI = ROOT / "public" / "fonts" / "Amiri-Bold.ttf"
AMIRI_REGULAR = ROOT / "public" / "fonts" / "Amiri-Regular.ttf"
PLEX = ROOT / "public" / "fonts" / "IBMPlexSansArabic-Medium.ttf"
PLEX_BOLD = ROOT / "public" / "fonts" / "IBMPlexSansArabic-Bold.ttf"
ARABIC_RE = re.compile(r"[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff]")


def shaped(text: str) -> str:
    """Return presentation-form Arabic in visual order for Pillow builds without RAQM."""
    return get_display(arabic_reshaper.reshape(text), base_dir="R")


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def text_bbox(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont) -> tuple[int, int, int, int]:
    return draw.textbbox((0, 0), shaped(text), font=face)


def measure(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont) -> int:
    box = text_bbox(draw, text, face)
    return box[2] - box[0]


def wrap_arabic(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and measure(draw, candidate, face) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def draw_ar_line(
    draw: ImageDraw.ImageDraw,
    text: str,
    *,
    center_x: float,
    top: int,
    face: ImageFont.FreeTypeFont,
    fill: str,
    align: str = "center",
) -> int:
    visual = shaped(text)
    box = draw.textbbox((0, 0), visual, font=face)
    width = box[2] - box[0]
    if align == "right":
        x = int(center_x - box[2])
    else:
        x = int(center_x - (box[0] + box[2]) / 2)
    y = int(top - box[1])
    draw.text((x, y), visual, font=face, fill=fill)
    return box[3] - box[1]


def draw_ar_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    *,
    center_x: float,
    top: int,
    max_width: int,
    face_path: Path,
    face_size: int,
    fill: str,
    max_lines: int = 2,
    align: str = "center",
    line_gap: int | None = None,
) -> tuple[int, list[str], int]:
    size = face_size
    while size >= 60:
        face = font(face_path, size)
        lines = wrap_arabic(draw, text, face, max_width)
        if len(lines) <= max_lines:
            break
        size -= 2
    if len(lines) > max_lines:
        raise ValueError(f"Cover copy does not fit in {max_lines} lines: {text!r}")
    gap = line_gap if line_gap is not None else max(5, round(size * 0.06))
    y = top
    for line in lines:
        height = draw_ar_line(draw, line, center_x=center_x, top=y, face=face, fill=fill, align=align)
        y += height + gap
    return y - gap, lines, size


def render_brand_mark(size: int) -> Image.Image:
    """Draw a lightweight Pillow-only arch-and-jewel Riwaq mark at 4× resolution."""
    scale = 4
    base_width, base_height = 112, 106
    image = Image.new("RGBA", (base_width * scale, base_height * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    def pt(value: float) -> int:
        return round(value * scale)
    arch_width = pt(13)
    # Outer arch (the open, double-line arch in the Riwaq BrandMark component).
    draw.arc((pt(30.5), pt(23.5), pt(89.5), pt(82.5)), 180, 360, fill=GOLD, width=arch_width)
    draw.line((pt(30.5), pt(53), pt(30.5), pt(104)), fill=GOLD, width=arch_width)
    draw.line((pt(89.5), pt(53), pt(89.5), pt(104)), fill=GOLD, width=arch_width)
    draw.line((pt(14), pt(104), pt(106), pt(104)), fill=GOLD, width=pt(5))
    draw.ellipse((pt(53.5), pt(59.5), pt(66.5), pt(72.5)), fill=GOLD_LIGHT)
    return image.resize((size, round(size * 104.98 / 111.48)), Image.Resampling.LANCZOS)


def draw_lockup(canvas: Image.Image, center_x: int, top: int, *, scale: float) -> int:
    draw = ImageDraw.Draw(canvas)
    icon_size = round(57 * scale)
    mark = render_brand_mark(icon_size)
    canvas.paste(mark, (center_x - mark.width // 2, top), mark)
    y = top + mark.height + round(3 * scale)
    name_face = font(AMIRI, round(48 * scale))
    y += draw_ar_line(draw, "رِواق", center_x=center_x, top=y, face=name_face, fill=PARCHMENT) + round(2 * scale)
    tag_face = font(AMIRI_REGULAR, round(19 * scale))
    y += draw_ar_line(draw, "تَارِيخْ وَتُرَاث", center_x=center_x, top=y, face=tag_face, fill=GOLD_LIGHT)
    return y


def make_source_frame(package: dict[str, Any], *, refresh: bool = False) -> Path:
    frame_path = SOURCE_FRAMES / f"{package['id']}.jpg"
    if frame_path.exists() and not refresh:
        return frame_path
    source = SOURCE_THUMBNAILS / package["source_thumbnail_name"]
    if not source.exists():
        raise FileNotFoundError(f"Missing original project thumbnail: {source}")
    image = Image.open(source).convert("RGB")
    if package["kind"] == "long":
        # The right-hand photo panel in the existing approved thumbnail is an actual source-video frame.
        crop = (566, 0, 1280, 720)
    else:
        # Crop the central video still above the subtitle/overlay bands; excludes the lower broadcast bug.
        crop = (184, 535, 896, 935)
    if image.size != ((1280, 720) if package["kind"] == "long" else (1080, 1920)):
        raise ValueError(f"Unexpected source thumbnail dimensions for {package['id']}: {image.size}")
    SOURCE_FRAMES.mkdir(parents=True, exist_ok=True)
    image.crop(crop).save(frame_path, format="JPEG", quality=95, optimize=True, progressive=True)
    return frame_path


def add_photo_panel(canvas: Image.Image, frame_path: Path, box: tuple[int, int, int, int], *, centering: tuple[float, float]) -> None:
    x, y, width, height = box
    with Image.open(frame_path) as original:
        photo = ImageOps.fit(original.convert("RGB"), (width, height), method=Image.Resampling.LANCZOS, centering=centering)
    canvas.paste(photo, (x, y))
    ImageDraw.Draw(canvas).rectangle((x - 2, y - 2, x + width + 1, y + height + 1), outline=GOLD, width=3)


def make_horizontal_cover(package: dict[str, Any], frame_path: Path) -> Image.Image:
    canvas = Image.new("RGB", (1280, 720), DARK)
    draw = ImageDraw.Draw(canvas)
    add_photo_panel(canvas, frame_path, (682, 58, 566, 578), centering=(0.53, 0.43))

    # Arch-and-jewel brand mark, Amiri Arabic lock-up, and IBM Plex secondary copy.
    draw_lockup(canvas, center_x=153, top=45, scale=0.90)
    label = font(PLEX, 29)
    draw_ar_line(draw, "مقتطف من بودكاست بدون ورق", center_x=625, top=207, face=label, fill=GOLD_LIGHT, align="right")
    bottom, _, _ = draw_ar_wrapped(
        draw,
        package["cover_text"],
        center_x=625,
        top=277,
        max_width=545,
        face_path=AMIRI,
        face_size=94,
        fill=PARCHMENT,
        max_lines=2,
        align="right",
        line_gap=5,
    )
    draw.line((516, bottom + 20, 625, bottom + 20), fill=GOLD, width=5)
    credit = font(PLEX_BOLD, 31)
    draw_ar_line(draw, "ياسر الحزيمي  •  رِواق", center_x=625, top=590, face=credit, fill=PARCHMENT, align="right")

    # Gold frame with an intentional lower-right gap for YouTube's duration badge.
    draw.line((28, 28, 1252, 28), fill=GOLD, width=2)
    draw.line((28, 28, 28, 692), fill=GOLD, width=2)
    draw.line((1252, 28, 1252, 634), fill=GOLD, width=2)
    draw.line((28, 692, 1030, 692), fill=GOLD, width=2)
    return canvas


def make_vertical_cover(package: dict[str, Any], frame_path: Path) -> Image.Image:
    canvas = Image.new("RGB", (1080, 1920), DARK)
    draw = ImageDraw.Draw(canvas)
    draw_lockup(canvas, center_x=540, top=37, scale=1.0)

    label = font(PLEX, 31)
    draw_ar_line(draw, "مقتطف معرفي  •  من بودكاست بدون ورق", center_x=540, top=220, face=label, fill=GOLD_LIGHT)
    title_bottom, _, _ = draw_ar_wrapped(
        draw,
        package["cover_text"],
        center_x=540,
        top=275,
        max_width=930,
        face_path=AMIRI,
        face_size=108,
        fill=PARCHMENT,
        max_lines=2,
        align="center",
        line_gap=0,
    )
    draw.line((445, title_bottom + 16, 635, title_bottom + 16), fill=GOLD, width=5)

    add_photo_panel(canvas, frame_path, (50, 600, 980, 551), centering=(0.50, 0.38))
    credit_face = font(PLEX_BOLD, 38)
    draw_ar_line(draw, "ياسر الحزيمي", center_x=540, top=1210, face=credit_face, fill=PARCHMENT)
    source_face = font(PLEX, 30)
    draw_ar_line(draw, "من حلقة «مركزية العلاقة مع الله»", center_x=540, top=1272, face=source_face, fill=GOLD_LIGHT)
    draw_ar_line(draw, "بودكاست بدون ورق", center_x=540, top=1320, face=source_face, fill=PARCHMENT)

    # Thin frame stops above the mobile safe area; the last 240px are deliberately blank.
    draw.line((28, 28, 1052, 28), fill=GOLD, width=2)
    draw.line((28, 28, 28, 1638), fill=GOLD, width=2)
    draw.line((1052, 28, 1052, 1638), fill=GOLD, width=2)
    draw.line((28, 1638, 1052, 1638), fill=GOLD, width=2)
    draw.rectangle((0, 1680, 1079, 1919), fill=DARK)
    return canvas


def parse_srt_blocks(text: str) -> list[list[str]]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
    return [block.splitlines() for block in re.split(r"\n\s*\n", normalized.strip()) if block.strip()]


def build_english_srt(bilingual_path: Path, output_path: Path, expected_cues: int) -> int:
    raw = bilingual_path.read_text(encoding="utf-8-sig")
    blocks = parse_srt_blocks(raw)
    english_blocks: list[str] = []
    for number, lines in enumerate(blocks, start=1):
        if len(lines) < 4 or "-->" not in lines[1]:
            raise ValueError(f"Malformed bilingual SRT block {number} in {bilingual_path}")
        text_lines = [line for line in lines[2:] if line.strip()]
        english_lines = [line for line in text_lines if not ARABIC_RE.search(line)]
        if not english_lines:
            raise ValueError(f"No English text in bilingual SRT block {number}: {bilingual_path}")
        english_blocks.append("\n".join([lines[0], lines[1], *english_lines]))
    if len(english_blocks) != expected_cues:
        raise ValueError(f"Expected {expected_cues} subtitle cues, found {len(english_blocks)} in {bilingual_path}")
    output_path.write_text("\n\n".join(english_blocks) + "\n", encoding="utf-8")
    return len(english_blocks)


def chapter_lines(package: dict[str, Any], language: str) -> list[str]:
    label_key = "label_ar" if language == "ar" else "label_en"
    return [f"{chapter['time']} {chapter[label_key]}" for chapter in package["chapters"]]


def excerpt_lines(manifest: dict[str, Any], package: dict[str, Any], language: str) -> list[str]:
    base = manifest["source_episode"]["url"]
    rows = []
    for excerpt in package["source_ranges"]:
        deep_link = f"{base}&t={excerpt['start_seconds']}s"
        if language == "ar":
            rows.append(f"- {excerpt['start']}–{excerpt['end']} — {deep_link}")
        else:
            rows.append(f"- {excerpt['start']}–{excerpt['end']} — {deep_link}")
    return rows


def description_text(manifest: dict[str, Any], package: dict[str, Any], language: str) -> str:
    source_url = manifest["source_episode"]["url"]
    if language == "ar":
        lines = [package["hook_ar"], "", package["summary_ar"], ""]
        lines.extend(f"• {bullet}" for bullet in package["bullets_ar"])
        if package["chapters"]:
            lines.extend(["", "الفصول:", *chapter_lines(package, "ar")])
        lines.extend(
            [
                "",
                f"مقتطف من حلقة «{manifest['source_episode']['title_ar']}».",
                f"الحلقة كاملة: {source_url}",
                "مواضع المقتطف في المصدر:",
                *excerpt_lines(manifest, package, "ar"),
                "",
                package["cta_ar"],
                "",
                " ".join(package["hashtags_ar"]),
            ]
        )
        return "\n".join(lines)

    lines = [package["hook_en"], "", package["summary_en"], ""]
    lines.extend(f"• {bullet}" for bullet in package["bullets_en"])
    if package["chapters"]:
        lines.extend(["", "Chapters:", *chapter_lines(package, "en")])
    lines.extend(
        [
            "",
            f"Excerpt from ‘{manifest['source_episode']['title_ar']}’.",
            f"Full episode: {source_url}",
            "Excerpt source points:",
            *excerpt_lines(manifest, package, "en"),
            "",
            package["cta_en"],
            "",
            " ".join(package["hashtags_en"]),
        ]
    )
    return "\n".join(lines)


def write_seo_markdown(manifest: dict[str, Any], package: dict[str, Any], out: Path, tags: str) -> tuple[int, int]:
    description_ar = description_text(manifest, package, "ar")
    description_en = description_text(manifest, package, "en")
    if description_ar.count("#") != 3 or description_en.count("#") != 3:
        raise ValueError(f"Description must contain exactly three hashtags per language: {package['id']}")
    chapters_note = (
        "الفصول مأخوذة من نقاط القطع الفعلية في النسخة النهائية ومراجعة على SRT الموقّت."
        if package["chapters"]
        else "لا فصول زمنية: هذا مقطع قصير واحد؛ لا تُضاف توقيتات مصطنعة."
    )
    checklist = [
        "[ ] تثبيت العنوان العربي النهائي أو اختيار أحد البديلين بعد مراجعة منصة النشر.",
        "[ ] رفع ملف الفيديو النهائي من Drive كما هو؛ لا إعادة ترميز.",
        "[ ] رفع الغلاف الأفقي 1280×720 واختبار ظهوره على الهاتف وسطح المكتب.",
        "[ ] إرفاق الغلاف العمودي 1080×1920؛ مساحة آخر 240px خالية.",
        "[ ] إضافة الترجمة العربية–الإنجليزية وملف English-only، والتأكد من لغة الفيديو العربية.",
        f"[ ] نسخ الوصف العربي كما هو؛ عدد الوسوم {len(tags)} حرفًا (المستهدف 400–500).",
        "[ ] التحقق من روابط الحلقة الكاملة وروابط المقتطف عند إدخالها في Studio.",
        "[ ] مراجعة الفصول على خطّ الزمن النهائي قبل النشر.",
        "[ ] اختيار التصنيف التعليمي، ومراجعة إعداد الجمهور وفق سياسة القناة.",
        "[ ] تثبيت التعليق المقترح، ثم مراجعة الخصوصية وموعد النشر.",
    ]
    content = [
        f"# حزمة نشر YouTube — {package['id']}",
        "",
        "## العنوان العربي النهائي",
        package["title"],
        "",
        "## بديلان للعنوان",
        f"1. {package['title_alternatives'][0]}",
        f"2. {package['title_alternatives'][1]}",
        "",
        "## الوصف العربي — جاهز للنسخ",
        "```text",
        description_ar,
        "```",
        "",
        "## الوسوم (Tags)",
        f"عدد الأحرف: {len(tags)} (الهدف 400–500).",
        "```text",
        tags,
        "```",
        "",
        "## التعليق المثبّت المقترح",
        package["pinned_comment_ar"],
        "",
        "## English title",
        package["title_en"],
        "",
        "## English description — copy-ready",
        "```text",
        description_en,
        "```",
        "",
        "## Suggested pinned comment (English fallback)",
        package["cta_en"],
        "",
        "## إعدادات النشر المقترحة",
        "- الفئة: Education / التعليم.",
        "- لغة الفيديو: العربية؛ الترجمتان: العربية والإنجليزية.",
        f"- الأبعاد النهائية: {package['frame_size']}؛ المدة: {package['duration_seconds']:.2f} ثانية.",
        "- نسبة المصدر: حلقة «مركزية العلاقة مع الله» — ياسر الحزيمي — بودكاست بدون ورق.",
        f"- ملاحظة الفصول: {chapters_note}",
        "- الأوقات المكتوبة في فقرة المصدر هي أوقات الحلقة الأصلية؛ أما الفصول فهي أوقات النسخة النهائية.",
        "",
        "## قائمة فحص النشر",
        *checklist,
        "",
        "## ملاحظة تحريرية",
        "الترجمة الإنجليزية مأخوذة من أسطر الترجمة الموجودة في SRT الثنائي مع الحفاظ على أرقام البطاقات وتوقيتها؛ لا توجد توقيتات مولّدة. روابط التوقيت مشتقة من مواضع المصدر المسجلة في بيانات المشروع.",
        "",
    ]
    out.write_text("\n".join(content), encoding="utf-8")
    return len(description_ar), len(description_en)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def image_info(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        width, height = image.size
    return {"bytes": path.stat().st_size, "dimensions": f"{width}x{height}", "sha256": sha256(path)}


def validate_description_copy(text: str, expected_hashes: list[str]) -> None:
    if text.count("#") != len(expected_hashes):
        raise ValueError("Unexpected hashtag count in copy-ready description")
    for hashtag in expected_hashes:
        if hashtag not in text:
            raise ValueError(f"Missing hashtag: {hashtag}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-frames", action="store_true", help="Recrop the committed source-frame stills from google_drive/*.jpg")
    parser.add_argument("--build-covers-only", action="store_true", help="Skip SRT/SEO generation and rebuild only cover images")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    counts: list[dict[str, Any]] = []

    for package in manifest["packages"]:
        if len(package["title"]) > 70:
            raise ValueError(f"Arabic title exceeds 70 characters: {package['id']} ({len(package['title'])})")
        words = len(package["cover_text"].split())
        if not 3 <= words <= 5:
            raise ValueError(f"Cover hook must be 3–5 words: {package['id']} ({words})")
        if len(package["hashtags_ar"]) != 3 or len(package["hashtags_en"]) != 3:
            raise ValueError(f"Exactly three hashtags are required for {package['id']}")
        tags = ", ".join(package["tags"])
        if not 400 <= len(tags) <= 500:
            raise ValueError(f"Tags must be 400–500 characters for {package['id']}; got {len(tags)}")
        if not manifest["source_episode"].get("verified_in_prior_session"):
            raise ValueError("Source episode URL is not marked as verified")

        package_dir = OUTPUT_ROOT / package["id"]
        package_dir.mkdir(parents=True, exist_ok=True)
        frame_path = make_source_frame(package, refresh=args.refresh_frames)
        horizontal = make_horizontal_cover(package, frame_path)
        vertical = make_vertical_cover(package, frame_path)
        assets: dict[str, Any] = {}

        for image, stem, expected in (
            (horizontal, "THUMBNAIL_1280x720", (1280, 720)),
            (vertical, "THUMBNAIL_1080x1920", (1080, 1920)),
        ):
            if image.size != expected:
                raise ValueError(f"Bad generated cover dimensions {package['id']} {stem}: {image.size}")
            for extension, options in (("jpg", {"quality": 94, "optimize": True, "progressive": True, "subsampling": 0}), ("png", {"optimize": True})):
                out_path = package_dir / f"{stem}.{extension}"
                image.save(out_path, format="JPEG" if extension == "jpg" else "PNG", **options)
                assets[out_path.name] = image_info(out_path)

        with Image.open(package_dir / "THUMBNAIL_1080x1920.png") as vertical_check:
            footer = vertical_check.crop((0, 1680, 1080, 1920)).convert("RGB")
            colors = footer.getcolors(maxcolors=2)
            if colors != [(1080 * 240, (28, 27, 25))]:
                raise ValueError(f"Last 240px must be a solid empty brand field: {package['id']}")

        description_ar_length = description_en_length = None
        if not args.build_covers_only:
            bilingual = package_dir / "CAPTIONS_AR_EN.srt"
            if not bilingual.exists():
                raise FileNotFoundError(f"Missing bilingual captions for {package['id']}: {bilingual}")
            cue_count = build_english_srt(bilingual, package_dir / "CAPTIONS_EN.srt", package["caption_cue_count"])
            if cue_count != package["caption_cue_count"]:
                raise ValueError(f"Caption cue count mismatch for {package['id']}")
            description_ar_length, description_en_length = write_seo_markdown(
                manifest, package, package_dir / "SEO.md", tags
            )
            validate_description_copy(description_text(manifest, package, "ar"), package["hashtags_ar"])
            validate_description_copy(description_text(manifest, package, "en"), package["hashtags_en"])
            for name in ("CAPTIONS_AR_EN.srt", "CAPTIONS_EN.srt", "SEO.md"):
                assets[name] = {"bytes": (package_dir / name).stat().st_size, "sha256": sha256(package_dir / name)}

        asset_manifest = {
            "package_id": package["id"],
            "folder_title": package["title"],
            "final_video_source": {
                "drive_id": package["final_video_drive_id"],
                "file_name": package["final_video_name"],
                "original_bytes": package["final_video_bytes"],
                "transfer_method": "Google Drive server-side copy; no decode/re-encode",
                "not_in_git": True,
            },
            "source_frame": {
                "file": f"source_frames/{frame_path.name}",
                "sha256": sha256(frame_path),
                "derived_from_drive_thumbnail": package["source_thumbnail_drive_id"],
                "crop_px": [566, 0, 1280, 720] if package["kind"] == "long" else [184, 535, 896, 935],
                "person_image_policy": "actual project frame crop; no generated face",
            },
            "source_caption_file": {
                "drive_id": package["caption_source_drive_id"],
                "original_name": package["caption_source_name"],
                "cue_count": package["caption_cue_count"],
                "english_only_timing": "copied unchanged from the corresponding bilingual cues",
            },
            "source_episode_url": manifest["source_episode"]["url"],
            "source_ranges": package["source_ranges"],
            "chapters": package["chapters"],
            "local_files": assets,
            "ready_for_drive_upload": len(assets) == 7,
        }
        (package_dir / "ASSET_MANIFEST.json").write_text(
            json.dumps(asset_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        counts.append(
            {
                "id": package["id"],
                "title_length": len(package["title"]),
                "tag_characters": len(tags),
                "cue_count": package["caption_cue_count"],
                "assets": len(assets),
                "description_ar_characters": description_ar_length,
                "description_en_characters": description_en_length,
                "horizontal": image_info(package_dir / "THUMBNAIL_1280x720.png")["dimensions"],
                "vertical": image_info(package_dir / "THUMBNAIL_1080x1920.png")["dimensions"],
            }
        )

    print(json.dumps({"built": len(counts), "packages": counts}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
