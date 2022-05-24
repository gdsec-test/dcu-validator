import os
from datetime import datetime, timedelta

from apscheduler import jobstores
from dcdatabase.phishstorymongo import PhishstoryMongo
from dcustructuredlogginggrpc import get_logging

from scheduler_service.schedulers.aps import APS
from scheduler_service.utils.api_helper import APIHelper
from scheduler_service.utils.db_settings import create_db_settings
from scheduler_service.utils.lock import Lock
from scheduler_service.validators.route import route

LOGGER = get_logging()
TTL = os.getenv('TTL') or 300
TTL *= 1000
ONEWEEK = 604800
KEY_LAST_MODIFIED = "last_modified"
# Need to support empty strings so we don't break behavior for older tickets.
ALLOWED_PROXY_VALUES = ['', 'USA']


def validate(ticket: str, data=None):
    """
    Runs validation on the provided ticket
    :return: Enumeration indicating the result of the validation
    """
    LOGGER.info(f'Validating {ticket} with payload {data}')
    lock = get_redlock(ticket)
    db_handle = phishstory_db()
    ticket_data = db_handle.get_incident(ticket)

    if ticket_data is None or ticket_data.get('phishstory_status', 'OPEN') == 'CLOSED':
        remove_job(ticket)
        return 'INVALID', 'unworkable'
    else:
        if lock.acquire():
            try:
                resp = route(ticket_data)
                if not resp[0]:
                    if data and data.get('close', False):
                        # close ticket
                        LOGGER.info(f'Closing ticket {ticket}')
                        # add close action reason and specific validator as user to mongodb ticket
                        db_handle.update_actions_sub_document(ticket, f'closed as {resp[1]}', resp[2])
                        if not APIHelper().close_incident(ticket, resp[1]):
                            LOGGER.error(f'Unable to close ticket {ticket}')
                    remove_job(ticket)
                    return 'INVALID', resp[1]
            except Exception as e:
                LOGGER.error(f'Unable to validate {ticket}:{e}')
            finally:
                lock.release()
        else:
            return 'LOCKED', 'being worked'
    return 'VALID', ''


def close_ticket(ticket: str):
    LOGGER.info(f'Running scheduled close_ticket check for {ticket}')
    lock = get_redlock(ticket)
    db_handle = phishstory_db()
    ticket_data = db_handle.get_incident(ticket)
    LOGGER.info(ticket_data)
    if lock.acquire():
        try:
            if ticket_data is None or ticket_data.get('phishstory_status', 'OPEN') == 'CLOSED':
                LOGGER.info(f'{ticket} was already closed, removing the scheduled close job')
                remove_job(f'{ticket}-close-job')
                return ''
            else:
                last_modified = ticket_data[KEY_LAST_MODIFIED]
                now = datetime.utcnow()
                diff = now - timedelta(hours=72)
                if diff <= last_modified <= now:
                    LOGGER.info(f'{ticket} was recently modified, rescheduling closure for next week')
                    remove_job(f'{ticket}-close-job')
                    get_scheduler().add_job(
                        close_ticket,
                        'interval',
                        seconds=ONEWEEK,
                        args=[
                            ticket
                        ],
                        id=f'{ticket}-close-job',
                        replace_existing=True)
                    return 'being worked'
                LOGGER.info(f'Closing ticket {ticket}')
                if not APIHelper().close_incident(ticket, 'resolved'):
                    LOGGER.error(f'Unable to close ticket {ticket}')
                    return 'unworkable'
                remove_job(f'{ticket}-close-job')
        except Exception as e:
            LOGGER.error(f'Unable to close exception {ticket}:{e}')
        finally:
            lock.release()
    else:
        return 'being worked'
    return ''


def remove_job(ticket: str):
    """
    Removes the ticket from the db jobs collection
    """
    try:
        if get_scheduler().get_job(ticket):
            get_scheduler().remove_job(ticket)
    except Exception as e:
        LOGGER.warning(f'Unable to remove job {ticket}:{e}')


def get_redlock(ticket: str):
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


class Service():
    """
    Handles scheduling and validating DCU tickets via gRPC
    """

    def __init__(self, scheduler):
        self._logger = LOGGER
        self.aps = scheduler

    def AddSchedule(self, ticketid: str, period: int, close: bool):
        """
        Adds a schedule (or reschedules) validation for a ticket
        """
        self._logger.info(f"Adding schedule for {ticketid}")
        job = self.aps.scheduler.get_job(ticketid)
        if job:
            self._logger.info(f"Rescheduling ticket {ticketid} for {period} seconds")
            job.reschedule('interval', seconds=period)
        else:
            self._logger.info(f"Scheduling ticket {ticketid} for {period} seconds")
            self.aps.scheduler.add_job(
                validate,
                'interval',
                seconds=period,
                args=[
                    ticketid,
                    dict(close=close)
                ],
                id=ticketid,
                replace_existing=True)
        return True

    def RemoveSchedule(self, ticketid: str):
        """
        Removes a scheduled validation job for a ticket
        """
        self._logger.info(f"Removing schedule for {ticketid}")
        try:
            # Need to use remove job to handle breaking changes between pickle
            # versions. This just removes by the job ID string, instead of
            # needing to parse the serialized object.
            self.aps.scheduler.remove_job(ticketid)
        except jobstores.base.JobLookupError:
            # Ensure we don't throw errors if someone deletes a job that
            # doesn't exist.
            pass

    def ValidateTicket(self, ticketid: str, close: bool = None):
        """
        Validates the source URI for a ticket
        """

        self._logger.info(f"Validating {ticketid}")
        res = validate(ticketid, dict(close=close))

        return res

    def AddClosureSchedule(self, ticketid: str, period: int):
        """
        Adds a schedule for closing a ticket
        """
        self._logger.info(f"Scheduling ticket {ticketid} for {period} seconds")
        self.aps.scheduler.add_job(
            close_ticket,
            'interval',
            seconds=period,
            args=[
                ticketid
            ],
            id=f'{ticketid}-close-job',
            replace_existing=True)
        return True
