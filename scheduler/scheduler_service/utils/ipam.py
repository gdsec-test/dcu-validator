import os
from urllib.error import URLError

from suds import WebFault
from suds.client import Client
from suds.transport.https import WindowsHttpAuthenticated


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

        # Create the NTLM authentication object.
        self.ntlm = WindowsHttpAuthenticated(
            username=self.smdbUsername, password=self.smdbPassword)

        # Create the SUDS SOAP client.
        self.client = Client(
            self.smdbUrls[self.environment], transport=self.ntlm)

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

    # Perform a SOAP call, and parse the results.
    def __soap_call(self, method, params, responseKey):
        # We need the params to be a tuple for Suds. So if it's a single element, cast as a tuple.
        if not isinstance(params, tuple):
            params = (params,)

        # Try and make the SOAP call, and return the results. Or throw an exception on any SOAP faults.
        try:
            # Dynamically make SOAP call.
            soapResult = getattr(self.client.service, method)(*params)

            # Manually parse the SOAP XML response.
            return soapResult
        except (WebFault, URLError) as e:
            try:
                raise Exception("IPAM SOAP Fault: %s" % e.fault.faultstring)
            except AttributeError as e2:
                raise Exception("IPAM SOAP Attribute Fault: %s" % str(e2))

    # Make sure all method parameters were supplied. The only exception is 'vlan', which is optional.
    def __validate_params(self, params):
        for key, val in params.items():
            if val is None and key != 'vlan':
                raise Exception('Missing parameter %s' % key)

    # Get the environment we're running under.
    def get_environment(self):
        return self.environment

    # SOAP METHODS

    # Get IP's assigned to a specific hostname. Returns a list.
    def get_ips_by_hostname(self, hostname):
        self.__validate_params(locals())
        return self.__get_ips(
            self.__soap_call('GetIPsByHostname', hostname,
                             'GetIPsByHostnameResult'))

    # Get details for a specific IP address. Returns a dictionary.
    def get_properties_for_ip(self, ip):
        self.__validate_params(locals())
        return self.client.service.GetPropertiesForIP(ip, transport=self.ntlm)
        # return self.__soap_call('GetPropertiesForIP', ip, 'GetPropertiesForIPResult')

    # Get details for multiple IP addresses. Returns a list.

    def get_properties_for_ip_list(self, ips):
        self.__validate_params(locals())
        return self.__get_ips(
            self.__soap_call('GetPropertiesForIPList', ips,
                             'GetPropertiesForIPListResult'))
