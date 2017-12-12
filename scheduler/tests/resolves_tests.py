from nose.tools import assert_true, assert_false

from scheduler.validators.resolves import Resolvable


class TestResolvable:

    def __init__(self):
        self._resolvable = Resolvable()

    def test_resolves(self):
        url = 'http://comicsn.beer'

        result = self._resolvable.resolves(url)

        return assert_true(result)

    def test_not_resolves(self):
        url = 'http://comicsn.beer/puppies'

        result = self._resolvable.resolves(url)

        return assert_false(result)

    def test_resolves_proxy(self):
        url = 'http://comicsn.beer/puppies'

        result = self._resolvable.resolves(url, proxy=True)

        return assert_true(result)
