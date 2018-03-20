# coding: utf-8

from unittest import TestCase
import hzrequestspanel.api.projects.project_creator as api
from ccitools.utils.snow.ticket import RequestState

import logging
import os


class TestProjectCreator(TestCase):
    def setUp(self):
        logging.getLogger("horizon.hzrequests").addHandler(
            logging.NullHandler())
        payload = {
            "ticket_type": "new_project",
            "username": "svchorizon",
            "comment": u"A spécial 人物",
            "accounting_group": "IT",
            "project_name": "makowals-unittests",
            "description": "unittest for hzrequestspanel",
            "owner": "svchorizon",
            "egroup": "cloud-infrastructure-3rd-level",
            "instances": 25,
            "cores": 25,
            "ram": 50,
            "volumes": {
                'wig-cp1':  {'gigabytes': '0', u'volumes': '0'},
                'wig-cpio1': {'gigabytes': '0', u'volumes': '0'},
                'io1': {'gigabytes': '0', u'volumes': '0'},
                'standard': {'gigabytes': '0', u'volumes': '0'},
                'cp1': {'gigabytes': '0', u'volumes': '0'},
                'cpio1': {'gigabytes': '0', u'volumes': '0'}
            }
        }

        self.request = api.NewProjectCreator(payload,
                                             config_file=os.path.dirname(os.path.abspath(__file__)) +
                                                         "/hzrequestspanel_test.conf",
                                             keytab_file="/etc/openstack-dashboard/svcrdeck.keytab",)
        self.request._create_empty_snow_ticket(
            "Unit tests for hzrequestspanel")

    def tearDown(self):
        self.request.ticket.change_state(RequestState.CLOSED)
        self.request.ticket.save()

    def test_create_ticket_positive(self):
        self.request.create_ticket()

    def test_create_ticket_positive_requestor_primary_account(self):
        self.request.dict_data['username'] = "makowals"
        self.request.create_ticket()

    def test_create_ticket_positive_requestor_secondary_account(self):
        self.request.dict_data['username'] = "admjcast"
        self.request.create_ticket()

    def test_create_ticket_positive_multiple_egroups(self):
        egroups = "cloud-infrastructure-3rd-level,cloud-infrastructure-baremetal-admin"
        self.request.dict_data['egroup'] = egroups
        self.request.create_ticket()
        record_producer = self.request.snowclient.get_project_creation_rp(self.request.ticket.info.number)
        self.assertEqual(record_producer.egroup, egroups)

    def test_create_ticket_wrong_egroup(self):
        self.request.dict_data['egroup'] = "svchorizon"
        with self.assertRaises(api.SnowException):
            self.request.create_ticket()

    def test_get_primary_account_from_ldap(self):
        self.assertEquals(
            self.request._get_primary_account_from_ldap(
                "svchorizon"), "jcastro")
        self.assertNotEquals(
            self.request._get_primary_account_from_ldap(
                "svchorizon"), "svchorizon")

    def test_verify_egroup_positive(self):
        self.request._verify_egroup("cloud-infrastructure-3rd-level")

    def test_verify_egroup_negative(self):
        with self.assertRaises(api.SnowException):
            self.request._verify_egroup("makowals")

    def _test_add_coordinators_to_watchlist(self, experiment):
        self.request.dict_data['accounting_group'] = experiment
        self.request.create_ticket()
        watch_list = self.request.ticket.info.watch_list
        self.assertEqual(watch_list, "cloud-infrastructure-%s-resource-coordinators@cern.ch" % experiment)
