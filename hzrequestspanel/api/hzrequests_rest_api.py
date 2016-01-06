from django.views import generic

from hzrequestspanel.api import hzrequests_service
from openstack_dashboard.api.rest import utils as rest_utils

from openstack_dashboard.api.rest import urls

@urls.register
class Request(generic.View):
    """API for requests.
    """
    url_regex = r'hzrequests/requests/$'

    @rest_utils.ajax(data_required=True)
    def post(self, request):
        request = {}
        return hzrequests_service.create(request)
