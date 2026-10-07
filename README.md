# رِواق — نظام إنتاج الفيديو (Riwaq Production System)

> **محرّك واحد، هويات متعددة.** القالب لا يعرف أي براند بالاسم — يقرأ كل شيء من الإعدادات.
> فيديو جديد = مجلد + `episode_meta.json`. صفر تعديل في الكود.

## الحالة الحالية
| المرحلة | الحالة |
|---|---|
| نظام التصميم والهوية (`brand.json`) | ✅ جاهز |
| طبقات الصوت (`voice_profiles.json`) | ✅ جاهز (رسمي + بديل تشغيلي + مؤقت) |
| سلسلة استوديو الصوت (`scripts/voice_finish.py`) | ✅ LUFS −16 · TP −1 · مطابقة تكيفية |
| **مطابقة البصمة (`scripts/pitch_match.py`)** | ❌ مرفوضة سمعيًا — أُلغيت من خط الإنتاج · الصوت التشغيلي = voice-01 + سلسلة الاستوديو |
| السونيك لوجو v2 | ✅ ثلاث نسخ (محرابي / نبض / قصيرة) |
| مكوّنات الفيديو (A–G) | ✅ سبعة + كابشنز + علامة مائية |
| الاختبار الذهبي `GOLDEN_001` | ✅ البيانات جاهزة — الريندر على جهازك |
| بوابة الجودة (`scripts/qc.py`) | ✅ فحوص بنيوية؛ فحوص الإطار بعد الريندر |

## التشغيل السريع
```bash
npm install
npm run studio                 # معاينة تفاعلية (Remotion Studio)
npm run render:golden:draft    # مسوّدة سريعة بنصف الدقة (للمراجعة)
```

## ☁️ الريندر السحابي (المعتمد — جهازك لا يعمل)
1. ارفع المستودع على GitHub مرة واحدة → `docs/GITHUB_SETUP.md` (دليل بالعربي خطوة بخطوة)
2. Actions → **render-episode** → Run workflow → اكتب معرّف المشروع
3. نزّل النتائج من **Artifacts**: MP4 + كابشنز AR/EN + تقرير QC

> الحصة المجانية تكفي ~30 شورتس أو ~6 فيديوهات طويلة شهريًا (مستودع خاص).

## البنية
```
10_System/
├── data/
│   ├── .. (انسخ brand.json + voice_profiles.json من 05_Template_Kit إلى data/)
│   └── projects/GOLDEN_001/episode_meta.json     ← مصدر الحقيقة الوحيد
├── src/
│   ├── engine/      types · theme(الألوان والخطوط) · safezones · timing
│   ├── components/  HookFrame · ChapterCard · QuoteCard · StatCard · LowerThird
│   │                SourceCard · EndScreen · Captions · Watermark · Paper(Look)
│   └── compositions/Episode.tsx                  ← يبني الخط الزمني من البيانات
├── public/           fonts (OFL) · projects/GOLDEN_001/audio
├── scripts/          voice_finish.py · make_srt.py · qc.py
└── docs/RUNBOOK.md
```

## قواعد إلزامية (من دستور الهوية)
- الألوان: `#1C1B19 #242218 #F3EBDB #EDE6D6 #A98A4B #C2A469 #EFE6D2 #5E2230 #8A7F6B #B9AE94` فقط.
- الخطوط: **Amiri** للعناوين · **IBM Plex Sans Arabic** للكابشنز والمعلومات.
- الحركة: منحنى واحد — تقطع مباشر + تلاشٍ 200ms · بلا وميض أو دوران.
- الكابشنز: سطران أقصى · ≤28 حرفًا عربيًا · الكلمات المؤثرة والأرقام ذهبية · لا تغطية للوجه.
- الصوت: الطبقة الرسمية للنشر فقط · وسم `DRAFT_VO` لأي مسوّدة · LUFS −16 ±0.5 · ذروة −1 dBTP.

## الريندر على جهازك (i7 · 8GB)
- `--concurrency=1` + `--gl=swiftshader` للمعاينة والمسودات.
- للريندر الطويل: قسّم لمقاطع ≤10 دقائق ثم ادمج بـ ffmpeg (أوامر جاهزة في `docs/RUNBOOK.md`).
- البديل السحابي: GitHub Actions (سير العمل مُوثَّق في RUNBOOK).

## الأصول والتراخيص
الخطوط المضمّنة بترخيص **OFL** (Amiri: aliftype · IBM Plex Sans Arabic: IBM) — استخدام تجاري مسموح.
أصول البراند (شعار/أيقونات/أنماط) مملوكة للمشروع وتُسحب من `riwaq-brand/`.
