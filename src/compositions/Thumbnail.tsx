import React from "react";
import { AbsoluteFill, Img } from "remotion";
import { BrandMark } from "../components/BrandMark";
import "../engine/fonts"; // تحميل خطوط العلامة الرسمية (Amiri + IBM Plex Sans Arabic)

// ── صور الشيخ ياسر الحزيمي — إطارات حقيقية مستخرجة من الفيديو الأصلي ──
// (بودكاست «بدون ورق» — الجزء 21 من 27 على Drive؛ قصّ 1152×864 حول الوجه بهامش علوي)
import imgA from "../../public/projects/PARADOX_012/assets/sheikh_f38.jpg"; // إيماءة شرح — طاقة تعليمية
import imgB from "../../public/projects/PARADOX_012/assets/sheikh_f100.jpg"; // ابتسامة دافئة — طاقة وجدانية

/**
 * 🖼️ أغلفة يوتيوب — الحلقة 12 «مفارقة الفلاح والنجاح» (PARADOX_012)
 *  - Thumbnail          : أفقي 1280×720 (فيديو عادي)
 *  - ThumbnailVertical  : عمودي 1080×1920 (YouTube Shorts)
 * صورتان حقيقيتان للشيخ من المصدر + هوية رِواق، بنسختين نصيتين:
 *   A — «النجاح ليس فلاحاً!» (لقطة الشرح)      B — «هل أنتَ مُفلح؟» (لقطة الابتسامة)
 * الزاوية السفلية اليمنى للأفقي فارغة عمداً (شارة مدة الفيديو)، وأسفل العمودي
 * خالٍ من العناصر الحرجة (منطقة واجهة Shorts).
 */

// ألوان هوية رِواق (brand.json)
const INK = "#1C1B19";
const GOLD = "#A98A4B";
const GOLD_LIGHT = "#C2A469";
const PARCHMENT = "#F3EBDB";
const FONT = "'IBM Plex Sans Arabic', sans-serif";
const DISPLAY_FONT = "'Amiri', serif"; // خط العرض في الهوية — لكلمة الذروة

type Variant = "A" | "B";

const COPY: Record<
  Variant,
  { eyebrow: string; line1: string; punch: string; footer: string }
> = {
  A: {
    eyebrow: "من بودكاست بدون ورق",
    line1: "النجاح ليس",
    punch: "فلاحاً!",
    footer: "سعي • وعي • وحي",
  },
  B: {
    eyebrow: "سؤالٌ يستحق التأمّل",
    line1: "هل أنتَ",
    punch: "مُفلح؟",
    footer: "الفرق بين النجاح والفلاح",
  },
};

/** الغلاف الأفقي الرسمي 1280×720 */
export const Thumbnail: React.FC<{ variant?: Variant }> = ({ variant = "A" }) => {
  const copy = COPY[variant];
  const photo = variant === "A" ? imgA : imgB;

  return (
    <AbsoluteFill style={{ backgroundColor: INK, overflow: "hidden", fontFamily: FONT }}>
      {/* توهّج ذهبي خفيف في الخلفية */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 60% 55% at 22% 38%, rgba(194,164,105,0.13) 0%, rgba(28,27,25,0) 70%), radial-gradient(ellipse 50% 60% at 88% 12%, rgba(194,164,105,0.08) 0%, rgba(28,27,25,0) 65%)",
        }}
      />

      {/* 📷 صورة الشيخ — الجانب الأيمن، بنظرة تتجه نحو النص */}
      <div style={{ position: "absolute", right: 0, top: 0, width: 730, height: 720, overflow: "hidden" }}>
        <Img
          src={photo}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: "92% 50%",
            filter: "contrast(1.07) saturate(1.1) brightness(1.02)",
          }}
        />
        {/* مزج قصير للحافة اليسرى في الخلفية (لا يصل إلى الوجه) + تعتيم سفلي/علوي خفيف */}
        <AbsoluteFill
          style={{
            background: `linear-gradient(90deg, ${INK} 0%, rgba(28,27,25,0.55) 8%, rgba(28,27,25,0) 20%), linear-gradient(0deg, rgba(28,27,25,0.45) 0%, rgba(28,27,25,0) 30%), linear-gradient(180deg, rgba(28,27,25,0.22) 0%, rgba(28,27,25,0) 22%)`,
          }}
        />
      </div>

      {/* 🖋️ كتلة النص — الجانب الأيسر (محاذاة عربية نحو الصورة) */}
      <div
        dir="rtl"
        style={{
          position: "absolute",
          left: 54,
          top: 0,
          width: 540,
          height: 720,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "flex-start",
          textAlign: "right",
        }}
      >
        {/* شارة علوية */}
        <div
          style={{
            border: `1.5px solid ${GOLD}`,
            borderRadius: 999,
            padding: "7px 20px 10px",
            color: PARCHMENT,
            fontSize: 26,
            fontWeight: 500,
            background: "rgba(28,27,25,0.55)",
            marginBottom: 28,
            whiteSpace: "nowrap",
          }}
        >
          {copy.eyebrow}
        </div>

        {/* العنوان الجاذب */}
        <div
          style={{
            color: PARCHMENT,
            fontSize: 92,
            fontWeight: 700,
            lineHeight: 1.16,
            textShadow: "0 6px 34px rgba(0,0,0,0.6)",
            whiteSpace: "nowrap",
          }}
        >
          {copy.line1}
        </div>
        <div
          style={{
            color: GOLD_LIGHT,
            fontFamily: DISPLAY_FONT,
            fontSize: 168,
            fontWeight: 700,
            lineHeight: 1.3,
            textShadow: "0 0 38px rgba(194,164,105,0.38), 0 8px 40px rgba(0,0,0,0.55)",
            whiteSpace: "nowrap",
          }}
        >
          {copy.punch}
        </div>

        {/* فاصل ذهبي + الاسم والتوقيع */}
        <div style={{ width: 86, height: 4, background: GOLD, borderRadius: 2, margin: "22px 0 18px" }} />
        <div
          style={{
            color: PARCHMENT,
            fontSize: 44,
            fontWeight: 700,
            lineHeight: 1.2,
            textShadow: "0 4px 24px rgba(0,0,0,0.6)",
            whiteSpace: "nowrap",
          }}
        >
          ياسر الحزيمي
        </div>
        <div
          style={{
            color: GOLD_LIGHT,
            fontSize: 31,
            fontWeight: 500,
            lineHeight: 1.3,
            marginTop: 8,
            textShadow: "0 3px 18px rgba(0,0,0,0.6)",
            whiteSpace: "nowrap",
          }}
        >
          {copy.footer}
        </div>
      </div>

      {/* مركيزة رِواق — الزاوية العلوية اليسرى */}
      <div style={{ position: "absolute", left: 54, top: 42, opacity: 0.92 }}>
        <BrandMark sizePx={56} color={GOLD_LIGHT} />
      </div>

      {/* إطار رِواق الذهبي الرفيع */}
      <div
        style={{
          position: "absolute",
          inset: 16,
          border: `1.5px solid ${GOLD}55`,
          boxSizing: "border-box",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};

/**
 * الغلاف العمودي 1080×1920 — YouTube Shorts.
 * التكوين: صورة الشيخ بعرض كامل في النصف العلوي، وكتلة النص ممركزة في الثلث
 * السفلي الأوسط (تنتهي قبل ~240px من الأسفل — خارج منطقة عنوان/أزرار الواجهة).
 */
export const ThumbnailVertical: React.FC<{ variant?: Variant }> = ({ variant = "B" }) => {
  const copy = COPY[variant];
  const photo = variant === "A" ? imgA : imgB;

  return (
    <AbsoluteFill style={{ backgroundColor: INK, overflow: "hidden", fontFamily: FONT }}>
      {/* 📷 صورة الشيخ — بعرض كامل أعلى الكادر، الوجه ممركز وكبير */}
      <div style={{ position: "absolute", left: 0, top: 0, width: 1080, height: 1170, overflow: "hidden" }}>
        <Img
          src={photo}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: "77% 50%",
            filter: "contrast(1.07) saturate(1.1) brightness(1.02)",
          }}
        />
        {/* تعتيم علوي للمركيزة + مزج سفلي ناعم في خلفية النص */}
        <AbsoluteFill
          style={{
            background: `linear-gradient(180deg, rgba(28,27,25,0.45) 0%, rgba(28,27,25,0) 20%), linear-gradient(0deg, ${INK} 2%, rgba(28,27,25,0.88) 15%, rgba(28,27,25,0) 42%)`,
          }}
        />
      </div>

      {/* توهّج ذهبي خلف كتلة النص */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 85% 32% at 50% 66%, rgba(194,164,105,0.13) 0%, rgba(28,27,25,0) 70%)",
        }}
      />

      {/* مركيزة رِواق — أعلى الوسط فوق الصورة */}
      <div
        style={{
          position: "absolute",
          top: 52,
          left: 0,
          width: 1080,
          display: "flex",
          justifyContent: "center",
          opacity: 0.95,
        }}
      >
        <BrandMark sizePx={64} color={GOLD_LIGHT} />
      </div>

      {/* 🖋️ كتلة النص — ممركزة، تنتهي قبل منطقة واجهة Shorts السفلية */}
      <div
        dir="rtl"
        style={{
          position: "absolute",
          left: 0,
          top: 940,
          width: 1080,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          textAlign: "center",
          padding: "0 56px",
          boxSizing: "border-box",
        }}
      >
        {/* شارة علوية */}
        <div
          style={{
            border: `1.5px solid ${GOLD}`,
            borderRadius: 999,
            padding: "8px 26px 12px",
            color: PARCHMENT,
            fontSize: 33,
            fontWeight: 500,
            background: "rgba(28,27,25,0.62)",
            marginBottom: 32,
            whiteSpace: "nowrap",
          }}
        >
          {copy.eyebrow}
        </div>

        {/* العنوان الجاذب */}
        <div
          style={{
            color: PARCHMENT,
            fontSize: 112,
            fontWeight: 700,
            lineHeight: 1.16,
            textShadow: "0 8px 40px rgba(0,0,0,0.65)",
            whiteSpace: "nowrap",
          }}
        >
          {copy.line1}
        </div>
        <div
          style={{
            color: GOLD_LIGHT,
            fontFamily: DISPLAY_FONT,
            fontSize: 246,
            fontWeight: 700,
            lineHeight: 1.3,
            textShadow: "0 0 44px rgba(194,164,105,0.4), 0 10px 48px rgba(0,0,0,0.6)",
            whiteSpace: "nowrap",
          }}
        >
          {copy.punch}
        </div>

        {/* فاصل ذهبي + الاسم والتوقيع */}
        <div style={{ width: 96, height: 5, background: GOLD, borderRadius: 3, margin: "24px 0 20px" }} />
        <div
          style={{
            color: PARCHMENT,
            fontSize: 56,
            fontWeight: 700,
            lineHeight: 1.2,
            textShadow: "0 5px 28px rgba(0,0,0,0.65)",
            whiteSpace: "nowrap",
          }}
        >
          ياسر الحزيمي
        </div>
        <div
          style={{
            color: GOLD_LIGHT,
            fontSize: 40,
            fontWeight: 500,
            lineHeight: 1.3,
            marginTop: 10,
            textShadow: "0 4px 22px rgba(0,0,0,0.65)",
            whiteSpace: "nowrap",
          }}
        >
          {copy.footer}
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
