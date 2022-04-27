from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from dcustructuredlogginggrpc import get_logging

from settings import AppConfig

from .validator_interface import ValidatorInterface


class NetcraftValidator(ValidatorInterface):

    app_settings = AppConfig()

    handlers = ['PHISHING', 'MALWARE']
    # Not checking proxy values here as this is for Netcraft's own status updates

    def __init__(self):
        self._logger = get_logging()

    def validate_ticket(self, ticket):
        """
        Returns whether or not a Netcraft-reported ticket should be closed due to them already considering it Resolved
        :param ticket:
        :return tuple: (False, 'resolved') if that is the case, otherwise return (True,):
        """
        reporter = ticket.get('reporter')
        netcraft = self.app_settings.NETCRAFT_ID
        created = ticket.get('created')
        status = ticket.get('phishstory_status')
        info_url = ticket.get('info_url', None)

        if status == 'OPEN' and info_url and reporter == netcraft and created < datetime.now() - timedelta(days=1):
            status_page = requests.get(info_url)  # grabbing Netcraft's status page for ticket

            if status_page.status_code == 200:
                soup = BeautifulSoup(status_page.content, 'html.parser')
                if soup.find(class_="alert-success"):
                    return False, 'resolved'

        return True,
