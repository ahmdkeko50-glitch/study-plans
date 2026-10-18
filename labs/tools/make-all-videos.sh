#!/usr/bin/env bash
# Builds labs/<L>-with-video.html for every lesson that does not have one yet (silent video inside the 3D lesson).
#   cd labs/tools && bash make-all-videos.sh            # all missing lessons
#   bash make-all-videos.sh L2-3 L5-7                   # only these
#   FORCE=1 bash make-all-videos.sh                     # rebuild even the ones that exist
# Uses the graphics card (GPU=1, a browser window opens for each lesson — leave it alone).
# Work files go to labs/tools/work/<L>/ and are deleted after each lesson (KEEP=1 keeps them).
set -uo pipefail
cd "$(dirname "$0")"
export GPU="${GPU-1}"
LIST=("$@")
if [ ${#LIST[@]} -eq 0 ]; then
  for f in ../L*.html; do b=$(basename "$f" .html)
    case "$b" in *-with-video|L1-4-dielectric) continue;; esac
    LIST+=("$b"); done
fi
ok=0; skip=0; fail=()
for L in "${LIST[@]}"; do
  if [ -f "../$L-with-video.html" ] && [ -z "${FORCE:-}" ]; then skip=$((skip+1)); continue; fi
  echo "=== $L  ($(date +%H:%M))"
  t0=$(date +%s)
  if bash make-video.sh "../$L.html" "../$L-with-video.html" "work/$L"; then
    ok=$((ok+1)); echo "    ✓ $L in $(( ($(date +%s)-t0)/60 )) min"
    [ -n "${KEEP:-}" ] || rm -rf "work/$L"
  else fail+=("$L"); echo "    ✗ $L failed (work files kept in work/$L)"; fi
done
echo "built $ok, already done $skip, failed ${#fail[@]} ${fail[*]:-}"
