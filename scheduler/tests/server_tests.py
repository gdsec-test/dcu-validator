from unittest import TestCase
from unittest.mock import MagicMock, patch

from scheduler_service.server.service import Service


class TestScheduler(TestCase):

    def test_add_schedule(self):
        service = Service(MagicMock())
        resp = service.AddSchedule('12345', 300, False)  # noqa: F841

    def test_reschedule(self):
        service = Service(MagicMock())
        resp = service.AddSchedule('12345', 300, False)  # noqa: F841

    def test_remove_schedule(self):
        service = Service(MagicMock())
        resp = service.RemoveSchedule('12345')  # noqa: F841

    @patch('scheduler_service.server.service.validate')
    def test_validate_ticket(self, validate):
        validate.return_value = (0, 'blah')
        service = Service(MagicMock())
        resp = service.ValidateTicket('12345')
        self.assertEqual(resp[0], 0)
