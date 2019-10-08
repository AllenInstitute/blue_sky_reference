#!/bin/bash
set -x

export PREFIX=/conda_envs
export ENV_BASE=${PREFIX}
export PY_37=${ENV_BASE}/py_37
#export FLASK=${ENV_BASE}/flask
export CIRCUS=${ENV_BASE}/circus
#export NB=${ENV_BASE}/nb
export PIP_INSTALL="pip install -q"
if [ -z "${APP_NAME}" ]; then
    APP_NAME=blue_sky
fi

cd /source/blue_sky_workflow_engine && make sdist
cd /source/${APP_NAME} && make sdist

mkdir -p ${ENV_BASE}

conda create -q --yes --prefix=${PY_37} --clone base
#conda create -q --yes --prefix=${FLASK} --clone base

#source activate ${FLASK} && (yes | ${PIP_INSTALL} -r /source/blue_sky_workflow_engine/flask_requirements.txt)

conda create -q --yes --prefix=${CIRCUS} python=2.7
source activate ${CIRCUS}
yes | ${PIP_INSTALL} -r /source/blue_sky_workflow_engine/circus_requirements.txt
yes | ${PIP_INSTALL} --upgrade --no-dependencies /source/blue_sky_workflow_engine/dist/*.tar.gz

source activate ${PY_37}
yes | ${PIP_INSTALL} -r /source/blue_sky_workflow_engine/requirements.txt
yes | ${PIP_INSTALL} -r /source/blue_sky_workflow_engine/test_requirements.txt
yes | ${PIP_INSTALL} -r /source/${APP_NAME}/requirements.txt
yes | ${PIP_INSTALL} -r /source/${APP_NAME}/test_requirements.txt
yes | ${PIP_INSTALL} -r /source/blue_sky_workflow_engine/nb_requirements.txt
yes | ${PIP_INSTALL} -r /source/blue_sky_workflow_engine/semantic_requirements.txt

#conda create -q --yes --prefix=${NB} --clone ${PY_37}
#source activate ${NB} && (yes | ${PIP_INSTALL} -r /blue_sky_workflow_engine/nb_requirements.txt)

