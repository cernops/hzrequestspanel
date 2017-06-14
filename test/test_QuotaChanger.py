from unittest import TestCase
import hzrequestspanel.api.projects.quota_changer as api

import logging
import os


class TestQuotaChanger(TestCase):
    def setUp(self):
        logging.getLogger("horizon.hzrequests").addHandler(
            logging.NullHandler())
        payload = {"ticket_type": "quota_change", "username": "svchorizon",
                   "projectname": "Personal makowals", "comments": "",
                   "instances": 25, "cores": 25, "ram": 50,
                   "volumes": {"wig-cpio1": {"gigabytes": "0", "volumes": "0"},
                               "wig-cp1": {"gigabytes": "0", "volumes": "0"},
                               "cpio1": {"gigabytes": "0", "volumes": "0"},
                               "cp2": {"gigabytes": "0", "volumes": "0"},
                               "cp1": {"gigabytes": "0", "volumes": "0"},
                               "io1": {"gigabytes": "0", "volumes": "0"},
                               "standard": {"gigabytes": "500",
                                            "volumes": "5"}}, "current_quota": {
                "nova_quota": {"instances": "25", "cores": "25", "ram": "50"},
                "cinder_quota": {"gigabytes_wig-cpio1": "0",
                                 "volumes_wig-cpio1": "0",
                                 "gigabytes_wig-cp1": "0",
                                 "volumes_wig-cp1": "0", "gigabytes_cpio1": "0",
                                 "volumes_cpio1": "0", "gigabytes_cp2": "0",
                                 "volumes_cp2": "0", "gigabytes_cp1": "0",
                                 "volumes_cp1": "0", "gigabytes_io1": "0",
                                 "volumes_io1": "0",
                                 "gigabytes_standard": "500",
                                 "volumes_standard": "5"}}}
        self.request = api.QuotaChanger(payload,
                                        config_file=os.path.dirname(
                                                       os.path.abspath(
                                                           __file__)) + "/hzrequestspanel_test.conf")
        self.request._create_empty_snow_ticket(
            "Unit tests for hzrequestspanel")

    def tearDown(self):
        self.request.snowclient.change_ticket_state(self.request.ticket_number, "closed")

    def test_create_ticket_positive(self):
        self.request.create_ticket()

    def _test_add_coordinators_to_watchlist(self, experiment):
        self.request.dict_data['projectname'] = experiment + " " + self.request.dict_data['projectname']
        self.request.create_ticket()
        watch_list = self.request.snowclient.get_ticket(self.request.ticket_number).watch_list
        self.assertEqual(watch_list, "cloud-infrastructure-%s-resource-coordinators@cern.ch" % experiment)

    def test_add_coordinators_to_watchlist_atlas(self):
        self._test_add_coordinators_to_watchlist("atlas")

    def test_add_coordinators_to_watchlist_cms(self):
        self._test_add_coordinators_to_watchlist("cms")

    def test_add_coordinators_to_watchlist_lhcb(self):
        self._test_add_coordinators_to_watchlist("lhcb")