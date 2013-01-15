#!/usr/bin/env python
import senseapi
import json
import string
import sys

def fail(error):
	print error
	sys.exit(-1)
def postData(sensorId, allData):
	allData=allData['data']
	#stupid heuristic to upload per 1000 items
	step=1000
	i=0

	while i < len(allData):
		end = min(i + 1000, len(allData))
		data = allData[i:end]
		if not api.SensorDataPost(sensorId, {'data':data}):
			fail('Couldn\'t upload data. Response: {}'.format(api.getResponse()))
		i += step

if len(sys.argv) != 3:
	fail('Usage: {} test_id input_file'.format(argv[0]))
testNr = sys.argv[1]
dataFile = sys.argv[2]

api=senseapi.SenseAPI()
api.setServer('dev')
credentials=json.load(open('credentials.json'))
username = credentials['username']
password = credentials['password']
password_md5 = senseapi.MD5Hash(password)

#inefficient, just parse once
json_data=open(dataFile)
data = json.load(json_data)
json_data.close()

api.AuthenticateSessionId(username, password_md5)
#create new foreground_app sensor
param = {'sensor':{'name':'foreground_app','device_type':testNr,'data_type':'integer'}}
if not api.SensorsPost(param):
	fail('Couldn\'t create sensor. Response: {}'.format(api.getResponse()))
headers = api.getResponseHeaders()
#headers are case insensitive, map to lower case for easy lookup
headers = dict(zip(map(string.lower, headers.keys()), headers.values()))
location = headers.get('location')
sensorId = location.split('/')[-1]

ds = {"service":{"name":"foreground_app_filter","sensor":{"name":"app_filtered","device_type":testNr}}}
#create service
if not api.ServicesPost(sensorId, ds):
	fail('Couldn\'t create service. Response: {}'.format(api.getResponse()))

postData(sensorId, data)
