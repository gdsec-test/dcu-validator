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


def AddSchedule(ticketid, period, close):
    stub = service_connect()
    return stub.AddSchedule(Request(period=period, close=close, ticket=ticketid))


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
                max=int(os.getenv('MAX_PERIOD', 90000)),
                default=86400,
                description='The period to close a ticket'),
    })


# ticket_model = api.model(
#     'Ticket', {
#         'result':
#             fields.String(
#                 description='Result of the validation checks', enum=['VALID', 'INVALID', 'LOCKED']),
#         'reason':
#             fields.String(
#                 description='Reason for the given result'
#             )
#     })


@api.route('/close/<string:ticketid>', endpoint='close')
@api.doc(params={'ticketid': 'DCU Ticket ID'})
class Close(Resource):

    @api.response(400, 'Closure Error')
    @api.response(200, 'Success')
    def post(self, ticketid):
        """
        Validate a DCU ticket
        """
        response = CloseTicket(ticketid)
        return response, 200


@api.route('/schedule/<string:ticketid>', endpoint='scheduler_closure')
@api.doc(params={'ticketid': 'DCU Ticket ID'})
class ClosureScheduler(Resource):

    @api.response(201, 'Schedule created')
    @api.response(400, 'Validation Error')
    @api.expect(closure)
    def post(self, ticketid):
        """
        Schedule/Re-schedule a ticket for validation
        """
        payload = request.json
        period = payload.get('period')
        AddSchedule(ticketid, period)
        return '', 201
