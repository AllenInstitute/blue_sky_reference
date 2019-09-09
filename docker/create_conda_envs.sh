#!/bin/bash

export PREFIX=/conda_envs
export ENV_BASE=${PREFIX}
export PY_37=${ENV_BASE}/py_37
export FLASK=${ENV_BASE}/flask
export CIRCUS=${ENV_BASE}/circus
export NB=${ENV_BASE}/nb
export PIP_INSTALL="pip install -q"

mkdir -p ${ENV_BASE}

conda create -q --yes --prefix=${PY_37} --clone base

conda create -q --yes --prefix=${FLASK} --clone ${PY_37}

source activate ${FLASK} && (yes | ${PIP_INSTALL} -r /blue_sky_workflow_engine/flask_requirements.txt)

conda create -q --yes --prefix=${CIRCUS} python=2.7
source activate ${CIRCUS} && (${PIP_INSTALL} -r /blue_sky_workflow_engine/circus_requirements.txt)

source activate ${PY_37} && \
  (yes | ${PIP_INSTALL} -r /blue_sky_workflow_engine/requirements.txt) && \
  (yes | ${PIP_INSTALL} -r /blue_sky_workflow_engine/test_requirements.txt) && \
  (yes | ${PIP_INSTALL} -r /blue_sky/requirements.txt) && \
  (yes | ${PIP_INSTALL} -r /blue_sky/test_requirements.txt)


conda create -q --yes --prefix=${NB} --clone ${PY_37}
source activate ${NB} && (yes | ${PIP_INSTALL} -r /blue_sky_workflow_engine/nb_requirements.txt)

