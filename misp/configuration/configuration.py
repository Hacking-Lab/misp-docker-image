import requests
from pymisp import PyMISP
import time
import subprocess
import os
from lab import Lab
from role import Role
from instance import Instance

misp_url = "http://localhost/"
misp_verifycert = False


def get_vital_signs():
    r = requests.get('http://localhost/users/login')


def get_api_key(email):
    subprocess.getoutput("/var/www/MISP/app/Console/cake Admin change_authkey " + email + " | sed '1d'")
    misp_key = subprocess.getoutput(
        "/var/www/MISP/app/Console/cake user change_authkey " + email + " | cut -d ':' -f 2 | cut -d ' ' -f 2")
    return misp_key


def new_admin_api(misp_key):
    global misp
    misp = PyMISP(misp_url, misp_key, misp_verifycert)


# Setup server
def update_instance():
    misp.update_object_templates()
    misp.update_galaxies()
    misp.update_taxonomies()
    # misp.enable_taxonomy('tlp')
    misp.update_warninglists()


def set_server_settings():
    misp.set_server_setting("Security.password_policy_length", 7, True)
    misp.set_server_setting("Security.password_policy_complexity", "/(a-z)*/", True)
    misp.set_server_setting("MISP.main_logo", "logo.png", True)
    misp.set_server_setting("MISP.welcome_text_top", "Welcome to Malware Information Sharing Platform ", True)


x = True
while x:
    try:
        time.sleep(10)
        get_vital_signs()
        misp_key = get_api_key('admin@admin.test')
        new_admin_api(misp_key)
        x = False
    except:
        x = True

update_instance()
set_server_settings()

# --------------------  LAB CONFIGURATION  -------------------- #

# Lab 0: Instance Admin Configuration
lab0 = Lab(0, misp, Instance.all)
lab0.add_org()
lab0.add_user(Role.admin)

# Lab 1: Introduction
lab1 = Lab(1, misp, Instance.default)
lab1.add_org()
lab1.add_user(Role.investigator)

# Lab 2: Phishing E-Mail
lab2 = Lab(2, misp, Instance.default)
lab2.add_org()
lab2.add_user(Role.investigator)

# Lab 3: Malware
lab3 = Lab(3, misp, Instance.default)
lab3.add_org()
lab3.add_user(Role.investigator)

# Lab 4: API
lab4 = Lab(4, misp, Instance.default)
lab4.add_org()
lab4.add_user(Role.investigator)

# Lab 5: MISP Visualisation
lab5 = Lab(5, misp, Instance.A)
lab5.add_org()
lab5.add_user(Role.org_admin)
lab5.add_user(Role.investigator)
lab5.import_events(lab5.get_admin())

# Lab 6: Synchronisation
lab6_a = Lab(6, misp, Instance.A)
lab6_a.add_org('lab6-org-A')
lab6_a.add_user(Role.org_admin, 'lab6-org-A')
lab6_a.add_user(Role.publisher, 'lab6-org-A')
lab6_a.add_user(Role.investigator, 'lab6-org-A')
lab6_a.import_events(lab6_a.get_admin())

lab6_b = Lab(6, misp, Instance.B)
lab6_b.add_org('lab6-org-B')
lab6_b.add_user(Role.org_admin, 'lab6-org-B')
lab6_b.add_user(Role.publisher, 'lab6-org-B')
lab6_b.add_user(Role.investigator, 'lab6-org-B')
lab6_b.add_org('lab6-org-F')
lab6_b.add_user(Role.org_admin, 'lab6-org-F')
lab6_b.add_user(Role.publisher, 'lab6-org-F')
lab6_b.add_user(Role.investigator, 'lab6-org-F')
lab6_b.add_user(Role.sync_user, 'lab6-org-F')

lab6_e = Lab(6, misp, Instance.E)
lab6_e.add_org('lab6-org-E')
lab6_e.add_user(Role.org_admin, 'lab6-org-E')
lab6_e.add_user(Role.investigator, 'lab6-org-E')
# TODO: Refactor this part
lab6_e.add_org('PLEASE-REPLACE-ME', False)
lab6_e.add_sync_server('Instance-B', 'http://misp-instance-B', 3)

# Lab 7: MISP Modules
lab7 = Lab(7, misp, Instance.A)
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
lab8 = Lab(8, misp, Instance.default)
lab8.add_org()
lab8.add_user(Role.org_admin)
lab8.add_user(Role.investigator)  # TODO @JW: Are higher privileges needed?

# --------------------  LAB CONFIGURATION  -------------------- #

os.system("cp /data/logo.png /var/www/MISP/app/webroot/img/custom/logo.png")
print(" -------------------- Configuration complete -------------------- ")
