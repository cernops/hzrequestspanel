from django.views import generic

import hzrequestspanel.api.projects.project_creator
import hzrequestspanel.api.projects.project_killer
import hzrequestspanel.api.projects.quota_changer
from openstack_dashboard.api.rest import utils as rest_utils
from openstack_dashboard.api.rest import urls


@urls.register
class HZRequest(generic.View):
    """API for requests.
    """
    url_regex = r'hzrequests/requests/$'

    @rest_utils.ajax(data_required=True)
    def post(self, request):
        if request.DATA['ticket_type'] == 'new_project':
            ticket = hzrequestspanel.api.projects.project_creator.NewProjectCreator(request.DATA)
        elif request.DATA['ticket_type'] == 'quota_change':
            ticket = hzrequestspanel.api.projects.quota_changer.QuotaChanger(request.DATA)
        elif request.DATA['ticket_type'] == 'delete_project':
            ticket = hzrequestspanel.api.projects.project_killer.ProjectKiller(request.DATA)

        return {"ticket_number": ticket.create_ticket()}
