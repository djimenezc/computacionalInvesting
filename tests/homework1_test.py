from nose_parameterized import parameterized
from assignments.homework1 import simulate
import datetime as dt
import numpy as np


@parameterized([
    (dt.datetime(2010, 1, 1), dt.datetime(2010, 12, 31),
     [0.0, 0.0, 0.0, 1.0], ['AXP', 'HPQ', 'IBM', 'HNZ'],
     0.00924299255937, 0.000756285585593, 1.1960583568, 1.29889334008),

    (dt.datetime(2011, 1, 1), dt.datetime(2011, 12, 31),
     [0.4, 0.4, 0.0, 0.2], ['AAPL', 'GLD', 'GOOG', 'XOM'],
     0.0101467067654, 0.000657261102001, 1.16487261965, 1.02828403099)
])
def test_simulate1(dt_start, dt_end, allocations, symbols, vol_exp,
                   daily_ret_exp,
                   cum_ret_exp, sharpe_exp):
    vol, daily_ret, sharpe, cum_ret = simulate(dt_start, dt_end,
                                               symbols, allocations)
    assert np.isclose(vol, vol_exp)
    assert np.isclose(daily_ret, daily_ret_exp)
    assert np.isclose(cum_ret, cum_ret_exp)
    assert np.isclose(sharpe, sharpe_exp)
