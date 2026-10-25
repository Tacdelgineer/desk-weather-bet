# Hand check — 5 random TEST bets (player: corrected AIFS v2 + rule), PAPER MONEY

## KXHIGHNY-26SEP27-B67.5 — YES
- forecast: AIFS run 2026-09-26T00:00:00, 6-hourly 2 m temps in the local day: 09-27T06Z=58.54;09-27T12Z=60.63;09-27T18Z=64.77;09-28T00Z=62.3 → raw high 64.77°F
- correction (KNYC, v2 rolling): mean(actual − raw) over 30 of the 30 days 2026-08-27…2026-09-25 = +0.68°F → 64.77 +0.68 = 65.45°F, sigma 1.70
- guards: GFS 65.0°F, gap 0.4°F ≤ 4; edge ≤ 0.30
- bracket: between floor=67.0 cap=68.0 (67° to 68°) → P(YES) = 0.2320, P(YES) = 0.2320
- price at bet time (candle ending 2026-09-26 16:00:00Z): YES ask = $0.10
- size: 9 contracts, cost $0.90, fee round_up(0.07×9×0.10×0.90) = $0.06; edge = 0.2320 − 0.10 − 0.0067 = 0.1253 > threshold 0.09
- settlement: Kalshi settled high 63.00°F, result NO → LOSS
- P&L: $0 − $0.90 − $0.06 = **$-0.96** (sim.py: $-0.96) ✓

## KXHIGHTSFO-26OCT12-B64.5 — YES
- forecast: AIFS run 2026-10-11T00:00:00, 6-hourly 2 m temps in the local day: 10-12T12Z=53.8;10-12T18Z=62.02;10-13T00Z=63.61;10-13T06Z=54.85 → raw high 63.61°F
- correction (KSFO, v2 rolling): mean(actual − raw) over 30 of the 30 days 2026-09-11…2026-10-10 = +3.72°F → 63.61 +3.72 = 67.33°F, sigma 2.17
- guards: GFS 69.1°F, gap 1.8°F ≤ 4; edge ≤ 0.30
- bracket: between floor=64.0 cap=65.0 (64° to 65°) → P(YES) = 0.1605, P(YES) = 0.1605
- price at bet time (candle ending 2026-10-11 16:00:00Z): YES ask = $0.05
- size: 18 contracts, cost $0.90, fee round_up(0.07×18×0.05×0.95) = $0.06; edge = 0.1605 − 0.05 − 0.0033 = 0.1072 > threshold 0.09
- settlement: Kalshi settled high 69.00°F, result NO → LOSS
- P&L: $0 − $0.90 − $0.06 = **$-0.96** (sim.py: $-0.96) ✓

## KXHIGHTPHX-26SEP19-T106 — YES
- forecast: AIFS run 2026-09-18T00:00:00, 6-hourly 2 m temps in the local day: 09-19T12Z=73.37;09-19T18Z=91.71;09-20T00Z=99.29;09-20T06Z=82.46 → raw high 99.29°F
- correction (KPHX, v2 rolling): mean(actual − raw) over 30 of the 30 days 2026-08-19…2026-09-17 = +3.30°F → 99.29 +3.30 = 102.59°F, sigma 3.14
- guards: GFS 100.8°F, gap 1.8°F ≤ 4; edge ≤ 0.30
- bracket: greater floor=106.0 cap=nan (107° or above) → P(YES) = 0.1068, P(YES) = 0.1068
- price at bet time (candle ending 2026-09-18 15:00:00Z): YES ask = $0.01
- size: 93 contracts, cost $0.93, fee round_up(0.07×93×0.01×0.99) = $0.07; edge = 0.1068 − 0.01 − 0.0008 = 0.0961 > threshold 0.09
- settlement: Kalshi settled high 103.00°F, result NO → LOSS
- P&L: $0 − $0.93 − $0.07 = **$-1.00** (sim.py: $-1.00) ✓

## KXHIGHTPHX-26OCT09-B105.5 — YES
- forecast: AIFS run 2026-10-08T00:00:00, 6-hourly 2 m temps in the local day: 10-09T12Z=76.34;10-09T18Z=95.01;10-10T00Z=100.97;10-10T06Z=86.22 → raw high 100.97°F
- correction (KPHX, v2 rolling): mean(actual − raw) over 30 of the 30 days 2026-09-08…2026-10-07 = +2.71°F → 100.97 +2.71 = 103.68°F, sigma 3.99
- guards: GFS 101.0°F, gap 2.7°F ≤ 4; edge ≤ 0.30
- bracket: between floor=105.0 cap=106.0 (105° to 106°) → P(YES) = 0.1786, P(YES) = 0.1786
- price at bet time (candle ending 2026-10-08 16:00:00Z): YES ask = $0.07
- size: 13 contracts, cost $0.91, fee round_up(0.07×13×0.07×0.93) = $0.06; edge = 0.1786 − 0.07 − 0.0046 = 0.1039 > threshold 0.09
- settlement: Kalshi settled high 104.00°F, result NO → LOSS
- P&L: $0 − $0.91 − $0.06 = **$-0.97** (sim.py: $-0.97) ✓

## KXHIGHCHI-26OCT06-B74.5 — NO
- forecast: AIFS run 2026-10-05T00:00:00, 6-hourly 2 m temps in the local day: 10-06T06Z=50.53;10-06T12Z=48.1;10-06T18Z=71.16;10-07T00Z=65.98 → raw high 71.16°F
- correction (KMDW, v2 rolling): mean(actual − raw) over 30 of the 30 days 2026-09-05…2026-10-04 = +1.85°F → 71.16 +1.85 = 73.01°F, sigma 2.45
- guards: GFS 72.7°F, gap 0.3°F ≤ 4; edge ≤ 0.30
- bracket: between floor=74.0 cap=75.0 (74° to 75°) → P(YES) = 0.2661, P(NO) = 0.7339
- price at bet time (candle ending 2026-10-05 16:00:00Z): NO ask = $0.55
- size: 1 contracts, cost $0.55, fee round_up(0.07×1×0.55×0.45) = $0.02; edge = 0.7339 − 0.55 − 0.0200 = 0.1639 > threshold 0.09
- settlement: Kalshi settled high 74.00°F, result YES → LOSS
- P&L: $0 − $0.55 − $0.02 = **$-0.57** (sim.py: $-0.57) ✓

All 5 recomputed independently match sim.py: YES