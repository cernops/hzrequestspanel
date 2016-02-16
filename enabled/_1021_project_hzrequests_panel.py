# The slug of the panel to be added to HORIZON_CONFIG. Required.
PANEL = 'hzrequestspanel'
# The slug of the dashboard the PANEL associated with. Required.
PANEL_DASHBOARD = 'project'

PANEL_GROUP = 'compute'

# Python panel class of the PANEL to be added.
ADD_PANEL = ('hzrequestspanel.content.panel.Hzrequestspanel')

ADD_INSTALLED_APPS = ['hzrequestspanel']

ADD_ANGULAR_MODULES = ['horizon.dashboard.project.hzrequestspanel']

AUTO_DISCOVER_STATIC_FILES = True

DEFAULT_PANEL = 'hzrequestspanel'

ADD_SCSS_FILES = [
    'dashboard/project/hzrequestspanel/hzrequestspanel.scss',
]
