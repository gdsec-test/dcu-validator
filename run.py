import logging
from flask import Flask, current_app
from flask_restplus import Api, Resource, fields
from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate(data):
    logger.info(data)


app = Flask(__name__)
api = Api(
    app,
    version='1.0',
    title='DCU Validator API',
    description='Periodically validates existing DCU tickets',
    validate=True,
)

ns = api.namespace('validator', description='Validator operations')

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


@ns.route('/schedule/<string:id>')
class Scheduler(Resource):

    @ns.doc('schedule/re-schedule validation')
    @ns.expect(validator)
    def post(self, id):
        scheduler = current_app.config.get('scheduler')
        job = scheduler.get_job(id)
        payload = api.payload
        period = payload.get('period')
        if job:
            logger.info("Rescheduling job for {} seconds".format(
                int(period)))
            job.reschedule('interval', seconds=int(period))
        else:
            logger.info("Scheduling job for {} seconds".format(
                int(period)))
            scheduler.add_job(
                validate, 'interval', seconds=int(period), args=[id], id=id)
        return '', 201

    @ns.doc('delete schedule')
    @ns.response(204, 'schedule deleted')
    def delete(self, id):
        scheduler = current_app.config.get('scheduler')
        job = scheduler.get_job(id)
        if job:
            logger.info("Removing job {}".format(id))
            job.remove()
        return '', 204


if __name__ == '__main__':
    job_defaults = {'coalesce': True, 'max_instances': 3}
    executers = {'default': ProcessPoolExecutor(5)}
    scheduler = BackgroundScheduler(
        job_defaults=job_defaults, executers=executers, timezone=utc)
    scheduler.add_jobstore('mongodb', connect=False)
    scheduler.start()
    app.config['scheduler'] = scheduler
    app.run(debug=True)
