import prettytable
import hzrequestspanel.api.projects
from hzrequestspanel.api.projects import LOG
from hzrequestspanel.api.projects import SnowException


class NewProjectCreator(hzrequestspanel.api.projects.AbstractRequestCreator):
    def __init__(self, dict_data, config_file):
        super(NewProjectCreator, self).__init__(dict_data, config_file)
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