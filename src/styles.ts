import React from 'react';
import { interpolateColors } from 'remotion';

/**
 * أنماط النصوص الكينتيكية — مبنية على قالب المستخدم الأصلي (3840×2160)
 * كل القيم بالبكسل مضروبة في `scale = width/3840` لتعمل على أي دقة.
 */

// تنسيق حاوية النص الكلية في الثلث السفلي من الشاشة
export const getTextContainerStyle = (scale = 1): React.CSSProperties => ({
  position: 'absolute',
  direction: 'rtl',
  bottom: `${180 * scale}px`,
  left: '5%',
  width: '90%',
  display: 'flex',
  flexWrap: 'wrap',
  justifyContent: 'center',
  alignItems: 'center',
  textAlign: 'center',
  pointerEvents: 'none',
  padding: `0 ${20 * scale}px`,
});

// تنسيق الكلمة بناءً على «شدة الإبراز» emphasis (0 = عادية، 1 = منطوقة الآن)
// ومعامل تكبير السبرينج popScale — كل القيم تتدرج بسلاسة من رقم الإطار نفسه.
// ملاحظة تصميمية: ذروة الحجم 134 والحجم العادي 118 هما نفس نسبة 85/75 لكن
// مضبوطتان على أساس 3840 (أي ~150/170 مكافئة عند 1080) حتى لا يصغر النص في 4K.
export const getKineticWordStyle = (
  emphasis: number,
  popScale: number,
  scale = 1
): React.CSSProperties => {
  const e = Math.min(1, Math.max(0, emphasis));

  return {
    display: 'inline-block',
    fontFamily: "'Amiri', 'IBM Plex Sans Arabic', serif",
    fontWeight: 900,
    fontSize: `${(118 + 16 * e) * scale}px`, // تكبير تدريجي للكلمة المنطوقة مع السبرينج

    // الألوان والهوية البصرية — لوحة علامة رِواق التجارية:
    // ذهبيات العلامة (gold_light #C2A469) للذروة والرقّي (#F3EBDB) للقاعدة
    // بدلاً من برتقالي/أبيض عام — التدرج محسوب إطاراً بإطار عبر interpolateColors
    color: interpolateColors(e, [0, 1], ['#F3EBDB', '#C2A469']),
    opacity: 0.3 + 0.7 * e, // من 0.3 (محيطية) إلى 1.0 (منطوقة الآن)

    // حركية التكبير والبروز: تكبير السبرينج + رفع خفيف يتناسب مع شدة الإبراز
    transform: `scale(${popScale}) translateY(${-14 * e * scale}px)`,

    // التوهج الخلفي للكلمة النشطة — شدتّه تتبع الإبراز حتى لا يومض عند الدخول والخروج
    textShadow:
      e > 0.01
        ? `0px 0px ${34 * scale}px rgba(194, 164, 105, ${0.6 * e}), 0px 0px ${68 * scale}px rgba(194, 164, 105, ${0.4 * e})`
        : 'none',

    // ⚠️ لا CSS `transition` هنا عمداً: Remotion يصدّر إطاراً بإطار، والانتقالات
    // المعتمدة على زمن المتصفح غير حتمية بين الإطارات. السلاسة تأتي من spring()
    // نفسه + إطارات التحرير الناعم في KineticWord.
    margin: `${12 * scale}px ${22 * scale}px`,
    letterSpacing: `${-1.5 * scale}px`,
  };
};

// تنسيق خلفية المشاهد مع تأثير كين بيرنز الخفيف
export const sceneContainerStyle: React.CSSProperties = {
  width: '100%',
  height: '100%',
  transformOrigin: 'center center',
};

// تنسيق صورة الخلفية
export const backgroundImageStyle: React.CSSProperties = {
  width: '100%',
  height: '100%',
  objectFit: 'cover',
};
