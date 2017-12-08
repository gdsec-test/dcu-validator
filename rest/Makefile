REPONAME=ITSecurity/dcu-validator-api
BUILDROOT=$(HOME)/dockerbuild/$(REPONAME)
DOCKERREPO=artifactory.secureserver.net:10014/docker-dcu-local/dcu-validator-api
DATE=$(shell date)
SHELL=/bin/bash

PRIVDEPS=

.PHONY: prep dev stage ote prod clean

all: prep dev


prep:
	@echo "----- preparing $(REPONAME) build -----"
	# stage pips we will need to install in Docker build
	mkdir -p $(BUILDROOT)/private_deps && rm -rf $(BUILDROOT)/private_deps/*
	for entry in $(PRIVDEPS) ; do \
		cd $(BUILDROOT)/private_deps && git clone $$entry ; \
	done
	# copy the app code to the build root
	cp -rp ./* $(BUILDROOT)

prod: prep
	@echo "----- building $(REPONAME) prod -----"
	docker build -t $(DOCKERREPO):prod $(BUILDROOT)

ote: prep
	@echo "----- building $(REPONAME) ote -----"
	docker build -t $(DOCKERREPO):ote $(BUILDROOT)

dev: prep
	@echo "----- building $(REPONAME) dev -----"
	docker build -t $(DOCKERREPO):dev $(BUILDROOT)

clean:
	@echo "----- cleaning $(REPONAME) app -----"
	rm -rf $(BUILDROOT)
