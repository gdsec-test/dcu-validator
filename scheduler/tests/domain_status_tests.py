from unittest import TestCase
from unittest.mock import patch

import requests
from requests.sessions import Session

from scheduler_service.validators.domain_status import DomainStatusValidator


class TestDomainStatus(TestCase):
    """Tests for the Domain Status Validator"""

    _ticket = {'sourceDomainOrIp': 'dmvsuspension.com', 'number': '123'}

    def setUp(self):
        self._domain_status = DomainStatusValidator()

    @patch.object(Session, 'request')
    def test_validate_ticket_true_404(self, request):

        domain_service_resp = requests.Response()
        domain_service_resp.status_code = 404
        domain_service_resp._content = 'Not Found\n'
        request.return_value = domain_service_resp

        result = self._domain_status.validate_ticket(self._ticket)

        self.assertTrue(result, (True,))

    @patch.object(Session, 'request')
    def test_get_validate_ticket_true_400(self, request):

        domain_service_resp = requests.Response()
        domain_service_resp.status_code = 400
        domain_service_resp._content = '{"error":"invalid character \'d\' looking for beginning of value","code":3}'
        request.return_value = domain_service_resp

        result = self._domain_status.validate_ticket(self._ticket)

        self.assertTrue(result, (True,))

    @patch.object(Session, 'request')
    def test_validate_ticket_true_500(self, request):

        domain_service_resp = requests.Response()
        domain_service_resp.status_code = 500
        domain_service_resp._content = '{"error":"No Active shoppers for this Domain Name","code":13}'
        request.return_value = domain_service_resp

        result = self._domain_status.validate_ticket(self._ticket)

        self.assertTrue(result, (True,))

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

        self.assertTrue(result, (True,))

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

        self.assertTrue(result, (False, 'unworkable'))

    @patch.object(Session, 'request')
    def test_validate_ticket_corporate_name_portfolio(self, request):

        domain_service_resp = requests.Response()
        domain_service_resp.status_code = 200
        domain_service_resp._content = b'{"domain":"dmvsuspension.com",' \
                                       b'"shopperId":"187897", ' \
                                       b'"domainId":12345, ' \
                                       b'"createDate":"10-15-2017", ' \
                                       b'"status":"SUSPENDED"}'

        request.return_value = domain_service_resp
        self._ticket['data'] = {
            'domainQuery': {
                'shopperInfo': {
                    'vip': {
                        'portfolioType': 'CN'
                    }
                }
            }
        }

        result = self._domain_status.validate_ticket(self._ticket)

        self.assertEqual(result, (True, None))
