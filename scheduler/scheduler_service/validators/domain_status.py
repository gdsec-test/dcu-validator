import json
import logging
import os

import requests

from validator_interface import ValidatorInterface


class DomainStatusValidator(ValidatorInterface):
    """Determines if a domain name is workable based on its status. The only time a ticket should validate as False
    is if the domain name is registered with us and has a domain status of something other than 'ACTIVE'
    """

    workable_states = ['ACTIVE', 'NO_DOMAIN_STATUS']
    handlers = ['PHISHING', 'MALWARE']

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        endpoint = os.getenv('DOMAIN_SERVICE') or 'domainservice:8080'
        domain_uri = 'http://{}/v1/domains'.format(endpoint)
        self._query_domain_endpoint = '{}/domaininfo'.format(domain_uri)

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
            self._logger.info('{} - domain status is NOT ACTIVE'.format(domain_name))
        else:
            self._logger.info('{} - domain status is ACTIVE, FOREIGN, or Failed lookup'.format(domain_name))

        return workable, reason

    def _get_domain_status(self, domain_name):
        """
        Get a status for a domain name
        :param domain_name:
        :return: string representing the status of a domain name
        """
        status = 'NO_DOMAIN_STATUS'
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
                if status_code not in [200, 404]:
                    self._logger.error('Domain lookup failed for {} with status code {} : {}'.format(domain_name,
                                                                                                     status_code,
                                                                                                     resp.text))
                elif status_code == 404:
                    self._logger.critical('URL not found : {}'.format(resp.text))
                elif status_code == 200:
                    # Valid response looks like:
                    #  {"domain":"XXX",
                    #   "shopperId":"XXX",
                    #   "domainId":###,
                    #   "createDate":"XXX",
                    #   "status":"XXX"}
                    resp_dict = json.loads(resp.text)
                    if not resp_dict.get('domainId', False):
                        self._logger.error('No domain id returned from domainservice query on {}'.format(domain_name))
                    elif not resp_dict.get('status', False):
                        self._logger.error('No status returned from domainservice query on {}'.format(domain_name))
                    else:
                        status = resp_dict.get('status')
                        self._logger.info("resp {}".format(resp.text))
            except Exception as e:
                self._logger.error('Exception: {}'.format(e))
        return status
