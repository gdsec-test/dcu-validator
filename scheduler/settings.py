import os
from urllib.parse import quote


class AppConfig(object):

    def __init__(self):
        self.BROKER_PASS = os.getenv('BROKER_PASS')
        self.BROKER_URL = os.getenv('BROKER_URL',
                                    f'amqp://02d1081iywc7Av2:{self.BROKER_PASS}@rmq-dcu.int.dev-godaddy.com:5672/grandma')


class ProductionAppConfig(AppConfig):
    VALIDATORQUEUE = 'validator'

    def __init__(self):
        super(ProductionAppConfig, self).__init__()


class OTEAppConfig(AppConfig):
    VALIDATORQUEUE = 'otevalidator'

    def __init__(self):
        super(OTEAppConfig, self).__init__()


class DevelopmentAppConfig(AppConfig):
    VALIDATORQUEUE = 'devvalidator'

    def __init__(self):
        super(DevelopmentAppConfig, self).__init__()


class TestAppConfig(AppConfig):
    VALIDATORQUEUE = 'testvalidator'


def get_env() -> str:
    return os.getenv('sysenv', 'dev')


def get_config(config_name: str = None) -> AppConfig:
    if not config_name:
        config_name = os.getenv('sysenv', 'dev')
    config_by_name = {'dev': DevelopmentAppConfig, 'prod': ProductionAppConfig, 'ote': OTEAppConfig,
                      'test': TestAppConfig}
    return config_by_name[config_name]()
