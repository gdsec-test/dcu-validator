import requests
from mock import patch
from nose.tools import assert_true
from requests.sessions import Session

from scheduler_service.validators.netcraft_check import NetcraftValidator


class TestNetcraftValidator:
    """Tests for the Netcraft Check Validator"""

    _netcraft_ticket = {'reporter': '0000', 'number': '123'}
    _other_ticket = {'reporter': '1111', 'number': '456'}

    def setUp(self):
        self._netcraft_check = NetcraftValidator()

    @patch.object(Session, 'request')
    def test_validate_netcraft_resolved(self, request):

        netcraft_check_resp = requests.Response()
        netcraft_check_resp.status_code = 200
        netcraft_check_resp._content = 'some html with <div class_="alert alert-success">, etc.'

        request.return_value = netcraft_check_resp

        result = self._netcraft_check.validate_ticket(self._netcraft_ticket)

        assert_true(result, (False, 'resolved'))

    @patch.object(Session, 'request')
    def test_validate_netcraft_not_resolved(self, request):

        netcraft_check_resp = requests.Response()
        netcraft_check_resp.status_code = 200
        netcraft_check_resp._content = 'some html without resolved indicator'

        request.return_value = netcraft_check_resp

        result = self._netcraft_check.validate_ticket(self._netcraft_ticket)

        assert_true(result, (True, ))

    @patch.object(Session, 'request')
    def test_validate_netcraft_other(self, request):

        netcraft_check_resp = requests.Response()
        netcraft_check_resp.status_code = 404
        netcraft_check_resp._content = 'Page not found'

        request.return_value = netcraft_check_resp

        result = self._netcraft_check.validate_ticket(self._netcraft_ticket)

        assert_true(result, (True, ))

    @patch.object(Session, 'request')
    def test_validate_not_netcraft(self, request):

        result = self._netcraft_check.validate_ticket(self._other_ticket)

        assert_true(result, (True, ))
