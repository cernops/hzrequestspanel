from unittest import TestCase
import hzrequestspanel.api.projects.project_creator as api

import logging
import os


class TestProjectCreator(TestCase):
    def setUp(self):
        logging.getLogger("horizon.hzrequests").addHandler(
            logging.NullHandler())
        payload = {"ticket_type": "new_project", "username": "svchorizon",
                   "comments": "", "accounting_group": "IT",
                   "projectname": "makowals-unittests",
                   "description": "unittest for hzrequestspanel",
                   "owner": "svchorizon",
                   "egroup": "makowals-federated",
                   "instances": 25,
                   "cores": 25,
                   "ram": 50,
                   "gigabytes": 500,
                   "volumes": 5}
        self.request = api.NewProjectCreator(payload,
                                             config_file=os.path.dirname(
                                                                os.path.abspath(
                                                                    __file__)) + "/hzrequestspanel_test.conf")
        self.request._create_empty_snow_ticket(
            "Unit tests for hzrequestspanel")

    def tearDown(self):
        self.request.snowclient.change_ticket_state(self.request.ticket_number, "closed")

    def test_create_ticket_positive(self):
        self.request.create_ticket()

    def test_create_ticket_positive_requestor_primary_account(self):
        self.request.dict_data['username'] = "makowals"
        self.request.create_ticket()

    def test_create_ticket_positive_requestor_secondary_account(self):
        self.request.dict_data['username'] = "admjcast"
        self.request.create_ticket()

    def test_create_ticket_wrong_egroup(self):
        self.request.dict_data['egroup'] = "svchorizon"
        with self.assertRaises(api.SnowException):
            self.request.create_ticket()

    def test_get_primary_account_from_ldap(self):
        self.assertEquals(
            self.request._get_primary_account_from_ldap(
                "svchorizon"), "makowals")
        self.assertNotEquals(
            self.request._get_primary_account_from_ldap(
                "svchorizon"), "svchorizon")

    def test_verify_egroup_positive(self):
        self.request._verify_egroup("makowals-federated")

    def test_verify_egroup_negative(self):
        with self.assertRaises(api.SnowException):
            self.request._verify_egroup("makowals")
