import json

from flask import url_for
from flask_testing.utils import TestCase
from mock import patch

import rest_service.api


class TestValidator(TestCase):
    HEADERS = {'Content-Type': 'application/json'}
    INVALID = 'INVALID'
    KEY_RESULT = 'result'
    SCHEDULER = 'scheduler'
    VALID = 'VALID'
    VALIDATE = 'validate'

    def create_app(self):
        return rest_service.api.create_app()

    def setUp(self):
        self.client = self.app.test_client()

    @patch('rest_service.api.api.AddSchedule')
    @patch('rest_service.api.api.service_connect')
    def test_schedule_success(self, service, add):
        data = dict(period=300)
        response = self.client.post(url_for(self.SCHEDULER, ticketid=12345),
                                    data=json.dumps(data),
                                    headers=self.HEADERS)
        self.assertEqual(response.status_code, 201)

    @patch('rest_service.api.api.AddSchedule')
    @patch('rest_service.api.api.service_connect')
    def test_reschedule_success(self, service, add):
        data = dict(period=300)
        response = self.client.post(url_for(self.SCHEDULER, ticketid=12345),
                                    data=json.dumps(data),
                                    headers=self.HEADERS)
        self.assertEqual(response.status_code, 201)

    @patch('rest_service.api.api.AddSchedule')
    @patch('rest_service.api.api.service_connect')
    def test_schedule_max_fail(self, service, add):
        data = dict(period=3000000000)
        response = self.client.post(url_for(self.SCHEDULER, ticketid=12345),
                                    data=json.dumps(data),
                                    headers=self.HEADERS)
        self.assertEqual(response.status_code, 400)

    @patch('rest_service.api.api.AddSchedule')
    @patch('rest_service.api.api.service_connect')
    def test_schedule_min_fail(self, service, add):
        data = dict(period=3)
        response = self.client.post(url_for(self.SCHEDULER, ticketid=12345),
                                    data=json.dumps(data),
                                    headers=self.HEADERS)
        self.assertEqual(response.status_code, 400)

    @patch('rest_service.api.api.AddSchedule')
    @patch('rest_service.api.api.service_connect')
    def test_schedule_no_close(self, service, add):
        data = dict(period=300, close=False)
        response = self.client.post(url_for(self.SCHEDULER, ticketid=12345),
                                    data=json.dumps(data),
                                    headers=self.HEADERS)
        self.assertEqual(response.status_code, 201)

    @patch('rest_service.api.api.AddSchedule')
    @patch('rest_service.api.api.service_connect')
    def test_schedule_invalid_close(self, service, add):
        data = dict(period=300, close=12345)
        response = self.client.post(url_for(self.SCHEDULER, ticketid=12345),
                                    data=json.dumps(data),
                                    headers=self.HEADERS)
        self.assertEqual(response.status_code, 400)

    @patch('rest_service.api.api.RemoveSchedule')
    @patch('rest_service.api.api.service_connect')
    def test_remove(self, service, remove):
        response = self.client.delete(url_for(self.SCHEDULER,
                                              ticketid=12345))
        self.assertEqual(response.status_code, 204)

    @patch('rest_service.api.api.ValidateTicket')
    @patch('rest_service.api.api.service_connect')
    def test_validate_true(self, service, validate):
        validate.return_value = dict(result=self.VALID, reason='')
        data = dict(close=False)
        response = self.client.post(url_for(self.VALIDATE, ticketid=12345),
                                    data=json.dumps(data),
                                    headers=self.HEADERS)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get(self.KEY_RESULT), self.VALID)

    @patch('rest_service.api.api.ValidateTicket')
    @patch('rest_service.api.api.service_connect')
    def test_validate_false(self, service, validate):
        validate.return_value = dict(result=self.INVALID, reason='')
        data = dict(close=False)
        response = self.client.post(url_for(self.VALIDATE, ticketid=12345),
                                    data=json.dumps(data),
                                    headers=self.HEADERS)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get(self.KEY_RESULT), self.INVALID)
