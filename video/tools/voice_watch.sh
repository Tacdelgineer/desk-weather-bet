#!/usr/bin/env bash
# tools/voice_watch.sh [hours=48] -> watches voice/drop/ for takes named NN_anything.wav|mp3|m4a and runs
# tools/take.sh on each new one (new = no .done or .failed marker newer than the file). Waits until the file has
# stopped growing, so a copy in progress is never picked up. Run it detached, PATH passed in:
#   systemd-run --user --unit=<prefix>-voice-watch --working-directory=$PWD -p Environment=PATH=$PATH tools/voice_watch.sh
# Stop: systemctl --user stop <prefix>-voice-watch      Log: logs/voice_watch.log
# A failed take leaves voice/drop/<file>.failed; copying the file in again retries it.
cd "$(dirname "$0")/.."; mkdir -p voice/drop logs; LOG=logs/voice_watch.log
END=$(( $(date +%s) + ${1:-48} * 3600 ))
echo "$(date '+%F %T') watching voice/drop/" >> $LOG
while [ $(date +%s) -lt $END ]; do
  for f in voice/drop/[0-9][0-9]*.wav voice/drop/[0-9][0-9]*.mp3 voice/drop/[0-9][0-9]*.m4a; do
    [ -e "$f" ] || continue
    [ -e "$f.done" ] && [ "$f.done" -nt "$f" ] && continue
    [ -e "$f.failed" ] && [ "$f.failed" -nt "$f" ] && continue
    s1=$(stat -c %s "$f"); sleep 5; [ "$s1" = "$(stat -c %s "$f")" ] || continue      # still being copied
    echo "$(date '+%F %T') take $f" >> $LOG
    if tools/take.sh "$f" >> $LOG 2>&1; then touch "$f.done"; echo "$(date '+%F %T') done $f" >> $LOG
    else touch "$f.failed"; echo "$(date '+%F %T') FAILED $f" >> $LOG; fi
  done
  sleep 30
done
