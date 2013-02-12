#!/usr/bin/env python
"""
	This script can be used to plot sample intervals.
"""
import json
import sys
import datetime
import numpy as np
from matplotlib import pyplot as plt

if len(sys.argv) != 2:
	fail('Usage: {} input_file'.format(argv[0]))
dataFile = sys.argv[1]

json_data=open(dataFile)
data = json.load(json_data)
json_data.close()

#naive implementation for few data points
intervals = []
Ts_prev=None
for x in data['data']:
	Ts=x['date']

	if Ts_prev is not None:
		dt = Ts - Ts_prev
		intervals.append(dt)
	Ts_prev = Ts

print "interval: {} +/- {}. median: {}, min: {}, max: {}".format(np.mean(intervals), np.std(intervals), np.median(intervals), np.min(intervals), np.max(intervals))

#and plot a histogram
plt.hist(intervals, bins=range(60))
plt.title("Sample interval histogram")
plt.xlabel("Time (s)")
plt.ylabel("Frequency")
plt.show()
