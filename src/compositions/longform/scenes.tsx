import React from "react";
import { AbsoluteFill, Audio, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import {
  Backdrop,
  C,
  DepthBox,
  Glass,
  KWord,
  Logo,
  PhotoCard,
  PlateSlot,
  Rule,
  SceneShell,
  TextRail,
  ShapeField,
  WordRow,
  ip,
} from "./kit";

/* ═══════════════════════════════════════════════════════════════════════════
   scenes — 13 مشهد للنسخة الطويلة (1920×1080 · 30fps)
   كل مشهد دالة مستقلة: بتاخد مدة الإطارات وترجع مشهد كامل.
   التوقيتات من PLAN_LONGFORM.md (النسخة النهائية v3).
   ═══════════════════════════════════════════════════════════════════════════ */

export const SCENE_DUR: Record<number, number> = {
  1: 20.2,
  2: 18.4,
  3: 24.5,
  4: 26.0,
  5: 19.3,
  6: 36.9,
  7: 39.5,
  8: 30.2,
  9: 27.7,
  10: 9.3,
  11: 10.0,
  12: 13.0,
  13: 13.3,
};

/* ═══ 1 · الخطاف — همس مشدود ═══════════════════════════════════════════════
   سواد → ٤٢٠٣ يظهر بضربة → كاميرا تبعد تكشف الغرفة المحروقة.        */
export const S01Hook: React.FC = () => {
  const f = useCurrentFrame();
  const numIn = ip(f, 22, 52, 0, 1);
  const numScale = interpolate(f, [22, 60], [1.35, 1.0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const roomIn = ip(f, 90, 150, 0, 1);
  const numOut = ip(f, 96, 150, 1, 0.14);

  return (
    <AbsoluteFill style={{ backgroundColor: C.ink }}>
      {/* الغرفة المحروقة تظهر في الخلفية */}
      <AbsoluteFill style={{ opacity: roomIn * 0.85 }}>
        <SceneShell dur={600} kind="push" tint="deep">
          <DepthBox x={660} y={540} z={0} w={1100} h={780} keepSharp>
            <PhotoCard src="projects/TMB_001/plates/tmb_empty.jpg" w={1100} h={780} grad={0.55} kb={[1.02, 1.14]} />
          </DepthBox>
          <ShapeField seed={2} camZ={0} amt={0.6} />
        </SceneShell>
      </AbsoluteFill>

      {/* الرقم */}
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          opacity: numOut,
          transform: `scale(${numScale})`,
        }}
      >
        <div
          style={{
            fontFamily: "Amiri",
            fontWeight: 700,
            fontSize: 330,
            lineHeight: 1,
            color: C.gold,
            opacity: numIn,
            textShadow: `0 0 120px ${C.goldDeep}aa, 0 10px 60px rgba(0,0,0,.95)`,
          }}
        >
          ٤٢٠٣
        </div>
      </AbsoluteFill>

      {/* النص المتأخر */}
      <div
        style={{
          position: "absolute",
          right: 72,
          top: 96,
          width: 620,
          direction: "rtl",
          textAlign: "right",
          opacity: ip(f, 300, 350, 0, 1),
        }}
      >
        <WordRow words={["الأغرب؟"]} size={92} start={300} />
        <div style={{ marginTop: 18 }}>
          <WordRow words={["المدينة", "دي", "كانت", "لسه", "مليانة", "كتب"]} size={64} start={330} gap={5} />
        </div>
      </div>

      <Logo delay={360} />
    </AbsoluteFill>
  );
};

/* ═══ 2 · الوعد — فضول دافئ ═════════════════════════════════════════════════
   باب المكتبة في الغروب، ثم التلات «ولا».                              */
export const S02Promise: React.FC = () => {
  const f = useCurrentFrame();
  const words = ["متحف", "عاصمة", "مكتبة عالمية"];
  return (
    <SceneShell dur={555} kind="drift" tint="warm">
      <DepthBox x={1440} y={520} z={-40} w={780} h={890} ry={-8} keepSharp>
        <PhotoCard src="projects/TMB_001/plates/tmb_outside.jpg" w={780} h={890} kb={[1.0, 1.12]} grad={0.7} />
      </DepthBox>
      <ShapeField seed={5} camZ={0} />

      <div
        style={{
          position: "absolute",
          left: 110,
          top: 250,
          width: 900,
          direction: "rtl",
          textAlign: "right",
        }}
      >
        <div style={{ fontFamily: "Amiri", fontWeight: 700, fontSize: 74, color: C.parch, lineHeight: 1.5 }}>
          <div style={{ opacity: ip(f, 8, 40, 0, 1) }}>أكبر عملية إنقاذ للتراث</div>
          <div style={{ opacity: ip(f, 34, 70, 0, 1), color: `${C.parch}d0` }}>في أفريقيا كلها…</div>
        </div>

        <div style={{ marginTop: 44, display: "flex", flexDirection: "column", gap: 16 }}>
          {["ماحصلتش في متحف.", "ولا في عاصمة.", "ولا حتى في مكتبة عالمية."].map((t, i) => (
            <div
              key={t}
              style={{
                fontFamily: "IBM Plex Sans Arabic",
                fontWeight: 500,
                fontSize: 44,
                color: i === 2 ? C.gold : `${C.parch}88`,
                opacity: ip(f, 190 + i * 46, 220 + i * 46, 0, 1),
                transform: `translateX(${ip(f, 190 + i * 46, 220 + i * 46, 40, 0)}px)`,
              }}
            >
              {t}
            </div>
          ))}
        </div>

        <div style={{ marginTop: 40, opacity: ip(f, 420, 460, 0, 1) }}>
          <div style={{ fontFamily: "Amiri", fontSize: 62, color: C.parch, lineHeight: 1.5 }}>
            حصلت في مدينة في نص الصحرا…
          </div>
          <div style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: 40, color: `${C.stone}`, marginTop: 10 }}>
            ومحدش شافها.
          </div>
        </div>
      </div>
    </SceneShell>
  );
};

/* ═══ 3 · مدينة الكتب — دهشة ════════════════════════════════════════════════ */
export const S03City: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <SceneShell dur={735} kind="push" tint="warm">
      <DepthBox x={660} y={540} z={-30} w={940} h={720} ry={6} keepSharp>
        <PhotoCard src="projects/TMB_001/plates/tmb_night.jpg" w={940} h={720} kb={[1.0, 1.1]} grad={0.62} />
      </DepthBox>
      <DepthBox x={560} y={870} z={-160} w={380} h={280} ry={12} delay={40} idx={2}>
        <PhotoCard src="projects/TMB_001/plates/tmb_library.jpg" w={400} h={300} kb={[1.0, 1.12]} grad={0.6} />
      </DepthBox>
      <ShapeField seed={9} camZ={0} amt={0.8} />

      <div
        style={{
          position: "absolute",
          right: 60,
          top: 84,
          width: 620,
          direction: "rtl",
          textAlign: "right",
        }}
      >
        <div style={{ fontFamily: "Amiri", fontWeight: 700, fontSize: 68, color: C.parch, lineHeight: 1.5 }}>
          <div style={{ opacity: ip(f, 6, 38, 0, 1) }}>تمبكتو مكانتش واحة</div>
          <div style={{ opacity: ip(f, 30, 64, 0, 1), color: `${C.parch}b0` }}>عشان القوافل تعدّي.</div>
        </div>

        <div style={{ marginTop: 30, opacity: ip(f, 118, 150, 0, 1) }}>
          <div style={{ fontFamily: "Amiri", fontSize: 96, color: C.gold }}>لأ.</div>
          <div style={{ fontFamily: "Amiri", fontSize: 58, color: C.parch, marginTop: 4 }}>
            كانت محطة. مقصد.
          </div>
        </div>

        <div style={{ marginTop: 34, display: "flex", flexWrap: "wrap", gap: "10px 22px", justifyContent: "flex-end" }}>
          {["طلبة", "علماء", "أسواق", "كتب"].map((t, i) => (
            <div
              key={t}
              style={{
                opacity: ip(f, 380 + i * 22, 410 + i * 22, 0, 1),
                padding: "12px 30px",
                borderRadius: 999,
                border: `1px solid ${C.gold}55`,
                background: `${C.gold}12`,
                fontFamily: "IBM Plex Sans Arabic",
                fontWeight: 700,
                fontSize: 34,
                color: `${C.parch}e0`,
              }}
            >
              {t}
            </div>
          ))}
        </div>

        <div style={{ marginTop: 32, opacity: ip(f, 560, 600, 0, 1) }}>
          <div style={{ fontFamily: "Amiri", fontSize: 74, color: C.gold, textShadow: `0 0 60px ${C.goldDeep}77` }}>
            مدينة الكتب.
          </div>
          <div style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: 34, color: C.stone }}>حرفيًا.</div>
        </div>
      </div>
    </SceneShell>
  );
};

/* ═══ 4 · ١٥٢٦ — احترام ═════════════════════════════════════════════════════
   الميزان الذهبي. الاقتباس يظهر على زجاج.                               */
export const S04Leo: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <SceneShell dur={780} kind="orbit" tint="warm">
      <DepthBox x={1380} y={520} z={-20} w={820} h={880} ry={-6} keepSharp>
        <PhotoCard src="projects/TMB_001/plates/tmb_gold.jpg" w={820} h={880} kb={[1.02, 1.12]} grad={0.6} />
      </DepthBox>
      <ShapeField seed={13} camZ={0} amt={0.7} />

      {/* كارت الاقتباس */}
      <div style={{ position: "absolute", left: 96, top: 200, width: 860, textAlign: "left", direction: "rtl" }}>
        <div style={{ fontFamily: "IBM Plex Sans Arabic", fontWeight: 500, fontSize: 36, color: `${C.gold}dd`, letterSpacing: "0.12em" }}>
          ١٥٢٦
        </div>
        <div style={{ fontFamily: "Amiri", fontWeight: 700, fontSize: 60, color: C.parch, lineHeight: 1.45, marginTop: 12 }}>
          <div style={{ opacity: ip(f, 10, 44, 0, 1) }}>ليو أفريكانوس</div>
          <div style={{ opacity: ip(f, 40, 76, 0, 1), color: `${C.parch}a8`, fontSize: 40 }}>
            قعد فيها. شاف. وكتب.
          </div>
        </div>

        <div
          style={{
            marginTop: 60,
            opacity: ip(f, 250, 300, 0, 1),
            transform: `translateY(${ip(f, 250, 300, 26, 0)}px)`,
            position: "relative",
            padding: "40px 44px",
            borderRadius: 26,
            maxWidth: 780,
          }}
        >
          {/* خلفية زجاجية للاقتباس */}
          <div style={{ position: "absolute", inset: 0 }}>
            <Glass r={26} tint="255,244,222" sheen={0.5} idx={4} />
          </div>
          <div style={{ position: "relative" }}>
            <div style={{ fontFamily: "Amiri", fontWeight: 700, fontSize: 76, color: `${C.gold}66`, lineHeight: 0.6 }}>﴾</div>
            <div style={{ fontFamily: "Amiri", fontSize: 58, color: C.parch, lineHeight: 1.55, marginTop: 14 }}>
              تجارة الكتب
              <br />
              أربح من الدهب
            </div>
            <div style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: 32, color: `${C.gold}d0`, marginTop: 22 }}>
              — ليو أفريكانوس · ١٥٢٦
            </div>
          </div>
        </div>

        <div style={{ marginTop: 40, opacity: ip(f, 600, 650, 0, 1) }}>
          <div style={{ fontFamily: "Amiri", fontSize: 50, color: C.parch }}>تخيل.</div>
          <div style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: 38, color: `${C.stone}` }}>
            الدهب كان أرخص من الورق.
          </div>
        </div>
      </div>
    </SceneShell>
  );
};

/* ═══ 5 · إيه في الكتب — افتتان ═════════════════════════════════════════════ */
export const S05Inside: React.FC = () => {
  const f = useCurrentFrame();
  const kinds = ["فلك", "طب", "شعر", "فقه", "عقود", "رسايل"];
  return (
    <SceneShell dur={585} kind="pan" tint="warm">
      <DepthBox x={1350} y={540} z={-10} w={1000} h={720} keepSharp>
        <PhotoCard src="projects/TMB_001/plates/tmb_close.jpg" w={1000} h={720} kb={[1.0, 1.14]} grad={0.62} />
      </DepthBox>
      <ShapeField seed={17} camZ={0} amt={0.6} />

      <TextRail side="left" top={140} width={620}>
        <div style={{ fontFamily: "Amiri", fontWeight: 700, fontSize: 62, color: C.parch, opacity: ip(f, 6, 40, 0, 1) }}>
          الكتب دي مكانتش ديكور.
        </div>

        <div style={{ marginTop: 40, display: "flex", flexWrap: "wrap", gap: "14px 14px" }}>
          {kinds.map((k, i) => (
            <div
              key={k}
              style={{
                padding: "11px 26px",
                borderRadius: 13,
                border: `1px solid ${C.gold}44`,
                background: `linear-gradient(140deg, ${C.gold}16, ${C.gold}05)`,
                fontFamily: "Amiri",
                fontWeight: 700,
                fontSize: 38,
                color: i === 5 ? C.gold : C.parch,
                opacity: ip(f, 110 + i * 26, 140 + i * 26, 0, 1),
                transform: `translateY(${ip(f, 110 + i * 26, 140 + i * 26, 24, 0)}px)`,
              }}
            >
              {k}
            </div>
          ))}
        </div>

        <div style={{ marginTop: 52, opacity: ip(f, 430, 470, 0, 1) }}>
          <div style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: 40, color: `${C.parch}cc` }}>
            رسايل بين ناس بيحبوا بعض.
          </div>
          <div style={{ marginTop: 26, fontFamily: "IBM Plex Sans Arabic", fontSize: 34, color: `${C.stone}` }}>
            زي ما انت بتكتب بقلمين ألوان.
          </div>
        </div>
      </TextRail>
    </SceneShell>
  );
};

/* ═══ 6 · الجفاف + ٢٠١٢ — توتر بطيء ═════════════════════════════════════════ */
export const S06Drought: React.FC = () => {
  const f = useCurrentFrame();
  const shift = ip(f, 560, 640, 1, 0); // تبديل المزاج
  return (
    <SceneShell dur={1104} kind="push" tint={shift > 0.5 ? "warm" : "cold"}>
      <DepthBox x={760} y={540} z={-20} w={960} h={760} keepSharp>
        <PhotoCard src="projects/TMB_001/plates/tmb_map.jpg" w={960} h={760} kb={[1.0, 1.1]} grad={0.6} />
      </DepthBox>
      <DepthBox x={620} y={880} z={-140} w={380} h={300} ry={10} delay={560} idx={3}>
        <PhotoCard src="projects/TMB_001/plates/tmb_fall.jpg" w={380} h={300} kb={[1.0, 1.1]} grad={0.66} />
      </DepthBox>
      <ShapeField seed={21} camZ={0} amt={0.7} />

      <div style={{ position: "absolute", right: 60, top: 76, width: 620, direction: "rtl", textAlign: "right" }}>
        <div style={{ fontFamily: "Amiri", fontWeight: 700, fontSize: 64, color: C.parch, lineHeight: 1.5 }}>
          <div style={{ opacity: ip(f, 6, 40, 0, 1) }}>وهنا حاجة غريبة، ولها معنى.</div>
          <div style={{ opacity: ip(f, 60, 100, 0, 1), color: `${C.parch}cc` }}>اللي بيقتل أي أثر تاني… الرطوبة.</div>
          <div style={{ opacity: ip(f, 210, 250, 0, 1), color: C.gold }}>كان بعيد عنهم.</div>
        </div>

        <div style={{ marginTop: 40, opacity: ip(f, 300, 340, 0, 1) }}>
          <div style={{ fontFamily: "Amiri", fontSize: 58, color: C.parch }}>الجفاف هو اللي حفظهم.</div>
          <div style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: 34, color: C.stone, marginTop: 8 }}>
            خمس قرون في الرمل. ولسه فيها.
          </div>
        </div>

        {/* التحوّل */}
        <div style={{ marginTop: 44, opacity: ip(f, 560, 600, 0, 1) }}>
          <Rule w={260} delay={560} flip />
          <div style={{ fontFamily: "Amiri", fontSize: 80, color: C.gold, marginTop: 22, textShadow: `0 0 50px ${C.goldDeep}88` }}>
            لغاية ٢٠١٢.
          </div>
          <div style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: 40, color: `${C.parch}c8`, marginTop: 14 }}>
            مجموعات مسلّحة دخلت المدينة.
          </div>
          <div style={{ fontFamily: "Amiri", fontSize: 52, color: C.parch, marginTop: 22 }}>
            كانوا عارفين اللي جاي.
          </div>
          <div style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: 36, color: `${C.stone}`, marginTop: 10 }}>
            اللي عندهم مش ورق. اللي عندهم هو مين هما.
          </div>
        </div>
      </div>
    </SceneShell>
  );
};

/* ═══ 7 · الحريق — حزن غاضب هادي ════════════════════════════════════════════ */
export const S07Fire: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <SceneShell dur={1185} kind="static" tint="deep">
      <DepthBox x={1390} y={540} z={-10} w={920} h={740} keepSharp>
        <PhotoCard src="projects/TMB_001/plates/tmb_smoke.jpg" w={920} h={740} kb={[1.0, 1.06]} grad={0.66} />
      </DepthBox>

      {/* الغرفة الفارغة — الدليل */}
      <div style={{ position: "absolute", inset: 0, opacity: ip(f, 250, 300, 0, 1) * ip(f, 520, 560, 1, 0) }}>
        <DepthBox x={1380} y={540} z={0} w={960} h={760} keepSharp>
          <PhotoCard src="projects/TMB_001/plates/tmb_empty.jpg" w={960} h={760} kb={[1.02, 1.08]} grad={0.5} />
        </DepthBox>
      </div>

      <ShapeField seed={25} camZ={0} amt={0.5} />

      {/* سرد */}
      <TextRail side="left" top={150} width={600}>
        <div style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: 34, color: `${C.gold}dd`, letterSpacing: "0.1em" }}>
          ٢٥ يناير ٢٠١٣ · مكتبة أحمد بابا
        </div>
        <div style={{ fontFamily: "Amiri", fontWeight: 700, fontSize: 64, color: C.parch, lineHeight: 1.4, marginTop: 14 }}>
          <div style={{ opacity: ip(f, 30, 66, 0, 1) }}>كبّوا بنزين.</div>
          <div style={{ opacity: ip(f, 150, 190, 0, 1) }}>وولّعوا.</div>
        </div>
      </TextRail>

      {/* «كانت فرن» */}
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", opacity: ip(f, 560, 600, 0, 1) }}>
        <div
          style={{
            fontFamily: "Amiri",
            fontWeight: 700,
            fontSize: 150,
            color: C.parch,
            textShadow: `0 0 90px ${C.burgundy}cc, 0 8px 50px rgba(0,0,0,.95)`,
          }}
        >
          كانت فرن.
        </div>
      </AbsoluteFill>

      {/* ٤٢٠٣ راحت + «مش رقم» */}
      <TextRail side="left" top={440} width={600}>
        <div style={{ opacity: ip(f, 700, 740, 0, 1) }}>
          <div style={{ fontFamily: "Amiri", fontWeight: 700, fontSize: 170, color: C.gold, lineHeight: 1 }}>
            ٤٢٠٣
          </div>
          <div style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: 46, color: C.parch, marginTop: 6 }}>مخطوطة. راحت.</div>
        </div>
        <div style={{ marginTop: 26, opacity: ip(f, 850, 890, 0, 1) }}>
          <div style={{ fontFamily: "Amiri", fontSize: 56, color: C.parch }}>مش رقم.</div>
          <div style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: 32, color: `${C.stone}` }}>
            ٤٢٠٣ مرة، حد فقد حاجة عمرها ٥٠٠ سنة.
          </div>
        </div>
      </TextRail>
    </SceneShell>
  );
};

/* ═══ 8 · الخطة — إعجاب بابتسامة ════════════════════════════════════════════ */
export const S08Plan: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <SceneShell dur={906} kind="orbit" tint="warm">
      <DepthBox x={1400} y={530} z={-30} w={900} h={840} ry={-10} keepSharp>
        <PhotoCard src="projects/TMB_001/plates/tmb_drums.jpg" w={900} h={840} kb={[1.0, 1.1]} grad={0.6} />
      </DepthBox>
      <DepthBox x={1290} y={870} z={-220} w={380} h={280} ry={20} delay={60} idx={1}>
        <PhotoCard src="projects/TMB_001/plates/tmb_hands.jpg" w={420} h={520} kb={[1.0, 1.1]} grad={0.6} />
      </DepthBox>
      <ShapeField seed={29} camZ={0} amt={0.7} />

      <TextRail side="left" top={90} width={620}>
        <div style={{ fontFamily: "Amiri", fontWeight: 700, fontSize: 62, color: C.parch, lineHeight: 1.5 }}>
          <div style={{ opacity: ip(f, 6, 40, 0, 1) }}>بس الحريق ده،</div>
          <div style={{ opacity: ip(f, 44, 80, 0, 1), color: `${C.parch}c8` }}>حصل بعد ما المدينة كانت خدت قرار.</div>
        </div>

        <div style={{ marginTop: 36, opacity: ip(f, 120, 160, 0, 1) }}>
          <div style={{ fontFamily: "Amiri", fontSize: 76, color: C.gold }}>١٤٠ ألف</div>
          <div style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: 38, color: `${C.parch}d0` }}>مخطوطة. سرًا.</div>
        </div>

        <div style={{ marginTop: 34, display: "flex", gap: 22, flexWrap: "wrap", justifyContent: "flex-end" }}>
          {["شحنة شحنة", "في الليل"].map((t, i) => (
            <div
              key={t}
              style={{
                opacity: ip(f, 240 + i * 40, 270 + i * 40, 0, 1),
                padding: "12px 28px",
                borderRadius: 12,
                border: `1px solid ${C.gold}44`,
                background: `${C.gold}10`,
                fontFamily: "IBM Plex Sans Arabic",
                fontSize: 32,
                color: `${C.parch}d8`,
              }}
            >
              {t}
            </div>
          ))}
        </div>

        <div style={{ marginTop: 40, opacity: ip(f, 470, 510, 0, 1) }}>
          <div style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: 38, color: `${C.parch}b8` }}>
            وفي إيه؟ في صناديق زيت معدنية.
          </div>
          <div style={{ fontFamily: "Amiri", fontSize: 54, color: C.parch, marginTop: 20, lineHeight: 1.5 }}>
            نفس الصندوق اللي كان بيولّع نار،
            <br />
            <span style={{ color: C.gold }}>بقى هو اللي شيّل الكتب.</span>
          </div>
        </div>
      </TextRail>
    </SceneShell>
  );
};

/* ═══ 9 · الرحلة — نَفَس محبوس ══════════════════════════════════════════════ */
export const S09Journey: React.FC = () => {
  const f = useCurrentFrame();
  const legs = [
    { t: "عربيات على الرمل", at: 110 },
    { t: "قوارب على النيجر", at: 290 },
    { t: "شاحنات وقوافل", at: 480 },
  ];
  return (
    <SceneShell dur={846} kind="pan" tint="cold">
      <DepthBox x={1120} y={540} z={-20} w={980} h={760} keepSharp>
        <PhotoCard src="projects/TMB_001/plates/tmb_route.jpg" w={980} h={760} kb={[1.0, 1.14]} grad={0.6} />
      </DepthBox>
      <DepthBox x={1610} y={430} z={-200} w={380} h={540} ry={-30} delay={240} idx={1}>
        <PhotoCard src="projects/TMB_001/plates/tmb_boat.jpg" w={380} h={540} kb={[1.0, 1.1]} grad={0.6} />
      </DepthBox>
      <DepthBox x={1620} y={680} z={-260} w={330} h={440} ry={-32} delay={440} idx={2}>
        <PhotoCard src="projects/TMB_001/plates/tmb_night.jpg" w={330} h={440} kb={[1.0, 1.1]} grad={0.62} />
      </DepthBox>
      <ShapeField seed={33} camZ={0} amt={0.6} />

      <TextRail side="left" top={96} width={580}>
        <div style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: 34, color: `${C.gold}dd`, letterSpacing: "0.1em" }}>
          المسار
        </div>
        <div style={{ fontFamily: "Amiri", fontWeight: 700, fontSize: 112, color: C.gold, lineHeight: 1.1, marginTop: 8, textShadow: `0 0 60px ${C.goldDeep}88` }}>
          ٤٠٠ ميل
        </div>
        <div style={{ fontFamily: "Amiri", fontSize: 54, color: C.parch }}>جنوبًا.</div>

        <div style={{ marginTop: 40, display: "flex", flexDirection: "column", gap: 14 }}>
          {legs.map((l, i) => (
            <div
              key={l.t}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 14,
                opacity: ip(f, l.at, l.at + 40, 0, 1),
                transform: `translateX(${ip(f, l.at, l.at + 40, 30, 0)}px)`,
                direction: "rtl",
              }}
            >
              <div style={{ width: 8, height: 8, borderRadius: "50%", background: C.gold, boxShadow: `0 0 14px ${C.gold}` }} />
              <div style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: 34, color: `${C.parch}cc` }}>{l.t}</div>
            </div>
          ))}
        </div>

        <div style={{ marginTop: 36, opacity: ip(f, 660, 700, 0, 1) }}>
          <div style={{ fontFamily: "Amiri", fontSize: 46, color: C.parch }}>ولو واحدة اتكشفت…</div>
          <div style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: 34, color: C.burgundy, letterSpacing: "0.06em" }}>
            خلاص.
          </div>
        </div>
      </TextRail>
    </SceneShell>
  );
};

/* ═══ 10 · الكشف — ارتياح ═══════════════════════════════════════════════════ */
export const S10Arrival: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <SceneShell dur={300} kind="static" tint="warm">
      <DepthBox x={1400} y={540} z={-10} w={900} h={720} keepSharp>
        <PhotoCard src="projects/TMB_001/plates/tmb_door.jpg" w={900} h={720} kb={[1.0, 1.05]} grad={0.5} />
      </DepthBox>

      <TextRail side="left" top={300} width={620}>
        <div
          style={{
            fontFamily: "Amiri",
            fontWeight: 700,
            fontSize: 168,
            color: C.parch,
            opacity: ip(f, 15, 45, 0, 1),
            transform: `scale(${ip(f, 15, 55, 0.94, 1)})`,
            transformOrigin: "right center",
            textShadow: `0 0 90px ${C.goldDeep}77`,
          }}
        >
          ووصلت.
        </div>
      </TextRail>
    </SceneShell>
  );
};

/* ═══ 11 · الأرقام الكبيرة ══════════════════════════════════════════════════ */
export const S11Numbers: React.FC = () => {
  const f = useCurrentFrame();
  const a = ip(f, 10, 60, 0, 1);
  const b = ip(f, 300, 340, 0, 1);
  return (
    <SceneShell dur={750} kind="push" tint="warm">
      <ShapeField seed={37} camZ={0} amt={0.9} />

      {/* ٣٥٠ ألف */}
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", opacity: a * ip(f, 280, 320, 1, 0) }}>
        <div style={{ textAlign: "center" }}>
          <div
            style={{
              fontFamily: "Amiri",
              fontWeight: 700,
              fontSize: 300,
              lineHeight: 1,
              color: C.gold,
              textShadow: `0 0 130px ${C.goldDeep}aa`,
            }}
          >
            ٣٥٠
          </div>
          <div style={{ fontFamily: "Amiri", fontSize: 90, color: C.parch, marginTop: -20 }}>ألف مخطوطة</div>
          <div style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: 44, color: `${C.parch}a8`, marginTop: 16 }}>
            نجت.
          </div>
        </div>
      </AbsoluteFill>

      {/* ١٪ */}
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", opacity: b }}>
        <div style={{ textAlign: "center" }}>
          <div
            style={{
              fontFamily: "Amiri",
              fontWeight: 700,
              fontSize: 340,
              lineHeight: 1,
              color: C.parch,
              textShadow: `0 0 120px ${C.burgundy}bb`,
            }}
          >
            ١٪
          </div>
          <div style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: 46, color: `${C.stone}` }}>الخسارة.</div>
        </div>
      </AbsoluteFill>
    </SceneShell>
  );
};

/* ═══ 12 · الرأي الشخصي ═════════════════════════════════════════════════════ */
export const S12Opinion: React.FC = () => {
  const f = useCurrentFrame();
  const lines = [
    { t: "اللي عملته الناس دي،", at: 10, s: 62 },
    { t: "مش بطولة أسطورية.", at: 60, s: 62 },
    { t: "ولا حكاية أبطال خارقين.", at: 110, s: 54 },
    { t: "هو أبسط من كده بكتير.", at: 200, s: 66 },
  ];
  return (
    <SceneShell dur={750} kind="drift" tint="deep">
      <DepthBox x={1500} y={560} z={-260} w={620} h={760} ry={-24} delay={20} idx={1}>
        <PhotoCard src="projects/TMB_001/plates/tmb_hands.jpg" w={620} h={760} kb={[1.0, 1.12]} grad={0.6} />
      </DepthBox>
      <ShapeField seed={41} camZ={0} amt={0.7} />

      <div style={{ position: "absolute", left: 76, top: 120, width: 660, textAlign: "right", direction: "rtl" }}>
        {lines.map((l) => (
          <div
            key={l.t}
            style={{
              fontFamily: "Amiri",
              fontWeight: 700,
              fontSize: l.s,
              color: C.parch,
              lineHeight: 1.55,
              opacity: ip(f, l.at, l.at + 34, 0, 1),
              transform: `translateY(${ip(f, l.at, l.at + 34, 26, 0)}px)`,
            }}
          >
            {l.t}
          </div>
        ))}

        <div style={{ marginTop: 36, opacity: ip(f, 380, 420, 0, 1) }}>
          <Rule w={340} delay={380} flip />
          <div style={{ fontFamily: "Amiri", fontSize: 88, color: C.gold, marginTop: 22, lineHeight: 1.5, textShadow: `0 0 70px ${C.goldDeep}88` }}>
            حد لقى حاجة مهمة،
            <br />
            ومكانش عايز يسيبها تروح.
          </div>
          <div style={{ fontFamily: "Amiri", fontSize: 60, color: `${C.parch}d0`, marginTop: 10 }}>وخلاص.</div>
        </div>

        <div style={{ marginTop: 34, opacity: ip(f, 560, 600, 0, 1) }}>
          <div style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: 38, color: `${C.parch}b0` }}>
            ويمكن ده بالظبط اللي بيخليه أعظم،
          </div>
          <div style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: 38, color: `${C.stone}`, marginTop: 6 }}>
            عشان أي حد فينا… يقدر يعمله.
          </div>
        </div>
      </div>
    </SceneShell>
  );
};

/* ═══ 13 · الخاتمة + التوقيع ════════════════════════════════════════════════ */
export const S13Signoff: React.FC = () => {
  const f = useCurrentFrame();
  const sigIn = ip(f, 620, 680, 0, 1);
  return (
    <AbsoluteFill style={{ backgroundColor: C.ink }}>
      <SceneShell dur={1110} kind="push" tint="warm">
        <DepthBox x={1430} y={520} z={-10} w={860} h={800} keepSharp>
          <PhotoCard src="projects/TMB_001/plates/tmb_outside.jpg" w={860} h={800} kb={[1.04, 1.0]} grad={0.72} />
        </DepthBox>
        <ShapeField seed={45} camZ={0} amt={0.8} />
      </SceneShell>

      <div style={{ position: "absolute", left: 80, top: 120, width: 620, textAlign: "left", direction: "rtl" }}>
        <div style={{ fontFamily: "Amiri", fontWeight: 700, fontSize: 72, color: C.parch, lineHeight: 1.5 }}>
          <div style={{ opacity: ip(f, 10, 50, 0, 1) }}>بس السؤال اللي بيفضل:</div>
          <div style={{ opacity: ip(f, 120, 160, 0, 1), color: `${C.parch}c0`, fontSize: 54 }}>
            فيه كتب محتاجة نفس القرار.
          </div>
        </div>

        <div style={{ marginTop: 44, opacity: ip(f, 300, 340, 0, 1) }}>
          <div style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: 38, color: `${C.stone}` }}>
            والسؤال مش: هل نقدر ننقذها؟
          </div>
          <div style={{ fontFamily: "Amiri", fontSize: 96, color: C.gold, marginTop: 16, textShadow: `0 0 80px ${C.goldDeep}88` }}>
            مين هيبدأ؟
          </div>
        </div>
      </div>

      {/* التوقيع */}
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          opacity: sigIn,
          transform: `scale(${ip(f, 620, 700, 0.94, 1)}`,
        }}
      >
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: "radial-gradient(ellipse 60% 50% at 50% 50%, rgba(6,5,5,.94) 0%, rgba(6,5,5,.98) 100%)",
          }}
        />
        <div style={{ textAlign: "center", position: "relative" }}>
          <div style={{ fontFamily: "Amiri", fontWeight: 700, fontSize: 130, color: C.parch, lineHeight: 1.2 }}>
            و دي رِواق .. سلاام
          </div>
          <div
            style={{
              marginTop: 30,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 16,
              textAlign: "left", direction: "rtl",
            }}
          >
            <div style={{ width: 3, height: 44, background: C.gold, boxShadow: `0 0 24px ${C.gold}` }} />
            <div style={{ fontFamily: "IBM Plex Sans Arabic", fontSize: 36, color: `${C.gold}dd`, letterSpacing: "0.18em" }}>
              رِواق
            </div>
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ═══ سجل المشاهد ═══════════════════════════════════════════════════════════ */
export const SCENES: Array<{ i: number; Comp: React.FC }> = [
  { i: 1, Comp: S01Hook },
  { i: 2, Comp: S02Promise },
  { i: 3, Comp: S03City },
  { i: 4, Comp: S04Leo },
  { i: 5, Comp: S05Inside },
  { i: 6, Comp: S06Drought },
  { i: 7, Comp: S07Fire },
  { i: 8, Comp: S08Plan },
  { i: 9, Comp: S09Journey },
  { i: 10, Comp: S10Arrival },
  { i: 11, Comp: S11Numbers },
  { i: 12, Comp: S12Opinion },
  { i: 13, Comp: S13Signoff },
];
