from validator import create_app
import os
import logging
import logging.config
import os
import yaml

if __name__ == '__main__':
    env = os.getenv('sysenv') or 'dev'
    path = os.path.dirname(os.path.abspath(__file__)) + '/' + 'logging.yml'
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
    app = create_app(env)
    app.run()
