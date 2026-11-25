# QA آلي — WHAT_IF_BAGHDAD_NEVER_FELL

| الفحص | النتيجة | القيمة المقاسة | الهدف |
|---|---|---|---|
| master.mp4 موجود | FAIL | غير موجود | — |
| master_no_voice.mp4 موجود | FAIL | غير موجود | — |
| master_sfx_only.mp4 موجود | FAIL | غير موجود | — |
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

**FAIL: 3** — master.mp4 موجود, master_no_voice.mp4 موجود, master_sfx_only.mp4 موجود
