#!/usr/bin/env bash
# One command: record a lesson's guided demo, encode it, and build its «video edition» HTML.
#   bash make-video.sh ../L1-4-dielectric.html ../L1-4-video.html [work-dir]
# Produces: the video edition (single file, video embedded), and next to it an .mp4 copy (for Telegram / YouTube).
set -euo pipefail
SRC="$1"; OUT="$2"; WORK="${3:-$(mktemp -d)}"
HERE="$(cd "$(dirname "$0")" && pwd)"
FPS=24
node "$HERE/record-demo.js" "$SRC" "$WORK/frames" 960 540 $FPS 1
# H.264 main profile + faststart: plays on every phone browser (Android / iPhone) with hardware decoding
ffmpeg -y -loglevel error -framerate $FPS -i "$WORK/frames/f%05d.jpg" -c:v libx264 -profile:v main -level 3.1 -preset slow -crf 27 \
  -pix_fmt yuv420p -movflags +faststart -an "$WORK/video.mp4"
cp "$WORK/frames/f$(printf %05d $((FPS*2)))".jpg "$WORK/poster.jpg"
python3 "$HERE/make-video-page.py" "$SRC" "$WORK/video.mp4" "$WORK/poster.jpg" "$WORK/frames/timeline.json" "$OUT"
cp "$WORK/video.mp4" "${OUT%.html}.mp4"
echo "done: $OUT  +  ${OUT%.html}.mp4  (work files in $WORK)"
