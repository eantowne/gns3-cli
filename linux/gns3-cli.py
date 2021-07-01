#!/usr/bin/env python3

import os
import sys
import time
import requests
import json
import argparse
import threading as th

if os.name == 'nt':

    import msvcrt
    import ctypes

    class _CursorInfo(ctypes.Structure):
        _fields_ = [("size", ctypes.c_int),
                    ("visible", ctypes.c_byte)]

parser = argparse.ArgumentParser()
parser.add_argument('address', type=str, help='ip/host Name/FQDN the controller is running on')
parser.add_argument('port', type=str, help='port number the controller is running on', )
parser.add_argument('interval', type=int, help='refresh interval in seconds')
args = parser.parse_args()
protocol_type = 'HTTP'      # If using HTTPS, change to True

url = f'{protocol_type}://{args.address}:{args.port}/v2/'

# Define colors
c_red = '\33[31m'
c_green = '\33[32m'
c_default = '\33[0m'