import os

from celery import Celery
from kombu import Exchange, Queue


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
    WORKER_ENABLE_REMOTE_CONTROL = False

    QUEUE = Queue('queue', Exchange('queue'), routing_key='queue', queue_arguments={'x-queue-type': 'quorum'}) \
        if os.getenv('QUEUE_TYPE') == 'quorum' else 'queue'
    VALIDATORQUEUE = Queue('devvalidator', Exchange('devvalidator'), routing_key='devvalidator',
                           queue_arguments={'x-queue-type': 'quorum'}) \
        if os.getenv('QUEUE_TYPE') == 'quorum' else 'devvalidator'

    def __init__(self):
        self.task_routes = {
            'run.add_closure_schedule': {self.QUEUE: self.VALIDATORQUEUE},
            'run.validate_ticket': {self.QUEUE: self.VALIDATORQUEUE},
            'run.add_schedule': {self.QUEUE: self.VALIDATORQUEUE}
        }
        self.broker_url = os.getenv('MULTIPLE_BROKERS') if os.getenv('QUEUE_TYPE') == 'quorum' \
            else os.getenv('SINGLE_BROKER')


app = Celery()
app.config_from_object(CeleryConfig())
task = app.send_task('run.add_closure_schedule', args=("DCU003508988", 10))
response1 = app.send_task('run.validate_ticket', args=("DCU003509216", True))
response2 = app.send_task('run.add_schedule', args=("DCU003509215", 10, True))
