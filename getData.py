#!/usr/bin/env python
'''
Created on Aug 15, 2012

@author: pim
'''
import senseapi
import json
import time

def getAllSensorData(se, sensorId, par):
    allData = []
    par['per_page'] = 1000

    first = True
    while (True):
        if not se.SensorDataGet(sensorId, par): #TODO check status code
            print "Error: " + repr(response);
            print "Waiting 30 seconds and try again"
            time.sleep(30)
            continue
        response = json.loads(se.getResponse())
        nr = len(response['data'])
        if (first):
            allData.extend(response['data'])
        else:
            allData.extend(response['data'][2:])
        if (nr < 1000):
            break
        first = False
        par['start_date'] = response['data'][-1]['date']
    
    return allData

def main():
    se = senseapi.SenseAPI()
    #se.setTimeout(30)
    se.setVerbosity(False)
    
    #Login
    credentials=json.load(open('credentials.json'))
    username = credentials['username']
    password = credentials['password']
    password_md5 = senseapi.MD5Hash(password)
    se.Login(username,password)
    
    #get all sensor data of some sensor
    par= {'sort': 'ASC'}
    #par['start_date'] = 1357776000
    #par['end_date'] = 1357927200
    sensorId = 285352
    sensorData = getAllSensorData(se, sensorId, par)
    print json.dumps({'data':sensorData})

if __name__ == '__main__':
    main()
