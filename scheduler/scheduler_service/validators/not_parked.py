import logging
from ipaddress import ip_address

from dns import resolver

from .validator_interface import ValidatorInterface


class ParkedValidator(ValidatorInterface):

    handlers = ['PHISHING', 'MALWARE']
    # IPAddress associated with GoDaddy parking systems
    parked_ips = ['34.102.136.180', '34.98.99.30']

    def __init__(self):
        self._logger = logging.getLogger()

    def validate_ticket(self, ticket: dict) -> tuple:
        """
        Check if the IP address for a domain is one of the parked addresses.
        returns either:
            (True, )
            (False, 'parked')
        """

        domain = ticket.get('sourceDomainOrIp')
        ip = domain

        if not ParkedValidator._is_ip(domain):
            try:
                dnsresolver = resolver.Resolver()
                dnsresolver.timeout = 1
                dnsresolver.lifetime = 1
                ip = dnsresolver.resolve(domain, 'A', search=True)[0].address
            except Exception:
                # Don't do anything. Fail out if we can't perform DNS lookups.
                pass

        if ip in self.parked_ips:
            self._logger.info(f'Matched {domain} for parked IP')
            return False, 'parked'

        return True, None

    @staticmethod
    def _is_ip(potential_ip: str) -> bool:
        try:
            ip_address(potential_ip)
            return True
        except Exception:
            return False
