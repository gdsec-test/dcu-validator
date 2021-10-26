from flask import Flask
from flask_restplus import Api

from .api import api as ns1
from .closure import api as ns2


def create_app():
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
    api.add_namespace(ns2)
    return app
