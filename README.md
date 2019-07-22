# dcu-validator

This project provides a mechanism to periodically validate DCU abuse complaints. Complaints that are determined to be false positives are closed.

The project is broken into two major components. A REST server and a gRPC scheduling and validation service.

## Cloning
To clone the repository via SSH perform the following
```
git clone https://github.secureserver.net/digital-crimes/dcu-validator.git
```
It is recommended that you clone this project into a pyvirtualenv or equivalent virtual environment.

## Installing Dependencies
To install all dependencies for development and testing simply run `make` from the parent or sub-project levels.

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


## Testing (can be performed from parent and sub-project levels)
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

## Documentation
Swaggar documentation can be found at

```
/doc
```
After starting each component.

## Examples

Schedule validation
```
curl -XPOST -H 'Content-Type: application/json' -v http://localhost:5000/validator/schedule/12345 -d '{"period":86400}'
```

Re-schedule validation
```
curl -XPOST -H 'Content-Type: application/json' -v http://localhost:5000/validator/schedule/12345 -d '{"period":300}'
```

Delete schedule
```
curl -XDELETE -H 'Content-Type: application/json' -v http://localhost:5000/validator/schedule/12345
```

One time validation (keep open)
```
curl -XPOST -H 'Content-Type: application/json' -v http://localhost:5000/validator/validate/12345 -d '{"close":false}'
```

One time validation (close if invalid)
```
curl -XPOST -H 'Content-Type: application/json' -v http://localhost:5000/validator/validate/12345 -d '{"close":true}'
```

## Running Locally
TODO
Temporarily
Install docker-compose
```
pip install docker-compose
```
Use the below file to test (docker-compose.yml)
```
api:
  image: artifactory.secureserver.net:10014/docker-dcu-local/dcu-validator-api:dev
  links:
    - validationscheduler:scheduler
  ports:
    - 5000:5000

validationscheduler:
  image: artifactory.secureserver.net:10014/docker-dcu-local/dcu-validator-scheduler:dev
  environment:
    - DB_HOST=mongo
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
This will enable you to run basic scheduling.

## Built With

*dcu-validator* is built utilizing the following key technologies
1. [Flask](http://flask.pocoo.org/)
2. [Flask-RestPlus](http://flask-restplus.readthedocs.io/en/stable/)
3. dcdatabase
4. [APS](https://apscheduler.readthedocs.io/en/latest/#)
5. [gRPC](https://grpc.io)
