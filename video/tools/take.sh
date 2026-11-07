#!/usr/bin/env bash
# tools/take.sh <audio>  -> a take that didn't come from voice_ch.py becomes chapter NN's voice, and NN is rebuilt.
# The file name must start with the chapter number (03_web_take.wav). Word timings come from tools/align.py (local,
# no credits) against voice/text/NN.txt (python3 tools/voice_ch.py --text-only NN writes it). The previous take is
# kept in voice/raw/old/. Prints the matched-word count: a low one means a swallowed or wrong word.
set -euo pipefail
cd "$(dirname "$0")/.."
F=$1; N=$(basename "$F" | cut -c1-2)
[[ $N =~ ^[0-9][0-9]$ ]] || { echo "name must start with NN_: $F"; exit 2; }
[ -f voice/text/$N.txt ] || python3 tools/voice_ch.py --text-only $N
mkdir -p voice/raw/old
STAMP=$(date +%Y%m%d-%H%M%S)
for x in mp3 words.json; do [ -f voice/raw/$N.$x ] && mv voice/raw/$N.$x voice/raw/old/$N.$STAMP.$x; done
ffmpeg -v error -y -i "$F" -ar 44100 -ac 1 -b:a 192k voice/raw/$N.mp3
python3 tools/align.py voice/raw/$N.mp3 voice/text/$N.txt voice/raw/$N.words.json
python3 tools/mute.py $N
python3 tools/mkpage.py $N
tools/build.sh $N
