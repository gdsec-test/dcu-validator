from flask import Flask
from flask_restplus import Api
from flask_restplus import Api, Resource, fields
from . validator import api as ns1
from . scheduler import Scheduler

def create_app(env):
    app = Flask(__name__)
    api = Api(
        app,
        version='1.0',
        title='DCU Validator API',
        description='Periodically validates existing DCU tickets',
        validate=True,
        doc='/doc',
    )
    api.add_namespace(ns1)
    if env != 'test':
        scheduler = Scheduler().scheduler
        scheduler.start()
        app.config['scheduler'] = scheduler
    return app
