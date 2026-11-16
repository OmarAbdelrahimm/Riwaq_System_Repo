import { interpolate, Easing } from "remotion";

export const secToFrames = (s: number, fps: number) => Math.round(s * fps);

/**
 * دخول/خروج موحّد للنصوص (من قواعد الحركة في brand.json)
 *
 * ملاحظة إصلاح: أي مُدخل زمني يُقسَّم على fps ليصبح «ثواني» قبل الاستيفاء،
 * ومُدخلات نطاق الخروج تُرتّب تصاعديًا. السبب: استدعاءات مثل
 * `textTiming(frame, fps, 12, durFrames - 10)` تعطي نطاقًا معكوسًا
 * [125, 0] عندما تقصُر مدة المشهد، فيرمي Remotion استثناء
 * "inputRange must be strictly monotonically increasing" ويتوقف الريندر.
 */
export function textTiming(
  frame: number,
  fps: number,
  inFrames: number,
  outFrames: number,
  rise: number
) {
  const f = fps > 0 ? fps : 30;
  // حد أدنى آمن: لا يبدأ الخروج قبل دخول مكتمل بإطار واحد
  const enterEnd = Math.max(1, inFrames);
  const exitStart = Math.max(enterEnd + 1, outFrames && isFinite(outFrames) ? outFrames : enterEnd + 1);

  const enterT = interpolate(frame, [0, enterEnd], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.2, 0.8, 0.2, 1),
  });
  const exitT = interpolate(frame, [exitStart, Math.max(exitStart + 1, f * 0.28)], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.2, 0.8, 0.2, 1),
  });
  return {
    opacity: Math.min(enterT, exitT),
    translateY: (1 - enterT) * rise - (1 - exitT) * rise * 0.6,
  };
}

/** Ken Burns خفيف جدًا للخلفية */
export function kenBurns(frame: number, durationFrames: number, from = 1.0, to = 1.06) {
  const t = interpolate(frame, [0, Math.max(1, durationFrames)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return from + (to - from) * t;
}
