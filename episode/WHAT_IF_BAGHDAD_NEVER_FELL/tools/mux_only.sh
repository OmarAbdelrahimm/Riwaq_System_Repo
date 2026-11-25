#!/usr/bin/env bash
# mux_only.sh — يعيد دمج الصوت فقط على الفيديو المرندر (بلا إعادة ريندر) — مثلًا بعد تغيير الموسيقى.
set -euo pipefail
cd "$(dirname "$0")/../../.."
EP=WHAT_IF_BAGHDAD_NEVER_FELL; V=exports/$EP/video; A=exports/$EP/audio; FF=${FFMPEG:-/tmp/ffmpeg}
mux () { $FF -y -hide_banner -loglevel error -i "$1" -i "$2" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 320k -ar 48000 -ac 2 -movflags +faststart -shortest "$3"; echo "muxed $3"; }
[[ -f $V/_short_video_only.mp4 ]] && { mux $V/_short_video_only.mp4 $A/mix_master_short.wav $V/short_v1.mp4; mux $V/_short_video_only.mp4 $A/mix_no_voice_short.wav $V/short_v1_no_voice.mp4; mux $V/_short_video_only.mp4 $A/mix_sfx_only_short.wav $V/short_v1_sfx_only.mp4; }
[[ -f $V/_master_video_only.mp4 ]] && { mux $V/_master_video_only.mp4 $A/mix_master.wav $V/master.mp4; mux $V/_master_video_only.mp4 $A/mix_no_voice.wav $V/master_no_voice.mp4; mux $V/_master_video_only.mp4 $A/mix_sfx_only.wav $V/master_sfx_only.mp4; }
echo MUX_DONE
