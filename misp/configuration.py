
import json
from pymisp import ExpandedPyMISP, MISPUser, MISPServer, PyMISP, MISPOrganisation, MISPEvent
import time
import subprocess
import uuid

misp_url = "http://192.168.0.172/"
#misp_key = subprocess.getoutput("/var/www/MISP/app/Console/cake user change_authkey 1 | cut -d ':' -f 2 | cut -d ' ' -f 2")
misp_key = "ERavM63SGBycNtx9VVwvfptcE6VdEwzisEXomOJk"
misp_verifycert = False

default_nickname = "investigator"
default_pw = "compass"
labs_count = 10

misp = PyMISP(misp_url, misp_key, misp_verifycert)


# Server settings
def setPasswordPolicyLength():
    misp.set_server_setting("Security.password_policy_length", 7, True)

def setPasswordPolicyComplexity():
    misp.set_server_setting("Security.password_policy_complexity", "/(a-z)*/", True)

def setMainLogo():
    misp.set_server_setting("MISP.main_logo", "logo.png", True)

def setWelcomeText():
    misp.set_server_setting("MISP.welcome_text_top","Welcome to Malware Information Sharing Platform " ,True)


# Create organizations
def setupOrg():
    for i in range(labs_count):
        org = MISPOrganisation()
        org.name = 'Lab_' + str(i+1)
        org.nationality = "Switzerland"
        org.local = True
        misp.add_organisation(org, pythonify=True)


# Create users
def setupUsers():
    for i in range(labs_count):
        user = MISPUser()
        user.email = default_nickname + '@misp-lab' + str(i+1) + '.com'
        #user.org_id = i+2 #offset -> org 1 = admin org
        user.org_id = 2
        user.role_id = 3
        user.password ="compass"
        user.change_pw = 0
        misp.add_user(user, pythonify=True)
    
# --------------------------------------------------------------------------------

# Import events
def importEvent():
    with open('./misp.json', 'r') as f:
            for e in f:
                event = json.loads(e)
                print(event)
                #misp.add_event(event)
    # print(event)

def jsonEvent():
    event = MISPEvent()
    event.info = 'This is my new MISP event'  # Required
    event.distribution = 0  # Optional, defaults to MISP.default_event_distribution in MISP config
    event.threat_level_id = 2  # Optional, defaults to MISP.default_event_threat_level in MISP config
    event.analysis = 1  # Optional, defaults to 0 (initial analysis)
    print(event.to_json())


def exitstingEvent():
    existing_event = MISPEvent()
    existing_event.load_file('./misp.json')

    # print(existing_event.attributes[0])
    # print(existing_event.attributes[0].tags)
    # print(existing_event.attributes[0].timestamp)
    # print(existing_event.attributes[0].to_json())
    print(existing_event)
    print(existing_event.attributes[0])
    misp.add_event(exitstingEvent)

def updateEvent():
    # event1 = misp.get_event(1231)

    # json_object = json.dumps(event1)
    # with open('./misp3.json', 'w') as f:
    #     f.write(json_object)

    with open('./misp4.json', 'r') as f:
            for e in f:
                event2 = json.loads(e)

    
    for i in range(len(event2['response'])):
        print(event2['response'][i])
        print("------------")

    
    # event2['Event']['id'] = 1233
    # event2['Event']['uuid'] = "2f451e80-03be-43bc-9f22-457e316004f3"
    
    #misp.add_event(event2)

    #print(misp.add_event(event))

    ## Push the updated event to MISP
    # event_dict = misp.update_event(event)
    # print(event_dict)


def importEvent():
    with open('./misp4.json', 'r') as f:
        for e in f:
            event = json.loads(e)
    
    for i in range(len(event['response'])):
        print(misp.add_event(event['response'][i]))

        


# userList()
# getServerSetting()
# setupOrg()
# setupUsers()

# importEvent()
# jsonEvent()
# exitstingEvent()
# updateEvent()
importEvent()



def userList():
    users_list = misp.users(pythonify=True)
    print(users_list)

def getServerSetting():
    print(misp.get_server_setting("Security.password_policy_length"))
    
def setServerSetting():
    server = misp.set_server_setting("Security.password_policy_length", 7, True)
    print(server)
    return

#  def set_server_setting(self, setting: str, value: Union[str, int, bool], force: bool = False) -> Dict:
#         """Set a setting on the MISP instance

#         :param setting: server setting name
#         :param value: value to set
#         :param force: override value test
#         """
#         data = {'value': value, 'force': force}
#         response = self._prepare_request('POST', f'servers/serverSettingsEdit/{setting}', data=data)
#         return self._check_json_response(response)




# user = MISPUser()
# user.email = "user2@user2.com"
# user.org_id = 1
# user.role_id = 1

# print(misp.add_user(user, pythonify=True))
