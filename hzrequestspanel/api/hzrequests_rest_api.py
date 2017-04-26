from django.views import generic

from hzrequestspanel.api import hzrequests_service
from openstack_dashboard.api import cinder
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
            ticket = hzrequests_service.NewProjectCreator(request.DATA)
        elif request.DATA['ticket_type'] == 'quota_change':
            volume_type_list = cinder.volume_type_list(request)
            volume_type_name_list = []
            for vt in volume_type_list:
                volume_type_name_list.append(vt.name)
            request.DATA['volume_type_name_list'] = volume_type_name_list
            ticket = hzrequests_service.QuotaChanger(request.DATA)
        elif request.DATA['ticket_type'] == 'delete_project':
            ticket = hzrequests_service.ProjectKiller(request.DATA)

        return {"ticket_number": ticket.create_ticket()}
