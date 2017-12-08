# DCU-Validator
#
#

FROM alpine:3.5
MAINTAINER DCUENG <dcueng@godaddy.com>

# Best Practice - Creating a user instead of running as root
RUN addgroup -S dcu && adduser -H -S -G dcu dcu

# apt-get installs
RUN apk update && \
    apk add --no-cache build-base \
    ca-certificates \
    libffi-dev \
    linux-headers \
    openssl-dev \
    pcre \
    pcre-dev \
    python-dev \
    py-pip

# Expose Flask port 5000
EXPOSE 5000

# Move files to new directory in docker container
COPY ./*.ini ./*.sh ./run.py ./*.yml /app/
COPY . /tmp
RUN chown dcu:dcu -R /app

RUN pip install --compile /tmp && rm -rf /tmp/*

ENTRYPOINT ["/app/runserver.sh"]
