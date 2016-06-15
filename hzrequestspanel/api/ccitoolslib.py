import logging
import prettytable

from ccitools.servicenow import ServiceNowClient

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

SNOW_MESSAGE = """Dear HW Resources manager,

Could you please review the following quota update request?

%s
Also, could you please make sure that the numbers in the form correspond to your decision,
before you reassign this ticket to the "Cloud Infrastructure 3rd Level" FE? This will allow
for the automated update of the project quota. Thanks!

Best regards,
        Cloud Infrastructure Team"""

USER_MESSAGE = """Dear %s,

Your quota update request has been received and sent to
HW Resources management in order to be evaluated.

Your request will be applied after approval.

Thank you,
        Cloud Infrastructure Team"""

def __calculate_variation(current, requested):
    current = int(current)
    requested = int(requested)
    if current:
        return requested-current, (float(requested-current)/current)*100
    else:
        if requested:
            return requested, 100
    return 0, 0


def request_summary(rp, nova_quota, cinder_quota):
    diff_cores, percent_cores = __calculate_variation(nova_quota['cores'], rp['cores'])
    variation_cores = "%+d (%+d%%)" % (diff_cores, percent_cores)

    diff_instances, percent_intances = __calculate_variation(nova_quota['instances'], rp['instances'])
    variation_instances = "%+d (%+d%%)" % (diff_instances, percent_intances)

    diff_ram, percent_ram = __calculate_variation(int(nova_quota['ram']), rp['ram'])
    variation_ram = "%+d (%+d%%)" % (diff_ram, percent_ram)

    t = prettytable.PrettyTable(["Quota", "Current", "Requested", "Variation"])
    t.add_row(["Cores", nova_quota['cores'], rp['cores'], variation_cores])
    t.add_row(["Instances", nova_quota['instances'], rp['instances'], variation_instances])
    t.add_row(["RAM (GB)", int(nova_quota['ram']), rp['ram'], variation_ram ])

    if 'volume_quota' in rp.keys():
        for volume_quota in rp['volume_quota']:
            t.add_row(["","","",""])
            current_volumes = cinder_quota['volumes_%s' % volume_quota['type']]
            requested_volumes = volume_quota['volumes']

            diff_volumes, percent_volumes = __calculate_variation(current_volumes, requested_volumes)
            variation_volumes = "%+d (%+d%%)" % (diff_volumes, percent_volumes)

            current_gigabytes = cinder_quota['gigabytes_%s' % volume_quota['type']]
            requested_gigabytes = volume_quota['gigabytes']

            diff_disk, percent_disk =  __calculate_variation(current_gigabytes, requested_gigabytes)
            variation_disk = "%+d (%+d%%)" % (diff_disk, percent_disk)

            t.add_row(["Volumes (%s)" % volume_quota['type'], current_volumes, requested_volumes, variation_volumes])
            t.add_row(["Diskspace (%s)" % volume_quota['type'], current_gigabytes, requested_gigabytes, variation_disk])

    t.border = True
    t.header = True
    t.align["Quota"] = 'c'
    t.align["Current"] = 'c'
    t.align["Requested"] = 'c'
    t.align["Variation"] = 'c'
    return t

def rp_to_dict(rp, nova_quota, cinder_quota):
    """
    Creates a python dictionary with the fields and values from the RP.

    :param rp: Quota Update record Producer
    :param nova_quota: Nova quota object
    :param cinder_quota: Cinder quota object
    """
    rp_dict={}
    for field in rp.fields:
        if field == "volume_quota":
            for volume_quota in rp.volume_quota:
                if field not in rp_dict:
                    rp_dict[field] = []
                for key in volume_quota:
                    try:
                        if volume_quota[key]:
                            volume_quota[key] = int(volume_quota[key])
                        else:
                            volume_quota[key] = int(cinder_quota["%s_%s" % (key, volume_quota['type'])])
                    except ValueError:
                        logging.debug("'%s' can't be converted to Integer" % volume_quota[key])

                rp_dict[field].append(volume_quota)
        else:
            if rp.__getattr__(field):
                try:
                    rp_dict[field] = int(rp.__getattr__(field))
                except ValueError:
                    logging.debug("'%s' cant be converted to int" % rp.__getattr__(field))
                    rp_dict[field] = rp.__getattr__(field)

            else: #if requested empty, then load current value
                if field in nova_quota.keys():
                    rp_dict[field] = int(nova_quota[field])
                elif field in cinder_quota.keys():
                    rp_dict[field] = int(cinder_quota[field])

    return rp_dict


def summary_to_monospace(summary):
    summary = "<br/>".join(summary.get_string().split("\n"))
    summary = "%s%s%s" % ("[code]<pre>", summary, "</pre>[/code]")
    return summary

def worknote_message(rp, summary):
    return SNOW_MESSAGE % (summary_to_monospace(summary))
