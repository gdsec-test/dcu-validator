from nose.tools import assert_true
from scheduler_service.validators.domain_status import DomainStatusValidator
from mock import patch
from requests.sessions import Session
import requests


class TestDomainStatus:
    """Tests for the Domain Status Validator"""

    _ticket = {'sourceDomainOrIp': 'dmvsuspension.com', 'number': '123'}

    def setUp(self):
        self._domain_status = DomainStatusValidator('domain-service-end-point')

    @patch.object(Session, 'request')
    def test_validate_ticket_true_404(self, request):

        domain_service_resp = requests.Response()
        domain_service_resp.status_code = 404
        domain_service_resp._content = 'Not Found\n'
        request.return_value = domain_service_resp

        result = self._domain_status.validate_ticket(self._ticket)

        assert_true(result, (True,))

    @patch.object(Session, 'request')
    def test_get_validate_ticket_true_400(self, request):

        domain_service_resp = requests.Response()
        domain_service_resp.status_code = 400
        domain_service_resp._content = '{"error":"invalid character \'d\' looking for beginning of value","code":3}'
        request.return_value = domain_service_resp

        result = self._domain_status.validate_ticket(self._ticket)

        assert_true(result, (True,))

    @patch.object(Session, 'request')
    def test_validate_ticket_true_500(self, request):

        domain_service_resp = requests.Response()
        domain_service_resp.status_code = 500
        domain_service_resp._content = '{"error":"No Active shoppers for this Domain Name","code":13}'
        request.return_value = domain_service_resp

        result = self._domain_status.validate_ticket(self._ticket)

        assert_true(result, (True,))

    @patch.object(Session, 'request')
    def test_validate_ticket_true(self, request):

        domain_service_resp = requests.Response()
        domain_service_resp.status_code = 200
        domain_service_resp._content = '{"domain":"dmvsuspension.com",' \
                                       '"shopperId":"187897", ' \
                                       '"domainId":12345, ' \
                                       '"createDate":"10-15-2017", ' \
                                       '"status":"ACTIVE"}'
        request.return_value = domain_service_resp

        result = self._domain_status.validate_ticket(self._ticket)

        assert_true(result, (True,))

    @patch.object(Session, 'request')
    def test_validate_ticket_false(self, request):

        domain_service_resp = requests.Response()
        domain_service_resp.status_code = 200
        domain_service_resp._content = '{"domain":"dmvsuspension.com",' \
                                       '"shopperId":"187897", ' \
                                       '"domainId":12345, ' \
                                       '"createDate":"10-15-2017", ' \
                                       '"status":"SUSPENDED"}'

        request.return_value = domain_service_resp

        result = self._domain_status.validate_ticket(self._ticket)

        assert_true(result, (False, 'unworkable'))
