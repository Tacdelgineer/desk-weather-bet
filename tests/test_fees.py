from backtest.fees import fee


def test_fee_doc_example_5c_100_contracts():
    # Kalshi fee table: price $0.05, 100 contracts ($5.00) -> fee $0.34
    assert fee(0.05, 100) == 0.34


def test_fee_doc_example_50c():
    # Kalshi fee table: price $0.50 -> fee $0.02 for 1 contract, $1.75 for 100 contracts
    assert fee(0.50, 1) == 0.02
    assert fee(0.50, 100) == 1.75


def test_fee_doc_table_rows():
    table = {0.01: (0.01, 0.07), 0.10: (0.01, 0.63), 0.15: (0.01, 0.90), 0.20: (0.02, 1.12), 0.25: (0.02, 1.32),
             0.30: (0.02, 1.47), 0.35: (0.02, 1.60), 0.40: (0.02, 1.68), 0.45: (0.02, 1.74), 0.55: (0.02, 1.74),
             0.60: (0.02, 1.68)}
    for p, (one, hundred) in table.items():
        assert fee(p, 1) == one, p
        assert fee(p, 100) == hundred, p
