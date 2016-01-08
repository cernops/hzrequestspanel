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
        volume_type_list = cinder.volume_type_list(request)
        volume_type_name_list = []
        for vt in volume_type_list:
            volume_type_name_list.append(vt.name)
        return hzrequests_service.create(request.DATA, volume_type_name_list)
