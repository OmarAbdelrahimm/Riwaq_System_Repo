"""تسمية ملفات رواق + حفظ الأغلفة — المرجع: docs/FILE_NAMING.md

    from naming import cover_name, seo_name, save_cover
    save_cover(im, cover_name("01", "CVR-H", "العلاقات أعمق من التواصل", variant="A", v=2))
    # => 01-CVR-H-A-العلاقات-اعمق-من-التواصل-v2.jpg (+ .png)

لا مسافات، لا شرطة سفلية — شرطة "-" فقط.
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from PIL import Image

TYPES = {
    "CVR-H": "غلاف أفقي 1280×720",
    "CVR-V": "غلاف عمودي 1080×1920",
    "SEO": "وثيقة العناوين والوصف والوسوم",
    "SUB-AR": "ترجمة عربية",
    "SUB-EN": "ترجمة إنجليزية",
    "SUB-BI": "ترجمة ثنائية",
    "VID": "ماستر الفيديو",
    "QC": "ورقة معاينة (لا تُرفع)",
}

_DIACRITICS = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")


def slug(text: str, words: int = 5) -> str:
    """3–5 كلمات، بلا تشكيل ولا ترقيم، بشرطات بين الكلمات.

    تُحفظ الحروف العربية كما هي (ة · أ · إ) لأنها جزء من الكلمة المقروءة،
    وأنظمة الملفات الحديثة وGoogle Drive تتعامل معها بلا مشاكل.
    """
    t = unicodedata.normalize("NFC", text)
    t = _DIACRITICS.sub("", t)
    t = re.sub(r"[^\u0621-\u064A0-9\s]", " ", t)   # يمسح الترقيم والرموز
    parts = [p for p in t.split() if p]
    return "-".join(parts[:words])


def name(number: str, kind: str, title: str, *, variant: str | None = None,
         v: int = 1, ext: str = "jpg", words: int = 5) -> str:
    """الاسم المعياري: {الرقم}-{النوع}-{البديل}-{slug}-{النسخة}.{الصيغة}"""
    if kind not in TYPES:
        raise ValueError(f"نوع غير معروف: {kind} — المسموح {list(TYPES)}")
    bits = [str(number), kind]
    if variant:
        bits.append(variant.upper())
    bits += [slug(title, words), f"v{v}"]
    return "-".join(b for b in bits if b) + "." + ext.lstrip(".")


def cover_name(number: str, kind: str, title: str, **kw) -> str:
    return name(number, kind, title, **kw)


def seo_name(number: str, title: str, **kw) -> str:
    kw.setdefault("ext", "md")
    return name(number, "SEO", title, **kw)


def save_cover(im: Image.Image, stem: str, out_dir: str | Path = ".") -> tuple[Path, Path]:
    """PNG ماستر أرشيفي + JPG للرفع (q95 · 4:4:4 ⇒ لا تشويه لوني على الذهبي الرفيع).

    stem = الاسم الكامل بصيغة .jpg أو بدونه.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    base = Path(stem)
    if base.suffix.lower() in {".jpg", ".jpeg", ".png"}:
        base = base.with_suffix("")
    png = out_dir / f"{base.name}.png"
    jpg = out_dir / f"{base.name}.jpg"

    rgb = im.convert("RGB") if im.mode != "RGB" else im
    rgb.save(png)                                     # ماستر بلا فقد
    rgb.save(jpg, quality=95, subsampling=0, optimize=True)   # ملف الرفع
    return jpg, png


if __name__ == "__main__":
    print(cover_name("01", "CVR-H", "العلاقات أعمق من التواصل", variant="A", v=2))
    print(cover_name("S03", "CVR-V", "المقارنة لازمة غير ملزمة", variant="B"))
    print(seo_name("F01", "العلاقة التي تُصلح كل العلاقات", v=1))
