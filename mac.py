# -*- coding: utf-8 -*-
# <nbformat>2</nbformat>

# <codecell>

import re
import senseapi
import csUtil
import datetime
import sys
import json

# <codecell>

#Login
credentials=json.load(open('credentials.json'))
username = credentials['username']
password = credentials['password']
description = credentials['description']
password_md5 = senseapi.MD5Hash(password)
api = senseapi.SenseAPI()
api.AuthenticateSessionId(username, password_md5)
uploader = csUtil.DataUploader(api, interval=5)

sensorId = None
description = "tcpdump"
try:
	sensorId = csUtil.getSensorId(api, "wifi_devices", description=description)
except ValueError:
	api.SensorsPost({'sensor':{'name':'wifi_devices', 'device_type':description, 'data_type':'json'}})
	sensorId = csUtil.getSensorId(api, "wifi_devices", description=description)

def parseLine(line):
	#TODO: match date
	m_db = re.search('([\-0-9]*)dB', line)
	rssi = m_db.group(1)
	m_smac = re.search('SA:([0-9a-f:]*) ', line)
	smac = m_smac.group(1)
	print "{}: {}".format(smac, rssi)

	uploader.addData(sensorId, datetime.datetime.now(), {"mac":smac, "rssi":float(rssi)})

good = True
while good:
	line = sys.stdin.readline()
	if not line:
		break
		
	try:
		parseLine(line)
	except:
		print "Exception"

