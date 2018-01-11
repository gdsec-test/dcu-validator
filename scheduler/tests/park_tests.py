from nose.tools import assert_equal
from mock import patch, MagicMock
from ..scheduler_service.validators.not_parked import ParkedValidator


class TestParked:

    def __init__(self):
        self._park = ParkedValidator()

    @patch.object(ParkedValidator, '_get_content')
    def test_is_parked_regex(self, _get_content):

        ticket = {'sourceDomainOrIp' : '160.153.77.227', 'source': 'http://comicsn.beer/test.html'}
        _get_content.return_value = MagicMock(content='OMG, its a Future home of something quite cool!!!!1!!1!!! Coming Soon')

        result = self._park.validate_ticket(ticket)

        return assert_equal(result, (False, 'parked'))

    @patch.object(ParkedValidator, '_get_content')
    def test_is_parked_suspended(self, _get_content):
        ticket = {'sourceDomainOrIp': '160.153.77.227', 'source': 'http://comicsn.beer/cgi-sys/suspendedpage.cgi'}
        _get_content.return_value = MagicMock(content='')

        result = self._park.validate_ticket(ticket)

        return assert_equal(result, (False, 'parked'))

    @patch.object(ParkedValidator, '_get_content')
    def test_is_not_parked_true(self, _get_content):
        ticket = {'sourceDomainOrIp': '160.153.77.227', 'source': 'http://comicsn.beer/index.php'}
        _get_content.return_value = MagicMock(content='just a website')

        result = self._park.validate_ticket(ticket)

        return assert_equal(result, (True, ))

    @patch.object(ParkedValidator, '_get_content')
    def test_is_parked_ip(self, _get_content):
        ticket = {'sourceDomainOrIp': '184.168.221.47', 'source': '184.168.221.47/index.php'}
        _get_content.return_value = MagicMock(content='')

        result = self._park.validate_ticket(ticket)

        return assert_equal(result, (False, 'parked'))
