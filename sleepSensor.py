import senseapi
import sys
import datetime
import time
import csUtil
import json


api = senseapi.SenseAPI()

def fail(msg):
    print msg;
    #print api.getResponseStatus()
    #print api.getResponse();
    sys.exit(1)

credentials=json.load(open('credentials.json'))
username = credentials['username']
password = credentials['password']
if not api.AuthenticateSessionId(username, senseapi.MD5Hash(password)):
    fail ("Couldn't login.")

#Check wether a sleep sensor already exists. Don't create a new one if one already exists, that WILL cause problems.
if len(csUtil.getSensorIdList(api, "Sleep")) > 0:
    fail("There is already a sleep sensor. Aborting")
    
accelerometer_id = csUtil.getSensorId(api, "accelerometer")
noise_id = csUtil.getSensorId(api, "noise_sensor")

print "Using noise sensor {} and accelerometer sensor {} as sleep sensor inputs".format(noise_id, accelerometer_id)

command = 'printf("%f",sleepTime([0 {noise_id} 0 0 {accelerometer_id}] , (time-(3600*24)), time))'.format(noise_id=noise_id, accelerometer_id=accelerometer_id)
#get last day 12 pm, as that's the time the script expects to run
midday = datetime.datetime.combine(datetime.date.today(),datetime.time(12,0))
if midday > datetime.datetime.now():
    midday = midday - datetime.timedelta(days=1)

lastTimestamp = time.mktime(midday.timetuple())
interval = datetime.timedelta(days=1).total_seconds()
param = {"dataprocessor":{"command":command, "execution_interval":interval,"last_start_time":lastTimestamp}, "sensor":{"name":"Sleep", "data_type":"float"}}
if not api.DataProcessorsPost(param):
    fail("Couldn't create data processor.");
print "Created Sleep sensor"
