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

# Define header row
a = 'NODE: '
b = ' | STATUS:'
c = '| CONSOLE'
d = '=========================================='

def hide_cursor():

    if os.name == 'nt':
        ci = _CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = False
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == 'posix':
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

def show_cursor():

    if os.name == 'nt':
        ci = _CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = True
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == 'posix':
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

def get_screen_clear_cmd():

    if os.name == 'posix': 
        return 'clear'
    else:
        return 'cls'

def key_capture_thread():

    global keep_going
    input()
    keep_going = False

project_id = ''
project_name = ''

def get_json_resp(api_call):

    r = ''

    try:
        r = requests.get(url + api_call)
        if r.status_code == 200:
            # Convert response from controller into JSON Dict
            return json.loads(json.dumps(r.json()))        
        else: exit(f'Invalid response code "{r.status_code}" from controller at: {url}')

    except:
        exit('\nError: Failed most likely due to not being able to establish a connection')

def get_open_project():

    resp = get_json_resp('projects')
    for project in range(len(resp)):

        #print(resp[project]['status'])
        status = 'closed'
        if resp[project]['status'] == 'opened':
           
            return resp[project]['project_id'], resp[project]['name']

    if status == 'closed': return 'closed'



def print_nodes(uuid):

    print(f'{a:25}{b:8}{c}\n{d}')

    apicall = 'projects/' + uuid + '/nodes'
    resp = get_json_resp(apicall)

    if len(resp) < 1:

        exit('\nThis project has no nodes.')

    for node in range(len(resp)):

        name = resp[node]['name']
        if resp[node]['status'] == 'started':
            status = c_green + 'UP' + c_default
        else: status = c_red + 'DOWN' + c_default
        console_type = resp[node]['console_type']
        if console_type == 'none':
            console_port = ''
        else:
            console_port = resp[node]['console']

        print(f'{name:25} | {status:15} | {console_type:15} {console_port}')


clear_cmd = get_screen_clear_cmd()
keep_going = True
hide_cursor()
os.system(clear_cmd)
th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()

while keep_going:

    try:

        if get_open_project() == 'closed':
    
            print('\nNo open project, please open one and retry.')
            break
        
        else:

            project = get_open_project()
            project_id = project[0]
            project_name = project[1]
            print(f'\nCurrently open project: {c_green + project[1] + c_default:15}\n')
            print_nodes(project_id)
            print('\nPress [ENTER] to quit')
            time.sleep(args.interval)
            os.system(clear_cmd)

    except:

        print(f'\nError: Failed to connect to server: {args.address}:{args.port} most likely due to not being able to establish a connection')
        show_cursor()
        break

print('Exiting')
show_cursor()