from validator_interface import ValidatorInterface
from resolves import ResolvesValidator
from parked import Parked


# Route tickets based on type
def route(ticket):
    print 'Validating:{}'.format(ticket.get('type'))
    handlers = ValidatorInterface.registry.get(ticket.get('type'))
    for clazz in handlers:
        ret = clazz().validate_ticket(
            ticket)  # construct class and run interface function
        if not ret[0]:
            return ret

    return (True,)