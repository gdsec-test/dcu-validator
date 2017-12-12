import os
import pymongo
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.jobstores.mongodb import MongoDBJobStore
from scheduler_service.utils.singleton import Singleton
from scheduler_service.utils.db_settings import create_db_settings
from pytz import utc


class APS:
    __metaclass__ = Singleton

    def __init__(self):
        job_defaults = {'coalesce': True, 'max_instances': 3}
        executers = {'default': ProcessPoolExecutor(5)}
        jobstores = {
            'default': self._get_jobstore(),
        }
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            job_defaults=job_defaults,
            executers=executers,
            timezone=utc)

    def _get_jobstore(self):
        settings = create_db_settings()
        client = pymongo.MongoClient(settings.DBURL, connect=False)
        return MongoDBJobStore(database=settings.DB, collection='jobs', client=client)
