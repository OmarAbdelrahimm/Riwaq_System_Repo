"""خط إنتاج الحلقات الجديدة 04–06: كابشن محرّر + بطاقات b-roll ثلاثية الأبعاد + ترميز.

    python build_ep.py prep EP04
    python build_ep.py render EP04
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

import broll as BR  # noqa: E402
import captions as CAP  # noqa: E402
import ep_data as E  # noqa: E402
import graphics as G  # noqa: E402
import music as M  # noqa: E402
import srtlib as S  # noqa: E402

REPO = "/home/user/Riwaq_System_Repo"
FF = os.environ.get("FFMPEG") or __import__("imageio_ffmpeg").get_ffmpeg_exe()
FONTS = f"{REPO}/public/fonts"
WORK = f"{REPO}/google_drive/work/ep"
OUTROOT = f"{REPO}/outputs/SERIES_RIWAQ/NEW"
MUSIC = f"{REPO}/assets/series_riwaq/music"

ENDPAD = 4.0
IDENT_END = 1.7
WM_PERIOD = 30.0
WM_LEN = 6.0

# بطاقات b-roll: (معرّف, مشهد, عنوان, سطر تعريفي, ملاحظة, لوحة لونية, البداية, المدة)
CARDS = {
    "EP04": [
        ("c1", "house", ["فنادق للشياطين"], "البيت", "لا تسمّي… فيسكنونه", "red", 7.0, 8.0),
        ("c2", "conference", ["مؤتمر كل يوم"], "عرشه على الماء", "تقرير يومي عن بني آدم", "gold", 29.0, 8.0),
        ("c3", "gap", ["أهمّ شيء عنده", "أن يفرّق"], "بين الزوجين", "ما فعله أحدٌ غيره فاحتضنه", "red", 47.0, 8.0),
        ("c4", "network", ["كلمة… وجمرة"], "الكلمة تشتعل", "﴿قل لعبادي يقولوا التي هي أحسن﴾", "gold", 168.0, 8.5),
        ("c5", "vessel", ["مجرى الدم"], "حديث صفية", "الشيطان يجري من ابن آدم مجرى الدم", "red", 205.0, 8.0),
        ("c6", "network", ["معركة في كل لحظة"], "الدخول… الأكل… النوم", "حاضر في كل تفاصيل حياتنا", "red", 229.0, 8.0),
    ],
    "EP05": [
        ("c1", "road", ["سيارة واحدة…", "خمسة مقاعد"], "المنظومة", "وجهة، خريطة، سائق، رفيق، لوحات", "gold", 2.0, 8.0),
        ("c2", "network", ["مَن يركب معك؟"], "الآخر", "اختيار الرفيق يحدد الوصول", "gold", 60.0, 8.0),
        ("c3", "ropes", ["حبلان"], "الصلاة والقرآن", "حبل صاعد… وحبل نازل", "gold", 96.0, 8.0),
        ("c4", "balance", ["جنة… ونار"], "هرة وكلب", "علاقة صغيرة… وزنها ضخم", "gold", 137.0, 8.0),
        ("c5", "balance", ["المُفلس"], "حسنات تُدفع دَينًا", "عبادات بلا تعاملات", "red", 196.0, 8.0),
        ("c6", "books", ["سرّ النجاح…", "في السرّ"], "الخلوة", "كيف حالك حين لا يراك أحد؟", "gold", 254.0, 8.0),
    ],
    "EP06": [
        ("c1", "funnel", ["رأي… وحقيقة"], "افرِز قبل أن تنقد", "الرأي يُلبس ويُخلع، الحقيقة تُتَّبع", "gold", 33.0, 8.0),
        ("c2", "network", ["إرضاء الجميع؟"], "مستحيل", "لا يوجد وقت ولا قدرة لذلك", "gold", 106.0, 8.0),
        ("c3", "network", ["تتابع الألسن"], "حين يتّفقون", "الرأي المتكرر يرتقي إلى حقيقة", "red", 142.0, 8.0),
        ("c4", "balance", ["كلام الناس"], "بميزان العاقل", "يأخذه بالاعتبار… ولا يكسره", "gold", 174.0, 8.0),
        ("c5", "compass", ["البوصلة"], "ليست كلامهم", "التقويم يهمّ… والتوجيه لله", "gold", 225.0, 8.0),
        ("c6", "books", ["«أنت لا تصلح»"], "قصة الطحاوي", "كلمة كادت تُطفئ إمامًا", "gold", 256.0, 12.0),
    ],
}


def edir(key: str) -> str:
    d = f"{WORK}/build_{key}"
    os.makedirs(d, exist_ok=True)
    return d


def vdir(key: str) -> str:
    d = f"{OUTROOT}/{key}"
    os.makedirs(d, exist_ok=True)
    return d


def sh(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"FAILED {' '.join(cmd[:6])}\n{p.stderr[-2500:]}")
    return p


def src(key: str) -> str:
    return f"{REPO}/google_drive/work/sources/{key}.mp4"


def dur_of(path: str) -> float:
    p = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True, text=True)
    for line in p.stderr.splitlines():
        if "Duration:" in line:
            t = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = t.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError("no duration")


# ------------------------------------------------------------------ captions
def align(rows: list[dict], ar: list[str], en: list[str]) -> list[dict]:
    """يوزّع النص المحرّر على زمن الحلقة بحسب طول كل سطر (مع السنّ على حدود المصدر)."""
    t0, t1 = rows[0]["start"], rows[-1]["end"]
    bounds = sorted({round(r["start"], 2) for r in rows} | {round(r["end"], 2) for r in rows})
    total = sum(len(x) + 12 for x in ar)
    out, acc = [], 0.0
    for i, (a, e) in enumerate(zip(ar, en)):
        st = t0 + (t1 - t0) * acc / total
        acc += len(a) + 12
        en_t = t0 + (t1 - t0) * acc / total
        st = min(bounds, key=lambda b: abs(b - st))
        en_t = min(bounds, key=lambda b: abs(b - en_t))
        out.append({"start": st, "end": max(st + 0.9, en_t), "text": a, "en": e})
    for i in range(len(out) - 1):
        out[i]["end"] = min(out[i]["end"], out[i + 1]["start"])
    for r in out:
        ws = S.words_of(r["text"])
        span = max(0.8, r["end"] - r["start"])
        per = span / max(1, len(ws))
        r["words"] = [S.Word(w, r["start"] + k * per, r["start"] + (k + 1) * per, 0) for k, w in enumerate(ws)]
    return out


def make_captions(key: str) -> dict:
    d = edir(key)
    rows = json.load(open(f"{WORK}/{key}_rows.json", encoding="utf-8"))
    fix = json.load(open(f"{REPO}/scripts/series/ep_fix/{key}.json", encoding="utf-8"))
    fin = align(rows, fix["ar"], fix["en"])
    CAP.build_ass(fin, f"{d}/captions.ass")
    CAP.build_ar_srt([{"start": r["start"], "end": r["end"], "text": r["text"]} for r in fin], f"{d}/CAPTIONS_AR.srt")
    en_rows = [{"start": r["start"], "end": r["end"], "text": r["en"]} for r in fin]
    CAP.build_en_srt(en_rows, f"{d}/CAPTIONS_EN.srt")
    CAP.build_bilingual_srt(fin, en_rows, f"{d}/CAPTIONS_AR_EN.srt")
    return {"rows": len(fin), "first": fin[0]["start"], "last": fin[-1]["end"]}


# ------------------------------------------------------------------ visuals
def make_assets(key: str) -> None:
    d = edir(key)
    e = E.by_key(key)
    G.caption_card().crop((239, 935, 1681, 1053)).save(f"{d}/card.png")
    G.watermark_bug(96).save(f"{d}/bug.png")
    G.ident_lockup().save(f"{d}/ident.png")
    nxt = E.by_key(f"EP0{e['order']+1}")["title_a"] if e["order"] < E.TOTAL_SERIES else None
    G.endcard(e["order"], E.TOTAL_SERIES, nxt, series="مركزية العلاقة مع الله — ياسر الحزيمي",
              channel="@gallery_of_history").save(f"{d}/endcard.png")
    # بطاقات b-roll → صور ثم مقاطع قصيرة بحركة تكبير بطيئة
    for cid, scene, head, kick, note, pal, t, dur in CARDS[key]:
        png = f"{d}/{cid}.png"
        BR.make_card(scene, head, kick, note, palette=pal, out=png)
        mp4 = f"{d}/{cid}.mp4"
        frames = int(round(dur * 25))
        zstep = 0.045 / max(1, frames)
        vf = (f"zoompan=z='1.0+{zstep:.6f}*on':x='iw/2-(iw/zoom/2)':"
              f"y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=25,"
              f"fade=t=in:st=0:d=0.35,fade=t=out:st={dur-0.4:.2f}:d=0.4")
        sh([FF, "-v", "error", "-y", "-loop", "1", "-i", png, "-t", f"{dur:.2f}",
            "-vf", vf, "-frames:v", str(frames), "-r", "25",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", mp4])
    # الموسيقى المشتركة
    os.makedirs(MUSIC, exist_ok=True)
    if not os.path.exists(f"{MUSIC}/MUSIC_INTRO_riwaq.wav"):
        M.write_wav(f"{MUSIC}/MUSIC_INTRO_riwaq.wav", M.intro())
        M.write_wav(f"{MUSIC}/MUSIC_OUTRO_riwaq.wav", M.outro())
    if not os.path.exists(f"{MUSIC}/MUSIC_BED_series.wav"):
        M.write_wav(f"{MUSIC}/MUSIC_BED_series.wav", M.bed(120.0, dbfs=-18.0))
    print(f"[{key}] assets OK: {len(CARDS[key])} بطاقة b-roll")


# ------------------------------------------------------------------ render
def video_filter(key: str, dur: float) -> str:
    d = edir(key)
    total = dur + ENDPAD
    f = [f"[0:v]trim=0:{total:.3f},setpts=PTS-STARTPTS,fps=25[base]"]
    idx = 2
    n = 0
    cur = "base"
    # بطاقات b-roll فوق الفيديو (تحت الكابشن)
    for cid, scene, head, kick, note, pal, t, cd in CARDS[key]:
        nxt = f"b{n+1}"
        f.append(f"[{idx}:v]format=rgba,tpad=start_duration={t:.2f}:start_mode=add:color=0x00000000,"
                 f"trim=0:{t+cd:.2f},setpts=PTS-STARTPTS[c{idx}]")
        f.append(f"[{cur}][c{idx}]overlay=0:0:enable='between(t,{t:.2f},{t+cd:.2f})':"
                 f"eof_action=pass:repeatlast=0[{nxt}]")
        idx += 1
        n += 1
        cur = nxt
    # شريط الكابشن فوق بطاقات b-roll (وإلا غطّته البطاقة)
    f.append(f"[1:v]format=rgba[card]")
    f.append(f"[{cur}][card]overlay=239:935:enable='between(t,0,{dur:.3f})'[bcard]")
    f.append(f"[bcard]ass={d}/captions.ass:fontsdir={FONTS}[bcap]")
    wm = []
    tt = 20.0
    while tt < dur - 1:
        wm.append(f"between(t,{tt:.2f},{min(tt + WM_LEN, dur - 0.3):.2f})")
        tt += WM_PERIOD
    f.append(f"[{idx}:v]format=rgba[bug]")
    f.append(f"[bcap][bug]overlay=54:H-h-118:enable='{'+'.join(wm)}'[bw]")
    idx += 1
    f.append(f"[{idx}:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1,fade=t=out:st={IDENT_END-0.45:.2f}:d=0.45:alpha=1[idn]")
    f.append(f"[bw][idn]overlay=0:0:enable='between(t,0,{IDENT_END:.2f})'[bi]")
    idx += 1
    f.append(f"[{idx}:v]trim=0:{ENDPAD:.2f},setpts=PTS-STARTPTS[ec]")
    f.append(f"[bi][ec]overlay=0:0:enable='gte(t,{dur:.3f})'[be]")
    idx += 1
    f.append(f"[be]fade=t=in:st=0:d=0.30,fade=t=out:st={total-0.55:.2f}:d=0.55,"
             f"format=yuv420p,setsar=1[vout]")
    nidx = {"bug": idx - 3, "ident": idx - 2, "endcard": idx - 1, "bed": idx, "intro": idx + 1, "outro": idx + 2}
    return ";".join(f), nidx


def audio_filter(key: str, dur: float, nidx: dict) -> str:
    total = dur + ENDPAD
    f = [f"[0:a]atrim=0:{dur:.3f},asetpts=N/SR/TB,aresample=48000,asplit=2[voice][sc]",
         f"[{nidx['bed']}:a]atrim=0:{dur:.3f},asetpts=N/SR/TB,volume=0.5,aresample=48000[bedraw]",
         "[bedraw][sc]sidechaincompress=threshold=0.03:ratio=9:attack=25:release=420:makeup=1:level_sc=1[bed]",
         f"[{nidx['intro']}:a]atrim=0:4.4,asetpts=N/SR/TB,volume=0.42,aresample=48000[in]",
         f"[{nidx['outro']}:a]atrim=0:{ENDPAD+0.6:.2f},asetpts=N/SR/TB,volume=0.62,"
         f"adelay={int((dur-0.6)*1000)}|{int((dur-0.6)*1000)},aresample=48000[out]",
         "[voice][bed][in][out]amix=inputs=4:duration=longest:normalize=0[premix]",
         f"[premix]apad=pad_dur={ENDPAD:.2f},atrim=0:{total:.3f},loudnorm=I=-14:TP=-1.5:LRA=11,"
         "aresample=48000,alimiter=limit=0.89:level=disabled[aout]"]
    return ";".join(f)


def render(key: str, preset="veryfast", crf=19, out_name=None) -> str:
    d = edir(key)
    dur = dur_of(src(key)) if abs(dur_of(src(key)) - (E.by_key(key)["cut"][1] - E.by_key(key)["cut"][0])) > 1 else \
        E.by_key(key)["cut"][1] - E.by_key(key)["cut"][0]
    dur = dur_of(src(key))
    total = dur + ENDPAD
    vf, nidx = video_filter(key, dur)
    af = audio_filter(key, dur, nidx)
    cmd = [FF, "-y", "-hide_banner", "-nostdin", "-i", src(key),
           "-loop", "1", "-i", f"{d}/card.png"]
    for cid, *_ in CARDS[key]:
        cmd += ["-i", f"{d}/{cid}.mp4"]
    cmd += ["-loop", "1", "-i", f"{d}/bug.png",
            "-loop", "1", "-i", f"{d}/ident.png",
            "-loop", "1", "-i", f"{d}/endcard.png",
            "-stream_loop", "-1", "-i", f"{MUSIC}/MUSIC_BED_series.wav",
            "-i", f"{MUSIC}/MUSIC_INTRO_riwaq.wav",
            "-i", f"{MUSIC}/MUSIC_OUTRO_riwaq.wav",
            "-filter_complex", vf + ";" + af,
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
            "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p",
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
            "-color_range", "tv", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
            "-movflags", "+faststart", "-t", f"{total:.3f}",
            out_name or f"{vdir(key)}/MASTER_FINAL_{key}.mp4"]
    sh(cmd)
    out = out_name or f"{vdir(key)}/MASTER_FINAL_{key}.mp4"
    print(f"[{key}] render OK -> {out} ({os.path.getsize(out)/1e6:.1f} MB)")
    return out


if __name__ == "__main__":
    mode, key = sys.argv[1], sys.argv[2]
    if mode == "prep":
        print(make_captions(key))
        make_assets(key)
    elif mode == "render":
        render(key)
