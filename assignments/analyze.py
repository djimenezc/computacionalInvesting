#!/usr/local/bin/python

"""
Expected output for homework 3 orders.csv:
http://wiki.quantsoftware.org/index.php?title=CompInvesti_Homework_3
The final value of the portfolio using the sample file is -- 2011,12,20,1133860
Details of the Performance of the portfolio :
Data Range :  2011-01-10 16:00:00  to  2011-12-20 16:00:00
Sharpe Ratio of Fund : 1.21540462111
Sharpe Ratio of $SPX : 0.0183391412227
Total Return of Fund :  1.13386
Total Return of $SPX : 0.97759401457
Standard Deviation of Fund :  0.00717514512699
Standard Deviation of $SPX : 0.0149090969828
Average Daily Return of Fund :  0.000549352749569
Average Daily Return of $SPX : 1.72238432443e-05
Expected output for orders2.csv
The final value of the portfolio using the sample file is -- 2011,12,14, 1078753
Details of the Performance of the portfolio
Data Range :  2011-01-14 16:00:00  to  2011-12-14 16:00:00
Sharpe Ratio of Fund : 0.788988545538
Sharpe Ratio of $SPX : -0.177204632551
Total Return of Fund :  1.078753
Total Return of $SPX : 0.937041848381
Standard Deviation of Fund :  0.00708034656073
Standard Deviation of $SPX : 0.0149914504972
Average Daily Return of Fund :  0.000351904599618
Average Daily Return of $SPX : -0.000167347202139
"""

import sys
import csv
import datetime as dt
import QSTK.qstkutil.tsutil as tsu

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import numpy as np
import matplotlib.pyplot as plt
import math

DT_TIME_OF_DAY = dt.timedelta(hours=16)


def analyze(values_file_name, benchmark_symbol):
    portfolio_day_value = []
    dates = []
    with open(values_file_name, 'rU') as csv_file:
        values_reader = csv.reader(csv_file, delimiter=',')
        for row in values_reader:
            portfolio_day_value.append(float(row[3]))
            dates.append(dt.datetime(int(row[0]), int(row[1]), int(row[2])))

    dt_start = dates[0]
    dt_end = dates[-1]
    initial_portfolio_value = portfolio_day_value[0]

    print "---Portfolio Analyzer---\n"

    ls_symbols = [benchmark_symbol]

    # Get a list of trading days between the start and the end.
    # Adding a day to the end_date since it doesn't seem to count the last day
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end + dt.timedelta(days=1),
                                    DT_TIME_OF_DAY)

    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')

    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['close']

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    # Filling the data for NAN
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    # Getting the numpy ndarray of close prices.
    adjusted_bench_mark_prices = d_data['close'].values

    # Normalize the prices
    benchmark_normalized_prices = \
        adjusted_bench_mark_prices / adjusted_bench_mark_prices[0, :]
    portfolio_normalized_prices = \
        [x / initial_portfolio_value for x in portfolio_day_value]

    # Benchmark value for initial portfolio value
    benchmark_day_value = [x * initial_portfolio_value for x in
                           benchmark_normalized_prices[:, 0]]

    # Create another matrix like dtf with the porfolio and the index
    portfolio_and_index = np.column_stack(
        (portfolio_day_value, benchmark_day_value))

    # Plotting the prices with x-axis=timestamps
    plt.clf()
    plt.plot(ldt_timestamps, portfolio_and_index)
    plt.legend(["Portfolio", benchmark_symbol])
    plt.ylabel('Value')
    plt.xlabel('Date')
    plt.savefig('analyze_portfolioVSbenchmark.pdf', format='pdf')

    # if we want daily returns we just apply formula
    # d(t) = (price(t) / price(t-1)) -1
    bench_mark_daily_returns = benchmark_normalized_prices.copy()
    tsu.returnize0(bench_mark_daily_returns)
    portfolio_daily_returns = np.copy(portfolio_normalized_prices)
    tsu.returnize0(portfolio_daily_returns)

    # Average daily returns
    benchmark_avg_daily_returns = np.average(bench_mark_daily_returns)
    portfolio_avg_daily_returns = np.average(portfolio_daily_returns)

    # Stdev of daily returns
    portfolio_stdev_daily_returns = np.std(portfolio_daily_returns)
    benchmark_stdev_daily_returns = np.std(bench_mark_daily_returns)

    # Sharpe ration
    portfolio_sharpe_ratio = math.sqrt(
        252) * portfolio_avg_daily_returns / portfolio_stdev_daily_returns
    benchmark_sharpe_ratio = math.sqrt(
        252) * benchmark_avg_daily_returns / benchmark_stdev_daily_returns

    print "The final value of the portfolio using", values_file_name, \
        "file is ", dt_end.year, ",", dt_end.month, ",", dt_end.day, ",", \
        portfolio_day_value[-1], "\n"

    print "Details of the Performance of the portfolio: \n"
    print "Data Range: ", str(dt_start), " to ", str(dt_end), "\n"

    print "Sharpe Ratio of Fund:", portfolio_sharpe_ratio
    print "Sharpe Ratio of ", benchmark_symbol, ":",\
        benchmark_sharpe_ratio, "\n"

    print "Total Return of Fund: ", portfolio_normalized_prices[-1]
    print "Total Return of", benchmark_symbol, ":", \
        benchmark_normalized_prices[-1][0], "\n"

    print "Standard Deviation of Fund:", portfolio_stdev_daily_returns
    print "Standard Deviation of", benchmark_symbol, ":", \
        benchmark_stdev_daily_returns, "\n"

    print "Average Daily Return of Fund:", portfolio_avg_daily_returns
    print "Average Daily Return of", benchmark_symbol, ":", \
        benchmark_avg_daily_returns, "\n"


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Invalid arguments to analyze.py, 2 required."
        print "Example input: analyze.py values.csv \$SPX"
        sys.exit(0)

    benchmarkSymbol = sys.argv[2]
    valuesFileName = sys.argv[1]

    analyze(valuesFileName, benchmarkSymbol)
