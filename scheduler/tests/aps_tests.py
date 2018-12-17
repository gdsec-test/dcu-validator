from apscheduler.schedulers.background import BackgroundScheduler

from scheduler_service.schedulers.aps import APS


class TestAPS:

    def test_aps(self):
        aps = APS()
        assert(type(aps.scheduler) is BackgroundScheduler)
