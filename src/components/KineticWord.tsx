import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate } from 'remotion';
import { getKineticWordStyle } from '../styles';

interface KineticWordProps {
  word: string;
  startFrame: number;
  endFrame: number;
}

export const KineticWord: React.FC<KineticWordProps> = ({ word, startFrame, endFrame }) => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  // مقياس التصميم: القيم الأساسية مضبوطة على عرض 3840 (4K) ثم تتدرج مع أي دقة
  const scale = width / 3840;

  // التحقق من ما إذا كانت هذه الكلمة هي الكلمة النشطة حالياً
  const isActive = frame >= startFrame && frame <= endFrame;

  // حساب تقدم الحركة للكلمة النشطة (0 إلى 1)
  const progress = isActive
    ? interpolate(frame, [startFrame, endFrame], [0, 1], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      })
    : 0;

  // تأثير السبرينج للتكبير
  const springAnimation = isActive ? Math.sin(progress * Math.PI) : 0;

  const style = getKineticWordStyle(isActive, springAnimation, scale);

  return <span style={style}>{word}</span>;
};