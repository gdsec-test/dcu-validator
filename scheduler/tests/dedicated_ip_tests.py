from unittest import TestCase
from unittest.mock import MagicMock, patch

from scheduler_service.validators.dedicated_ip import DedicatedIpValidator


class TestDedicated(TestCase):

    def setUp(self):
        self._dedicated = DedicatedIpValidator()

    @patch('scheduler_service.validators.dedicated_ip.Ipam', autospec=True)
    def test_is_dedicated_ip(self, ipam):
        ipamo = ipam.return_value
        ipamo.get_properties_for_ip.return_value = MagicMock(HostName='VEL4567')
        ticket = {'sourceDomainOrIp': '104.238.65.160'}
        result = self._dedicated.validate_ticket(ticket)
        self.assertEqual(result, (True, ))

    @patch('scheduler_service.validators.dedicated_ip.Ipam', autospec=True)
    def test_is_not_dedicated_ip(self, ipam):
        ipamo = ipam.return_value
        ipamo.get_properties_for_ip.return_value = MagicMock(HostName='p3plcpnl0940')
        ticket = {'sourceDomainOrIp': '160.153.77.227'}
        result = self._dedicated.validate_ticket(ticket)
        self.assertEqual(result, (False, 'shared_ip'))
