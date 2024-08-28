##############################################################################
# COPYRIGHT Ericsson AB 2013
#
# The copyright to the computer program(s) herein is the property of
# Ericsson AB. The programs may be used and/or copied only with written
# permission from Ericsson AB. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
##############################################################################


import unittest
from ntp_extension.ntp_extension import NtpExtension, NtpServerValidator
from litp.core.validators import ValidationError

class TestNtpExtension(unittest.TestCase):

    def setUp(self):
        self.ext = NtpExtension()

    def test_item_types_registered(self):
        item_types_expected = ['ntp-service','ntp-server']
        item_types = [it.item_type_id for it in
                      self.ext.define_item_types()]
        self.assertEquals(item_types_expected, item_types)

    def test_property_types_registered(self):
        expected_property_types = ['ntp_fqdn']
        actual_property_types = [pt.property_type_id for pt in
                                 self.ext.define_property_types()]
        self.assertEquals(expected_property_types, actual_property_types)

    def test_ntp_fqdn_hostname(self):
        validator = NtpServerValidator()

        # Check valid hostname
        properties = {'server': 'ms1'}

        error = validator.validate(properties)
        self.assertEquals(None, error)

        # Check invalid hostname
        invalid_exp = ['.', '/', '-hostname', 'host_name', 'hostn@me',
                       'hostn#me', 'host~name']

        for exp in invalid_exp:
            properties = {'server': exp}

            error = validator.validate(properties)
            expected = ValidationError(property_name="server",
                                       error_message="The property 'server' has "
                                                     "incorrect format")
            self.assertEquals(expected, error)

    def test_ntp_fqdn_ipv4(self):
        validator = NtpServerValidator()

        # Check valid IPv4
        properties = {'server': '192.168.0.1'}

        error = validator.validate(properties)
        self.assertEquals(None, error)

        # Check valid IPv4 - fully expanded with prefix
        properties = {'server': '192.168.0.1/128'}

        error = validator.validate(properties)
        self.assertEquals(None, error)

        # Check invalid IPv4 address - O instead of 0
        properties = {'server': ""}

        error = validator.validate(properties)
        expected = ValidationError(property_name="server",
                                   error_message="The property 'server' has "
                                                 "incorrect format")

    def test_ntp_fqdn_ipv6(self):
        validator = NtpServerValidator()

        # Check valid IPv6 - fully expanded
        properties = {'server': '2001:1b70:6207:5f:0000:4024:5622:1c'}

        error = validator.validate(properties)
        self.assertEquals(None, error)

        # Check valid IPv6 - fully expanded with prefix
        properties = {'server': '2001:1b70:6207:5f:0000:4024:5622:1c/64'}

        error = validator.validate(properties)
        self.assertEquals(None, error)

        # Check valid IPv6 - with padding
        properties = {'server': '2001:1b70:6207:5f::4024:5622:1c'}

        error = validator.validate(properties)
        self.assertEquals(None, error)

        # Check valid IPv6 - fully padded
        properties = {'server': '2001::1c'}

        error = validator.validate(properties)
        self.assertEquals(None, error)

        # Check invalid IPv6 address - O instead of 0
        properties = {'server': "2001:1b70:62O7:5f::4024:5622:1c"}

        error = validator.validate(properties)
        expected = ValidationError(property_name="server",
                                   error_message="The property 'server' has "
                                                 "incorrect format")

        self.assertEquals(expected, error)

        # Check invalid IPv6 address - No support for port numbers
        properties = {'server': "[2001:1b70::1c]:22"}

        error = validator.validate(properties)
        expected = ValidationError(property_name="server",
                                   error_message="The property 'server' has "
                                                 "incorrect format")

        self.assertEquals(expected, error)

        # Check invalid IPv6 address - No support for IP address in a URL
        properties = {'server': "http://[2001:1b70::1c]:22"}

        error = validator.validate(properties)
        expected = ValidationError(property_name="server",
                                   error_message="The property 'server' has "
                                                 "incorrect format")

        self.assertEquals(expected, error)

        # Check invalid IPv6 address - Outside range
        properties = {'server': "2001:1b70:62O7:5g::4024:5622:1c"}

        error = validator.validate(properties)
        expected = ValidationError(property_name="server",
                                   error_message="The property 'server' has "
                                                 "incorrect format")

        self.assertEquals(expected, error)

if __name__ == '__main__':
    unittest.main()
