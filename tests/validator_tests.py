import validator
from flask import url_for
from mock import patch, MagicMock
from nose.tools import assert_true
from flask_testing.utils import TestCase
from apscheduler.schedulers.background import BackgroundScheduler
import json


class TestValidator(TestCase):

    def create_app(self):
        return validator.create_app('test')

    def setUp(self):
        self.client = self.app.test_client()


    def test_schedule_success(self):
        scheduler = MagicMock(spec=BackgroundScheduler, get_job=lambda x: False)
        self.client.application.config['scheduler'] = scheduler
        data = dict(period=300)
        response = self.client.post(url_for('validator_scheduler', id=12345), data=json.dumps(data), headers={'Content-Type':'application/json'})
        self.assertEqual(response.status_code, 201)

    def test_reschedule_success(self):
        scheduler = MagicMock(spec=BackgroundScheduler)
        self.client.application.config['scheduler'] = scheduler
        data = dict(period=300)
        response = self.client.post(url_for('validator_scheduler', id=12345), data=json.dumps(data), headers={'Content-Type':'application/json'})
        self.assertEqual(response.status_code, 201)

    def test_schedule_max_fail(self):
        scheduler = MagicMock(spec=BackgroundScheduler)
        self.client.application.config['scheduler'] = scheduler
        data = dict(period=3000000000)
        response = self.client.post(url_for('validator_scheduler', id=12345), data=json.dumps(data), headers={'Content-Type':'application/json'})
        self.assertEqual(response.status_code, 400)

    def test_schedule_min_fail(self):
        scheduler = MagicMock(spec=BackgroundScheduler)
        self.client.application.config['scheduler'] = scheduler
        data = dict(period=3)
        response = self.client.post(url_for('validator_scheduler', id=12345), data=json.dumps(data), headers={'Content-Type':'application/json'})
        self.assertEqual(response.status_code, 400)

    def test_schedule_no_close(self):
        scheduler = MagicMock(spec=BackgroundScheduler)
        self.client.application.config['scheduler'] = scheduler
        data = dict(period=300, close=False)
        response = self.client.post(url_for('validator_scheduler', id=12345), data=json.dumps(data), headers={'Content-Type':'application/json'})
        self.assertEqual(response.status_code, 201)

    def test_schedule_invalid_close(self):
        scheduler = MagicMock(spec=BackgroundScheduler)
        self.client.application.config['scheduler'] = scheduler
        data = dict(period=300, close=12345)
        response = self.client.post(url_for('validator_scheduler', id=12345), data=json.dumps(data), headers={'Content-Type':'application/json'})
        self.assertEqual(response.status_code, 400)

    def test_remove(self):
        scheduler = MagicMock(spec=BackgroundScheduler)
        self.client.application.config['scheduler'] = scheduler
        response = self.client.delete(url_for('validator_scheduler', id=12345))
        self.assertEqual(response.status_code, 204)
