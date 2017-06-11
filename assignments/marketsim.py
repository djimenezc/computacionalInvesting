"""
Homework 3:
http://wiki.quantsoftware.org/index.php?title=CompInvesti_Homework_3
Read in python marketsim.py initialCash orders.csv values.csv
"""

import sys
import csv
import datetime as dt

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da

DT_TIME_OF_DAY = dt.timedelta(hours=16)


def extract_data_from_orders_file(orders_file_name):
    symbols_dic = {}
    orders = []
    with open(orders_file_name, 'rU') as csv_file:
        orders_reader = csv.reader(csv_file, delimiter=',')

        for row in orders_reader:
            orders.append(
                {'date': dt.datetime(int(row[0]), int(row[1]), int(row[2])),
                 'symbol': row[3], 'order': row[4],
                 'shares': row[5]})
            symbols_dic[row[3]] = True

        # list with the symbols and the sorted orders
        ls_symbols = list(symbols_dic)
        orders = sorted(orders, key=lambda order: order['date'])

        # the range is the first and last order date
        dt_start = orders[0]['date']
        dt_end = orders[len(orders) - 1]['date']

        return ls_symbols, orders, dt_start, dt_end


def get_market_data(dt_start, dt_end, ls_symbols):
    ls_symbols += ["SPY"]

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

    return d_data


def market_simulator(initial_cash, orders_file_name, values_file_name):
    print "---Executing market simulator for"
    print "Initial Cash: ", initial_cash
    print "Orders filename: ", orders_file_name
    print "Values filename: ", values_file_name, "\n"

    market_input_data = extract_data_from_orders_file(orders_file_name)
    ls_symbols = market_input_data[0]
    orders = market_input_data[1]
    dt_start = market_input_data[2]
    dt_end = market_input_data[3]

    print "Start date: ", dt_start
    print "End date: ", dt_end
    print "Symbols: ", ls_symbols, "\n"

    market_data = get_market_data(dt_start, dt_end, ls_symbols)
    market_data_size = len(market_data['close'])
    cash_list = [0] * market_data_size
    portfolio_value = [0] * market_data_size

    # create a clone of close but for owned stocks at a given point
    market_data['owned'] = market_data['close'].copy()
    for symbol in market_data['owned']:
        market_data['owned'][symbol][0:market_data_size] = 0

    # The following sequence is a hymn to bad performance -
    #  blame in on the python noob
    for i in range(0, market_data_size):
        if i == 0:
            cash_list[i] = initial_cash
        else:
            cash_list[i] = cash_list[i - 1]
            for symbol in market_data['owned']:
                market_data['owned'][symbol][i] = market_data['owned'][symbol][
                    i - 1]

        current_date = market_data['close'].index[i].replace(hour=0)

        for order in orders:
            if order['date'] == current_date:
                symbol = order['symbol']
                price = float(market_data['close'][symbol][i])
                share_number = int(order['shares'])
                order_type = order['order']
                order_factor = -1 if order_type == "Buy" else 1
                order_value = price * share_number

                # print "--Logging transaction--"
                # print "symbol: ", symbol
                # print "price: ", price
                # print "number of shares: ", shareNumber
                # print "order type: ", orderType
                # print "previous cash: ", cashList[i]
                # print "previously owned ", symbol,
                #  ": ", marketData['owned'][symbol][i]

                market_data['owned'][symbol][i] += \
                    (-1) * order_factor * share_number
                cash_list[i] += order_factor * order_value

                # print "currently cash:", cashList[i]
                # print "currently owned ", symbol,
                # ": ", marketData['owned'][symbol][i]

        print "-- Portfolio value at day ", i, "---"
        print "Cash value: ", cash_list[i]
        portfolio_value[i] = cash_list[i]
        for symbol in market_data['owned']:
            owned_shares = market_data['owned'][symbol][i]
            if owned_shares == 0:
                continue
            price = float(market_data['close'][symbol][i])
            symbol_value_in_portfolio = owned_shares * price
            portfolio_value[i] += symbol_value_in_portfolio

            print "Adding ", owned_shares, " of ", symbol, " at price ",\
                price, " totaling:", symbol_value_in_portfolio

    # Write the output
    with open(values_file_name, 'wb') as csv_file:
        values_writer = csv.writer(csv_file, delimiter=',')
        for i in range(0, market_data_size):
            current_date = market_data['close'].index[i]
            values_writer.writerow(
                [current_date.year, current_date.month, current_date.day,
                 portfolio_value[i]])


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print "Invalid arguments to marketsim.py, 3 required."
        print "Example input: marketsim.py initialCash orders.csv values.csv"
        sys.exit(0)

    initialCash = int(sys.argv[1])
    ordersFileName = sys.argv[2]
    valuesFileName = sys.argv[3]

    market_simulator(initialCash, ordersFileName, valuesFileName)
