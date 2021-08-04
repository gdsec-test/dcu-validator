import json
import os

import requests
from dcustructuredlogginggrpc import get_logging

from .validator_interface import ValidatorInterface


class DomainStatusValidator(ValidatorInterface):
    """Determines if a domain name is workable based on its status. The only time a ticket should validate as False
    is if the domain name is registered with us and has a domain status of something other than 'ACTIVE'
    """
    KEY_STATUS = 'status'
    NO_DOMAIN_STATUS = 'NO_DOMAIN_STATUS'
    STATUS_200 = 200
    STATUS_404 = 404

    handlers = ['PHISHING', 'MALWARE']

    workable_states = ['ACTIVE', 'AWAITING_VERIFICATION_ICANN', 'AWAITING_VERIFICATION_ICANN_MANUAL', 'HELD_DISPUTED',
                       'HELD_EXPIRED_REDEMPTION_MOCK', 'HELD_SHOPPER', NO_DOMAIN_STATUS, 'PENDING_HOLD_REDEMPTION',
                       'PENDING_UPDATE_OWNERSHIP', 'PENDING_TRANSFER_OUT']

    def __init__(self):
        self._logger = get_logging()
        endpoint = os.getenv('DOMAIN_SERVICE') or 'domainservice:8080'
        domain_uri = f'http://{endpoint}/v1/domains'
        self._query_domain_endpoint = f'{domain_uri}/domaininfo'

    def validate_ticket(self, ticket):
        """
        Checks to see if a domain name/ticket should be worked based on its domain status
        If there is no domain status or the lookup fails, the ticket should be further processed and not closed
        :param ticket:
        :return: a tuple (bool, str)
        """
        domain_name = ticket.get('sourceDomainOrIp')
        workable = True
        reason = None

        if self._get_domain_status(domain_name) not in self.workable_states:
            workable = False
            reason = 'unworkable'
            self._logger.info(f'{domain_name} - domain status is NOT ACTIVE')
        else:
            self._logger.info(f'{domain_name} - domain status is a workable status, FOREIGN, or Failed lookup')

        return workable, reason

    def _get_domain_status(self, domain_name):
        """
        Get a status for a domain name
        :param domain_name:
        :return: string representing the status of a domain name
        """
        status = self.NO_DOMAIN_STATUS
        if domain_name:
            try:
                # Query the domain to get status
                with requests.Session() as session:
                    resp = session.post(self._query_domain_endpoint, data=json.dumps({"domain": domain_name}))

                status_code = int(resp.status_code)

                # So far, I've received the following status_code responses:
                #  200: u'{"shopperId":"1274145"}'
                #  400: u'{"error":"invalid character \'d\' looking for beginning of value","code":3}'
                #  404: u'Not Found\n'
                #  500: u'{"error":"No Active shoppers for this Domain Name","code":13}'
                if status_code not in [self.STATUS_200, self.STATUS_404]:
                    self._logger.error(
                        f'Domain lookup failed for {domain_name} with status code {status_code} : {resp.text}')
                elif status_code == self.STATUS_404:
                    self._logger.critical(f'URL not found : {resp.text}')
                elif status_code == self.STATUS_200:
                    # Valid response looks like:
                    #  {"domain":"XXX",
                    #   "shopperId":"XXX",
                    #   "domainId":###,
                    #   "createDate":"XXX",
                    #   "status":"XXX"}
                    resp_dict = json.loads(resp.text)
                    if not resp_dict.get('domainId', False):
                        self._logger.error(f'No domain id returned from domainservice query on {domain_name}')
                    elif not resp_dict.get(self.KEY_STATUS, False):
                        self._logger.error(f'No status returned from domainservice query on {domain_name}')
                    else:
                        status = resp_dict.get(self.KEY_STATUS)
                        self._logger.info(f'resp {resp.text}')
            except Exception as e:
                self._logger.error(f'Exception: {e}')
        return status
