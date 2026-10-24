#!/usr/bin/env bash
# Fetch archived AIFS 2t at stations for every backtest init (D-1 00Z for each market date D). Safe to re-run.
cd "$(dirname "$0")/.."
~/.local/bin/uv run --project model/aifs python fetch/aifs_archive.py points-all --init 2000-01-01T00 --steps 24-60
