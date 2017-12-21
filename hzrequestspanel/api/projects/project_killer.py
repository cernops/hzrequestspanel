import hzrequestspanel.api.projects
from hzrequestspanel.api.projects import LOG
from hzrequestspanel.api.projects import SnowException


class ProjectKiller(hzrequestspanel.api.projects.AbstractRequestCreator):
    def __init__(self, dict_data, **kwargs):
        super(ProjectKiller, self).__init__(dict_data, **kwargs)

        self.target_functional_element = self.config['cloud_functional_element']
        self.target_group = self.config['cloud_group']

        self.title = "Request removal of Cloud Project {0}".format(
            self.dict_data['project_name'])

        self.user_message = """Dear %s,

Your project deletion request has been received
and sent to Cloud Infrastructure management in order to be confirmed.

Thank you,
        Cloud Infrastructure Team"""
        self.supporter_message = """Hi, it's me, Rundeck,

In order to delete this project, please execute the following Rundeck job - [code]<a href="https://cirundeck.cern.ch/project/Cloud-Operations/job/show/207957c5-f0ff-486d-95bc-24ce4f40f807?opt.snow_ticket=%s" target="_blank">https://cirundeck.cern.ch/project/Cloud-Operations/job/...</a>[/code]"""

    def _generate_supporter_message(self):
        return self.supporter_message % self.ticket.info.number

    def _fill_ticket_with_proper_data(self):
        try:
            self.snowclient.record_producer.convert_RQF_to_project_deletion(
                self.ticket, self.dict_data)
        except Exception as e:
            LOG.error("Error updating snow ticket:" + e.message)
            raise SnowException(e)

        self._add_project_members_to_watchlist(self.dict_data['project_name'])

    def _verify_prerequisites(self):
        self._verify_project_owner(self.dict_data['project_name'],
                                   self.dict_data['username'])

    def _add_project_members_to_watchlist(self, project_name):
        try:
            for member in self.cloudclient.get_project_members(project_name):
                self.ticket.add_email_to_watch_list(member + "@cern.ch")
        except Exception as e:
            LOG.error("Error adding members to watchlist:" + e.message)

    def _verify_project_owner(self, project_name, username):
        try:
            owner = self.cloudclient.get_project_owner(project_name)
        except Exception as e:
            LOG.error("Error checking project owner:" + e.message)
            raise SnowException(e)

        if owner != username:
            raise SnowException("Unable to create the ticket. You are not the owner of this project.")

        return
