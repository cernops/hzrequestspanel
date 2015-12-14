from horizon import views

from openstack_dashboard import usage

class IndexView(views.APIView):
    # A very simple class-based view...
    template_name = 'hzrequestspanel/index.html'

    def get_data(self, request, context, *args, **kwargs):
        # Add data to the context here...
        return context
