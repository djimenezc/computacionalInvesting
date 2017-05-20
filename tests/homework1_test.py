from nose_parameterized import parameterized
from assignments.homework1 import simulate
import datetime as dt

SYMBOLS = ['AAPL', 'GLD', 'GOOG', 'XOM']


@parameterized([
    (dt.datetime(2010, 1, 1), dt.datetime(2010, 12, 31), [0.0, 0.0, 0.0, 1.0],
     0.00924299255937, 0.000756285585593, 1.1960583568, 1.29889334008)
])
def test_simulate1(dt_start, dt_end, allocations, vol_exp, daily_ret_exp,
                   cum_ret_exp, sharpe_exp):
    vol, daily_ret, sharpe, cum_ret = simulate(dt_start, dt_end, SYMBOLS,
                                               allocations)
    assert vol == vol_exp
    assert daily_ret == daily_ret_exp
    assert cum_ret == cum_ret_exp
    assert sharpe == sharpe_exp
