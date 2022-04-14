BUILDNAME=digital-crimes/dcu-validator
DOCKERREPO=docker-dcu-local.artifactory.secureserver.net
BUILDROOT=$(HOME)/dockerbuild/$(BUILDNAME)
DATE=$(shell date)
GIT_COMMIT=
BUILD_BRANCH=origin/main
SCHEDULER_IMAGE=$(DOCKERREPO)/dcu-validator-scheduler

.PHONY: prep dev stage test-env ote prod clean dev-deploy ote-deploy prod-deploy prod-deploy

all: prep

.PHONY: env
env:
	pip install -r scheduler/test_requirements.txt
	pip install -r scheduler/requirements.txt

.PHONY: tools
tools:
	cd scheduler && $(MAKE) tools

.PHONY: test
test:
	cd scheduler && $(MAKE) test

.PHONY: testcov
testcov:
	cd scheduler && $(MAKE) testcov
	coverage combine scheduler/.coverage
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
	cd scheduler && $(MAKE) build TAG=$(GIT_COMMIT) IMAGE=$(SCHEDULER_IMAGE)
	git checkout -

ote: prep
	@echo "----- building $(BUILDNAME) ote -----"
	sed -ie 's/THIS_STRING_IS_REPLACED_DURING_BUILD/$(DATE)/g' $(BUILDROOT)/k8s/ote/deployment.yaml
	cd scheduler && $(MAKE) build IMAGE=$(SCHEDULER_IMAGE) TAG=ote

test-env: prep
	@echo "----- building $(BUILDNAME) dev -----"
	sed -ie 's/THIS_STRING_IS_REPLACED_DURING_BUILD/$(DATE)/g' $(BUILDROOT)/k8s/test/deployment.yaml
	cd scheduler && $(MAKE) build IMAGE=$(SCHEDULER_IMAGE) TAG=test

dev: prep
	@echo "----- building $(BUILDNAME) dev -----"
	sed -ie 's/THIS_STRING_IS_REPLACED_DURING_BUILD/$(DATE)/g' $(BUILDROOT)/k8s/dev/deployment.yaml
	cd scheduler && $(MAKE) build IMAGE=$(SCHEDULER_IMAGE) TAG=dev

prod-deploy: prod
	@echo "----- deploying $(BUILDNAME) prod -----"
	docker push $(SCHEDULER_IMAGE):$(GIT_COMMIT)
	kubectl --context prod-admin apply -f $(BUILDROOT)/k8s/prod/deployment.yaml

ote-deploy: ote
	@echo "----- deploying $(BUILDNAME) ote -----"
	docker push $(SCHEDULER_IMAGE):ote
	kubectl --context ote-dcu apply -f $(BUILDROOT)/k8s/ote/deployment.yaml

test-deploy: test-env
	@echo "----- deploying $(BUILDNAME) test -----"
	docker push $(SCHEDULER_IMAGE):test
	kubectl --context test-dcu apply -f $(BUILDROOT)/k8s/test/deployment.yaml

dev-deploy: dev
	@echo "----- deploying $(BUILDNAME) dev -----"
	docker push $(SCHEDULER_IMAGE):dev
	kubectl --context dev-admin apply -f $(BUILDROOT)/k8s/dev/deployment.yaml

clean:
	@echo "----- cleaning $(BUILDNAME) app -----"
	rm -rf $(BUILDROOT)
	cd scheduler && $(MAKE) clean
