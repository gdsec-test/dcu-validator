FROM python:3.7.10-slim
LABEL MAINTAINER=dcueng@godaddy.com

# Best Practice - Creating a user instead of running as root
RUN addgroup dcu && adduser --disabled-password --disabled-login --no-create-home --ingroup dcu --system dcu
# Expose grpc port 50051
EXPOSE 50051

# Move files to new directory in docker container
COPY ./*.ini ./*.sh ./*.yaml ./*.py /app/
COPY . /tmp
RUN chown dcu:dcu -R /app

# install custom root certificates
RUN mkdir -p /usr/local/share/ca-certificates/
RUN cp /tmp/certs/* /usr/local/share/ca-certificates/
RUN update-ca-certificates

RUN pip install --compile /tmp/private_deps/dcdatabase
RUN pip install --compile /tmp && rm -rf /tmp/*

# Over-write the certifi shipped certificate with the system cert.
RUN cp /etc/ssl/certs/ca-certificates.crt /usr/local/lib/python3.7/site-packages/certifi/cacert.pem

ENTRYPOINT ["/app/runserver.sh"]
