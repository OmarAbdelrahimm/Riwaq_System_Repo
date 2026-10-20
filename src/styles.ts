import React from 'react';

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

// الدالة المسؤولة عن حساب التنسيق الحركي لكل كلمة بناءً على حالتها
export const getKineticWordStyle = (
  isSelected: boolean,
  springAnimation: number,
  scale = 1
): React.CSSProperties => {
  // حساب حجم التكبير الديناميكي باستخدام سبرينج ريموشن
  const wordScale = isSelected ? 1 + springAnimation * 0.15 : 1.0;

  return {
    display: 'inline-block',
    fontFamily: "'Amiri', 'IBM Plex Sans Arabic', serif",
    fontWeight: 900,
    fontSize: `${(isSelected ? 85 : 75) * scale}px`, // تضخيم الكلمة النشطة

    // الألوان والهوية البصرية — لوحة علامة رِواق التجارية
    color: isSelected ? '#C2A469' : '#F3EBDB', // gold_light للنشط، parchment للآخرين
    opacity: isSelected ? 1.0 : 0.3, // تعتيم الكلمات المحيطة لتركيز الانتباه

    // حركية التكبير والبروز
    transform: `scale(${wordScale}) translateY(${isSelected ? `${-10 * scale}px` : '0px'})`,

    // تأثير الإضاءة الخلفية للكلمة النشطة (Glow Effect)
    textShadow: isSelected
      ? `0px 0px ${25 * scale}px rgba(194, 164, 105, 0.6), 0px 0px ${50 * scale}px rgba(194, 164, 105, 0.4)`
      : 'none',

    // سلاسة النقل بين الحالات لمنع التقطع البصري
    transition: 'all 0.08s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
    margin: `${10 * scale}px ${18 * scale}px`,
    letterSpacing: `${-1 * scale}px`,
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
