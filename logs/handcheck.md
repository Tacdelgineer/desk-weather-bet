# Hand check — 5 random TEST bets (player: corrected AIFS + rule), PAPER MONEY

## KXHIGHCHI-26SEP22-B62.5 — NO
- forecast: AIFS run 2026-09-21T00:00:00, 6-hourly 2 m temps in the local day: 09-22T06Z=58.42;09-22T12Z=55.48;09-22T18Z=59.52;09-23T00Z=59.9 → raw high 59.90°F
- correction (KMDW, TRAIN fit): -4.518 + 1.0918 × 59.90 = 60.88°F, sigma 1.91
- bracket: between floor=62.0 cap=63.0 (62° to 63°) → P(YES) = 0.2879, P(NO) = 0.7121
- price at bet time (candle ending 2026-09-21 16:00:00Z): NO ask = $0.63
- size: 1 contracts, cost $0.63, fee round_up(0.07×1×0.63×0.37) = $0.02; edge = 0.7121 − 0.63 − 0.0200 = 0.0621 > threshold 0.04
- settlement: Kalshi settled high 64.00°F, result NO → WIN
- P&L: 1 × $1 − $0.63 − $0.02 = **$+0.35** (sim.py: $+0.35) ✓

## KXHIGHTSFO-26OCT07-B83.5 — YES
- forecast: AIFS run 2026-10-06T00:00:00, 6-hourly 2 m temps in the local day: 10-07T12Z=61.26;10-07T18Z=75.49;10-08T00Z=79.83;10-08T06Z=65.26 → raw high 79.83°F
- correction (KSFO, TRAIN fit): 12.367 + 0.8479 × 79.83 = 80.05°F, sigma 3.14
- bracket: between floor=83.0 cap=84.0 (83° to 84°) → P(YES) = 0.1395, P(YES) = 0.1395
- price at bet time (candle ending 2026-10-06 16:00:00Z): YES ask = $0.07
- size: 13 contracts, cost $0.91, fee round_up(0.07×13×0.07×0.93) = $0.06; edge = 0.1395 − 0.07 − 0.0046 = 0.0649 > threshold 0.04
- settlement: Kalshi settled high 76.00°F, result NO → LOSS
- P&L: $0 − $0.91 − $0.06 = **$-0.97** (sim.py: $-0.97) ✓

## KXHIGHLAX-26AUG24-B82.5 — YES
- forecast: AIFS run 2026-08-23T00:00:00, 6-hourly 2 m temps in the local day: 08-24T12Z=69.95;08-24T18Z=82.36;08-25T00Z=85.79;08-25T06Z=76.18 → raw high 85.79°F
- correction (KLAX, TRAIN fit): 23.671 + 0.6889 × 85.79 = 82.77°F, sigma 2.01
- bracket: between floor=82.0 cap=83.0 (82° to 83°) → P(YES) = 0.3775, P(YES) = 0.3775
- price at bet time (candle ending 2026-08-23 16:00:00Z): YES ask = $0.24
- size: 3 contracts, cost $0.72, fee round_up(0.07×3×0.24×0.76) = $0.04; edge = 0.3775 − 0.24 − 0.0133 = 0.1242 > threshold 0.04
- settlement: Kalshi settled high 84.00°F, result NO → LOSS
- P&L: $0 − $0.72 − $0.04 = **$-0.76** (sim.py: $-0.76) ✓

## KXHIGHLAX-26SEP05-T80 — NO
- forecast: AIFS run 2026-09-04T00:00:00, 6-hourly 2 m temps in the local day: 09-05T12Z=65.17;09-05T18Z=76.78;09-06T00Z=79.95;09-06T06Z=72.06 → raw high 79.95°F
- correction (KLAX, TRAIN fit): 23.671 + 0.6889 × 79.95 = 78.75°F, sigma 2.01
- bracket: greater floor=80.0 cap=nan (81° or above) → P(YES) = 0.1921, P(NO) = 0.8079
- price at bet time (candle ending 2026-09-04 16:00:00Z): NO ask = $0.59
- size: 1 contracts, cost $0.59, fee round_up(0.07×1×0.59×0.41) = $0.02; edge = 0.8079 − 0.59 − 0.0200 = 0.1979 > threshold 0.04
- settlement: Kalshi settled high 81.00°F, result YES → LOSS
- P&L: $0 − $0.59 − $0.02 = **$-0.61** (sim.py: $-0.61) ✓

## KXHIGHMIA-26SEP23-T89 — YES
- forecast: AIFS run 2026-09-22T00:00:00, 6-hourly 2 m temps in the local day: 09-23T06Z=79.53;09-23T12Z=79.05;09-23T18Z=82.91;09-24T00Z=80.16 → raw high 82.91°F
- correction (KMIA, TRAIN fit): 25.064 + 0.7717 × 82.91 = 89.05°F, sigma 1.30
- bracket: greater floor=89.0 cap=nan (90° or above) → P(YES) = 0.3635, P(YES) = 0.3635
- price at bet time (candle ending 2026-09-22 16:00:00Z): YES ask = $0.09
- size: 10 contracts, cost $0.90, fee round_up(0.07×10×0.09×0.91) = $0.06; edge = 0.3635 − 0.09 − 0.0060 = 0.2675 > threshold 0.04
- settlement: Kalshi settled high 83.00°F, result NO → LOSS
- P&L: $0 − $0.90 − $0.06 = **$-0.96** (sim.py: $-0.96) ✓

All 5 recomputed independently match sim.py: YES