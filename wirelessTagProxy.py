#! python3
# -*- coding: utf-8 -*-

# A simple proxy server to receive Wireless Sensor Tag data(http://wirelesstag.net/)
# set to use local URL.

# With thanks to Ben Jones <ben.jones12()gmail.com> for inspiration, see:
# https://github.com/sumnerboy12/nukiproxy

import os
import sys
import logging
import requests
from bottle import get, put, request, run, response

# Script name (without extension) used for config/logfile names
APPNAME = os.path.splitext(os.path.basename(__file__))[0]
DIRNAME = os.path.dirname(os.path.abspath(__file__))
INIFILE = DIRNAME + "/" + APPNAME + ".ini"

DEBUG = True
PROXY_PORT = 9090
OPENHAB_PORT = 8080


def updateOpenhab(item, value):
    url = f"http://localhost:{OPENHAB_PORT}/rest/items/{item}/state"
    headers = {"Content-Type": "text/plain"}
    logging.debug(f"item: {item}, value: {value}")
    requests.put(url, headers=headers, data=value)


@get("/")
def monitor():
    response.status = 200


@get("/Door/<state>/<tagName>")
def door(state, tagName):
    logging.debug("Door " + tagName + " " + state)
    item = "Door" + tagName
    updateOpenhab(item, state)


@put("/Temperature/<tagName>")
def temperature(tagName):
    """
    WirelessTag sends a JSON PUT like this:
         {"Temperature": 23.12, "Humidity": 11.98, 'Battery': 2.86}
    """
    logging.debug(f"temperature, {tagName}")

    temp = request.json["Temperature"]
    item = "Temperature" + tagName
    updateOpenhab(item, str(temp))

    battery = request.json["Battery"]
    # Battery voltage is 2.5 for 0%, and 3.1 for 100%
    base = battery - 2.5
    if base < 0:
        base = 0
    percent = int(base * 100 / 0.6)
    item = "Battery" + tagName
    updateOpenhab(item, str(percent))

    # humidity = request.json["Humidity"]


if __name__ == "__main__":

    try:
        logging.basicConfig(
            filename=DIRNAME + "/" + APPNAME + ".log",
            filemode="a",
            level=logging.DEBUG if DEBUG else logging.WARN,
            format="%(asctime)s %(levelname)s %(message)s",
        )
        logging.warning("Starting up")
        logging.debug("APPNAME: %s", APPNAME)
        logging.debug("DIRNAME: %s", DIRNAME)

        if DEBUG:
            run(host="0.0.0.0", port=PROXY_PORT, debug=True, reloader=True)
        else:
            run(host="0.0.0.0", port=PROXY_PORT, quiet=True)

    except KeyboardInterrupt:
        logging.debug("Exit by Ctrl-C")
        sys.exit(0)
