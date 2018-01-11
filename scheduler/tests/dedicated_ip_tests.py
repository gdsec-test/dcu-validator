from nose.tools import assert_equal
from scheduler.scheduler_service.validators.dedicated_ip import DedicatedIpValidator
from scheduler.scheduler_service.utils.ipam import Ipam
from mock import patch, MagicMock


class TestDedicated:

    def __init__(self):
        self._dedicated = DedicatedIpValidator()

    @patch.object(Ipam, 'get_properties_for_ip')
    def test_is_dedicated_ip(self, get_properties_for_ip):
        get_properties_for_ip.return_value = MagicMock(HostName='VEL4567')
        ticket = {'sourceDomainOrIp': '104.238.65.160'}
        result = self._dedicated.validate_ticket(ticket)
        return assert_equal(result, (True, ))

    @patch.object(Ipam, 'get_properties_for_ip')
    def test_is_not_dedicated_ip(self, get_properties_for_ip):
        get_properties_for_ip.return_value = MagicMock(HostName='p3plcpnl0940')
        ticket = {'sourceDomainOrIp': '160.153.77.227'}
        result = self._dedicated.validate_ticket(ticket)
        return assert_equal(result, (False, 'shared ip'))
