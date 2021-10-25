import os
from datetime import datetime, timedelta

import grpc
from apscheduler import jobstores
from dcdatabase.phishstorymongo import PhishstoryMongo
from dcustructuredlogginggrpc import get_logging

import scheduler_service.grpc_stub.schedule_service_pb2
import scheduler_service.grpc_stub.schedule_service_pb2_grpc
from scheduler_service.grpc_stub.schedule_service_pb2 import (
    INVALID, LOCKED, VALID, Response, ValidationResponse)
# Request
from scheduler_service.grpc_stub.schedule_service_pb2_grpc import \
    SchedulerServicer
from scheduler_service.schedulers.aps import APS
from scheduler_service.utils.api_helper import APIHelper
from scheduler_service.utils.db_settings import create_db_settings
from scheduler_service.utils.lock import Lock
from scheduler_service.validators.route import route

LOGGER = get_logging()
TTL = os.getenv('TTL') or 300
TTL *= 1000
ONEWEEK = 604800
# Need to support empty strings so we don't break behavior for older tickets.
ALLOWED_PROXY_VALUES = ['', 'USA']


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
    elif ticket_data.get('proxy', '') in ALLOWED_PROXY_VALUES:
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


def service_connect():
    scheduler_loc = os.getenv('scheduler', 'scheduler')
    channel = grpc.insecure_channel(scheduler_loc + ':50051')
    return scheduler_service.grpc_stub.schedule_service_pb2_grpc.SchedulerStub(channel)


def close_ticket(ticket):
    LOGGER.info(f'Running scheduled close_ticket check for {ticket}')
    lock = get_redlock(ticket)
    db_handle = phishstory_db()
    ticket_data = db_handle.get_incident(ticket)
    LOGGER.info(ticket)
    if lock.acquire():
        try:
            last_modified = ticket_data[os.getenv('KEY_LAST_MODIFIED') or 'last_modified']
            now = datetime.now()
            diff = now - timedelta(hours=24)
            if diff <= last_modified <= now:
                LOGGER.info(f'{ticket} was recently modified, rescheduling closure for tomorrow')
                # remove_job(ticket)
                # stub = service_connect()
                # stub.AddClosureSchedule(Request(period=ONEWEEK, ticket=ticket), None)
                return LOCKED, 'being worked'
            LOGGER.info(f'Closing ticket {ticket}')
            if not APIHelper().close_incident(ticket, 'resolved'):
                LOGGER.error(f'Unable to close ticket {ticket}')
                return INVALID, 'unworkable'
            remove_job(ticket)
        except Exception as e:
            LOGGER.error(f'Unable to close exception {ticket}:{e}')
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
        self._logger = LOGGER
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

    def AddClosureSchedule(self, request: scheduler_service.grpc_stub.schedule_service_pb2.Request, context):
        """
        Adds a schedule for closing a ticket
        """
        self._logger.info(f"Adding schedule for {request}")
        ticketid = request.ticket
        period = request.period
        self._logger.info(f"Scheduling ticket {ticketid} for {period} seconds")
        self.aps.scheduler.add_job(
            close_ticket,
            'interval',
            seconds=period,
            args=[
                ticketid,
            ],
            id=ticketid,
            replace_existing=True)
        return Response()
