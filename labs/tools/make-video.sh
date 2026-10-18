#!/usr/bin/env bash
# One command: record every experiment's guided demo in high quality, narrate, encode, and embed all of them in a COPY
# of the 3D lesson (the original lesson file is not changed).
#
#   bash make-video.sh <lesson.html> <out.html> [work-dir] [voice] [narration-dir]
#
#   voice          an unpacked sherpa-onnx Piper voice folder (offline TTS), or "-" for recorded takes, or empty = silent
#   narration-dir  folder with one narration file per experiment: <CODE>-<tab>.json (CODE = lesson file name, e.g. L2-3-0.json)
#                  default: ../voiceover next to this script. Missing file for a tab → that video is silent.
# Legacy (one experiment): bash make-video.sh <lesson> <out> <work> <narration.json> <voice|->
# Recording runs once per tab; frames are kept in <work>/<tab>/frames and reused on the next run.
# Set MP4=1 to also leave <out>-<tab>.mp4 copies.
set -euo pipefail
SRC="$1"; OUT="$2"; WORK="${3:-$(mktemp -d)}"; A4="${4:-}"; A5="${5:-}"
HERE="$(cd "$(dirname "$0")" && pwd)"
FPS="${FPS:-20}"; DPR="${DPR:-1.5}"   # 1024×576 layout × 1.5 = 1536×864 frames, downscaled to 720p (supersampled)
CODE="$(basename "$SRC" .html)"
if [[ "$A4" == *.json ]]; then LEGACY="$A4"; VOICE="$A5"; NARDIR=""; else LEGACY=""; VOICE="$A4"; NARDIR="${A5:-$HERE/../voiceover}"; fi
NT=$(grep -q '"only": [0-9]' "$SRC" && echo 1 || grep -c 'ctx.demo(' "$SRC")   # one-experiment builds show a single tab
ITEMS=()
for ((t = 0; t < NT; t++)); do
  W="$WORK/$t"; mkdir -p "$W"
  [ "$NT" = 1 ] && [ -f "$WORK/frames/timeline.json" ] && [ ! -e "$W/frames" ] && ln -s "$WORK/frames" "$W/frames"   # old single-tab layout
  [ -f "$W/frames/timeline.json" ] || NOAA=1 node "$HERE/record-demo.js" "$SRC" "$W/frames" 1024 576 $FPS 1 "$DPR" $t
  NAR=""; if [ -n "$LEGACY" ]; then NAR="$LEGACY"; elif [ -n "$VOICE" ] && [ -f "$NARDIR/$CODE-$t.json" ]; then NAR="$NARDIR/$CODE-$t.json"; fi
  RATE=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['fps'])" "$W/frames/timeline.json")   # the recording's own frame rate
  FR="$W/frames"; IN="$W/frames"; AUD=(); AENC=(-an)
  if [ -n "$NAR" ]; then   # spoken narration: holds the picture where a line needs more time, shifts the timeline
    python3 "$HERE/voiceover.py" "$W/frames" "$NAR" "${VOICE:--}" "$W/vo"; FR="$W/vo"; IN="$W/vo/frames"
    AUD=(-i "$W/vo/narration.wav"); AENC=(-c:a aac -b:a 64k -ac 1 -ar 44100 -shortest)
  fi
  # H.264 main profile + faststart: hardware decoding on every phone; lanczos downscale = crisp labels
  ffmpeg -y -loglevel error -framerate $RATE -i "$IN/f%05d.jpg" "${AUD[@]}" -vf "scale=1280:720:flags=lanczos" \
    -c:v libx264 -profile:v main -level 3.1 -preset slow -tune animation -crf 26 -pix_fmt yuv420p -movflags +faststart \
    "${AENC[@]}" "$W/video.mp4"
  ffmpeg -y -loglevel error -ss 2 -i "$W/video.mp4" -frames:v 1 -q:v 3 "$W/poster.jpg"
  ITEMS+=("$FR/timeline.json:$W/video.mp4:$W/poster.jpg")
  [ -n "${MP4:-}" ] && cp "$W/video.mp4" "${OUT%.html}-$t.mp4"
done
python3 "$HERE/embed-video.py" "$SRC" "$OUT" "${ITEMS[@]}"
echo "done: $OUT  (work files in $WORK)"
