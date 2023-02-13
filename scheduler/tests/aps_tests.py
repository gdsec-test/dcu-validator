from unittest import TestCase

from apscheduler.schedulers.background import BackgroundScheduler

from scheduler_service.schedulers.aps import APS


class TestAPS(TestCase):
    def test_aps(self):
        aps = APS()
        self.assertTrue(type(aps.scheduler) is BackgroundScheduler)
