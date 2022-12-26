#!/bin/sh

SPEC_FILE=a
MODELERFOUR_VERSION="4.23.6"
AUTOREST_PYTHON_VERSION="6.0.1"
PACKAGE_VERSION:=0.0.1

echo "=== Generating client with spec: ${SPEC_FILE}\n\n"; \
npm run autorest -- client_gen_config.md \
    --output-converted-oai3 \
    --use:@autorest/modelerfour@${MODELERFOUR_VERSION} \
    --use:@autorest/python@${AUTOREST_PYTHON_VERSION} \
    --input-file=${SPEC_FILE}
#    --package-version=${PACKAGE_VERSION} \
#    --apply-transforms-in-place \
