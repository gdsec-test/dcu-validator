import os

from requests import Session
from requests_ntlm import HttpNtlmAuth
from zeep import Client
from zeep.transports import Transport


# This class calls into the IPAM SOAP Service to retrieve and modify IP data.
class Ipam:
    # Local Suds SOAP client.
    client = None

    # dev, test, or prod.
    environment = os.getenv('sysenv') or 'dev'

    # SMDB credentials.
    smdbUsername = None
    smdbPassword = None

    # Environment specific SMDB IPAM SOAP API URL's.
    smdbUrls = {
        'dev': 'https://smdb.int.dev-godaddy.com/IPService/ipam.asmx?WSDL',
        'test': 'https://smdb.test.intranet.gdg/ipservice/ipam.asmx?WSDL',
        'ote': 'https://smdb.int.godaddy.com/IPService/ipam.asmx?WSDL',
        'prod': 'https://smdb.int.godaddy.com/IPService/ipam.asmx?WSDL'
    }

    # This method is called automatically when this class is instantiated.
    def __init__(self):

        # Load the SMDB credentials from Nimitz.
        self.__load_credentials()

        session = Session()
        session.auth = HttpNtlmAuth(self.smdbUsername, self.smdbPassword)

        self.client = Client(self.smdbUrls[self.environment], transport=Transport(session=session))

    # Get a list of IP addresses from an object. This is specific to the IPAM IP SOAP response.
    def __get_ips(self, obj):
        # Default to empty list.
        ips = []

        # Make sure the object is a list, and contains a 'IPAddress' key.
        if obj and hasattr(obj, '__iter__') and 'IPAddress' in obj:
            # If the object is a list already, just return it.
            if isinstance(obj['IPAddress'], list):
                ips = obj['IPAddress']
            # If the object is a dictionary, cast as a list.
            elif isinstance(obj['IPAddress'], dict):
                ips.append(obj['IPAddress'])

        return ips

    # Load the SMDB credentials from Nimitz.
    def __load_credentials(self):
        self.smdbUsername = os.getenv('SMDB_USERNAME')
        self.smdbPassword = os.getenv('SMDB_PASSWORD')

    # Make sure all method parameters were supplied. The only exception is 'vlan', which is optional.
    def __validate_params(self, params):
        for key, val in params.items():
            if val is None and key != 'vlan':
                raise Exception('Missing parameter %s' % key)

    # Get details for a specific IP address. Returns a dictionary.
    def get_properties_for_ip(self, ip):
        self.__validate_params(locals())
        return self.client.service.GetPropertiesForIP(ip)
