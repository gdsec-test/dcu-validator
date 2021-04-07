import logging
import logging.config
import os
import time
from concurrent import futures

import grpc
import yaml

import scheduler_service.grpc_stub.schedule_service_pb2
import scheduler_service.grpc_stub.schedule_service_pb2_grpc
from scheduler_service.schedulers.aps import APS
from scheduler_service.server.service import Service

_ONE_DAY_IN_SECONDS = 86400


def serve():
    path = os.path.dirname(os.path.abspath(__file__)) + '/' + 'logging.yaml'
    value = os.getenv('LOG_CFG', None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            lconfig = yaml.safe_load(f.read())
        logging.config.dictConfig(lconfig)
    else:
        logging.basicConfig(level=logging.INFO)
    logging.raiseExceptions = True
    logger = logging.getLogger(__name__)

    # Create and start our APScheduler
    aps = APS()
    aps.scheduler.start()
    scheduler = Service(aps)

    # Configure and start service
    server = grpc.server(thread_pool=futures.ThreadPoolExecutor(max_workers=10))
    scheduler_service.grpc_stub.schedule_service_pb2_grpc.add_SchedulerServicer_to_server(
        scheduler, server)
    logger.info("Listening on port 50051...")
    server.add_insecure_port(f'{os.getenv("LISTEN_IP", "[::]")}:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        logger.info("Stopping server")
        server.stop(0)


if __name__ == '__main__':
    serve()
