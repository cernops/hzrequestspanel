from unittest import TestCase
import hzrequestspanel.api.projects.project_killer as api

import logging
import os


class TestProjectKiller(TestCase):
    def setUp(self):
        logging.getLogger("horizon.hzrequests").addHandler(
            logging.NullHandler())
        payload = {"ticket_type": "delete_project", "username": "makowals",
                   "project_name": "Personal makowals", "comment": ""}
        self.request = api.ProjectKiller(payload,
                                         config_file=os.path.dirname(
                                                          os.path.abspath(
                                                              __file__)) + "/hzrequestspanel_test.conf")
        self.request._create_empty_snow_ticket(
            "Unit tests for hzrequestspanel")

    def tearDown(self):
        self.request.snowclient.change_ticket_state(self.request.ticket_number, "closed")

    def test_verify_project_owner_positive(self):
        self.request._verify_project_owner("Personal makowals", "makowals")

    def test_verify_project_owner_negative(self):
        with self.assertRaises(api.SnowException):
            self.request._verify_project_owner("Personal makowals", "svchorizon")

    def test_create_ticket_positive(self):
        self.request.create_ticket()

    def test_create_ticket_wrong_owner(self):
        self.request.dict_data['username'] = "jcastro"
        with self.assertRaises(api.SnowException):
            self.request.create_ticket()
