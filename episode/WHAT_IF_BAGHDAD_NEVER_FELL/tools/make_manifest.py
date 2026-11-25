#!/usr/bin/env python3
"""make_manifest.py — يكتب exports/<EP>/publish/manifest.json من الملفات الفعلية + قياسات qa.py.
الحالة دائمًا READY_FOR_REVIEW (لا نشر بدون موافقة البوابة 2)."""
import datetime, glob, hashlib, json, os

HERE = os.path.dirname(os.path.abspath(__file__)); EPDIR = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(EPDIR, "..", ".."))
EP = "WHAT_IF_BAGHDAD_NEVER_FELL"
EX = os.path.join(ROOT, "exports", EP)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def entry(p, media):
    rel = os.path.relpath(p, ROOT)
    e = {"path": rel, "bytes": os.path.getsize(p), "sha256": sha(p)}
    m = media.get(os.path.basename(p))
    if m:
        e.update({"duration_s": m["dur"], "resolution": f'{m["w"]}x{m["h"]}', "fps": m["fps"], "video_codec": m["vcodec"],
                  "pix_fmt": m["pix"], "audio": f'{m["acodec"]} {m["ahz"]} Hz', "loudness_lufs": m["I"], "true_peak_dbtp": m["TP"], "lra_lu": m["LRA"]})
    return e


def main():
    mp = os.path.join(EX, "tmp", "qa_media.json")
    media = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {}
    groups = {
        "video": sorted(p for p in glob.glob(os.path.join(EX, "video", "*.mp4")) if not os.path.basename(p).startswith("_")),
        "video_parts_for_drive": sorted(glob.glob(os.path.join(EX, "video", "parts", "*.mp4"))),
        "thumbnails": sorted(glob.glob(os.path.join(EX, "publish", "thumbnails", "*.png"))),
        "subtitles": sorted(glob.glob(os.path.join(EX, "publish", "subtitles", "*.srt"))),
        "publish_text": sorted(glob.glob(os.path.join(EX, "publish", "*.txt"))),
        "audio_stems": sorted(glob.glob(os.path.join(EX, "audio", "*.wav"))),
        "episode_docs": [os.path.join(EPDIR, f) for f in ("research.md", "sources.md", "script.md", "style_brief.json", "FACT_CHECK.csv",
                                                       "credits.csv", "music_license.md", "visual_prompts.md", "timestamps.json", "qa_report.md")
                         if os.path.exists(os.path.join(EPDIR, f))],
    }
    man = {
        "episode_id": EP,
        "series": "ماذا لو؟",
        "channel": "رواق | قصص الأفكار والتحولات الكبرى",
        "status": "READY_FOR_REVIEW",
        "published": False,
        "gate": "G2 — بانتظار موافقة المالك (لا رفع/نشر قبلها)",
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
        "content_label": "historical fiction / alternate history — fiction ranges permanently labelled on screen",
        "fiction_ranges_s": {"long": [[261.13, 490.679], [513.217, 530.896]], "short": [[18.0, 47.145]]},
        "voice": {"provider": "Arena platform TTS (voice-01)", "tag": "DRAFT_VO", "note": "synthetic voice — not an official/recorded narrator"},
        "music": {"source": "ORIGINAL procedural (Hijaz on D)", "youtube_audio_library": "BLOCKED (login-gated) — swap via tools/mux_only.sh",
                  "register": "episode/WHAT_IF_BAGHDAD_NEVER_FELL/music_license.md"},
        "visuals": {"ai_generated": 10, "public_domain_archival": 4, "credits": "episode/WHAT_IF_BAGHDAD_NEVER_FELL/credits.csv",
                    "label_on_screen": "إعادة تصوّر (AI) / سطر مصدر (أرشيف)"},
        "youtube_settings": {"altered_or_synthetic_content": "YES (AI visuals + synthetic voice + alternate history)",
                             "made_for_kids": False, "captions_burned_in": {"long": False, "short": True},
                             "upload_subtitles": ["subtitles_ar.srt (ar)", "subtitles_en.srt (en — needs human review)"]},
        "drive": {"episode_folder_id": "1iHMuisq4IhRK65jVLYQelc_guz3Ed4U8", "video_folder_id": "1AHaq-oW8YvnI4wSmMfBZBV5twqMRpF3c",
                  "publish_folder_id": "1XBpvcusShuDRKgDS5hjGwXil8Cdvz4lE",
                  "note": "long masters >100 MB (connector cap) → uploaded as 4 lossless stream-copy parts each; re-join per video/JOIN_README.txt (decoded frames verified identical)"},
        "files": {k: [entry(p, media) for p in v] for k, v in groups.items()},
    }
    out = os.path.join(EX, "publish", "manifest.json")
    json.dump(man, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(out, sum(len(v) for v in man["files"].values()), "files")


if __name__ == "__main__":
    main()
