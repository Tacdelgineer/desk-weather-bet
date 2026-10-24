import pandas as pd
import pytest

from backtest.correct import fit
from backtest.window import SPLIT, TEST, TRAIN, assert_train_only


def test_split_halves():
    assert len(TRAIN) == len(TEST) == 60
    assert max(TRAIN) < SPLIT <= min(TEST)


def test_fit_refuses_test_dates():
    df = pd.DataFrame({"date": [str(TRAIN[0]), str(TEST[0])], "settled_high": [70, 71], "aifs_high": [69, 70]})
    with pytest.raises(AssertionError):
        fit(df, "aifs_high")
    with pytest.raises(AssertionError):
        assert_train_only([TEST[-1]])
    assert_train_only(TRAIN)
