from nose.tools import assert_true, assert_false
from scheduler_service.validators.domain_status import DomainStatusValidator
from mock import patch, MagicMock
from requests.sessions import Session


import requests


class TestDomainStatus:



    def __init__(self):
        self._domain_status = DomainStatusValidator('domain-service-end-point')

    @patch.object(Session, 'request')
    def test_get_domain_status_active(self, request):
        ticket = {'sourceDomainOrIp': 'dmvsuspension.com', 'number': '123'}

        request.return_value = MagicMock(status_code=200)
        domain_status_result = self._domain_status.get_domain_status(ticket)

        assert_true(domain_status_result, 'ACTIVE')


        # {"domain": "dmvsuspension.com",
        # "shopperId": "12345",
        # "domainId": 85789,
        # "createDate": "10-05-2006",
        # "status": "ACTIVE"}

    @patch.object(Session, 'request')
    def test_get_domain_status_not_active(self, request):
        ticket = {'sourceDomainOrIp': 'dmvsuspension.com', 'number': '123'}

        request.return_value = MagicMock(status_code=404)
        domain_status_result = self._domain_status.get_domain_status(ticket)

        assert_true(domain_status_result, 'Unable to query domain status')

    @patch.object(DomainStatusValidator, 'get_domain_status')
    def test_validate_ticket_true(self, get_domain_status):
        ticket = {'sourceDomainOrIp': 'dmvsuspension.com', 'number': '123'}
        get_domain_status.return_value = MagicMock(status='ACTIVE')
        result = self._domain_status.validate_ticket(ticket)
        assert_true(result, (True, ''))
