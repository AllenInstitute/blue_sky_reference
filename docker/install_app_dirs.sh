#!/bin/bash

export PREFIX=/conda_envs
export ENV_BASE=${PREFIX}
export PY_37=${ENV_BASE}/py_37
export FLASK=${ENV_BASE}/flask
export CIRCUS=${ENV_BASE}/circus
export NB=${ENV_BASE}/nb
export PIP_INSTALL="pip install -q"
if [ -z "${APP_NAME}" ]; then
    APP_NAME=blue_sky
fi

mkdir -p ${ENV_BASE}

source activate ${PY_37} && \
  (cd /source/blue_sky_workflow_engine && make sdist) && \
  (cd /source/${APP_NAME} && make sdist) && \
  (yes | ${PIP_INSTALL} --upgrade --no-dependencies --target /app_dir /source/blue_sky_workflow_engine/dist/*.tar.gz) && \
  (yes | ${PIP_INSTALL} --upgrade --no-dependencies --target /app_dir /source/${APP_NAME}/dist/*.tar.gz)

