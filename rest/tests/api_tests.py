import rest.api
from flask import url_for
from mock import patch, MagicMock
from flask_testing.utils import TestCase
from collections import namedtuple
import json


class TestValidator(TestCase):

    def create_app(self):
        return rest.api.create_app('test')

    def setUp(self):
        self.client = self.app.test_client()

    @patch('rest.api.api.AddSchedule')
    @patch('rest.api.api.service_connect')
    def test_schedule_success(self, service, add):
        data = dict(period=300)
        response = self.client.post(url_for('scheduler', ticketid=12345), data=json.dumps(data), headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 201)

    @patch('rest.api.api.AddSchedule')
    @patch('rest.api.api.service_connect')
    def test_reschedule_success(self, service, add):
        data = dict(period=300)
        response = self.client.post(url_for('scheduler', ticketid=12345), data=json.dumps(data), headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 201)

    @patch('rest.api.api.AddSchedule')
    @patch('rest.api.api.service_connect')
    def test_schedule_max_fail(self, service, add):
        data = dict(period=3000000000)
        response = self.client.post(url_for('scheduler', ticketid=12345), data=json.dumps(data), headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 400)

    @patch('rest.api.api.AddSchedule')
    @patch('rest.api.api.service_connect')
    def test_schedule_min_fail(self, service, add):
        data = dict(period=3)
        response = self.client.post(url_for('scheduler', ticketid=12345), data=json.dumps(data), headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 400)

    @patch('rest.api.api.AddSchedule')
    @patch('rest.api.api.service_connect')
    def test_schedule_no_close(self, service, add):
        data = dict(period=300, close=False)
        response = self.client.post(url_for('scheduler', ticketid=12345), data=json.dumps(data), headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 201)

    @patch('rest.api.api.AddSchedule')
    @patch('rest.api.api.service_connect')
    def test_schedule_invalid_close(self, service, add):
        data = dict(period=300, close=12345)
        response = self.client.post(url_for('scheduler', ticketid=12345), data=json.dumps(data), headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 400)

    @patch('rest.api.api.RemoveSchedule')
    @patch('rest.api.api.service_connect')
    def test_remove(self, service, remove):
        response = self.client.delete(url_for('scheduler', ticketid=12345))
        self.assertEqual(response.status_code, 204)

    @patch('rest.api.api.ValidateTicket')
    @patch('rest.api.api.service_connect')
    def test_validate_true(self, service, validate):
        response = self.client.get(url_for('validate', ticketid=12345))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('valid'))

    @patch('rest.api.api.ValidateTicket')
    @patch('rest.api.api.service_connect')
    def test_validate_false(self, service, validate):
        resp = namedtuple('ValidationResponse', 'valid')
        validate.return_value = resp(False)
        response = self.client.get(url_for('validate', ticketid=12345))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data.get('valid'))
