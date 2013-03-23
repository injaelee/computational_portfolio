import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd

import math
import numpy as np

#Start Date: January 1, 2011
#End Date: December 31, 2011
#Symbols: ['AAPL', 'GLD', 'GOOG', 'XOM']
#Optimal Allocations: [0.4, 0.4, 0.0, 0.2]
#Sharpe Ratio: 1.02828403099
#Volatility (stdev of daily returns):  0.0101467067654
#Average Daily Return:  0.000657261102001
#Cumulative Return:  1.16487261965

symbols = ["AAPL", "GLD", "GOOG", "XOM"]
datetime_start = dt.datetime(2011, 1, 1)
datetime_end = dt.datetime(2011,12,31)
allocations = [0.4, 0.4, 0.0, 0.2]
expected = {"sharpe": 1.02828403099, "std": 0.0101467067654, "avg": 0.000657261102001, "cum": 1.16487261965}

#symbols = ["AXP", "HPQ", "IBM", "HNZ"]
#datetime_start = dt.datetime(2010, 1, 1)
#datetime_end = dt.datetime(2010,12,31)
#allocations = [0.0, 0.0, 0.0, 1.0]
#expected = {"sharpe": 1.29889334008, "std": 0.00924299255937, "avg": 0.000756285585593, "cum": 1.1960583568}

#symbols = ["AAPL", "AMZN"]
#datetime_start = dt.datetime(2011, 1, 1)
#datetime_end = dt.datetime(2012,12,31)
#datetime_timeofday = dt.timedelta(hours=16)
#trading_days = du.getNYSEdays(datetime_start, datetime_end, datetime_timeofday)

#dataobj = da.DataAccess('Yahoo')
#interested_value_types = ['close', 'actual_close']
#interested_data = dataobj.get_data(trading_days, symbols, interested_value_types)
#d_data = dict(zip(interested_value_types, interested_data))

#print d_data['actual_close'][:10]
#print ((d_data['actual_close'].divide(d_data['actual_close'].ix[0])-1)* 100)[:10]


#returns = d_data['actual_close'] / d_data['actual_close'].shift(1) - 1
#print (returns * 100).std(0)


# Start Date: January 1, 2011
# End Date: December 31, 2011
# Symbols: ['AAPL', 'GLD', 'GOOG', 'XOM']
# Optimal Allocations: [0.4, 0.4, 0.0, 0.2]
# Sharpe Ratio: 1.02828403099
# Volatility (stdev of daily returns):  0.0101467067654
# Average Daily Return:  0.000657261102001
# Cumulative Return:  1.16487261965
# 
# Start Date: January 1, 2010
# End Date: December 31, 2010
# Symbols: ['AXP', 'HPQ', 'IBM', 'HNZ']
# Optimal Allocations:  [0.0, 0.0, 0.0, 1.0]
# Sharpe Ratio: 1.29889334008
# Volatility (stdev of daily returns): 0.00924299255937
# Average Daily Return: 0.000756285585593
# Cumulative Return: 1.1960583568

# Standard deviation of daily returns of the total portfolio
# Average daily return of the total portfolio
# Sharpe ratio (Always assume you have 252 trading days in an year. And risk free rate = 0) of the total portfolio
# Cumulative return of the total portfolio

def simulate(startdate, enddate, symbols, allocations, expected):
	# check input size check
	if len(symbols) != len(allocations):
		raise Exception('The symbols set size must equal to the allocations set size.')

	# check allocation
	allocation_sum = sum(allocations)
	if allocation_sum != 1:
		raise Exception('Allocation must equal to 1; it equals to ' + str(allocation_sum) + '.')    

	datetime_timeofday = dt.timedelta(hours=16)
	trading_days = du.getNYSEdays(datetime_start, datetime_end, datetime_timeofday)
	
	dataobj = da.DataAccess("Yahoo", cachestalltime=0)
	interested_value_types = ["close", "actual_close"]
	interested_data = dataobj.get_data(trading_days, symbols, interested_value_types)
	d_data = dict(zip(interested_value_types, interested_data))

	df_rets = d_data['close'].copy()
	df_rets = df_rets.fillna(method='ffill')
	df_rets = df_rets.fillna(method='bfill')
	na_rets = df_rets.values
	
	tsu.returnize0(na_rets)
	print na_rets


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

	print "Sharpe Ratio: (" + str(expected["sharpe"]) + ") " + str(sh1)
	print "Volatility:   (" + str(expected["std"]) + ") " + str(na_std)
	print "Average Daily Return: (" + str(expected["avg"]) + ") " + str(na_mean)
	print "Cumulative Return: (" + str(expected["cum"]) + ") " + str(na_cumret)



	
	norm_cum_value = d_data['close'] / d_data['close'].ix[0]
	norm_sum_w_value = norm_cum_value * allocations
	daily_values = norm_sum_w_value.sum(axis=1)
	cumulative_return = daily_values.tail(1).ix[0]

	na_rets[np.isnan(na_rets) == True] = 0
	daily_returns = np.dot(na_rets, allocations) -1

	std = np.std(daily_returns)
	avg = np.mean(daily_returns)
	sharpe = math.sqrt(252)*(avg/std)

	print "Sharpe Ratio: (" + str(expected["sharpe"]) + ") " + str(sharpe)
	print "Volatility:   (" + str(expected["std"]) + ") " + str(std)
	print "Average Daily Return: (" + str(expected["avg"]) + ") " + str(avg)
	print "Cumulative Return: (" + str(expected["cum"]) + ") " + str(cumulative_return)



	print ""
	print ""


	print na_daily_port
	print daily_returns

	print na_daily_port - daily_returns





	#normalized_cumulative_weighted_value = normalized_cumulative_value * allocations
	#sum_normalized_cumulative_weighted_values = normalized_cumulative_weighted_value.sum(axis=1)
	#sum_normalized_cumulative_weighted_returns = sum_normalized_cumulative_weighted_values - 1
#
	#daily_returns_individual = d_data['close'] / d_data['close'].shift(1) - 1
	#daily_returns_individual.ix[0] = 0
	#cumulative_daily_returns_individual = (daily_returns_individual * allocations).sum(axis=1)
#
	#entire_sum = cumulative_daily_returns_individual.sum(axis=0)
#
	#mean = cumulative_daily_returns_individual.mean(axis=0)
	#mean = sum_normalized_cumulative_weighted_returns.mean(axis=0)
#
	#std_dev = math.sqrt(((cumulative_daily_returns_individual - mean) ** 2).sum(axis=0) / (len(trading_days)))
	#std_dev = math.sqrt(((sum_normalized_cumulative_weighted_returns - mean) ** 2).sum(axis=0) / (len(trading_days)))
#
	## not used: cumulative_daily_returns_individual.std(axis=0)
#
	#sharpe_ratio = math.sqrt(252) * mean / std_dev #math.sqrt(len(trading_days)) * mean / std_dev
	#print "Sharpe Ratio: (" + str(expected["sharpe"]) + ") " + str(sharpe_ratio)
	#print "Volatility:   (" + str(expected["std"]) + ") " + str(std_dev)
	#print "Average Daily Return: (" + str(expected["avg"]) + ") " + str(mean)
	#print "Cumulative Return: (" + str(expected["cum"]) + ") " + str(sum_normalized_cumulative_weighted_returns.tail(1).ix[0])
	
	
	
	

	#Start Date: January 1, 2011
#End Date: December 31, 2011
#Symbols: ['AAPL', 'GLD', 'GOOG', 'XOM']
#Optimal Allocations: [0.4, 0.4, 0.0, 0.2]
#Sharpe Ratio: 1.02828403099
#Volatility (stdev of daily returns): 0.0101467067654
#Average Daily Return: 0.000657261102001
#Cumulative Return: 1.16487261965

	#print "Average Daily Return: " + str(sum_cumulative_weighted_returns.mean(axis=0))
	#print "Volatility: " + str(sum_cumulative_weighted_returns.std(axis=0))
	

	#print "AVG: " + str(sum_cumulative_weighted_returns.tail(1).ix[0] / len(trading_days))

	#closing_prices = d_data['close'] 
	#normalized = d_data['close'].divide(d_data['close'].ix(0))
	#print normalized[:10]
	#daily_returns_individual = d_data['close'] / d_data['close'].ix(0)
	#print daily_returns_individual[:5]
	#daily_returns_individual = d_data['close'] / d_data['close'].shift(1) - 1
	#daily_returns_individual.ix[0] = 0
	#daily_weighted_returns_individual = daily_returns_individual * allocations
	#daily_weighted_returns = daily_weighted_returns_individual.sum(axis=1)

	# print daily_returns_individual[:4]
	#print daily_weighted_returns_individual[:4]
	#print "Average Daily Return: " + str(daily_weighted_returns.mean(axis=0))
	#print "Volatility: " + str(daily_weighted_returns.std(axis=0))


simulate(datetime_start, datetime_end, symbols, allocations, expected)