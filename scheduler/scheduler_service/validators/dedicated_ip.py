import logging
from validator_interface import ValidatorInterface
from scheduler.scheduler_service.utils.enrichment import nutrition_label
from scheduler.scheduler_service.utils.ipam import Ipam


class DedicatedIpValidator(ValidatorInterface):

    handlers = ['NETABUSE']

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def validate_ticket(self, ticket):
        """
        Check IP to determine if Dedicated or shared hosting product
        Returns either (True, ) or (False, 'shared ip')
        :param ticket:
        :return:
        """

        ipam = Ipam()
        data = ipam.get_properties_for_ip(ticket.get('sourceDomainOrIp'))

        if data.HostName:

            if nutrition_label(data.HostName)[2] == 'Open':
                return True,

            return False, 'shared ip'
