# coding: utf-8

from unittest import TestCase
import hzrequestspanel.api.projects.project_killer as api
from ccitools.utils.snow.ticket import RequestState

import logging
import os


class TestProjectKiller(TestCase):
    def setUp(self):
        logging.getLogger("horizon.hzrequests").addHandler(
            logging.NullHandler())
        payload = {"ticket_type": "delete_project",
                   "username": "jcastro",
                   "project_name": "Personal jcastro",
                   "comment": u"A spécial 人物"}
        self.request = api.ProjectKiller(payload,
                                         config_file=os.path.dirname(os.path.abspath(__file__)) +
                                                     "/hzrequestspanel_test.conf",
                                         keytab_file="/etc/openstack-dashboard/svcrdeck.keytab",
                                         )
        self.request._create_empty_snow_ticket(
            "Unit tests for hzrequestspanel")

    def tearDown(self):
        self.request.ticket.change_state(RequestState.CLOSED)
        self.request.ticket.save()

    def test_verify_project_owner_positive(self):
        self.request._verify_project_owner("Personal jcastro", "jcastro")

    def test_verify_project_owner_negative(self):
        with self.assertRaises(api.SnowException):
            self.request._verify_project_owner("Personal jcastro", "makowals")

    def test_create_ticket_positive(self):
        self.request.create_ticket()

    def test_create_ticket_wrong_owner(self):
        self.request.dict_data['username'] = "wiebalck"
        with self.assertRaises(api.SnowException):
            self.request.create_ticket()
