import logging
import logging.config
import os

import yaml

from rest_service.api import create_app

env = os.getenv('sysenv') or 'dev'
app = create_app(env)

if __name__ == '__main__':
    path = os.path.dirname(os.path.abspath(__file__)) + '/' + 'logging.yaml'
    value = os.getenv('LOG_CFG', None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            lconfig = yaml.safe_load(f.read())
        logging.config.dictConfig(lconfig)
    else:
        logging.basicConfig(level=logging.INFO)
    logging.raiseExceptions = True
    app.run()
