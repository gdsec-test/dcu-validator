import logging
import time
from dcustructuredlogginggrpc import LoggerInterceptor, get_logging

from scheduler_service.schedulers.aps import APS
from scheduler_service.server.service import Service

from celery import Celery
from settings import get_config
from celeryconfig import CeleryConfig

app_settings = get_config()
celery_app = Celery()
celery_app.config_from_object(CeleryConfig(app_settings))

aps = APS()
aps.scheduler.start()
scheduler = Service(aps)

@celery_app.task
def addclosureschedule(ticket, period):
    logger = get_logging()
    logger.info("made it here")

    # scheduler.AddClosureSchedule(ticket, period)



