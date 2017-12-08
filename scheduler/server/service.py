import logging
from grpc_stub.schedule_service_pb2_grpc import SchedulerServicer
from grpc_stub.schedule_service_pb2 import Response, ValidationResponse

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


class Service(SchedulerServicer):

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
