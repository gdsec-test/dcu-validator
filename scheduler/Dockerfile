FROM gdartifactory1.jfrog.io/docker-dcu-local/dcu-python3.11:1.1
LABEL MAINTAINER=dcueng@godaddy.com

USER root

# Move files to new directory in docker container
COPY ./*.ini ./*.sh ./*.py /app/
COPY . /tmp
RUN chown dcu:dcu -R /app

RUN PIP_CONFIG_FILE=/tmp/pip_config/pip.conf pip install --compile /tmp && rm -rf /tmp/*

# Over-write the certifi shipped certificate with the system cert.
RUN cp /etc/ssl/certs/ca-certificates.crt /usr/local/lib/python3.11/site-packages/certifi/cacert.pem

WORKDIR "/app"
USER dcu
ENTRYPOINT ["/usr/local/bin/celery", "-A", "run", "worker", "-l", "INFO", "--without-heartbeat", "--without-gossip", "--without-mingle"]
