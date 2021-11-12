
from pymisp import ExpandedPyMISP, MISPUser, MISPServer, PyMISP

import time
import subprocess

misp_url = "http://192.168.0.172/"
misp_key = subprocess.getoutput("/var/www/MISP/app/Console/cake user change_authkey 1 | cut -d ':' -f 2 | cut -d ' ' -f 2")
misp_verifycert = False

default_nickname = "investigator"
default_pw = "compass"

labs_count = 10

misp = PyMISP(misp_url, misp_key, misp_verifycert)


# Set password policy




# Setup organizations
def setupOrg():
    return True

# Create users
def setupUsers():
    for i in range(labs_count):
        user = MISPUser()
        user.email = default_nickname + '@misp-lab' + str(i+1) + '.com'
        user.org_id = 1
        user.role_id = 1
        user.password ="compass"
        user.change_pw = 0
        print(misp.add_user(user, pythonify=True))
    

# Import events


def userList():
    users_list = misp.users(pythonify=True)
    print(users_list)

def getServerSetting():
    print(misp.get_server_setting("Security.password_policy_length"))
    


def setServerSetting():
    server = misp.set_server_setting("Security.password_policy_length", 7, True)
    print(server)
    return

# userList()
getServerSetting()


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
