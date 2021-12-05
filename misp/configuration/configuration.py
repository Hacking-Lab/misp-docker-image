from pymisp import PyMISP
import time
import subprocess
import os
from lab import Lab
from role import Role

misp_url = "http://localhost/"
misp_verifycert = False


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


def setServerSettings():
    misp.set_server_setting("Security.password_policy_length", 7, True)
    misp.set_server_setting("Security.password_policy_complexity", "/(a-z)*/", True)
    misp.set_server_setting("MISP.main_logo", "logo.png", True)
    misp.set_server_setting("MISP.welcome_text_top", "Welcome to Malware Information Sharing Platform ", True)

if not os.path.isfile("/var/tmp/first-configuration"):
    raise Exception('The MISP Instance is already configured')

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
if os.environ['MISP_BASEURL'] == "http://instance-a.misp.localhost":
    lab6_a = Lab(6, misp, "A")
    lab6_a.add_org('lab6-org-A')
    lab6_a.add_user(Role.org_admin, 'lab6-org-A')
    lab6_a.add_user(Role.publisher, 'lab6-org-A')
    lab6_a.add_user(Role.investigator, 'lab6-org-A')
    lab6_a.import_events(lab6_a.get_admin())

if os.environ['MISP_BASEURL'] == "http://instance-b.misp.localhost":
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

if os.environ['MISP_BASEURL'] == "http://instance-e.misp.localhost":
    lab6_e = Lab(6, misp, "E")
    lab6_e.add_org('lab6-org-E')
    lab6_e.add_user(Role.admin, 'lab6-org-E')
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

os.system("cp /data/logo.png /var/www/MISP/app/webroot/img/custom/logo.png")
print(" -------------------- Configuration complete -------------------- ")
