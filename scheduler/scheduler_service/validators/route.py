from .dedicated_ip import DedicatedIpValidator  # noqa: F401
from .domain_status import DomainStatusValidator  # noqa: F401
from .netcraft_check import NetcraftValidator  # noqa: F401
from .not_parked import ParkedValidator  # noqa: F401
from .resolves import ResolvesValidator  # noqa: F401
from .validator_interface import ValidatorInterface

"""Any class that defines handlers must be imported, these imports will appear unused
but are necessary in order to provide classes that define handlers"""

from dcustructuredlogginggrpc import get_logging

logger = get_logging()


# Route tickets based on type
def route(ticket):
    logger.debug('Validating:{}'.format(ticket.get('type')))
    handlers = ValidatorInterface.registry.get(ticket.get('type'))
    for clazz in handlers:
        ret = clazz().validate_ticket(ticket)
        if not ret[0]:
            return ret

    return (True,)
