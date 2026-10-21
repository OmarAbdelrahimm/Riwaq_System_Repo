import React from 'react';
import { useCurrentFrame, useVideoConfig, spring } from 'remotion';
import { getKineticWordStyle } from '../styles';

interface KineticWordProps {
  word: string;
  startFrame: number;
  endFrame: number;
}

// إعدادات السبرينج الفيزيائي لدخول الكلمة المنطوقة (Remotion spring — بطلب المراجعة)
const SPRING_CONFIG = { damping: 12, mass: 0.4, stiffness: 180 };
// إطارات «التحرير الناعم» بعد انتهاء الكلمة: رجوع تدريجي محسوب من رقم الإطار
// (البديل الحتمي عن CSS transition الذي لا يعمل بثبات في تصدير Remotion)
const RELEASE_FRAMES = 4;

export const KineticWord: React.FC<KineticWordProps> = ({ word, startFrame, endFrame }) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  // مقياس التصميم: القيم الأساسية مضبوطة على عرض 3840 (4K) ثم تتدرج مع أي دقة
  const scale = width / 3840;

  const clamp01 = (v: number) => Math.min(1, Math.max(0, v));

  let emphasis = 0; // شدة الإبراز 0..1 — تقود الحجم واللون والشفافية والتوهج
  let popScale = 1; // معامل التكبير اللحظي (transform) من السبرينج

  if (frame >= startFrame && frame <= endFrame) {
    // الكلمة منطوقة الآن: سبرينج حقيقي مرساة لحظة بدء الكلمة (لا يعتمد على مدتها)
    const activeProgress = spring({
      frame: frame - startFrame,
      fps,
      config: SPRING_CONFIG,
    });
    emphasis = clamp01(activeProgress);
    // تكبير ديناميكي: تجاوز مرن فوق القيمة المستقرة (1.15) عند ذروة السبرينج
    popScale = 1 + activeProgress * 0.15;
  } else if (frame > endFrame && frame <= endFrame + RELEASE_FRAMES) {
    // بعد انتهاء الكلمة مباشرة: تحرير ناعم من حالة الإبراز إلى الحالة العادية
    const endProgress = spring({
      frame: endFrame - startFrame,
      fps,
      config: SPRING_CONFIG,
    });
    const t = (frame - endFrame) / RELEASE_FRAMES;
    emphasis = clamp01(endProgress) * (1 - t);
    popScale = 1 + endProgress * 0.15 * (1 - t);
  }

  const style = getKineticWordStyle(emphasis, popScale, scale);

  return <span style={style}>{word}</span>;
};
