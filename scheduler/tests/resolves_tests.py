from unittest import TestCase
from unittest.mock import MagicMock, patch

from requests.sessions import Session

from scheduler_service.validators.resolves import ResolvesValidator


class TestResolvable(TestCase):

    url = 'http://comicsn.beer/'
    doc = {'number': '123', 'source': url, 'proxy': 'USA'}

    def setUp(self):
        self._resolvable = ResolvesValidator()

    @patch.object(Session, 'request')
    def test_resolves_1xx(self, request):
        request.return_value = MagicMock(status_code=100)
        result = self._resolvable.validate_ticket(self.doc)
        self.assertEqual(result, (True,))
        self.assertTrue(request.called)

    @patch.object(Session, 'request')
    def test_resolves_2xx(self, request):
        request.return_value = MagicMock(status_code=200)
        result = self._resolvable.validate_ticket(self.doc)
        self.assertEqual(result, (True,))
        self.assertTrue(request.called)

    @patch.object(Session, 'request')
    def test_resolves_3xx(self, request):
        request.return_value = MagicMock(status_code=300)
        result = self._resolvable.validate_ticket(self.doc)
        self.assertEqual(result, (True,))
        self.assertTrue(request.called)

    @patch.object(Session, 'request')
    def test_resolves_403(self, request):
        request.return_value = MagicMock(status_code=403)
        result = self._resolvable.validate_ticket(self.doc)
        self.assertEqual(result, (True,))
        self.assertTrue(request.called)

    @patch.object(Session, 'request')
    def test_resolves_406(self, request):
        request.return_value = MagicMock(status_code=406)
        result = self._resolvable.validate_ticket(self.doc)
        self.assertEqual(result, (True,))
        self.assertTrue(request.called)

    @patch.object(Session, 'request')
    def test_not_resolves_404(self, request):
        request.return_value = MagicMock(status_code=404)
        result = self._resolvable.validate_ticket(self.doc)
        self.assertEqual(result, (False, 'unresolvable'))
        self.assertTrue(request.called)

    @patch.object(Session, 'request')
    def test_not_resolves_empty_proxy(self, request):
        request.return_value = MagicMock(status_code=404)
        self.doc['proxy'] = ''
        result = self._resolvable.validate_ticket(self.doc)
        self.assertEqual(result, (False, 'unresolvable'))
        self.assertTrue(request.called)

    def test_not_resolves_disallowed_proxy(self):
        self.doc['proxy'] = 'DEU'
        result = self._resolvable.validate_ticket(self.doc)
        self.assertEqual(result, (True,))

    @patch.object(Session, 'request')
    def test_not_resolves_missing_proxy(self, request):
        request.return_value = MagicMock(status_code=404)
        del self.doc['proxy']
        result = self._resolvable.validate_ticket(self.doc)
        self.assertEqual(result, (False, 'unresolvable'))
        self.assertTrue(request.called)

    @patch.object(ResolvesValidator, '_verify_connection', return_value=True)
    def test_not_resolves_connection_error(self, verify_connection):
        url = 'http://i.i'  # domain that doesn't exist to cause: [Errno -2] Name or service not known
        self.doc['source'] = url
        result = self._resolvable.validate_ticket(self.doc)
        self.assertEqual(result, (False, 'unresolvable'))
        self.assertTrue(verify_connection.called)

    def test_not_resolves_non_connection_error(self):
        url = ''
        self.doc['source'] = url
        result = self._resolvable.validate_ticket(self.doc)
        self.assertEqual(result, (True,))
