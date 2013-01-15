#!/usr/bin/env python
"""
	Simple script to request a check on the default states for all api keys in stdin.
"""
import senseapi
import sys


api=senseapi.SenseAPI()
def checkDefaultStates(api_key):
	print "Check for key {}".format(api_key)
	api.SetApiKey(api_key)
	if api.StatesDefaultCheck():
		print "Check ok: {}".format(api.getResponse())
	else:
		print api.__error__
		print api.getResponse()

#keys = open('users','r')
for key in sys.stdin:
	key=key[0:-1] #remove newline
	checkDefaultStates(key)
