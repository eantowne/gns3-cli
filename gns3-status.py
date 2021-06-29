import os
import sys
import time
import requests
import json
import argparse
import threading as th

parser = argparse.ArgumentParser()
parser.add_argument('address', type=str, help='ip/host Name/FQDN the controller is running on')
parser.add_argument('port', type=str, help='port number the controller is running on', )
parser.add_argument('interval', type=int, help='refresh interval in seconds')
args = parser.parse_args()

protocol_type = 'http'      # If using HTTPS, change to True

url = f'{protocol_type}://{args.address}:{args.port}/v2/'

# Define colors
c_red = '\33[31m'
c_green = '\33[32m'
c_yellow = '\33[33m'
c_default = '\33[0m'

# Define header row
a = 'COMPUTE: '
b = ' | STATUS:'
c = ' | CPU:'
d = ' | RAM:'
e = '=========================================='

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

# =========================================================================================

if os.name == 'nt':

    import msvcrt
    import ctypes

    class _CursorInfo(ctypes.Structure):
        _fields_ = [("size", ctypes.c_int),
                    ("visible", ctypes.c_byte)]

clear_cmd = get_screen_clear_cmd()


#exit()

keep_going = True
hide_cursor()
os.system(clear_cmd)
th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()

while keep_going:

    try:

        resp = get_json_resp('version')
        version = resp['version']
        print(f'\nController: {args.address}\nVersion: {version:20}')
        resp = get_json_resp('computes')

        # Print header row
        print(f'\n{a:15}{b:10}{c:8}{d:8}\n{e}')

        # Extract, format and print to console applicable data for status
        for compute in range(len(resp)):

            host = resp[compute]['name']

            if resp[compute]['connected']:
                status = c_green + 'UP' + c_default
            else:               
                status = c_red + 'DOWN' + c_default

            cpu = resp[compute]['cpu_usage_percent']

            if int(cpu) > 85:
                cpu = c_red + str(cpu) + '%' + c_default
            elif int(cpu) > 50:
                cpu = c_yellow + str(cpu) + '%' +  c_default
            else:    
                cpu = c_green + str(cpu) + '%' +  c_default

            ram = resp[compute]['memory_usage_percent']

            if ram > 85:
                ram = c_red + str(ram) + '%' +  c_default
            elif ram > 50:
                ram = c_yellow + str(ram) + '%' +  c_default
            else:
                ram = c_green + str(ram) + '%' +  c_default

            print(f'{host:15} | {status:16} | {cpu:4} | {ram:4}')
        
        print('\nPress [ENTER] to quit')
        time.sleep(args.interval)
        os.system(clear_cmd)

    except:
        print(f'\nError: Failed to connect to server: {args.address}:{args.port} most likely due to not being able to establish a connection')
        show_cursor()
        break

print('Exiting')
show_cursor()
