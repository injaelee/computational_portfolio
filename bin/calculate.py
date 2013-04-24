import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd

import math
import numpy as np

import sys
import time



def simulate(startdate, enddate, symbols, allocations):
	# check input size check
	if len(symbols) != len(allocations):
		raise Exception('The symbols set size must equal to the allocations set size.')

	# check allocation
	allocation_sum = sum(allocations)
	#if abs(allocation_sum - 1.0) < 0.1:
	#	print allocation_sum
#		print math.fabs(allocation_sum - 1.0)
#		raise Exception('Allocation must equal to 1.0; it equals to ' + str(allocation_sum) + '.')    

	datetime_timeofday = dt.timedelta(hours=16)
	trading_days = du.getNYSEdays(datetime_start, datetime_end, datetime_timeofday)
	
	dataobj = da.DataAccess("Yahoo", cachestalltime=0)
	interested_value_types = ["close", "actual_close"]
	interested_data = dataobj.get_data(trading_days, symbols, interested_value_types)
	d_data = dict(zip(interested_value_types, interested_data))

	na_price = d_data['close'].values
	na_normalized_price = na_price / na_price[0, :]
	na_rets = na_normalized_price.copy()
	na_portret_alloc = (na_rets * allocations) 
	na_daily_port = na_portret_alloc.sum(axis=1) 
	na_cumret = na_daily_port[na_daily_port.size-1]
	tsu.returnize0(na_daily_port)
	na_daily_port[np.isnan(na_daily_port) == True] = 0 
	na_std = np.std(na_daily_port) 
	na_mean = np.mean(na_daily_port) 
	sh1 = math.sqrt(252)*(na_mean/na_std)

	#print "Sharpe Ratio: (" + str(expected["sharpe"]) + ") " + str(sh1)
	#print "Volatility:   (" + str(expected["std"]) + ") " + str(na_std)
	#print "Average Daily Return: (" + str(expected["avg"]) + ") " + str(na_mean)
	#print "Cumulative Return: (" + str(expected["cum"]) + ") " + str(na_cumret)

	# :: Caveats of Using Equations with 'shift(...)'
	#   There is something wrong with calculating daily returns in the following way
	# 
	#       daily_returns_individual = d_data['close'] / d_data['close'].shift(1) - 1
	#
	#
	
	# :: Notes on access DataFrame
	#    Access row i: DataFrame.is[i]
	#      ex) norm_cum_value = d_data['close'] / d_data['close'].ix[0]
	#
	#    Operations on each column. Axis #1
	#               on each row.    Axis #0
	#      ex) norm_sum_w_value.sum(axis=1) # sum the columns producing one row

	# return vol, daily_ret, sharpe, cum_ret
	#   1) volatility
	#   2) daily returns
	#   3) sharpe ratio
	#   4) cumulative return
	return (na_std, na_mean, sh1, na_cumret)

symbols = ["AAPL", "GLD", "GOOG", "XOM"]
datetime_start = dt.datetime(2011, 1, 1)
datetime_end = dt.datetime(2011,12,31)
allocations = [0.4, 0.4, 0.0, 0.2]
expected = {"sharpe": 1.02828403099, "std": 0.0101467067654, "avg": 0.000657261102001, "cum": 1.16487261965}
volatility, daily_returns, sharpe_ratio, cum_return = simulate(datetime_start, datetime_end, symbols, allocations)
print str(volatility) + "," + str(daily_returns) + "," + str(sharpe_ratio) + "," + str(cum_return)

symbols = ["AXP", "HPQ", "IBM", "HNZ"]
datetime_start = dt.datetime(2010, 1, 1)
datetime_end = dt.datetime(2010,12,31)
allocations = [0.0, 0.0, 0.0, 1.0]
expected = {"sharpe": 1.29889334008, "std": 0.00924299255937, "avg": 0.000756285585593, "cum": 1.1960583568}
volatility, daily_returns, sharpe_ratio, cum_return = simulate(datetime_start, datetime_end, symbols, allocations)


symbols = ["BRCM", "TXN", "IBM", "HNZ"] 
#symbols = ["BRCM", "ADBE", "AMD", "ADI"]
datetime_start = dt.datetime(2011, 1, 1)
datetime_end = dt.datetime(2011,12,31)
#allocations = [0.9, 0.0, 0.1, 0.0]
#allocations = [0.0, 0.0, 0.9, 0.1]
#allocations = [0.0, 0.0, 1.0, 0.0]
#allocations = [0.2, 0.8, 0.0, 0.0]
allocations = [0.0, 0.3, 0.7, 0.0]
volatility, daily_returns, sharpe_ratio, cum_return = simulate(datetime_start, datetime_end, symbols, allocations)
print sharpe_ratio


allocations = []
# generate the allocation sequence
for ma in range(0,10):
	ia = 0.1 * ma
	for mb in range(0,10):
		ib = 0.1 * mb
		isum = ib + ia
		if 1.0 < ib + ia:
			continue # skip if sum of i's are bigger than 1.0

		for mc in range(0,10):
			ic = 0.1 * mc
			if 1.0 < ic + ib + ia:
				continue

			for md in range(0,10):
				id_ = 0.1 * md
				isum = id_ + ic + ib + ia
				if 1.0 < isum or 1.0 > isum:
					continue

				#print str(ia) + "," + str(ib) + "," + str(ic) + "," + str(id_)
				allocations.append([ia, ib, ic, id_])

best_allocation = []
best_sharpe_ratio = 0
progress_index = 0
for a in allocations:
	progress_index += 1
	

	volatility, daily_returns, sharpe_ratio, cum_return = simulate(
		datetime_start, 
		datetime_end, 
		symbols, 
		a
	)
	print "Calculated: " + str(a) + " : " + str(sharpe_ratio)	
	if best_sharpe_ratio < sharpe_ratio:
		best_allocation = a
		best_sharpe_ratio = sharpe_ratio

	#sys.stdout.write( 
	print (
		"\rprogress: [" + str(progress_index) + "/" + str(len(allocations)) + 
		"] best sharpe ratio:[" +  str(best_sharpe_ratio) + "]" +
		" best allocation:["+ str(best_allocation) +"]"
	)
	
	