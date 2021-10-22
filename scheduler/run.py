import os
import time
from concurrent import futures

import grpc
from dcustructuredlogginggrpc import LoggerInterceptor, get_logging

import scheduler_service.grpc_stub.schedule_service_pb2
import scheduler_service.grpc_stub.schedule_service_pb2_grpc
from scheduler_service.schedulers.aps import APS
from scheduler_service.server.service import Service

_ONE_DAY_IN_SECONDS = 86400


def serve():
    logger = get_logging()

    # Create and start our APScheduler
    aps = APS()
    aps.scheduler.start()
    scheduler = Service(aps)

    # Configure and start service
    server = grpc.server(thread_pool=futures.ThreadPoolExecutor(max_workers=10), interceptors=[LoggerInterceptor()])
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
