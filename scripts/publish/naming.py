"""تسمية ملفات رواق + حفظ الأغلفة — المرجع: docs/FILE_NAMING.md

الأسماء **إنجليزية بالكامل** (لاتيني فقط): أوضح في الفرز، أأمن عند الرفع
عبر المتصفح وعلى أي نظام ملفات، وتصلح عنوانًا افتراضيًا على يوتيوب.

    from naming import cover_name, seo_name, save_cover
    save_cover(im, cover_name("02", "CVR-H", "المقارنة أداة لا معيار",
                              variant="A", en="comparison-is-a-tool-not-a-standard"))
    # => 02-CVR-H-A-comparison-is-a-tool-not-a-standard-v1.jpg (+ .png)

لا مسافات، لا شرطة سفلية، ولا حروف عربية — شرطة "-" فقط.
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from PIL import Image

TYPES = {
    "CVR-H": "horizontal cover 1280x720",
    "CVR-V": "vertical cover 1080x1920",
    "SEO": "titles / description / tags",
    "SUB-AR": "Arabic subtitles",
    "SUB-EN": "English subtitles",
    "SUB-BI": "bilingual subtitles",
    "VID": "final master",
    "QC": "preview sheet (never uploaded)",
}

_DIACRITICS = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")
_NON_LATIN = re.compile(r"[^a-z0-9\s-]")

# خريطة تحويل تقريبية (franco/latin) — تُستخدم فقط عند غياب الاسم الإنجليزي الجاهز
_TRANSLIT = {
    "ا": "a", "أ": "a", "إ": "e", "آ": "aa", "ب": "b", "ت": "t", "ث": "th",
    "ج": "j", "ح": "h", "خ": "kh", "د": "d", "ذ": "dh", "ر": "r", "ز": "z",
    "س": "s", "ش": "sh", "ص": "s", "ض": "d", "ط": "t", "ظ": "z", "ع": "a",
    "غ": "gh", "ف": "f", "ق": "q", "ك": "k", "ل": "l", "م": "m", "ن": "n",
    "ه": "h", "و": "w", "ي": "y", "ى": "a", "ة": "a", "ء": "", "ئ": "e",
    "ؤ": "o", "ﻻ": "la",
}

# كلمات العنوان → مقابل إنجليزي مباشر (أفضل من التحويل الحرفي في أسماء الملفات)
GLOSSARY = {
    "المقارنة": "comparison", "أداة": "tool", "لا": "not", "معيار": "standard",
    "العلاقات": "relationships", "أعمق": "deeper-than", "التواصل": "communication",
    "النهايات": "endings", "الشيطان": "shaytan", "يجري": "runs", "مجرى": "through",
    "الدم": "blood", "من": "who", "يقود": "drives", "سيارتك": "your-car",
    "الرأي": "opinion", "ليس": "is-not", "الحقيقة": "the-truth",
    "تطوير": "self-development", "الذات": "self", "طور": "develop",
    "ذاتك": "yourself", "ياسر": "yaser", "الحزيمي": "alhazimi",
    "بودكاست": "podcast", "بدون": "bila", "ورق": "waraq", "رواق": "riwaq",
}


def translit(text: str, words: int = 5) -> str:
    """تحويل عربي → لاتيني (franco) — بديل احتياطي فقط."""
    t = _DIACRITICS.sub("", unicodedata.normalize("NFC", text))
    t = re.sub(r"[^\u0621-\u064A\s]", " ", t)
    out = []
    for w in t.split():
        if w in GLOSSARY:
            out.append(GLOSSARY[w])
            continue
        s = "".join(_TRANSLIT.get(ch, "") for ch in w)
        s = re.sub(r"([a-z])\1+", r"\1", s)        # لا تكرار حروف (محمّد → mhmd)
        if s:
            out.append(s)
    return "-".join(out[:words])


def slug(text: str, words: int = 5) -> str:
    """slug لاتيني دائمًا: يُستخدم النص كما هو لو كان إنجليزيًا، وإلا يُحوّل."""
    if re.search(r"[\u0621-\u064A]", text):
        return translit(text, words)
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    parts = [p for p in _NON_LATIN.sub(" ", t.lower()).split() if p]
    return "-".join(parts[:words])


def name(number: str, kind: str, title_or_en: str, *, variant: str | None = None,
         v: int = 1, ext: str = "jpg", words: int = 6, en: str | None = None) -> str:
    """{number}-{kind}-{A|B}-{english-slug}-{v}.{ext}"""
    if kind not in TYPES:
        raise ValueError(f"نوع غير معروف: {kind} — المسموح {list(TYPES)}")
    s = slug(en or title_or_en, words)
    if not s:
        raise ValueError(f"لا يمكن توليد slug لاتيني من: {title_or_en!r} — مرّر en=")
    bits = [str(number), kind]
    if variant:
        bits.append(variant.upper())
    bits += [s, f"v{v}"]
    return "-".join(b for b in bits if b) + "." + ext.lstrip(".")


def cover_name(number: str, kind: str, title: str, **kw) -> str:
    return name(number, kind, title, **kw)


def seo_name(number: str, title: str, **kw) -> str:
    kw.setdefault("ext", "md")
    return name(number, "SEO", title, **kw)


def save_cover(im: Image.Image, stem: str, out_dir: str | Path = ".") -> tuple[Path, Path]:
    """PNG ماستر أرشيفي + JPG للرفع (q95 · 4:4:4 ⇒ لا تشويه لوني على الذهبي الرفيع)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    base = Path(stem)
    if base.suffix.lower() in {".jpg", ".jpeg", ".png"}:
        base = base.with_suffix("")
    png = out_dir / f"{base.name}.png"
    jpg = out_dir / f"{base.name}.jpg"

    rgb = im.convert("RGB") if im.mode != "RGB" else im
    rgb.save(png)
    rgb.save(jpg, quality=95, subsampling=0, optimize=True)
    return jpg, png


if __name__ == "__main__":
    print(cover_name("02", "CVR-H", "المقارنة أداة لا معيار", variant="A", v=1,
                     en="comparison-is-a-tool-not-a-standard"))
    print(cover_name("S03", "CVR-V", "المقارنة لازمة غير ملزمة", variant="B",
                     en="comparison-is-necessary-but-not-binding"))
    print(seo_name("F01", "العلاقة التي تُصلح كل العلاقات", v=1,
                   en="the-relationship-that-fixes-all-relationships"))
    print(slug("المقارنة أداة لا معيار"))       # بديل احتياطي
