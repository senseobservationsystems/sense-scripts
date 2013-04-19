#!/usr/bin/env python
'''
@author jg@sense-os.nl
'''

import sense_helpers
import zeo_csv_parser


def upload_graph(csv_filename):

    data = zeo_csv_parser.get_graph( csv_filename )
    # print("test:"+json_str)
    sense_helpers.initSense()
    sensor_id = sense_helpers.createSensorOnce("zeo_graph_30sec","zeo value for every 30 seconds (0:undefined, 1:Wake, 2:REM, 3:Light, 4:Deep)","integer")
    sense_helpers.postData(sensor_id,data)

def upload_zq(csv_filename):
    data = zeo_csv_parser.get_zq( csv_filename )
    sense_helpers.initSense()
    sensor_id = sense_helpers.createSensorOnce("zeo_zq", "zeo zq scores per night","integer")
    sense_helpers.postData(sensor_id,data)

if __name__ == '__main__':
    import sys;

    if len(sys.argv) != 3:
        print "Error, usage: {} csv_filename data_type (either 'zq' or 'graph')".format(sys.argv[0])
    
    if sys.argv[2] == 'graph':
        upload_graph(sys.argv[1]) 
    elif sys.argv[2] == 'zq':
        upload_zq(sys.argv[1]) 
