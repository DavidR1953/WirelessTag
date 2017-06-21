#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A simple proxy server to receive Wireless Sensor Tag data(http://wirelesstag.net/)
# set to use local URL.

# With thanks to Ben Jones <ben.jones12()gmail.com> for inspiration, see:
# https://github.com/sumnerboy12/nukiproxy

from bottle import get, post, put, request, run, response, abort
import os
import sys
import ConfigParser
import json
import time
import re
import requests
import logging


# Script name (without extension) used for config/logfile names
APPNAME = os.path.splitext(os.path.basename(__file__))[0]
DIRNAME = os.path.dirname(os.path.abspath(__file__))
INIFILE = DIRNAME + '/' + APPNAME + '.ini'

# Read the config file
config = ConfigParser.RawConfigParser()
config.read(INIFILE)

# Use ConfigParser to pick out the settings
DEBUG = config.getboolean("global", "DEBUG")

PROXY_HOST = config.get("proxy", "PROXY_HOST")
PROXY_PORT = config.getint("proxy", "PROXY_PORT")
PROXY_ENDPOINT = config.get("proxy", "PROXY_ENDPOINT")

OPENHAB_HOST = config.get("openhab", "OPENHAB_HOST")
OPENHAB_PORT = config.getint("openhab", "OPENHAB_PORT")
OPENHAB_USER = config.get("openhab", "OPENHAB_USER")
OPENHAB_PASSWORD = config.get("openhab", "OPENHAB_PASSWORD")

OPENHAB_ITEM_LOCKED = config.get("openhab", "OPENHAB_ITEM_LOCKED")
OPENHAB_ITEM_STATE = config.get("openhab", "OPENHAB_ITEM_STATE")
OPENHAB_ITEM_STATENAME = config.get("openhab", "OPENHAB_ITEM_STATENAME")
OPENHAB_ITEM_BATTERYCRITICAL = config.get("openhab", "OPENHAB_ITEM_BATTERYCRITICAL")


def update_openhab(item, value):
    url = 'http://%s:%d/rest/items/%s/state' % (OPENHAB_HOST, OPENHAB_PORT, item)
    headers = { 'Content-Type': 'text/plain' }
    logging.debug('item: %s, value: %s', item, value)
    requests.put(url, headers=headers, data=value)

@get('/')
def monitor():
    response.status = 200
    return

@get('/Door/<state>/<tagName>')
def door(state, tagName):
    logging.debug('Door ' + tagName + ' ' + state)
    item = 'Door' + tagName
    update_openhab(item, state)
    
    return


@put('/Temperature/<tagName>')
def temperature(tagName):
    '''WirelessTag
        Sends a JSON PUT in the form'
         {"Temperature": 23.1234, "Humidity": 11.9876}
    '''
    try:
        try:
            data = request.json
        except:
            logging.warn(tagName + ': JSON not valid')
            raise ValueError

        if data is None:
            logging.warn(tagName + ': JSON empty')
            raise ValueError

        temperature = data['Temperature']
        humidity = data['Humidity']
        item = 'Temperature' + tagName
        update_openhab(item, str(temperature))

    except ValueError:
        response.status = 400
        return

    response.status = 200
    return


if __name__ == '__main__':

    try:
        logging.basicConfig(filename = DIRNAME + '/' + APPNAME + '.log', filemode='w', level=logging.WARN, format='%(asctime)s %(levelname)s %(message)s')
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
