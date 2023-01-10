import os

import pymongo
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

from scheduler_service.utils.db_settings import create_db_settings
from scheduler_service.utils.singleton import Singleton


class APS(metaclass=Singleton):
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
        client = pymongo.MongoClient(settings.DBURL, connect=False, tls=True, tlsCertificateKeyFile=os.getenv("MONGO_CLIENT_CERT"))
        return MongoDBJobStore(database=settings.DB,
                               collection=os.getenv('JOBS_COLLECTION', 'jobs'),
                               client=client)
