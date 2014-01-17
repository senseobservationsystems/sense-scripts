"""
This script removes empty sensors.
"""
import senseapi
import json
import os

s = senseapi.SenseAPI()
s.Login('pimtest2',senseapi.MD5Hash('livelaevolution'))
#s.Login('ivitality1000@gmail.com',senseapi.MD5Hash('ivitality'))
if s.getResponseStatus() != 200:
	print "Couldn't login"

par={}
par['owned']=1
par['physical']=1
par['per_page']=1000
s.SensorsGet(par)

sensors = json.loads(s.getResponse())['sensors']
print "Found {} sensors".format(len(sensors))

par={}
par['per_page']=1
par['date']=0
for sensor in sensors:
  if s.SensorDataGet(sensor['id'],par):
    j=json.loads(s.getResponse())
    print "{} data points.".format(len(j['data']))
    if len(j['data']) == 0:
      print "Delete {}".format(sensor['id'])
      s.SensorsDelete(sensor['id'])
