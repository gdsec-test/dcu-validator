import logging

from scheduler_service.utils.enrichment import nutrition_label
from scheduler_service.utils.ipam import Ipam

from .validator_interface import ValidatorInterface


class DedicatedIpValidator(ValidatorInterface):

    handlers = ['NETWORK_ABUSE']

    def __init__(self):
        self._logger = logging.getLogger()

    def validate_ticket(self, ticket):
        """
        Check IP to determine if Dedicated or shared hosting product
        Returns either (True, ) or (False, 'shared ip')
        :param ticket:
        :return:
        """
        ip = None
        try:
            ipam = Ipam()
            ip = ticket.get('sourceDomainOrIp')
            data = ipam.get_properties_for_ip(ip)
            if data.HostName and nutrition_label(data.HostName)[2] != 'Open':
                return False, 'shared_ip'
        except Exception as e:
            self._logger.error("Unable to determine if {} is dedicated ip:{}".format(ip, e))
        return True,
