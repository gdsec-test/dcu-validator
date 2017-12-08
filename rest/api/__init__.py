from flask import Flask
from flask_restplus import Api, Resource, fields
from .api import api as ns1
import os


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
    return app
