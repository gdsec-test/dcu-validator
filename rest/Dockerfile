FROM python:3.7.10-slim
LABEL MAINTAINER=dcueng@godaddy.com

# Best Practice - Creating a user instead of running as root
RUN addgroup dcu && adduser --disabled-password --disabled-login --no-create-home --ingroup dcu --system dcu
RUN apt-get update && apt-get install -y gcc
EXPOSE 5000

# Move files to new directory in docker container
COPY ./*.ini ./*.sh ./*.yaml ./*.py /app/
COPY . /tmp
RUN chown dcu:dcu -R /app

RUN PIP_CONFIG_FILE=/tmp/pip_config/pip.conf pip install --compile /tmp && rm -rf /tmp/*
RUN apt-get remove -y gcc

ENTRYPOINT ["/app/runserver.sh"]