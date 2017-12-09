IMAGENAME=docker-dcu-local/dcu-validator-scheduler
BUILDROOT=$(HOME)/dockerbuild/$(IMAGENAME)
DOCKERREPO=artifactory.secureserver.net:10014/$(IMAGENAME)
SHELL=/bin/bash

PRIVDEPS="git@github.secureserver.net:ITSecurity/dcdatabase.git"

.PHONY: prep dev stage ote prod clean

all: prep dev


prep:
	@echo "----- preparing $(IMAGENAME) build -----"
	# stage pips we will need to install in Docker build
	mkdir -p $(BUILDROOT)/private_deps && rm -rf $(BUILDROOT)/private_deps/*
	for entry in $(PRIVDEPS) ; do \
		cd $(BUILDROOT)/private_deps && git clone $$entry ; \
	done
	@echo "Generating gRPC stubs"
	python -m grpc_tools.protoc -I../pb --python_out=./grpc_stub --grpc_python_out=./grpc_stub ../pb/schedule_service.proto
	# copy the app code to the build root
	cp -rp ./* $(BUILDROOT)

prod: prep
	@echo "----- building $(IMAGENAME) prod -----"
	docker build -t $(DOCKERREPO):$(TAG) $(BUILDROOT)

ote: prep
	@echo "----- building $(IMAGENAME) ote -----"
	docker build -t $(DOCKERREPO):ote $(BUILDROOT)

dev: prep
	@echo "----- building $(IMAGENAME) dev -----"
	docker build -t $(DOCKERREPO):dev $(BUILDROOT)

clean:
	@echo "----- cleaning $(IMAGENAME) app -----"
	rm -rf $(BUILDROOT)
