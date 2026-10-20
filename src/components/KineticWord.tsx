import React from 'react';
import { useCurrentFrame, interpolate } from 'remotion';
import { getKineticWordStyle } from '../styles';

interface KineticWordProps {
  word: string;
  startFrame: number;
  endFrame: number;
}

export const KineticWord: React.FC<KineticWordProps> = ({ word, startFrame, endFrame }) => {
  const frame = useCurrentFrame();
  
  // التحقق من ما إذا كانت هذه الكلمة هي الكلمة النشطة حالياً
  const isActive = frame >= startFrame && frame <= endFrame;
  
  // حساب تقدم الحركة للكلمة النشطة (0 إلى 1)
  const progress = isActive 
    ? interpolate(frame, [startFrame, endFrame], [0, 1], { 
        extrapolateLeft: 'clamp', 
        extrapolateRight: 'clamp' 
      })
    : 0;
  
  // تأثير السبرينج للتكبير
  const springAnimation = isActive ? Math.sin(progress * Math.PI) : 0;
  
  const style = getKineticWordStyle(isActive, springAnimation);
  
  return (
    <span style={style}>
      {word}
    </span>
  );
};