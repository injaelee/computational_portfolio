import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu

import sys
import locale
import datetime as dt
import numpy as np
import math

def fill_in_the_blanks(d_data, interested_value_types):
	for s_key in interested_value_types:
 		d_data[s_key] = d_data[s_key].fillna(method = 'ffill')
 		d_data[s_key] = d_data[s_key].fillna(method = 'bfill')
 		d_data[s_key] = d_data[s_key].fillna(1.0)
 	return d_data


locale.setlocale(locale.LC_ALL, '')

balance = float(sys.argv[1])
input_orders_filepath = sys.argv[2]
output_value_filepath = sys.argv[3]

print "Starting balance: [", \
      locale.currency(balance, grouping=True), "]; Input: [", \
      input_orders_filepath, \
      "] Output: [", output_value_filepath, "]"


cash_balances = balance
entries = [line.strip() for line in open(input_orders_filepath)]


class Trade:
	def __init__(self, symbol, action, shares):
		self.symbol = symbol
		self.action = action
		self.shares = shares

	def __str__(self):
		s = "[%s] (%s) %s shares" % (self.symbol, self.action, self.shares)
		return s

	def __repr__(self):
		return "[", self.symbol, "] (", self.action ,") #:", self.shares


# need to determine start and end dates
symbols_to_fetch = []
datetime_start = None #dt.datetime(2011, 1, 1)
datetime_end = None #dt.datetime(2011,12,31)
min_datetime = None
max_datetime = None
map_date_trades = {}
for e in entries:
	tokens = e.split(",")
	year = int(tokens[0].strip())
	month = int(tokens[1].strip())
	day = int(tokens[2].strip())
	symbol = tokens[3].strip()
	action = tokens[4].strip()
	shares = int(tokens[5].strip())
	if not symbol in symbols_to_fetch:
		symbols_to_fetch.append(symbol)

	date = dt.datetime(year, month, day, 16)
	if min_datetime == None or date < min_datetime:
		min_datetime = date

	if max_datetime == None or date > max_datetime:
		max_datetime = date

	if date in map_date_trades:
		map_date_trades[date].append(Trade(symbol, action, shares))
	else:
		map_date_trades[date] = [Trade(symbol, action, shares)]


# fetch the amount
#max_datetime += dt.timedelta(1)
datetime_timeofday = dt.timedelta(hours=16)
trading_days = du.getNYSEdays(min_datetime, max_datetime, datetime_timeofday)


dataobj = da.DataAccess("Yahoo", cachestalltime=0)
interested_value_types = ["close", "actual_close"]
interested_data = dataobj.get_data(trading_days, symbols_to_fetch, interested_value_types)
d_data = dict(zip(interested_value_types, interested_data))

aggregate_values = []

print d_data["actual_close"]
print "\n\n\n"

out = open(output_value_filepath, "w")

# symbol, number of shares
total_value = 0;
holdings = {}
for td in trading_days:
	print ":: Start (%s)Trading Day: %s" %  (locale.currency(cash_balances, grouping=True), str(td))
	if td in map_date_trades:
		for t in map_date_trades[td]:
			price = d_data["close"].lookup([td], [t.symbol])
			value = price * t.shares
			if t.action.upper() == "BUY":
				
				# take the money out
				cash_balances -= value
				print "\t\tBought %s shares. %s of %s. Cash balance: %s" % \
				(t.shares, t.symbol, locale.currency(value, grouping=True), \
					locale.currency(cash_balances, grouping=True))
				# add to the number of shares
				if t.symbol in holdings:
					holdings[t.symbol] += t.shares
				else:
					holdings[t.symbol] = t.shares

			elif t.action.upper() == "SELL":
				cash_balances += value
				print "\t\tSold %s shares. %s of %s. Cash balance: %s" % \
				(t.shares, t.symbol, locale.currency(value, grouping=True), \
					locale.currency(cash_balances, grouping=True))

				if t.symbol in holdings:
					holdings[t.symbol] -= t.shares
				else:
					holdings[t.symbol] = t.shares * -1
	else:
		print "\t\tNone"

	# calculate aggregate portfolio value
	
	total_value = cash_balances + 0
	
	for h in holdings:
		price = d_data["close"].lookup([td], [h])
		print "\t + %s: %s x %s = %s" % \
		(h, locale.currency(price, grouping=True), holdings[h], \
			locale.currency(holdings[h] * price, grouping=True))
		total_value += holdings[h] * price


	print>>out, "%s,%s,%s,%.2f" % (td.year, td.month, td.day, total_value)
	
	aggregate_values.append(float(total_value))


	print "::  End  (%s)Trading Day: %s" %  (locale.currency(cash_balances, grouping=True), str(td))
	print td, ":", locale.currency(total_value, grouping=True), \
	"\n_____________________________________________________________\n"
	print holdings


aggregate_values = np.array(aggregate_values)
aggregate_values = aggregate_values / aggregate_values[0]

tsu.returnize0(aggregate_values)

returns_mean = np.mean(aggregate_values)
returns_std = np.std(aggregate_values)

sharpe_ratio = math.sqrt(252)*(returns_mean/returns_std)

print "Returns mean: %s ; std: %s ; sharpe ratio: %s" % (returns_mean, returns_std, sharpe_ratio)


