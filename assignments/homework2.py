"""
Author: Vitor Monteiro
Homework 2 (http://wiki.quantsoftware.org/index.php?title=CompInvestI_Homework_2)
"""

import copy
import datetime as dt

import numpy as np
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep


def find_events(ls_symbols, d_data):
    ''' Finding the event dataframe '''
    dt_actualClose = d_data['actual_close']

    print "Finding Events"

    # Creating an empty dataframe, using df_close just for size
    df_events = copy.deepcopy(dt_actualClose)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = dt_actualClose.index

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating if the event happens for this day i
            acToday = dt_actualClose[s_sym].ix[ldt_timestamps[i]]
            acYesterday = dt_actualClose[s_sym].ix[ldt_timestamps[i - 1]]

            # Event is found if the symbol is was >= 5 yesterday and less than 5 today
            if acYesterday >= 5.0 > acToday:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1

    return df_events


def generateEventProfiler(dt_start, dt_end, listName, eventId):
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list(listName)
    ls_symbols.append('SPY')

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    df_events = find_events(ls_symbols, d_data)
    eventFileName = eventId + ".pdf"
    print "Creating Study for:", eventId

    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                     s_filename=eventFileName, b_market_neutral=True, b_errorbars=True,
                     s_market_sym='SPY')


if __name__ == '__main__':
    generateEventProfiler(dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), "sp5002008", "sp50008-2008-2009")
    generateEventProfiler(dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), "sp5002012", "sp50012-2008-2009")
