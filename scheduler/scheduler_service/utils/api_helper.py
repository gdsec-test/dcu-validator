import logging
import os

import requests


class APIHelper:
    """
    This class handles access to the DCU API
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._url = os.getenv('API_UPDATE_URL') or '"http://localhost/v1/abuse/tickets'
        self._token = os.getenv('API_TOKEN') or 'token'
        self._header = {'Authorization': self._token}

    def close_incident(self, ticket_id, reason):
        """
        Closes out the given ticket
        :param ticket_id: string
        :param reason: string representing close reason
        :return boolean True on success, False otherwise:
        """

        payload = {"closed": "true", "close_reason": reason}
        data = False
        try:
            r = requests.patch(
                '{}/{}'.format(self._url, ticket_id),
                json=payload,
                headers=self._header)
            if r.status_code == 204:
                data = True
            else:
                self._logger.warning("Unable to update ticket {} {}".format(
                    ticket_id, r.content))
        except Exception as e:
            self._logger.error("Exception while updating ticket {} {}".format(
                ticket_id, e.message))
        return data
