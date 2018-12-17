from mock import MagicMock, patch
from nose.tools import assert_true
from requests.sessions import Session

from scheduler_service.validators.resolves import ResolvesValidator


class TestResolvable:

    url = 'http://comicsn.beer/'
    doc = {'number': '123', 'source': url}

    def __init__(self):
        self._resolvable = ResolvesValidator()

    @patch.object(Session, 'request')
    def test_resolves_1xx(self, request):
        request.return_value = MagicMock(status_code=100)

        result = self._resolvable.validate_ticket(self.doc)

        return assert_true(result == (True,))

    @patch.object(Session, 'request')
    def test_resolves_2xx(self, request):
        request.return_value = MagicMock(status_code=200)

        result = self._resolvable.validate_ticket(self.doc)

        return assert_true(result == (True,))

    @patch.object(Session, 'request')
    def test_resolves_3xx(self, request):
        request.return_value = MagicMock(status_code=300)

        result = self._resolvable.validate_ticket(self.doc)

        return assert_true(result == (True,))

    @patch.object(Session, 'request')
    def test_resolves_403(self, request):
        request.return_value = MagicMock(status_code=403)

        result = self._resolvable.validate_ticket(self.doc)

        return assert_true(result == (True,))

    @patch.object(Session, 'request')
    def test_resolves_406(self, request):
        request.return_value = MagicMock(status_code=406)

        result = self._resolvable.validate_ticket(self.doc)

        return assert_true(result == (True,))

    @patch.object(Session, 'request')
    def test_not_resolves_404(self, request):
        request.return_value = MagicMock(status_code=404)

        result = self._resolvable.validate_ticket(self.doc)

        return assert_true(result == (False, 'unresolvable'))
