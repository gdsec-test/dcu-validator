from dedicated_ip import DedicatedIpValidator
from domain_status import DomainStatusValidator
from not_parked import ParkedValidator
from resolves import ResolvesValidator
from validator_interface import ValidatorInterface


"""Any class that defines handlers must be imported, these imports will appear unused
but are necessary in order to provide classes that define handlers"""


# Route tickets based on type
def route(ticket):
    print 'Validating:{}'.format(ticket.get('type'))
    handlers = ValidatorInterface.registry.get(ticket.get('type'))
    for clazz in handlers:
        ret = clazz().validate_ticket(ticket)  # construct class and run interface function
        if not ret[0]:
            return ret

    return (True,)
