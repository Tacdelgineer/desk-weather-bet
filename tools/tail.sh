#!/usr/bin/env bash
# usage: tools/tail.sh <log> [n]  — tail a log without progress-bar noise
tr '\r' '\n' < "$1" | grep -v -E '[0-9]+%\||B/s\]|uncommit|^\s*$|^\s+\S+$' | tail -n "${2:-10}" | cut -c1-220
