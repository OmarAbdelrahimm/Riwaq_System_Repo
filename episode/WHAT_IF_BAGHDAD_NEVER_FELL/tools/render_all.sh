#!/usr/bin/env bash
# render_all.sh — يرندر الفيديو صامتًا (Remotion) ثم يدمج المكساجات الصوتية (ffmpeg) لكل نسخة.
set -euo pipefail
cd "$(dirname "$0")/../../.."
EP=WHAT_IF_BAGHDAD_NEVER_FELL
V=exports/$EP/video; A=exports/$EP/audio
export LD_LIBRARY_PATH=/tmp/al/lib:/tmp
FF=${FFMPEG:-/tmp/ffmpeg}
what=${1:-all}
R="npx remotion render src/index.ts Episode --browser-executable=/tmp/chromium --gl=swiftshader --muted --codec=h264 --crf=18 --pixel-format=yuv420p --concurrency=2 --log=info"
mux () { # video audio out
  $FF -y -hide_banner -loglevel error -i "$1" -i "$2" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 320k -ar 48000 -ac 2 -movflags +faststart -shortest "$3"
  echo "muxed $3"
}
if [[ $what == all || $what == short ]]; then
  $R --props=_build/tmp/props_short.json $V/_short_video_only.mp4
  mux $V/_short_video_only.mp4 $A/mix_master_short.wav $V/short_v1.mp4
  mux $V/_short_video_only.mp4 $A/mix_no_voice_short.wav $V/short_v1_no_voice.mp4
  mux $V/_short_video_only.mp4 $A/mix_sfx_only_short.wav $V/short_v1_sfx_only.mp4
fi
if [[ $what == all || $what == long ]]; then
  $R --props=_build/tmp/props.json $V/_master_video_only.mp4
  mux $V/_master_video_only.mp4 $A/mix_master.wav $V/master.mp4
  mux $V/_master_video_only.mp4 $A/mix_no_voice.wav $V/master_no_voice.mp4
  mux $V/_master_video_only.mp4 $A/mix_sfx_only.wav $V/master_sfx_only.mp4
fi
echo RENDER_ALL_DONE
