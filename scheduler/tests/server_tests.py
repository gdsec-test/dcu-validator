from scheduler_service.server.service import Service
from mock import MagicMock, patch
from scheduler_service.grpc_stub.schedule_service_pb2 import Request


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

    @patch('scheduler_service.server.service.get_redlock')
    @patch('scheduler_service.server.service.phishstory_db')
    def test_validate_ticket(self, phishstory, redlock):
        ticket_data = dict(phishstory_status='OPEN')
        redlock.return_value=MagicMock(create_lock=lambda x: True, acquire=lambda: True)
        phishstory.return_value=MagicMock(get_incident=lambda x: ticket_data)
        service = Service(MagicMock())
        request = Request(ticket='12345')
        resp = service.ValidateTicket(request, None)
        assert(resp.valid is True)
