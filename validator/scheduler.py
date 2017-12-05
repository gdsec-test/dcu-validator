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
        self.scheduler.add_jobstore('mongodb', connect=False)
