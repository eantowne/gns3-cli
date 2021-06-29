import os
import time
import requests
import json

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

def get_json_resp(api_call):

    r = ''

    try:

        r = requests.get(url + api_call)

        if r.status_code == 200:

            # Convert response from controller into JSON Dict
            return json.loads(json.dumps(r.json()))
        
        else: print(f'Invalid response code "{r.status_code}" from controller at: {url}')

    except:
        exit('\nError: Failed most likely due to not being able to establish a connection')

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

except:
    print('\nError: Failed most likely due to not being able to establish a connection')
