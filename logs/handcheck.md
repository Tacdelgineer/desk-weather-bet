# Hand check — 5 random TEST bets (player: corrected AIFS + rule), PAPER MONEY

## KXHIGHMIA-26SEP22-B87.5 — NO
- forecast: AIFS run 2026-09-21T00:00:00, 6-hourly 2 m temps in the local day: 09-22T06Z=78.56;09-22T12Z=78.67;09-22T18Z=85.19;09-23T00Z=80.72 → raw high 85.19°F
- correction (KMIA, TRAIN fit): 37.148 + 0.6204 × 85.19 = 90.00°F, sigma 1.30
- bracket: between floor=87.0 cap=88.0 (87° to 88°) → P(YES) = 0.1214, P(NO) = 0.8786
- price at bet time (candle ending 2026-09-21 16:00:00Z): NO ask = $0.58
- size: 1 contracts, cost $0.58, fee round_up(0.07×1×0.58×0.42) = $0.02; edge = 0.8786 − 0.58 − 0.0200 = 0.2786 > threshold 0.09
- settlement: Kalshi settled high 89.00°F, result NO → WIN
- P&L: 1 × $1 − $0.58 − $0.02 = **$+0.40** (sim.py: $+0.40) ✓

## KXHIGHCHI-26SEP08-B85.5 — NO
- forecast: AIFS run 2026-09-07T00:00:00, 6-hourly 2 m temps in the local day: 09-08T06Z=64.84;09-08T12Z=62.0;09-08T18Z=81.07;09-09T00Z=80.64 → raw high 81.07°F
- correction (KMDW, TRAIN fit): 2.240 + 0.9935 × 81.07 = 82.79°F, sigma 2.18
- bracket: between floor=85.0 cap=86.0 (85° to 86°) → P(YES) = 0.1715, P(NO) = 0.8285
- price at bet time (candle ending 2026-09-07 16:00:00Z): NO ask = $0.63
- size: 1 contracts, cost $0.63, fee round_up(0.07×1×0.63×0.37) = $0.02; edge = 0.8285 − 0.63 − 0.0200 = 0.1785 > threshold 0.09
- settlement: Kalshi settled high 87.00°F, result NO → WIN
- P&L: 1 × $1 − $0.63 − $0.02 = **$+0.35** (sim.py: $+0.35) ✓

## KXHIGHNY-26OCT09-B69.5 — NO
- forecast: AIFS run 2026-10-08T00:00:00, 6-hourly 2 m temps in the local day: 10-09T06Z=52.23;10-09T12Z=50.44;10-09T18Z=71.06;10-10T00Z=59.5 → raw high 71.06°F
- correction (KNYC, TRAIN fit): 10.988 + 0.8691 × 71.06 = 72.75°F, sigma 1.86
- bracket: between floor=69.0 cap=70.0 (69° to 70°) → P(YES) = 0.1021, P(NO) = 0.8979
- price at bet time (candle ending 2026-10-08 16:00:00Z): NO ask = $0.70
- size: 1 contracts, cost $0.70, fee round_up(0.07×1×0.70×0.30) = $0.02; edge = 0.8979 − 0.70 − 0.0200 = 0.1779 > threshold 0.09
- settlement: Kalshi settled high 70.00°F, result YES → LOSS
- P&L: $0 − $0.70 − $0.02 = **$-0.72** (sim.py: $-0.72) ✓

## KXHIGHLAX-26AUG28-B84.5 — YES
- forecast: AIFS run 2026-08-27T00:00:00, 6-hourly 2 m temps in the local day: 08-28T12Z=72.36;08-28T18Z=80.34;08-29T00Z=82.67;08-29T06Z=75.04 → raw high 82.67°F
- correction (KLAX, TRAIN fit): 12.635 + 0.8895 × 82.67 = 86.17°F, sigma 1.98
- bracket: between floor=84.0 cap=85.0 (84° to 85°) → P(YES) = 0.2790, P(YES) = 0.2790
- price at bet time (candle ending 2026-08-27 16:00:00Z): YES ask = $0.16
- size: 5 contracts, cost $0.80, fee round_up(0.07×5×0.16×0.84) = $0.05; edge = 0.2790 − 0.16 − 0.0100 = 0.1090 > threshold 0.09
- settlement: Kalshi settled high 86.00°F, result NO → LOSS
- P&L: $0 − $0.80 − $0.05 = **$-0.85** (sim.py: $-0.85) ✓

## KXHIGHTPHX-26OCT07-B103.5 — NO
- forecast: AIFS run 2026-10-06T00:00:00, 6-hourly 2 m temps in the local day: 10-07T12Z=76.31;10-07T18Z=93.51;10-08T00Z=101.52;10-08T06Z=86.26 → raw high 101.52°F
- correction (KPHX, TRAIN fit): 27.175 + 0.7641 × 101.52 = 104.75°F, sigma 2.23
- bracket: between floor=103.0 cap=104.0 (103° to 104°) → P(YES) = 0.2986, P(NO) = 0.7014
- price at bet time (candle ending 2026-10-06 16:00:00Z): NO ask = $0.57
- size: 1 contracts, cost $0.57, fee round_up(0.07×1×0.57×0.43) = $0.02; edge = 0.7014 − 0.57 − 0.0200 = 0.1114 > threshold 0.09
- settlement: Kalshi settled high 102.00°F, result NO → WIN
- P&L: 1 × $1 − $0.57 − $0.02 = **$+0.41** (sim.py: $+0.41) ✓

All 5 recomputed independently match sim.py: YES