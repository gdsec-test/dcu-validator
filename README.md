# dcu-validator

This project provides a mechanism to periodically validate DCU abuse complaints. Complaints that are determined to be false positives are closed.

The project is broken into two major components. A REST server and a gRPC scheduling and validation service.

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

*Important Note: `pip install grpcio-tools==1.14.0` must be performed separately from above `make` instructions

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
5. [gRPC](https://grpc.io)

## Documentation
Swaggar documentation can be found at

```
/doc
```
After starting each component.

## Running Locally

Temporarily Install docker-compose
```
pip install docker-compose
```
Use the text below to create a `docker-compose.yml` file.
Place at project root level, do NOT overwrite the docker-compose file in the `scheduler` directory.

Then run `docker-compose up`

This will start both a `mongodb` and `redis` instance locally, and will access your local mongo instance's `devphishstory` database in both the `incidents` and `jobs` collections.
```
api:
  image: docker-dcu-local.artifactory.secureserver.net/dcu-validator-api:dev
  links:
    - validationscheduler:scheduler
  ports:
    - 5000:5000

validationscheduler:
  image: docker-dcu-local.artifactory.secureserver.net/dcu-validator-scheduler:dev
  environment:
    - DB_HOST=mongo
    - DB=devphishstory
    - COLLECTION=incidents
  ports:
    - 50051:50051
  links:
    - mongo:mongo
    - redis:redis

mongo:
  image: mongo:latest
  ports:
     - 27017:27017

redis:
  image: redis:latest
  ports:
     - 6379:6379
```
This will enable you to run _basic scheduling ONLY_... the _validate endpoints_ will not work, as locally running code is unable to access the `domainservice` REST endpoints, since they are k8s accessible only.

## Examples

It is easier to run the examples using [POSTMAN](https://www.postman.com/) after importing the `Validator` configuration file located in [this document](https://confluence.godaddy.com/display/ITSecurity/Postman+Configurations+for+Services+DCU+Utilizes)

#### Schedule validation
```
curl -POST -H 'Content-Type: application/json' http://localhost:5000/validator/schedule/12345 -d '{"period":86400}'
```
```
Responses: ""
If successful: 201 status. Scheduling a job for a non-existent ticket returns successfully.
```
#### Re-Schedule validation: replaces an existing job
```
curl -POST -H 'Content-Type: application/json' http://localhost:5000/validator/schedule/12345 -d '{"period":300}'
```
```
Responses: ""
If successful: 201 status. Re-Scheduling a job for a non-existent ticket returns successfully.
```
#### Delete schedule
```
curl -XDELETE -H 'Content-Type: application/json' http://localhost:5000/validator/schedule/12345
```
```
Responses: no content returned
If successful: 204 status. Deleting a non-existent job returns successfully.
```
#### One time validation (keep open) (example curl only, will not run successfully locally)
However... you can modify the following curl command to use domain `validator.abuse-api-dev.svc.cluster.local` which
 you can then run inside any of the godaddy-service pods in the development environment.
```
curl -POST -H 'Content-Type: application/json' http://localhost:5000/validator/validate/12345 -d '{"close":false}'
```
```
Responses: {"reason": "", "result": "VALID"}
If bad ticket number or unable to lookup ticket:
{
    "reason": "unworkable",
    "result": "INVALID"
}
```
#### One time validation (close if invalid) (example curl only, will not run successfully locally)
```
curl -POST -H 'Content-Type: application/json' http://localhost:5000/validator/validate/12345 -d '{"close":true}'
```
```
Responses: {"reason": "", "result": "VALID"}
If bad ticket number or unable to lookup ticket:
{
    "reason": "unworkable",
    "result": "INVALID"
}
```