import logging
import os
from scheduler_service.grpc_stub.schedule_service_pb2_grpc import SchedulerServicer
from scheduler_service.grpc_stub.schedule_service_pb2 import Response, ValidationResponse
from scheduler_service.schedulers.aps import APS
from redlock import RedLockFactory
from dcdatabase.phishstorymongo import PhishstoryMongo
from scheduler_service.utils.db_settings import create_db_settings
from scheduler_service.utils.lock import Lock

LOGGER = logging.getLogger(__name__)
TTL = os.getenv('TTL') or 300
TTL *= 1000


def validate(ticket, data=None):
    '''
    Runs validation on the provided ticket
    :param ticket:
    :param data: Dictionary containing properties used for scheduling
    :return: Boolean indicating whether the ticket will be scheduled again
    '''
    LOGGER.info("Validating {} with payload {}".format(ticket, data))
    lock = get_redlock(ticket)
    db_handle = phishstory_db()
    ticket_data = db_handle.get_incident(ticket)

    if ticket_data is None or ticket_data.get('phishstory_status', 'OPEN') == 'CLOSED':
       try:
           get_scheduler().remove_job(ticket)
       except Exception as e:
           LOGGER.error('Unable to remove job {}:{}'.format(ticket, e))
    else:
        if lock.acquire():
            try:
                if False:  # TODO call validate funcion
                    if data and data.get('close', False):
                        # close ticket
                        LOGGER.info('Closing ticket {}'.format(ticket))
                    get_scheduler().remove_job(ticket)
                else:
                    return True
            except Exception as e:
               LOGGER.error('Unable to validate {}:{}'.format(ticket, e))
            finally:
               lock.release()
    return False

def get_redlock(ticket):
    '''
    Retrieves RedLock lock
    :param ticket:
    :return:
    '''
    return Lock().lock.create_lock(ticket, ttl=TTL)


def phishstory_db():
    '''
    Retrieves a PhishstoryMongo instance
    '''
    return PhishstoryMongo(create_db_settings())

def get_scheduler():
    '''
    Retrieves a APS instance
    :return:
    '''
    return APS().scheduler

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
