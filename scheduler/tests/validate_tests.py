from mock import MagicMock, patch
from redlock import RedLockFactory

from scheduler_service.server.service import validate
from scheduler_service.utils.api_helper import APIHelper


class TestValidate:

    @patch.object(APIHelper, '_get_jwt')
    @patch('scheduler_service.server.service.get_redlock')
    @patch('scheduler_service.server.service.phishstory_db')
    @patch('scheduler_service.validators.route.route')
    def test_valid(self, route, phishstory, redlock, mock_jwt):
        route.return_value = (True, ' ')
        ticket_data = dict(phishstory_status='OPEN')
        redlock.return_value = MagicMock(spec=RedLockFactory, acquire=lambda: True, create_lock=lambda x: True, release=lambda: True)
        phishstory.return_value = MagicMock(get_incident=lambda x: ticket_data)
        res = validate('12345')
        assert(res[0] == 0)

    @patch.object(APIHelper, '_get_jwt')
    @patch('scheduler_service.server.service.get_redlock')
    @patch('scheduler_service.server.service.phishstory_db')
    @patch('scheduler_service.server.service.get_scheduler')
    def test_closed(self, scheduler, phishstory, redlock, mock_jwt):
        ticket_data = dict(phishstory_status='CLOSED')
        scheduler.return_value = MagicMock(remove_job=lambda x: True)
        redlock.return_value = MagicMock(spec=RedLockFactory, create_lock=lambda x: True)
        phishstory.return_value = MagicMock(get_incident=lambda x: ticket_data)
        res = validate('12345')
        assert(res[0] == 1)

    @patch.object(APIHelper, '_get_jwt')
    @patch.object(APIHelper, 'close_incident')
    @patch('scheduler_service.server.service.get_redlock')
    @patch('scheduler_service.server.service.phishstory_db')
    @patch('scheduler_service.server.service.get_scheduler')
    @patch('scheduler_service.server.service.route')
    def test_invalid(self, route, scheduler, phishstory, redlock, apihelper, mock_jwt):
        route.return_value = (False, 'unresolvable')
        scheduler.return_value = MagicMock(remove_job=lambda x: True)
        ticket_data = dict(phishstory_status='OPEN')
        phishstory.return_value = MagicMock(get_incident=lambda x: ticket_data)
        apihelper.return_value = True
        redlock.return_value = MagicMock(spec=RedLockFactory, acquire=lambda: True, create_lock=lambda x: True, release=lambda: True)
        res = validate('12345')
        assert(res[0] == 1)
