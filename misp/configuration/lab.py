import json
import os
import subprocess
import uuid
from role import Role
from instance import Instance
from mail_format import MailFormat
from pymisp import MISPUser, MISPOrganisation, PyMISP


class Lab:
    default_password = 'compass'

    def __init__(self, lab_nr: int, api: PyMISP, instance: Instance = Instance.all):
        self.__lab_nr = lab_nr
        self.__api = api
        self.__instance = instance
        self.__users = []
        self.__admins = []
        self.__orgs = {}
        self.__server_settings = ()
        self.__run_on_this_instance = self.check_instance()

    def check_instance(self):
        """
        Check if current instance correlate with set instance
        :return: If it is equal or not
        :rtype: bool
        """
        if self.__instance.name == str(os.environ['INSTANCE_TAG']):
            return True
        elif self.__instance == Instance.all:
            return True

    def add_user(self, role: Role, mail_format: MailFormat = MailFormat.default, org_name: str = None):
        """
        Adds a user to MISP
        :param Role role: Role of the new user
        :param org_name: Organisation of the new user
        :type org_name: str or None
        :param MailFormat mail_format: The format of the generated email address
        """
        if not self.__run_on_this_instance:
            return
        if org_name is None:
            org_name = "lab" + str(self.__lab_nr)

        if org_name in self.__orgs:
            user = MISPUser()
            user.email = self.__gen_email(role, org_name[-1], mail_format)
            user.org_id = self.__orgs[org_name]
            user.role_id = role.value
            user.password = self.default_password
            user.change_pw = False
            user.disabled = False

            result: MISPUser = self.__api.add_user(user, pythonify=True)
            if role.value > 2:
                self.__users.append(result)
            else:
                result.api_key = subprocess.getoutput(
                    "/var/www/MISP/app/Console/cake user change_authkey " + result.email + " | cut -d ':' -f 2 | cut -d ' ' -f 2")
                self.__admins.append(result)

    def __gen_email(self, role: Role, org: str, mail_format: MailFormat) -> str:
        """
        Generates the email address
        :param Role role: Role of the user
        :param str org: Org of the user
        :return: Valid email address
        :rtype: str
        """
        # <role>@misp-labX.com
        if mail_format == MailFormat.default:
            return role.name + "@misp-lab" + str(self.__lab_nr) + ".com"
        # <role>@misp-lab.com
        elif mail_format == MailFormat.none:
            return role.name + "@misp-lab.com"
        # <role>-org-X@misp-labX.com
        elif mail_format == MailFormat.org:
            return role.name + "-org-" + org.lower() + "@misp-lab" + str(self.__lab_nr) + ".com"
        # <role>@instance-X.misp-labX.com
        elif mail_format == MailFormat.instance:
            return role.name + "@instance-" + self.__instance.name.lower() + ".misp-lab" + str(self.__lab_nr) + ".com"
        # <role>-org-X@instance-X.misp-labX.com
        else:
            return role.name + "-org-" + org.lower() + "@instance-" + self.__instance.name + ".misp-lab" + str(self.__lab_nr) + ".com"

    def add_org(self, org_name: str = None, local: bool = True):
        """
        Add a new organisation to MISP
        :param org_name: The org name,
        :type org_name: str or None
        :param local: If org is a local
        :type local: bool or None
        """
        if not self.__run_on_this_instance:
            return
        if org_name is None:
            org_name = "lab" + str(self.__lab_nr)

        org = MISPOrganisation()
        org.name = org_name
        org.nationality = 'Switzerland'
        org.local = local
        self.__orgs[org_name] = int(self.__api.add_organisation(org, pythonify=True).id)

    def import_events(self, user: MISPUser):
        """
        Import new events from file system
        :param MISPUser user: The user that will create the event in MISP
        """
        if not self.__run_on_this_instance:
            return
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
        """
        Import new server configuration from file system
        """
        # TODO: Import events from fs
        if not self.__run_on_this_instance:
            return
        self.__api.set_server_setting("Plugin.Enrichment_services_enable", True, True)
        self.__api.set_server_setting("Plugin.Enrichment_hover_enable", True, True)
        self.__api.set_server_setting("Plugin.Enrichment_geoip_city_enabled", True, True)
        self.__api.set_server_setting("Plugin.Enrichment_geoip_city_restrict", 6, True)
        self.__api.set_server_setting("Plugin.Enrichment_geoip_city_local_geolite_db", "/data-shared/geolite/city.mmdb",
                                      True)
        self.__api.set_server_setting("Plugin.Enrichment_btc_scam_check_enabled", True, True)
        self.__api.set_server_setting("Plugin.Enrichment_btc_scam_check_restrict", 6, True)
        self.__api.set_server_setting("Plugin.Enrichment_macvendors_enabled", True, True)
        self.__api.set_server_setting("Plugin.Enrichment_macvendors_restrict", 6, True)
        self.__api.set_server_setting("Plugin.Enrichment_qrcode_enabled", True, True)
        self.__api.set_server_setting("Plugin.Enrichment_qrcode_restrict", 6, True)
        self.__api.set_server_setting("Plugin.Enrichment_urlhaus_enabled", True, True)
        self.__api.set_server_setting("Plugin.Enrichment_urlhaus_restrict", 6, True)

    def get_org(self, pos: int = 0):
        """
        Get default or specific org
        :param pos: Position in the org dict
        :return: Org name and id
        :rtype: dict
        """
        if not self.__run_on_this_instance:
            return
        return self.__orgs[pos]

    def get_admin(self, pos: int = 0):
        """
        Get the admin account for that lab
        :param pos: Position in the admin dict
        :return: Administrator
        :rtype: MISPUser
        """
        if not self.__run_on_this_instance:
            return
        return self.__admins[pos]

    def add_sync_server(self, name: str, url: str, remote_org_id: int):
        """
        Add a new sync server to MISP
        :param str name: Name of the server
        :param url: url to the remote server
        :param int remote_org_id: id of the remote org
        """
        if not self.__run_on_this_instance:
            return
        server = {"Server": {'name': name, 'url': url, 'uuid': '0ac33559-ad37-4147-b61d-95df6ab76920', 'authkey': "aaaaaasaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", 'self_signed': 'True', 'pull': True, 'remote_org_id': remote_org_id}}
        self.__api.add_server(server)