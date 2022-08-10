import logging
import os
from functools import partial
from json import loads

import requests


class APIHelper:
    """
    This class handles access to the DCU API
    """

    def __init__(self):
        self._logger = logging.getLogger()
        self._url = os.getenv('API_UPDATE_URL') or 'http://localhost/v1/abuse/tickets'
        self._sso_endpoint = os.getenv('SSO_URL') or 'https://sso.dev-gdcorp.tools'
        self._user = os.getenv('SSO_USER')
        self._password = os.getenv('SSO_PASSWORD')
        self._header = {'Authorization': self._get_jwt()}

    def close_incident(self, ticket_id: str, reason: str) -> bool:
        """
        Closes out the given ticket
        """

        payload = {"closed": "true", "close_reason": reason}
        data = False
        try:
            api_call = partial(
                requests.patch,
                f'{self._url}/{ticket_id}',
                json=payload,
                headers=self._header
            )
            r = api_call()
            if r.status_code in [401, 403]:
                self._header['Authorization'] = self._get_jwt()
                r = api_call()

            if r.status_code == 204:
                data = True
            else:
                self._logger.warning(r.status_code)
                self._logger.warning(f'Unable to update ticket {ticket_id} {r.content}')
        except Exception as e:
            self._logger.error(f'Exception while updating ticket {ticket_id} {e}')
        return data

    def _get_jwt(self) -> str:
        """
        Pull down JWT via username/password.
        """
        try:
            response = requests.post(
                f'{self._sso_endpoint}/v1/api/token',
                json={'username': self._user, 'password': self._password},
                params={'realm': 'idp'}
            )
            response.raise_for_status()
            body = loads(response.text)
            return body.get('data')
        except Exception as e:
            self._logger.error(e)
        return None
