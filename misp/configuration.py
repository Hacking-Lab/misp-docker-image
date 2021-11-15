
import json
from pymisp import ExpandedPyMISP, MISPUser, MISPServer, PyMISP, MISPOrganisation, MISPEvent
import time
import subprocess
import uuid

misp_url = "http://localhost/"
misp_key = subprocess.getoutput("/var/www/MISP/app/Console/cake user change_authkey 1 | cut -d ':' -f 2 | cut -d ' ' -f 2")
#misp_key = "wK4t1jDRa9u9OKEz2TOPtvGv8t9i93vCbxEB3MCp"
misp_verifycert = False

default_nickname = "investigator"
default_pw = "compass"
labs_count = 10

misp = PyMISP(misp_url, misp_key, misp_verifycert)


# Setup server
def setServerSettings():
    misp.set_server_setting("Security.password_policy_length", 7, True)
    misp.set_server_setting("Security.password_policy_complexity", "/(a-z)*/", True)
    misp.set_server_setting("MISP.main_logo", "logo.png", True)
    misp.set_server_setting("MISP.welcome_text_top","Welcome to Malware Information Sharing Platform " ,True)

# Create organizations
def createOrg():
    for i in range(labs_count):
        org = MISPOrganisation()
        org.name = 'Lab_' + str(i+1)
        org.nationality = "Switzerland"
        org.local = True
        misp.add_organisation(org, pythonify=True)


# Create users
def createUsers():
    for i in range(labs_count):
        user = MISPUser()
        user.email = default_nickname + '@misp-lab' + str(i+1) + '.com'
        user.org_id = i+2 #offset -> org 1 = admin org
        user.role_id = 3
        user.password ="compass"
        user.change_pw = 0
        misp.add_user(user, pythonify=True)

def createUser():
    user = MISPUser()
    user.email = default_nickname + '@misp-lab99.com'
    user.org_id = 3 #offset -> org 1 = admin org
    user.role_id = 3
    user.password ="compass"
    user.change_pw = 0
    print(misp.add_user(user, pythonify=True))

# import MISP events from export File
def importEventsFromFile(path):
    with open(path, 'r') as f:
        for e in f:
            event = json.loads(e)
    
    for i in range(len(event['response'])):
        event['response'][i]['Event']['uuid'] = ""
        event['response'][i]['Event']['Attribute'][0]['uuid'] = ""
        misp.add_event(event['response'][i])



# import events for every lab
def importEvents():
    for lab in range(labs_count):
        current_lab = 'Lab_' + str(lab + 1)

        # open json file with events
        try:
            with open ('/' + current_lab + '.json', 'r') as f:
                for e in f:
                    events = json.loads(e)
                print('found file ' + current_lab)
        except:
            print('cant find file' + current_lab)
            continue

        # find correct lab org uuid
        org = misp.get_organisation(lab + 2)
        org_id = org['Organisation']['id']
        org_name = org ['Organisation']['name']
        org_uuid = org['Organisation']['uuid']
        
        # edit file
        for event in range(len(events['response'])):
            # remove event uuid
            events['response'][event]['Event']['uuid'] = ""
            events['response'][event]['Event']['orgc_id'] = org_id
            events['response'][event]['Event']['org_id'] = org_id
            
            # edit org
            events['response'][event]['Event']['Org']['id'] = org_id
            events['response'][event]['Event']['Org']['name'] = org_name
            events['response'][event]['Event']['Org']['uuid'] = org_uuid
            # edit orgC
            events['response'][event]['Event']['Orgc']['id'] = org_id
            events['response'][event]['Event']['Orgc']['name'] = org_name
            events['response'][event]['Event']['Orgc']['uuid'] = org_uuid

    # upload file
            print(misp.add_event(events['response'][event]))


time.sleep(10)
setServerSettings()
createOrg()
createUsers()
importEvents()
# createUser()