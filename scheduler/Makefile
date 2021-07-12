BUILDNAME=digital-crimes/dcu-validator-scheduler
BUILDROOT=$(HOME)/dockerbuild/$(BUILDNAME)
SHELL=/bin/bash

PRIVDEPS="git@github.secureserver.net:digital-crimes/dcdatabase.git" \
 "git@github.com:gdcorp-infosec/dcu-structured-logging-grpc.git"

.PHONY: prep build

all: env

env:
	pip install -r test_requirements.txt
	pip install -r private_pips.txt
	pip install -r requirements.txt

.PHONY: flake8
flake8:
	@echo "----- Running linter -----"
	flake8 --config ./.flake8 .

.PHONY: isort
isort:
	@echo "----- Optimizing imports -----"
	isort --atomic --skip scheduler_service/grpc_stub --skip .venv/ .

.PHONY: grpc
grpc:
	@echo "Generating gRPC stubs"
	python -m grpc_tools.protoc -I../pb --python_out=./scheduler_service/grpc_stub --grpc_python_out=./scheduler_service/grpc_stub ../pb/schedule_service.proto

.PHONY: tools
tools: flake8 isort grpc

.PHONY: test
test: tools
	@echo "----- Running tests -----"
	nosetests tests

.PHONY: testcov
testcov:
	@echo "----- Running tests with coverage -----"
	nosetests tests --with-coverage --cover-erase --cover-package=scheduler_service --cover-xml

prep:
	@echo "----- preparing $(IMAGE) build -----"
	# stage pips we will need to install in Docker build
	mkdir -p $(BUILDROOT)/private_deps && rm -rf $(BUILDROOT)/private_deps/*
	for entry in $(PRIVDEPS) ; do \
		IFS=";" read repo revision <<< "$$entry" ; \
		cd $(BUILDROOT)/private_deps && git clone $$repo ; \
		if [ "$$revision" != "" ] ; then \
			name=$$(echo $$repo | awk -F/ '{print $$NF}' | sed -e 's/.git$$//') ; \
			cd $(BUILDROOT)/private_deps/$$name ; \
			current_revision=$$(git rev-parse HEAD) ; \
			echo $$repo HEAD is currently at revision: $$current_revision ; \
			echo Dependency specified in the Makefile for $$name is set to revision: $$revision ; \
			echo Reverting to revision: $$revision in $$repo ; \
			git reset --hard $$revision; \
		fi ; \
	done
	# copy the app code to the build root
	cp -rp ./* $(BUILDROOT)

build: prep
	@echo "----- building $(IMAGE):$(TAG) -----"
	docker build -t $(IMAGE):$(TAG) $(BUILDROOT)

clean:
	@echo "----- cleaning $(BUILDROOT) -----"
	rm -rf $(BUILDROOT)
	
