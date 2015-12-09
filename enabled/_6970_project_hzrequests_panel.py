# The slug of the panel to be added to HORIZON_CONFIG. Required.
PANEL = 'ngrequests'
# The slug of the dashboard the PANEL associated with. Required.
PANEL_DASHBOARD = 'project'

PANEL_GROUP = 'compute'

# Python panel class of the PANEL to be added.
ADD_PANEL = ('openstack_dashboard.dashboards.project.'
             'hzrequestspanel.content.panel.Hzrequestspanel')

ADD_INSTALLED_APPS = ['hzrequestspanel']

AUTO_DISCOVER_STATIC_FILES = True
