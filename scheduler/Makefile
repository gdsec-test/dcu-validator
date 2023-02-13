BUILDNAME=digital-crimes/dcu-validator-scheduler
BUILDROOT=$(HOME)/dockerbuild/$(BUILDNAME)

.PHONY: prep build

all: env

env:
	pip install -r test_requirements.txt
	pip install -r requirements.txt

.PHONY: flake8
flake8:
	@echo "----- Running linter -----"
	flake8 --config ./.flake8 .

.PHONY: isort
isort:
	@echo "----- Optimizing imports -----"
	isort --atomic --skip .venv/ .

.PHONY: tools
tools: flake8 isort

.PHONY: test
test: tools
	@echo "----- Running tests -----"
	python -m unittest discover tests "*_tests.py"

.PHONY: testcov
testcov:
	@echo "----- Running tests with coverage -----"
	@coverage run --source=scheduler_service -m unittest discover tests "*_tests.py"
	@coverage xml
	@coverage report

prep:
	@echo "----- preparing $(IMAGE) build -----"
	mkdir -p $(BUILDROOT)
	cp -rp ./* $(BUILDROOT)
	cp -rp ~/.pip $(BUILDROOT)/pip_config

build: prep
	@echo "----- building $(IMAGE):$(TAG) -----"
	docker build -t $(IMAGE):$(TAG) $(BUILDROOT)

clean:
	@echo "----- cleaning $(BUILDROOT) -----"
	rm -rf $(BUILDROOT)
	
