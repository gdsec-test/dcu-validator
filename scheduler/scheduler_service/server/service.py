import logging
import os
from scheduler_service.grpc_stub.schedule_service_pb2_grpc import SchedulerServicer
from scheduler_service.grpc_stub.schedule_service_pb2 import Response, ValidationResponse, INVALID, VALID, LOCKED
from scheduler_service.schedulers.aps import APS
from scheduler_service.utils.db_settings import create_db_settings
from scheduler_service.utils.lock import Lock
from scheduler_service.validators.route import route
from scheduler_service.utils.api_helper import APIHelper
from dcdatabase.phishstorymongo import PhishstoryMongo

LOGGER = logging.getLogger(__name__)
TTL = os.getenv('TTL') or 300
TTL *= 1000


def validate(ticket, data=None):
    '''
    Runs validation on the provided ticket
    :param ticket:
    :param data: Dictionary containing properties used for scheduling
    :return: Enumeration indicating the result of the validation
    '''
    LOGGER.info('Validating {} with payload {}'.format(ticket, data))
    lock = get_redlock(ticket)
    db_handle = phishstory_db()
    ticket_data = db_handle.get_incident(ticket)

    if ticket_data is None or ticket_data.get('phishstory_status', 'OPEN') == 'CLOSED':
        remove_job(ticket)
        return INVALID
    else:
        if lock.acquire():
            try:
                resp = route(ticket_data)
                if not resp[0]:
                    if data and data.get('close', False):
                        # close ticket
                        LOGGER.info('Closing ticket {}'.format(ticket))
                        if not APIHelper().close_incident(ticket, resp[1]):
                            LOGGER.error('Unable to close ticket {}'.format(ticket))
                    remove_job(ticket)
                    return INVALID
            except Exception as e:
                LOGGER.error('Unable to validate {}:{}'.format(ticket, e))
            finally:
                lock.release()
        else:
            return LOCKED
    return VALID


def remove_job(ticket):
    try:
        get_scheduler().remove_job(ticket)
    except Exception as e:
        LOGGER.warning('Unable to remove job {}:{}'.format(ticket, e))


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
        res = validate(request.ticket)
        return ValidationResponse(
            result=res)
