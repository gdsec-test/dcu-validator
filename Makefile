REPONAME=ITSecurity/dcu-validator
BUILDROOT=$(HOME)/dockerbuild/$(REPONAME)
DOCKERREPO=artifactory.secureserver.net:10014/docker-dcu-local/dcu-validator
DATE=$(shell date)
COMMIT=
BUILD_BRANCH=origin/master
SHELL=/bin/bash

PRIVDEPS="git@github.secureserver.net/ITSecurity/dcdatabase.git"

.PHONY: prep dev stage ote prod clean dev-deploy ote-deploy prod-deploy

all: prep dev


prep:
	@echo "----- preparing $(REPONAME) build -----"
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
			if [ "$$revision" != "$$current_revision" ] ; then \
				read -p "Update to latest revision? (Y/N): " response ; \
				if [[ $$response == 'N' || $$response == 'n' ]] ; then \
					echo Reverting to revision: $$revision in $$repo ; \
					git reset --hard $$revision; \
				fi ; \
			fi ; \
		fi ; \
	done

	# copy the app code to the build root
	cp -rp ./* $(BUILDROOT)

prod: prep
	@echo "----- building $(REPONAME) prod -----"
	read -p "About to build production image from $(BUILD_BRANCH) branch. Are you sure? (Y/N): " response ; \
	if [[ $$response == 'N' || $$response == 'n' ]] ; then exit 1 ; fi
	if [[ `git status --porcelain | wc -l` -gt 0 ]] ; then echo "You must stash your changes before proceeding" ; exit 1 ; fi
	git fetch && git checkout $(BUILD_BRANCH)
	$(eval COMMIT:=$(shell git rev-parse --short HEAD))
	sed -ie 's/THIS_STRING_IS_REPLACED_DURING_BUILD/$(DATE)/' $(BUILDROOT)/k8s/prod/dcuvalidator.deployment.yml
	sed -ie 's/REPLACE_WITH_GIT_COMMIT/$(COMMIT)/' $(BUILDROOT)/k8s/prod/dcuvalidator.deployment.yml
	docker build -t $(DOCKERREPO):$(COMMIT) $(BUILDROOT)
	git checkout -

ote: prep
	@echo "----- building $(REPONAME) ote -----"
	sed -ie 's/THIS_STRING_IS_REPLACED_DURING_BUILD/$(DATE)/g' $(BUILDROOT)/k8s/ote/dcuvalidator.deployment.yml
	docker build -t $(DOCKERREPO):ote $(BUILDROOT)

dev: prep
	@echo "----- building $(REPONAME) dev -----"
	sed -ie 's/THIS_STRING_IS_REPLACED_DURING_BUILD/$(DATE)/g' $(BUILDROOT)/k8s/dev/dcuvalidator.deployment.yml
	docker build -t $(DOCKERREPO):dev $(BUILDROOT)

test: prep
	@echo "----- building $(REPONAME) test -----"
	sed -ie 's/THIS_STRING_IS_REPLACED_DURING_BUILD/$(DATE)/g' $(BUILDROOT)/k8s/dev/test.dcuvalidator.deployment.yml
	docker build -t $(DOCKERREPO):test $(BUILDROOT)

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

test-deploy: test
	@echo "----- deploying $(REPONAME) test -----"
	docker push $(DOCKERREPO):test
	kubectl --context dev apply -f $(BUILDROOT)/k8s/dev/test.dcuvalidator.deployment.yml --record

clean:
	@echo "----- cleaning $(REPONAME) app -----"
	rm -rf $(BUILDROOT)
