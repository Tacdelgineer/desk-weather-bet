#!/usr/bin/env bash
# tools/build_all.sh -> every chapter (2 at a time), then the master and the Shorts. Resumable: a chapter whose MP4 is
# newer than its page, scenes, voice, data, the shared styles and the mix/compose tools is skipped. Run it detached,
# with PATH passed in (systemd's PATH has no uv), under the project's name prefix:
#   systemd-run --user --unit=<prefix>-render --working-directory=$PWD -p Environment=PATH=$PATH tools/build_all.sh
#   journalctl --user -u <prefix>-render -n 5      (or tail logs/build_NN.log)
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs work
echo $$ > work/render.pid
PY=${PY:-"uv run -q --no-project --with numpy --with scipy --with pillow python"}
stale() {   # 0 (true) when chapter $1 needs a build
  local page out; page=$(ls chapters/${1}_*.html | head -1); out=results/final/chapters/$(basename "$page" .html).mp4
  [ ! -f "$out" ] && return 0
  for f in "$page" chapters/${1}_scenes.js chapters/common.js chapters/data.js voice/${1}.wav styles/*.js tools/compose.py tools/sfx.py; do [ "$f" -nt "$out" ] && return 0; done
  return 1
}
todo=(); for i in $(python3 -c "import sys; sys.path.insert(0, 'tools'); import kit; print(' '.join(sorted(kit.chapters())))"); do stale "$i" && todo+=("$i"); done
echo "$(date +%T) to build: ${todo[*]:-none}"
printf '%s\n' "${todo[@]}" | xargs -r -P 2 -I{} sh -c 'tools/build.sh {} > logs/build_{}.log 2>&1 && tail -1 logs/build_{}.log || { echo "FAILED {} (logs/build_{}.log)"; exit 255; }'
python3 tools/master.py
[ -f chapters/shorts.json ] && $PY tools/shorts.py
python3 tools/stills.py | tail -1
echo "$(date +%T) RENDER DONE"
