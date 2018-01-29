#!/bin/bash

pkill -9 -f "server_worker"
pkill -9 -f "run_execution_worker"
pkill -9 -f "runserver"
pkill -9 -f "worker_client"

rm /log/server.log
rm /log/execution_worker.log
rm /log/debug.log

export WORKFLOW_CONFIG_YAML=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.WORKFLOW_CONFIG_YAML)")
export APP_PACKAGE=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.APP_PACKAGE)")
export MESSAGE_QUEUE_HOST=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.MESSAGE_QUEUE_HOST)")

DEBUG_LOG=/log/server.log python -m manage server_worker &
DEBUG_LOG=/log/execution_worker.log python -m manage run_execution_worker &
DEBUG_LOG=/log/debug.log python -m manage runserver 0.0.0.0:8000 &

python -m celery -A workflow_client.worker_client worker --loglevel=debug --concurrency=2 -Q ${APP_PACKAGE}2 -n server_worker@${APP_PACKAGE} &

export BLUE_SKY_WORKER_NAME=pbs
python -m celery -A workflow_client.worker_client worker \
 --loglevel=debug --concurrency=2 \
 -Q ${BLUE_SKY_WORKER_NAME}_${APP_PACKAGE} \
 -n ${BLUE_SKY_WORKER_NAME}_worker@${APP_PACKAGE} 2>&1 | \
 tee /log/${BLUE_SKY_WORKER_NAME}_worker.log &
