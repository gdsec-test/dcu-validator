import logging
import os
from collections import namedtuple
from scheduler_service.grpc_stub.schedule_service_pb2_grpc import SchedulerServicer
from scheduler_service.grpc_stub.schedule_service_pb2 import Response, ValidationResponse
from scheduler_service.schedulers.aps import APS
from redlock import RedLockFactory
from dcdatabase.phishstorymongo import PhishstoryMongo

LOGGER = logging.getLogger(__name__)


def validate(ticket, data=None):
    LOGGER.info("Validating {} with payload {}".format(ticket, data))
    lock = get_redlock(ticket)
    db_handle = phishstory_db()
    ticket_data = db_handle.get_incident(ticket)

    if ticket_data is None or ticket_data.get('phishstory_status', 'OPEN') == 'CLOSED':
        APS().scheduler.remove_job(ticket)
    else:
        if lock.acquire():
            if False:  # TODO call validate funcion
                if data and data.get('close', False):
                    # close ticket
                    LOGGER.info('Closing ticket {}'.format(ticket))
                APS().scheduler.remove_job(ticket)
    return True

def get_redlock(ticket):
    redis = os.getenv('REDIS') or 'localhost'
    ttl = os.getenv('TTL') or 300
    ttl *= 1000
    lock = RedLockFactory(connection_details=redis)
    ticket_lock = lock.create_lock(ticket, ttl=ttl)


def phishstory_db():
    '''
    Retrieves a PhishstoryMongo instance
    '''
    db_user = os.getenv('DB_USER') or ''
    db_pass = os.getenv('DB_PASS') or ''
    db_host = os.getenv('DB_HOST') or 'localhost'
    db = os.getenv('DB') or 'test'
    collection = os.getenv('COLLECTION') or 'test'
    db_url = 'mongodb://{}:{}@{}/{}'.format(db_user, db_pass, db_host, db)
    settings = namedtuple('settings', 'DB COLLECTION DBURL')
    return PhishstoryMongo(settings(DB=db, COLLECTION=collection, DBURL=db_url))


class Service(SchedulerServicer):
    '''
    Handles scheduling and validating DCU tickets via gRPC
    '''

    def __init__(self, scheduler):
        self._logger = logging.getLogger(__name__)
        self.aps = scheduler

    def AddSchedule(self, request, context):
        self._logger.info("Adding schedule for {}".format(request))
        ticketid = request.ticket
        period = request.period
        job = self.aps.scheduler.get_job(ticketid)
        if job:
            self._logger.info("Rescheduling ticket {} for {} seconds".format(
                ticketid, int(period)))
            job.reschedule('interval', seconds=int(period))
        else:
            self._logger.info("Scheduling ticket {} for {} seconds".format(
                ticketid, int(period)))
            self.aps.scheduler.add_job(
                validate,
                'interval',
                seconds=int(period),
                args=[
                    ticketid,
                    dict(period=period, close=request.period, ticket=ticketid)
                ],
                id=ticketid)
        return Response()

    def RemoveSchedule(self, request, context):
        self._logger.info("Removing schedule for {}".format(request))
        ticketid = request.ticket
        job = self.aps.scheduler.get_job(ticketid)
        if job:
            job.remove()
        return Response()

    def ValidateTicket(self, request, context):
        self._logger.info("Validating {}".format(request))
        valid = validate(request.ticket)
        return ValidationResponse(
            valid=valid)
