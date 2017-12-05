from flask import Flask
from flask_restplus import Api
from flask_restplus import Api, Resource, fields
from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
from . validator import api as ns1


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
        job_defaults = {'coalesce': True, 'max_instances': 3}
        executers = {'default': ProcessPoolExecutor(5)}
        scheduler = BackgroundScheduler(
            job_defaults=job_defaults, executers=executers, timezone=utc)
        scheduler.add_jobstore('mongodb', connect=False)
        scheduler.start()
        app.config['scheduler'] = scheduler
    return app
