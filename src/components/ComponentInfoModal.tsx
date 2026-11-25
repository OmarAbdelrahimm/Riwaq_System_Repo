/**
 * Component & Hotspot Documentary Inspection Card
 */

import React from 'react';
import { X, ShieldCheck, Calendar, User, Info } from 'lucide-react';
import { AnnotationItem } from '../types.ts';

interface ComponentInfo {
  id: string;
  nameEn: string;
  nameAr: string;
  descriptionEn?: string;
  descriptionAr?: string;
  era?: string;
  certainty?: string;
}

interface ComponentInfoModalProps {
  selectedComponent: ComponentInfo | null;
  selectedAnnotation: AnnotationItem | null;
  onClose: () => void;
}

export const ComponentInfoModal: React.FC<ComponentInfoModalProps> = ({
  selectedComponent,
  selectedAnnotation,
  onClose,
}) => {
  if (!selectedComponent && !selectedAnnotation) return null;

  const titleEn = selectedAnnotation?.titleEn || selectedComponent?.nameEn || 'Architectural Component';
  const titleAr = selectedAnnotation?.titleAr || selectedComponent?.nameAr || '';
  const date = selectedAnnotation?.date || selectedComponent?.era || 'Historic Period';
  const descEn = selectedAnnotation?.descriptionEn || selectedComponent?.descriptionEn || '';
  const descAr = selectedAnnotation?.descriptionAr || selectedComponent?.descriptionAr || '';
  const certainty = selectedAnnotation?.certainty || selectedComponent?.certainty || 'Archaeological Record';

  return (
    <div className="absolute top-20 left-1/2 -translate-x-1/2 z-40 w-full max-w-lg px-4 pointer-events-auto">
      <div className="bg-[#1C1B19]/95 border-2 border-[#A98A4B] text-[#F3EBDB] rounded-xl p-5 shadow-2xl backdrop-blur-none flex flex-col gap-3 font-sans">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-[#A98A4B]/30 pb-3">
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono-doc uppercase tracking-wider px-2 py-0.5 rounded bg-[#A98A4B] text-[#1C1B19] font-bold">
                DOCUMENTARY CALLOUT
              </span>
              <span className="text-xs font-mono-doc text-[#A98A4B]">{date}</span>
            </div>
            <h2 className="text-lg font-serif-doc font-bold text-[#F3EBDB] mt-1">
              {titleEn}
            </h2>
            {titleAr && (
              <span className="font-arabic text-sm text-[#A98A4B]">
                {titleAr}
              </span>
            )}
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded-full text-[#F3EBDB]/70 hover:text-white hover:bg-[#F3EBDB]/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex flex-col gap-2.5 text-xs text-[#F3EBDB]/90 leading-relaxed">
          <p>{descEn}</p>
          {descAr && (
            <p className="font-arabic text-sm text-[#A98A4B]/90 text-right leading-relaxed border-t border-white/10 pt-2">
              {descAr}
            </p>
          )}
        </div>

        {/* Footer with Historical Certainty */}
        <div className="flex items-center justify-between border-t border-[#A98A4B]/30 pt-2.5 text-[11px] font-mono-doc text-[#F3EBDB]/70">
          <div className="flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-[#A98A4B]" />
            <span>Certainty: <strong className="text-[#F3EBDB]">{certainty}</strong></span>
          </div>

          <span className="text-[#A98A4B]">RUWAQ • وثائقي</span>
        </div>
      </div>
    </div>
  );
};
