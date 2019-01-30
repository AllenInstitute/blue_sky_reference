#!/bin/bash
set -x

pkill -9 -f "flower"
pkill -9 -f "circus"
pkill -9 -f "ui_server"
pkill -9 -f "beat"
pkill -9 -f "manage"
pkill -9 -f "notebook"

export MOAB_AUTH=''

export BASE_DIR=/blue_sky

rm ${BASE_DIR}/logs/worker.log
rm ${BASE_DIR}/logs/ui.log
rm ${BASE_DIR}/logs/moab.log
rm ${BASE_DIR}/logs/monitor.log
rm ${BASE_DIR}/logs/workflow.log
rm ${BASE_DIR}/logs/local.log
rm ${BASE_DIR}/logs/circus.log
rm ${BASE_DIR}/logs/result.log
rm ${BASE_DIR}/logs/beat.log
rm celerybeat.pid

export WORKFLOW_CONFIG_YAML=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.WORKFLOW_CONFIG_YAML)")
export APP_PACKAGE=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.APP_PACKAGE)")
export MESSAGE_QUEUE_HOST=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.MESSAGE_QUEUE_HOST)")
export MESSAGE_QUEUE_PORT=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.MESSAGE_QUEUE_PORT)")

source activate base

python -m celery flower --url_prefix=flower \
  --backend=rpc:// \
  --broker=amqp://blue_sky_user:blue_sky_user@${MESSAGE_QUEUE_HOST}:${MESSAGE_QUEUE_PORT} \
  -n flower@${APP_PACKAGE} &
