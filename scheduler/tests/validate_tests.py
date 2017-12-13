from scheduler_service.server.service import validate, phishstory_db, get_redlock
from apscheduler.schedulers.background import BackgroundScheduler
from scheduler_service.schedulers.aps import APS
from redlock import RedLockFactory
from mock import patch, MagicMock


class TestValidate:

    @patch('scheduler_service.server.service.get_redlock')
    @patch('scheduler_service.server.service.phishstory_db')
    def test_valid(self, phishstory, redlock):
        ticket_data = dict(phishstory_status='OPEN')
        redlock.return_value = MagicMock(spec=RedLockFactory, acquire=lambda: True, create_lock=lambda x: True, release=lambda: True)
        phishstory.return_value = MagicMock(get_incident=lambda x: ticket_data)
        assert(validate('12345') is True)

    @patch('scheduler_service.server.service.get_redlock')
    @patch('scheduler_service.server.service.phishstory_db')
    @patch('scheduler_service.server.service.get_scheduler')
    def test_closed(self, scheduler, phishstory, redlock):
        ticket_data = dict(phishstory_status='CLOSED')
        scheduler.return_value = MagicMock(remove_job=lambda x: True)
        redlock.return_value = MagicMock(spec=RedLockFactory, create_lock=lambda x: True)
        phishstory.return_value = MagicMock(get_incident=lambda x: ticket_data)
        assert(validate('12345') is False)
