import logging
import os

import grpc
from flask import request
from flask_restplus import Namespace, Resource, fields

import rest_service.grpc_stub.schedule_service_pb2_grpc
from rest_service.grpc_stub.schedule_service_pb2 import Request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def service_connect():
    scheduler_loc = os.getenv('scheduler') or 'scheduler'
    channel = grpc.insecure_channel(scheduler_loc + ':50051')
    return rest_service.grpc_stub.schedule_service_pb2_grpc.SchedulerStub(channel)


def AddSchedule(ticketid, period, close):
    stub = service_connect()
    return stub.AddSchedule(Request(period=period, close=close, ticket=ticketid))


def RemoveSchedule(ticketid):
    stub = service_connect()
    return stub.RemoveSchedule(Request(ticket=ticketid))


def ValidateTicket(ticketid, close):
    stub = service_connect()
    ret = stub.ValidateTicket(Request(ticket=ticketid, close=close))
    return dict(result=rest_service.grpc_stub.schedule_service_pb2.Result.Name(
        ret.result),
        reason=ret.reason
    )


api = Namespace('validator', description='Validator operations')

validator = api.model(
    'Validator', {
        'period':
            fields.Integer(
                min=300,
                max=90000,
                default=86400,
                description='The period to validate a ticket'),
        'close':
            fields.Boolean(
                default=True,
                description='Close the ticket if validation fails')
    })

options = api.model(
    'Options', {
        'close':
            fields.Boolean(
                default=True,
                description='Close the ticket if validation fails')
    })

ticket_model = api.model(
    'Ticket', {
        'result':
            fields.String(
                description='Result of the validation checks', enum=['VALID', 'INVALID', 'LOCKED']),
        'reason':
            fields.String(
                description='Reason for the given result'
            )
    })


@api.route('/validate/<string:ticketid>', endpoint='validate')
@api.doc(params={'ticketid': 'DCU Ticket ID'})
class Validate(Resource):

    @api.response(400, 'Validation Error')
    @api.response(200, 'Success', model=ticket_model)
    @api.marshal_with(ticket_model, 200)
    @api.expect(options)
    def post(self, ticketid):
        """
        Validate a DCU ticket
        """
        payload = request.json
        close = payload.get('close', False)
        response = ValidateTicket(ticketid, close)
        return response, 200


@api.route('/schedule/<string:ticketid>', endpoint='scheduler')
@api.doc(params={'ticketid': 'DCU Ticket ID'})
class TicketScheduler(Resource):

    @api.response(201, 'Schedule created')
    @api.response(400, 'Validation Error')
    @api.expect(validator)
    def post(self, ticketid):
        """
        Schedule/Re-schedule a ticket for validation
        """
        payload = request.json
        period = payload.get('period')
        close = payload.get('close', False)
        AddSchedule(ticketid, period, close)
        return '', 201

    @api.response(204, 'Schedule deleted')
    @api.response(400, 'Validation Error')
    def delete(self, ticketid):
        """
        Delete an existing schedule
        """
        logger.info("Removing schedule for {}".format(ticketid))
        RemoveSchedule(ticketid)
        return '', 204
