import os
import sys
import time
import requests
import json
import threading as th


ip = 'localhost'    # IP address/hostname/fqdn of server that is controller
port = "3080"       # Release VM's use 80, local install, and install via PIP/APT use 3080
protocol_type = 'HTTP'      # If using HTTPS, change to True

url = f'{protocol_type}://{ip}:{port}/v2/'

# Define colors
c_red = '\33[31m'
c_green = '\33[32m'
c_default = '\33[0m'

# Define header row
a = 'COMPUTE: '
b = ' | STATUS:'
c = ' | CPU:'
d = ' | RAM:'
e = '=========================================='

if os.name == 'nt':
    import msvcrt
    import ctypes

    class _CursorInfo(ctypes.Structure):
        _fields_ = [("size", ctypes.c_int),
                    ("visible", ctypes.c_byte)]

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

clear_cmd = get_screen_clear_cmd()
keep_going = True
hide_cursor()
th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
while keep_going:

    try:
        resp = get_json_resp('computes')

        # Print header row
        print(f'\n{a:15}{b:10}{c:8}{d:8}\n{e}')

        # Extract, format and print to console applicable data for status
        for compute in range(len(resp)):
            host = resp[compute]['name']
            if resp[compute]['connected']:
                status = c_green + 'UP' + c_default
            else: status = c_red + 'DOWN' + c_default
            cpu = resp[compute]['cpu_usage_percent']
            ram = resp[compute]['memory_usage_percent']
            print(f'{host:15} | {status:16} | {cpu:4}% | {ram:4}%')
        
        print('\nPress [ENTER] to quit')
        time.sleep(1)
        os.system(clear_cmd)

    except:
        print('\nError: Failed most likely due to not being able to establish a connection')
        show_cursor()

print('Exiting')
show_cursor()
