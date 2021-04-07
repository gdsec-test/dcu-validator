import logging
import os

from apscheduler import jobstores
from dcdatabase.phishstorymongo import PhishstoryMongo

from scheduler_service.grpc_stub.schedule_service_pb2 import (
    INVALID, LOCKED, VALID, Response, ValidationResponse)
from scheduler_service.grpc_stub.schedule_service_pb2_grpc import \
    SchedulerServicer
from scheduler_service.schedulers.aps import APS
from scheduler_service.utils.api_helper import APIHelper
from scheduler_service.utils.db_settings import create_db_settings
from scheduler_service.utils.lock import Lock
from scheduler_service.validators.route import route

LOGGER = logging.getLogger(__name__)
TTL = os.getenv('TTL') or 300
TTL *= 1000


def validate(ticket, data=None):
    """
    Runs validation on the provided ticket
    :param ticket: string
    :param data: Dictionary containing properties used for scheduling
    :return: Enumeration indicating the result of the validation
    """
    LOGGER.info('Validating {} with payload {}'.format(ticket, data))
    lock = get_redlock(ticket)
    db_handle = phishstory_db()
    ticket_data = db_handle.get_incident(ticket)

    if ticket_data is None or ticket_data.get('phishstory_status', 'OPEN') == 'CLOSED':
        remove_job(ticket)
        return INVALID, 'unworkable'
    else:
        if lock.acquire():
            try:
                resp = route(ticket_data)
                if not resp[0]:
                    if data and data.get('close', False):
                        # close ticket
                        LOGGER.info('Closing ticket {}'.format(ticket))
                        db_handle.update_actions_sub_document(ticket, 'closed as {}'.format(resp[1]))
                        if not APIHelper().close_incident(ticket, resp[1]):
                            LOGGER.error('Unable to close ticket {}'.format(ticket))
                    remove_job(ticket)
                    return INVALID, resp[1]
            except Exception as e:
                LOGGER.error('Unable to validate {}:{}'.format(ticket, e))
            finally:
                lock.release()
        else:
            return LOCKED, 'being worked'
    return VALID, ''


def remove_job(ticket):
    """
    Removes the ticket from the db jobs collection
    :param ticket: string
    :return: None
    """
    try:
        if get_scheduler().get_job(ticket):
            get_scheduler().remove_job(ticket)
    except Exception as e:
        LOGGER.warning('Unable to remove job {}:{}'.format(ticket, e))


def get_redlock(ticket):
    """
    Retrieves RedLock lock
    :param ticket:
    :return: lock object
    """
    return Lock().lock.create_lock(ticket, ttl=TTL)


def phishstory_db():
    """
    Retrieves a PhishstoryMongo instance
    :return: db instance
    """
    return PhishstoryMongo(create_db_settings())


def get_scheduler():
    """
    Retrieves a APS instance
    :return: scheduler instance
    """
    return APS().scheduler


class Service(SchedulerServicer):
    """
    Handles scheduling and validating DCU tickets via gRPC
    """

    def __init__(self, scheduler):
        self._logger = logging.getLogger(__name__)
        self.aps = scheduler

    def AddSchedule(self, request, context):
        """
        Adds a schedule (or reschedules) validation for a ticket
        :param request: GRPC scheduler.Request
        :param context: not used
        :return: GRPC scheduler.Response
        """
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
                    dict(close=request.close)
                ],
                id=ticketid,
                replace_existing=True)
        return Response()

    def RemoveSchedule(self, request, context):
        """
        Removes a scheduled validation job for a ticket
        :param request: GRPC scheduler.Request
        :param context: not used
        :return: GRPC scheduler.Response
        """
        self._logger.info("Removing schedule for {}".format(request))
        ticketid = request.ticket
        try:
            # Need to use remove job to handle breaking changes between pickle
            # versions. This just removes by the job ID string, instead of
            # needing to parse the serialized object.
            self.aps.scheduler.remove_job(ticketid)
        except jobstores.base.JobLookupError:
            # Ensure we don't throw errors if someone deletes a job that
            # doesn't exist.
            pass
        return Response()

    def ValidateTicket(self, request, context):
        """
        Validates the source URI for a ticket
        :param request: GRPC scheduler.Request
        :param context: not used
        :return: GRPC scheduler.ValidationResponse
        """
        self._logger.info("Validating {}".format(request))
        res = validate(request.ticket, dict(close=request.close))
        return ValidationResponse(result=res[0], reason=res[1])
