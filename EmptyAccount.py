#/usr/bin/env python
# -*- coding: utf-8 -*-
#Simple code snippet to empty a common sense account.
import senseapi
import json

api=senseapi.SenseAPI()
username = ""
password = ""

api.AuthenticateSessionId(username, senseapi.MD5Hash(password))

#Clean-up data processors
api.DataProcessorsGet({})
response = json.loads(api.getResponse())
for dp in response['dataprocessors']:
    api.DataProcessorsDelete(dp['id'])

#Clean-up sensors
par={}
par['owned']=1
par['per_page']=1000
api.SensorsGet(par)
response = json.loads(api.getResponse())
for sensor in response['sensors']:
    api.SensorsDelete(sensor['id'])

