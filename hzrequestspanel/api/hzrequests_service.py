import logging

from ConfigParser import ConfigParser
from ccitools.servicenow import ServiceNowClient
from hzrequestspanel.api.ccitoolslib import *

LOG = logging.getLogger('horizon.hzrequests')
LOG.setLevel(logging.INFO)

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
    functional_element_escalate = config.get("servicenow", "sn_functional_element_escalate")
    group_escalate = config.get("servicenow", "sn_group_escalate")

    watchlist_departments = [dep.lower() for dep in config.get("servicenow", "watchlist_departments").split()]
    watchlist_egroup_template = config.get("servicenow", "watchlist_egroup_template")

    snowclient = None
    ticket = None

    default_exception = Exception("Unable to create the ticket. Please retry. " \
                                  "If the problem persists, contact " \
                                  "the Cloud Team")

    # Setup clients
    LOG.info("Instanciate SNOW client")
    try:
        snowclient = ServiceNowClient(sn_user, sn_pass, instance=sn_instance)
    except Exception as e:
        LOG.error("Error instanciating snow client:" + e.message)
        raise default_exception

    # Create the ticket
    LOG.info("Create SNOW ticket short_description: '{0}', " \
             "funtional_element: '{1}', assignment_group: " \
             "'{2}'".format(short_description, funtional_element,group))
    try:
        ticket = snowclient.create_request(short_description, funtional_element,
                                           assignment_group=group)
    except Exception as e:
        LOG.error("Error creating ticket:" + e.message)
        raise default_exception

    # Fill the ticket
    LOG.info("Update SNOW ticket '{0}', volume_type_name_list: {1}, " \
             "dict_data: {2}".format(ticket.number,
                                     volume_type_name_list,
                                     dict_data))
    try:
        snowclient.create_quota_update(ticket.number, volume_type_name_list, dict_data)
    except Exception as e:
        LOG.error("Error updating snow ticket:" + e.message)
        raise default_exception

    # Add experiment resource coordinator to the watchlist
    add_to_watchlist(snowclient, ticket.number, watchlist_departments, watchlist_egroup_template)

    # Scalate the ticket to other FE
    LOG.info("Escalate ticket '{0}' to FE {1} and group " \
             "{2}".format(ticket.number,
                          functional_element_escalate,
                          group_escalate))
    try:
        escalate_ticket(snowclient, ticket.number, functional_element_escalate, group_escalate, dict_data)
    except Exception as e:
        msg = "Error escalating snow ticket {0} to FE '{1}' and Group " \
              "'{2}': ".format(ticket.number, functional_element_escalate, group_escalate)
        LOG.error(msg + e.message)
        raise Exception("Your ticket {0} has been successfully created, " \
                        "however we have identified some issues during the " \
                        "process. Please go to Service-Now and verify your " \
                        "request. If you find any problems, please contact " \
                        "the Cloud Team.".format(ticket.number))

    return ticket.number

def create(dict_data, volume_type_name_list):
    LOG.info("Creating service now ticket with: {0}".format(dict_data))
    ticket_number = _create(dict_data, volume_type_name_list)
    LOG.info("SNOW ticket created successfully")
    return {"ticket_number": ticket_number}

def add_to_watchlist(snowclient, ticket_number, watchlist_departments, watchlist_egroup_template):
    rp = snowclient.get_quota_update_request_rp(ticket_number)
    project_name = rp.project_name.lower()
    department = [dep for dep in watchlist_departments if project_name.startswith(dep)]
    if len(department) != 0:
        LOG.info("[ OK ] Adding '%s' to %s" % (watchlist_egroup_template % department[0], ticket_number))
        snowclient.add_email_watch_list(ticket_number, watchlist_egroup_template % department[0])
    else:
        LOG.info("No need of adding resource coordinator to the watchlist")

def escalate_ticket(snowclient, ticket_number, fe, asign_group, dict_data):
    LOG.info("GET record producer from SNOW with ticket '{0}'".format(ticket_number))
    rp = snowclient.get_quota_update_request_rp(ticket_number)

    LOG.info("Get username from ticket number '{0}'".format(ticket_number))
    username = snowclient.users.getRecords(sys_id=snowclient.get_ticket(ticket_number).u_caller_id)[0].first_name

    LOG.info("Add comment to ticket number '{0}'".format(ticket_number))
    snowclient.add_comment(ticket_number, USER_MESSAGE % username)

    rp_dict = rp_to_dict(rp,
                         dict_data['current_quota']['nova_quota'],
                         dict_data['current_quota']['cinder_quota'])

    LOG.info("Getting request summary")
    req_summary = request_summary(rp_dict,
                                  dict_data['current_quota']['nova_quota'],
                                  dict_data['current_quota']['cinder_quota'])
    LOG.info("Getting worknote message")
    worknote_msg = worknote_message(ticket_number, req_summary)
    LOG.info("Add worknote to ticket number '{0}'".format(ticket_number))
    snowclient.add_work_note(ticket_number, worknote_msg)

    LOG.info("Escalate ticket number '{0}' to FE '{1}' and Group " \
             "'{2}'".format(ticket_number, fe, asign_group))
    snowclient.change_functional_element(ticket_number, fe, asign_group)
