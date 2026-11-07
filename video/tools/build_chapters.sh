#!/usr/bin/env bash
# Render every chapter (tools/build.sh), two at a time, logging to logs/build_NN.log; resumable (skips chapters whose
# mp4 is newer than their page). Then the master.
set -uo pipefail
cd "$(dirname "$0")/.."
NS=$(python3 -c "import sys;sys.path.insert(0,'tools');import kit;print(' '.join(sorted(kit.chapters())))")
run() { n=$1; page=$(ls chapters/${n}_*.html | head -1); out=results/final/chapters/$(basename "$page" .html).mp4
  if [ -f "$out" ] && [ "$out" -nt "$page" ]; then echo "skip $n"; return; fi
  bash tools/build.sh "$n" > logs/build_$n.log 2>&1 && echo "OK $n" || echo "FAIL $n"; }
for n in $NS; do run "$n" & while [ "$(jobs -r | wc -l)" -ge 2 ]; do sleep 2; done; done; wait
echo "ALL CHAPTERS DONE"
