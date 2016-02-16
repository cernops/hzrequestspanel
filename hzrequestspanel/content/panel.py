from django.utils.translation import ugettext_lazy as _

import horizon

class Hzrequestspanel(horizon.Panel):
    name = _("Overview")
    slug = "hzrequestspanel"
