import logging


class IsWorkable(object):
    """Determines if a domain name is workable, based on its status"""

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def domain_status(self, domain):
        """
        Get a status for a domain name
        :param domain: 
        :return: 
        """""
        pass

    def is_domain_status_workable(self):
        """
        Returns a tuple (True, '') or (False, 'Close Reason') based on whether the status of a domain name is a status
        we should continue to work or if the domain name is in a status that we should not work
        :return:
        """
        pass
