import logging
from flask import current_app, request
from flask_restplus import Namespace, fields, Resource

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate(ticket, data):
    logger.info('Validating {}')


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


@api.route('/schedule/<string:id>')
@api.doc(params={'id': 'DCU Ticket ID'})
class Scheduler(Resource):

    @api.doc('schedule/re-schedule validation')
    @api.response(201, 'Schedule created')
    @api.response(400, 'Validation Error')
    @api.expect(validator)
    def post(self, id):
        scheduler = current_app.config.get('scheduler')
        job = scheduler.get_job(id)
        payload = request.json
        period = payload.get('period')
        if job:
            logger.info("Rescheduling job for {} seconds".format(
                int(period)))
            job.reschedule('interval', seconds=int(period))
        else:
            logger.info("Scheduling job for {} seconds".format(
                int(period)))
            scheduler.add_job(
                validate, 'interval', seconds=int(period), args=[id, payload], id=id)
        return '', 201

    @api.doc('delete schedule')
    @api.response(204, 'Schedule deleted')
    @api.response(400, 'Validation Error')
    def delete(self, id):
        scheduler = current_app.config.get('scheduler')
        job = scheduler.get_job(id)
        if job:
            logger.info("Removing job {}".format(id))
            job.remove()
        return '', 204
