import os

from celery import Celery, bootsteps
from dcustructuredlogginggrpc import get_logging
from elasticapm import Client, instrument
from elasticapm.contrib.celery import (register_exception_tracking,
                                       register_instrumentation)
from kombu.common import QoS

from apm import register_dcu_transaction_handler
from celeryconfig import CeleryConfig
from scheduler_service.schedulers.aps import APS
from scheduler_service.server.service import Service
from settings import get_config

app_settings = get_config()
celery_app = Celery()
celery_app.config_from_object(CeleryConfig(app_settings))

instrument()
apm = Client(service_name='validator', env=os.getenv('sysenv', 'dev'))
register_exception_tracking(apm)
register_instrumentation(apm)
register_dcu_transaction_handler(apm)

aps = APS()
aps.scheduler.start()
scheduler = Service(aps)
logger = get_logging()


# turning off global qos in celery
class NoChannelGlobalQoS(bootsteps.StartStopStep):
    requires = {'celery.worker.consumer.tasks:Tasks'}

    def start(self, c):
        qos_global = False

        c.connection.default_channel.basic_qos(0, c.initial_prefetch_count, qos_global)

        def set_prefetch_count(prefetch_count):
            return c.task_consumer.qos(
                prefetch_count=prefetch_count,
                apply_global=qos_global,
            )

        c.qos = QoS(set_prefetch_count, c.initial_prefetch_count)


celery_app.steps['consumer'].add(NoChannelGlobalQoS)


@celery_app.task
def add_schedule(ticket, period, close):
    return scheduler.AddSchedule(ticket, period, close)


@celery_app.task
def validate_ticket(ticket, close):
    return scheduler.ValidateTicket(ticket, close)


@celery_app.task
def add_closure_schedule(ticket, period):
    return scheduler.AddClosureSchedule(ticket, period)
