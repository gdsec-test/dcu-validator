from dns import resolver
from netaddr.ip import all_matching_cidrs
import re


class Parked():

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

    def _is_parked(self, domain_name, content, url):
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
        else:
            ip = domain_name
        if all_matching_cidrs(ip, self.parkweb):
            return True
        else:
            parked = filter(None, [x.search(content) for x in self.parked_regex])
            suspended = [x.search(url) for x in self.suspended_regex]

        return any(suspended) or len(parked) >= 2
