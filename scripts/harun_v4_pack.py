"""HARUN v4 — حزمة النشر في ملف واحد (PDF): غلافان + عنوانان + وصف + وسوم.

ملف واحد قابل للنسخ (نص حقيقي لا صورة):
  صفحة ١: الغلافان A/B + العنوانان + خلاصة الرفع.
  صفحة ٢: الوصف الجاهز + الفصول.
  صفحة ٣: الوسوم + إعدادات النشر + التعليق المثبّت + قائمة الفحص.

الاستخدام: python scripts/harun_v4_pack.py
"""
from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

REPO = Path("/home/user/Riwaq_System_Repo")
FONTS = REPO / "public/fonts"
PUB = REPO / "exports/HARUN_001/publish"
OUT = PUB / "PUBLISH_PACK_HARUN_001.pdf"

INK = (26, 24, 19)
PARCH = (243, 235, 219)
GOLD = (150, 121, 63)
STONE = (110, 101, 84)
LINE = (206, 194, 169)
BOX = (246, 241, 231)

TITLE_A = "هارون الرشيد والرجل الحكيم | ٣ أسئلة أعجزت الخليفة"
TITLE_B = "شيخ يغرس شجرًا لا يأكله… فماذا قال للخليفة؟"


def L(t: str) -> str:
    """عزل اتجاهي (LRI…PDI): يُبقي الأرقام واللاتيني بترتيبه الصحيح داخل سطر عربي."""
    return "\u2066" + t + "\u2069"


DESC = [
    "ثلاثة أسئلة ألقاها هارون الرشيد على شيخ عجوز في بستانٍ على أطراف بغداد…",
    "وثلاثة أجوبة جعلته يقول: «أثرانا حسنُ كلامك يا شيخ».",
    "",
    "خرج الخليفة هارون الرشيد ومعه وزيره جعفر البرمكي يتفقدان أحوال الرعية، فمرّا",
    "ببستانٍ جميل، ورأيا شيخًا طاعنًا في السن يغرس شجيرات صغيرة لا تُثمر إلا بعد",
    "سنوات طويلة. فسأله الخليفة: أتغرس شجرًا وأنت في هذا العمر، فهل ترجو أن تأكل",
    "من ثمره؟ فكان الجواب: «غرس مَن قبلنا فأكلنا، ونغرس ليأكل مَن بعدنا» — جوابًا",
    "حوّل السؤال إلى حكمة، والعطاء إلى لغز.",
    "",
    "في هذه الحلقة من «حكايات رواق»:",
    "• قصة الشيخ الذي غرس لمن بعده لا لنفسه.",
    "• كيف صار الكلام الجميل سببًا في العطاء مرّتين.",
    "• اللغز الذي انتهت به الحلقة: جمادان كلّمهما الله في الدنيا فأجابا،",
    "  وجمادان سألهما في الآخرة فأخبرا، وثلاثة عُرض عليهم العرض فأبَوا.",
    "",
    "الفصول:",
    "00:00 ثلاثة أسئلة… وحكاية أعمق مما تبدو",
    "00:38 الخليفة في أحياء بغداد",
    "00:56 البستان والشيخ العجوز",
    "01:10 «وتغرس شجرًا لا يُثمر إلا بعد سنوات؟»",
    "01:23 «غرس مَن قبلنا فأكلنا»",
    "01:30 الأشجار تُثمر في وقتها",
    "01:51 «العجب كل العجب»",
    "02:06 الانصراف قبل أن تستفرغ الخزائن",
    "02:15 اللغز الأخير",
    "02:29 «سَلْ ما شئتَ يا أمير المؤمنين»",
    "",
    "حلقة من سلسلة «حكايات رواق» — قصص من التاريخ الإسلامي تُروى بهدوء،",
    "بلا مبالغة ولا تهويل.",
    "",
    "اشترك في القناة وفعّل جرس التنبيه ليصلك كل جديد.",
    "اكتب لنا: هل عرفت جواب اللغز قبل نهاية الحلقة؟",
    "",
    "#حكايات_رواق #هارون_الرشيد #قصص_إسلامية",
]

TAGS = ("حكايات رواق, هارون الرشيد, الرجل الحكيم, قصص إسلامية, قصص تاريخية, "
        "قصص من التاريخ الإسلامي, قصص قبل النوم, حكمة, جعفر البرمكي, بغداد, "
        "الخليفة العباسي, قصص وعبر, الصدقة الجارية, غرس الشجر, العطاء, "
        "قصص للكبار, تاريخ إسلامي, Riwaq stories, Harun al-Rashid, Islamic stories")

PINNED = ("اللغز ما زال مفتوحًا: جمادان كلّمهما الله في الدنيا فأجابا، وجمادان سألهما في "
          "الآخرة فأخبرا، وثلاثة عُرض عليهم العرض فأبَوا… من يعرف الجواب؟")


class Pack(FPDF):
    def bar(self, sub: str) -> None:
        self.set_fill_color(*INK)
        self.rect(0, 0, 210, 26, style="F")
        self.set_font("amiri", size=19)
        self.set_text_color(*PARCH)
        self.set_xy(16, 7)
        self.cell(50, 12, "رواق", align="L")
        self.set_font("plexm", size=8.5)
        self.set_text_color(196, 180, 148)
        self.set_xy(66, 10)
        self.cell(128, 8, sub, align="R")
        self.set_draw_color(*GOLD)
        self.set_line_width(0.4)
        self.line(0, 26, 210, 26)
        self.set_text_color(*INK)
        self.set_xy(16, 32)

    def h2(self, txt: str) -> None:
        self.set_font("amiri", size=14)
        self.set_text_color(*GOLD)
        self.multi_cell(self.epw, 7.5, txt, align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*LINE)
        self.set_line_width(0.3)
        y = self.get_y() + 1
        self.line(16, y, 194, y)
        self.set_y(y + 3)
        self.set_text_color(*INK)

    def body(self, txt: str, size: float = 9.6, h: float = 5.6,
             colour=INK, font: str = "plexm", align: str = "R") -> None:
        self.set_font(font, size=size)
        self.set_text_color(*colour)
        self.multi_cell(self.epw, h, txt if txt else " ", align=align,
                        new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*INK)

    def kicker(self, txt: str) -> None:
        self.set_font("plexm", size=8.4)
        self.set_text_color(*STONE)
        self.multi_cell(self.epw, 5, txt, align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*INK)


def main() -> None:
    pdf = Pack(format="A4")
    pdf.set_auto_page_break(True, margin=16)
    pdf.set_margins(16, 16, 16)
    pdf.add_font("amiri", "", str(FONTS / "Amiri-Bold.ttf"))
    pdf.add_font("plexm", "", str(FONTS / "IBMPlexSansArabic-Medium.ttf"))
    pdf.add_font("plexb", "", str(FONTS / "IBMPlexSansArabic-Bold.ttf"))
    pdf.set_text_shaping(True)

    # ────────── صفحة ١
    pdf.add_page()
    pdf.bar("حزمة نشر يوتيوب — الحلقة ٠١")
    pdf.set_font("amiri", size=20)
    pdf.multi_cell(pdf.epw, 9.5, "هارون الرشيد والرجل الحكيم", align="R",
                   new_x="LMARGIN", new_y="NEXT")
    pdf.kicker(f"المدة {L('2:39')} · {L('1920×1080')} · {L('30 fps')} · "
               f"الصوت {L('−15.9 LUFS')} · ذروة {L('−2.0 dB')}")
    pdf.ln(3)

    pdf.h2(f"الغلافان ({L('1280×720')})")
    y = pdf.get_y()
    pdf.image(str(PUB / "COVER_A_1280x720.jpg"), x=106, y=y, w=88)
    pdf.image(str(PUB / "COVER_B_1280x720.jpg"), x=14, y=y, w=88)
    pdf.set_y(y + 51)
    pdf.set_font("plexm", size=8.4)
    pdf.set_text_color(*STONE)
    pdf.set_x(106)
    pdf.cell(88, 5, "A · «الرجل الحكيم / و٣ أسئلة»", align="R")
    pdf.set_x(14)
    pdf.cell(88, 5, "B · «جمادات / تكلّمت»", align="R")
    pdf.set_text_color(*INK)
    pdf.set_y(y + 58)
    pdf.body("الوجه في ثلث، والنص في الثلث المقابل · ٤ كلمات كحد أقصى · تباين يزيد على "
             + L("12:1") + " · منطقة آمنة أسفل اليمين لشارة المدة · هوية ذهبية ثابتة كل حلقة.",
             size=8.4, h=4.9, colour=STONE)

    pdf.ln(2)
    pdf.h2(f"العنوانان — اختبار {L('A/B')}")
    for tag, title, note in (
        ("A", TITLE_A, "٤٩ حرفًا · يبدأ باسم الشخصية التي يبحث عنها الناس، ويَعِد بثلاثة أسئلة."),
        ("B", TITLE_B, "٤٨ حرفًا · مشهد ملموس مع سؤال مفتوح يدفع للضغط."),
    ):
        pdf.set_font("plexb", size=11)
        pdf.multi_cell(pdf.epw, 6.4, title, align="R", new_x="LMARGIN", new_y="NEXT")
        y2 = pdf.get_y()
        pdf.set_font("plexb", size=9)
        pdf.set_fill_color(238, 231, 214)
        pdf.rect(180, y2, 14, 6, style="F", round_corners=True, corner_radius=1.5)
        pdf.set_xy(180, y2)
        pdf.set_text_color(*GOLD)
        pdf.cell(14, 6, tag, align="C")
        pdf.set_font("plexm", size=8.4)
        pdf.set_text_color(*STONE)
        pdf.set_xy(16, y2 + 0.6)
        pdf.multi_cell(160, 4.9, note, align="R", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*INK)
        pdf.ln(1.6)
    pdf.body("كلاهما أقل من ٦٠ حرفًا فلا يُقتطع على الهاتف، والكلمة المفتاحية في أول ٣٠ حرفًا. "
             "جرّب A سبعة أيام ثم B سبعة أيام، وقارن نسبة النقر لا المشاهدات.",
             size=8.4, h=4.9, colour=STONE)

    # خلاصة الرفع
    pdf.ln(4)
    pdf.set_fill_color(*BOX)
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.35)
    y = pdf.get_y()
    pdf.rect(16, y, 178, 39, style="DF", round_corners=True, corner_radius=2.5)
    pdf.set_xy(22, y + 3)
    pdf.set_font("plexb", size=9.6)
    pdf.set_text_color(*GOLD)
    pdf.multi_cell(166, 6, "خلاصة الرفع", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("plexm", size=8.4)
    pdf.set_text_color(*INK)
    for line in (
        "١) الماستر: " + L("HARUN_001_v4_delivery.mp4") + f" — {L('78 MB')} · {L('2:39')} · "
        f"{L('1080p30')} · يُرفع كما هو بلا إعادة ترميز.",
        f"٢) الغلاف: ابدأ بـ A، وبدّله إلى B إذا نزل الـ{L('CTR')} تحت {L('4%')} بعد {L('48')} ساعة.",
        "٣) الوصف من صفحة ٢ والوسوم من صفحة ٣ — نص حقيقي قابل للنسخ.",
    ):
        pdf.set_x(22)
        pdf.multi_cell(166, 4.9, line, align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_y(y + 43)

    pdf.ln(2)
    pdf.h2("قواعد مطبَّقة في كل حلقة")
    rules = (
        "الغلاف: ٤ كلمات كحد أقصى، وجه في ثلث ونص في الثلث المقابل، تباين عالٍ، ومنطقة آمنة لشارة المدة.",
        "العنوان: الكلمة المفتاحية في أول ٣٠ حرفًا، وأقل من ٦٠ حرفًا كي لا يُقتطع على الهاتف.",
        "الوصف: أول ١٥٠ حرفًا تحمل الكلمات المفتاحية، والفصول تظهر كلحظات رئيسية في البحث.",
        "الوسوم: عشرون وسمًا تغطي الاسم والشخصيات والموضوع والسلسلة، بلا حشو ولا تكرار.",
        "الصوت: " + L("−15.9 LUFS") + " وذروة " + L("−2.0 dB") + " — مطابق لما يعرضه يوتيوب بلا خفض أو رفع.",
    )
    pdf.set_font("plexm", size=8.6)
    for r in rules:
        pdf.multi_cell(pdf.epw, 5.2, "•  " + r, align="R", new_x="LMARGIN", new_y="NEXT")

    # ────────── صفحة ٢
    pdf.add_page()
    pdf.bar("الوصف الجاهز — انسخه كما هو")
    import re as _re
    for line in DESC:
        if line == "":
            pdf.ln(2.0)
            continue
        m = _re.match(r"^(\d{2}:\d{2}) (.+)$", line)
        if m:
            pdf.set_font("plexm", size=9.6)
            pdf.set_text_color(*INK)
            pdf.set_x(148)
            pdf.cell(46, 5.6, m.group(1), align="R")
            pdf.set_x(16)
            pdf.cell(130, 5.6, m.group(2), align="R")
            pdf.ln(5.6)
            continue
        if line.startswith("#"):
            pdf.ln(1)
            pdf.body(line, size=9.6, h=5.6, colour=GOLD)
            continue
        pdf.body(line, size=9.6, h=5.6)
    pdf.ln(2)
    pdf.body("الفصول تظهر كلحظات رئيسية في نتائج البحث، وكل فصل لا يقل عن ١٠ ثوانٍ ويبدأ من "
             + L("00:00") + ". أول ١٥٠ حرفًا تحمل الكلمات المفتاحية الثلاث. ثلاث هاشتاجات فقط — "
             f"أكثر من {L('15')} يُلغيها يوتيوب كلها.",
             size=8.4, h=4.9, colour=STONE)

    # ────────── صفحة ٣
    pdf.add_page()
    pdf.bar("الوسوم والإعدادات وقائمة الفحص")
    pdf.h2("الوسوم")
    pdf.body(TAGS, size=9.2, h=5.3)
    pdf.ln(2)
    pdf.h2("إعدادات النشر")
    rows = (
        ("الفئة", "Education"),
        ("اللغة", "العربية"),
        ("الترجمة", L("harun-vo-transcript-approved.srt")),
        ("الغلاف", "الغلاف A أولًا ثم B في اختبار نسبة النقر"),
        ("قائمة التشغيل", "حكايات رواق — الحلقة ١"),
        ("وقت النشر", "بتوقيت مكة " + L("20:00–22:00")),
        ("المدة", f"{L('2:39')} · {L('1920×1080')} · {L('30 fps')}"),
        ("الصوت", f"{L('−15.9 LUFS')} · ذروة {L('−2.0 dB')}"),
    )
    pdf.set_font("plexm", size=9)
    for k, v in rows:
        pdf.set_draw_color(*LINE)
        pdf.set_line_width(0.2)
        y = pdf.get_y()
        pdf.line(16, y + 6.4, 194, y + 6.4)
        pdf.set_x(158)
        pdf.set_text_color(*STONE)
        pdf.cell(36, 6.8, k, align="R")
        pdf.set_text_color(*INK)
        pdf.set_x(16)
        pdf.cell(140, 6.8, v, align="R")
        pdf.ln(6.8)
    pdf.ln(3)
    pdf.h2("التعليق المثبّت")
    pdf.body(PINNED, size=9.4, h=5.4)
    pdf.ln(2)
    pdf.h2("قائمة الفحص قبل الرفع")
    pdf.set_font("plexm", size=9)
    checks = (
        "رفع الماستر كما هو بلا إعادة ترميز.",
        "العنوان يظهر كاملًا على الهاتف (أقل من ٦٠ حرفًا).",
        "رفع الغلاف A واختياره من Studio.",
        "لصق الوصف والتأكد من ظهور الفصول.",
        "إضافة الوسوم والترجمة العربية.",
        "الإضافة إلى قائمة التشغيل وتثبيت التعليق.",
        f"بعد {L('48')} ساعة: {L('CTR')} أقل من {L('4%')} ⇒ بدّل إلى الغلاف B.",
    )
    for item in checks:
        pdf.multi_cell(pdf.epw, 6.0, "☐  " + item, align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.output(str(OUT))
    print("wrote", OUT, round(OUT.stat().st_size / 1024), "KB")


if __name__ == "__main__":
    main()
