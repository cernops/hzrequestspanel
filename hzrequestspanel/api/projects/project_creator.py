import prettytable
import hzrequestspanel.api.projects
from hzrequestspanel.api.projects import LOG
from hzrequestspanel.api.projects import SnowException


class NewProjectCreator(hzrequestspanel.api.projects.AbstractRequestCreator):
    def __init__(self, dict_data, **kwargs):
        super(NewProjectCreator, self).__init__(dict_data, **kwargs)

        self.target_functional_element = self.config['resources_functional_element']
        self.target_group = self.config['resources_group']

        self.title = "Request for shared Cloud Service Project - name: {0}".format(
            self.dict_data['project_name'])
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

If not, in order to accept the request, please execute the following Rundeck job - [code]<a href="https://cirundeck.cern.ch/project/HW-Resources/job/show/14d9ba7f-5dbf-47b7-9142-5d9873fef80d?opt.snow_ticket=%s" target="_blank">https://cirundeck.cern.ch/project/Cloud-Operations/job/...</a>[/code]

Best regards,
        Cloud Infrastructure Team"""

    def _generate_supporter_message(self):
        t = prettytable.PrettyTable(["Quota", "Requested"])
        t.add_row(["Cores", self.dict_data["cores"]])
        t.add_row(["Instances", self.dict_data["instances"]])
        t.add_row(["RAM (GB)", self.dict_data["ram"]])

        for volume_type in self.dict_data["volumes"].keys():
            t.add_row(["Volumes (%s)" % volume_type, self.dict_data["volumes"][volume_type]["volumes"]])
            t.add_row(["Diskspace (%s)" % volume_type, self.dict_data["volumes"][volume_type]["gigabytes"]])

        t.border = True
        t.header = True
        t.align["Quota"] = 'c'
        t.align["Requested"] = 'c'

        worknote_msg = self.supporter_message % (
            self._convert_to_monospace(t), self.ticket.info.number)

        return worknote_msg

    def _verify_prerequisites(self):
        self.dict_data['owner'] = self._get_primary_account_from_ldap(
            self.dict_data['owner'])

        for egroup in self.dict_data['egroup'].split(','):
            self._verify_egroup(egroup.strip())

    def _fill_ticket_with_proper_data(self):
        try:
            # self.dict_data['username'] = self.dict_data['owner']
            self.dict_data['username'] = self._get_primary_account_from_ldap(self.dict_data['username'])
            self._generate_volume_types_new_syntax(self.dict_data)
            self.snowclient.record_producer.convert_RQF_to_project_creation(self.ticket,
                                                                            self.dict_data)
        except Exception as e:
            LOG.error("Error updating snow ticket:" + e.message)
            raise SnowException

        self._add_coordinators_to_watchlist()

    def _add_coordinators_to_watchlist(self):
        try:
            acc_group = self.dict_data['accounting_group'].lower()

            if acc_group in self.config['watchlist_departments']:
                self.ticket.add_email_to_watch_list(self.config['watchlist_egroup_template'] % acc_group)
        except Exception as e:
            LOG.error("Error adding coordinators to watchlist:" + e.message)
