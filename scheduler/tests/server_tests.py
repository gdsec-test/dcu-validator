from scheduler.server.service import Service
from mock import MagicMock
from grpc_stub.schedule_service_pb2 import Request


class TestScheduler:

    def test_add_schedule(self):
        service = Service(MagicMock())
        request = Request(ticket='12345', close=False, period=300)
        resp = service.AddSchedule(request, None)

    def test_reschedule(self):
        service = Service(MagicMock())
        request = Request(ticket='12345', close=False, period=300)
        resp = service.AddSchedule(request, None)

    def test_remove_schedule(self):
        service = Service(MagicMock())
        request = Request(ticket='12345')
        resp = service.RemoveSchedule(request, None)

    def test_validate_ticket(self):
        service = Service(MagicMock())
        request = Request(ticket='12345')
        resp = service.ValidateTicket(request, None)
        assert(resp.valid is True)
