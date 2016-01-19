import logging
import os

from ConfigParser import ConfigParser
from ccitools.servicenow import ServiceNowClient

LOG = logging.getLogger(__name__)

def _get_config_data():
    config = ConfigParser()
    config.readfp(open(os.path.join(os.path.dirname(__file__),
                                    '../hzrequestspane.conf')))
    return config

def _create(dict_data, volume_type_name_list):
    config = _get_config_data()

    # Service Now data needed
    sn_user = config.get("servicenow", "sn_user")
    sn_pass = config.get("servicenow", "sn_pass")
    sn_instance = config.get("servicenow", "sn_instance")

    # Extra params needed
    short_description = config.get("servicenow",
                                   "sn_short_desc").format(dict_data['projectname'])
    funtional_element = config.get("servicenow", "sn_functional_element")
    group = config.get("servicenow", "sn_group")

    # Setup clients
    snowclient = ServiceNowClient(sn_user, sn_pass, instance=sn_instance)

    # Create the ticket
    ticket = snowclient.create_request(short_description, funtional_element,
                                       assignment_group=group)

    # Fill the ticket
    snowclient.create_quota_update(ticket.number, volume_type_name_list, dict_data)

    return ticket.number

def create(dict_data, volume_type_name_list):
    LOG.info("Creating service now ticket with: {0}".format(dict_data))
    ticket_number = ''
    try:
       ticket_number = _create(dict_data, volume_type_name_list)
       return {"ticket_number": ticket_number}
    except Exception as e:
        LOG.error(e.message)
        return {"error_message": e.message}
