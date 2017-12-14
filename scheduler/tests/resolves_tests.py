from mock import patch, MagicMock
from nose.tools import assert_true, assert_false
from requests.sessions import Session

from scheduler_service.validators.resolves import Resolvable


class TestResolvable:

    url = 'http://comicsn.beer/'

    def __init__(self):
        self._resolvable = Resolvable()

    @patch.object(Session, 'request')
    def test_resolves_1xx(self, request):
        request.return_value = MagicMock(status_code=100)

        result = self._resolvable.resolves(self.url)

        return assert_true(result)

    @patch.object(Session, 'request')
    def test_resolves_2xx(self, request):
        request.return_value = MagicMock(status_code=200)

        result = self._resolvable.resolves(self.url)

        return assert_true(result)

    @patch.object(Session, 'request')
    def test_resolves_3xx(self, request):
        request.return_value = MagicMock(status_code=300)

        result = self._resolvable.resolves(self.url)

        return assert_true(result)

    @patch.object(Session, 'request')
    def test_resolves_403(self, request):
        request.return_value = MagicMock(status_code=403)

        result = self._resolvable.resolves(self.url)

        return assert_true(result)

    @patch.object(Session, 'request')
    def test_resolves_406(self, request):
        request.return_value = MagicMock(status_code=406)

        result = self._resolvable.resolves(self.url)

        return assert_true(result)

    @patch.object(Session, 'request')
    def test_not_resolves_404(self, request):
        request.return_value = MagicMock(status_code=404)

        result = self._resolvable.resolves(self.url)

        return assert_false(result)
