import os


class AppConfig(object):

    def __init__(self):
        self.BROKER_URL = os.getenv('MULTIPLE_BROKERS')

        self.NETCRAFT_ID = os.getenv('NETCRAFT_ID', 'netcraft_id')


class ProductionAppConfig(AppConfig):
    VALIDATORQUEUE = 'validator'

    def __init__(self):
        super(ProductionAppConfig, self).__init__()
        self.NETCRAFT_ID = '132668659'


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

    def __init__(self):
        super(TestAppConfig, self).__init__()
        self.NETCRAFT_ID = '0000'


def get_env() -> str:
    return os.getenv('sysenv', 'dev')


def get_config(config_name: str = None) -> AppConfig:
    if not config_name:
        config_name = os.getenv('sysenv', 'dev')
    config_by_name = {'dev': DevelopmentAppConfig, 'prod': ProductionAppConfig, 'ote': OTEAppConfig,
                      'test': TestAppConfig}
    return config_by_name[config_name]()
