import schedule_service_pb2
import schedule_service_pb2_grpc
import pymongo
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.jobstores.mongodb import MongoDBJobStore
from pytz import utc
import logging
import grpc
import time
from concurrent import futures

_ONE_DAY_IN_SECONDS = 86400
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate(ticket, data=None):
    logger.info("Validating {} with payload {}".format(ticket, data))
    # TODO
    # Lookup ticket.
    # if ticket doesnt exist delete schedule
    # if ticket exists and is not locked
    #     if invalid
    #        if  data.close=True then close ticket
    #     delete schedule
    # else
    #     return True
    return True


class Scheduler(schedule_service_pb2_grpc.SchedulerServicer):

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        job_defaults = {'coalesce': True, 'max_instances': 3}
        executers = {'default': ProcessPoolExecutor(5)}
        jobstores = {
            'default': self._get_jobstore(),
        }
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            job_defaults=job_defaults,
            executers=executers,
            timezone=utc)
        self.scheduler.start()

    def AddSchedule(self, request, context):
        self._logger.info("Adding schedule for {}".format(request))
        ticketid = request.ticket
        period = request.period
        job = self.scheduler.get_job(ticketid)
        if job:
            self._logger.info("Rescheduling ticket {} for {} seconds".format(
                ticketid, int(period)))
            job.reschedule('interval', seconds=int(period))
        else:
            self._logger.info("Scheduling ticket {} for {} seconds".format(
                ticketid, int(period)))
            self.scheduler.add_job(
                validate, 'interval',
                seconds=int(period),
                args=[ticketid, request],
                id=ticketid)
        return schedule_service_pb2.Response()

    def RemoveSchedule(self, request, context):
        self._logger.info("Removing schedule for {}".format(request))
        ticketid = request.ticket
        job = self.scheduler.get_job(ticketid)
        if job:
            job.remove()
        return schedule_service_pb2.Response()

    def ValidateTicket(self, request, context):
        self._logger.info("Validating {}".format(request))
        return schedule_service_pb2.ValidationResponse(valid=validate(request.ticket))

    def _get_jobstore(self):
        db_user = os.getenv('DB_USER') or ''
        db_pass = os.getenv('DB_PASS') or ''
        db_host = os.getenv('DB_HOST') or 'localhost'
        db = os.getenv('DB') or 'apscheduler'
        if db_user and db_pass:
            db_url = 'mongodb://{}:{}@{}/{}'.format(db_user, db_pass, db_host,
                                                    db)
        else:
            db_url = 'mongodb://{}/{}'.format(db_host, db)
        client = pymongo.MongoClient(db_url, connect=False)
        return MongoDBJobStore(database=db, client=client)


def serve():
    server = grpc.server(thread_pool=futures.ThreadPoolExecutor(max_workers=10))
    schedule_service_pb2_grpc.add_SchedulerServicer_to_server(
        Scheduler(), server)

    logger.info("Listening on port 50051...")
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        logger.info("Stopping server")
        server.stop(0)


if __name__ == '__main__':
    serve()
