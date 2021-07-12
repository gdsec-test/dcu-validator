BUILDNAME=digital-crimes/dcu-validator
DOCKERREPO=docker-dcu-local.artifactory.secureserver.net
BUILDROOT=$(HOME)/dockerbuild/$(BUILDNAME)
DATE=$(shell date)
GIT_COMMIT=
BUILD_BRANCH=origin/master
SHELL=/bin/bash
API_IMAGE=$(DOCKERREPO)/dcu-validator-api
SCHEDULER_IMAGE=$(DOCKERREPO)/dcu-validator-scheduler

.PHONY: prep dev stage ote prod clean dev-deploy ote-deploy prod-deploy

all: prep

.PHONY: env
env:
	pip install -r rest/test_requirements.txt
	pip install -r scheduler/test_requirements.txt
	pip install -r scheduler/private_pips.txt
	pip install -r rest/private_pips.txt
	pip install -r scheduler/requirements.txt
	pip install -r rest/requirements.txt

.PHONY: tools
tools:
	cd rest && $(MAKE) tools
	cd scheduler && $(MAKE) tools

.PHONY: test
test:
	cd rest && $(MAKE) test
	cd scheduler && $(MAKE) test

.PHONY: testcov
testcov:
	cd rest && $(MAKE) testcov
	cd scheduler && $(MAKE) testcov
	coverage combine rest/.coverage scheduler/.coverage
	coverage report
	coverage xml

.PHONY: prep
prep: tools test
	@echo "----- preparing $(BUILDNAME) build -----"
	mkdir -p $(BUILDROOT)/k8s && rm -rf $(BUILDROOT)/k8s/*
	# copy k8s configs to BUILDROOT
	cp -rp ./k8s/* $(BUILDROOT)/k8s


prod: prep
	@echo "----- building $(BUILDNAME) prod -----"
	read -p "About to build production image from $(BUILD_BRANCH) branch. Are you sure? (Y/N): " response ; \
	if [[ $$response == 'N' || $$response == 'n' ]] ; then exit 1 ; fi
	if [[ `git status --porcelain | wc -l` -gt 0 ]] ; then echo "You must stash your changes before proceeding" ; exit 1 ; fi
	git fetch && git checkout $(BUILD_BRANCH)
	$(eval GIT_COMMIT:=$(shell git rev-parse --short HEAD))
	sed -ie 's/THIS_STRING_IS_REPLACED_DURING_BUILD/$(DATE)/' $(BUILDROOT)/k8s/prod/deployment.yaml
	sed -ie 's/REPLACE_WITH_GIT_COMMIT/$(GIT_COMMIT)/' $(BUILDROOT)/k8s/prod/deployment.yaml
	cd rest && $(MAKE) build TAG=$(GIT_COMMIT) IMAGE=$(API_IMAGE)
	cd scheduler && $(MAKE) build TAG=$(GIT_COMMIT) IMAGE=$(SCHEDULER_IMAGE)
	git checkout -

ote: prep
	@echo "----- building $(BUILDNAME) ote -----"
	sed -ie 's/THIS_STRING_IS_REPLACED_DURING_BUILD/$(DATE)/g' $(BUILDROOT)/k8s/ote/deployment.yaml
	cd rest && $(MAKE) build IMAGE=$(API_IMAGE) TAG=ote
	cd scheduler && $(MAKE) build IMAGE=$(SCHEDULER_IMAGE) TAG=ote

dev: prep
	@echo "----- building $(BUILDNAME) dev -----"
	sed -ie 's/THIS_STRING_IS_REPLACED_DURING_BUILD/$(DATE)/g' $(BUILDROOT)/k8s/dev/deployment.yaml
	cd rest && $(MAKE) build IMAGE=$(API_IMAGE) TAG=dev
	cd scheduler && $(MAKE) build IMAGE=$(SCHEDULER_IMAGE) TAG=dev

prod-deploy: prod
	@echo "----- deploying $(BUILDNAME) prod -----"
	docker push $(API_IMAGE):$(GIT_COMMIT)
	docker push $(SCHEDULER_IMAGE):$(GIT_COMMIT)
	kubectl --context prod-dcu apply -f $(BUILDROOT)/k8s/prod/deployment.yaml --record

ote-deploy: ote
	@echo "----- deploying $(BUILDNAME) ote -----"
	docker push $(API_IMAGE):ote
	docker push $(SCHEDULER_IMAGE):ote
	kubectl --context ote-dcu apply -f $(BUILDROOT)/k8s/ote/deployment.yaml --record

dev-deploy: dev
	@echo "----- deploying $(BUILDNAME) dev -----"
	docker push $(API_IMAGE):dev
	docker push $(SCHEDULER_IMAGE):dev
	kubectl --context dev-dcu apply -f $(BUILDROOT)/k8s/dev/deployment.yaml --record

clean:
	@echo "----- cleaning $(BUILDNAME) app -----"
	rm -rf $(BUILDROOT)
	cd rest && $(MAKE) clean
	cd scheduler && $(MAKE) clean
