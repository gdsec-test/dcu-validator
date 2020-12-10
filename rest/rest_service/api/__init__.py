from flask import Flask
from flask_restplus import Api

from .api import api as ns1


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
    return app
