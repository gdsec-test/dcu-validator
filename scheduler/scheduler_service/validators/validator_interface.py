from collections import defaultdict


# ValidatorInterface Meta class
class ValidatorInterfaceMeta(type):
    # we use __init__ rather than __new__ here because we want
    # to modify attributes of the class *after* they have been
    # created
    def __init__(cls, name, bases, dct):
        if not hasattr(cls, 'registry'):
            # this is the base class.  Create an empty registry
            cls.registry = defaultdict(list)
        else:
            # this is a derived class.  Add cls handlers to the registry
            if hasattr(cls, 'handlers'):
                if isinstance(cls.handlers, (list, tuple)):
                    for handler in cls.handlers:
                        if isinstance(handler, basestring):
                            cls.registry[handler].append(cls)
                else:
                    if isinstance(cls.handlers, basestring):
                            cls.registry[cls.handlers].append(cls)

        super(ValidatorInterfaceMeta, cls).__init__(name, bases, dct)


# main Validator  interface
class ValidatorInterface(object):
    __metaclass__ = ValidatorInterfaceMeta
    handlers = None

    def validate_ticket(self, ticket):
        raise(NotImplementedError)


# implementation classes
class ParkedValidator(ValidatorInterface):
    handlers = ['PHISHING', 'MALWARE', 'NETWORK_ABUSE']

    def validate_ticket(self, ticket):
        print "Parked Validator handles {}".format(self.handlers)
        print "Received {}".format(ticket)


class ResolvesValidator(ValidatorInterface):
    handlers = ['PHISHING', 'MALWARE']

    def validate_ticket(self, ticket):
        print "Resolves validator handles {}".format(self.handlers)
        print "Received {}".format(ticket)


# Route tickets based on type
def route(ticket):
    handlers = ValidatorInterface.registry.get(ticket.get('type'))
    for clazz in handlers:
        clazz().validate_ticket(ticket)  # construct class and run interface function


if __name__ == '__main__':
    tickets = [dict(id='123', type='NETWORK_ABUSE'), dict(id='456', type='PHISHING'), dict(id='789', type='MALWARE')]
    for ticket in tickets:
        route(ticket)
