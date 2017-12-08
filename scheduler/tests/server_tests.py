from mock import patch
from scheduler.server.service import Scheduler
from mock import patch, MagicMock
from grpc_stub.schedule_service_pb2 import Request, ValidationResponse
from apscheduler.schedulers.background import BackgroundScheduler


class TestScheduler:

    @patch.object(Scheduler, '_create_scheduler')
    def test_add_schedule(self, scheduler):
        scheduler.return_value = MagicMock()
        service = Scheduler()
        request = Request(ticket='12345', close=False, period=300)
        resp = service.AddSchedule(request, None)

    @patch.object(Scheduler, '_create_scheduler')
    def test_reschedule(self, scheduler):
        scheduler.return_value = MagicMock(get_job=lambda x: False)
        service = Scheduler()
        request = Request(ticket='12345', close=False, period=300)
        resp = service.AddSchedule(request, None)

    @patch.object(Scheduler, '_create_scheduler')
    def test_remove_schedule(self, scheduler):
        scheduler.return_value = MagicMock()
        service = Scheduler()
        request = Request(ticket='12345')
        resp = service.RemoveSchedule(request, None)

    @patch.object(Scheduler, '_create_scheduler')
    def test_validate_ticket(self, scheduler):
        scheduler.return_value = MagicMock()
        service = Scheduler()
        request = Request(ticket='12345')
        resp = service.ValidateTicket(request, None)
        assert(resp.valid is True)

    def test_create_schedduler(self):
        scheduler = Scheduler()
        assert(type(scheduler.scheduler) is BackgroundScheduler)
