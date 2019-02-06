#!/bin/bash

pkill -9 -f "shell_plus"

export BASE_DIR=/blue_sky

rm ${BASE_DIR}/logs/nb.log

export WORKFLOW_CONFIG_YAML=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.WORKFLOW_CONFIG_YAML)")
export APP_PACKAGE=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.APP_PACKAGE)")
export MESSAGE_QUEUE_HOST=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.MESSAGE_QUEUE_HOST)")
export MESSAGE_QUEUE_PORT=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.MESSAGE_QUEUE_PORT)")

source activate base

echo 'STARTING NOTEBOOK WORKER'
#/bin/bash -c 'source activate nb; DEBUG_LOG=${BASE_DIR}/logs/nb.log nohup python -m manage shell_plus --notebook 2>&1 >> /dev/null &'
source activate nb; DEBUG_LOG=${BASE_DIR}/logs/nb.log python -m manage shell_plus --notebook
sleep 10
echo 'done'
