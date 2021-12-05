from pymisp import ExpandedPyMISP, MISPUser, MISPServer, PyMISP, MISPOrganisation, MISPEvent
import time
import subprocess
import os
import requests
from lab import Lab
from role import Role

misp_url = "http://localhost/"
misp_verifycert = False

# def getVitalSigns():
#     r = requests.get('http://localhost/users/login')

def getApiKey(email):
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
    # misp.enable_taxonomy('tlp')
    misp.update_warninglists()
    misp.get_user(1, True)

def setServerSettings():
    misp.set_server_setting("Security.password_policy_length", 7, True)
    misp.set_server_setting("Security.password_policy_complexity", "/(a-z)*/", True)
    misp.set_server_setting("MISP.main_logo", "logo.png", True)
    misp.set_server_setting("MISP.welcome_text_top", "Welcome to Malware Information Sharing Platform ", True)

# Create organizations
# def createOrg(orgname):
#     org = MISPOrganisation()
#     org.name = orgname
#     org.nationality = "Switzerland"
#     org.local = True
#     misp.add_organisation(org, pythonify=True)


# def createExternalOrg(orgname):
#     org = MISPOrganisation()
#     org.name = orgname
#     org.nationality = "Switzerland"
#     org.local = False
#     misp.add_organisation(org, pythonify=True)

# Create user
# def createUser(email, orgId, role, password):
#     user = MISPUser()
#     user.email = email
#     user.org_id = orgId
#     user.role_id = role
#     user.password = password
#     user.change_pw = 0
#     misp.add_user(user, pythonify=True)

# import events for every lab
# def importEvents(apiKey, lab):
#
# labApiSession = PyMISP(misp_url, apiKey, misp_verifycert)
# lab_name = 'Lab_' + str(lab)
#
# # open json file with events
# try:
#     with open ('./' + lab_name + '.json', 'r') as f:
#         for e in f:
#             events = json.loads(e)
#         print('found file ' + lab_name)
# except:
#     print('cannot find file ' + lab_name)
#     return
#
# # find correct lab org uuid
# org = misp.get_organisation(lab + 1)
# org_id = org['Organisation']['id']
# org_name = org ['Organisation']['name']
# org_uuid = org['Organisation']['uuid']
#
# # edit file
# for event in range(len(events['response'])):
#     # set new event uuids
#     events['response'][event]['Event']['uuid'] = uuid.uuid4()
#     events['response'][event]['Event']['orgc_id'] = org_id
#     events['response'][event]['Event']['org_id'] = org_id
#     # edit org
#     events['response'][event]['Event']['Org']['id'] = org_id
#     events['response'][event]['Event']['Org']['name'] = org_name
#     events['response'][event]['Event']['Org']['uuid'] = org_uuid
#     # edit orgC
#     events['response'][event]['Event']['Orgc']['id'] = org_id
#     events['response'][event]['Event']['Orgc']['name'] = org_name
#     events['response'][event]['Event']['Orgc']['uuid'] = org_uuid
#     for attribute in range(len(events['response'][event]['Event']['Attribute'])):
#         events['response'][event]['Event']['Attribute'][attribute]['uuid'] = uuid.uuid4()
#     # upload file
#     labApiSession.add_event(events['response'][event])

# def addSyncServer(name, url, remote_org_id):
#     server = {"Server": {'name': name, 'url': url, 'uuid': '0ac33559-ad37-4147-b61d-95df6ab76920', 'authkey': "aaaaaasaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", 'self_signed': 'True', 'pull': True, 'remote_org_id': remote_org_id}}
#     misp.add_server(server)


# def cleanup():
#     # remove initalisation user + org
#     # misp.delete_user(1)
#     # misp.delete_organisation(1)
#
#     # remove itself from supervisord.conf
#     lines = []
#     path = "/etc/supervisor/conf.d/supervisord.conf"
#     with open(path, 'r') as fp:
#         lines = fp.readlines()
#
#     with open(path, 'w') as fp:
#         for line in lines:
#             if line == "[program:configuration]\n":
#                 break
#             else:
#                 fp.write(line)


x = True
while x:
    try:
        time.sleep(10)
        misp_key = getApiKey('admin@admin.test')
        adminApiSession(misp_key)
        x = False
    except:
        x = True

updateInstance()
setServerSettings()

# --------------------  LAB CONFIGURATION  -------------------- #

# Lab 0: Instance Admin Configuration
lab0 = Lab(0, misp)
lab0.add_org()
lab0.add_user(Role.admin)

# Lab 1: Introduction
lab1 = Lab(1, misp)
lab1.add_org()
lab1.add_user(Role.investigator)

# Lab 2: Phishing E-Mail
lab2 = Lab(2, misp)
lab2.add_org()
lab2.add_user(Role.investigator)

# Lab 3: Malware
lab3 = Lab(3, misp)
lab3.add_org()
lab3.add_user(Role.investigator)

# Lab 4: API
lab4 = Lab(4, misp)
lab4.add_org()
lab4.add_user(Role.investigator)

# Lab 5: MISP Visualisation
lab5 = Lab(5, misp)
lab5.add_org()
lab5.add_user(Role.org_admin)
lab5.add_user(Role.investigator)
lab5.import_events(lab5.get_admin())

# Lab 6: Synchronisation
# TODO: Implement if else statement for Lab instance
lab6_a = Lab(6, misp, "A")
lab6_a.add_org('lab6-org-A')
lab6_a.add_user(Role.org_admin)
lab6_a.add_user(Role.publisher)
lab6_a.add_user(Role.investigator)
lab6_a.import_events(lab6_a.get_admin())

lab6_b = Lab(6, misp, "B")
lab6_b.add_org('lab6-org-B')
lab6_b.add_user(Role.org_admin, 'lab6-org-B')
lab6_b.add_user(Role.publisher, 'lab6-org-B')
lab6_b.add_user(Role.investigator, 'lab6-org-B')
lab6_b.add_org('lab6-org-F')
lab6_b.add_user(Role.org_admin, 'lab6-org-F')
lab6_b.add_user(Role.publisher, 'lab6-org-F')
lab6_b.add_user(Role.investigator, 'lab6-org-F')
lab6_b.add_user(Role.sync_user, 'lab6-org-F')

lab6_e = Lab(6, misp, "E")
lab6_e.add_org('lab6-org-E')
lab6_e.add_user(Role.admin,'lab6-org-E')
lab6_e.add_user(Role.investigator, 'lab6-org-E')
# TODO: Refactor this part
lab6_e.add_org('PLEASE-REPLACE-ME', False)
lab6_e.add_sync_server('Instance-B', 'http://misp-instance-B', 4)

# Lab 7: MISP Modules
lab7 = Lab(7, misp)
lab7.add_org('lab7-org-A')
lab7.add_user(Role.org_admin, 'lab7-org-A')
lab7.add_user(Role.investigator, 'lab7-org-A')
lab7.import_events(lab7.get_admin(0))

lab7.add_org('lab7-org-B')
lab7.add_user(Role.org_admin, 'lab7-org-B')
lab7.add_user(Role.investigator, 'lab7-org-B')
lab7.import_events(lab7.get_admin(1))
lab7.add_configuration()

# Lab 8: Warninglist
lab8 = Lab(8, misp)
lab8.add_org()
lab8.add_user(Role.org_admin)
lab8.add_user(Role.investigator)  # TODO @JW: Are higher privileges needed?

# --------------------  LAB CONFIGURATION  -------------------- #

os.system("cp /logo.png /var/www/MISP/app/webroot/img/custom/logo.png")
print(" -------------------- Configuration complete -------------------- ")
# if os.environ['MISP_BASEURL'] == "http://instance-a.misp.localhost":
