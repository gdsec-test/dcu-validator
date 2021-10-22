import os

import grpc
from dcustructuredloggingflask.flasklogger import get_logging
from flask import request
from flask_restplus import Namespace, Resource, fields

import rest_service.grpc_stub.schedule_service_pb2_grpc
from rest_service.grpc_stub.schedule_service_pb2 import Request

logger = get_logging()


def service_connect():
    scheduler_loc = os.getenv('scheduler', 'scheduler')
    channel = grpc.insecure_channel(scheduler_loc + ':50051')
    return rest_service.grpc_stub.schedule_service_pb2_grpc.SchedulerStub(channel)


def AddClosureSchedule(ticketid, period):
    stub = service_connect()
    logger.info("period {}".format(period))
    return stub.AddClosureSchedule(Request(period=period, ticket=ticketid))


def RemoveSchedule(ticketid):
    stub = service_connect()
    return stub.RemoveSchedule(Request(ticket=ticketid))


def CloseTicket(ticketid):
    stub = service_connect()
    ret = stub.CloseTicket(Request(ticket=ticketid))
    return dict(result=rest_service.grpc_stub.schedule_service_pb2.Result.Name(
        ret.result),
        reason=ret.reason
    )


api = Namespace('closure', description='auto-close ticket')

closure = api.model(
    'closure', {
        'period':
            fields.Integer(
                min=int(os.getenv('MIN_PERIOD', 300)),
                max=15724800,
                default=15724800,
                description='The period to close a ticket'),
    })


@api.route('/schedule/<string:ticketid>', endpoint='scheduler_closure')
@api.doc(params={'ticketid': 'DCU Ticket ID'})
class ClosureScheduler(Resource):

    @api.response(201, 'Schedule created')
    @api.response(400, 'Validation Error')
    @api.expect(closure)
    def post(self, ticketid):
        """
        Schedule a ticket for closure
        """
        payload = request.json
        period = payload.get('period')
        AddClosureSchedule(ticketid, period)
        return '', 201
