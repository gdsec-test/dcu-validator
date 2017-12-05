# DCU-Validator
#
#

FROM alpine:3.5
MAINTAINER DCUENG <dcueng@godaddy.com>

# TODO: Very if want dcu as user or something else
# Best Practice - Creating a user instead of running as root
RUN addgroup -S dcu && adduser -H -S -G dcu dcu

# TODO: Determine what installs we need.  Below is duplicate of Phishnet installs.  Some may/may not be needed
# apt-get installs
RUN apk update && \
    apk add --no-cache build-base \
    ca-certificates \
    libffi-dev \
    linux-headers \
    openssl-dev \
    python-dev \
    py-pip

# TODO: Verify this is port Chris is using in flask api app
# Expose Flask port 5000
EXPOSE 5000

# TODO: Conform 'app' foldername for docker and runserver.py is what is being used
# Move files to new directory in docker container
COPY ./*.ini ./*.sh ./runserver.py ./*.yml /app/
COPY . /tmp
RUN chown dcu:dcu -R /app

# TODO: Confirm only DCDatabase from Chris' branch and path
# pip install from our private pips staged by our Makefile
RUN for dep in dcdatabase; \
  do \
  pip install --compile "/tmp/private_deps/$dep"; \
done

RUN pip install --compile /tmp && rm -rf /tmp/*

# TODO: Confirm runserver.sh entrypoint
ENTRYPOINT ["/app/runserver.sh"]