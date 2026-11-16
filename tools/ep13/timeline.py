"""Audio-locked timeline for the 0-6 s proof.

Authority: the original S01 take, ``public/ep13/audio/chapter01.mp3``
(sha256 83be0fd3…, byte-identical to the user-selected take referenced by the
handoff). Phrase boundaries are MEASURED from that file by
``tools/ep13/audio_analysis.py`` — see ``episode/ep13/measured_audio.json``.

Word-level sync is NOT claimed. A native Arabic listen is still required; the
Arabic strings below are the director's editorial cues, marked as such.
"""

from __future__ import annotations

FPS = 30
FRAMES = 180          # 6.0 s
WIDTH, HEIGHT = 1280, 720   # review size; design space is 1920x1080

# Measured speech runs (seconds) -> frames
PHRASES = {
    "P1": {"onset": 0.12, "offset": 1.66, "cue": "إوعى تشرب لبن بعد السمك", "verified": "ONSET_MEASURED"},
    "P2": {"onset": 2.08, "offset": 2.78, "cue": "هيجيلك بهاق؟", "verified": "ONSET_MEASURED"},
    "P3": {"onset": 3.24, "offset": 5.04, "cue": "الجملة دي غالبًا سمعتها قبل كده", "verified": "ONSET_MEASURED"},
    "P4": {"onset": 5.46, "offset": 6.00, "cue": "(next sentence begins)", "verified": "ONSET_MEASURED"},
}
for p in PHRASES.values():
    p["onset_f"] = round(p["onset"] * FPS)
    p["offset_f"] = round(p["offset"] * FPS)

# Headline words in reading order; exactly one gold stress word.
HEADLINE = [("إوعى", "parchment"), ("تشرب", "parchment"), ("لبن", "gold"),
            ("بعد", "parchment"), ("السمك", "parchment")]
KICKER = "ادعاء متوارث"
MICRO = "وليس حقيقة مثبتة"
CLAIM = [("هيجيلك", "parchment"), ("بهاق؟", "gold")]
CLAIM_LABEL = "قول شعبي متكرر"
CLAIM_FOOTER = "بلا مصدر طبي"
REPEAT_KICKER = "الجملة دي غالبًا"
REPEAT_TITLE = [("سمعتها", "parchment"), ("قبل", "gold"), ("كده", "parchment")]
EVIDENCE_LABEL = "بطاقة دليل"
EVIDENCE_TITLE = "المصدر قيد التحقق"
EVIDENCE_NOTE = "لا نعرض مصدرًا غير موثّق"

# Scene boundaries (frames). S1/S2 follow the measured phrase onsets.
S1 = (0, 54)
S2 = (54, 91)
S3 = (91, FRAMES)

# Key beats, all expressed in frames so nothing depends on wall-clock time.
BEATS = {
    "occluder_clear": 22,
    "fish_enter": (0, 20),
    "glass_enter": (5, 30),
    "type_in": (4, 34),          # P1 words stagger inside the measured phrase
    "arc_draw": (28, 46),
    "arc_break": (56, 76),
    "question_draw": (58, 78),
    "claim_card": (64, 78),
    "heroes_dim": (92, 120),
    "repeat_text": (97, 109),
    "echo_1": 100,
    "echo_2": 112,
    "evidence_enter": (164, 179),
}
