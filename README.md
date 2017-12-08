# dcu-validator

This project provides a mechanism to periodically validate DCU abuse complaints. Complaints that are determined to be false positives are closed.

The project is broken into two major components. A REST server and a gRPC scheduling service.

## Cloning
To clone the repository via SSH perform the following
```
git clone https://github.secureserver.net/ITSecurity/dcu-validator.git
```
It is recommended that you clone this project into a pyvirtualenv or equivalent virtual enviornment.

## Installing Dependencies
You can install the required private dependencies for each component via:
```
pip install -r private_pips.txt
```
You may also manually pip install private pips using this command:
```
pip install git+ssh://git@github.secureserver.net/{orgname}/{reponame}.git
```
You can install the required dependencies for each component via
```
pip install -r requirements.txt
```

## Building
Building a local Docker image for the respective development environments can be achieved with the following commands:

`make [dev, ote, prod]`

## Deploying
Deploying the Docker image to Kubernetes can be achieved with the
following commands:

`make [dev-deploy, ote-deploy, prod-deploy]`

You must also ensure you have the proper push permissions to
Artifactory or you may experience a Forbidden message.

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

One time validation
```
curl -X GET --header 'Accept: application/json' 'http://localhost:5000/validator/validate/12345'
```

## Testing
In order to run the tests you must first install the required dependencies for each component via
```
pip install -r test_requirements.txt
```

After this you may run the tests via
```
nosetests -w rest/tests/ --cover-package=rest
nosetests -w scheduler/tests/ --cover-package=scheduler
```
Optionally, you may provide the flag `--with-coverage` to `nosetests` to determine the test coverage of this project.

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
  ports:
    - 50051:50051
  links:
    - mongo:mongo

mongo:
  image: mongo:latest
  ports:
     - 27017:27017
```
This will enable you to run basic scheduling.

## Built With

*dcu-validator* is built utilizing the following key technologies
1. [Flask](http://flask.pocoo.org/)
2. [Flask-RestPlus](http://flask-restplus.readthedocs.io/en/stable/)
3. dcdatabase
4. [APS](https://apscheduler.readthedocs.io/en/latest/#)
5. [gRPC](https://grpc.io)
