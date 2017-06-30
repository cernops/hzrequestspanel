import logging
from abc import abstractmethod

from ConfigParser import ConfigParser
from ccitools.cloud import CloudClient
from ccitools.servicenow import ServiceNowClient
from ccitools.xldap import XldapClient
from keystoneauth1 import session
from keystoneauth1.identity import v3

LOG = logging.getLogger('horizon.hzrequests')
LOG.setLevel(logging.INFO)


class SnowException(Exception):
    def __init__(self):
        msg = "Unable to create the ticket. Please retry. " \
              "If the problem persists, contact " \
              "the Cloud Team"
        super(SnowException, self).__init__(msg)

    def __init__(self, msg):
        super(SnowException, self).__init__(msg)


class AbstractRequestCreator(object):
    def __init__(self, dict_data,
                 config_file='/etc/openstack-dashboard/hzrequestspanel.conf'):
        self.dict_data = dict_data
        self.config = None
        self._parse_config_file(config_file)
        self.snowclient = self._create_snowclient_instance()
        self.cloudclient = self._create_cloudclient_instance()
        self.ticket_number = None
        self.user_message = None
        self.supporter_message = None
        self.username = dict_data['username']
        self.target_functional_element = None
        self.target_group = None

    def _parse_config_file(self, config_file):
        try:
            self.config = ConfigParser()
            self.config.readfp(open(config_file))

            config = {'user': self.config.get("servicenow", "user"),
                      'pass': self.config.get("servicenow", "pass"),
                      'instance': self.config.get("servicenow", "instance"),
                      'cloud_functional_element': self.config.get("servicenow", "cloud_functional_element"),
                      'cloud_group': self.config.get("servicenow", "cloud_group"),
                      'resources_functional_element': self.config.get("servicenow", "resources_functional_element"),
                      'resources_group': self.config.get("servicenow", "resources_group"),
                      'watchlist_departments': [dep.lower() for dep in self.config.get("servicenow", "watchlist_departments").split()],
                      'watchlist_egroup_template': self.config.get("servicenow", "watchlist_egroup_template"),
                      'svc_user': self.config.get("cloud", "user"),
                      'svc_pass': self.config.get("cloud", "pass"),
                      'keystone_endpoint': self.config.get("cloud", "keystone_endpoint")
                      }

            self.config = config
        except Exception as e:
            LOG.error("Error parsing configuration:" + e.message)
            raise SnowException

    def _create_snowclient_instance(self):
        try:
            return ServiceNowClient(self.config['user'], self.config['pass'],
                                    instance=self.config['instance'])
        except Exception as e:
            LOG.error("Error instanciating SNOW client:" + e.message)
            raise SnowException

    def _create_cloudclient_instance(self):
        try:
            auth = v3.Password(
                username=self.config['svc_user'],
                password=self.config['svc_pass'],
                auth_url=self.config['keystone_endpoint'],
                user_domain_name='default',
                project_name='services',
                project_domain_name='default'
            )
            sess = session.Session(auth=auth)
            return CloudClient(session=sess)

        except Exception as e:
            LOG.error("Error instanciating cloud client:" + e.message)
            raise SnowException

    def _create_empty_snow_ticket(self, title):
        try:
            self.ticket_number = self.snowclient.create_request(title,
                                                                self.target_functional_element,
                                                                assignment_group=self.target_group).number
        except Exception as e:
            LOG.error("Error creating empty SNOW ticket:" + e.message)
            raise SnowException

    def _create_notes_and_comments(self):
        try:
            self.snowclient.add_comment(self.ticket_number,
                                        self.user_message % self.dict_data['username'])

            worknote_msg = self._generate_supporter_message()

            self.snowclient.add_work_note(self.ticket_number, worknote_msg)

        except Exception as e:
            LOG.error("Error creating notes for SNOW ticket {0}".format(self.ticket_number))
            raise Exception("Your ticket {0} has been successfully created, " \
                            "however we have identified some issues during the " \
                            "process. Please go to Service-Now and verify your " \
                            "request. If you find any problems, please contact " \
                            "the Cloud Team.".format(self.ticket_number))

    def create_ticket(self):
        LOG.info("Creating SNOW ticket with: {0}".format(self.dict_data))
        self._verify_prerequisites()
        self._create_empty_snow_ticket(self.title)
        self._fill_ticket_with_proper_data()
        self._create_notes_and_comments()
        LOG.info("SNOW ticket '{0}' created successfully".format(self.ticket_number))

        return self.ticket_number

    @staticmethod
    def _convert_to_monospace(text):
        text = "<br/>".join(text.get_string().split("\n"))
        text = "%s%s%s" % ("[code]<pre>", text, "</pre>[/code]")
        return text

    @staticmethod
    def _get_primary_account_from_ldap(username):
        try:
            xldap = XldapClient('ldap://xldap.cern.ch')
            return xldap.get_primary_account(username)
        except Exception as e:
            LOG.error("Error creating SNOW ticket. '{0}' is not a valid username".format(username))
            raise SnowException("Unable to create the ticket. Username you have provided is not correct.")

    @staticmethod
    def _verify_egroup(name):
        try:
            xldap = XldapClient('ldap://xldap.cern.ch')
            if not xldap.is_existing_egroup(name):
                raise Exception
            return True
        except Exception as e:
            LOG.error("Error creating SNOW ticket. E-group not found: '{0}'".format(name))
            raise SnowException("Unable to create the ticket. E-group you have provided is not correct.")

    @abstractmethod
    def _verify_prerequisites(self):
        pass

    @abstractmethod
    def _fill_ticket_with_proper_data(self):
        pass

    @abstractmethod
    def _generate_supporter_message(self):
        pass
