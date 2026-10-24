"""Kalshi trading fee.

Source: Kalshi Fee Schedule PDF (kalshi.com/docs/kalshi-fee-schedule.pdf, "Last updated and effective: Feb 5, 2026";
copy archived 2026-06-12 in results/sources/). General (taker) fee:
    fees = round up(0.07 x C x P x (1-P))      P = price in dollars, C = contracts, round up = to the next cent
Maker fee (only on markets Kalshi lists): round up(0.0175 x C x P x (1-P)).
The KXHIGH series report fee_type "quadratic" with fee_multiplier 1 in the API, i.e. the general formula.
"""
import math

TAKER_RATE = 0.07
MAKER_RATE = 0.0175


def fee(price, contracts, rate=TAKER_RATE, multiplier=1.0):
    """Fee in dollars for one trade of `contracts` at `price` dollars (0 < price < 1), rounded up to the cent."""
    if contracts <= 0:
        return 0.0
    raw = multiplier * rate * contracts * price * (1 - price)
    return math.ceil(round(raw * 100, 9)) / 100  # round() guards float noise like 1.7500000000000002
