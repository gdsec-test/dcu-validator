BUILDROOT=$(HOME)/dockerbuild/$(IMAGE)
SHELL=/bin/bash

PRIVDEPS=

.PHONY: prep build

all: prep build


prep:
	@echo "----- preparing $(IMAGE) build -----"
	# stage pips we will need to install in Docker build
	mkdir -p $(BUILDROOT)/private_deps && rm -rf $(BUILDROOT)/private_deps/*
	for entry in $(PRIVDEPS) ; do \
		cd $(BUILDROOT)/private_deps && git clone $$entry ; \
	done
	@echo "Generating gRPC stubs"
	python -m grpc_tools.protoc -I../pb --python_out=./rest_service/grpc_stub --grpc_python_out=./rest_service/grpc_stub ../pb/schedule_service.proto
	# copy the app code to the build root
	cp -rp ./* $(BUILDROOT)

build: prep
	@echo "----- building $(IMAGE) prod -----"
	docker build -t $(IMAGE):$(TAG) $(BUILDROOT)

clean:
	@echo "----- cleaning $(BUILDROOT) app -----"
	rm -rf $(BUILDROOT)
