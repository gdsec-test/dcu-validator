from nose.tools import assert_true, assert_false
from scheduler_service.validators.workable_domain_status import IsWorkable
from mock import patch

import requests


class TestDomainStatus:

    def __init__(self):
        self._is_workable = IsWorkable('domain_service_endpoint')

    @patch.object(IsWorkable, 'get_domain_status')
    def test_get_domain_status_active(self, get_domain_status):
        domain = 'dmvsuspension.com'
        get_domain_status.return_value = {"domain": "dmvsuspension.com",
                                            "shopperId": "12345",
                                            "domainId": 85789,
                                            "createDate": "10-05-2006",
                                            "status": "ACTIVE"}

        result = self._is_workable.get_domain_status(domain)
        assert_true(result, 'ACTIVE')

    def test_get_domain_status_not_active(self):
        domain = 'dmvsuspension.com'
        pass

    def test_unable_to_get_domain_status(self):
        domain = 'dmvsuspension.com'
        pass
