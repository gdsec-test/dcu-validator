import logging
from requests import sessions
from requests.exceptions import ConnectionError
from validator_interface import ValidatorInterface


class ResolvesValidator(ValidatorInterface):

    handlers = ['PHISHING', 'MALWARE']

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def validate_ticket(self, ticket):
        """
         Returns whether or not a ticket should be closed
        :param ticket:
        :return tuple: False and reason if ticket is not resolvable, return True, 'Resolves' otherwise:
        """
        source_url = ticket.get('source')

        try:
            with sessions.Session() as session:
                resp = session.request(method='GET', url=source_url, timeout=10)
                status = str(resp.status_code)
                resolves = status[0] in ["1", "2", "3"] or status in ["403", "406"]
            if not resolves:
                return (False, 'unresolvable')
        except ConnectionError as e:
            self._logger.error(e)

        return (True,)
