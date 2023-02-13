from unittest import TestCase
from unittest.mock import MagicMock, patch

from scheduler_service.validators.not_parked import ParkedValidator


class TestParked(TestCase):

    def setUp(self):
        self._park = ParkedValidator()

    @staticmethod
    def make_resolver_mock(ip: str) -> MagicMock:
        return MagicMock(
            resolve=MagicMock(
                return_value=[
                    MagicMock(address=ip)
                ]
            )
        )

    def test_is_not_parked_ip_true(self):
        ticket = {'sourceDomainOrIp': '184.168.221.47'}
        result = self._park.validate_ticket(ticket)
        self.assertEqual(result, (True, None))

    def test_is_parked_ip(self):
        ticket = {'sourceDomainOrIp': '34.102.136.180'}
        result = self._park.validate_ticket(ticket)
        self.assertEqual(result, (False, 'parked'))

    @patch('dns.resolver.Resolver')
    def test_is_parked_domain(self, mocked_resolver):
        mocked_resolver.return_value = self.make_resolver_mock('34.102.136.180')
        ticket = {'sourceDomainOrIp': 'randomtestdomainthatshouldneverexist.randomthing'}
        result = self._park.validate_ticket(ticket)
        self.assertEqual(result, (False, 'parked'))

    @patch('dns.resolver.Resolver')
    def test_is_not_parked_domain(self, mocked_resolver):
        mocked_resolver.return_value = self.make_resolver_mock('127.0.0.1')
        ticket = {'sourceDomainOrIp': 'randomtestdomainthatshouldneverexist.randomthing'}
        result = self._park.validate_ticket(ticket)
        self.assertEqual(result, (True, None))
