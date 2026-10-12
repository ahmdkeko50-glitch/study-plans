#!/usr/bin/env bash
# One command: record a lesson's guided demo in high quality, encode it, and embed it in a COPY of the 3D lesson.
#   bash make-video.sh ../L1-4-dielectric.html ../L1-4-with-video.html [work-dir]
# The original lesson file is not changed. Also leaves an .mp4 next to the output (for Telegram / YouTube).
set -euo pipefail
SRC="$1"; OUT="$2"; WORK="${3:-$(mktemp -d)}"
HERE="$(cd "$(dirname "$0")" && pwd)"
FPS=24
# 1024×576 layout rendered at 1.875× = 1920×1080 frames (sharp edges and labels)
node "$HERE/record-demo.js" "$SRC" "$WORK/frames" 1024 576 $FPS 1 1.875
# downscale 1080p → 720p (supersampled = crisp), H.264 main profile + faststart: plays on every phone with hardware decoding
ffmpeg -y -loglevel error -framerate $FPS -i "$WORK/frames/f%05d.jpg" -vf "scale=1280:720:flags=lanczos" \
  -c:v libx264 -profile:v main -level 3.1 -preset slow -tune animation -crf 26 -pix_fmt yuv420p -movflags +faststart -an "$WORK/video.mp4"
ffmpeg -y -loglevel error -ss 2 -i "$WORK/video.mp4" -frames:v 1 -q:v 3 "$WORK/poster.jpg"
python3 "$HERE/embed-video.py" "$SRC" "$WORK/video.mp4" "$WORK/poster.jpg" "$WORK/frames/timeline.json" "$OUT"
cp "$WORK/video.mp4" "${OUT%.html}.mp4"
echo "done: $OUT  +  ${OUT%.html}.mp4  (work files in $WORK)"
