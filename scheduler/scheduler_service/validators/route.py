from .dedicated_ip import DedicatedIpValidator  # noqa: F401
from .domain_status import DomainStatusValidator  # noqa: F401
from .resolves import ResolvesValidator  # noqa: F401
from .validator_interface import ValidatorInterface

"""Any class that defines handlers must be imported, these imports will appear unused
but are necessary in order to provide classes that define handlers"""

import logging

logger = logging.getLogger()


# Route tickets based on type
def route(ticket):
    logger.info('{} in route'.format(ticket.get('type')))
    logger.debug('Validating:{}'.format(ticket.get('type')))
    handlers = ValidatorInterface.registry.get(ticket.get('type'))
    if handlers:
        logger.info('{} in route, if handlers'.format(ticket.get('type')))
        for clazz in handlers:
            ret = clazz().validate_ticket(ticket)
            if not ret[0]:
                logger.info('{} in route, return something else'.format(ticket.get('type')))
                return (*ret, str(clazz).lower().split('.')[3].replace("'>", "") + '_automation')

    logger.info('{} in route, return True'.format(ticket.get('type')))
    return (True,)
