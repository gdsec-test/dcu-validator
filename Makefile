BUILDNAME=ITSecurity/dcu-validator
DOCKERREPO=docker-dcu-local.artifactory.secureserver.net
BUILDROOT=$(HOME)/dockerbuild/$(BUILDNAME)
DATE=$(shell date)
GIT_COMMIT=
BUILD_BRANCH=origin/master
SHELL=/bin/bash
API_IMAGE=$(DOCKERREPO)/dcu-validator-api
SCHEDULER_IMAGE=$(DOCKERREPO)/dcu-validator-scheduler

.PHONY: prep dev stage ote prod clean dev-deploy ote-deploy prod-deploy

all: prep dev

.PHONY: flake8
flake8:
	cd rest && $(MAKE) flake8
	cd scheduler && $(MAKE) flake8

.PHONY: isort
isort:
	cd rest && $(MAKE) isort
	cd scheduler && $(MAKE) isort

.PHONY: tools
tools: flake8 isort

.PHONY: test
test:
	cd rest && $(MAKE) test
	cd scheduler && $(MAKE) test

.PHONY: testcov
testcov:
	cd rest && $(MAKE) testcov
	cd scheduler && $(MAKE) testcov

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
	sed -ie 's/THIS_STRING_IS_REPLACED_DURING_BUILD/$(DATE)/' $(BUILDROOT)/k8s/prod/dcuvalidator.deployment.yml
	sed -ie 's/REPLACE_WITH_GIT_COMMIT/$(GIT_COMMIT)/' $(BUILDROOT)/k8s/prod/dcuvalidator.deployment.yml
	cd rest && $(MAKE) build TAG=$(GIT_COMMIT) IMAGE=$(API_IMAGE)
	cd scheduler && $(MAKE) build TAG=$(GIT_COMMIT) IMAGE=$(SCHEDULER_IMAGE)
	git checkout -

ote: prep
	@echo "----- building $(BUILDNAME) ote -----"
	sed -ie 's/THIS_STRING_IS_REPLACED_DURING_BUILD/$(DATE)/g' $(BUILDROOT)/k8s/ote/dcuvalidator.deployment.yml
	cd rest && $(MAKE) build IMAGE=$(API_IMAGE) TAG=ote
	cd scheduler && $(MAKE) build IMAGE=$(SCHEDULER_IMAGE) TAG=ote

dev: prep
	@echo "----- building $(BUILDNAME) dev -----"
	sed -ie 's/THIS_STRING_IS_REPLACED_DURING_BUILD/$(DATE)/g' $(BUILDROOT)/k8s/dev/dcuvalidator.deployment.yml
	cd rest && $(MAKE) build IMAGE=$(API_IMAGE) TAG=dev
	cd scheduler && $(MAKE) build IMAGE=$(SCHEDULER_IMAGE) TAG=dev

prod-deploy: prod
	@echo "----- deploying $(BUILDNAME) prod -----"
	docker push $(API_IMAGE):$(GIT_COMMIT)
	docker push $(SCHEDULER_IMAGE):$(GIT_COMMIT)
	kubectl --context prod apply -f $(BUILDROOT)/k8s/prod/dcuvalidator.deployment.yml --record

ote-deploy: ote
	@echo "----- deploying $(BUILDNAME) ote -----"
	docker push $(API_IMAGE):ote
	docker push $(SCHEDULER_IMAGE):ote
	kubectl --context ote apply -f $(BUILDROOT)/k8s/ote/dcuvalidator.deployment.yml --record

dev-deploy: dev
	@echo "----- deploying $(BUILDNAME) dev -----"
	docker push $(API_IMAGE):dev
	docker push $(SCHEDULER_IMAGE):dev
	kubectl --context dev apply -f $(BUILDROOT)/k8s/dev/dcuvalidator.deployment.yml --record

clean:
	@echo "----- cleaning $(BUILDNAME) app -----"
	rm -rf $(BUILDROOT)
	cd rest && $(MAKE) clean
	cd scheduler && $(MAKE) clean
