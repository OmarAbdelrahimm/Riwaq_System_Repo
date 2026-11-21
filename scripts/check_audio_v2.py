#!/usr/bin/env python3
"""
check_audio_v2.py — بوابة الصوت V2
تتأكد إن المكس المدمج موجود وسليم قبل أي رندر،
وإن الصوت القديم (8kHz) مش هو اللي هيطلع.
"""
import sys, os, wave

MIX = "public/projects/TMB_001/audio/MIX_V2_full.mp4"
MIN_BYTES = 5_000_000
EXPECT_S = 288.3


def fail(msg):
    print(f"❌ {msg}")
    sys.exit(1)


def main():
    print("── بوابة الصوت V2 ──")

    if not os.path.exists(MIX):
        fail("المكس V2 مش موجود — الرندر هيطلع بصوت V1 القديم")

    size = os.path.getsize(MIX)
    print(f"  الحجم: {size/1024/1024:.1f} MB")
    if size < MIN_BYTES:
        fail(f"الملف صغير أوي — متوقع > {MIN_BYTES/1024/1024:.0f} MB")

    # AAC داخل mp4 — نستخدم ffprobe من Remotion
    import subprocess, json
    probe = "node_modules/@remotion/compositor-linux-x64-gnu/ffprobe"
    out = subprocess.run([probe, "-v", "quiet", "-print_format", "json",
                          "-show_streams", "-show_format", MIX],
                         capture_output=True, text=True).stdout
    info = json.loads(out)
    st = [x for x in info["streams"] if x["codec_type"] == "audio"][0]
    ch = st["channels"]; sr = int(st["sample_rate"])
    dur = float(info["format"]["duration"])
    print(f"  {ch} قناة · {sr} Hz · {st['codec_name']} · {dur:.1f}s")

    if ch != 2:
        fail(f"المكس لازم ستيريو، لقيت {ch} قناة")
    if sr < 24000:
        fail(f"معدل العينات منخفض ({sr} Hz) — الجودة هتضيع")
    if abs(dur - EXPECT_S) > 2.0:
        fail(f"المدة غلط: {dur:.1f}s (المتوقع {EXPECT_S}s)")

    # اتأكد إن الصوت القديم مش مستخدم في الكومبوزيشن
    lf = "src/compositions/longform/Longform.tsx"
    if os.path.exists(lf):
        import re
        src = open(lf, encoding="utf-8").read()
        # نفحص عناصر <Audio> الفعلية بس — التعليقات مش مهمة
        audio_srcs = re.findall(r'<Audio\s+src=\{staticFile\("([^"]+)"\)\}', src)
        print(f"  ملفات الصوت في Longform: {audio_srcs}")
        if not audio_srcs:
            fail("مفيش أي <Audio> في Longform.tsx")
        if len(audio_srcs) != 1:
            fail(f"متوقع <Audio> واحد بس (المكس)، لقيت {len(audio_srcs)}")
        if audio_srcs[0] != "projects/TMB_001/audio/MIX_V2_full.mp4":
            fail(f"Longform.tsx بيربط ملف غلط: {audio_srcs[0]}")
        print("  ✅ Longform.tsx بيربط المكس V2 بس")

    print("✅ بوابة الصوت V2 سليمة")
    return 0


if __name__ == "__main__":
    sys.exit(main())
