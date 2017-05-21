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

# We need closing prices so the timestamp should be hours=16.
dt_time_of_day = dt.timedelta(hours=16)

# Creating an object of the data access class with Yahoo as the source.
c_data_obj = da.DataAccess('Yahoo', cachestalltime=0)
# Keys to be read from the data, it is good to read everything in one go.
ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']


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


def plot_close_price_series(d_data, ldt_timestamps, ls_symbols):
    # Getting the numpy ndarray of close prices.
    na_price = d_data['close'].values
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


def simulate(dt_start_date, dt_end_date, ls_symbols, ls_allocations):
    d_data, ldt_timestamps = get_data(dt_start_date, dt_end_date, ls_symbols)

    create_output_folder()
    na_price = plot_close_price_series(d_data, ldt_timestamps, ls_symbols)

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
