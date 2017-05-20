from assignments.homework1 import simulate


def test_simulate1():
    vol, daily_ret, sharpe, cum_ret = simulate()
    assert sharpe == 1.29889334008
