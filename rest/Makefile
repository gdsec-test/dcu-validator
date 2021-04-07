BUILDNAME=digital-crimes/dcu-validator-rest
BUILDROOT=$(HOME)/dockerbuild/$(BUILDNAME)
SHELL=/bin/bash

PRIVDEPS=

.PHONY: prep build

all: env

env:
	pip install -r test_requirements.txt
	pip install -r requirements.txt

.PHONY: flake8
flake8:
	@echo "----- Running linter -----"
	flake8 --config ./.flake8 .

.PHONY: isort
isort:
	@echo "----- Optimizing imports -----"
	isort --atomic --skip rest_service/grpc_stub --skip .venv/ .

.PHONY: grpc
grpc:
	@echo "Generating gRPC stubs"
	python -m grpc_tools.protoc -I../pb --python_out=./rest_service/grpc_stub --grpc_python_out=./rest_service/grpc_stub ../pb/schedule_service.proto

.PHONY: tools
tools: flake8 isort grpc

.PHONY: test
test: tools
	@echo "----- Running tests -----"
	nosetests tests

.PHONY: testcov
testcov:
	@echo "----- Running tests with coverage -----"
	nosetests tests --with-coverage --cover-erase --cover-package=rest_service

prep: tools
	@echo "----- preparing $(IMAGE) build -----"
	# stage pips we will need to install in Docker build
	mkdir -p $(BUILDROOT)/private_deps && rm -rf $(BUILDROOT)/private_deps/*
	for entry in $(PRIVDEPS) ; do \
		cd $(BUILDROOT)/private_deps && git clone $$entry ; \
	done
	# copy the app code to the build root
	cp -rp ./* $(BUILDROOT)

build: prep
	@echo "----- building $(IMAGE):$(TAG) -----"
	docker build -t $(IMAGE):$(TAG) $(BUILDROOT)

clean:
	@echo "----- cleaning $(BUILDROOT) -----"
	rm -rf $(BUILDROOT)
