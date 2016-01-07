import logging
LOG = logging.getLogger(__name__)
def create(dict_data):
    LOG.info("Creating service now ticket with: ".format(dict_data))
    # Call Daniel's function
    return {"status_code": 201, "ticket_id": "INC74616"}
