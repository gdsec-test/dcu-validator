import logging

from requests import sessions
from requests.exceptions import ConnectionError

from .validator_interface import ValidatorInterface


class ResolvesValidator(ValidatorInterface):

    handlers = ['PHISHING', 'MALWARE']
    # Need to support empty strings so we don't break behavior for older tickets.
    ALLOWED_PROXY_VALUES = ['', 'USA']

    def __init__(self):
        self._logger = logging.getLogger()

    def validate_ticket(self, ticket):
        """
         Returns whether or not a ticket should be closed
        :param ticket:
        :return tuple: (False,'unresolvable') and reason if ticket is not resolvable, return (True,) otherwise:
        """
        source_url = ticket.get('source')
        self._logger.info('{} Checking if {} resolves'.format(__name__, source_url))

        try:
            # If proxy is not set to one of the allowed values, mark it as resolved.
            if ticket.get('proxy', '') in self.ALLOWED_PROXY_VALUES:
                with sessions.Session() as session:
                    resp = session.request(method='GET', url=source_url, timeout=10, verify=False)
                    status = str(resp.status_code)
                    resolves = status[0] in ["1", "2", "3"] or status in ["403", "406"]
                if not resolves:
                    return False, 'unresolvable'
        except ConnectionError as e:
            if '[Errno 8] nodename nor servname provided, or not known' in e.args[0].args[0]:
                return False, 'unresolvable'
            else:
                self._logger.error(e)

        return (True,)
