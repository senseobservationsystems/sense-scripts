#!/usr/bin/env python
"""
	This script can be used to sort data based on insertion time, which
	might come in handy when debugging state sensors.
"""
import json
import sys
import datetime

if len(sys.argv) != 2:
	fail('Usage: {} input_file'.format(argv[0]))
dataFile = sys.argv[1]

json_data=open(dataFile)
data = json.load(json_data)
json_data.close()

print "Imported {} data points.".format(len(data['data']))

#first 8 digits are timestamp, last 6 are counter, sort on them. See http://docs.mongodb.org/manual/core/object-id/
data['data'].sort(key=lambda x:int(x['id'][0:8].join(x['id'][18:24]),16))
#Print sorted data
#print json.dumps(data)

#print human-readable table with insertion times and sample times.
print "Insertion time, Sample time"
Ts_last = 0
lastValue=None
for x in data['data']:
	Ti=int(x['id'][0:8],16)
	strTi = datetime.datetime.fromtimestamp(Ti).strftime('%Y-%m-%d %H:%M:%S')
	Ts=x['date']
	strTs = datetime.datetime.fromtimestamp(Ts).strftime('%Y-%m-%d %H:%M:%S')
	strTs_last = datetime.datetime.fromtimestamp(Ts_last).strftime('%Y-%m-%d %H:%M:%S')
	if Ts < Ts_last:
		print "Out of order:\t{}, {} -- {}".format(strTi, strTs_last, strTs)
	Ts_last = Ts;
	lastValue = x['value']
	

