##############################################################################
# COPYRIGHT Ericsson AB 2013
#
# The copyright to the computer program(s) herein is the property of
# Ericsson AB. The programs may be used and/or copied only with written
# permission from Ericsson AB. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
##############################################################################

from litp.core.model_type import ItemType, Collection, Property, PropertyType
from litp.core.extension import ModelExtension
from litp.core.litp_logging import LitpLogger
from litp.core.validators import ItemValidator, ValidationError

import re
import netaddr

log = LitpLogger()


class NtpExtension(ModelExtension):
    """
    LITP Ntp Model Extension allows for the configuration of the ntp service
    on the MS and the managed nodes.

    Update and remove reconfiguration actions are supported for this plugin
    (with some exceptions - see the Validation section).

    An example ntp fqdn: 1.europe.pool.ntp.org
    """

    def define_property_types(self):
        property_types = [
            PropertyType("ntp_fqdn",
                         regex=r"^.*$"),
        ]

        return property_types

    def define_item_types(self):
        item_types = []

        item_types.append(ItemType("ntp-service",
                extend_item="software-item",
                item_description="This item type represents the LITP "
                                 "NTP (Network Time Protocol) service. "
                                 "This service enables clock synchronisation "
                                 "between the management server and "
                                 "external time servers, and between "
                                 "peer servers and the management server.",
                servers=Collection("ntp-server"),
            ))
        item_types.append(ItemType("ntp-server",
                item_description="This item type represents an NTP "
                                 "(Network Time Protocol) server.",
                server=Property("ntp_fqdn",
                    site_specific=True,
                    prop_description="Host address of a pool server.",
                    required=True),
                validators=[NtpServerValidator()]
            ))
        return item_types


class NtpServerValidator(ItemValidator):

    """
    Custom ItemValidator for ntp-server item type.

    Ensures the 'server' property has a correct ip or hostname format.

    """

    def validate(self, properties):
        if 'server' in properties:
            valid_hostname_regex = re.compile(r"^(([a-zA-Z0-9]|[a-zA-Z0-9]"
                r"[a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9]"
                r"[A-Za-z0-9\-]*[A-Za-z0-9])$")

            ip_no_prefix = re.sub(r'\/\d+$', '', properties['server'])

            find_hostname = re.match(valid_hostname_regex,
                                     properties['server'])
            try:
                find_ipv4 = netaddr.valid_ipv4(ip_no_prefix,
                                           netaddr.INET_PTON)
                find_ipv6 = netaddr.valid_ipv6(ip_no_prefix)
            except netaddr.AddrFormatError:
                return ValidationError(
                    property_name="server",
                    error_message="Invalid value '{0}'".format(properties[
                                                                   'server']))
            if not find_ipv4 and not find_ipv6 and find_hostname is None:
                return ValidationError(
                    property_name="server",
                    error_message="The property 'server' has incorrect format")
