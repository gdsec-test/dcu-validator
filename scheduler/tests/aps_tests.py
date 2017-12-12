from scheduler_service.schedulers.aps import APS
from apscheduler.schedulers.background import BackgroundScheduler


class TestAPS:

    def test_aps(self):
        aps = APS()
        assert(type(aps.scheduler) is BackgroundScheduler)
