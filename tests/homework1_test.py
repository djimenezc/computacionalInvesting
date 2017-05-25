from nose_parameterized import parameterized
from assignments.homework1 import simulate, get_data, calc_stats, \
    create_output_folder, plot_close_price_series, get_close_price, optimize, \
    calculate_allocations_list, Stats, print_stats
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
def test_calc_stats(dt_start_date, dt_end_date, allocations, ls_symbols,
                    vol_exp,
                    daily_ret_exp,
                    cum_ret_exp, sharpe_exp):
    d_data, ldt_timestamps = get_data(dt_start_date, dt_end_date, ls_symbols)
    # na_price = plot_close_price_series(d_data, ldt_timestamps, ls_symbols)
    na_price = get_close_price(d_data)

    vol, daily_ret, sharpe, cum_ret = calc_stats(na_price, allocations)
    assert np.isclose(vol, vol_exp)
    assert np.isclose(daily_ret, daily_ret_exp)
    assert np.isclose(cum_ret, cum_ret_exp)
    assert np.isclose(sharpe, sharpe_exp)


@parameterized([
    (dt.datetime(2011, 1, 1), dt.datetime(2011, 12, 31),
     [0.4, 0.4, 0.0, 0.2], ['AAPL', 'GLD', 'GOOG', 'XOM'])
])
def test_simulate(dt_start_date, dt_end_date, allocations, ls_symbols):
    assert simulate(dt_start_date, dt_end_date, allocations,
                    ls_symbols, True) is not None


def test_plot_prices():
    ls_symbols = ['AAPL', 'GLD', 'GOOG', 'XOM']
    dt_start_date = dt.datetime(2011, 1, 1)
    dt_end_date = dt.datetime(2011, 12, 31)

    d_data, ldt_timestamps = get_data(dt_start_date, dt_end_date, ls_symbols)
    create_output_folder()
    na_price = plot_close_price_series(d_data, ldt_timestamps, ls_symbols)

    assert na_price is not None


@parameterized([
    (dt.datetime(2011, 1, 1), dt.datetime(2011, 12, 31),
     ['AAPL', 'GLD', 'GOOG', 'XOM'])
])
def test_optimize(dt_start_date, dt_end_date, ls_symbols):
    best_port, stats = \
        optimize(dt_start_date, dt_end_date, ls_symbols)
    assert np.isclose(stats[Stats.SHARPE_RATIO], 1.02828403099)
    assert best_port == [0.4, 0.4, 0, 0.2]


def test_calculate_allocations_list():
    ls_allocations = calculate_allocations_list(1, 10)
    assert len(ls_allocations) == 1
    assert ls_allocations[0][0] == 1
    ls_allocations = calculate_allocations_list(2, 10)
    assert len(ls_allocations) == 11
    ls_allocations = calculate_allocations_list(3, 10)
    assert len(ls_allocations) == 66
    ls_allocations = calculate_allocations_list(4, 10)
    assert len(ls_allocations) == 286


def test_print_stats():
    stats = {
        Stats.VOLATILITY: 50,
        Stats.AVERAGE_RETURNS: 60,
        Stats.SHARPE_RATIO: 40,
        Stats.CUMULATIVE_RETURN: 11
    }
    print_stats(stats)


def test_plot_portfolio_returns():
    assert True
