#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A simple proxy server to receive Wireless Sensor Tag data(http://wirelesstag.net/)
# set to use local URL.

# With thanks to Ben Jones <ben.jones12()gmail.com> for inspiration, see:
# https://github.com/sumnerboy12/nukiproxy

import os
import sys
import ConfigParser
import logging
import requests
from bottle import get, put, request, run, response

#Test change
# Script name (without extension) used for config/logfile names
APPNAME = os.path.splitext(os.path.basename(__file__))[0]
DIRNAME = os.path.dirname(os.path.abspath(__file__))
INIFILE = DIRNAME + '/' + APPNAME + '.ini'

# Read the config file
config = ConfigParser.RawConfigParser()
config.read(INIFILE)

# Use ConfigParser to pick out the settings
DEBUG = config.getboolean("global", "DEBUG")
PROXY_PORT = config.getint("proxy", "PROXY_PORT")
OPENHAB_HOST = config.get("openhab", "OPENHAB_HOST")
OPENHAB_PORT = config.getint("openhab", "OPENHAB_PORT")

def updateOpenhab(item, value):
    url = 'http://%s:%d/rest/items/%s/state' % (OPENHAB_HOST, OPENHAB_PORT, item)
    headers = {'Content-Type': 'text/plain'}
    logging.debug('item: %s, value: %s', item, value)
    requests.put(url, headers=headers, data=value)

@get('/')
def monitor():
    response.status = 200

@get('/Door/<state>/<tagName>')
def door(state, tagName):
    logging.debug('Door ' + tagName + ' ' + state)
    item = 'Door' + tagName
    updateOpenhab(item, state)

@put('/Temperature/<tagName>')
def temperature(tagName):
    '''
    WirelessTag sends a JSON PUT like this:
         {"Temperature": 23.1234, "Humidity": 11.9876}
    '''
    try:
        try:
            dat = request.json
        except:
            logging.warning(tagName + ': JSON not valid')
            raise ValueError

        if dat is None:
            logging.warning(tagName + ': JSON empty')
            raise ValueError

        temp = dat['Temperature']
        humidity = dat['Humidity']
        item = 'Temperature' + tagName
        updateOpenhab(item, str(temp))

    except ValueError:
        response.status = 400

    response.status = 200


if __name__ == '__main__':

    try:
        logging.basicConfig(filename = DIRNAME + '/' + APPNAME + '.log', filemode='a', level=logging.WARN, format='%(asctime)s %(levelname)s %(message)s')
        logging.warn('Starting up')
        logging.debug('APPNAME: %s', APPNAME)
        logging.debug('DIRNAME: %s', DIRNAME)
        logging.debug('INIFILE: %s', INIFILE)

        run(host='0.0.0.0', port=PROXY_PORT, quiet=True)
#        run(host='0.0.0.0', port=PROXY_PORT, debug=True, reloader=True)

    except KeyboardInterrupt:
        sys.exit(0)
    except:
        raise
