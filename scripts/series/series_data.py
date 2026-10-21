"""بيانات سلسلة «مركزية العلاقة مع الله» — العناوين، الفصول، ترتيب النشر، مصادر الكابشن."""
from __future__ import annotations

SERIES = "مركزية العلاقة مع الله — ياسر الحزيمي"
CHANNEL = "@gallery_of_history"

# ترتيب النشر: 1 → 2 → 3 (من العام إلى الخاص، وبناءً على التسلسل المنطقي للمحتوى)
# 002 العلاقات أعمق من التواصل → 003 المقارنة والنقد الذاتي → 004 النهايات والبدايات
VIDEOS = [
    {
        "key": "002",
        "master": "MASTER_WEB_RELATIONSHIP_002.mp4",
        "order": 1,
        "duration": 293.88,
        "title_a": "العلاقات أعمق من التواصل: ما الذي يوجّهها حقًا؟",
        "title_b": "لا تكفي مهارات التواصل لبناء علاقة… فما البوصلة؟",
        "hook": "أعمق من الكلام",
        "sub": "بوصلة العلاقات",
        "chapter_on_screen": "العلاقات أعمق من التواصل",
        "next": "003",
    },
    {
        "key": "003",
        "master": "MASTER_WEB_RELATIONSHIP_003.mp4",
        "order": 2,
        "duration": 227.28,
        "title_a": "المقارنة أداة لا معيار: كيف تسعى للأفضل دون قسوة؟",
        "title_b": "توقّف عن جلد ذاتك: قارن لتسترشد لا لتنافس",
        "hook": "قارن… ولا تجلد",
        "sub": "المقارنة وجلد الذات",
        "chapter_on_screen": "المقارنة أداة لا معيار",
        "next": "004",
    },
    {
        "key": "004",
        "master": "MASTER_WEB_RELATIONSHIP_004.mp4",
        "order": 3,
        "duration": 246.72,
        "title_a": "النهايات في العلاقات: هل كل خروج بداية دخول؟",
        "title_b": "لا تنهِ علاقة قبل أن تعرف إلى أين تدخل",
        "hook": "كل خروج… دخول",
        "sub": "نهايات العلاقات",
        "chapter_on_screen": "كل خروج هو دخول",
        "next": None,
    },
]

TOTAL = len(VIDEOS)


def by_key(key: str) -> dict:
    for v in VIDEOS:
        if v["key"] == key:
            return v
    raise KeyError(key)


def publish_order_text(key: str) -> str:
    v = by_key(key)
    nxt = by_key(v["next"])["title_a"] if v["next"] else "—"
    return f"ترتيب النشر: {v['order']} من {TOTAL} | الحلقة التالية: {nxt}"
