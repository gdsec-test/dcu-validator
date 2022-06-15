BUILDNAME=digital-crimes/dcu-validator
DOCKERREPO=docker-dcu-local.artifactory.secureserver.net/dcu-validator/dcu-validator-scheduler
BUILDROOT=$(HOME)/dockerbuild/$(BUILDNAME)
DATE=$(shell date)
GIT_COMMIT=
BUILD_BRANCH=origin/main
SCHEDULER_IMAGE=$(DOCKERREPO)/dcu-validator-scheduler

.PHONY: prep dev stage test-env ote prod clean dev-deploy ote-deploy prod-deploy prod-deploy
define deploy_k8s
	docker push $(SCHEDULER_IMAGE):$(2)
	cd k8s/$(1) && kustomize edit set image $$(docker inspect --format='{{index .RepoDigests 0}}' $(SCHEDULER_IMAGE):$(2))
	kubectl --context $(1)-dcu apply -k k8s/$(1)
	cd k8s/$(1) && kustomize edit set image $(SCHEDULER_IMAGE):$(1)
endef

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
	cd scheduler && $(MAKE) build TAG=$(GIT_COMMIT) IMAGE=$(SCHEDULER_IMAGE)
	git checkout -

ote: prep
	@echo "----- building $(BUILDNAME) ote -----"
	cd scheduler && $(MAKE) build IMAGE=$(SCHEDULER_IMAGE) TAG=ote

test-env: prep
	@echo "----- building $(BUILDNAME) dev -----"
	cd scheduler && $(MAKE) build IMAGE=$(SCHEDULER_IMAGE) TAG=test

dev: prep
	@echo "----- building $(BUILDNAME) dev -----"
	cd scheduler && $(MAKE) build IMAGE=$(SCHEDULER_IMAGE) TAG=dev

prod-deploy: prod
	@echo "----- deploying $(BUILDNAME) prod -----"
	$(call deploy_k8s,prod,$(GIT_COMMIT))

ote-deploy: ote
	@echo "----- deploying $(BUILDNAME) ote -----"
	$(call deploy_k8s,ote,ote)

test-deploy: test-env
	@echo "----- deploying $(BUILDNAME) test -----"
	$(call deploy_k8s,test,test)

dev-deploy: dev
	@echo "----- deploying $(BUILDNAME) dev -----"
	$(call deploy_k8s,dev,dev)

clean:
	@echo "----- cleaning $(BUILDNAME) app -----"
	rm -rf $(BUILDROOT)
	cd scheduler && $(MAKE) clean
