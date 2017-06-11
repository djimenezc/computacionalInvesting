"""
Author: Vitor Monteiro
Homework 2
(http://wiki.quantsoftware.org/index.php?title=CompInvestI_Homework_2)
"""

import copy
import datetime as dt

import numpy as np
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep


''' Finding the event dataframe '''


def find_events(ls_symbols, d_data):
    dt_actual_close = d_data['actual_close']

    print "Finding Events"

    # Creating an empty dataframe, using df_close just for size
    df_events = copy.deepcopy(dt_actual_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = dt_actual_close.index

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating if the event happens for this day i
            ac_today = dt_actual_close[s_sym].ix[ldt_timestamps[i]]
            ac_yesterday = dt_actual_close[s_sym].ix[ldt_timestamps[i - 1]]

            # Event is found if the symbol is was >= 5 yesterday
            # and less than 5 today
            if ac_yesterday >= 5.0 > ac_today:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1

    return df_events


def generate_event_profiler(dt_start, dt_end, list_name, event_id):
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    data_obj = da.DataAccess('Yahoo')
    ls_symbols = data_obj.get_symbols_from_list(list_name)
    ls_symbols.append('SPY')

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = data_obj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    df_events = find_events(ls_symbols, d_data)
    event_file_name = event_id + ".pdf"
    print "Creating Study for:", event_id

    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                     s_filename=event_file_name, b_market_neutral=True,
                     b_errorbars=True,
                     s_market_sym='SPY')


if __name__ == '__main__':
    generate_event_profiler(dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31),
                            "sp5002008", "sp50008-2008-2009")
    generate_event_profiler(dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31),
                            "sp5002012", "sp50012-2008-2009")
