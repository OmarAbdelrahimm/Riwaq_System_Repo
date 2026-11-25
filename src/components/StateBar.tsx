/**
 * Architectural States Selector Bar
 * Maps directly to the 8 required states from the RUWAQ documentary brief
 */

import React from 'react';
import { ViewerState } from '../types.ts';

interface StateBarProps {
  currentState: ViewerState;
  onSelectState: (state: ViewerState) => void;
}

interface StateTabItem {
  id: ViewerState;
  index: number;
  labelEn: string;
  labelAr: string;
  badge?: string;
}

const STATES_LIST: StateTabItem[] = [
  {
    id: 'FATIMID_ORIGINAL',
    index: 1,
    labelEn: 'Fatimid Gate (1092)',
    labelAr: 'الحالة الأصلية 1092',
    badge: '1092 CE',
  },
  {
    id: 'TOP_PLAN',
    index: 2,
    labelEn: 'Top Plan',
    labelAr: 'المسقط الأفقي',
    badge: 'Ortho',
  },
  {
    id: 'SIDE_ELEVATION',
    index: 3,
    labelEn: 'Side Elevation',
    labelAr: 'المسقط الجانبي',
    badge: 'Ortho',
  },
  {
    id: 'FRONT_ELEVATION',
    index: 4,
    labelEn: 'Front Elevation',
    labelAr: 'الواجهة',
    badge: 'Ortho',
  },
  {
    id: 'PERSPECTIVE_3Q',
    index: 5,
    labelEn: 'Perspective 3/4',
    labelAr: 'منظور ثلاثي الأبعاد',
    badge: 'Cine',
  },
  {
    id: 'MAMLUK_ADDITIONS',
    index: 6,
    labelEn: 'Mamluk Minarets',
    labelAr: 'الإضافات اللاحقة',
    badge: '1415 CE',
  },
  {
    id: 'EXPLODED_VIEW',
    index: 7,
    labelEn: 'Exploded View',
    labelAr: 'المخطط التفكيكي',
    badge: 'Components',
  },
  {
    id: 'FULLY_ASSEMBLED',
    index: 8,
    labelEn: 'Fully Assembled',
    labelAr: 'التكوين النهائي',
    badge: 'Complete',
  },
];

export const StateBar: React.FC<StateBarProps> = ({
  currentState,
  onSelectState,
}) => {
  return (
    <div className="w-full flex items-center justify-start sm:justify-center overflow-x-auto gap-1.5 pb-1 px-1 scrollbar-thin">
      {STATES_LIST.map((item) => {
        const isActive = currentState === item.id;
        return (
          <button
            key={item.id}
            onClick={() => onSelectState(item.id)}
            className={`flex-shrink-0 flex items-center gap-2 px-3 py-1.5 rounded-md text-xs transition-all font-mono-doc border text-left ${
              isActive
                ? 'bg-[#A98A4B] text-[#1C1B19] border-[#A98A4B] font-semibold shadow-md'
                : 'bg-[#1C1B19]/80 text-[#F3EBDB]/80 border-[#A98A4B]/30 hover:bg-[#1C1B19] hover:text-[#F3EBDB] hover:border-[#A98A4B]/60'
            }`}
          >
            <span
              className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] ${
                isActive
                  ? 'bg-[#1C1B19] text-[#A98A4B] font-bold'
                  : 'bg-[#A98A4B]/20 text-[#A98A4B]'
              }`}
            >
              {item.index}
            </span>

            <div className="flex flex-col">
              <span className="leading-tight text-[11px] font-sans">
                {item.labelEn}
              </span>
              <span className="font-arabic text-[10px] opacity-80 leading-tight">
                {item.labelAr}
              </span>
            </div>
          </button>
        );
      })}
    </div>
  );
};
