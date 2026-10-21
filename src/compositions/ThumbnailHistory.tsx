import React from "react";
import { AbsoluteFill, Img } from "remotion";
import { BrandMark } from "../components/BrandMark";
import "../engine/fonts"; // تحميل خطوط العلامة الرسمية (Amiri + IBM Plex Sans Arabic)

// ── لوحتا «رحلة العصور» — رسم مولّد بموضوع الفيديو (لا أشخاص) بألوان رِواق ──
// art_wide: بانوراما 1584×672 (حجر ← زراعة وكتابة ← طباعة وصناعة ← ذكاء اصطناعي)
// art_tall: نسخة عمودية 768×1376 بنفس التدرّج من الكهف إلى كرة الذكاء الاصطناعي
import artWide from "../../public/projects/HISTORY83_001/assets/art_wide.jpg";
import artTall from "../../public/projects/HISTORY83_001/assets/art_tall.jpg";

/**
 * 🖼️ أغلفة فيديو «تاريخ البشرية في 83 ثانية: من الحجر إلى الذكاء الاصطناعي» (HISTORY83_001)
 *  - HistoryThumbnail         : أفقي 1280×720 — البانوراما بعرض كامل كلوحة متحف + شريط عنوان حبري
 *  - HistoryThumbnailVertical : عمودي 1080×1920 (YouTube Shorts) — اللوحة العمودية ملء الكادر
 * نص الغلاف: «تاريخ البشرية كله في 83 ثانية!» + «من الحجر إلى الذكاء الاصطناعي».
 * الزاوية السفلية اليمنى للأفقي بلا عناصر حرجة (شارة المدة)، وأسفل العمودي
 * خالٍ بنحو 240px (منطقة واجهة Shorts).
 */

// ألوان هوية رِواق (brand.json)
const INK = "#1C1B19";
const GOLD = "#A98A4B";
const GOLD_LIGHT = "#C2A469";
const PARCHMENT = "#F3EBDB";
const FONT = "'IBM Plex Sans Arabic', sans-serif";
const DISPLAY_FONT = "'Amiri', serif"; // خط العرض في الهوية — لكلمة الذروة

const COPY = {
  eyebrow: "رِواق | تاريخ وتراث",
  line1: "تاريخ البشرية كله في",
  punch: "83 ثانية!",
  footer: "من الحجر إلى الذكاء الاصطناعي",
};

/** الغلاف الأفقي الرسمي 1280×720 */
export const HistoryThumbnail: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: INK, overflow: "hidden", fontFamily: FONT }}>
      {/* 🎨 البانوراما — بعرض كامل أعلى الكادر (1584×672 ← 1280×543) */}
      <div style={{ position: "absolute", left: 0, top: 0, width: 1280, height: 543, overflow: "hidden" }}>
        <Img
          src={artWide}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: "50% 50%",
            filter: "contrast(1.06) saturate(1.08) brightness(1.01)",
          }}
        />
        {/* تعتيم علوي خفيف لقراءة الشارة */}
        <AbsoluteFill
          style={{
            background:
              "linear-gradient(180deg, rgba(28,27,25,0.30) 0%, rgba(28,27,25,0) 20%)",
          }}
        />
      </div>

      {/* شارة القناة — أعلى اليمين فوق اللوحة */}
      <div
        dir="rtl"
        style={{
          position: "absolute",
          top: 26,
          right: 26,
          border: `1.5px solid ${GOLD}`,
          borderRadius: 999,
          padding: "6px 20px 9px",
          color: PARCHMENT,
          fontSize: 24,
          fontWeight: 500,
          background: "rgba(28,27,25,0.58)",
          whiteSpace: "nowrap",
        }}
      >
        {COPY.eyebrow}
      </div>

      {/* خط ذهبي فاصل بين اللوحة وشريط العنوان */}
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 543,
          width: 1280,
          height: 3,
          background: `linear-gradient(90deg, ${GOLD} 0%, ${GOLD_LIGHT} 50%, ${GOLD} 100%)`,
          opacity: 0.85,
        }}
      />

      {/* توهّج ذهبي خفيف في شريط العنوان */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 55% 30% at 70% 92%, rgba(194,164,105,0.12) 0%, rgba(28,27,25,0) 70%)",
        }}
      />

      {/* 🖋️ شريط العنوان — صف عربي: نص تمهيدي + كلمة الذروة + مركيزة رِواق */}
      <div
        dir="rtl"
        style={{
          position: "absolute",
          left: 0,
          top: 546,
          width: 1280,
          height: 174,
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          padding: "0 126px 0 46px", // هامش أيمن أوسع: إخلاء زاوية شارة مدة الفيديو
          boxSizing: "border-box",
          gap: 30,
        }}
      >
        {/* السطران التمهيدي والختامي */}
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-start" }}>
          <div
            style={{
              color: PARCHMENT,
              fontSize: 54,
              fontWeight: 700,
              lineHeight: 1.16,
              textShadow: "0 5px 26px rgba(0,0,0,0.6)",
              whiteSpace: "nowrap",
            }}
          >
            {COPY.line1}
          </div>
          <div
            style={{
              color: GOLD_LIGHT,
              fontSize: 31,
              fontWeight: 500,
              lineHeight: 1.3,
              marginTop: 7,
              textShadow: "0 3px 18px rgba(0,0,0,0.6)",
              whiteSpace: "nowrap",
            }}
          >
            {COPY.footer}
          </div>
        </div>

        {/* كلمة الذروة */}
        <div
          style={{
            color: GOLD_LIGHT,
            fontFamily: DISPLAY_FONT,
            fontSize: 124,
            fontWeight: 700,
            lineHeight: 1.3,
            textShadow: "0 0 36px rgba(194,164,105,0.4), 0 8px 38px rgba(0,0,0,0.55)",
            whiteSpace: "nowrap",
          }}
        >
          {COPY.punch}
        </div>

        <div style={{ flex: 1 }} />

        {/* مركيزة رِواق — نهاية الصف */}
        <div style={{ opacity: 0.92 }}>
          <BrandMark sizePx={56} color={GOLD_LIGHT} />
        </div>
      </div>

      {/* إطار رِواق الذهبي الرفيع */}
      <div
        style={{
          position: "absolute",
          inset: 12,
          border: `1.5px solid ${GOLD}55`,
          boxSizing: "border-box",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};

/** الغلاف العمودي 1080×1920 — YouTube Shorts */
export const HistoryThumbnailVertical: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: INK, overflow: "hidden", fontFamily: FONT }}>
      {/* 🎨 اللوحة العمودية — ملء الكادر كاملاً */}
      <div style={{ position: "absolute", left: 0, top: 0, width: 1080, height: 1920, overflow: "hidden" }}>
        <Img
          src={artTall}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: "50% 50%",
            filter: "contrast(1.06) saturate(1.08) brightness(1.01)",
          }}
        />
        {/* تعتيم علوي للمركيزة + ستارة سفلية لكتلة النص */}
        <AbsoluteFill
          style={{
            background: `linear-gradient(180deg, rgba(28,27,25,0.38) 0%, rgba(28,27,25,0) 16%), linear-gradient(0deg, ${INK} 4%, rgba(28,27,25,0.9) 30%, rgba(28,27,25,0) 56%)`,
          }}
        />
      </div>

      {/* مركيزة رِواق — أعلى اليسار (كرة الذكاء الاصطناعي تحتل أعلى الوسط) */}
      <div style={{ position: "absolute", left: 44, top: 48, opacity: 0.95 }}>
        <BrandMark sizePx={60} color={GOLD_LIGHT} />
      </div>

      {/* 🖋️ كتلة النص — ممركزة، تنتهي قبل منطقة واجهة Shorts السفلية */}
      <div
        dir="rtl"
        style={{
          position: "absolute",
          left: 0,
          top: 1086,
          width: 1080,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          textAlign: "center",
          padding: "0 56px",
          boxSizing: "border-box",
        }}
      >
        {/* شارة القناة */}
        <div
          style={{
            border: `1.5px solid ${GOLD}`,
            borderRadius: 999,
            padding: "8px 26px 12px",
            color: PARCHMENT,
            fontSize: 32,
            fontWeight: 500,
            background: "rgba(28,27,25,0.62)",
            marginBottom: 30,
            whiteSpace: "nowrap",
          }}
        >
          {COPY.eyebrow}
        </div>

        {/* العنوان الجاذب */}
        <div
          style={{
            color: PARCHMENT,
            fontSize: 88,
            fontWeight: 700,
            lineHeight: 1.16,
            textShadow: "0 8px 40px rgba(0,0,0,0.7)",
            whiteSpace: "nowrap",
          }}
        >
          {COPY.line1}
        </div>
        <div
          style={{
            color: GOLD_LIGHT,
            fontFamily: DISPLAY_FONT,
            fontSize: 210,
            fontWeight: 700,
            lineHeight: 1.3,
            textShadow: "0 0 46px rgba(194,164,105,0.42), 0 10px 50px rgba(0,0,0,0.65)",
            whiteSpace: "nowrap",
          }}
        >
          {COPY.punch}
        </div>

        {/* فاصل ذهبي + سطر الرحلة */}
        <div style={{ width: 96, height: 5, background: GOLD, borderRadius: 3, margin: "22px 0 18px" }} />
        <div
          style={{
            color: GOLD_LIGHT,
            fontSize: 46,
            fontWeight: 500,
            lineHeight: 1.3,
            textShadow: "0 4px 24px rgba(0,0,0,0.7)",
            whiteSpace: "nowrap",
          }}
        >
          {COPY.footer}
        </div>
      </div>

      {/* إطار رِواق الذهبي الرفيع */}
      <div
        style={{
          position: "absolute",
          inset: 20,
          border: `1.5px solid ${GOLD}55`,
          boxSizing: "border-box",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};
