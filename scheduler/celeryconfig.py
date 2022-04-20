import os

from kombu import Exchange, Queue


class CeleryConfig:
    _result_hostname = os.getenv("RESULT_BACKEND_HOSTNAME", "result-backend")
    broker_transport = 'pyamqp'
    broker_use_ssl = not os.getenv('DISABLESSL', False)  # True unless local docker-compose testing
    worker_concurrency = 4
    task_serializer = 'json'
    result_serializer = 'pickle'
    result_backend = f'redis://{_result_hostname}:6379/0'
    accept_content = ['json', 'pickle']
    imports = 'run'
    worker_hijack_root_logger = False
    task_acks_late = True
    worker_prefetch_multiplier = 1
    worker_send_task_events = False
    # Force kill a task if it takes longer than three minutes.
    task_time_limit = 180
    WORKER_ENABLE_REMOTE_CONTROL = False

    def __init__(self, app_settings):
        self.broker_url = app_settings.BROKER_URL
        self.task_queues = (
            Queue(app_settings.VALIDATORQUEUE, Exchange(app_settings.VALIDATORQUEUE),
                  routing_key=app_settings.VALIDATORQUEUE, queue_arguments={'x-queue-type': 'quorum'})
            if app_settings.QUEUE_TYPE == 'quorum' else
            Queue(app_settings.VALIDATORQUEUE, Exchange(app_settings.VALIDATORQUEUE),
                  routing_key=app_settings.VALIDATORQUEUE),
        )
