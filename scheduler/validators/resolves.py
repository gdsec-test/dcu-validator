import logging
from requests import sessions
from requests.exceptions import ConnectionError


class Resolvable(object):

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def resolves(self, source_url, proxy=False):
        """
        Returns whether or not a ticket should be closed
        :param source_url:
        :param proxy:
        :return False if ticket is not resolvable, return True otherwise:
        """
        try:
            with sessions.Session() as session:
                resp = session.request(method='GET', url=source_url, timeout=60)
                status = str(resp.status_code)
                resolves = status[0] in ["1", "2", "3"] or status in ["403", "406"]
            if not resolves:
                return False
        except ConnectionError as e:
            self._logger.error(e)
            return False

        return True
