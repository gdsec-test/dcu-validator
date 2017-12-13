from nose.tools import assert_true, assert_false
from mock import patch
from scheduler.validators.parked import Parked


class TestParked:

    def __init__(self):
        self._park = Parked()

    @patch('scheduler.validators.parked.Parked.is_not_parked')
    def test_is_not_parked_domain_ip(self, ip):
        ip.return_value = '184.168.221.47'
        domain = 'comicsn.tech'
        content = ''
        url = 'http://comicsn.tech/test.html'

        result = self._park.is_not_parked(domain, content, url)

        return assert_false(result)

    @patch('scheduler.validators.parked.Parked.is_not_parked')
    def test_is_not_parked_regex(self, ip):
        ip.return_value = '160.153.77.227'
        domain = 'comicsn.beer'
        content = 'OMG, its a Future home of something quite cool!!!!1!!1!!! Coming Soon'
        url = 'http://comicsn.beer/test.html'

        result = self._park.is_not_parked(domain, content, url)

        return assert_false(result)

    @patch('scheduler.validators.parked.Parked.is_not_parked')
    def test_is_not_parked_suspended(self, ip):
        ip.return_value = '160.153.77.227'
        domain = 'comicsn.beer'
        content = ''
        url = 'http://comicsn.beer/cgi-sys/suspendedpage.cgi'

        result = self._park.is_not_parked(domain, content, url)

        return assert_false(result)

    def test_is_not_parked_true(self):
        domain = 'comicsn.beer'
        content = 'just a website'
        url = 'http://comicsn.beer/index.php'

        result = self._park.is_not_parked(domain, content, url)

        return assert_true(result)

    def test_is_not_parked_ip_ip(self):
        domain = '184.168.221.47'
        content = ''
        url = '184.168.221.47/index.php'

        result = self._park.is_not_parked(domain, content, url)

        return assert_false(result)
