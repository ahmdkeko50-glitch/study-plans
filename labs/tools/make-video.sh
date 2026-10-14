#!/usr/bin/env bash
# One command: record a lesson's guided demo in high quality, encode it, and embed it in a COPY of the 3D lesson.
#   bash make-video.sh ../L1-4-dielectric.html ../L1-4-with-video.html [work-dir] [narration.json voice-dir]
# With narration.json + voice-dir (an unpacked sherpa-onnx Piper voice), an offline spoken narration is added;
# with a recorded-voice narration.json (has "audio" + "segments", e.g. ../voiceover/L1-4.sufyan.json) pass "-" as voice-dir.
# The original lesson file is not changed. Also leaves an .mp4 next to the output (for Telegram / YouTube).
set -euo pipefail
SRC="$1"; OUT="$2"; WORK="${3:-$(mktemp -d)}"; NAR="${4:-}"; VOICE="${5:-}"
HERE="$(cd "$(dirname "$0")" && pwd)"
FPS=24
# 1024×576 layout rendered at 1.875× = 1920×1080 frames (sharp edges and labels)
[ -f "$WORK/frames/timeline.json" ] || node "$HERE/record-demo.js" "$SRC" "$WORK/frames" 1024 576 $FPS 1 1.875
# downscale 1080p → 720p (supersampled = crisp), H.264 main profile + faststart: plays on every phone with hardware decoding
FR="$WORK/frames"; AUDIO=()
if [ -n "$NAR" ]; then   # spoken narration: holds the picture where a line needs more time, shifts the timeline
  python3 "$HERE/voiceover.py" "$WORK/frames" "$NAR" "$VOICE" "$WORK/vo"; FR="$WORK/vo"
  AUDIO=(-i "$WORK/vo/narration.wav" -c:a aac -b:a 64k -ac 1 -ar 44100 -shortest)
fi
ffmpeg -y -loglevel error -framerate $FPS -i "$( [ -n "$NAR" ] && echo "$FR/frames" || echo "$FR")/f%05d.jpg" "${AUDIO[@]:0:2}" -vf "scale=1280:720:flags=lanczos" \
  "${AUDIO[@]:2}" -c:v libx264 -profile:v main -level 3.1 -preset slow -tune animation -crf 26 -pix_fmt yuv420p -movflags +faststart $([ -z "$NAR" ] && echo -an) "$WORK/video.mp4"
ffmpeg -y -loglevel error -ss 2 -i "$WORK/video.mp4" -frames:v 1 -q:v 3 "$WORK/poster.jpg"
python3 "$HERE/embed-video.py" "$SRC" "$WORK/video.mp4" "$WORK/poster.jpg" "$FR/timeline.json" "$OUT"
cp "$WORK/video.mp4" "${OUT%.html}.mp4"
echo "done: $OUT  +  ${OUT%.html}.mp4  (work files in $WORK)"
