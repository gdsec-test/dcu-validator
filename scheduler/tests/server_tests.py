from mock import MagicMock, patch

from scheduler_service.grpc_stub.schedule_service_pb2 import Request
from scheduler_service.server.service import Service


class TestScheduler:

    def test_add_schedule(self):
        service = Service(MagicMock())
        request = Request(ticket='12345', close=False, period=300)
        resp = service.AddSchedule(request, None)  # noqa: F841

    def test_reschedule(self):
        service = Service(MagicMock())
        request = Request(ticket='12345', close=False, period=300)
        resp = service.AddSchedule(request, None)  # noqa: F841

    def test_remove_schedule(self):
        service = Service(MagicMock())
        request = Request(ticket='12345')
        resp = service.RemoveSchedule(request, None)  # noqa: F841

    @patch('scheduler_service.server.service.validate')
    def test_validate_ticket(self, validate):
        validate.return_value = (0, 'blah')
        service = Service(MagicMock())
        request = Request(ticket='12345')
        resp = service.ValidateTicket(request, None)
        assert(resp.result is 0)
