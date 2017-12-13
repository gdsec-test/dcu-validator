import logging
import re
from dns import resolver
from netaddr.ip import all_matching_cidrs


class Parked(object):

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

    def is_not_parked(self, domain_name, content, url):
        """
        Checks domain's IP Address against parkweb servers and falls back to check the page
        content and url against known park/landing page regexes
        :param domain_name:
        :param content:
        :param url:
        :return:
        """
        if not self._is_ip(domain_name):
            dnsresolver = resolver.Resolver()
            dnsresolver.timeout = 1
            dnsresolver.lifetime = 1
            ip = dnsresolver.query(domain_name, 'A')[0].address
            self._logger.info('Domain {} has IP: {}', domain_name, ip)
        else:
            ip = domain_name
        if all_matching_cidrs(ip, self.parkweb):
            self._logger.info('Matched {} for parked IP', domain_name)
            return False
        else:
            parked = filter(None, [x.search(content) for x in self.parked_regex])
            suspended = [x.search(url) for x in self.suspended_regex]

            if any(suspended) or len(parked) >= 2:
                self._logger.info('{} has been found parked/suspended', domain_name)
                return False

    def _is_ip(self, source_domain_or_ip):
        """
        Returns whether the given sourceDomainOrIp is an ip address
        :param source_domain_or_ip:
        :return:
        """
        pattern = re.compile(r"((([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])[ (\[]?(\.|dot)[ )\]]?){3}[0-9]{1,3})")
        return pattern.match(source_domain_or_ip) is not None
