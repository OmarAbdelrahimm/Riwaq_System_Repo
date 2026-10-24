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


# ───────────────────────── فحص النمط (يُستخدم من seo_pack --audit) ─────────────────────────
# {number}-{KIND}-{A|B}-{english-slug}-v{n}.{ext}
NAME_RE = re.compile(
    r"^(?P<num>(?:S|F)?\d{2})-"
    r"(?P<kind>CVR-H|CVR-V|SEO|SUB-AR|SUB-EN|SUB-BI|VID|QC)"
    r"(?:-(?P<variant>[AB]))?-"
    r"(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)-"
    r"v(?P<v>\d+)\."
    r"(?P<ext>[a-z0-9]+)$"
)

# الامتداد المسموح لكل نوع — ملف بـ .mp4 اسمه SEO خطأ يجب أن يُرفض
ALLOWED_EXT = {
    "CVR-H": {"jpg", "png"},
    "CVR-V": {"jpg", "png"},
    "SEO": {"md"},
    "SUB-AR": {"srt"},
    "SUB-EN": {"srt"},
    "SUB-BI": {"srt"},
    "VID": {"mp4", "mov"},
    "QC": {"png", "pdf"},
}

# الأنواع التي تحتاج A/B، والأنواع التي يجب ألا تحملهما
NEEDS_VARIANT = {"CVR-H", "CVR-V"}
NO_VARIANT = {"SEO", "SUB-AR", "SUB-EN", "SUB-BI", "VID", "QC"}

_SLUG_BAD = re.compile(r"[^a-z0-9-]")


def parse_name(filename: str) -> dict | None:
    """يفكّك اسمًا مطابقًا للنمط، أو None لو كان خارج النمط."""
    m = NAME_RE.match(Path(filename).name)
    if not m:
        return None
    d = m.groupdict()
    return {"number": d["num"], "kind": d["kind"], "variant": d["variant"],
            "slug": d["slug"], "v": int(d["v"]), "ext": d["ext"]}


def check_name(filename: str) -> list[str]:
    """يرجّع قائمة المخالفات؛ قائمة فارغة = الاسم مطابق للمعيار.

    يفحص: النمط · الحروف اللاتينية فقط · الشرطة الواحدة · A/B في موضعه ·
    الامتداد المناسب للنوع · طول الـ slug (≤ 6 كلمات).
    """
    errs: list[str] = []
    base = Path(filename).name
    if re.search(r"[\u0600-\u06FF]", base):
        errs.append(f"«{base}»: حروف عربية — الأسماء لاتينية فقط")
    if "_" in base or " " in base:
        errs.append(f"«{base}»: مسافة أو شرطة سفلية — استخدم «-» فقط")
    p = parse_name(base)
    if p is None:
        return errs + [f"«{base}»: خارج النمط {{number}}-{{KIND}}-{{A|B}}-{{slug}}-v{{n}}.{{ext}}"]

    if p["kind"] in NEEDS_VARIANT and not p["variant"]:
        errs.append(f"«{base}»: {p['kind']} يحتاج A أو B")
    if p["kind"] in NO_VARIANT and p["variant"]:
        errs.append(f"«{base}»: {p['kind']} لا يحمل A/B")
    if p["ext"] not in ALLOWED_EXT.get(p["kind"], set()):
        errs.append(f"«{base}»: امتداد .{p['ext']} غير مناسب لـ {p['kind']}")
    if p["slug"] != p["slug"].lower():
        errs.append(f"«{base}»: الـ slug بحروف كبيرة — صغير فقط (KIND وA/B فقط بأحرف كبيرة)")
    words = p["slug"].split("-")
    if len(words) > 7:
        errs.append(f"«{base}»: الـ slug {len(words)} كلمة — الحد 7")
    if _SLUG_BAD.search(p["slug"]):
        errs.append(f"«{base}»: الـ slug يحتوي محارف غير مسموحة")
    return errs


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
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        # python naming.py --check "01-CVR-H-A-x-v1.jpg" ...  → 0 = كلها مطابقة
        bad = 0
        for fn in sys.argv[2:]:
            e = check_name(fn)
            print(("✅ " if not e else "❌ ") + fn)
            for msg in e:
                print("   ·", msg)
            bad += bool(e)
        raise SystemExit(1 if bad else 0)

    print(cover_name("02", "CVR-H", "المقارنة أداة لا معيار", variant="A", v=1,
                     en="comparison-is-a-tool-not-a-standard"))
    print(cover_name("S03", "CVR-V", "المقارنة لازمة غير ملزمة", variant="B",
                     en="comparison-is-necessary-but-not-binding"))
    print(seo_name("F01", "العلاقة التي تُصلح كل العلاقات", v=1,
                   en="the-relationship-that-fixes-all-relationships"))
    print(slug("المقارنة أداة لا معيار"))       # بديل احتياطي
