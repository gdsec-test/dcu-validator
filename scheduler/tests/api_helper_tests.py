from scheduler_service.utils.api_helper import APIHelper
from mock import patch, MagicMock
from nose.tools import assert_true, assert_false


class TestAPIHelper:

    @patch('requests.patch')
    def test_close_incident(self, mock):
        mock.return_value = MagicMock(status_code=204)
        assert_true(APIHelper().close_incident('123', 'some reason'))

    @patch('requests.patch')
    def test_bad_close_incident(self, mock):
        mock.return_value = MagicMock(status_code=500)
        assert_false(APIHelper().close_incident('123', 'some reason'))

