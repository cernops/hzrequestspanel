import hzrequestspanel.api.projects
from hzrequestspanel.api.projects import LOG
from hzrequestspanel.api.projects import SnowException


class ProjectKiller(hzrequestspanel.api.projects.AbstractRequestCreator):
    def __init__(self, dict_data, **kwargs):
        super(ProjectKiller, self).__init__(dict_data, **kwargs)
        self.title = "Request removal of Cloud Project {0}".format(
            self.dict_data['project_name'])

        self.user_message = """Dear %s,

Your project deletion request has been received 
and sent to
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
