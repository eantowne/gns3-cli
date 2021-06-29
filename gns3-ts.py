from sys import exit
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
a = 'NODE: '
b = ' | STATUS:'
c = '| CONSOLE'
d = '=========================================='

project_id = ''
project_name = ''

def get_json_resp(api_call):

    r = ''

    try:

        r = requests.get(url + api_call)

        if r.status_code == 200:

            # Convert response from controller into JSON Dict
            return json.loads(json.dumps(r.json()))
        
        else: print(f'Invalid response code "{r.status_code}" from controller at: {url}')

    except:
        exit('Error: Failed most likely due to not being able to establish a connection')

def get_open_project():

    resp = get_json_resp('projects')
    for project in range(len(resp)):

        #print(resp[project]['status'])
        
        if resp[project]['status'] == 'opened':
           
            return resp[project]['project_id'], resp[project]['name']

        else:

            return 'closed'

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

if get_open_project() == 'closed':
    
    exit('\nNo open project, please open one and retry.')
    
else:

    project = get_open_project()
    project_id = project[0]
    project_name = project[1]
    print(f'\nCurrently open project: {c_green + project[1] + c_default:15}\nUUID: {project[0]}\n')

print_nodes(project_id)
