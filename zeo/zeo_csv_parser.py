#!/usr/bin/env python
'''
@author: jg@sense-os.nl
'''
import senseapi
import json
import time
import datetime
import csv
from pprint import pprint
from StringIO import StringIO


def get_zq(csv_filename):
    zeoIO = StringIO()
    zqlist = []
    
    with open(csv_filename, 'rb') as csvfile:
        zeoreader = csv.reader(csvfile )
        zeoreader.next();
        for row in zeoreader:
            # print ', '.join(row)
            d = datetime.datetime.strptime(str(row[0]),"%m/%d/%Y")
            d += datetime.timedelta(days=1)
            
            # print "raw:" + str(row[0]) + ":" + str(row[1])
            # print "date:"+str(d)
            ts = time.mktime(d.timetuple())
            # print "timestamp:" + str( ts)
            zqlist.append({"value":int(row[1]), "date":ts })

    # print ar
    # with open('sensified-zeo-data.json', 'w') as outfile:
        # json.dump(ar, outfile)
    return zqlist;


def get_graph(csv_filename):
    """Graph data exists in two ways.
    csv col 74 = one data point per 5 min
    csv col 75 = one data point per 30 sec
    """

    zeoIO = StringIO()
    graphlist = []

    with open(csv_filename,'rb') as csvfile:
        zeoreader = csv.reader(csvfile)
        
        #skip header
        zeoreader.next();

        for row in zeoreader:
            start = datetime.datetime.strptime(str(row[9]),"%m/%d/%Y %H:%M")
            
            data = str(row[75]).split(" ")
            for i, score in enumerate(data):
                t = start + datetime.timedelta(seconds=30*i)
                ts = time.mktime(t.timetuple())
                graphlist.append({"value":int(score), "date":ts})

    return graphlist;


def list_to_json_file(filename,data):
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)

def list_to_json_str(data):
    sio = StringIO()
    json.dump(data,sio)
    return sio.getvalue()

def main():
    import sys
    
    if len(sys.argv) != 3:
        print "Error, standalone usage: {} csv_filename data_type (either 'zq' or 'graph')".format(sys.argv[0])
        sys.exit(-1)
    
    if sys.argv[2] == 'zq':
        print str( get_zq( sys.argv[1] ) );
    elif sys.argv[2] == 'graph':
        print str( get_graph( sys.argv[1] ) );
    else:
        print "Unknown type: use 'graph' or 'zq'"
        sys.exit(-1)


if __name__ == '__main__':
    main()
