#!/usr/bin/env bash
# tools/build.sh NN  -> results/final/chapters/NN_name.mp4  (render frames, mix voice + sfx, lay clips, loudnorm)
# PY: the python that has numpy + scipy (default: a throwaway uv environment). TACDEL_SKILLS: see tools/kit.py.
set -euo pipefail
cd "$(dirname "$0")/.."
N=$1; PAGE=$(ls chapters/${N}_*.html | head -1); NAME=$(basename "$PAGE" .html)
SKILLS=${TACDEL_SKILLS:-$HOME/ai-dev-skills/skills}
export NODE_PATH=${NODE_PATH:-$(dirname "$SKILLS")/node_modules}
PY=${PY:-"uv run -q --no-project --with numpy --with scipy python"}
mkdir -p work/render work/audio results/final/chapters logs
$PY tools/sfx.py "$PAGE" voice/$N.wav work/audio/${N}_mix.wav work/audio/${N}_meta.json
DUR=$(python3 -c "import json;print(json.load(open('work/audio/${N}_meta.json'))['DUR'])")
node "$SKILLS/tacdel-shorts/tools/render.cjs" "$PAGE" work/render/${N}_raw.mp4 "$DUR" -
python3 tools/compose.py work/render/${N}_raw.mp4 work/audio/${N}_mix.wav work/audio/${N}_meta.json chapters results/final/chapters/$NAME.mp4
echo "BUILD OK $N $(date +%T)"
