# dcu-validator

This project provides a mechanism to periodically validate DCU abuse complaints. Complaints that are determined to be false positives are closed.

The project is a celery validation service.

[This document](https://confluence.godaddy.com/pages/viewpage.action?pageId=176456269) attempts to explore why each open PHISHING/MALWARE/NETABUSE ticket doesnt have a corresponding scheduled job.

## Table of Contents
  1. [Cloning](#cloning)
  2. [Installing Dependencies](#installing-dependencies)
  3. [Building](#building)
  4. [Deploying](#deploying)
  5. [Testing](#testing)
  6. [Style and Standards](#style-and-standards)
  7. [Built With](#built-with)
  8. [Documentation](#documentation)
  9. [Running Locally](#running-locally)
  10. [Examples](#examples)

## Cloning
To clone the repository via SSH perform the following
```
git clone https://github.secureserver.net/digital-crimes/dcu-validator.git
```
It is recommended that you clone this project into a pyvirtualenv or equivalent virtual environment.

## Installing Dependencies
To install all dependencies for development and testing simply run `make` from the sub-project AND parent levels.

## Building
Building a local Docker image for the respective development environments can be achieved with the following commands from the parent level only:

`make [dev, ote, prod]`

## Deploying
Deploying the Docker image to Kubernetes can be achieved with the
following commands from the parent level only:

`make [dev-deploy, ote-deploy, prod-deploy]`

You must also ensure you have the proper push permissions to
Artifactory or you may experience a Forbidden message.


## Testing
(can be performed from parent and sub-project levels)
```
make test     # runs all unit tests
make testcov  # runs tests with coverage
```

## Style and Standards
All deploys must pass Flake8 linting and all unit tests which are baked into the [Makefile](Makfile).

There are a few commands that might be useful to ensure consistent Python style:

```
make flake8  # Runs the Flake8 linter
make isort   # Sorts all imports
make tools   # Runs both Flake8 and isort
```

These can be performed from parent and sub-project levels.

## Built With

*dcu-validator* is built utilizing the following key technologies
1. [Flask](http://flask.pocoo.org/)
2. [Flask-RestPlus](http://flask-restplus.readthedocs.io/en/stable/)
3. dcdatabase
4. [APS](https://apscheduler.readthedocs.io/en/latest/#)

## Documentation
OpenAPI documentation can be found at
```
/doc
```
after starting the rest service.

## Running Locally

### Running everything in Docker
1. Define these environment variables.
```
scheduler=scheduler
SSO_USER="user to retrieve JWT with"
SSO_PASSWORD="password to retrieve JWT with"
SMDB_USERNAME="<username>"
SMDB_PASSWORD="<password>"
```
2. Run `make dev` to generate the docker images.
1. Run `docker-compose up` to start

### Debugging REST in PyCharm
1. Define these environment variables in your terminal.
```
SSO_USER="user to retrieve JWT with"
SSO_PASSWORD="password to retrieve JWT with"
SMDB_USERNAME="<username>"
SMDB_PASSWORD="<password>"
```
2. Define these environment variables in PyCharm.
```
scheduler='localhost'
MIN_PERIOD=10
```
3. Then run `docker-compose up -d mongo redis kubernetes_proxy scheduler`.
1. In PyCharm, debug the run.py file in the `rest` directory.  This will listen on port `5000`.

This will enable you to debug the REST API endpoints `/validate/<string:ticketid>` and `/schedule/<string:ticketid>`.

### Debugging Scheduler in PyCharm
1. Define these environment variables in your terminal.
```
scheduler='host.docker.internal'
MIN_PERIOD=10
```
2. Define these environment variables in PyCharm.
```
SSO_USER="user to retrieve JWT with"
SSO_PASSWORD="password to retrieve JWT with"
API_UPDATE_URL=https://abuse.api.int.dev-godaddy.com/v1/abuse/tickets
COLLECTION=incidents
DB=devphishstory
DB_HOST=localhost
DOMAIN_SERVICE=localhost:8080
JOBS_COLLECTION=jobs
LISTEN_IP=127.0.0.1
MIN_PERIOD=10
MAX_PERIOD=300
REDIS=localhost
SMDB_USERNAME="<username>"
SMDB_PASSWORD="<password>"
```
2. Then run `docker compose up -d mongo redis kubernetes_proxy api`.
1. In PyCharm, debug the run.py file in the `scheduler` directory.  This will listen on port `50051`.

This will enable you to debug the `AddSchedule`, `RemoveSchedule` and `ValidateTicket` scheduler services.

> The _validate endpoint_ may not be completely functional, as `domainservices` is broken in the dev/test/ote environments, so you can comment/un-comment the appropriate lines in `kube-services.sh` to connect to either the `dev` or `prod` instance of `domainservices`.


## Examples

It is easier to run the examples using [POSTMAN](https://www.postman.com/) after importing the `Validator` configuration file located in [this document](https://confluence.godaddy.com/display/ITSecurity/Postman+Configurations+for+Services+DCU+Utilizes)

#### Schedule validation
```
curl -POST -H 'Content-Type: application/json' http://localhost:5000/validator/schedule/DCU12345 -d '{"period":86400}'
```
```
Responses: ""
If successful: 201 status. Scheduling a job for a non-existent ticket returns successfully.
```
#### Re-Schedule validation: replaces an existing job
```
curl -POST -H 'Content-Type: application/json' http://localhost:5000/validator/schedule/DCU12345 -d '{"period":300}'
```
```
Responses: ""
If successful: 201 status. Re-Scheduling a job for a non-existent ticket returns successfully.
```
#### Delete schedule
```
curl -XDELETE -H 'Content-Type: application/json' http://localhost:5000/validator/schedule/DCU12345
```
```
Responses: no content returned
If successful: 204 status. Deleting a non-existent job returns successfully.
```
#### One time validation (keep open) (example curl only, not completely functional locally)
However... you can modify the following curl command to use domain `validator.abuse-api-dev.svc.cluster.local` which
 you can then run inside any of the godaddy-service pods in the development environment.
```
curl -POST -H 'Content-Type: application/json' http://localhost:5000/validator/validate/DCU12345 -d '{"close":false}'
```
```
Responses: {"reason": "", "result": "VALID"}
If bad ticket number or unable to lookup ticket:
{
    "reason": "unworkable",
    "result": "INVALID"
}
```
#### One time validation (close if invalid) (example curl only, not completely functional locally)
```
curl -POST -H 'Content-Type: application/json' http://localhost:5000/validator/validate/DCU12345 -d '{"close":true}'
```
```
Responses: {"reason": "", "result": "VALID"}
If bad ticket number or unable to lookup ticket:
{
    "reason": "unworkable",
    "result": "INVALID"
}
```