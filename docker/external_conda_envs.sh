#!/bin/bash
set -x

export PREFIX=/conda_envs
export ENV_BASE=${PREFIX}
export RENDER_MODULES=${ENV_BASE}/render_modules
export PIP_INSTALL="pip install -q"
if [ -z "${APP_NAME}" ]; then
    APP_NAME=blue_sky
fi

conda create -q --yes --prefix=${RENDER_MODULES} python=2.7

source activate ${RENDER_MODULES}
yes | ${PIP_INSTALL} -r /source/render_modules/requirements.txt
yes | ${PIP_INSTALL} --upgrade /source/render_modules
${PIP_INSTALL} boto3

