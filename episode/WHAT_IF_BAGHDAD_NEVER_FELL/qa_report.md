# qa_report — WHAT_IF_BAGHDAD_NEVER_FELL

**الحالة:** READY_FOR_REVIEW · بانتظار البوابة البشرية 2 (لا نشر)
**التاريخ:** 2026-11-25 · أُنتج بـ `tools/qa.py` (قياسات ffmpeg/ebur128 فعلية) + مراجعة يدوية لإطارات مستخرجة من الملفات النهائية.

## الملخّص

| المخرَج | المدة | الأبعاد | Loudness | True peak | الحجم |
|---|---|---|---|---|---|
| master.mp4 | 9:24.6 | 1920×1080 · 30fps · H.264 | −14.0 LUFS | −1.0 dBTP | 263 MB |
| master_no_voice.mp4 | 9:24.6 | 1920×1080 | −16.0 LUFS | −1.0 dBTP | 264 MB |
| master_sfx_only.mp4 | 9:24.6 | 1920×1080 | −19.5 LUFS | −3.0 dBTP | 244 MB |
| short_v1.mp4 | 0:53.6 | 1080×1920 · 30fps · H.264 | −14.0 LUFS | −1.4 dBTP | 31 MB |
| short_v1_no_voice.mp4 | 0:53.6 | 1080×1920 | −15.9 LUFS | −2.4 dBTP | 31 MB |
| short_v1_sfx_only.mp4 | 0:53.6 | 1080×1920 | −19.1 LUFS | −3.0 dBTP | 30 MB |

الفحوص الآلية: **0 FAIL**. البنود المفتوحة: 2 RISK · 1 BLOCKED · 3 WARN (تفاصيلها في المراجعة اليدوية).
النسختان «بلا صوت» و«مؤثرات فقط» لا تُستهدفان بـ−14 (لا تعليق)؛ الفحص فيهما على الذروة فقط.

## الفحوص الآلية
| الفحص | النتيجة | القيمة المقاسة | الهدف |
|---|---|---|---|
| master.mp4 · الأبعاد | PASS | 1920x1080 | 1920x1080 |
| master.mp4 · fps/codec | PASS | 30.0 fps · h264 · yuvj420p | 30 · h264 · yuv420p |
| master.mp4 · الصوت | PASS | aac 48000 Hz 279 kb/s | AAC 48 kHz |
| master.mp4 · Loudness | PASS | -14.0 LUFS | -14 ±1 LU |
| master.mp4 · True peak | PASS | -1.0 dBFS | ≤ −1 dBTP (تسامح 0.1) |
| master_no_voice.mp4 · الأبعاد | PASS | 1920x1080 | 1920x1080 |
| master_no_voice.mp4 · fps/codec | PASS | 30.0 fps · h264 · yuvj420p | 30 · h264 · yuv420p |
| master_no_voice.mp4 · الصوت | PASS | aac 48000 Hz 291 kb/s | AAC 48 kHz |
| master_no_voice.mp4 · True peak | PASS | -1.0 dBFS | ≤ −1 dBTP (تسامح 0.1) |
| master_sfx_only.mp4 · الأبعاد | PASS | 1920x1080 | 1920x1080 |
| master_sfx_only.mp4 · fps/codec | PASS | 30.0 fps · h264 · yuvj420p | 30 · h264 · yuv420p |
| master_sfx_only.mp4 · الصوت | PASS | aac 48000 Hz 11 kb/s | AAC 48 kHz |
| master_sfx_only.mp4 · True peak | PASS | -3.0 dBFS | ≤ −1 dBTP (تسامح 0.1) |
| short_v1.mp4 · الأبعاد | PASS | 1080x1920 | 1080x1920 |
| short_v1.mp4 · fps/codec | PASS | 30.0 fps · h264 · yuvj420p | 30 · h264 · yuv420p |
| short_v1.mp4 · الصوت | PASS | aac 48000 Hz 272 kb/s | AAC 48 kHz |
| short_v1.mp4 · Loudness | PASS | -14.0 LUFS | -14 ±1 LU |
| short_v1.mp4 · True peak | PASS | -1.4 dBFS | ≤ −1 dBTP (تسامح 0.1) |
| short_v1_no_voice.mp4 · الأبعاد | PASS | 1080x1920 | 1080x1920 |
| short_v1_no_voice.mp4 · fps/codec | PASS | 30.0 fps · h264 · yuvj420p | 30 · h264 · yuv420p |
| short_v1_no_voice.mp4 · الصوت | PASS | aac 48000 Hz 285 kb/s | AAC 48 kHz |
| short_v1_no_voice.mp4 · True peak | PASS | -2.4 dBFS | ≤ −1 dBTP (تسامح 0.1) |
| short_v1_sfx_only.mp4 · الأبعاد | PASS | 1080x1920 | 1080x1920 |
| short_v1_sfx_only.mp4 · fps/codec | PASS | 30.0 fps · h264 · yuvj420p | 30 · h264 · yuv420p |
| short_v1_sfx_only.mp4 · الصوت | PASS | aac 48000 Hz 27 kb/s | AAC 48 kHz |
| short_v1_sfx_only.mp4 · True peak | PASS | -3.0 dBFS | ≤ −1 dBTP (تسامح 0.1) |
| المدة · الطويل | PASS | 564.57 s (9:24.6) | 8–10 دقائق |
| المدة · الشورت | PASS | 53.56 s | 45–55 ث |
| subtitles_ar.srt · بنية | PASS | 184 مقطع · >حد السطر: 0 · >سطرين: 0 · تداخل: 0 | ≤2 سطر · بلا تداخل |
| subtitles_ar.srt · مقاطع < 1.2 ث | INFO | 3 | تحذير فقط (repo make_srt) |
| subtitles_ar_short.srt · بنية | PASS | 16 مقطع · >حد السطر: 0 · >سطرين: 0 · تداخل: 0 | ≤2 سطر · بلا تداخل |
| subtitles_ar_short.srt · مقاطع < 1.2 ث | INFO | 1 | تحذير فقط (repo make_srt) |
| subtitles_en.srt · بنية | PASS | 163 مقطع · >حد السطر: 0 · >سطرين: 0 · تداخل: 0 | ≤2 سطر · بلا تداخل |
| subtitles_en.srt · مقاطع < 1.2 ث | INFO | 8 | تحذير فقط (repo make_srt) |
| subtitles_en_short.srt · بنية | PASS | 15 مقطع · >حد السطر: 0 · >سطرين: 0 · تداخل: 0 | ≤2 سطر · بلا تداخل |
| subtitles_en_short.srt · مقاطع < 1.2 ث | INFO | 1 | تحذير فقط (repo make_srt) |
| episode_meta.json · قفل الباليت (البيانات) | PASS | لا ألوان حرفية | ألوان brand.json فقط |
| episode_meta.json · وسم الصور | PASS | AI=20 (وسم تلقائي «إعادة تصوّر») · أرشيف=6 بسطر مصدر | كل صورة موسومة |
| episode_meta.json · نطاقات الخيال | PASS | [{"t_in": 261.13, "t_out": 490.679}, {"t_in": 513.217, "t_out": 530.896}] | وسم «خيال تاريخي» دائم داخل الافتراض |
| episode_meta_short.json · قفل الباليت (البيانات) | PASS | لا ألوان حرفية | ألوان brand.json فقط |
| episode_meta_short.json · وسم الصور | PASS | AI=6 (وسم تلقائي «إعادة تصوّر») · أرشيف=1 بسطر مصدر | كل صورة موسومة |
| episode_meta_short.json · نطاقات الخيال | PASS | [{"t_in": 18.0, "t_out": 47.145}] | وسم «خيال تاريخي» دائم داخل الافتراض |
| المكوّنات الجديدة · قفل الباليت | PASS | {} | لا HEX خارج الهوية |
| قفل الخطوط | PASS | headlineFont/bodyFont من الثيم فقط | Amiri + IBM Plex Sans Arabic |
| credits.csv يغطي كل الصور | PASS | 14 صورة · 20 سجل | كل أصل مسجّل |
| FACT_CHECK | INFO | {"VERIFIED": 21, "VERIFIED_ATTRIBUTED": 1, "NEEDS_2ND_SOURCE": 1, "REVIEW": 2, "VERIFIED_SECONDARY": 2, "FICTION_LABELED": 1} | كل ادعاء ← مصدر |

**FAIL: 0**

## المراجعة اليدوية (إطارات مستخرجة من الملفات النهائية)

| البند | النتيجة | ملاحظة |
|---|---|---|
| RTL واتجاه النص العربي | PASS | كل العناوين والترجمات تُقرأ من اليمين؛ الأرقام اللاتينية معزولة بعلامات BiDi في SRT |
| الخطوط | PASS | Amiri للعناوين، IBM Plex Sans Arabic للمتن — لا Cairo/Inter |
| الباليت | PASS | ألوان brand.json فقط (فحص آلي + بصري)؛ العنابي محصور في نطاقات الخيال |
| وسم الخيال | PASS | شارة «خيال تاريخي» + إطار عنابي دائمان طوال كل نطاق افتراضي (طويل 04:21–08:10 و08:33–08:51؛ شورت 00:18–00:47) |
| وسم صور AI | PASS | «إعادة تصوّر · ذكاء اصطناعي» أعلى كل لقطة مولّدة |
| سطر مصدر الأرشيف | PASS | «جامع التواريخ · نحو 1430 · ملكية عامة» على لقطات الأرشيف |
| العلامة المائية | PASS | أعلى الوسط؛ تختفي في شاشة النهاية بالطويل (الشعار الرسمي ظاهر فيها). في الشورت تبقى فوق بطاقة الـCTA لأنها ليست شاشة نهاية بشعار |
| منطقة الترجمة (Safe area) | PASS* | 9:16 داخل 1210–1360. *عند 00:45 في الشورت: عنوان اللوحة السفلية في الشاشة المنقسمة قريب من شريط الترجمة (لا تداخل نصّي، لكن ازدحام بصري) |
| تداخل الترجمات المحروقة (الشورت) | PASS | أُصلح تداخل 0.08 ث بين المقاطع وأُعيد رندر الشورت بالكامل (06:11 UTC) — 0 تداخل في SRT |
| الترجمة المحروقة (الطويل) | INFO | الطويل بلا ترجمة محروقة (burn_in=false) ← يُرفع SRT العربي والإنجليزي على يوتيوب |
| مقاطع ترجمة < 1.2 ث | INFO | طويل AR 3 / EN 8 · شورت AR 1 / EN 1 — مقروءة لكنها سريعة |
| pix_fmt | INFO | yuvj420p (نطاق كامل pc) من خط Remotion؛ يوتيوب يقبله ويحوّله. لا يؤثر على الجودة |
| الصورة المصغّرة A | RISK | العنوان «لو قَبِل الخليفة؟» مع صورة **هولاكو** (pd03) ← قد يُفهم أنها صورة الخليفة. البديل: B أو C، أو تعديل العنوان |
| مصدر pd03 | RISK | حقل المصدر في Commons يشير إلى meisterdrucke.fr ← يُتحقق من نسخة BnF Gallica قبل النشر، أو تُستبدل |
| الموسيقى | BLOCKED | ليست من YouTube Audio Library (تتطلب تسجيل دخول) ← موسيقى أصلية مولّدة إجرائيًا؛ الاستبدال عبر `tools/mux_only.sh` |
| التعليق الصوتي | DRAFT_VO | صوت منصة اصطناعي (voice-01)، ليس تسجيلًا رسميًا |
| FACT_CHECK | WARN | F09 يحتاج مصدرًا ثانيًا؛ F10/F16 قيد المراجعة؛ F28 خيال موسوم |
| الترجمة الإنجليزية | WARN | تحتاج مراجعة بشرية (قاعدة brand.json) |
