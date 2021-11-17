from celery import Celery
from dcustructuredlogginggrpc import get_logging

from celeryconfig import CeleryConfig
from scheduler_service.schedulers.aps import APS
from scheduler_service.server.service import Service
from settings import get_config

app_settings = get_config()
celery_app = Celery()
celery_app.config_from_object(CeleryConfig(app_settings))

aps = APS()
aps.scheduler.start()
scheduler = Service(aps)
logger = get_logging()


@celery_app.task
def add_schedule(ticket, period, close):
    return scheduler.AddSchedule(ticket, period, close)


@celery_app.task
def validate_ticket(ticket, close):
    return scheduler.ValidateTicket(ticket, close)


@celery_app.task
def add_closure_schedule(ticket, period):
    return scheduler.AddClosureSchedule(ticket, period)
