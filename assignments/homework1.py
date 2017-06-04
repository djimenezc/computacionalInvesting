"""
Created on January, 24, 2013

@author: David Jimenez
@contact: david.jimenez19@gmail.com
@summary: Write a Python function that can simulate
 and assess the performance of a 4 stock portfolio.
http://wiki.quantsoftware.org/index.php?title=CompInvestI_Homework_1
"""

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import os

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import time
import itertools
from enum import Enum

# We need closing prices so the timestamp should be hours=16.
dt_time_of_day = dt.timedelta(hours=16)

# Creating an object of the data access class with Yahoo as the source.
c_data_obj = da.DataAccess('Yahoo', cachestalltime=0)
# Keys to be read from the data, it is good to read everything in one go.
ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']


class Stats(Enum):
    VOLATILITY = 0
    AVERAGE_RETURNS = 1
    SHARPE_RATIO = 2
    CUMULATIVE_RETURN = 3


def create_output_folder():
    output_path = 'out'
    if not os.path.exists(output_path):
        os.makedirs(output_path)


def get_na_price(d_data):
    # Getting the numpy ndarray of close prices.
    return d_data['close'].values


def get_data(dt_start_date, dt_end_date, ls_symbols):
    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start_date, dt_end_date, dt_time_of_day)
    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_data_obj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    # Filling the data for NAN
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    return d_data, ldt_timestamps


def get_close_price(d_data):
    return d_data['close'].values


def plot_close_price_series(d_data, ldt_timestamps, ls_symbols):
    # Getting the numpy ndarray of close prices.
    na_price = get_close_price(d_data)
    plot_price_series(na_price, ldt_timestamps, ls_symbols)

    return na_price


def plot_price_series(na_price, ldt_timestamps, ls_symbols,
                      name='close.pdf'):
    # Plotting the prices with x-axis=timestamps
    plt.clf()
    plt.plot(ldt_timestamps, na_price)
    plt.legend(ls_symbols)
    plt.ylabel('Adjusted Close')
    plt.xlabel('Date')
    output_path = 'out'

    plt.savefig(output_path + '/' + name, format='pdf')


def calculate_series_return(price_series):
    return price_series[-1] - price_series[0]


def get_cumulative_return(na_port_normalized_price):
    na_port_returns = np.sum(na_port_normalized_price, axis=1)

    return na_port_returns[-1]


'''
 Calculate Portfolio Statistics 
 @param na_normalized_price: NumPy Array for normalized prices (starts at 1)
 @param lf_allocations: allocation list
 @return list of statistics:
 (Volatility, Average Return, Sharpe, Cumulative Return)
'''


def calc_stats(na_price, ls_allocations):
    na_normalized_price = na_price / na_price[0, :]
    na_weighted_price = na_normalized_price * ls_allocations

    cum_ret = get_cumulative_return(na_weighted_price)

    # row-wise sum
    na_portf_value = na_weighted_price.copy().sum(axis=1)

    # Calculate daily returns on portfolio
    na_portf_rets = na_portf_value.copy()
    tsu.returnize0(na_portf_rets)

    # Calculate volatility (stdev) of daily returns of portfolio
    f_portf_volatility = np.std(na_portf_rets)

    # Calculate average daily returns of portfolio
    f_portf_avg_ret = np.mean(na_portf_rets)

    # Calculate portfolio sharpe ratio
    # (avg portfolio return / portfolio stdev) * sqrt(252)
    f_portf_sharpe = (f_portf_avg_ret / f_portf_volatility) * np.sqrt(252)

    return f_portf_volatility, f_portf_avg_ret, f_portf_sharpe, cum_ret


'''
' Simulate and assess performance of multi-stock portfolio
' @param li_startDate:	start date in list structure: [year,month,day]
     e.g. [2012,1,28]
' @param li_endDate:	end date in list structure: [year,month,day] 
    e.g. [2012,12,31]
' @param ls_symbols:	list of symbols: e.g. ['GOOG','AAPL','GLD','XOM']
' @param lf_allocations:	list of allocations: e.g. [0.2,0.3,0.4,0.1]
' @param b_print:       print results (True/False)
'''


def simulate(dt_start_date, dt_end_date, lf_allocations, ls_symbols,
             b_print=False):
    start = time.time()

    # Check if ls_symbols and lf_allocations have same length
    if len(ls_symbols) != len(lf_allocations):
        print "ERROR: Make sure symbol and allocation lists have same number " \
              "of elements."
        return
    # Check if lf_allocations adds up to 1
    sum_allocations = 0
    for x in lf_allocations:
        sum_allocations += x
    # noinspection PyTypeChecker
    if not np.isclose(sum_allocations, 1):
        print "ERROR: Make sure allocations add up to 1."
        return

    # Prepare data for statistics
    # d_data = readData(li_start_date, li_end_date, ls_symbols)[0]
    d_data, ldt_timestamps = get_data(dt_start_date, dt_end_date, ls_symbols)
    na_price = get_close_price(d_data)

    # Normalize prices to start at 1 (if we do not do this, then portfolio value
    # must be calculated by weight*Budget/startPriceOfStock)
    na_normalized_price = na_price / na_price[0, :]

    lf_stats = calc_stats(na_normalized_price, lf_allocations)

    # Print results
    if b_print:
        create_output_folder()
        plot_close_price_series(d_data, ldt_timestamps, ls_symbols)

        print "Start Date: ", dt_start_date
        print "End Date: ", dt_end_date
        print "Symbols: ", ls_symbols
        print "Volatility (stdev daily returns): ", lf_stats[0]
        print "Average daily returns: ", lf_stats[1]
        print "Sharpe ratio: ", lf_stats[2]
        print "Cumulative daily return: ", lf_stats[3]

        print "Run in: ", (time.time() - start), " seconds."

    return {
        Stats.VOLATILITY: lf_stats[0],
        Stats.AVERAGE_RETURNS: lf_stats[1],
        Stats.SHARPE_RATIO: lf_stats[2],
        Stats.CUMULATIVE_RETURN: lf_stats[3]
    }


def optimize_precise(na_normalized_price, port_len):
    return []


def calculate_allocations_list(port_len, percentage_slot=10):
    numbers = range(0, (100 / percentage_slot) + 1)
    result = [seq for i in [0] for seq in
              itertools.product(numbers, repeat=port_len) if
              sum(seq) == 10 and len(seq) == port_len]
    return (np.asarray(result, dtype=float) / 10).tolist()


def optimize_non_precise(dt_start_date, dt_end_date, ls_symbols,
                         ratio_diana=Stats.SHARPE_RATIO):
    ls_allocations = calculate_allocations_list(len(ls_symbols))
    best_port = []
    best_ratio_diana = 0
    best_port_stats = None

    # noinspection PyTypeChecker
    print 'Looking for the best allocation between %s possibilities' % len(
        ls_allocations)

    for idx, allocation in enumerate(ls_allocations):
        print "Simulating allocation %s number %s" % (', '.join(
            map(str, allocation)), idx)
        stats = simulate(dt_start_date, dt_end_date, allocation, ls_symbols)
        if stats[ratio_diana] > best_ratio_diana:
            best_port = allocation
            best_ratio_diana = stats[ratio_diana]
            best_port_stats = stats
            print '[Found better allocation [%s]  new value %s]' % (', '.join(
                map(str, best_port)), best_ratio_diana)

    print 'Best allocation [%s]' % (', '.join(map(str, best_port)))
    print_stats(best_port_stats)

    return best_port, best_port_stats


def print_stats(stats):
    print 'stats: [%s]' % (', '.join(map(lambda x: str(x.value), stats)))


'''
' Optimize portfolio allocations  to maximise Sharpe ratio
' @param li_startDate:	start date in list structure: [year,month,day] 
    e.g. [2012,1,28]
' @param li_endDate:	end date in list structure: [year,month,day] 
    e.g. [2012,12,31]
' @param ls_symbols:	list of symbols: e.g. ['GOOG','AAPL','GLD','XOM']
' @param s_precision:   true - precise optimization; false - 
    10% increments & positive weights
'''


def optimize(dt_start_date, dt_end_date, ls_symbols, b_precision=False):
    start = time.time()

    # Prepare data for statistics
    d_data, ldt_timestamps = get_data(dt_start_date, dt_end_date, ls_symbols)

    # Get numpy ndarray of close prices (numPy)
    na_price = d_data['close'].values

    # Normalize prices to start at 1 (if we do not do this,
    # then portfolio value must be calculated by
    #  weight*Budget/startPriceOfStock)
    na_normalized_price = na_price / na_price[0, :]

    port_len = len(ls_symbols)

    stats = []

    if b_precision:
        lf_curr_eff_allocation = optimize_precise(na_normalized_price, port_len)
    else:
        lf_curr_eff_allocation, stats = optimize_non_precise(dt_start_date,
                                                             dt_end_date,
                                                             ls_symbols)

    lf_curr_stats = calc_stats(na_price, lf_curr_eff_allocation)

    # Print results:
    print "Start Date: ", dt_start_date
    print "End Date: ", dt_end_date
    print "Symbols: ", ls_symbols
    print "Optimal Allocations: ", lf_curr_eff_allocation
    print "Volatility (stdev daily returns): ", lf_curr_stats[0]
    print "Average daily returns: ", lf_curr_stats[1]
    print "Sharpe ratio: ", lf_curr_stats[2]
    print "Cumulative daily return: ", lf_curr_stats[3]

    print "Run in: ", (time.time() - start), " seconds."

    return lf_curr_eff_allocation, stats
