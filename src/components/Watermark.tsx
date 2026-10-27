import React from "react";
import { AbsoluteFill } from "remotion";
import { useTheme } from "../engine/theme";
import { BrandMark } from "./BrandMark";

/**
 * العلامة المائية — ثابتة من أول فريم لآخر فريم (حماية الـLoop: لا ظهور/اختفاء).
 * الموضع والهامش يأتيان من الثيم: الموضع داخل المنطقة الآمنة للاتجاه الحالي،
 * لا فوق شريط المنصة ولا فوق وجه/كابشن.
 */
export const Watermark: React.FC = () => {
  const { brand, width, color, safe } = useTheme();
  const wm = brand.theme.watermark;
  if (!wm) return null;

  const size = (wm.size_px * width) / 1080;
  const position = wm.position ?? "top-left";
  const insetX = (wm.inset_from_safe_zone ? safe.side : width * 0.055) as number;
  const insetY = (wm.inset_from_safe_zone ? safe.top : width * 0.055) as number;

  // الهامش الرأسي: أعلى = داخل المنطقة الآمنة العليا؛ أسفل = فوق المنطقة الآمنة السفلية
  const style: React.CSSProperties = { position: "absolute", opacity: wm.opacity };

  switch (position) {
    case "top-center":
      style.top = insetY;
      style.left = 0;
      style.right = 0;
      style.display = "flex";
      style.justifyContent = "center";
      break;
    case "top-right":
      style.top = insetY;
      style.right = insetX;
      break;
    case "bottom-right":
      style.bottom = (wm.inset_from_safe_zone ? safe.bottom : width * 0.055) as number;
      style.right = insetX;
      break;
    case "top-left":
    default:
      style.top = insetY;
      style.left = insetX;
      break;
  }

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div style={style}>
        <BrandMark sizePx={size} color={color("gold_light")} />
      </div>
    </AbsoluteFill>
  );
};
