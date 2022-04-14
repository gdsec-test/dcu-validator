import os

from celery import Celery


class CeleryConfig:
    broker_transport = 'pyamqp'
    broker_use_ssl = True
    task_serializer = 'pickle'
    result_serializer = 'pickle'
    accept_content = ['json', 'pickle']
    imports = 'run'
    worker_hijack_root_logger = False
    task_acks_late = True
    worker_prefetch_multiplier = 1
    worker_send_task_events = False
    QUEUE = 'queue'
    VALIDATORQUEUE = 'devvalidator'

    def __init__(self):
        self.task_routes = {
            'run.add_closure_schedule': {self.QUEUE: self.VALIDATORQUEUE},
            'run.validate_ticket': {self.QUEUE: self.VALIDATORQUEUE},
            'run.add_schedule': {self.QUEUE: self.VALIDATORQUEUE}
        }
        # TODO: lkm - fix this!
        self.BROKER_PASS = os.getenv('BROKER_PASS', None)
        self.broker_url = 'amqp://02d1081iywc7Av2:' + self.BROKER_PASS + '@rmq-dcu.int.dev-godaddy.com:5672/grandma'


app = Celery()
app.config_from_object(CeleryConfig())
task = app.send_task('run.add_closure_schedule', args=("DCU003508988", 10))
response1 = app.send_task('run.validate_ticket', args=("DCU003509216", True))
response2 = app.send_task('run.add_schedule', args=("DCU003509215", 10, True))
