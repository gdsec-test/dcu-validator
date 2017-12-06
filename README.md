# dcu-validator

This project provides a mechanism to periodically validate DCU abuse complaints. Complaints that are determined to be false positives are closed.

## Cloning
To clone the repository via SSH perform the following
```
git clone https://github.secureserver.net/ITSecurity/dcu-validator.git
```
It is recommended that you clone this project into a pyvirtualenv or equivalent virtual enviornment.

## Installing Dependencies
You can install the required private dependencies via:
```
pip install -r private_pips.txt
```
You may also manually pip install private pips using this command:
```
pip install git+ssh://git@github.secureserver.net/{orgname}/{reponame}.git
```
You can install the required dependencies via
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
In order to run the tests you must first install the required dependencies via
```
pip install -r test_requirements.txt
```

After this you may run the tests via
```
nosetests tests/ --cover-package=validator/
```
Optionally, you may provide the flag `--with-coverage` to `nosetests` to determine the test coverage of this project.

## Running Locally
TODO
temporarily you can start mongo via
```
docker run -d -name mongo -p 27017:27017 mongo:latest
python run.py
```

## Built With

*dcu-validator* is built utilizing the following key technologies
1. Flask
2. Flask-RestPlus
3. dcdatabase
4. APS
