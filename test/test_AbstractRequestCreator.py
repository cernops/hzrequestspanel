from unittest import TestCase
import hzrequestspanel.api.projects as api

import logging
import os


class TestAbstractRequestCreator(TestCase):
    def setUp(self):
        logging.getLogger("horizon.hzrequests").addHandler(
            logging.NullHandler())
        self.request = api.AbstractRequestCreator(
            {'username': 'svchorizon'}, config_file=os.path.dirname(
                os.path.abspath(__file__)) + "/hzrequestspanel_test.conf")
        self.request._create_empty_snow_ticket("Unit tests for hzrequestspanel")

    def tearDown(self):
        self.request.snowclient.change_ticket_state(self.request.ticket_number, "closed")

    def test_get_primary_account_from_ldap(self):
        self.assertEquals(
            api.AbstractRequestCreator._get_primary_account_from_ldap(
                "svchorizon"), "makowals")
        self.assertNotEquals(
            api.AbstractRequestCreator._get_primary_account_from_ldap(
                "svchorizon"), "svchorizon")

    def test_verify_egroup_positive(self):
        api.AbstractRequestCreator._verify_egroup("makowals-federated")

    def test_verify_egroup_negative(self):
        with self.assertRaises(api.SnowException):
            api.AbstractRequestCreator._verify_egroup("makowals")
