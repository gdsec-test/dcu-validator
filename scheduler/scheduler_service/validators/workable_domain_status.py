import logging
import requests
import json


class IsWorkable(object):
    """Determines if a domain name is workable, based on its status"""

    WORKABLE_STATES = ['ACTIVE']

    def __init__(self, endpoint):
        self._logger = logging.getLogger(__name__)
        domain_uri = 'http://{}/v1/domains'.format(endpoint)
        self._query_domain_endpoint = '{}/domaininfo'.format(domain_uri)

    def domain_status(self, domain_name):
        """
        Get a status for a domain name
        :param domain_name: 
        :return status: string representing domain name status
        """""
        status = 'Unable to query domain status'
        try:
            # Query the domain to get status
            with requests.Session() as session:
                resp = session.post(self._query_domain_endpoint, data=json.dumps({"domain": domain_name}))
            resp_dict = json.loads(resp.text)

            status_code = int(resp.status_code)

            # So far, I've received the following status_code responses:
            #  200: u'{"shopperId":"1274145"}'
            #  400: u'{"error":"invalid character \'d\' looking for beginning of value","code":3}'
            #  404: u'Not Found\n'
            #  500: u'{"error":"No Active shoppers for this Domain Name","code":13}'
            if status_code not in [200, 404]:
                self._logger.error('Domain lookup failed for {} with status code {} : {}'.format(domain_name,
                                                                                                 status_code,
                                                                                                 resp.text))
            elif status_code == 404:
                self._logger.critical('URL not found : {}'.format(resp.text))
            elif status_code == 200:
                # Valid response looks like:
                #  {"domain":"XXX",
                #   "shopperId":"XXX",
                #   "domainId":###,
                #   "createDate":"XXX",
                #   "status":"XXX"}
                if not resp_dict.get('domainId', False):
                    self._logger.error('No domain id returned from domainservice query on {}'.format(domain_name))
                elif not resp_dict.get('status', False):
                    self._logger.error('No status returned from domainservice query on {}'.format(domain_name))
                else:
                    status = resp_dict.get('status')
                    self._logger.info("resp {}".format(resp.text))
        except Exception as e:
            self._logger.error('Exception: {}'.format(e))
        return status

    def workable_domain_status(self, domain_name):
        """
        Returns a tuple (True, '') or (False, 'Close Reason') based on whether the status of a domain name is a status
        we should continue to work or if the domain name is in a status that we should not work
        :param domain_name:
        :return:
        """
        workable = False
        reason = ''

        try:
            if self.domain_status(domain_name) not in self.WORKABLE_STATES:
                reason = 'Unworkable domain status'
                self._logger.info('{} - domain status is unworkable').format(domain_name)
            else:
                workable = True
                self._logger.info('{} - domain status is workable').format(domain_name)
        except Exception as e:
            self._logger.error('Exception: {}'.format(e))
        return workable, reason
