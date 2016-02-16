from django.template.defaultfilters import capfirst  # noqa
from django.template.defaultfilters import floatformat  # noqa
from django.utils.translation import ugettext_lazy as _

from horizon.utils import csvbase
from horizon import views

from openstack_dashboard import usage


class ProjectUsageCsvRenderer(csvbase.BaseCsvResponse):

    columns = [_("Instance Name"), _("VCPUs"), _("RAM (MB)"),
               _("Disk (GB)"), _("Usage (Hours)"),
               _("Time since created (Seconds)"), _("State")]

    def get_row_data(self):

        for inst in self.context['usage'].get_instances():
            yield (inst['name'],
                   inst['vcpus'],
                   inst['memory_mb'],
                   inst['local_gb'],
                   floatformat(inst['hours'], 2),
                   inst['uptime'],
                   capfirst(inst['state']))

class IndexView(usage.UsageView):
    table_class = usage.ProjectUsageTable
    usage_class = usage.ProjectUsage
    template_name = 'hzrequestspanel/index.html'
    csv_response_class = ProjectUsageCsvRenderer

    def get_data(self):
        super(IndexView, self).get_data()
        return self.usage.get_instances()
