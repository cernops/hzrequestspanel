import logging

from ccitools.cloud import CloudClient
from ccitools.servicenow import ServiceNowClient

LOG = logging.getLogger(__name__)

def _create(dict_data, volume_type_name_list):
    # Service Now data needed
    sn_user = ''
    sn_pass = ''
    sn_instance = 'cerntest'

    # Setup clients
    snowclient = ServiceNowClient(sn_user, sn_pass, instance=sn_instance)
    cloud = CloudClient()

    # Extra params needed
    short_description = "Request change of resource quota for the " \
                        "Cloud Project: {0}".format(dict_data['projectname'])
    funtional_element = "Cloud Infrastructure"
    group = "Cloud Infrastructure 3rd Line Support"
 
    # Create the ticket
    ticket = snowclient.create_request(short_description, funtional_element,
                                       assignment_group=group)
    # Fill the ticket
    snowclient.create_quota_update(ticket.number, volume_type_name_list, dict_data)

    return ticket.number

def create(dict_data):
    LOG.info("Creating service now ticket with: {0}".format(dict_data))
    # Call Daniel's function
    ticket_id = ''
    try {
       ticket_id = _create(dict_data, volume_type_name_list)
       return {"ticket_id": ticket_id}
    } except Exception as e:
        LOG.error(e.message)
        return {"error_message": e.message}
    }
