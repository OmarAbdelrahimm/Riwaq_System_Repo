#!/usr/bin/env bash
# يهيّئ أدوات السلسلة (ffmpeg مع libass + PIL + تشكيل عربي) داخل جلسة معزولة.
# الاستخدام:  source scripts/series/env.sh
set -e
if ! python3 -c "import PIL, arabic_reshaper, bidi, imageio_ffmpeg" >/dev/null 2>&1; then
  echo "[env] installing python deps ..." >&2
  python3 -m pip install -q --break-system-packages --no-input \
    pillow numpy arabic-reshaper python-bidi imageio-ffmpeg 2>&1 | tail -2 || true
fi
export FFMPEG="$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')"
export FFPROBE="${FFMPEG%ffmpeg*}ffprobe"
ln -sf "$FFMPEG" /usr/local/bin/ffmpeg 2>/dev/null || true
echo "[env] ffmpeg = $FFMPEG" >&2
"$FFMPEG" -hide_banner -filters 2>/dev/null | grep -c ' ass ' >&2 || true
