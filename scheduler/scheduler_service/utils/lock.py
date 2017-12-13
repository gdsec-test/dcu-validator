import os
from singleton import Singleton
from redlock import RedLockFactory

class Lock:
    __metaclass__ = Singleton

    def __init__(self):
        redis = os.getenv('REDIS') or 'redis'
        pool = [{"host": x} for x in redis.split(':')]
        self.lock = RedLockFactory(connection_details=pool)