#!/usr/bin/env python3
"""build_meta.py — يبني episode_meta.json (طويل + شورت) من timeline*.json وخطة المشاهد.

كل الأزمنة مشتقة من توقيتات الكلمات الفعلية في التعليق (timeline.json → words)،
فتظهر الكلمات المفتاحية والتواريخ لحظة نطقها.

الاستخدام:  python3 episode/WHAT_IF_BAGHDAD_NEVER_FELL/tools/build_meta.py
المخرجات:
  data/projects/WHAT_IF_BAGHDAD_NEVER_FELL/episode_meta.json        (16x9)
  data/projects/WHAT_IF_BAGHDAD_NEVER_FELL/episode_meta_short.json  (9x16)
  episode/WHAT_IF_BAGHDAD_NEVER_FELL/timestamps.json
"""
import json, os, re

EP = "WHAT_IF_BAGHDAD_NEVER_FELL"
HERE = os.path.dirname(os.path.abspath(__file__))
EPDIR = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(EPDIR, "..", ".."))
OUT = os.path.join(ROOT, "data", "projects", EP)
IMG = f"projects/{EP}/img/"
MIX = f"projects/{EP}/mix/"

TL = json.load(open(os.path.join(EPDIR, "timeline.json"), encoding="utf-8"))
TS = json.load(open(os.path.join(EPDIR, "timeline_short.json"), encoding="utf-8"))
SC = json.load(open(os.path.join(EPDIR, "script_scenes.json"), encoding="utf-8"))

TASHKEEL = re.compile(r"[\u064B-\u0652\u0670\u0640]")
PUNCT = re.compile(r"[^\w]", re.UNICODE)


def norm(w):
    return PUNCT.sub("", TASHKEEL.sub("", w)).replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي")


SCN = {s["id"]: s for s in TL["scenes"]}
FICTION_IDS = {s["id"] for s in SC["scenes"] if s.get("fiction")}


def t_in(sid):
    return SCN[sid]["t_in"]


def t_out(sid):
    return SCN[sid]["t_out"]


def W(sid, needle, n=0, end=False):
    """زمن الكلمة رقم n (من 0) داخل المشهد sid التي تحتوي needle."""
    nd = norm(needle)
    hits = [w for w in TL["words"] if w["scene"] == sid and nd in norm(w["w"])]
    if len(hits) <= n:
        raise SystemExit(f"word not found: scene {sid} '{needle}' #{n}")
    return round(hits[n]["t1" if end else "t0"], 3)


def WS(needle, n=0, end=False):
    nd = norm(needle)
    hits = [w for w in TS["words"] if nd in norm(w["w"])]
    if len(hits) <= n:
        raise SystemExit(f"short word not found: '{needle}' #{n}")
    return round(hits[n]["t1" if end else "t0"], 3)


def vis(src, a, b, kind="ai", **kw):
    d = {"src": IMG + src, "t_in": round(a, 3), "t_out": round(b, 3), "kind": kind}
    d.update(kw)
    return d


def ov(typ, a, b, **kw):
    d = {"type": typ, "t_in": round(a, 3), "t_out": round(b, 3)}
    d.update(kw)
    return d


def kw_items(base, pairs):
    return [{"text": t, "at": round(max(0.0, at - base), 3), "tone": tone} for t, at, tone in pairs]


CR_SIEGE = "جامع التواريخ لرشيد الدين · نسخة نحو 1430 · BnF · ملكية عامة"
CR_HULAGU = "هولاكو · منمنمة من جامع التواريخ · ملكية عامة"
CR_GHAZAN = "غازان وأولجايتو · جامع التواريخ · نحو 1430 · ملكية عامة"

# إحداثيات تقريبية [lon, lat]
G = {
    "baghdad": (44.36, 33.31), "cairo": (31.24, 30.04), "delhi": (77.2, 28.6), "karakorum": (102.8, 47.2),
    "alamut": (50.59, 36.44), "hamadan": (48.5, 34.8), "anbar": (43.6, 33.4), "hilla": (44.42, 32.47),
    "kufa": (44.4, 32.03), "basra": (47.8, 30.5), "maragha": (46.24, 37.39), "tabriz": (46.3, 38.08),
    "aleppo": (37.16, 36.2), "damascus": (36.29, 33.51), "aynjalut": (35.36, 32.55), "homs": (36.72, 34.73),
    "sarai": (47.0, 46.6), "derbent": (48.29, 42.06), "samarqand": (66.97, 39.65),
}


def P(k):
    return list(G[k])


def build_long():
    V, O, TR = [], [], []

    # 01 HOOK
    s = "01"; a, b = t_in(s), t_out(s)
    cut = W(s, "لكن")
    V.append(vis("pd01_bagdad1258_siege.jpg", a, cut, "archival", credit=CR_SIEGE, kb={"from": 1.0, "to": 1.06, "fx0": 0.5, "fy0": 0.55, "fx1": 0.42, "fy1": 0.4}))
    V.append(vis("img01_gate_night.jpg", cut, b, kb={"fx0": 0.55, "fy0": 0.5}))
    O.append(ov("keyword", a + 0.3, W(s, "خليفة") - 0.1, items=[{"text": "10 فبراير 1258", "tone": "gold"}], position="lower_right", size=58))
    O.append(ov("scene_title", W(s, "ماذا"), b, title="ماذا لو؟", kicker="خرج قبلها بعام", size=120))

    # 02 PROMISE
    s = "02"; a, b = t_in(s), t_out(s)
    O.append(ov("keyword", a + 0.2, b - 0.1, layout="row", size=64, items=kw_items(a + 0.2, [
        ("حقيقة", W(s, "تاريخ", 0), "gold"), ("خلاف", W(s, "تقوله"), "stone"), ("خيال", W(s, "خيال", 0), "burgundy")])))
    O.append(ov("scene_title", a + 0.2, W(s, "خيال", 0) - 0.05, title="سلسلة «ماذا لو؟»", position="upper", size=64, tone="gold"))
    TR.append({"t": b, "type": "fade_black_200ms"})

    # 03 BACKGROUND — خريطة الشرعية
    s = "03"; a, b = t_in(s), t_out(s)
    O.append(ov("map", a, b, bbox=[28, 22, 80, 42], rivers=False, title="الشرعية أكبر من الحدود",
                points=[{"label": "بغداد", "lon": G["baghdad"][0], "lat": G["baghdad"][1], "big": True, "at": 0.3, "anchor": "t"},
                        {"label": "القاهرة", "lon": G["cairo"][0], "lat": G["cairo"][1], "at": W(s, "مصر") - a, "anchor": "b"},
                        {"label": "دلهي", "lon": G["delhi"][0], "lat": G["delhi"][1], "at": W(s, "الهند") - a, "anchor": "b"}],
                lines=[{"path": [P("baghdad"), P("cairo")], "tone": "gold", "at": W(s, "مصر") - a, "dur": 1.4, "width": 2},
                       {"path": [P("baghdad"), P("delhi")], "tone": "gold", "at": W(s, "الهند") - a, "dur": 1.8, "width": 2}]))
    O.append(ov("timeline", W(s, "السياسية"), b, **{"from": 1240, "to": 1262}, cursor=[{"t": 0, "year": 1240}, {"t": 1.2, "year": 1250}],
                marks=[{"year": 1250, "label": "منتصف القرن", "tone": "gold"}]))

    # 04
    s = "04"; a, b = t_in(s), t_out(s)
    V.append(vis("img03_library_candle.jpg", a, b, kb={"fx0": 0.35, "fy0": 0.5, "fx1": 0.5, "fy1": 0.5}))
    O.append(ov("keyword", W(s, "عام"), W(s, "ربما") + 0.3, items=[{"text": "1245", "tone": "gold"}, {"text": "بغداد تصدّ المغول", "tone": "parchment", "at": 0.5}], position="lower_right", layout="stack"))
    O.append(ov("keyword", W(s, "مشروع") - 0.2, b - 0.1, items=[{"text": "مشروعُ إمبراطورية", "tone": "gold"}], chip=False, font="headline", size=88))

    # 05 — قوريلتاي، الخريطة ثم الفرسان
    s = "05"; a, b = t_in(s), t_out(s)
    mid = W(s, "المهمة")
    O.append(ov("map", a, mid, bbox=[38, 26, 108, 50], rivers=False, title="1251 · قُورِيلْتَاي",
                points=[{"label": "قراقورم", "lon": G["karakorum"][0], "lat": G["karakorum"][1], "big": True, "at": 0.3, "anchor": "t"},
                        {"label": "سمرقند", "lon": G["samarqand"][0], "lat": G["samarqand"][1], "at": W(s, "هولاكو") - a + 0.8, "anchor": "t", "tone": "stone"},
                        {"label": "إيران", "lon": G["hamadan"][0], "lat": G["hamadan"][1], "at": W(s, "الغرب") - a + 0.6, "anchor": "t"},
                        {"label": "بغداد", "lon": G["baghdad"][0], "lat": G["baghdad"][1], "at": W(s, "الغرب") - a + 1.0, "anchor": "b"}],
                lines=[{"path": [P("karakorum"), [88, 44], P("samarqand"), P("hamadan")], "tone": "gold", "at": W(s, "الغرب") - a, "dur": 2.4, "arrow": True}]))
    O.append(ov("lower_third", W(s, "مونكو"), W(s, "مونكو") + 4.2, name="مُونْكُو", role="الخان الأعظم (1251–1259)"))
    O.append(ov("keyword", W(s, "رجلان") - 0.1, mid - 0.2, items=[{"text": "2 من كل 10", "tone": "gold", "sub": "من رجال جيوش المغول"}], position="upper_right", size=64))
    V.append(vis("img04_mongol_cavalry.jpg", mid, b, kb={"fx0": 0.6, "fy0": 0.5, "fx1": 0.45, "fy1": 0.5}))
    O.append(ov("keyword", mid, W(s, "ينقل") - 0.2, layout="stack", position="lower_right", size=44,
                items=kw_items(mid, [("سحق قلاع الإسماعيلية", W(s, "سحق"), "parchment"), ("ثم إخضاع الخليفة", W(s, "اخضاع"), "gold")])))
    O.append(ov("quote", W(s, "ينقل"), W(s, "لكن", 0) - 0.1, text="«إن خضع الخليفة… فلا يُمَسّ»", source="بحسب رشيد الدين", scrim=True))
    O.append(ov("keyword", W(s, "يختلفون"), b - 0.1, items=[{"text": "أمرٌ بإسقاط الخلافة؟", "tone": "parchment"}, {"text": "أم تجاوزٌ للأوامر؟", "tone": "stone", "at": W(s, "تجاوز") - W(s, "يختلفون")}], layout="stack", size=50, scrim=True))

    # 06 — ألموت ثم العرش
    s = "06"; a, b = t_in(s), t_out(s)
    c = W(s, "بقي")
    V.append(vis("img05_alamut.jpg", a, c, kb={"from": 1.0, "to": 1.06, "fx0": 0.5, "fy0": 0.4}))
    V.append(vis("img06_throne_empty.jpg", c, b, kb={"fx0": 0.5, "fy0": 0.55}))
    O.append(ov("keyword", W(s, "التاسع"), c - 0.2, items=[{"text": "19 نوفمبر 1256", "tone": "gold"}, {"text": "سقوط ألَمُوت", "tone": "parchment", "at": W(s, "سقطت") - W(s, "التاسع")}], position="lower_right", layout="stack"))
    O.append(ov("keyword", W(s, "قرار"), b - 0.1, items=[{"text": "قرارٌ في يد الخليفة", "tone": "gold"}], chip=False, font="headline", size=80, position="bottom"))

    # 07 — الرسالة
    s = "07"; a, b = t_in(s), t_out(s)
    V.append(vis("img07_sealed_letter.jpg", a, b, kb={"fx0": 0.45, "fy0": 0.5, "fx1": 0.55, "fy1": 0.45}))
    O.append(ov("lower_third", a + 0.3, a + 5.5, name="المُسْتَعْصِم بالله", role="آخر خلفاء بني العباس في بغداد"))
    O.append(ov("keyword", W(s, "الوزير"), W(s, "بدلا") - 0.1, layout="row", size=40, position="upper_right",
                items=kw_items(W(s, "الوزير"), [("الوزير", W(s, "الوزير"), "parchment"), ("سليمان شاه", W(s, "سليمان"), "parchment"), ("الدَّوَادَار", W(s, "الدوادار"), "parchment")])))
    O.append(ov("keyword", W(s, "عرضا"), W(s, "فجاءه") - 0.1, items=[{"text": "عرضٌ بجزيةٍ سنوية", "tone": "gold"}], position="lower_right"))
    O.append(ov("quote", W(s, "فجاءه"), b, text="«كيف نعود… دون أن نرى الخليفة؟»", source="رشيد الدين", scrim=True))

    # 08 — المجلس
    s = "08"; a, b = t_in(s), t_out(s)
    V.append(vis("img08_council_shadows.jpg", a, b, kb={"fx0": 0.5, "fy0": 0.5}))
    O.append(ov("keyword", W(s, "خيانة") - 0.3, W(s, "نعرفه") - 0.2, items=[{"text": "«خيانة» ابن العَلْقَمِي؟", "tone": "parchment"}, {"text": "محلّ خلاف", "tone": "burgundy", "at": W(s, "محل") - W(s, "خيانة") + 0.3}], layout="stack", size=54, scrim=True))
    O.append(ov("keyword", W(s, "نعرفه"), b - 0.1, items=[{"text": "لم يخضع… ولم يستعد", "tone": "gold"}], position="bottom", chip=False, font="headline", size=76))

    # 09 — الأنبار والسدود
    s = "09"; a, b = t_in(s), t_out(s)
    c = W(s, "صباح")
    O.append(ov("map", a, c, bbox=[42.6, 32.3, 45.6, 34.2], rivers=True, title="الأنبار · 16–17 يناير 1258",
                points=[{"label": "بغداد", "lon": G["baghdad"][0], "lat": G["baghdad"][1], "big": True, "at": 0.2, "anchor": "r"},
                        {"label": "الأنبار", "lon": G["anbar"][0], "lat": G["anbar"][1], "at": W(s, "الانبار") - a, "anchor": "t"}],
                lines=[{"path": [[44.9, 33.75], [44.2, 33.55], [43.85, 33.45]], "tone": "burgundy", "at": W(s, "يعبر") - a, "dur": 1.6, "arrow": True}],
                water={"lon": 43.75, "lat": 33.3, "r": 0.55, "at": W(s, "يفتح") - a, "dur": 2.0}))
    V.append(vis("img09_flood_camp.jpg", c, b, kb={"fx0": 0.5, "fy0": 0.55}))
    O.append(ov("stat", W(s, "يقتل"), b, number="~12,000", label="قتيل · بحسب رشيد الدين", scrim=True))

    # 10 — الحصار (قطع إيقاعي على المنمنمة)
    s = "10"; a, b = t_in(s), t_out(s)
    crops = [(0.5, 0.5, 0.45, 0.45), (0.2, 0.8, 0.3, 0.75), (0.75, 0.3, 0.7, 0.25), (0.5, 0.85, 0.55, 0.8)]
    n = len(crops); step = (b - a) / n
    for i, (x0, y0, x1, y1) in enumerate(crops):
        V.append(vis("pd01_bagdad1258_siege.jpg", a + i * step, a + (i + 1) * step, "archival", credit=CR_SIEGE,
                     kb={"from": 1.25 if i else 1.0, "to": 1.32 if i else 1.06, "fx0": x0, "fy0": y0, "fx1": x1, "fy1": y1}))
    O.append(ov("keyword", W(s, "التاسع"), W(s, "التاسع") + 4.5, items=[{"text": "29 يناير 1258", "tone": "gold"}, {"text": "بدء الحصار", "tone": "parchment", "at": 0.6}], position="lower_right", layout="stack"))

    # 11 — النهر ثم الطوسي
    s = "11"; a, b = t_in(s), t_out(s)
    c = W(s, "وعند")
    V.append(vis("img10_river_night.jpg", a, c, kb={"fx0": 0.5, "fy0": 0.55}))
    V.append(vis("img02_baghdad_dusk.jpg", c, b, tint="dark", kb={"fx0": 0.55, "fy0": 0.45, "fx1": 0.6, "fy1": 0.5}))
    O.append(ov("lower_third", W(s, "نصير"), W(s, "نصير") + 5.0, name="نَصِير الدِّين الطُّوسِي", role="فلكي ومستشار لهولاكو"))
    O.append(ov("keyword", W(s, "السابع"), b - 0.1, items=kw_items(W(s, "السابع"), [("7 فبراير: خروج الأعيان", W(s, "السابع"), "parchment"), ("8 فبراير: مقتل الدوادار", W(s, "الثامن"), "gold")]), layout="stack", position="upper_right", size=42))

    # 12 — الاستسلام
    s = "12"; a, b = t_in(s), t_out(s)
    c = W(s, "انتهت")
    V.append(vis("img01_gate_night.jpg", a, c, tint="dark", kb={"from": 1.06, "to": 1.0, "fx0": 0.55, "fy0": 0.5}))
    O.append(ov("keyword", a + 0.2, c - 0.2, layout="stack", position="upper_right", size=44,
                items=kw_items(a + 0.2, [("10 فبراير: الاستسلام", W(s, "العاشر"), "parchment"), ("13 فبراير: النهب", W(s, "الثالث"), "parchment"), ("مقتل المستعصم", W(s, "قتل"), "gold")])))
    O.append(ov("scene_title", c, b, title="750 – 1258", kicker="نهاية الخلافة العباسية في بغداد", size=110, tone="gold"))
    TR.append({"t": b, "type": "fade_black_200ms"})

    # 13 — الأرقام
    s = "13"; a, b = t_in(s), t_out(s)
    c = W(s, "وصورة")
    O.append(ov("bars", a, c, title="كم قُتل في بغداد؟", note="الأرقام مختلف عليها", noteAt=W(s, "وصاف") - a + 2.5,
                items=[{"label": "ابن العبري", "value": 50, "display": "عشرات الآلاف", "at": W(s, "العبري") - a},
                       {"label": "مصدر صيني", "value": 100, "display": "100 ألف", "at": W(s, "صيني") - a},
                       {"label": "هولاكو", "value": 200, "display": "200 ألف", "at": W(s, "هولاكو") - a},
                       {"label": "وصّاف", "value": 800, "display": "800 ألف", "at": W(s, "وصاف") - a}]))
    V.append(vis("img10_river_night.jpg", c, b, tint="dark", kb={"fx0": 0.4, "fy0": 0.6}))
    O.append(ov("keyword", W(s, "ليست"), b - 0.1, items=[{"text": "صورة أدبية… لا سجلّ موثق", "tone": "gold"}], position="bottom", size=50))

    # 14 — نقطة التحوّل
    s = "14"; a, b = t_in(s), t_out(s)
    O.append(ov("timeline", a, b, position="center", **{"from": 1255, "to": 1262},
                cursor=[{"t": 0, "year": 1258}, {"t": W(s, "نوفمبر") - a, "year": 1258}, {"t": W(s, "نوفمبر") - a + 1.4, "year": 1257.85}],
                marks=[{"year": 1258, "label": "سقوط بغداد", "tone": "stone"}],
                branch={"year": 1257.85, "at": W(s, "قبل") - a, "alt": [{"t": W(s, "قبل") - a, "year": 1257.85}, {"t": b - a, "year": 1258.6}], "label": "الخليفة يقبل"}))
    O.append(ov("scene_title", W(s, "سنفترض"), b, title="من هنا يبدأ الخيال التاريخي", position="upper", size=70, tone="burgundy", kicker="افتراض"))

    # 15
    s = "15"; a, b = t_in(s), t_out(s)
    c = W(s, "عالمنا")
    O.append(ov("map", a, c, bbox=[42.4, 29.8, 48.6, 34.4], rivers=True, title="خضعت… فنجت",
                points=[{"label": "بغداد", "lon": G["baghdad"][0], "lat": G["baghdad"][1], "big": True, "at": 0.2, "anchor": "r", "tone": "burgundy"},
                        {"label": "الحِلّة", "lon": G["hilla"][0], "lat": G["hilla"][1], "at": W(s, "الحلة") - a, "anchor": "l"},
                        {"label": "الكوفة", "lon": G["kufa"][0], "lat": G["kufa"][1], "at": W(s, "والكوفة") - a, "anchor": "l"},
                        {"label": "البصرة", "lon": G["basra"][0], "lat": G["basra"][1], "at": W(s, "والبصرة") - a, "anchor": "l"}]))
    O.append(ov("keyword", W(s, "الحلة"), c - 0.1, items=[{"text": "حقيقة تاريخية", "tone": "gold"}], position="lower_right", size=36))
    V.append(vis("img02_baghdad_dusk.jpg", c, b, kb={"fx0": 0.5, "fy0": 0.5, "fx1": 0.45, "fy1": 0.42}, fade_in=True))
    O.append(ov("keyword", W(s, "لا", 0), b - 0.1, layout="stack", position="upper_right", size=44,
                items=kw_items(W(s, "لا", 0), [("لا حصار", W(s, "حصار"), "parchment"), ("لا سدود تُفتح", W(s, "سدود"), "parchment"), ("17 يناير… يومٌ عادي", W(s, "يمر"), "gold")])))

    # 16
    s = "16"; a, b = t_in(s), t_out(s)
    O.append(ov("map", a, b, bbox=[34, 30, 52, 41], rivers=True, title="لا عجلة نحو الشام",
                points=[{"label": "بغداد", "lon": G["baghdad"][0], "lat": G["baghdad"][1], "at": 0.2, "anchor": "b", "tone": "burgundy"},
                        {"label": "معسكر أذربيجان", "lon": G["tabriz"][0], "lat": G["tabriz"][1], "big": True, "at": W(s, "اذربيجان") - a, "anchor": "t"},
                        {"label": "الشام", "lon": G["aleppo"][0], "lat": G["aleppo"][1], "at": W(s, "الشام") - a, "anchor": "t", "tone": "stone"}],
                lines=[{"path": [P("tabriz"), [42, 37.8], P("aleppo")], "tone": "stone", "at": W(s, "الشام") - a, "dur": 1.5, "dashed": True}]))
    O.append(ov("timeline", W(s, "تاريخنا"), b, **{"from": 1257, "to": 1261}, cursor=[{"t": 0, "year": 1258}, {"t": 2.5, "year": 1259.8}],
                marks=[{"year": 1259.8, "label": "حتى أواخر 1259 (حقيقة)", "tone": "gold"}]))

    # 17
    s = "17"; a, b = t_in(s), t_out(s)
    c = W(s, "وتخيل")
    V.append(vis("img06_throne_empty.jpg", a, c, tint="burgundy", kb={"fx0": 0.5, "fy0": 0.55}))
    O.append(ov("keyword", W(s, "تنجو"), W(s, "اما") - 0.1, layout="row", position="upper_right", size=42,
                items=kw_items(W(s, "تنجو"), [("المدينة", W(s, "المدينة"), "parchment"), ("أهلها", W(s, "اهلها"), "parchment"), ("مدارسها ومكتباتها", W(s, "مدارسها"), "parchment")])))
    O.append(ov("keyword", W(s, "يمنح") - 0.6, c - 0.1, items=[{"text": "النتيجة 1", "tone": "burgundy"}, {"text": "شرعية بلا قرار", "tone": "gold", "at": 0.4}], layout="stack", size=64, scrim=True))
    V.append(vis("img03_library_candle.jpg", c, b, kb={"fx0": 0.6, "fy0": 0.5, "fx1": 0.5, "fy1": 0.5}))

    # 18 — موت مونكو: حدث مشترك
    s = "18"; a, b = t_in(s), t_out(s)
    c = W(s, "وفي")
    O.append(ov("timeline", a, c, position="center", **{"from": 1257, "to": 1261},
                cursor=[{"t": 0, "year": 1258}, {"t": W(s, "الحادي") - a + 1.5, "year": 1259.6}],
                branch={"year": 1257.85, "at": 0, "alt": [{"t": 0, "year": 1258.6}, {"t": W(s, "الحادي") - a + 1.5, "year": 1259.6}]},
                merge={"year": 1259.6, "at": W(s, "الحادي") - a + 1.2, "label": "11 أغسطس 1259 · حقيقة في العالمين"},
                marks=[{"year": 1259.6, "label": "موت مونكو", "tone": "gold"}]))
    O.append(ov("map", c, b, bbox=[33, 30, 50, 40], rivers=True, title="ربيع 1260 · الانسحاب",
                points=[{"label": "الشام", "lon": G["aleppo"][0], "lat": G["aleppo"][1], "at": 0.2, "anchor": "t"},
                        {"label": "أذربيجان", "lon": G["tabriz"][0], "lat": G["tabriz"][1], "at": 0.4, "anchor": "t", "big": True}],
                lines=[{"path": [P("aleppo"), [41, 37.6], P("tabriz")], "tone": "gold", "at": W(s, "يسحب") - c, "dur": 1.6, "arrow": True}]))

    # 19 — عين جالوت
    s = "19"; a, b = t_in(s), t_out(s)
    c = W(s, "هذه")
    V.append(vis("img04_mongol_cavalry.jpg", a, c, kb={"fx0": 0.4, "fy0": 0.5, "fx1": 0.55, "fy1": 0.5}))
    O.append(ov("keyword", W(s, "الثالث"), c - 0.1, items=[{"text": "3 سبتمبر 1260", "tone": "gold"}, {"text": "عين جالوت (حقيقة)", "tone": "parchment", "at": W(s, "عين") - W(s, "الثالث")}], layout="stack", position="lower_right"))
    O.append(ov("map", c, b, bbox=[33, 30, 40, 36.5], rivers=False, title="في العالمين",
                points=[{"label": "عين جالوت", "lon": G["aynjalut"][0], "lat": G["aynjalut"][1], "big": True, "at": 0.2, "anchor": "r"},
                        {"label": "دمشق", "lon": G["damascus"][0], "lat": G["damascus"][1], "at": 0.6, "anchor": "r", "tone": "stone"},
                        {"label": "حمص · 11 ديسمبر 1260", "lon": G["homs"][0], "lat": G["homs"][1], "at": W(s, "حمص") - c, "anchor": "r"}]))
    O.append(ov("keyword", W(s, "الارجح"), W(s, "وبعدها") - 0.1, items=[{"text": "على الأرجح (تقدير)", "tone": "burgundy"}], position="lower_right", size=44))

    # 20 — شاشة منقسمة
    s = "20"; a, b = t_in(s), t_out(s)
    V.append(vis("img02_baghdad_dusk.jpg", a, W(s, "اما") , tint="dark", kb={"fx0": 0.5, "fy0": 0.5}))
    O.append(ov("keyword", W(s, "بيبرس"), W(s, "اما") - 0.1, items=[{"text": "1261 · خليفة القاهرة", "tone": "gold", "sub": "بيبرس ينصّب أميرًا عباسيًا (حقيقة)"}], position="center", size=58, scrim=True))
    O.append(ov("split", W(s, "اما"), b, openAt=0,
                right={"title": "خليفة القاهرة", "sub": "رمزٌ يمنح المماليك الشرعية", "tag": "الواقع · 1261", "world": "real", "src": IMG + "img08_council_shadows.jpg"},
                left={"title": "خليفة تابع في بغداد", "sub": "تحت راية المغول", "tag": "الخيال", "world": "fiction", "src": IMG + "img06_throne_empty.jpg", "at": 1.0}))

    # 21 — الفرات خط شرعية
    s = "21"; a, b = t_in(s), t_out(s)
    O.append(ov("map", a, b, bbox=[29, 28, 49, 38.5], rivers=True, title="خليفتان؟",
                points=[{"label": "بغداد · تابع للإيلخانات", "lon": G["baghdad"][0], "lat": G["baghdad"][1], "big": True, "at": 0.3, "anchor": "b", "tone": "burgundy"},
                        {"label": "القاهرة · يحميه المماليك", "lon": G["cairo"][0], "lat": G["cairo"][1], "big": True, "at": W(s, "القاهرة") - a, "anchor": "b"}],
                lines=[{"path": [[38.4, 37.0], [38.9, 36.2], [39.6, 35.8], [40.5, 35.0], [41.4, 34.4], [42.4, 34.1], [43.4, 33.45]], "tone": "burgundy", "at": W(s, "الفرات") - a, "dur": 2.0, "width": 6}]))
    O.append(ov("keyword", W(s, "الشرعية"), b - 0.1, items=[{"text": "النتيجة 2", "tone": "burgundy"}, {"text": "حرب على الشرعية", "tone": "gold", "at": 0.4}], layout="stack", position="upper_right", size=50))

    # 22 — بركة
    s = "22"; a, b = t_in(s), t_out(s)
    c = W(s, "لكن")
    O.append(ov("map", a, c, bbox=[38, 33, 56, 49], rivers=False, title="القوقاز",
                points=[{"label": "القبيلة الذهبية", "lon": G["sarai"][0], "lat": G["sarai"][1], "big": True, "at": 0.3, "anchor": "t"},
                        {"label": "الإيلخانات", "lon": G["tabriz"][0], "lat": G["tabriz"][1], "big": True, "at": 0.6, "anchor": "b"}],
                lines=[{"path": [P("sarai"), [47.6, 43.5]], "tone": "gold", "at": 1.0, "dur": 1.2, "arrow": True},
                       {"path": [P("tabriz"), [47.4, 41.0]], "tone": "burgundy", "at": 1.4, "dur": 1.2, "arrow": True}]))
    O.append(ov("lower_third", W(s, "بركة"), W(s, "بركة") + 4.5, name="بَرْكَة", role="خان القبيلة الذهبية"))
    V.append(vis("img04_mongol_cavalry.jpg", c, b, tint="cold", kb={"from": 1.06, "to": 1.0, "fx0": 0.5, "fy0": 0.5}))
    O.append(ov("keyword", W(s, "اي"), b - 0.1, items=[{"text": "النتيجة 3", "tone": "burgundy"}, {"text": "الحرب نفسها… بذريعة أقل", "tone": "gold", "at": 0.4}], layout="stack", size=50, scrim=True))

    # 23 — غازان
    s = "23"; a, b = t_in(s), t_out(s)
    c = W(s, "عالمنا")
    V.append(vis("pd04_ghazan_oljaitu.jpg", a, c, "archival", fit="card", credit=CR_GHAZAN, kb={"from": 1.0, "to": 1.04}))
    O.append(ov("keyword", W(s, "اعلن"), c - 0.1, items=[{"text": "1295", "tone": "gold"}, {"text": "غازان يعلن إسلامه (حقيقة)", "tone": "parchment", "at": 0.5}], layout="stack", position="lower_right", size=46))
    O.append(ov("split", c, b, right={"title": "إيلخان مسلم", "sub": "1295", "tag": "الواقع", "world": "real", "src": IMG + "img04_mongol_cavalry.jpg"},
                left={"title": "وخليفةٌ حيّ في بغداد", "sub": "واجهةٌ لشرعيته؟", "tag": "الخيال", "world": "fiction", "src": IMG + "img06_throne_empty.jpg", "at": 1.2}))

    # 24 — العلم (حقيقة)
    s = "24"; a, b = t_in(s), t_out(s)
    V.append(vis("img03_library_candle.jpg", a, b, tint="warm", kb={"fx0": 0.45, "fy0": 0.5, "fx1": 0.55, "fy1": 0.45}))
    O.append(ov("source", W(s, "ميخال"), W(s, "ميخال") + 5.5, label="بحث أكاديمي محكّم", value="ميخال بيران (2019)", scrim=True))
    O.append(ov("keyword", W(s, "المستنصرية"), b - 0.1, layout="stack", position="upper_right", size=42,
                items=kw_items(W(s, "المستنصرية"), [("المستنصرية تُفتح: 1259", W(s, "المستنصرية"), "gold"), ("الجويني حاكمًا", W(s, "الجويني"), "parchment"), ("مرصد مراغة: 1259", W(s, "مرصدا"), "gold")])))

    # 25 — ConceptMorph
    s = "25"; a, b = t_in(s), t_out(s)
    O.append(ov("morph", a, b, src=IMG + "img03_library_candle.jpg", at=1.2, labelA="الواقع", labelB="الخيال"))
    O.append(ov("keyword", W(s, "سيحفظ"), b - 0.1, layout="row", position="top", size=40,
                items=kw_items(W(s, "سيحفظ"), [("الأرواح", W(s, "الارواح"), "parchment"), ("المدينة", W(s, "المدينة"), "parchment"), ("المكتبات", W(s, "ومكتبات"), "parchment"), ("المركز", W(s, "المركز"), "gold")])))

    # 26 — الخاتمة
    s = "26"; a, b = t_in(s), t_out(s)
    V.append(vis("img02_baghdad_dusk.jpg", a, b, kb={"from": 1.0, "to": 1.06, "fx0": 0.5, "fy0": 0.45}, fade_in=True))
    O.append(ov("keyword", W(s, "القاهرة"), W(s, "وربما") - 0.1, items=[{"text": "القاهرة: خلافة اسمًا… بلا سلطة", "tone": "parchment"}], position="lower_right", size=44))
    O.append(ov("scene_title", W(s, "هل"), W(s, "اكتب") - 0.1, title="هل سقطت الفكرة\nقبل المدينة؟", size=96, scrim=True))
    O.append(ov("keyword", W(s, "اكتب"), b - 0.1, items=[{"text": "ما الذي كان سيتغيّر فعلًا؟", "tone": "gold", "sub": "اكتب رأيك في التعليقات"}], size=52, scrim=True))

    # 27 — النهاية
    s = "27"; a, b = t_in(s), t_out(s)
    O.append(ov("end", a, b, tease="المصادر في الوصف"))
    TR.append({"t": a, "type": "fade_black_200ms"})

    fiction = []
    for sid in sorted(FICTION_IDS):
        r = [t_in(sid), t_out(sid)]
        if fiction and abs(fiction[-1][1] - r[0]) < 0.05:
            fiction[-1][1] = r[1]
        else:
            fiction.append(r)
    fiction = [{"t_in": round(x, 3), "t_out": round(y, 3)} for x, y in fiction]

    chapters = [{"t": round(t_in(s), 3)} for s in ("03", "13", "14", "17", "26")]
    return V, O, TR, fiction, chapters


# ───────── كابشنز من توقيت الكلمات: ≤2 سطر × ≤28 حرفًا، ≥1.2 ث ─────────
MAXC, MINDUR = 28, 1.2


def wrap2(words):
    lines, cur = [], ""
    for w in words:
        cand = (cur + " " + w).strip()
        if len(cand) <= MAXC or not cur:
            cur = cand
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def _fits(ws):
    return len(wrap2([w["w"] for w in ws])) <= 2


def _split_balanced(ws):
    """يقسم جملة إلى أقل عدد من الكتل المتوازنة (كل كتلة ≤ سطرين × 28 حرفًا)."""
    if _fits(ws):
        return [ws]
    total = sum(len(w["w"]) + 1 for w in ws)
    for n in range(2, len(ws) + 1):
        target = total / n
        chunks, cur, acc = [], [], 0
        for i, w in enumerate(ws):
            cur.append(w); acc += len(w["w"]) + 1
            left = len(ws) - i - 1
            soft = bool(re.search(r"[،,:؛…]$", w["w"]))
            if len(chunks) < n - 1 and left > 0 and (acc >= target or (soft and acc >= target * 0.7)):
                chunks.append(cur); cur, acc = [], 0
        if cur:
            chunks.append(cur)
        if all(_fits(c) for c in chunks):
            return chunks
    return [[w] for w in ws]


def make_cues(words, max_end):
    # 1) جمل (نهاية جملة أو تغيّر مشهد)
    sents, buf = [], []
    for w in words:
        if buf and w.get("scene") != buf[0].get("scene"):
            sents.append(buf); buf = []
        buf.append(w)
        if re.search(r"[.؟?!]»?$|…$", w["w"]) and not re.search(r"^…", w["w"]):
            sents.append(buf); buf = []
    if buf:
        sents.append(buf)
    # 2) دمج الجمل القصيرة جدًا مع التالية/السابقة إن اتّسعت
    merged = []
    for st in sents:
        dur = st[-1]["t1"] - st[0]["t0"]
        if merged and dur < MINDUR and merged[-1][0].get("scene") == st[0].get("scene") and _fits(merged[-1] + st):
            merged[-1] = merged[-1] + st
        else:
            merged.append(st)
    i = 0
    while i < len(merged) - 1:
        st = merged[i]
        if st[-1]["t1"] - st[0]["t0"] < MINDUR and merged[i + 1][0].get("scene") == st[0].get("scene") and _fits(st + merged[i + 1]):
            merged[i] = st + merged.pop(i + 1)
        else:
            i += 1
    # 3) تقسيم متوازن
    chunks = [c for st in merged for c in _split_balanced(st)]
    out = [{"t_in": c[0]["t0"], "t_out": c[-1]["t1"], "words": [w["w"] for w in c]} for c in chunks]
    for c in out:
        c["t_in"] = max(0.0, c["t_in"] - 0.08)
    for i, c in enumerate(out):
        nxt = out[i + 1]["t_in"] - 0.04 if i + 1 < len(out) else max_end
        c["t_out"] = min(max(c["t_out"] + 0.25, c["t_in"] + MINDUR), nxt)
        if c["t_out"] - c["t_in"] < MINDUR and i > 0:
            prev_end = out[i - 1]["t_out"] + 0.04
            c["t_in"] = max(prev_end, c["t_out"] - MINDUR)
    return [{"t_in": round(c["t_in"], 3), "t_out": round(c["t_out"], 3), "ar": "\n".join(wrap2(c["words"])), "en": ""} for c in out]


KEYS = ["1258", "1257", "1259", "1260", "1261", "1295", "بغداد", "هولاكو", "الخليفة", "المغول", "الشرعية", "خيال", "عين جالوت"]


def add_keywords(cues):
    for c in cues:
        flat = c["ar"].replace("\n", " ")
        c["keywords"] = [k for k in KEYS if k in flat][:2]
    return cues


def base_meta(pid_suffix, title, aspect, res, duration):
    return {
        "schema_version": "2.0",
        "brand_ref": {"theme_path": "data/brand.json", "watermark": "on"},
        "project": {"id": EP + pid_suffix, "series_id": "riwaq_what_if", "title": title, "episode_number": None,
                    "video_type": "documentary" if aspect == "16x9" else "short",
                    "platforms": ["youtube"] if aspect == "16x9" else ["youtube_shorts"], "aspect_ratios": [aspect],
                    "language_primary": "ar", "language_secondary": "en", "priority": "quality"},
        "source": {"type": "none", "rights": "owned", "provenance_note": "صور: ويكيميديا كومنز (ملكية عامة) + إعادة تصوّر بالذكاء الاصطناعي — انظر credits.csv"},
        "narration": {"mode": "provided", "profile_id": "arena_tts_voice01", "replacement_policy": "drafts_allowed", "note": "DRAFT_VO — صوت منصة غير رسمي (موافقة المالك في البوابة 1)"},
        "edit": {"fps": 30, "cut_style": "medium", "duration_s": duration, "music_mood": "hijaz-original", "stingers": {"in": False, "out": True}},
        "render": {"resolution": res, "preset": "youtube_master" if aspect == "16x9" else "social_vertical", "per_platform_export": False},
        "deliverables": {},
        "qc_rules": {"must_pass": ["loudness", "true_peak", "captions_sync", "caption_line_length", "safe_zones", "no_flash", "logo_present", "palette_lock", "font_lock", "source_logged"], "tolerance_lu": 0.5},
        "status": "READY_FOR_REVIEW",
        "notes": "DRAFT_VO · الخيال التاريخي موسوم دائمًا (ConceptFrame) · صور الذكاء الاصطناعي موسومة «إعادة تصوّر»",
    }


def build_short():
    D = TS["duration_s"]; B = TS["beats"]
    bt = lambda i: B[i]["t_in"]; be = lambda i: B[i]["t_out"]
    V, O = [], []
    cb = lambda src, a, b, kind="ai", **kw: V.append(vis(src, a, b, kind, fit="contain_blur", **kw))
    cb("pd02_bagdad1258_crop43.jpg", 0, be(1), "archival", credit="جامع التواريخ · نحو 1430 · ملكية عامة", kb={"from": 1.0, "to": 1.08, "fx0": 0.5, "fy0": 0.5})
    O.append(ov("keyword", 0.2, be(0), items=[{"text": "10 فبراير 1258", "tone": "gold"}], position="top", size=64))
    cb("img07_sealed_letter.jpg", bt(2), be(2))
    O.append(ov("keyword", WS("يخضع"), be(2), items=[{"text": "أن يخضع… فينجو", "tone": "gold"}], position="top", size=60))
    cb("img02_baghdad_dusk.jpg", bt(3), be(3), tint="dark")
    O.append(ov("keyword", bt(3) + 0.1, be(3), layout="stack", position="top", size=56,
                items=kw_items(bt(3) + 0.1, [("الحِلّة", WS("الحلة"), "parchment"), ("الكوفة", WS("والكوفة"), "parchment"), ("البصرة", WS("والبصرة"), "parchment"), ("خضعت… فنجت", WS("فنجت"), "gold")])))
    O.append(ov("scene_title", bt(4), be(5), title="فماذا لو قَبِل؟", size=110, kicker="خيال تاريخي مبنيّ على المصادر", tone="burgundy"))
    cb("img03_library_candle.jpg", bt(6), be(6))
    O.append(ov("keyword", bt(6), be(6), layout="stack", position="top", size=56,
                items=kw_items(bt(6), [("تنجو بغداد", WS("تنجو"), "parchment"), ("وأهلها", WS("واهلها"), "parchment"), ("ومكتباتها", WS("ومكتباتها"), "gold")])))
    cb("img06_throne_empty.jpg", bt(7), be(7), tint="burgundy")
    O.append(ov("keyword", WS("يمنح") - 0.3, be(7), items=[{"text": "شرعية بلا قرار", "tone": "gold"}], position="top", size=66))
    cb("img04_mongol_cavalry.jpg", bt(8), be(9))
    O.append(ov("keyword", WS("مونكو") - 0.6, be(8), items=[{"text": "1259 · موت مُونْكُو", "tone": "gold", "sub": "حقيقة في العالمين"}], position="top", size=58))
    O.append(ov("keyword", bt(9), be(9), items=[{"text": "عين جالوت 1260", "tone": "gold", "sub": "في العالمين"}], position="top", size=58))
    O.append(ov("split", bt(10), be(11), right={"title": "خليفة القاهرة", "tag": "الواقع", "world": "real", "src": IMG + "img08_council_shadows.jpg"},
                left={"title": "لا خليفة لاجئًا", "sub": "بيبرس بلا شرعية جاهزة", "tag": "الخيال", "world": "fiction", "src": IMG + "img06_throne_empty.jpg", "at": WS("بيبرس") - bt(10)}))
    cb("img02_baghdad_dusk.jpg", bt(12), D)
    O.append(ov("scene_title", bt(12), be(12), title="بغداد… أم الفكرة؟", size=96, scrim=True))
    O.append(ov("keyword", bt(13), D, items=[{"text": "القصة كاملة على رِواق", "tone": "gold"}], size=60, scrim=True))
    fiction = [{"t_in": round(bt(5), 3), "t_out": round(be(11), 3)}]
    return V, O, fiction


def main():
    os.makedirs(OUT, exist_ok=True)
    V, O, TR, fiction, chapters = build_long()
    D = TL["duration_s"]
    cues = add_keywords(make_cues(TL["words"], D))
    m = base_meta("", "ماذا لو لم تسقط بغداد؟", "16x9", [1920, 1080], D)
    m["story"] = {"hook": SC["scenes"][0]["text"], "scenes": [], "cta_question": "ما الذي كان سيتغيّر فعلًا؟"}
    m["audio"] = {"vo": [{"src": MIX + "mix_master.wav", "t_in": 0, "volume_db": 0}], "music": None, "stingers": []}
    m["captions"] = {"styles": ["keyword_highlight"], "languages": ["ar", "en"], "sync_source": "timeline.json words (aligned)", "burn_in": False, "data": cues}
    m["visuals"], m["overlays"], m["fiction"], m["transitions"] = V, O, fiction, TR
    m["progress"] = {"chapters": chapters}
    m["deliverables"] = {"master": f"exports/{EP}/video/master.mp4", "captions": [f"exports/{EP}/subtitles/subtitles_ar.srt"]}
    json.dump(m, open(os.path.join(OUT, "episode_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    Vs, Os, fs = build_short()
    Ds = TS["duration_s"]
    cs = add_keywords(make_cues([dict(w, scene="S") for w in TS["words"]], Ds))
    ms = base_meta("_SHORT", "ماذا لو لم تسقط بغداد؟ (Short)", "9x16", [1080, 1920], Ds)
    ms["story"] = {"scenes": []}
    ms["audio"] = {"vo": [{"src": MIX + "mix_master_short.wav", "t_in": 0, "volume_db": 0}], "music": None, "stingers": []}
    ms["captions"] = {"styles": ["keyword_highlight"], "languages": ["ar", "en"], "sync_source": "timeline_short.json words", "burn_in": True, "data": cs}
    ms["visuals"], ms["overlays"], ms["fiction"], ms["transitions"] = Vs, Os, fs, []
    ms["progress"] = None
    json.dump(ms, open(os.path.join(OUT, "episode_meta_short.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # timestamps.json — مرجع التوقيت الموحّد (مشاهد + جمل + كلمات)
    ts = {
        "episode_id": EP, "voice": "voice-01 (DRAFT_VO)", "tempo": TL["tempo"],
        "long": {"duration_s": D, "scenes": [dict(id=s["id"], t_in=round(s["t_in"], 3), t_out=round(s["t_out"], 3), fiction=s["id"] in FICTION_IDS) for s in TL["scenes"]],
                 "captions": [{k: c[k] for k in ("t_in", "t_out", "ar")} for c in cues],
                 "words": [{"w": w["w"], "t0": round(w["t0"], 3), "t1": round(w["t1"], 3), "scene": w["scene"]} for w in TL["words"]]},
        "short": {"duration_s": Ds, "beats": [{k: b[k] for k in ("i", "t_in", "t_out", "text")} for b in TS["beats"]],
                  "captions": [{k: c[k] for k in ("t_in", "t_out", "ar")} for c in cs],
                  "words": [{"w": w["w"], "t0": round(w["t0"], 3), "t1": round(w["t1"], 3)} for w in TS["words"]]},
    }
    json.dump(ts, open(os.path.join(EPDIR, "timestamps.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    short_c = [c for c in cues if c["t_out"] - c["t_in"] < MINDUR - 1e-6]
    longl = [c for c in cues if any(len(l) > MAXC for l in c["ar"].split("\n"))]
    print(f"long: {len(V)} visuals, {len(O)} overlays, {len(cues)} cues (short<{MINDUR}s: {len(short_c)}, >28ch lines: {len(longl)}), fiction={fiction}")
    print(f"short: {len(Vs)} visuals, {len(Os)} overlays, {len(cs)} cues (short: {sum(1 for c in cs if c['t_out']-c['t_in']<MINDUR-1e-6)})")


if __name__ == "__main__":
    main()
