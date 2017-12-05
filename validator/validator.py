import logging
from flask import current_app, request
from flask_restplus import Namespace, fields, Resource
from . scheduler import Scheduler
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate(ticket, data=None):
    logger.info('Validating {} with payload {}'.format(ticket, data))
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
        'valid': fields.Boolean(description='Indicates if the ticket has passed validation')
    }
)


@api.route('/validate/<string:id>', endpoint='validate')
@api.doc(params={'id': 'DCU Ticket ID'})
class Validate(Resource):

    @api.marshal_with(ticket_model, 200)
    def get(self, id):
        """
        Validate a DCU ticket
        """
        return {'valid': validate(id)}, 200


@api.route('/schedule/<string:id>', endpoint='scheduler')
@api.doc(params={'id': 'DCU Ticket ID'})
class TicketScheduler(Resource):

    @api.response(201, 'Schedule created')
    @api.response(400, 'Validation Error')
    @api.expect(validator)
    def post(self, id):
        """
        Schedule/Re-schedule a ticket for validation
        """
        scheduler = current_app.config.get('scheduler')
        job = scheduler.get_job(id)
        payload = request.json
        period = payload.get('period')
        if job:
            logger.info("Rescheduling ticket {} for {} seconds".format(
                id, int(period)))
            job.reschedule('interval', seconds=int(period))
        else:
            logger.info("Scheduling ticket {} for {} seconds".format(
                id, int(period)))
            scheduler.add_job(
                validate, 'interval', seconds=int(period), args=[id, payload], id=id)
        return '', 201

    @api.response(204, 'Schedule deleted')
    @api.response(400, 'Validation Error')
    def delete(self, id):
        """
        Delete and existing schedule
        """
        scheduler = current_app.config.get('scheduler')
        job = scheduler.get_job(id)
        if job:
            logger.info("Removing schedule for {}".format(id))
            job.remove()
        return '', 204
