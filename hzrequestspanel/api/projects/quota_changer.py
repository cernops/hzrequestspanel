import logging
import prettytable

import hzrequestspanel.api.projects
from hzrequestspanel.api.projects import LOG
from hzrequestspanel.api.projects import SnowException


class QuotaChanger(hzrequestspanel.api.projects.AbstractRequestCreator):
    def __init__(self, dict_data, **kwargs):
        super(QuotaChanger, self).__init__(dict_data, **kwargs)

        self.target_functional_element = self.config['resources_functional_element']
        self.target_group = self.config['resources_group']

        # self._generate_volume_type_list()
        self.title = "Request change of resource quota for the Cloud Project {0}".format(
            self.dict_data['projectname'])
        self.user_message = """Dear %s,

Your quota update request has been received and sent to
HW Resources management in order to be evaluated.

Your request will be applied after approval.

Thank you,
        Cloud Infrastructure Team"""
        self.supporter_message = """Dear HW Resources manager,

Could you please review the following quota update request?

%s

In order to apply these values, please execute the following Rundeck job - [code]<a href="https://cirundeck.cern.ch/project/HW-Resources/job/show/ad45c0a5-5a81-4861-a7ee-fbb7d54f122a?opt.snow_ticket=%s&opt.behaviour=perform" target="_blank">https://cirundeck.cern.ch/project/Cloud-Operations/job/...</a>[/code]

Best regards,
        Cloud Infrastructure Team"""

    def _generate_supporter_message(self):
        req_summary = self._quota_change_request_summary(self.dict_data,
                                                         self.dict_data[
                                                             'current_quota'][
                                                             'nova_quota'],
                                                         self.dict_data[
                                                             'current_quota'][
                                                             'cinder_quota'])

        worknote_msg = self.supporter_message % (
            self._convert_to_monospace(req_summary), self.ticket.info.number)

        return worknote_msg

    def _verify_prerequisites(self):
        pass

    def _fill_ticket_with_proper_data(self):
        self.dict_data['username'] = self._get_primary_account_from_ldap(
            self.dict_data['username'])

        try:
            self._generate_volume_types_new_syntax(self.dict_data)
            self.snowclient.record_producer.convert_RQF_to_quota_update(
                self.ticket, self.dict_data)
        except Exception as e:
            LOG.error("Error updating snow ticket:" + e.message)
            raise SnowException

        self._add_coordinators_to_watchlist()

    def _add_coordinators_to_watchlist(self):
        try:
            project_name = self.dict_data['projectname']

            # This has strict dependency of having experiment in the project name
            department = [dep for dep in self.config['watchlist_departments'] if
                          project_name.startswith(dep)]
            if len(department) != 0:
                self.snowclient.add_email_watch_list(self.ticket.info.number,
                                                     self.config['watchlist_egroup_template'] %
                                                     department[0])
        except Exception as e:
            LOG.error("Error adding coordinators to watchlist:" + e.message)

    def _generate_volume_types_new_syntax(self, dict_data):
        """Create new JSON schema for volume types in dict_data

        In old times dict_data contained "volumes" which structure was more or
        less like this

        dict_data["volumes"]["standard"] = {
            "gigabytes": 1,
            "volumes": 1
        }

        Currently we want to have a flat schema like

        dict_data["cp1_gigabytes"] = 1
        dict_data["cp1_volumes"] = 1

        This function will take dict_data and generate a new schema provided
        the old one exists. Because of historical reasons it's easier to have
        this converter instead of modifying user-facing JavaScript to generate
        a new structure at the first place.

        As python dictionaries are mutable, this function is changing `dict`
        passed as an argument

        :param dict_data: `dict` with values to create the record producer
        """

        volume_type_list = self.cloudclient.cinder.volume_types.list()
        for vt in volume_type_list:
            dict_data[vt.name + "_gigabytes"] = dict_data["volumes"][vt.name]["gigabytes"]
            dict_data[vt.name + "_volumes"] = dict_data["volumes"][vt.name]["volumes"]

    @staticmethod
    def __calculate_variation(current, requested):
        current = int(current)
        requested = int(requested)
        if current:
            return requested - current, (
                float(requested - current) / current) * 100
        else:
            if requested:
                return requested, 100
        return 0, 0

    @staticmethod
    def _quota_change_request_summary(rp, nova_quota, cinder_quota):
        diff_cores, percent_cores = QuotaChanger.__calculate_variation(
            nova_quota['cores'],
            rp['cores'])
        variation_cores = "%+d (%+d%%)" % (diff_cores, percent_cores)

        diff_instances, percent_intances = QuotaChanger.__calculate_variation(
            nova_quota['instances'], rp['instances'])
        variation_instances = "%+d (%+d%%)" % (diff_instances, percent_intances)

        diff_ram, percent_ram = QuotaChanger.__calculate_variation(
            int(nova_quota['ram']),
            rp['ram'])
        variation_ram = "%+d (%+d%%)" % (diff_ram, percent_ram)

        t = prettytable.PrettyTable(
            ["Quota", "Current", "Requested", "Variation"])
        t.add_row(["Cores", nova_quota['cores'], rp['cores'], variation_cores])
        t.add_row(["Instances", nova_quota['instances'], rp['instances'],
                   variation_instances])
        t.add_row(
            ["RAM (GB)", int(nova_quota['ram']), rp['ram'], variation_ram])

        if 'volumes' in rp.keys():
            for type, values in rp['volumes'].items():
                t.add_row(["", "", "", ""])
                current_volumes = cinder_quota[
                    'volumes_%s' % type]
                requested_volumes = values['volumes']

                diff_volumes, percent_volumes = QuotaChanger.__calculate_variation(
                    current_volumes, requested_volumes)
                variation_volumes = "%+d (%+d%%)" % (
                    diff_volumes, percent_volumes)

                current_gigabytes = cinder_quota[
                    'gigabytes_%s' % type]
                requested_gigabytes = values['gigabytes']

                diff_disk, percent_disk = QuotaChanger.__calculate_variation(
                    current_gigabytes, requested_gigabytes)
                variation_disk = "%+d (%+d%%)" % (diff_disk, percent_disk)

                t.add_row(
                    ["Volumes (%s)" % type, current_volumes,
                     requested_volumes, variation_volumes])
                t.add_row(
                    ["Diskspace (%s)" % type, current_gigabytes,
                     requested_gigabytes, variation_disk])

        t.border = True
        t.header = True
        t.align["Quota"] = 'c'
        t.align["Current"] = 'c'
        t.align["Requested"] = 'c'
        t.align["Variation"] = 'c'
        return t
