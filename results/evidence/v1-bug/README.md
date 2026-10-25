# Evidence: the v1 correction bug (dry run for market day 2026-10-24)

- `2026-10-23_picks.json`: copy of logs/live/2026-10-23_picks.json, the by-hand DRY_RUN with the v1 rules (tag `rules-locked`).
- `nws_pfm_PSR_2026-10-23.txt`, `nws_pfm_MFL_2026-10-23.txt`: NWS Point Forecast Matrices (Phoenix, Miami offices), every
  issuance from 2026-10-23 to 2026-10-24, as archived by the Iowa Environmental Mesonet
  (`https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?pil=PFMPSR&sdate=2026-10-23&edate=2026-10-24&limit=10&fmt=text`,
  same for `PFMMFL`). Retrieved 2026-10-25 ~04:40 UTC. The NWS forecast checked during the by-hand run was not saved
  at the time; these are the NWS's own forecast products for the same day, archived as issued.
- `nws_cli_prelim_KPHX_2026-10-24.json`, `nws_cli_prelim_KMIA_2026-10-24.json`: NWS Daily Climate Report for 10-24 via
  IEM `json/cli.py`. **Preliminary** (issued the same afternoon). Kalshi's settled value is what counts.
- `summary.json`: written by `backtest/v1_bug.py`. Per station: TRAIN raw-high range, v1 fit, raw and corrected highs, GFS,
  NWS forecast max per issuance, preliminary NWS high; plus the TRAIN scatter (raw AIFS vs actual) for the video.
