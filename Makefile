LOCAL_SPEC_FILE=./openapi.fixed.yaml
MODELERFOUR_VERSION="4.23.6"
#AUTOREST_PYTHON_VERSION="6.0.1"
AUTOREST_PYTHON_VERSION="6.1.6"
POETRY_VERSION:=$(shell poetry version)
PACKAGE_VERSION:=$(lastword $(POETRY_VERSION))
ROOT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
ORIGIN ?= origin
BUMP ?= patch
OPENAPI_CODEGEN_IMAGE=openapitools/openapi-generator-cli@${OPENAPI_CODEGEN_SHA}
DOCKER_OPENAPI=docker run --rm -u ${CURRENT_UID}:${CURRENT_GID} -v $(CURDIR):/local ${OPENAPI_CODEGEN_IMAGE}


ifeq (, $(findstring -m,$(PYTEST_ARGS)))
	PYTEST_EXCLUDE_MARKS=-m "not real_billing"
endif

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'; \
	printf "\nNOTE: Run 'SPEC_FILE=path/to/local/spec make generate' to skip the download and use a local spec file.\n"

.PHONY: dev-dependencies
dev-dependencies: ## Install development tooling
	npm install --only=dev

.PHONY: clean
clean: ## Removes all generated code (except _patch.py files)
	@printf "=== Cleaning src directory\n"
	@find src/equinixmetalpy -type f ! -name "_patch.py" ! -name "custom_*.py" ! -name "exceptions.py" -exec rm -rf {} +

#.PHONY: download-spec 
#download-spec: ## Download Latest DO Spec
#	@echo Downloading published spec; \
#	touch api-docs && \
#	curl  https://api.equinix.com/metal/v1/api-docs -o $(LOCAL_SPEC_FILE)
#

SPEC_DIR_ENTRY_POINT=oas3.fetched/openapi/public/openapi3.yaml
STITCHED_DIR=oas3.stitched
STITCHED_FILE=metal.yaml
OPENAPI_CODEGEN_SHA=sha256:be8c2ef6be22f695410c2cc13d0ec7fdf2533fc88a7f17288ad758b7679de8df


stitch-spec:
	${DOCKER_OPENAPI} generate \
		-i /local/${SPEC_DIR_ENTRY_POINT} \
		-g openapi-yaml \
		-p skipOperationExample=true -p outputFile=${STITCHED_FILE} \
		-o /local/${STITCHED_DIR}

patch-spec: stitch-spec
	scripts/patch_metal_spec.py ${STITCHED_DIR}/${STITCHED_FILE} ${LOCAL_SPEC_FILE}



.PHONY: generate
ifndef SPEC_FILE
generate: SPEC_FILE = $(LOCAL_SPEC_FILE)
generate: dev-dependencies ## Generates the python client using the latest published spec first.
endif
generate: install clean dev-dependencies patch-spec
	@printf "=== Generating client with spec: $(SPEC_FILE)\n\n"; \
	npm run autorest -- client_gen_config.md \
		--use:@autorest/modelerfour@$(MODELERFOUR_VERSION) \
		--use:@autorest/python@$(AUTOREST_PYTHON_VERSION) \
		--package-version=$(PACKAGE_VERSION) \
		--input-file=$(SPEC_FILE)

	@poetry run black src

.PHONY: install
install: ## Install test dependencies
ifneq (, $(shell which poetry))
	poetry install --no-interaction -E aio
else
	@(echo "poetry is not installed. See https://python-poetry.org/docs/#installation for more info."; exit 1)
endif

.PHONY: dev
dev: dev-dependencies # Turns the current terminal into a poetry env
	poetry shell

.PHONY: test-mocked
test-integration: install
	poetry run pytest -rA --tb=short tests/integration/. $(PYTEST_EXCLUDE_MARKS) $(PYTEST_ARGS)

# This command runs a single integration test
# > make test-integration-single test=test_actions
.PHONY: test-mocked
test-integration-single: install
	poetry run pytest -rA --tb=short tests/integration/. -k $(test)

.PHONY: docker-build
docker-build:
	docker build -t equinixmetalpy:dev .

.PHONY: docker-python
docker-python: docker-build  ## Runs a python shell within a docker container
	docker run -it --rm --name equinixmetalpy equinixmetalpy:dev python

.PHONY: lint-docs
lint-docs:
	docker run -v $(ROOT_DIR):/workdir ghcr.io/igorshubovych/markdownlint-cli:latest "README.md"

.PHONY: generate-docs
generate-docs: install ## readthedocs requires a requirements.txt file, this step converts poetry file to requirements.txt file before re-gen the docs
	@echo Generating documentation...;
	@echo Converting poetry file to requirements.txt...; 
	poetry export -f requirements.txt -o requirements.txt --without-hashes
	cd docs && \
	poetry run sphinx-apidoc -o source/ ../src/equinixmetalpy && \
	poetry run make html

.PHONY: clean-docs
clean-docs: ## Delete everything in docs/build/html
	cd docs && \
	poetry run make clean

.PHONY: _install_github_release_notes
_install_github_release_notes:
	@GO111MODULE=off go get -u github.com/digitalocean/github-changelog-generator

.PHONY: changes
changes: _install_github_release_notes
	@echo "==> Merged PRs since last release"
	@echo ""
	@github-changelog-generator -org t0mk -repo equinixmetalpy

.PHONY: version
version:
	@poetry version

.PHONY: _install_sembump
_install_sembump:
	@echo "=> installing/updating sembump tool"
	@echo ""
	@GO111MODULE=off go get -u github.com/jessfraz/junk/sembump

.PHONY: bump_version
bump_version: _install_sembump
	@echo "==> BUMP=${BUMP} bump_version"
	@echo ""
	@ORIGIN=${ORIGIN} scripts/bumpversion.sh

.PHONY: tag
tag:
	@echo "==> ORIGIN=${ORIGIN} COMMIT=${COMMIT} tag"
	@echo ""
	@ORIGIN=${ORIGIN} scripts/tag.sh
