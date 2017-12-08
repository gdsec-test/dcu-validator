REPONAME=ITSecurity/dcu-validator
BUILDROOT=$(HOME)/dockerbuild/$(REPONAME)
DATE=$(shell date)
GIT_COMMIT=
BUILD_BRANCH=origin/master
SHELL=/bin/bash

.PHONY: prep dev stage ote prod clean dev-deploy ote-deploy prod-deploy

all: prep dev


prep:
	@echo "----- preparing $(REPONAME) build -----"
	mkdir -p $(BUILDROOT)/k8s && rm -rf $(BUILDROOT)/k8s/*
	# copy k8s configs to BUILDROOT
	cp -rp ./k8s/* $(BUILDROOT)/k8s


prod: prep
	@echo "----- building $(REPONAME) prod -----"
	read -p "About to build production image from $(BUILD_BRANCH) branch. Are you sure? (Y/N): " response ; \
	if [[ $$response == 'N' || $$response == 'n' ]] ; then exit 1 ; fi
	if [[ `git status --porcelain | wc -l` -gt 0 ]] ; then echo "You must stash your changes before proceeding" ; exit 1 ; fi
	git fetch && git checkout $(BUILD_BRANCH)
	$(eval GIT_COMMIT:=$(shell git rev-parse --short HEAD))
	sed -ie 's/THIS_STRING_IS_REPLACED_DURING_BUILD/$(DATE)/' $(BUILDROOT)/k8s/prod/dcuvalidator.deployment.yml
	sed -ie 's/REPLACE_WITH_GIT_COMMIT/$(GIT_COMMIT)/' $(BUILDROOT)/k8s/prod/dcuvalidator.deployment.yml
	cd rest && $(MAKE) TAG=$(GIT_COMMIT) prod
	cd scheduler && $(MAKE) TAG=$(GIT_COMMIT) prod
	git checkout -

ote: prep
	@echo "----- building $(REPONAME) ote -----"
	sed -ie 's/THIS_STRING_IS_REPLACED_DURING_BUILD/$(DATE)/g' $(BUILDROOT)/k8s/ote/dcuvalidator.deployment.yml
	cd rest && $(MAKE) ote
	cd scheduler && $(MAKE) ote

dev: prep
	@echo "----- building $(REPONAME) dev -----"
	sed -ie 's/THIS_STRING_IS_REPLACED_DURING_BUILD/$(DATE)/g' $(BUILDROOT)/k8s/dev/dcuvalidator.deployment.yml
	cd rest && $(MAKE) dev
	cd scheduler && $(MAKE) dev

prod-deploy: prod
	@echo "----- deploying $(REPONAME) prod -----"
	docker push $(DOCKERREPO):$(COMMIT)
	kubectl --context prod apply -f $(BUILDROOT)/k8s/prod/dcuvalidator.deployment.yml --record

ote-deploy: ote
	@echo "----- deploying $(REPONAME) ote -----"
	docker push $(DOCKERREPO):ote
	kubectl --context ote apply -f $(BUILDROOT)/k8s/ote/dcuvalidator.deployment.yml --record

dev-deploy: dev
	@echo "----- deploying $(REPONAME) dev -----"
	docker push $(DOCKERREPO):dev
	kubectl --context dev apply -f $(BUILDROOT)/k8s/dev/dcuvalidator.deployment.yml --record

clean:
	@echo "----- cleaning $(REPONAME) app -----"
	rm -rf $(BUILDROOT)
