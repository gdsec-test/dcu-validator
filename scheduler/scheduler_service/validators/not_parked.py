import logging
import re

from dns import resolver
from netaddr.ip import all_matching_cidrs
from requests import sessions

from validator_interface import ValidatorInterface


class ParkedValidator(ValidatorInterface):

    handlers = ['PHISHING', 'MALWARE']

    # URL redirects to error/suspension page
    suspended_regex = [
        re.compile(r'cgi-sys/suspendedpage.cgi$'),
        re.compile(r'^https?://error\.hostinger*')
    ]

    # IPAddress associated with parkweb servers
    parkweb = ['50.63.202.32/27', '184.168.221.32/27', '50.63.202.64/27', '184.168.221.64/27']

    # Page content is a landing page/park page
    parked_regex = [
        re.compile(r'GD_Sharehead.jpg'),
        re.compile(r'\.wsimg\.com'),
        re.compile(r'This Web page is parked for FREE'),
        re.compile(r'http://www.godaddy.com/domains/search'),
        re.compile(r'Site Unavailable'),
        re.compile(r'This site is currently unavailable.'),
        re.compile(r'Coming Soon'),
        re.compile(r'Future home of something quite cool.')
    ]

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def validate_ticket(self, ticket):
        """
        Checks domain's IP Address against parkweb servers and falls back to check the page
        content and url against known park/landing page regexes
        returns either (True, ) or (False, 'not parked')
        :param ticket:
        :return:
        """

        domain_name = ticket.get('sourceDomainOrIp')
        url = ticket.get('source')
        content = self._get_content(url)

        if not self._is_ip(domain_name):
            dnsresolver = resolver.Resolver()
            dnsresolver.timeout = 1
            dnsresolver.lifetime = 1
            ip = dnsresolver.query(domain_name, 'A')[0].address
            self._logger.info('Domain {} has IP: {}'.format(domain_name, ip))
        else:
            ip = domain_name
        if all_matching_cidrs(ip, self.parkweb):
            self._logger.info('Matched {} for parked IP'.format(domain_name))
            return False, 'parked'
        else:
            parked = filter(None, [x.search(content) for x in self.parked_regex])
            suspended = [x.search(url) for x in self.suspended_regex]

            if any(suspended) or len(parked) >= 2:
                return False, 'parked'
            return True,

    def _is_ip(self, source_domain_or_ip):
        """
        Returns whether the given sourceDomainOrIp is an ip address
        :param source_domain_or_ip:
        :return:
        """
        pattern = re.compile(r"((([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])[ (\[]?(\.|dot)[ )\]]?){3}[0-9]{1,3})")
        return pattern.match(source_domain_or_ip) is not None

    def _get_content(self, url):
        with sessions.Session() as session:
            return session.get(url=url, timeout=60).text