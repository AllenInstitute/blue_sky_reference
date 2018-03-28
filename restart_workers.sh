#!/bin/bash

pkill -9 -f "server_worker"
pkill -9 -f "run_execution_worker"
pkill -9 -f "runserver"
pkill -9 -f "worker_client"

export BASE_DIR=/blue_sky

rm ${BASE_DIR}/logs/server.log
rm ${BASE_DIR}/logs/execution_worker.log
rm ${BASE_DIR}/logs/debug.log

export WORKFLOW_CONFIG_YAML=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.WORKFLOW_CONFIG_YAML)")
export APP_PACKAGE=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.APP_PACKAGE)")
export MESSAGE_QUEUE_HOST=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.MESSAGE_QUEUE_HOST)")

DEBUG_LOG=${BASE_DIR}/logs/server.log python -m manage server_worker &
DEBUG_LOG=${BASE_DIR}/logs/server.log python -m manage celery_pbs_worker &
# DEBUG_LOG=${BASE_DIR}/logs/execution_worker.log python -m manage run_execution_worker &
DEBUG_LOG=${BASE_DIR}/logs/debug.log python -m manage runserver 0.0.0.0:8000 &

#export BLUE_SKY_WORKER_NAME=pbs

#python -m celery -A workflow_client.celery_worker_app worker \
# --loglevel=debug --concurrency=2 \
# -Q ${BLUE_SKY_WORKER_NAME}_${APP_PACKAGE} \
# -n ${BLUE_SKY_WORKER_NAME}_worker@${APP_PACKAGE} 2>&1 | \
# tee ${BASE_DIR}/logs/${BLUE_SKY_WORKER_NAME}_worker.log &
