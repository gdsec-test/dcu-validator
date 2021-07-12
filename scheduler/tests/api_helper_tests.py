from mock import MagicMock, call, patch
from nose.tools import assert_false, assert_true

from scheduler_service.utils.api_helper import APIHelper


class TestAPIHelper:

    _jwt_call = call('https://sso.dev-godaddy.com/v1/api/token', json={'username': 'test-user', 'password': 'test-password'}, params={'realm': 'idp'})
    _status_check_call = call().raise_for_status()
    _patch_call = call(
        'http://localhost/v1/abuse/tickets/123',
        json={'closed': 'true', 'close_reason': 'some reason'},
        headers={'Authorization': 'test-jwt'}
    )

    @patch('requests.patch')
    @patch('requests.post')
    def test_close_incident(self, jwt_mock, close_mock):
        jwt_mock.return_value = MagicMock(raise_for_status=MagicMock(), text='{"data": "test-jwt"}')
        close_mock.return_value = MagicMock(status_code=204)
        assert_true(APIHelper().close_incident('123', 'some reason'))
        jwt_mock.assert_has_calls([self._jwt_call, self._status_check_call])
        close_mock.assert_has_calls([self._patch_call])

    @patch('requests.patch')
    @patch('requests.post')
    def test_bad_close_incident(self, jwt_mock, close_mock):
        jwt_mock.return_value = MagicMock(raise_for_status=MagicMock(), text='{"data": "test-jwt"}')
        close_mock.return_value = MagicMock(status_code=500)
        assert_false(APIHelper().close_incident('123', 'some reason'))
        jwt_mock.assert_has_calls([self._jwt_call, self._status_check_call])
        close_mock.assert_has_calls([self._patch_call])

    @patch('requests.patch')
    @patch('requests.post')
    def test_close_incident_expired_jwt(self, jwt_mock, close_mock):
        jwt_mock.return_value = MagicMock(raise_for_status=MagicMock(), text='{"data": "test-jwt"}')
        close_mock.side_effect = [MagicMock(status_code=401), MagicMock(status_code=204)]
        assert_true(APIHelper().close_incident('123', 'some reason'))
        jwt_mock.assert_has_calls([self._jwt_call, self._status_check_call, self._jwt_call, self._status_check_call])
        close_mock.assert_has_calls([self._patch_call, self._patch_call])
