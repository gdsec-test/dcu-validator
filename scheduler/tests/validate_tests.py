from scheduler_service.server.service import validate, phishstory_db, get_redlock
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
