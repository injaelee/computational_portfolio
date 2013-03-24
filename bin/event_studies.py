import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep

import pandas as pd
import numpy as np
import copy
import datetime as dt

def find_events(ls_symbols, d_data):
	''' Finding the event dataframe '''
	df_close = d_data["actual_close"]

	print "Finding Events"

	# Creating an empty dataframe
	df_events = copy.deepcopy(df_close)
	df_events = df_events * np.NAN

	# Time stamps for the event range
	ldt_timestamps = df_close.index

	total_number_of_events = 0
	for s_sym in ls_symbols:
		for i in range(1, len(ldt_timestamps)):
			# Calculating the returns for this timestamp
			f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
			f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]

			# Event is found if the symbol is down more then 3% while the
			# market is up more then 2%
			if f_symprice_yest >= 9.0 and f_symprice_today < 9.0:
				df_events[s_sym].ix[ldt_timestamps[i]] = 1
				total_number_of_events += 1


	print "Total number of events:[" + str(total_number_of_events) + "]"
	return df_events


def fill_in_the_blanks(d_data, interested_value_types):
	for s_key in interested_value_types:
 		d_data[s_key] = d_data[s_key].fillna(method = 'ffill')
 		d_data[s_key] = d_data[s_key].fillna(method = 'bfill')
 		d_data[s_key] = d_data[s_key].fillna(1.0)
 	return d_data


#remain constant
interested_value_types = ["actual_close"]
datetime_timeofday = dt.timedelta(hours=16)
datetime_start = dt.datetime(2008, 1, 1)
datetime_end = dt.datetime(2009,12,31)

dataobj = da.DataAccess("Yahoo")
symbols = dataobj.get_symbols_from_list("sp5002008")
symbols.append('SPY')

trading_days = du.getNYSEdays(datetime_start, datetime_end, datetime_timeofday)
d_data = dataobj.get_data(trading_days, symbols, interested_value_types)
d_data = dict(zip(interested_value_types, d_data))
d_data = fill_in_the_blanks(d_data, interested_value_types)

df_events = find_events(symbols, d_data)
print int(np.nansum(df_events.values))

ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
s_filename='2008.pdf', b_market_neutral=True, b_errorbars=True,
s_market_sym='SPY')



symbols = dataobj.get_symbols_from_list("sp5002012")
symbols.append('SPY')

trading_days = du.getNYSEdays(datetime_start, datetime_end, datetime_timeofday)
d_data = dataobj.get_data(trading_days, symbols, interested_value_types)
d_data = dict(zip(interested_value_types, d_data))
d_data = fill_in_the_blanks(d_data, interested_value_types)

df_events = find_events(symbols, d_data)
print int(np.nansum(df_events.values))

ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
s_filename='2012.pdf', b_market_neutral=True, b_errorbars=True,
s_market_sym='SPY')
