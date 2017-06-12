from abc import abstractmethod
import logging
import prettytable

from ConfigParser import ConfigParser
from ccitools.cloud import CloudClient
from ccitools.servicenow import ServiceNowClient
from ccitools.xldap import XldapClient

from keystoneauth1.identity import v3
from keystoneauth1 import session

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
    def __init__(self, dict_data):
        self.dict_data = dict_data
        self.config = None
        self.sn_user = None
        self.sn_pass = None
        self.sn_instance = None
        self.functional_element = None
        self.group = None
        self.functional_element_escalate = None
        self.group_escalate = None
        self.watchlist_departments = None
        self.watchlist_egroup_template = None
        self.svc_user = None
        self.svc_pass = None
        self.keystone_endpoint = None
        self._parse_config_file()
        self.snowclient = self._create_snowclient_instance()
        self.cloudclient = self._create_cloudclient_instance()
        self.ticket_number = None
        self.user_message = None
        self.supporter_message = None
        self.username = dict_data['username']

    def _parse_config_file(self):
        try:
            self.config = ConfigParser()
            self.config.readfp(open(
                # TODO make this value customizable or use fixed /etc/...
                '/Users/makowals/CERNBox/git/hzrequestspanel/hzrequestspanel.conf'))
            self.sn_user = self.config.get("servicenow", "sn_user")
            self.sn_pass = self.config.get("servicenow", "sn_pass")
            self.sn_instance = self.config.get("servicenow", "sn_instance")
            self.functional_element = self.config.get("servicenow",
                                                     "sn_functional_element")
            self.group = self.config.get("servicenow", "sn_group")
            self.functional_element_escalate = self.config.get("servicenow",
                                                               "sn_functional_element_escalate")
            self.group_escalate = self.config.get("servicenow",
                                                  "sn_group_escalate")
            self.watchlist_departments = [dep.lower() for dep in
                                          self.config.get("servicenow",
                                                          "watchlist_departments").split()]
            self.watchlist_egroup_template = self.config.get("servicenow",
                                                             "watchlist_egroup_template")
            self.svc_user = self.config.get("cloud", "svc_user")
            self.svc_pass = self.config.get("cloud", "svc_pass")
            self.keystone_endpoint = self.config.get("cloud", "keystone_endpoint")
        except Exception as e:
            LOG.error("Error parsing configuration:" + e.message)
            raise SnowException

    def _create_snowclient_instance(self):
        try:
            return ServiceNowClient(self.sn_user, self.sn_pass,
                                    instance=self.sn_instance)
        except Exception as e:
            LOG.error("Error instanciating SNOW client:" + e.message)
            raise SnowException

    def _create_cloudclient_instance(self):
        try:
            auth = v3.Password(
                username=self.svc_user,
                password=self.svc_pass,
                auth_url=self.keystone_endpoint,
                user_domain_name='default',
                project_name='admin',
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
                                                                self.functional_element,
                                                                assignment_group=self.group).number
        except Exception as e:
            LOG.error("Error creating empty SNOW ticket:" + e.message)
            raise SnowException

    def _escalate_ticket(self, functional_element_escalate, group_escalate):
        try:
            username = self.snowclient.users.getRecords(
                sys_id=self.snowclient.get_ticket(
                    self.ticket_number).u_caller_id)[
                0].first_name
            self.snowclient.add_comment(self.ticket_number,
                                        self.user_message % username)

            worknote_msg = self._generate_supporter_message()

            self.snowclient.add_work_note(self.ticket_number, worknote_msg)

            self.snowclient.change_functional_element(self.ticket_number,
                                                      functional_element_escalate,
                                                      group_escalate)
        except Exception as e:
            LOG.error("Error escalating SNOW ticket {0}".format(self.ticket_number))
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
            LOG.error("Error creating SNOW ticket. E-group not found:" + e.message)
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


class NewProjectCreator(AbstractRequestCreator):
    def __init__(self, dict_data):
        super(NewProjectCreator, self).__init__(dict_data)
        self.title = "Request for shared Cloud Service Project - name: {0}".format(
            self.dict_data['projectname'])
        self.user_message = """Dear %s,

Your project creation request has been received and sent to
HW Resources management in order to be evaluated.

Your request will be applied after approval.

Thank you,
        Cloud Infrastructure Team"""
        self.supporter_message = """Dear HW Resources manager,

Could you please review the following project creation request?

%s

If there are any special requests regarding non-standard flavours, please
reassign the ticket back to Cloud Team.

If not, in order to accept the request, please execute [code]<a href="https://cirundeck.cern.ch/project/HW-Resources/job/show/14d9ba7f-5dbf-47b7-9142-5d9873fef80d?opt.snow_ticket=%s&opt.enable_project=yes
" target="_blank">the following Rundeck job</a>[/code].

Best regards,
        Cloud Infrastructure Team"""

    def _generate_supporter_message(self):
        t = prettytable.PrettyTable(["Quota", "Requested"])
        t.add_row(["Cores", self.dict_data["cores"]])
        t.add_row(["Instances", self.dict_data["instances"]])
        t.add_row(["RAM (GB)", self.dict_data["ram"]])
        t.add_row(["Volumes (standard)", self.dict_data["volumes"]])
        t.add_row(["Diskspace (standard)", self.dict_data["gigabytes"]])
        t.border = True
        t.header = True
        t.align["Quota"] = 'c'
        t.align["Requested"] = 'c'

        worknote_msg = self.supporter_message % (
            self._convert_to_monospace(t), self.ticket_number)

        return worknote_msg

    def _verify_prerequisites(self):
        self.dict_data['owner'] = self._get_primary_account_from_ldap(
            self.dict_data['owner'])

        self._verify_egroup(self.dict_data['egroup'])

    def _fill_ticket_with_proper_data(self):
        try:
            self.snowclient.create_project_creation(self.ticket_number,
                                                    self.dict_data)
        except Exception as e:
            LOG.error("Error updating snow ticket:" + e.message)
            raise SnowException

        self._escalate_ticket(self.functional_element_escalate,
                              self.group_escalate)


class QuotaChanger(AbstractRequestCreator):
    def __init__(self, dict_data):
        super(QuotaChanger, self).__init__(dict_data)
        self.title = "Request change of resource quota for the Cloud Project {0}".format(
            self.dict_data['projectname'])
        self.user_message = """Dear %s,

Your quota update request has been received and sent to
HW Resources management in order to be evaluated.

Your request will be applied after approval.

Thank you,
        Cloud Infrastructure Team"""
        self.supporter_message = """Dear HW Resources manager,

Could you please review the following quota update request?

%s

In order to apply these values, please execute [code]<a href="https://cirundeck.cern.ch/project/HW-Resources/job/show/ad45c0a5-5a81-4861-a7ee-fbb7d54f122a?opt.snow_ticket=%s&opt.behaviour=perform
" target="_blank">the following Rundeck job</a>[/code].

Best regards,
        Cloud Infrastructure Team"""

    def _generate_supporter_message(self):
        rp = self.snowclient.get_quota_update_request_rp(self.ticket_number)

        rp_dict = self._quota_update_rp_to_dict(rp,
                                                self.dict_data['current_quota'][
                                                    'nova_quota'],
                                                self.dict_data['current_quota'][
                                                    'cinder_quota'])

        req_summary = self._quota_change_request_summary(rp_dict,
                                                         self.dict_data[
                                                             'current_quota'][
                                                             'nova_quota'],
                                                         self.dict_data[
                                                             'current_quota'][
                                                             'cinder_quota'])

        worknote_msg = self.supporter_message % (
            self._convert_to_monospace(req_summary), self.ticket_number)

        return worknote_msg

    def _verify_prerequisites(self):
        pass

    def _fill_ticket_with_proper_data(self):
        self.dict_data['username'] = self._get_primary_account_from_ldap(
            self.dict_data['username'])

        try:
            self.snowclient.create_quota_update(self.ticket_number,
                                                self.dict_data[
                                                    'volume_type_name_list'],
                                                self.dict_data)
        except Exception as e:
            LOG.error("Error updating snow ticket:" + e.message)
            raise SnowException

        self._add_coordinators_to_watchlist()

        self._escalate_ticket(self.functional_element_escalate,
                              self.group_escalate)

    def _add_coordinators_to_watchlist(self):
        try:
            rp = self.snowclient.get_quota_update_request_rp(self.ticket_number)
            project_name = rp.project_name.lower()

            # This has strict dependency of having experiment in the project name
            department = [dep for dep in self.watchlist_departments if
                          project_name.startswith(dep)]
            if len(department) != 0:
                self.snowclient.add_email_watch_list(self.ticket_number,
                                                     self.watchlist_egroup_template %
                                                     department[0])
        except Exception as e:
            LOG.error("Error adding coordinators to watchlist:" + e.message)

    @staticmethod
    def __calculate_variation(current, requested):
        current = int(current)
        requested = int(requested)
        if current:
            return requested - current, (
                float(requested - current) / current) * 100
        else:
            if requested:
                return requested, 100
        return 0, 0

    @staticmethod
    def _quota_change_request_summary(rp, nova_quota, cinder_quota):
        diff_cores, percent_cores = QuotaChanger.__calculate_variation(
            nova_quota['cores'],
            rp['cores'])
        variation_cores = "%+d (%+d%%)" % (diff_cores, percent_cores)

        diff_instances, percent_intances = QuotaChanger.__calculate_variation(
            nova_quota['instances'], rp['instances'])
        variation_instances = "%+d (%+d%%)" % (diff_instances, percent_intances)

        diff_ram, percent_ram = QuotaChanger.__calculate_variation(
            int(nova_quota['ram']),
            rp['ram'])
        variation_ram = "%+d (%+d%%)" % (diff_ram, percent_ram)

        t = prettytable.PrettyTable(
            ["Quota", "Current", "Requested", "Variation"])
        t.add_row(["Cores", nova_quota['cores'], rp['cores'], variation_cores])
        t.add_row(["Instances", nova_quota['instances'], rp['instances'],
                   variation_instances])
        t.add_row(
            ["RAM (GB)", int(nova_quota['ram']), rp['ram'], variation_ram])

        if 'volume_quota' in rp.keys():
            for volume_quota in rp['volume_quota']:
                t.add_row(["", "", "", ""])
                current_volumes = cinder_quota[
                    'volumes_%s' % volume_quota['type']]
                requested_volumes = volume_quota['volumes']

                diff_volumes, percent_volumes = QuotaChanger.__calculate_variation(
                    current_volumes, requested_volumes)
                variation_volumes = "%+d (%+d%%)" % (
                    diff_volumes, percent_volumes)

                current_gigabytes = cinder_quota[
                    'gigabytes_%s' % volume_quota['type']]
                requested_gigabytes = volume_quota['gigabytes']

                diff_disk, percent_disk = QuotaChanger.__calculate_variation(
                    current_gigabytes, requested_gigabytes)
                variation_disk = "%+d (%+d%%)" % (diff_disk, percent_disk)

                t.add_row(
                    ["Volumes (%s)" % volume_quota['type'], current_volumes,
                     requested_volumes, variation_volumes])
                t.add_row(
                    ["Diskspace (%s)" % volume_quota['type'], current_gigabytes,
                     requested_gigabytes, variation_disk])

        t.border = True
        t.header = True
        t.align["Quota"] = 'c'
        t.align["Current"] = 'c'
        t.align["Requested"] = 'c'
        t.align["Variation"] = 'c'
        return t

    @staticmethod
    def _quota_update_rp_to_dict(rp, nova_quota, cinder_quota):
        """
        Creates a python dictionary with the fields and values from the RP.

        :param rp: Quota Update record Producer
        :param nova_quota: Nova quota object
        :param cinder_quota: Cinder quota object
        """
        rp_dict = {}
        for field in rp.fields:
            if field == "volume_quota":
                for volume_quota in rp.volume_quota:
                    if field not in rp_dict:
                        rp_dict[field] = []
                    for key in volume_quota:
                        try:
                            if volume_quota[key]:
                                volume_quota[key] = int(volume_quota[key])
                            else:
                                volume_quota[key] = int(cinder_quota["%s_%s" % (
                                    key, volume_quota['type'])])
                        except ValueError:
                            logging.debug("'%s' can't be converted to Integer" %
                                          volume_quota[key])

                    rp_dict[field].append(volume_quota)
            else:
                if rp.__getattr__(field):
                    try:
                        rp_dict[field] = int(rp.__getattr__(field))
                    except ValueError:
                        logging.debug(
                            "'%s' cant be converted to int" % rp.__getattr__(
                                field))
                        rp_dict[field] = rp.__getattr__(field)

                else:  # if requested empty, then load current value
                    if field in nova_quota.keys():
                        rp_dict[field] = int(nova_quota[field])
                    elif field in cinder_quota.keys():
                        rp_dict[field] = int(cinder_quota[field])

        return rp_dict


class ProjectKiller(AbstractRequestCreator):
    def __init__(self, dict_data):
        super(ProjectKiller, self).__init__(dict_data)
        self.title = "Request removal of Cloud Project {0}".format(
            self.dict_data['project_name'])

        self.user_message = """Dear %s,

Your project deletion request has been received and sent to
Cloud Infrastructure management in order to be confirmed.

Thank you,
        Cloud Infrastructure Team"""
        self.supporter_message = """Hi, it's me, Rundeck,

In order to delete this project, please execute [code]<a href="https://cirundeck.cern.ch/project/Cloud-Operations/job/show/207957c5-f0ff-486d-95bc-24ce4f40f807?opt.snow_ticket=%s
" target="_blank">the following Rundeck job</a>[/code]."""

    def _generate_supporter_message(self):
        return self.supporter_message % self.ticket_number

    def _fill_ticket_with_proper_data(self):
        try:
            self.snowclient.create_project_deletion(self.ticket_number,
                                                    self.dict_data)
        except Exception as e:
            LOG.error("Error updating snow ticket:" + e.message)
            raise SnowException

        self._add_project_members_to_watchlist(self.dict_data['project_name'])

        self._escalate_ticket(self.functional_element, self.group)

    def _verify_prerequisites(self):
        self.dict_data['username'] = self._get_primary_account_from_ldap(
            self.dict_data['username'])

        self._verify_project_owner(self.dict_data['project_name'],
                                   self.dict_data['username'])

    def _add_project_members_to_watchlist(self, project_name):
        try:
            for member in self.cloudclient.get_project_members(project_name):
                self.snowclient.add_email_watch_list(self.ticket_number,
                                                     member + "@cern.ch")
        except Exception as e:
            LOG.error("Error adding members to watchlist:" + e.message)

    def _verify_project_owner(self, project_name, username):
        try:
            owner = self.cloudclient.get_project_owner(project_name)
        except Exception as e:
            LOG.error("Error checking project owner:" + e.message)
            raise SnowException

        if owner != username:
            raise SnowException("Unable to create the ticket. You are not the owner of this project.")

        return
