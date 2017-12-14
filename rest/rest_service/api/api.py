import logging
from flask import request
from flask_restplus import Namespace, fields, Resource
from rest_service.grpc_stub.schedule_service_pb2 import Request
import rest_service.grpc_stub.schedule_service_pb2_grpc
import os
import grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def service_connect():
    scheduler_loc = os.getenv('scheduler') or 'scheduler'
    channel = grpc.insecure_channel(scheduler_loc + ':50051')
    return rest_service.grpc_stub.schedule_service_pb2_grpc.SchedulerStub(channel)


def AddSchedule(ticketid, period):
    stub = service_connect()
    return stub.AddSchedule(Request(period=period, close=False, ticket=ticketid))


def RemoveSchedule(ticketid):
    stub = service_connect()
    return stub.RemoveSchedule(Request(ticket=ticketid))


def ValidateTicket(ticketid):
    stub = service_connect()
    return stub.ValidateTicket(Request(ticket=ticketid))

api = Namespace('validator', description='Validator operations')

validator = api.model(
    'Validator', {
        'period':
            fields.Integer(
                min=300,
                max=86400,
                default=86400,
                description='The period to validate a ticket'),
        'close':
            fields.Boolean(
                default=True,
                description='Close the ticket if validation fails')
    })

ticket_model = api.model(
    'Ticket', {
        'valid':
            fields.Boolean(
                description='Indicates if the ticket has passed validation')
    })


@api.route('/validate/<string:ticketid>', endpoint='validate')
@api.doc(params={'ticketid': 'DCU Ticket ID'})
class Validate(Resource):

    @api.marshal_with(ticket_model, 200)
    def get(self, ticketid):
        """
        Validate a DCU ticket
        """
        response = ValidateTicket(ticketid)
        data = dict(valid=response.valid)
        return data, 200


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
        AddSchedule(ticketid, period)
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
