#!/usr/bin/env python3
"""Build script.md from script_scenes.json and compute timing from spoken words only.

Usage: python3 episode/WHAT_IF_BAGHDAD_NEVER_FELL/build_script.py
- Counts spoken words only (the text field), per editorial standard §5.
- Duration = words / wpm * 60 + a fixed pause per scene.
- Timings are estimates; they are replaced by real TTS timestamps in Phase 4.
"""
import json, re, pathlib

HERE = pathlib.Path(__file__).parent
data = json.loads((HERE / "script_scenes.json").read_text(encoding="utf-8"))
wpm, pause = data["wpm"], data["pause_s_per_scene"]


def words(t: str) -> int:
    return len([w for w in re.split(r"\s+", re.sub(r"[«»…،.؟?!:؛,]", " ", t)) if w])


def mmss(s: float) -> str:
    s = int(round(s)); return f"{s // 60:02d}:{s % 60:02d}"


t = 0.0; rows = []; total_w = 0
for sc in data["scenes"]:
    w = words(sc["text"]); total_w += w
    d = round(w / wpm * 60 + pause, 1)
    rows.append((sc, w, t, t + d, d)); t += d

short_w = words(data["short"]["text"]); short_d = short_w / wpm * 60

out = []
out.append(f"# SCRIPT — {data['episode_id']} «{data['title_working']}»\n")
out.append("> **الحالة: DRAFT — بانتظار Human Gate 1 (مراجعة السكربت والفرضية).** ممنوع تحويل النص إلى صوت قبل الإجازة.")
out.append("> المصدر الأصلي للنص: `script_scenes.json` — هذا الملف مولَّد عبر `build_script.py`، فلا يُعدَّل يدويًا.")
out.append(f"> طريقة الحساب: الكلمات المنطوقة فقط ÷ {wpm} كلمة/دقيقة + {pause} ث وقفة لكل مشهد. التوقيتات تقديرية، وتُستبدل بطوابع TTS الفعلية في المرحلة 4.\n")
out.append(f"**إجمالي الكلمات المنطوقة: {total_w} · المدة التقديرية: {mmss(t)} ({t/60:.2f} د) · عدد المشاهد: {len(rows)}**\n")
out.append(f"نطاق المدة عند 130–150 كلمة/دقيقة: {mmss(total_w/150*60 + pause*len(rows))} – {mmss(total_w/130*60 + pause*len(rows))}\n")
labels = {"HOOK":"Hook","PROMISE":"وعد وتصنيف","BACKGROUND":"خلفية","MYTH_CHECK":"تصحيح الأساطير","TURNING_POINT":"لحظة الفرضية","ALT_SHIFT":"التحول البديل","CLOSE_OPEN_QUESTION":"خاتمة بسؤال مفتوح","END":"شاشة النهاية"}
groups = []
for sc, *_ in rows:
    lab = labels.get(sc["beat"], "نتائج متسلسلة")
    if groups and groups[-1][0] == lab: groups[-1][2] = sc["id"]
    else: groups.append([lab, sc["id"], sc["id"]])
out.append("**البنية:** " + " → ".join(f"{g[0]} ({g[1]}" + (f"–{g[2]})" if g[2] != g[1] else ")") for g in groups) + "\n")
out.append("**تمييز الخيال:** المشاهد الموسومة ⟨خيال⟩ تحمل وسم «خيال تاريخي» دائمًا على الشاشة، مع إطار عنابي (style_brief.json).\n\n---\n")
for sc, w, a, b, d in rows:
    tag = " ⟨خيال⟩" if sc["fiction"] else ""
    out.append(f"### [SCENE {sc['id']} | {mmss(a)}-{mmss(b)} | المدة {d:.0f}s] — {sc['beat']}{tag}\n")
    out.append(f"- **النص:** {sc['text']}")
    out.append(f"- **الصورة:** {sc['visual']} — *النوع: {sc['type']}*")
    out.append(f"- **الحركة:** {sc['motion']}")
    out.append(f"- **النص على الشاشة:** {sc['onscreen']}")
    out.append(f"- **المؤثر الصوتي:** {sc['sfx']}")
    out.append(f"- **الدليل:** {sc['evidence']} · *كلمات: {w}*\n")
sh = data["short"]
out.append("---\n\n## SHORT_V1 (9:16 · الهدف 45–55 ث)\n")
out.append(f"*كلمات: {short_w} · تقدير عند {wpm} ك/د: {short_d:.0f} ث · عند 150 ك/د: {short_w/150*60:.0f} ث*\n")
out.append(f"> {sh['text']}\n")
out.append(f"ملاحظات: {sh['notes']}\n")
(HERE / "script.md").write_text("\n".join(out), encoding="utf-8")
print(f"words={total_w} duration={mmss(t)} scenes={len(rows)} short_words={short_w} short_s={short_d:.1f}")
