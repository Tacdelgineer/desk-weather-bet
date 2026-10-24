#!/usr/bin/env bash
# Archived AIFS (ECMWF real-time) msl/10u/10v over the Atlantic box for each storm run (5/3/1 days before). Safe to re-run.
cd "$(dirname "$0")/.."
mkdir -p results/.done
for init in $(~/.local/bin/uv run python -c "
import json, datetime as dt, sys; sys.path.insert(0,'model')
from hurricanes import init_for, DAYS_BEFORE
for s in json.load(open('results/storms.json')):
    for d in DAYS_BEFORE: print(init_for(dt.datetime.fromisoformat(s['ref_time']), d).strftime('%Y-%m-%dT%H'))"); do
  ~/.local/bin/uv run --project model/aifs python fetch/aifs_archive.py field --init $init --steps 0-144 --box 5,50,-100,-30
done
touch results/.done/hurricane_fields_archive
