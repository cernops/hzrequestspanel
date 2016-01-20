import logging

from ConfigParser import ConfigParser
from ccitools.servicenow import ServiceNowClient

LOG = logging.getLogger(__name__)

def _get_config_data():
    config = ConfigParser()
    try:
        config.readfp(open('/etc/openstack-dashboard/hzrequestspanel.conf'))
    except Exception as e:
        LOG.error("Error reading hzrequestspanel.conf file:" + e.message)

    return config

def _create(dict_data, volume_type_name_list):
    LOG.info("Reading SNOW config file")
    config = _get_config_data()

    LOG.info("Reading vars from [servicenow] section in config file")
    # Service Now data needed
    sn_user = config.get("servicenow", "sn_user")
    sn_pass = config.get("servicenow", "sn_pass")
    sn_instance = config.get("servicenow", "sn_instance")

    # Extra params needed
    short_description = config.get("servicenow",
                                   "sn_short_desc").format(dict_data['projectname'])
    funtional_element = config.get("servicenow", "sn_functional_element")
    group = config.get("servicenow", "sn_group")

    snowclient = None
    ticket = None

    # Setup clients
    LOG.info("Instanciate SNOW client")
    try:
        snowclient = ServiceNowClient(sn_user, sn_pass, instance=sn_instance)
    except Exception as e:
        LOG.error("Error instanciating snow client:" + e.message)

    # Create the ticket
    LOG.info("Create SNOW ticket short_description: '{0}', " \
             "funtional_element: '{1}', assignment_group: " \
             "'{2}'".format(short_description, funtional_element,group))
    try:
        ticket = snowclient.create_request(short_description, funtional_element,
                                           assignment_group=group)
    except Exception as e:
        LOG.error("Error creating ticket:" + e.message)

    # Fill the ticket
    LOG.info("Update SNOW ticket ticket.number: '{0}', " \
             "volume_type_name_list: {1}, dict_data: {2}".format(ticket.number,
                                                             volume_type_name_list,
                                                             dict_data))
    try:
        snowclient.create_quota_update(ticket.number, volume_type_name_list, dict_data)
    except Exception as e:
        LOG.error("Error updating snow ticket:" + e.message)

    return ticket.number

def create(dict_data, volume_type_name_list):
    LOG.info("Creating service now ticket with: {0}".format(dict_data))
    ticket_number = ''
    try:
       ticket_number = _create(dict_data, volume_type_name_list)
       LOG.info("SNOW ticket created successfully")
       return {"ticket_number": ticket_number}
    except Exception as e:
        LOG.error("Error creating SNOW ticket: " + e.message)
        return {"error_message": e.message}
