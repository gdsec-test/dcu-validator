from nose.tools import assert_true, assert_false

from scheduler.validators.parked import Parked


class TestParked:

    def __init__(self):
        self._park = Parked()

    def test_is_parked_domain_ip(self):
        domain = 'comicsn.tech'
        content = ''
        url = 'http://comicsn.tech/test.html'

        result = self._park.is_parked(domain, content, url)

        return assert_true(result)

    def test_is_parked_regex(self):
        domain = 'comicsn.beer'
        content = 'OMG, its a Future home of something quite cool!!!!1!!1!!! Coming Soon'
        url = 'http://comicsn.beer/test.html'

        result = self._park.is_parked(domain, content, url)

        return assert_true(result)

    def test_is_parked_suspended(self):
        domain = 'comicsn.beer'
        content = ''
        url = 'http://comicsn.beer/cgi-sys/suspendedpage.cgi'

        result = self._park.is_parked(domain, content, url)

        return assert_true(result)

    def test_is_parked_false(self):
        domain = 'comicsn.beer'
        content = 'just a website'
        url = 'http://comicsn.beer/index.php'

        result = self._park.is_parked(domain, content, url)

        return assert_false(result)

    def test_is_parked_ip_ip(self):
        domain = '184.168.221.47'
        content = ''
        url = '184.168.221.47/index.php'

        result = self._park.is_parked(domain, content, url)

        return assert_true(result)
