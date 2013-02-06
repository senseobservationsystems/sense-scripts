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

prev = None
duplicates = []
for x in data['data']:
	duplicate = False
	if prev is not None and x['date'] == prev['date']:
		duplicates.append(x)
	prev = x

for x in duplicates:
	data['data'].remove(x)

print "Deleted {} duplicates.".format(len(duplicates))
print "Remaining {} data points.".format(len(data['data']))

# first 8 digits are timestamp, last 6 are counter, sort on them. See http://docs.mongodb.org/manual/core/object-id/
data['data'].sort(key=lambda x:int(x['id'][0:8].join(x['id'][18:24]),16))
# Print sorted data
# print json.dumps(data)

# print human-readable table with insertion times and sample times.
prev = None
for x in data['data']:
	Ti = int(x['id'][0:8], 16)
	counter = x['id'][18:24]
	strTi = datetime.datetime.fromtimestamp(Ti).strftime('%d/%m %H:%M:%S')
	Ts = x['date']
	strTs = datetime.datetime.fromtimestamp(Ts).strftime('%d/%m %H:%M:%S')
	
	# insert a line for identify separate upload batches
	if prev is not None and Ti != int(prev['id'][0:8], 16):
		print ("-" * 72)
	
	# flag data where sample time is not increasing
	if prev is not None and Ts < prev['date']:
		flag = "<" * 10
	else:
		flag = ""

	print "Ti: {Ti} ({counter}),\tTs: {Ts},\tvalue: {value}\t{flag}".format(Ti=strTi, Ts=strTs, counter=counter, flag=flag, value=x['value'])
	prev = x
	

