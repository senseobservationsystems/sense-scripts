import json
import threading
import time
import datetime
import Queue
from ssl import SSLError
import copy
import operator

class DataUploader:
    #size to limit an upload request to
    MAX_UPLOAD_SIZE = 500*1024
    def __init__(self, api, interval=30):
        self.api = api
        self.interval = interval
        self.dataQueue = Queue.Queue()
        threading.Thread(target=self.run).start()
        
    def addData(self, sensorId, date, value):
        self.dataQueue.put_nowait((sensorId, date, copy.deepcopy(value)))
        
    def upload(self):
        sensorData = {}
        size = 0
        while size < self.MAX_UPLOAD_SIZE:
            try:
                (sensorId, date, value) = self.dataQueue.get_nowait()
            except Queue.Empty:
                break
            if sensorId not in sensorData:
                sensorData[sensorId] = []
            unixTimestamp = time.mktime(date.timetuple())
            item = {"date":unixTimestamp, "value":value}
            sensorData[sensorId].append(item)
            size += len(json.dumps(item))
        
        parameters = {"sensors":[]}
        for sensorId in sensorData:
            parameters["sensors"].append({"sensor_id":sensorId, "data":sensorData[sensorId]})
        print "Posting {} sensors to CS!".format(len(sensorData))
        errorCount = 0
        while not self.api.SensorsDataPost(parameters):
            print "Error uploading to sensor. Status code: {}. Response: {}".format(self.api.getResponseStatus(), self.api.getResponse())
            time.sleep(30)
            #give up after 3 attempts, we lose the data and move on...
            if errorCount > 3:
                print "Giving up... discarding this data and move on"
                break
        
    def run(self):
        while True:
            while self.dataQueue.qsize() > 0:
                try:
                    self.upload()
                except SSLError:
                    print "SSLError."
            time.sleep(self.interval)


class Session(object):
    def __init__(self,api):
        self.api = api
        self.dataUploader = DataUploader(api)

    def user(self, username):
        return User(username, self)

    def me(self):
        self.api.UsersGetCurrent()
        username = json.loads(self.api.getResponse())["user"]["username"]
        u = User(username, self)
        u._isMe = True
        return u
    
    def createSensorOnce(self, sensorName, description, dataType, dataStructure=None):
        try:
            sensorId = getSensorId(self.api, sensorName, description=description)
        except ValueError:
            #doesn't exist, create sensor
            par = {'sensor': {'name':sensorName, 'device_type':description, 'data_type':'dataType'}}
            if dataStructure:
                par["sensor"]["data_structure"] = dataStructure
            if self.api.SensorsPost(par):
                sensorId = self.api.getLocationId()
        return sensorId


class User(object):
    def __init__(self, username, session):
        self._session = session
        self.username = username
        self._isMe = False
        
    
def getDataFromFile(dataFile):
    json_data=open(dataFile)
    data = json.load(json_data)
    json_data.close()
    for x in data['data']:
        yield (x['date'], x['value'])
        
def getSensorIdList(api, sensorName, deviceType=None, description=None, userName=None):
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
    return correctSensors

def getSensorId(api, sensorName, deviceType=None, description=None, userName=None):
    correctSensors = getSensorIdList(api, sensorName, deviceType, description, userName)
    if len(correctSensors) == 0:
        raise ValueError("Sensor {} not found!".format(sensorName))
    
    ids = [x["id"] for x in correctSensors]
    if len(correctSensors) > 0:
        #choose the sensor with the most recent data point
        def lastDate(sensorId):
            ld = 0
            if api.SensorDataGet(sensorId,{"last":1}):
                data = json.loads(api.getResponse())["data"]
                if len(data) > 0:
                    ld = data[-1]["date"]
            return ld
        sensorDate = {x:lastDate(x) for x in ids}
	sensorId = max(sensorDate.iteritems(), key=operator.itemgetter(1))[0]
    else:
        sensorId = ids[-1]

    return sensorId


def getSensorData(api, sensorId, fromDate=None, refreshInterval=None):
    par= {'sort': 'ASC'}
    if fromDate is not None:
        par['start_date'] = time.mktime(fromDate.timetuple())
    par['per_page'] = 1000

    first = True
    while (True):
        if not api.SensorDataGet(sensorId, par): #TODO check status code
            print "Error: " + repr(api.getResponse());
            print "Waiting 30 seconds and try again"
            time.sleep(30)
            continue
        response = json.loads(api.getResponse())
        
        #yield each data point
        if first:
            for x in response['data']: yield (datetime.datetime.fromtimestamp(float(x['date'])), x['value'])
        elif len(response['data']) >= 2:
            for x in response['data'][1:]: yield (datetime.datetime.fromtimestamp(float(x['date'])), x['value'])
        
        #see whether all data is got
        nr = len(response['data'])
        if (nr < par['per_page']):
            #all data retrieved
            if refreshInterval is None:
                break
            else:
                time.sleep(refreshInterval)
                
        first = False
        if len(response['data']) > 0:
            par['start_date'] = response['data'][-1]['date']
