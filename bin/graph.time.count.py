import numpy as np
import pylab as P
import sys
from matplotlib.backends.backend_pdf import PdfPages


# --------------------------------------------------------------------------------
#
#   Graph the count distribution given a list of time and quantity pairs.
# 
#   If there is a gap in the input, this script will fill up the empty times.
#     ex) time_interval is 300 seconds or 5 minutes
#   
#   Input:
#     1) Input path of the file
#     2) PDF output file
#     3) time interval of times in seconds
#
# --------------------------------------------------------------------------------
input_path = sys.argv[1]
pdf_filepath = sys.argv[2]
time_interval = int(sys.argv[3])

current_item = ""
current_start_time = 0

item_distribution = {}
times = []
quantities = []
# we need to normalize on the time
with open(input_path) as f:
	for line in f:
		# item
		# time
		# quantity
		values = line.strip().split(',')
		item = values[0]
		time = int(values[1])
		quantity = int(values[2])

		if current_item != item:
			# assign the distribution
			item_distribution[current_item] = np.array(quantities)

			current_item = item
			current_start_time = time
			
			# reset
			quantities = []
			times = []
		
		relative_time = time - current_start_time
		# let's try to backfill some times
		if len(times) > 0:
			for tt in xrange(times[-1] + time_interval, relative_time, time_interval):
				times.append(tt)
				quantities.append(0)

		times.append(relative_time)
		quantities.append(quantity)

# take care of the last iteration
item_distribution[current_item] = np.array(quantities)


# ==========================================================================================
#
#  Graph the distribution
#
# ==========================================================================================
num_rows = 3
num_cols = 2
num_plots_per_page = num_rows * num_cols
pp = PdfPages(pdf_filepath)
item_ids = item_distribution.keys()
item_ids.pop(0)
f_i = 1
for i in xrange(0, len(item_ids), num_plots_per_page):
	f = P.figure()

	for j in range(1,num_plots_per_page + 1):
		current_index = i + j - 1
		if current_index >= len(item_ids):
			break
		distr = item_distribution[item_ids[current_index]]
		P.subplot(num_rows, num_cols, j)
		P.subplots_adjust(wspace = 0.3, hspace = 0.5)
		n, bins, patches = P.hist(distr, 100, histtype='bar')
		P.title("Item ID: %s" %item_ids[current_index])

	pp.savefig(f)
pp.close()
