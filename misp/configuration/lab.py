import json
import subprocess
import uuid
from role import Role
from pymisp import MISPUser, MISPOrganisation, PyMISP


class Lab:
    default_password = 'compass'

    def __init__(self, lab_nr: int, api: PyMISP, instance: str = None):
        self.__lab_nr = lab_nr
        self.__api = api
        self.__instance = instance
        self.__users = []
        self.__admins = []
        self.__orgs = {}
        self.__server_settings = ()


    def add_user(self, role: Role, org_name: str = None):
        if org_name is None:
            org_name = "lab" + str(self.__lab_nr)

        if org_name in self.__orgs:
            user = MISPUser()
            user.email = self.__calc_email(role, org_name)
            user.org_id = self.__orgs[org_name]
            user.role_id = role.value
            user.password = self.default_password
            user.change_pw = False
            user.disabled = False

            result: MISPUser = self.__api.add_user(user, pythonify=True)
            if role.value > 2:
                self.__users.append(result)
            else:
                result.api_key = subprocess.getoutput("/var/www/MISP/app/Console/cake user change_authkey " + result.email + " | cut -d ':' -f 2 | cut -d ' ' -f 2")
                self.__admins.append(result)

    def __calc_email(self, role: Role, org_name: str) -> str:
        if role.value == 1:
            return role.name + "@misp-lab.com"
        elif len(self.__orgs) == 1:
            return role.name + "@misp-lab" + str(self.__lab_nr) + ".com"
        elif self.__instance is None:
            return role.name + "-org-" + org_name + "@misp-lab" + str(self.__lab_nr) + ".com"
        else:
            return role.name + "-org-" + org_name + "@instance-" + self.__instance + ".misp-lab" + str(self.__lab_nr) + ".com"

    def add_org(self, org_name: str = None, local: bool = True):
        if org_name is None:
            org_name = "lab" + str(self.__lab_nr)

        org = MISPOrganisation()
        org.name = org_name
        org.nationality = 'Switzerland'
        org.local = local
        self.__orgs[org_name] = int(self.__api.add_organisation(org, pythonify=True).id)

    def import_events(self, user: MISPUser):
        if not hasattr(user, 'api_key'):
            return
        api = PyMISP('http://localhost/', user.api_key, False)

        # open json file with events
        try:
            with open('./data/lab_' + str(self.__lab_nr) + '.json', 'r') as f:
                for e in f:
                    events = json.loads(e)
        except:
            return

        # edit file
        org = self.__api.get_organisation(user.org_id, pythonify=True)
        for event in range(len(events['response'])):
            events['response'][event]['Event']['uuid'] = uuid.uuid4()
            events['response'][event]['Event']['orgc_id'] = org.id
            events['response'][event]['Event']['org_id'] = org.id
            events['response'][event]['Event']['Org']['id'] = org.id
            events['response'][event]['Event']['Org']['name'] = org.name
            events['response'][event]['Event']['Org']['uuid'] = org.uuid
            events['response'][event]['Event']['Orgc']['id'] = org.id
            events['response'][event]['Event']['Orgc']['name'] = org.name
            events['response'][event]['Event']['Orgc']['uuid'] = org.uuid
            for attribute in range(len(events['response'][event]['Event']['Attribute'])):
                events['response'][event]['Event']['Attribute'][attribute]['uuid'] = uuid.uuid4()
            # upload file
            api.add_event(events['response'][event])

    def add_configuration(self):
        self.__api.set_server_setting("Plugin.Enrichment_services_enable", True, True)
        self.__api.set_server_setting("Plugin.Enrichment_hover_enable", True, True)
        self.__api.set_server_setting("Plugin.Enrichment_geoip_city_enabled", True, True)
        self.__api.set_server_setting("Plugin.Enrichment_geoip_city_restrict", 11, True)
        self.__api.set_server_setting("Plugin.Enrichment_geoip_city_local_geolite_db", "/data-shared/geolite/city.mmdb", True)
        self.__api.set_server_setting("Plugin.Enrichment_btc_scam_check_enabled", True, True)
        self.__api.set_server_setting("Plugin.Enrichment_btc_scam_check_restrict", 11, True)
        self.__api.set_server_setting("Plugin.Enrichment_macvendors_enabled", True, True)
        self.__api.set_server_setting("Plugin.Enrichment_macvendors_restrict", 11, True)
        self.__api.set_server_setting("Plugin.Enrichment_qrcode_enabled", True, True)
        self.__api.set_server_setting("Plugin.Enrichment_qrcode_restrict", 11, True)
        self.__api.set_server_setting("Plugin.Enrichment_services_enable", True, True)
        self.__api.set_server_setting("Plugin.Enrichment_services_restrict", 11, True)
        self.__api.set_server_setting("Plugin.Enrichment_urlhaus_enabled", True, True)
        self.__api.set_server_setting("Plugin.Enrichment_urlhaus_restrict", 11, True)

    def get_org(self, pos: int):
        return self.__orgs[pos]

    def get_admin(self, pos: int = 0) -> MISPUser:
        return self.__admins[pos]

    def add_sync_server(self, name, url, remote_org_id):
        server = {"Server": {'name': name, 'url': url, 'uuid': '0ac33559-ad37-4147-b61d-95df6ab76920', 'authkey': "aaaaaasaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", 'self_signed': 'True', 'pull': True, 'remote_org_id': remote_org_id}}
        self.__api.add_server(server)
