"""
كابشنز TMB_001 — النسخة الطويلة.

كل cue مربوط بـ:
  clip      : الملف الصوتي
  gap       : [بداية, نهاية] فاصل الصمت الحقيقي داخل الملف (مقاس بـRMS)
  start_off : أين تبدأ الجملة داخل الفاصل (ثانية، قياسيًا +0.06)
  end_off   : أين تنتهي قبل الفاصل التالي (قياسيًا -0.30)
  ar        : النص العربي (≤28 حرف للسطر، ≤44 للسطرين)
  en        : الترجمة الإنجليزية

⚠️ النص هنا مطابق حرفيًا لما نُطق في v3_*.wav.
   لو تغيّر الصوت، هذا الملف يتغيّر معه — لا يُعاد استخدامه.
"""

CLIPS = [
    # (index, filename, offset_of_clip_start_in_film)
    (1, "v3_01.wav", 0.0),
    (2, "v3_02.wav", 20.2),
    (3, "v3_03.wav", 38.6),
    (4, "v3_04.wav", 63.1),
    (5, "v3_05.wav", 89.1),
    (6, "v3_06.wav", 108.4),
    (7, "v3_07.wav", 145.3),
    (8, "v3_08.wav", 184.8),
    (9, "v3_09.wav", 215.0),
    (10, "v3_10.wav", 242.7),
]

# ─────────────────────────────────────────────────────────────────────────────
# clip 1 ─ 18.2s
# فواصل مقاسة: 1.34 | 4.04 | 6.42 | 7.74 | 9.20 | 10.68 | 12.56 | 13.84 |
#               14.88 | 16.46 | (نهاية)
# ─────────────────────────────────────────────────────────────────────────────
C1 = [
    (0.00, 1.34, "بصّ في الرقم ده.", "Look at this number."),
    (1.34, 4.04, "أربعة آلاف وميتين وتلاتة.", "Four thousand two hundred three."),
    (4.04, 6.42, "عدد الكتب اللي اتحرقت…\nفي يوم واحد.", "The books burned —\nin a single day."),
    (6.42, 7.74, "والأغرب؟", "And the strangest part?"),
    (7.74, 9.42, "المدينة دي كانت\nلسه مليانة كتب.", "This city was still\nfull of books."),
    (9.20, 10.68, "اسمها تمبكتو.", "Its name: Timbuktu."),
    (10.68, 12.56, "ودي حكاية\nمش هتصدقها.", "A story you\nwon't believe."),
]

# clip 2 ─ 16.9s  فواصل: 1.48 2.92 7.32 8.90 10.22 12.28 15.04
C2 = [
    (0.00, 1.48, "قبل ما تحكم عليها،", "Before you judge it,"),
    (1.48, 2.92, "لازم تعرف حاجة.", "you need to know something."),
    (2.92, 7.32, "أكبر عملية إنقاذ للتراث\nفي أفريقيا كلها…", "The largest heritage rescue\nin all of Africa…"),
    (7.32, 8.90, "ماحصلتش في متحف.", "Didn't happen in a museum."),
    (8.90, 10.22, "ولا في عاصمة.", "Not in a capital."),
    (10.22, 12.28, "ولا حتى في مكتبة عالمية.", "Not even a world library."),
    (12.28, 15.04, "حصلت في مدينة\nفي نص الصحرا…", "It happened in a city\nin the middle of the desert…"),
    (15.04, 16.62, "ومحدش شافها.", "And nobody saw it."),
]

# clip 3 ─ 22.6s  فواصل: 3.92 6.02 6.96 8.60 9.42 10.44 13.08 14.34 16.48 17.58 19.34 21.12
C3 = [
    (0.00, 3.92, "تمبكتو مكانتش واحة\nعشان القوافل تعدّي.", "Timbuktu wasn't a stop\nfor caravans to pass through."),
    (3.92, 6.02, "لأ.\nكانت محطة. مقصد.", "No.\nIt was a destination."),
    (6.02, 6.96, "تخيل معايا بقى:", "Picture it with me:"),
    (6.96, 8.60, "مدينة وسط الرمل،", "A city in the sand,"),
    (8.60, 9.42, "بعيدة عن البحر", "far from the sea"),
    (9.42, 10.44, "بميتين يوم سير؟", "by two hundred days' walk?"),
    (10.44, 13.08, "ومع كده فيها طلبة\nجايين من كل حتة،", "Yet students came\nfrom everywhere,"),
    (13.08, 14.34, "وعلماء،", "and scholars,"),
    (14.34, 16.48, "وأسواق مالية من الكتب.", "and markets trading books."),
    (16.48, 17.58, "مدينة الكتب.", "A city of books."),
    (17.58, 19.34, "حرفيًا.", "Literally."),
]

# clip 4 ─ 23.0s  فواصل: 2.66 5.42 6.50 7.70 8.56 9.68 13.92 15.18 16.88 19.24 20.24
C4 = [
    (0.00, 2.66, "وسنة ألف وخمسمية\nوستة وعشرين،", "In fifteen hundred\ntwenty-six,"),
    (2.66, 5.42, "واحد مغربي اسمه\nليو أفريكانوس دخل المدينة.", "a Moroccan named\nLeo Africanus entered the city."),
    (5.42, 6.50, "قعد فيها.", "He sat there."),
    (6.50, 7.70, "شاف.", "He saw."),
    (7.70, 8.56, "وكتب.", "And he wrote."),
    (8.56, 9.68, "وكتب سطر واحد", "He wrote one line"),
    (9.68, 13.92, "خلّى الناس مش مصدقينه\nلحد النهاردة.", "that people still\nrefuse to believe."),
    (13.92, 15.18, "قال بالحرف:", "His exact words:"),
    (14.90, 16.88, "«تجارة الكتب\nأربح من الدهب».", "«Trade in books\nbeats gold.»"),
    (16.88, 19.24, "تخيل. الدهب كان\nأرخص من الورق.", "Imagine. Gold was\ncheaper than paper."),
]

# clip 5 ─ 17.8s  فواصل: 2.08 3.28 4.48 5.22 6.72 8.94 12.34 13.46 15.64
C5 = [
    (0.00, 2.08, "الكتب دي مكانتش ديكور.", "These books were not decoration."),
    (2.08, 3.28, "فلك.", "Astronomy."),
    (3.28, 4.48, "طب.", "Medicine."),
    (4.48, 5.22, "شعر.", "Poetry."),
    (5.22, 6.72, "فقه.", "Law."),
    (6.72, 8.94, "عقود بيع وشرا.", "Contracts of sale and trade."),
    (8.94, 12.34, "رسايل بين ناس\nبيحبوا بعض.", "Letters between people\nwho loved each other."),
    (12.10, 13.46, "وبعضها مكتوب\nبحبر دهبي،", "Some written\nin gold ink,"),
    (13.46, 15.64, "وبعضها أحمر،\nوبعضها أسود.", "some in red,\nsome in black."),
    (15.64, 17.44, "زي ما انت بتكتب\nبقلمين ألوان.", "Like you writing\nwith two colored pens."),
]

# clip 6 ─ 34.8s  فواصل: 1.72 2.88 6.02 7.04 8.32 9.72 12.06 13.42 15.66 16.98
#          19.46 21.24 23.76 27.20 28.58 29.88 31.98 33.32
C6 = [
    (0.00, 1.72, "وهنا حاجة غريبة،", "And here's something strange,"),
    (1.72, 2.88, "ولها معنى.", "and it means something."),
    (2.88, 6.02, "اللي بيقتل أي أثر تاني\nفي الدنيا… الرطوبة…", "What destroys every other\nrelic in the world — humidity —"),
    (6.02, 7.04, "كان بعيد عنهم.", "was far from them."),
    (7.04, 8.32, "الجفاف،", "Drought,"),
    (8.32, 9.72, "اللي بيطحن\nالأخضر واليابس،", "which grinds down\neverything alive,"),
    (9.72, 12.06, "هو اللي حفظهم.", "is what preserved them."),
    (12.06, 13.42, "خمس قرون في الرمل.", "Five centuries in the sand."),
    (13.42, 15.66, "ولسه فيها.", "Still there."),
    (15.66, 16.98, "بتفتح صفحة، وصفحة،", "You open page after page,"),
    (16.98, 19.46, "والصفحة بتتنفس.", "and the page breathes."),
    (19.46, 21.24, "لغاية ألفين واتناشر.", "Until 2012."),
    (21.24, 23.76, "لغاية ما دخلت المدينة\nمجموعات مسلّحة.", "Until armed groups\nentered the city."),
    (23.76, 27.20, "والناس هناك كانوا\nعارفين اللي جاي.", "And the people there\nknew what was coming."),
    (27.20, 28.58, "عشان اللي عندهم\nمش ورق.", "Because what they held\nwasn't paper."),
    (28.58, 29.88, "اللي عندهم\nهو مين هما.", "What they held\nwas who they were."),
]

# clip 7 ─ 27.5s  فواصل: 3.36 5.66 7.18 8.54 10.20 12.72 14.06 17.90 19.18 20.54 23.86
C7 = [
    (0.00, 3.36, "في خمسة وعشرين يناير\nألفين وتلتاشر،", "On the twenty-fifth of January,\ntwo thousand thirteen,"),
    (3.36, 5.66, "دخلوا مكتبة أحمد بابا.", "they entered the Ahmed Baba library."),
    (5.66, 7.18, "كبّوا بنزين.", "They poured gasoline."),
    (7.18, 8.54, "وولّعوا.", "And lit it."),
    (8.54, 10.20, "ولمّا خرجوا…", "And when they left…"),
    (10.20, 12.72, "الغرفة مكانتش\nغرفة مكتبة.", "The room was no longer\na library room."),
    (12.72, 14.06, "كانت فرن.", "It was an oven."),
    (14.06, 17.90, "أربعة آلاف وميتين\nوتلاتة مخطوطة. راحت.", "Four thousand two hundred\nthree manuscripts. Gone."),
    (17.90, 19.18, "مش رقم.", "Not a number."),
    (19.18, 23.86, "أربعة آلاف وميتين وتلاتة\nحد فقد حاجة عمرها ٥٠٠ سنة", "Four thousand two hundred three times,\nsomeone lost something five hundred years old."),
]

# clip 8 ─ 28.7s  فواصل: 1.32 4.16 5.32 6.22 7.58 8.90 10.46 12.94 13.94 15.36
#          16.32 17.40 19.58 21.46 23.16 26.40
C8 = [
    (0.00, 1.32, "بس الحريق ده،", "But this fire"),
    (1.32, 4.16, "حصل بعد ما المدينة\nكانت خدت قرار.", "came after the city\nhad made a decision."),
    (4.16, 5.32, "قرار… بصراحة،", "A decision… honestly,"),
    (5.32, 6.22, "لو قريته في فيلم", "if you saw it in a film"),
    (6.22, 7.58, "كنت هتقول مبالغة.", "you'd call it exaggerated."),
    (7.58, 10.46, "كانوا هينقلوا مية\nوأربعين ألف مخطوطة. سرًا.", "They were moving a hundred\nforty thousand manuscripts. In secret."),
    (10.46, 12.94, "شحنة شحنة.\nفي الليل.", "Shipment by shipment.\nAt night."),
    (12.94, 13.94, "وفي إيه؟", "In what?"),
    (13.94, 17.40, "في صناديق زيت معدنية.", "In metal oil drums."),
    (17.40, 19.58, "اللي بيتباع فيها البنزين…", "The kind that sells gasoline…"),
    (19.58, 21.46, "اللي حرق المكتبة.", "the gasoline that burned the library."),
    (21.46, 26.40, "نفس الصندوق اللي كان\nبيولّع نار،\nبقى هو اللي شيّل الكتب.", "The same drum that once\nheld fire\nnow carried the books."),
]

# clip 9 ─ 26.2s  فواصل: 0.74 2.32 3.62 5.38 8.72 9.74 11.64 13.66 14.68 15.84
#          16.78 17.66 19.66 21.90 23.10 24.80
C9 = [
    (0.00, 0.74, "الطريق؟", "The road?"),
    (0.74, 2.32, "أربعمية ميل.", "Four hundred miles."),
    (2.32, 3.62, "أول حتة،", "First leg:"),
    (3.62, 5.38, "عربيات دفع على الرمل،", "pickups on the sand,"),
    (5.38, 8.72, "والسواقين بيقفوا كل شوية\nيشيّكوا على الحمولة.", "drivers stopping constantly\nto check the load."),
    (8.72, 9.74, "بعدها،", "Then,"),
    (9.74, 11.64, "قوارب صغيرة على النيجر،", "small boats on the Niger,"),
    (11.64, 13.66, "خمس تيام على المية.", "five days on the water."),
    (13.66, 14.68, "بعدها،", "Then,"),
    (14.68, 15.84, "عربيات تاني.", "pickups again."),
    (15.84, 16.78, "وشاحنات.", "And trucks."),
    (16.78, 17.66, "وقوافل.", "And caravans."),
    (17.66, 19.66, "كل واحدة بتحمل كتب.", "Every one carrying books."),
    (19.66, 21.90, "ومحدش بيعرف إيه اللي\nجواها، غير اللي حمّلها.", "No one knew what was\ninside but the loader."),
    (21.90, 23.10, "ولو واحدة اتكشفت…", "If even one was caught…"),
    (23.10, 24.80, "خلاص.", "It was over."),
]

# clip 10 ─ 37.6s  فواصل: 2.42 3.44 7.00 7.82 9.02 10.42 11.78 13.34 15.10 16.62
#           18.72 20.96 22.78 24.66 25.62 27.60 28.82 30.70 32.50 33.90
C10 = [
    (0.00, 2.42, "ولمّا وقفت آخر عربية…", "And when the last truck stopped…"),
    (2.42, 3.44, "ووصلت.", "It arrived."),
    (3.44, 7.00, "تلتمية وخمسين ألف\nمخطوطة. نجت.", "Three hundred fifty thousand\nmanuscripts. They survived."),
    (7.00, 7.82, "والخسارة؟", "The loss?"),
    (7.82, 9.02, "واحد في المية.", "One percent."),
    (9.02, 11.78, "دلوقتي خليني أقولك\nرأيي بصراحة.", "Now let me tell you\nmy honest opinion."),
    (11.78, 13.34, "اللي عملته الناس دي،", "What these people did,"),
    (13.34, 15.10, "مش بطولة أسطورية.", "wasn't a mythic heroism."),
    (15.10, 16.62, "ولا حكاية\nأبطال خارقين.", "Nor a tale\nof superheroes."),
    (16.62, 18.72, "هو أبسط من كده بكتير.", "It's far simpler than that."),
    (18.72, 20.96, "حد لقى حاجة مهمة،", "Someone found something precious,"),
    (20.96, 22.78, "ومكانش عايز\nيسيبها تروح.", "and couldn't bear\nto let it go."),
    (22.78, 24.66, "وخلاص.", "That's it."),
    (24.66, 27.60, "ويمكن ده بالظبط\nاللي بيخليه أعظم،", "And maybe that's exactly\nwhat makes it great,"),
    (27.60, 30.70, "عشان أي حد فينا،\nوانت قاعد بتتفرج دلوقتي…", "because any one of us,\nsitting here watching now…"),
    (30.70, 32.50, "يقدر يعمله.", "could do it."),
    (32.50, 36.20, "و دي رِواق .. سلاام", "And this is Riwaq…\nsalaam."),
]

CUES = {1: C1, 2: C2, 3: C3, 4: C4, 5: C5, 6: C6, 7: C7, 8: C8, 9: C9, 10: C10}

EN_ONLY = []
