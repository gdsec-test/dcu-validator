import pymongo
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
from pytz import utc


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(
                *args, **kwargs)
        return cls._instances[cls]


class Scheduler:
    __metaclass__ = Singleton

    def __init__(self):
        job_defaults = {'coalesce': True, 'max_instances': 3}
        executers = {'default': ProcessPoolExecutor(5)}
        self.scheduler = BackgroundScheduler(
            job_defaults=job_defaults, executers=executers, timezone=utc)
        self.scheduler.add_jobstore('mongodb', client=self._get_client())

    def _get_client(self):
        db_user = os.getenv('DB_USER') or ''
        db_pass = os.getenv('DB_PASS') or ''
        db_host = os.getenv('DB_HOST') or 'localhost'
        db = os.getenv('DB') or 'apscheduler'
        if db_user and db_pass:
            db_url = 'mongodb://{}:{}@{}/{}'.format(db_user, db_pass,
                                                    db_host, db)
        else:
            db_url = 'mongodb://{}/{}'.format(db_host, db)
        return pymongo.MongoClient(db_url, connect=False)
