#!/bin/bash

pkill -9 -f "server_worker"
pkill -9 -f "workflow_worker"
pkill -9 -f "runserver"
pkill -9 -f "worker_client"
pkill -9 -f "moab_worker"
pkill -9 -f "celery_pbs_worker"
pkill -9 -f "result_worker"


export BASE_DIR=/blue_sky

rm ${BASE_DIR}/logs/worker.log
rm ${BASE_DIR}/logs/ui.log
rm ${BASE_DIR}/logs/pbs.log
rm ${BASE_DIR}/logs/moab.log
rm ${BASE_DIR}/logs/workflow.log
rm ${BASE_DIR}/logs/result.log


export WORKFLOW_CONFIG_YAML=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.WORKFLOW_CONFIG_YAML)")
export APP_PACKAGE=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.APP_PACKAGE)")
export MESSAGE_QUEUE_HOST=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.MESSAGE_QUEUE_HOST)")

DEBUG_LOG=${BASE_DIR}/logs/result.log python -m manage result_worker &
DEBUG_LOG=${BASE_DIR}/logs/worker.log python -m manage server_worker &
DEBUG_LOG=${BASE_DIR}/logs/pbs.log python -m manage celery_pbs_worker &
DEBUG_LOG=${BASE_DIR}/logs/workflow.log python -m manage workflow_worker &
DEBUG_LOG=${BASE_DIR}/logs/moab.log python -m manage moab_worker &
# DEBUG_LOG=${BASE_DIR}/logs/execution_worker.log python -m manage run_execution_worker &
DEBUG_LOG=${BASE_DIR}/logs/ui.log python -m manage runserver 0.0.0.0:8000 &

#export BLUE_SKY_WORKER_NAME=pbs

#python -m celery -A workflow_client.celery_worker_app worker \
# --loglevel=debug --concurrency=2 \
# -Q ${BLUE_SKY_WORKER_NAME}_${APP_PACKAGE} \
# -n ${BLUE_SKY_WORKER_NAME}_worker@${APP_PACKAGE} 2>&1 | \
# tee ${BASE_DIR}/logs/${BLUE_SKY_WORKER_NAME}_worker.log &
