#!/usr/bin/env python
'''
@author: jg@sense-os.nl
'''

import senseapi
import json
import sys

#module wide variables
api = senseapi.SenseAPI()



def initSense():
    # api.setServer('dev')
    credentials = json.load(open('credentials.json'))
    username = credentials['username']
    password = credentials['password']
    password_md5 = senseapi.MD5Hash(password)
    api.AuthenticateSessionId(username, password_md5)


def getSensorId( sensorName, deviceType=None, description=None, userName=None):
    owned = 1 if userName is None else 0
    #find sensor
    if not api.SensorsGet({'per_page':1000, 'details':'full', 'order':'asc', "owned":owned}):
            raise Exception("Couldn't get sensors. {}".format(api.getResponse()))
    sensors = json.loads(api.getResponse())['sensors']
    correctSensors = filter(lambda x: x['name'] == sensorName, sensors)
    if deviceType:
        correctSensors = filter(lambda x: "device" in x and x['device']['type'] == deviceType, correctSensors)
    if description:
        correctSensors = filter(lambda x: "device_type" in x and x["device_type"] == description, correctSensors)
    if userName:
        correctSensors = filter(lambda x: "owner" in x and x["owner"]["username"] == userName, correctSensors)
    if len(correctSensors) == 0:
        raise ValueError("Sensor {} not found!".format(sensorName))
    sensorId = correctSensors[-1]["id"]
    return sensorId


def createSensorOnce( sensorName, description, dataType, dataStructure=None):
    try:
        sensorId = getSensorId( sensorName, description=description)
    except ValueError:
        #doesn't exist, create sensor
        par = {'sensor': {'name':sensorName, 'device_type':description, 'data_type':'dataType'}}
        if dataStructure:
            par["sensor"]["data_structure"] = dataStructure
        if api.SensorsPost(par):
            sensorId = api.getLocationId()
    return sensorId


def postData(sensorId, allData):

    #stupid heuristic to upload per 1000 items
    step=1000
    i=0
    print "len:"+str(len(allData))
    while i < len(allData):
        end = min(i + 1000, len(allData))
        data = allData[i:end]
        if not api.SensorDataPost(sensorId, {'data':data}):
            fail('Couldn\'t upload data. Response: {}'.format(api.getResponse()))
        i += step



def fail(error):
    print error
    sys.exit(-1)
