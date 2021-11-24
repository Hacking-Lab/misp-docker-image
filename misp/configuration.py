
import json
from pymisp import ExpandedPyMISP, MISPUser, MISPServer, PyMISP, MISPOrganisation, MISPEvent
import time
import subprocess
import os
import requests
import uuid

misp_url = "http://localhost/"
misp_verifycert = False

default_nickname = "investigator"
default_pw = "compass"
admin_nickname = "admin"
admin_pw = "lab-admin"

labs_count = 10

def getVitalSigns():
    r = requests.get('http://localhost/users/login')

def getKey(email):
    subprocess.getoutput("/var/www/MISP/app/Console/cake Admin change_authkey "+ email +" | sed '1d'")
    misp_key = subprocess.getoutput("/var/www/MISP/app/Console/cake user change_authkey "+ email +" | cut -d ':' -f 2 | cut -d ' ' -f 2")
    return misp_key

def adminApiSession(misp_key):
    global misp 
    misp = PyMISP(misp_url, misp_key, misp_verifycert)

# Setup server
def updateInstance():
    misp.update_object_templates()
    misp.update_galaxies()
    misp.update_taxonomies()
    #misp.enable_taxonomy('tlp')

def setServerSettings():
    misp.set_server_setting("Security.password_policy_length", 7, True)
    misp.set_server_setting("Security.password_policy_complexity", "/(a-z)*/", True)
    misp.set_server_setting("MISP.main_logo", "logo.png", True)
    misp.set_server_setting("MISP.welcome_text_top","Welcome to Malware Information Sharing Platform " ,True)
    #set event attribute sharing type

# Create organizations
def createOrg(orgname):
    org = MISPOrganisation()
    org.name = orgname
    org.nationality = "Switzerland"
    org.local = True
    misp.add_organisation(org, pythonify=True)

# Create user
def createUser(email, orgId, role, password):
    user = MISPUser()
    user.email = email
    user.org_id = orgId
    user.role_id = role
    user.password = password
    user.change_pw = 0
    misp.add_user(user, pythonify=True)

# import events for every lab
def importEvents(apiKey, lab):
        
    labApiSession = PyMISP(misp_url, apiKey, misp_verifycert)
    lab_name = 'Lab_' + str(lab)

    # open json file with events
    try:
        with open ('./' + lab_name + '.json', 'r') as f:
            for e in f:
                events = json.loads(e)
            print('found file ' + lab_name)
    except:
        print('cannot find file ' + lab_name)
        return

    # find correct lab org uuid
    org = misp.get_organisation(lab + 1)
    org_id = org['Organisation']['id']
    org_name = org ['Organisation']['name']
    org_uuid = org['Organisation']['uuid']
    
    # edit file
    for event in range(len(events['response'])):
        # set new event uuids
        events['response'][event]['Event']['uuid'] = uuid.uuid4()
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
        labApiSession.add_event(events['response'][event])

def addSyncServer(id, name, url, org, push, pull, remote_org_id):
    server = MISPServer()
    server.id = id
    server.name = name
    server.url = url
    server.org_id = org
    server.push = push
    server.pull = pull
    server.remote_org_id = remote_org_id
    server.self_signed = True
    misp.add_server(server)


def cleanup():
    # remove initalisation user + org
    misp.delete_user(1)
    misp.delete_organisation(1)

    # remove itself from supervisord.conf
    lines = []
    path = "/etc/supervisor/conf.d/supervisord.conf"
    with open(path, 'r') as fp:
        lines = fp.readlines()

    with open(path, 'w') as fp:
        for number, line in enumerate(lines):
            if number not in [29, 36]:
                fp.write(line)

x = True
while x:
    try:
        time.sleep(10)
        getVitalSigns()
        misp_key = getKey('admin@admin.test')
        adminApiSession(misp_key)
        x = False
    except:
        x = True

updateInstance()
setServerSettings()


#################### LAB CONFIGURATION ####################

# Instance Admin
createOrg(orgname='instance-admin')
misp.get_organisation('instance-admin')
createUser(email='instance-admin@misp-lab.com', orgId=2, role=1, password=default_pw)

# Lab 1 (Introduction)
if os.environ['MISP_BASEURL'] == "http://instance-a.misp.localhost":
    createOrg(orgname='lab1')
    createUser(email=default_nickname + '@misp-lab1.com', orgId=3, role=3, password=default_pw)

# Lab 2 (Phishing)
if os.environ['MISP_BASEURL'] == "http://instance-a.misp.localhost":
    createOrg(orgname='lab2')
    createUser(email=default_nickname + '@misp-lab2.com', orgId=4, role=3, password=default_pw)

# Lab 3 (Sandbox)
if os.environ['MISP_BASEURL'] == "http://instance-a.misp.localhost":
    createOrg(orgname='lab3')
    createUser(email=default_nickname + '@misp-lab3.com', orgId=5, role=3, password=default_pw)

# Lab 4 (API)
if os.environ['MISP_BASEURL'] == "http://instance-a.misp.localhost":
    createOrg(orgname='lab4')
    createUser(email=default_nickname + '@misp-lab4.com', orgId=6, role=3, password=default_pw)

# Lab 5 (MITRE ATT&CK)
if os.environ['MISP_BASEURL'] == "http://instance-a.misp.localhost":
    createOrg(orgname='lab5')
    createUser(email=admin_nickname + '@misp-lab5.com', orgId=7, role=2, password=default_pw)
    createUser(email=default_nickname + '@misp-lab5.com', orgId=7, role=3, password=default_pw)
    importEvents(lab=5, apiKey=getKey(email=admin_nickname + '@misp-lab5.com'))

# Lab 6 (Organization Sync)
if os.environ['MISP_BASEURL'] == "http://instance-a.misp.localhost":
    createOrg(orgname='lab6-org-A')
    createUser(email=admin_nickname + '-org-a@instance-a.misp-lab6.com', orgId=8, role=2, password=default_pw)
    createUser(email=default_nickname + '-org-a@instance-a.misp-lab6.com', orgId=8, role=3, password=default_pw)
    createUser(email=admin_nickname + '-org-a@instance-a.misp-lab6.com', orgId=8, role=4, password=default_pw)

    createOrg(orgname='lab6-org-B')
    createUser('admin-org-b@instance-a.misp-lab6.com', orgId=9, role=2, password=default_pw)
    createUser(email=default_nickname + '-org-b@instance-a.misp-lab6.com', orgId=9, role=3, password=default_pw)
    createUser(email='publisher-org-b@instance-a.misp-lab6.com', orgId=9, role=4, password=default_pw)
    importEvents(lab=6, apiKey=getKey(email=admin_nickname + '-org-b@instance-a.misp-lab6.com'))

if os.environ['MISP_BASEURL'] == "http://instance-b.misp.localhost":
    createOrg(orgname='lab6-org-F')
    createUser(email=admin_nickname + '-org-f@instance-b.misp-lab6.com', orgId=3, role=2, password=default_pw)
    createUser(email=default_nickname + '-org-f@instance-b.misp-lab6.com', orgId=3, role=3, password=default_pw)
    createUser(email='publisher-org-f@instance-b.misp-lab6.com', orgId=3, role=4, password=default_pw)

if os.environ['MISP_BASEURL'] == "http://instance-c.misp.localhost":
    createOrg(orgname='lab6-org-E')
    createUser(email=admin_nickname + '-org-e@instance-c.misp-lab6.com', orgId=3, role=2, password=default_pw)
    createUser(email=default_nickname + '-org-e@instance-c.misp-lab6.com', orgId=3, role=3, password=default_pw)
    createUser(email='publisher-org-e@instance-c.misp-lab6.com', orgId=3, role=4, password=default_pw)
    addSyncServer(id=2, name="Instance B", url="http://misp-instance-B", org=2, pull=True, push=False, remote_org_id=4)



# Lab 7 (Sharing Correlation)
if os.environ['MISP_BASEURL'] == "http://instance-a.misp.localhost":
    createOrg(orgname='lab7')
    createUser(email=default_nickname + '@misp-lab7.com', orgId=10, role=3, password=default_pw)

# Lab 8 (IDS / Snort)
if os.environ['MISP_BASEURL'] == "http://instance-a.misp.localhost":
    createOrg(orgname='lab8')
    createUser(email=default_nickname + '@misp-lab8.com', orgId=11, role=3, password=default_pw)

# Lab 9 (Modules)
if os.environ['MISP_BASEURL'] == "http://instance-a.misp.localhost":
    createOrg(orgname='lab9')
    createUser(email=default_nickname + '@misp-lab9.com', orgId=12, role=3, password=default_pw)



#################### LAB CONFIGURATION ####################

#cleanup()
os.system("cp /logo.png /var/www/MISP/app/webroot/img/custom/logo.png")
