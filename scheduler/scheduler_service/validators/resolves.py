import logging
import socket

from requests import sessions
from requests.exceptions import ConnectionError

from .validator_interface import ValidatorInterface


class ResolvesValidator(ValidatorInterface):

    handlers = ['PHISHING', 'MALWARE']
    # Need to support empty strings, so we don't break behavior for older tickets.
    ALLOWED_PROXY_VALUES = ['', 'USA']
    CONNECTION_ERRORS = ['[Errno -2] Name or service not known',
                         '[Errno 8] nodename nor servname provided, or not known']

    def __init__(self):
        self._logger = logging.getLogger()

    def _verify_connection(self) -> bool:
        """
        Attempt to get godaddy.com IP and connect to it for verifying internet connection. The connection error given
        for no internet connection, [Errno -2] Name or service not known, is the same for expired and suspended domains.
        """
        try:
            host = socket.gethostbyname('godaddy.com')
            s = socket.create_connection((host, 443), 2)
            s.close()
            return True
        except Exception as e:
            self._logger.error(f'Unable to connect to godaddy.com IP: {e}')
            return False

    def validate_ticket(self, ticket: dict) -> tuple:
        """
        Returns boolean and close reason when boolean is False
        """
        source_url = ticket.get('source')
        self._logger.info(f'Checking if {source_url} resolves')

        try:
            # If proxy is not set to one of the allowed values, mark it as resolved.
            if ticket.get('proxy', '') in self.ALLOWED_PROXY_VALUES:
                with sessions.Session() as session:
                    resp = session.request(method='GET', url=source_url, timeout=10, verify=False, allow_redirects=False)
                    status = str(resp.status_code)
                    resolves = status[0] in ["1", "2", "3"] or status in ["403", "406"]
                if not resolves:
                    return False, 'unresolvable'
        except ConnectionError as e:
            verify = False
            for error_message in self.CONNECTION_ERRORS:
                if error_message in e.args[0].args[0]:
                    verify = True
                    break
            if verify:
                if self._verify_connection():
                    return False, 'unresolvable'
            self._logger.error(f'ConnectionError not in CONNECTION_ERRORS list: {e}')
        except Exception as e:
            self._logger.error(f'Non-ConnectionError exception: {e}')
        return True,
