#!/bin/sh
ifconfig wlan0 down
ifconfig wlan0 promisc
iwconfig wlan0 mode monitor
ifconfig wlan0 up
tcpdump -l -i wlan0 -e -tttt type mgt and not type mgt subtype beacon |tee wifi_scan.log |python mac.py
