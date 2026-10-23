"""بناء الحلقة المجمّعة «العلاقة التي تُصلح كل العلاقات» من الحلقات الست.

المبدأ: فيلم واحد في ستة فصول، لا «ست حلقات في فيديو واحد».

ما يفعله:
1) يقصّ معرّف كل حلقة (عدا الأولى) وبطاقة ختامها.
2) يضيف بطاقة فصل بين كل مقطعين + بطاقة افتتاح + بطاقة ختام جديدة.
3) يوازن الصوت لكل مقطع على −14.5 LUFS (قياس فعلي ثم gain ثابت، بلا ضخّ).
4) ينعم الوصلات: fade صورة/صوت 0.45s على كل طرف، فتصبح الفصول فواصل هادئة.
5) يبني ترجمة إنجليزية واحدة (SRT) بإزاحات صحيحة.

التشغيل:
    python3 scripts/series/compile.py cards      # يبني البطاقات فقط
    python3 scripts/series/compile.py srt        # يبني ترجمة EN
    python3 scripts/series/compile.py render     # يبني الفيديو
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

import graphics as G  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

REPO = "/home/user/Riwaq_System_Repo"
DRIVE = f"{REPO}/google_drive"
WORK = f"{REPO}/work/compile"
CARDS = f"{WORK}/cards"
OUTDIR = f"{REPO}/outputs/SERIES_RIWAQ/COMPILED"
FF = os.environ.get("FFMPEG", "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2")

W, H, FPS = 1920, 1080, 25
ENDPAD = 8.0          # بطاقة الختام المدمجة داخل كل ماستر (تبدأ عند dur−8)
IDENT = 2.05          # معرّف البداية داخل كل ماستر
FADE = 0.45           # تلاشي طرفي لكل مقطع
CARD_D = 1.55         # مدة بطاقة الفصل
OPEN_D = 4.2          # بطاقة الافتتاح
END_D = 6.0           # بطاقة الختام
TARGET_I = -14.5

EPISODES = [
    {"key": "01", "file": "الفيديو 01 — العلاقات أعمق من التواصل (ماستر).mp4",
     "dur": 297.88, "skip": 0.0, "pad": 0.6, "chapter": "العلاقات أعمق من التواصل", "n": 1},
    {"key": "02", "file": "الفيديو 02 — المقارنة أداة لا معيار (ماستر).mp4",
     "dur": 235.28, "skip": IDENT, "pad": ENDPAD, "chapter": "المقارنة أداة لا معيار", "n": 2},
    {"key": "03", "file": "الفيديو 03 — النهايات في العلاقات (ماستر).mp4",
     "dur": 254.72, "skip": IDENT, "pad": ENDPAD, "chapter": "النهايات في العلاقات", "n": 3},
    {"key": "04", "file": "الفيديو 04 — الشيطان يجري مجرى الدم (ماستر).mp4",
     "dur": 259.40, "skip": IDENT, "pad": ENDPAD, "chapter": "الشيطان يجري مجرى الدم", "n": 4},
    {"key": "05", "file": "الفيديو 05 — من يقود سيارتك؟ منظومة العلاقات (ماستر).mp4",
     "dur": 289.00, "skip": IDENT, "pad": ENDPAD, "chapter": "من يقود سيارتك؟", "n": 5},
    {"key": "06", "file": "الفيديو 06 — الرأي ليس الحقيقة النقد بلا جرح (ماستر).mp4",
     "dur": 299.01, "skip": IDENT, "pad": ENDPAD, "chapter": "الرأي ليس الحقيقة", "n": 6},
]

SERIES_TITLE = ["العلاقة التي", "تُصلح كل العلاقات"]
ORDINALS = ["الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس"]


# ------------------------------------------------------------------ بطاقات
def _bg() -> Image.Image:
    img = Image.new("RGB", (W, H), (17, 15, 12))
    d = ImageDraw.Draw(img)
    for y in range(H):
        k = 1 - (y / H) * 0.55
        d.line([(0, y), (W, y)], fill=(int(30 * k) + 8, int(27 * k) + 7, int(22 * k) + 6))
    d.rectangle([70, 58, W - 70, H - 58], outline=G.GOLD, width=2)
    d.rectangle([86, 74, W - 86, H - 74], outline=(116, 96, 52), width=1)
    return img


def _brand_dots(d: ImageDraw.ImageDraw, y: int) -> None:
    d.line([(W // 2 - 90, y), (W // 2 + 90, y)], fill=G.GOLD + (255,), width=2)


def card_opening(out: str) -> None:
    img = _bg()
    d = ImageDraw.Draw(img)
    lock = G.brand_lockup(190, color=G.PARCH)
    img.paste(lock, ((W - lock.width) // 2, 150), lock)
    y = 150 + lock.height + 70
    _brand_dots(d, y)
    y += 52
    f_k = G.font(G.PLEX_M, 30)
    G.draw_ar(d, (W // 2, y), "ستة فصول · رحلة واحدة", f_k, G.GOLD_L, anchor="ma")
    y += 66
    for line in SERIES_TITLE:
        fnt = G.fit_font(G.AMIRI_B, line, W - 560, 96, 56)
        G.draw_ar(d, (W // 2, y), line, fnt, G.PARCH, anchor="ma")
        y += int(fnt.size * 1.5)
    y += 34
    f_n = G.font(G.PLEX_M, 32)
    G.draw_ar(d, (W // 2, y), "د. ياسر الحزيمي", f_n, (206, 195, 172), anchor="ma")
    img.save(out, quality=95)
    print("card", out)


def card_chapter(n: int, title: str, out: str) -> None:
    img = _bg()
    d = ImageDraw.Draw(img)
    lock = G.brand_lockup(132, color=G.PARCH)
    img.paste(lock, ((W - lock.width) // 2, 132), lock)
    y = 132 + lock.height + 86
    _brand_dots(d, y)
    y += 54
    f_k = G.font(G.PLEX_B, 34)
    G.draw_ar(d, (W // 2, y), f"الفصل {ORDINALS[n - 1]}", f_k, G.GOLD_L, anchor="ma")
    y += 96
    fnt = G.fit_font(G.AMIRI_B, title, W - 460, 96, 56)
    G.draw_ar(d, (W // 2, y), title, fnt, G.PARCH, anchor="ma")
    # شريط تقدّم صغير يعطي إحساس التسلسل
    bw, bh = 520, 4
    x0 = (W - bw) // 2
    yb = H - 168
    d.rectangle([x0, yb, x0 + bw, yb + bh], fill=(68, 60, 46))
    d.rectangle([x0 + bw - int(bw * n / 6), yb, x0 + bw, yb + bh], fill=G.GOLD_L)
    f_small = G.font(G.PLEX_M, 24)
    G.draw_ar(d, (W // 2, yb + 30), f"{n} / 6", f_small, (150, 140, 120), anchor="ma")
    img.save(out, quality=95)
    print("card", out)


def card_end(out: str) -> None:
    img = _bg()
    d = ImageDraw.Draw(img)
    lock = G.brand_lockup(196, color=G.PARCH)
    img.paste(lock, ((W - lock.width) // 2, 120), lock)
    y = 120 + lock.height + 66
    _brand_dots(d, y)
    y += 52
    fnt = G.fit_font(G.AMIRI_B, "العلاقة التي تُصلح كل العلاقات", W - 420, 84, 52)
    G.draw_ar(d, (W // 2, y), "العلاقة التي تُصلح كل العلاقات", fnt, G.PARCH, anchor="ma")
    y += int(fnt.size * 1.95)

    # دعوة واضحة: قائمة التشغيل + أيقونة تشغيل على يمين النص
    f_cta = G.font(G.PLEX_B, 40)
    cta = "الحلقات الست كاملة في قائمة التشغيل"
    G.draw_ar(d, (W // 2, y), cta, f_cta, G.GOLD_L, anchor="ma")
    tw = G.text_w(f_cta, G.ar(cta))
    cx = W // 2 + tw // 2 + 34
    cy = y + 26
    d.polygon([(cx + 20, cy), (cx - 10, cy - 17), (cx - 10, cy + 17)], fill=G.GOLD_L)

    y += 92
    f3 = G.font(G.PLEX_M, 30)
    G.draw_ar(d, (W // 2, y), "د. ياسر الحزيمي · بودكاست بدون ورق", f3, (200, 190, 168), anchor="ma")

    # سطر ختامي هادئ
    f4 = G.font(G.PLEX_M, 26)
    d.line([(W // 2 - 60, H - 196), (W // 2 + 60, H - 196)], fill=(120, 102, 60), width=2)
    G.draw_ar(d, (W // 2, H - 158), "@gallery_of_history", f4, (150, 140, 120), anchor="ma")
    img.save(out, quality=95)
    print("card", out)


def build_cards() -> None:
    os.makedirs(CARDS, exist_ok=True)
    card_opening(f"{CARDS}/00_opening.png")
    for e in EPISODES[1:]:
        card_chapter(e["n"], e["chapter"], f"{CARDS}/c{e['n']}.png")
    card_end(f"{CARDS}/99_end.png")


# ------------------------------------------------------------------ الصوت
def measure(path: str, start: float, dur: float) -> dict:
    cmd = [FF, "-hide_banner", "-nostdin", "-ss", f"{start:.3f}", "-t", f"{dur:.3f}",
           "-i", path, "-vn", "-af", f"loudnorm=I={TARGET_I}:TP=-1.5:LRA=11:print_format=json",
           "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    blob = r.stderr[r.stderr.rfind("{"):]
    try:
        return json.JSONDecoder().raw_decode(blob)[0]
    except Exception:
        return {"input_i": "-20.0", "input_tp": "-3.0"}


def gains() -> dict:
    path = f"{WORK}/gains.json"
    if os.path.exists(path):
        return json.load(open(path))
    out = {}
    for e in EPISODES:
        m = measure(f"{DRIVE}/{e['file']}", e["skip"], e["dur"] - e["skip"] - 0.6)
        gain = TARGET_I - float(m["input_i"])       # مطابقة الجهارة فقط
        gain = max(-6.0, min(9.0, gain))            # حماية من القفزات
        out[e["key"]] = {"gain_db": round(gain, 2),
                         "input_i": float(m["input_i"]), "input_tp": float(m["input_tp"])}
        print(f"ep{e['key']}: I={m['input_i']} TP={m['input_tp']} -> gain {gain:+.2f} dB")
    os.makedirs(WORK, exist_ok=True)
    json.dump(out, open(path, "w"), indent=2, ensure_ascii=False)
    return out


# ------------------------------------------------------------------ الترجمة
TIME = re.compile(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)")


def _secs(h, m, s, ms):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def parse_srt(path: str):
    txt = open(path, encoding="utf-8-sig").read().replace("\r", "")
    cues = []
    for block in re.split(r"\n\s*\n", txt.strip()):
        lines = [l for l in block.split("\n") if l.strip()]
        if not lines:
            continue
        ti = next((i for i, l in enumerate(lines) if "-->" in l), None)
        if ti is None:
            continue
        m = TIME.search(lines[ti])
        if not m:
            continue
        g = m.groups()
        cues.append({"s": _secs(*g[:4]), "e": _secs(*g[4:]),
                     "t": " ".join(lines[ti + 1:]).strip()})
    return cues


def _clean(t: str) -> str:
    t = re.sub(r"\s+", " ", t).strip()
    return t


def sentence_merge(cues):
    """يدمج القطع المقطوعة في منتصف الجملة (كابشن آلي) إلى جمل كاملة."""
    out, buf = [], None
    for c in cues:
        t = _clean(c["t"])
        if not t:
            continue
        if buf is None:
            buf = {"s": c["s"], "e": c["e"], "t": t}
        elif c["s"] - buf["e"] <= 0.8 and not re.search(r'[.!?…]["»”)]?$', buf["t"]):
            buf["e"] = c["e"]
            buf["t"] = (buf["t"] + " " + t).strip()
        else:
            out.append(buf)
            buf = {"s": c["s"], "e": c["e"], "t": t}
        # جملة طويلة جدًا تُغلق
        if buf and len(buf["t"]) > 175:
            out.append(buf)
            buf = None
    if buf:
        out.append(buf)
    return out


def wrap2(text: str, width: int = 42, max_lines: int = 2) -> str:
    """سطران كحد أقصى، 42 حرفًا في السطر، وتوازن عند الحاجة."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    if len(lines) <= max_lines:
        return "\n".join(lines)
    n = len(words)
    half = n // 2
    return "\n".join([" ".join(words[:half]), " ".join(words[half:])])


def _split_long(c, max_d: float = 6.5):
    """يقسّم الكابشن الطويل إلى قطع متساوية زمنيًا ونصيًا."""
    s, e, t = c["s"], c["e"], _clean(c["t"])
    dur = e - s
    if dur <= max_d or not t:
        return [{"s": s, "e": e, "t": t}]
    words = t.split()
    n = int(min(len(words), max(1, -(-dur // max_d))))   # ceil
    while n > 1 and len(words) / n < 4:
        n -= 1
    step = dur / n
    per = len(words) / n
    out = []
    for i in range(n):
        a = int(round(i * per))
        b = int(round((i + 1) * per))
        seg = " ".join(words[a:b]).strip()
        if not seg:
            continue
        out.append({"s": s + i * step, "e": s + (i + 1) * step - 0.04, "t": seg})
    return out


def build_srt() -> str:
    """ترجمة إنجليزية واحدة بإزاحات مطابقة للخط الزمني النهائي."""
    os.makedirs(WORK, exist_ok=True)
    t = 0.0
    t += OPEN_D                                         # بطاقة الافتتاح
    timeline = []
    for i, e in enumerate(EPISODES):
        seg_dur = e["dur"] - e["skip"] - e["pad"]        # بطاقة الختام المدمجة تُقصّ
        timeline.append((e, t, seg_dur))
        t += seg_dur
        t += CARD_D if i < len(EPISODES) - 1 else 0.0
    total = t + END_D

    items = []
    for e, t0, seg_dur in timeline:
        src = f"{WORK}/en/en_{e['key']}.srt"
        if not os.path.exists(src):
            continue
        off = t0 - e["skip"]
        tail = e["dur"] - e["pad"] - 0.05               # نهاية المقطع الصالحة
        for c in parse_srt(src):
            for p in _split_long(c):
                s, en = p["s"], p["e"]
                if s >= tail - 0.2 or en <= e["skip"] + 0.05:
                    continue
                s = max(s, e["skip"])
                en = min(en, tail)
                if en - s < 0.8:
                    continue                            # أثر ضئيل عند الفصل
                items.append([s + off, en + off, p["t"]])
    items.sort(key=lambda x: x[0])

    # منع التداخل + الحد الأدنى للمدة
    fixed = []
    for s, en, txt in items:
        if fixed and s < fixed[-1][1] + 0.02:
            s = fixed[-1][1] + 0.02
        if en - s < 0.55:
            en = s + 0.55
        fixed.append([s, en, txt])

    # منع تجاوز بطاقات الفصول والبطاقة الختامية
    def ts(x):
        h = int(x // 3600)
        m = int(x % 3600 // 60)
        s2 = int(x % 60)
        ms = int(round((x - int(x)) * 1000))
        if ms >= 1000:
            s2, ms = s2 + 1, 0
        if s2 >= 60:
            m, s2 = m + 1, s2 - 60
        return f"{h:02d}:{m:02d}:{s2:02d},{ms:03d}"

    out = []
    for i, (s, en, txt) in enumerate(fixed, 1):
        out.append(f"{i}\n{ts(s)} --> {ts(en)}\n{wrap2(txt)}\n")
    path = f"{OUTDIR}/CAPTIONS_EN.srt"
    os.makedirs(OUTDIR, exist_ok=True)
    open(path, "w", encoding="utf-8").write("\n".join(out))
    print(f"SRT: {len(fixed)} cues, total {ts(total)} -> {path}")
    return path


# ------------------------------------------------------------------ الفيديو
PARTS = f"{WORK}/parts"


def _enc_args(video_kbps: int, audio_kbps: int):
    return ["-c:v", "libx264", "-preset", "medium", "-profile:v", "high", "-pix_fmt", "yuv420p",
            "-b:v", f"{video_kbps}k", "-maxrate", f"{int(video_kbps * 1.2)}k",
            "-bufsize", f"{int(video_kbps * 2)}k",
            "-x264-params", "aq-mode=3:deblock=1,1:ref=3:keyint=50:min-keyint=25",
            "-c:a", "aac", "-b:a", f"{audio_kbps}k", "-ac", "2", "-ar", "48000",
            "-r", str(FPS), "-g", "50", "-video_track_timescale", "12800"]


def _run(cmd: list) -> None:
    subprocess.run(cmd, check=True)


def card_clip(png: str, dur: float, out: str, video_kbps: int, audio_kbps: int,
              fade_in: float, fade_out: float) -> str:
    KB = ("zoompan=z='min(1.0+0.00030*on,1.05)':"
          "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=%dx%d:fps=%d" % (W, H, FPS))
    vf = (f"scale={int(W * 1.05)}:{int(H * 1.05)}:flags=lanczos,{KB}")
    if fade_in > 0:
        vf += f",fade=t=in:st=0:d={fade_in}"
    if fade_out > 0:
        vf += f",fade=t=out:st={dur - fade_out:.3f}:d={fade_out}"
    vf += ",format=yuv420p,setsar=1"
    cmd = [FF, "-y", "-hide_banner", "-nostdin", "-loglevel", "error",
           "-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", png,
           "-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anullsrc=r=48000:cl=stereo",
           "-vf", vf, "-af", f"atrim=0:{dur:.3f},asetpts=N/SR/TB",
           *_enc_args(video_kbps, audio_kbps), "-t", f"{dur:.3f}", out]
    _run(cmd)
    return out


def _mix(video: str, wav: str, dur: float, out: str, volume: float,
         fade_in: float, fade_out: float, audio_kbps: int) -> str:
    """يركّب موسيقى على مقطع صامت مع الحفاظ على الفيديو كما هو."""
    af = (f"[1:a]atrim=0:{dur:.3f},asetpts=N/SR/TB,aresample=48000,volume={volume},"
          f"afade=t=in:st=0:d={fade_in},afade=t=out:st={dur - fade_out:.3f}:d={fade_out}[m];"
          f"[0:a][m]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a]")
    cmd = [FF, "-y", "-hide_banner", "-nostdin", "-loglevel", "error",
           "-i", video, "-i", wav, "-filter_complex", af,
           "-map", "0:v", "-map", "[a]", "-c:v", "copy",
           "-c:a", "aac", "-b:a", f"{audio_kbps}k", "-ac", "2", "-ar", "48000",
           "-t", f"{dur:.3f}", out]
    _run(cmd)
    return out


def episode_part(e: dict, out: str, video_kbps: int, audio_kbps: int) -> str:
    start = e["skip"]
    seg = e["dur"] - start - e["pad"]
    g = gains()
    vf = (f"trim={start:.3f}:{start + seg:.3f},setpts=PTS-STARTPTS,fps={FPS},"
          f"scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p,"
          f"fade=t=in:st=0:d={FADE},fade=t=out:st={seg - FADE:.3f}:d={FADE}")
    af = (f"atrim={start:.3f}:{start + seg:.3f},asetpts=N/SR/TB,aresample=48000,"
          f"volume={g[e['key']]['gain_db']}dB,"
          f"alimiter=level_in=1:level_out=1:limit=0.89:attack=4:release=60:level=0,"
          f"afade=t=in:st=0:d={FADE},afade=t=out:st={seg - FADE:.3f}:d={FADE}")
    cmd = [FF, "-y", "-hide_banner", "-nostdin", "-loglevel", "error",
           "-i", f"{DRIVE}/{e['file']}",
           "-filter_complex", f"[0:v]{vf}[v];[0:a]{af}[a]",
           "-map", "[v]", "-map", "[a]", *_enc_args(video_kbps, audio_kbps), out]
    _run(cmd)
    return out


def render(out: str, video_kbps: int = 370, audio_kbps: int = 88) -> str:
    """ينتج المقاطع منفردة ثم يدمجها بلا إعادة ترميز (ذاكرة أقل ودقة أعلى)."""
    os.makedirs(PARTS, exist_ok=True)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    seq = []

    opening = card_clip(f"{CARDS}/00_opening.png", OPEN_D, f"{PARTS}/000_open_silent.mp4",
                        video_kbps, audio_kbps, 0.0, 0.0)
    _mix(opening, f"{WORK}/music_intro.wav", OPEN_D, f"{PARTS}/000_open.mp4",
         volume=0.66, fade_in=0.35, fade_out=1.5, audio_kbps=audio_kbps)
    seq.append(f"{PARTS}/000_open.mp4")

    for i, e in enumerate(EPISODES):
        seq.append(episode_part(e, f"{PARTS}/{100 + i:03d}_ep{e['key']}.mp4",
                                video_kbps, audio_kbps))
        if i < len(EPISODES) - 1:
            cn = e["n"] + 1
            sil = card_clip(f"{CARDS}/c{cn}.png", CARD_D,
                            f"{PARTS}/{200 + i:03d}_card{cn}_silent.mp4",
                            video_kbps, audio_kbps, 0.18, 0.18)
            _mix(sil, f"{WORK}/music_card.wav", CARD_D, f"{PARTS}/{200 + i:03d}_card{cn}.mp4",
                 volume=1.0, fade_in=0.30, fade_out=0.45, audio_kbps=audio_kbps)
            seq.append(f"{PARTS}/{200 + i:03d}_card{cn}.mp4")

    end_silent = card_clip(f"{CARDS}/99_end.png", END_D, f"{PARTS}/900_end_silent.mp4",
                           video_kbps, audio_kbps, 0.3, 0.6)
    _mix(end_silent, f"{WORK}/music_outro.wav", END_D, f"{PARTS}/900_end.mp4",
         volume=0.66, fade_in=0.45, fade_out=1.9, audio_kbps=audio_kbps)
    seq.append(f"{PARTS}/900_end.mp4")

    # دمج
    lst = f"{PARTS}/list.txt"
    with open(lst, "w", encoding="utf-8") as f:
        for s in seq:
            f.write(f"file '{s}'\n")
    cmd = [FF, "-y", "-hide_banner", "-nostdin", "-loglevel", "error",
           "-f", "concat", "-safe", "0", "-i", lst,
           "-c", "copy", "-movflags", "+faststart", out]
    _run(cmd)
    print("DONE", out, os.path.getsize(out) // 1024 // 1024, "MB")
    return out


def make_music() -> None:
    sys.path.insert(0, os.path.join(REPO, "scripts", "series"))
    import music as M
    os.makedirs(WORK, exist_ok=True)
    M.write_wav(f"{WORK}/music_intro.wav", M.intro(5.5))
    M.write_wav(f"{WORK}/music_outro.wav", M.outro(8.0))
    M.write_wav(f"{WORK}/music_card.wav", M.bed(3.2, dbfs=-33.0))
    print("music ok")


def timeline():
    t = OPEN_D
    rows = [(0.0, "الافتتاح")]
    for i, e in enumerate(EPISODES):
        seg = e["dur"] - e["skip"] - e["pad"]
        rows.append((t, e["chapter"]))
        t += seg
        if i < len(EPISODES) - 1:
            t += CARD_D
    rows.append((t, "الخاتمة"))
    return rows, t + END_D


def chapters() -> None:
    def mm(s):
        return f"{int(s // 60):02d}:{int(s % 60):02d}"
    rows, total = timeline()
    path = f"{WORK}/chapters.txt"
    os.makedirs(WORK, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for s, name in rows:
            line = f"{mm(s)}  {name}"
            print(line)
            f.write(line + "\n")
        print(f"TOTAL  {mm(total)}  ({total:.2f}s)")
        f.write(f"TOTAL  {mm(total)}\n")
    print("->", path)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("cards", "all"):
        build_cards()
    if cmd in ("music", "all"):
        make_music()
    if cmd in ("srt", "all"):
        build_srt()
    if cmd in ("gains", "all"):
        gains()
    if cmd in ("chapters",):
        chapters()
    if cmd in ("render", "all"):
        out = sys.argv[2] if len(sys.argv) > 2 else f"{OUTDIR}/MASTER_COMPILED.mp4"
        render(out)
        print("DONE", out)
