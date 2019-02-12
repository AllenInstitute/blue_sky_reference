#!/bin/bash

pkill -9 -f "flower"
pkill -9 -f "circus"
pkill -9 -f "ui_server"
pkill -9 -f "beat"
pkill -9 -f "manage"
pkill -9 -f "notebook"

export MOAB_AUTH=':'

export BASE_DIR=/blue_sky

rm ${BASE_DIR}/logs/ingest.log
rm ${BASE_DIR}/logs/ui.log
rm ${BASE_DIR}/logs/moab.log
rm ${BASE_DIR}/logs/moab_status.log
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

echo 'STARTING RESULT WORKER'
DEBUG_LOG=${BASE_DIR}/logs/result.log \
  celery -A workflow_engine.celery.result_tasks worker \
  --concurrency=1 --loglevel=info -n result@blue_sky &
echo 'STARTING INGEST WORKER'
DEBUG_LOG=${BASE_DIR}/logs/ingest.log \
  celery -A workflow_engine.celery.ingest_tasks worker \
  --concurrency=1 --loglevel=info -n ingest@blue_sky &
echo 'STARTING WORKFLOW WORKER'
DEBUG_LOG=${BASE_DIR}/logs/workflow.log \
  celery -A workflow_engine.celery.worker_tasks worker \
  --concurrency=1 --loglevel=info -n workflow@blue_sky &
echo 'STARTING MOAB WORKER'
DEBUG_LOG=${BASE_DIR}/logs/moab.log \
  celery -A workflow_engine.celery.moab_tasks worker \
  --concurrency=1 --loglevel=info -n moab@blue_sky &
echo 'STARTING MOAB STATUS WORKER'
DEBUG_LOG=${BASE_DIR}/logs/moab_status.log \
  celery -A workflow_engine.celery.moab_status_tasks worker \
  --concurrency=1 --loglevel=info -n moab_status@blue_sky &
echo 'STARTING LOCAL WORKER'
DEBUG_LOG=${BASE_DIR}/logs/local.log \
  celery -A workflow_engine.celery.local_tasks worker \
  --concurrency=1 --loglevel=info -n local@blue_sky &
echo 'STARTING MONITOR WORKER'
DEBUG_LOG=${BASE_DIR}/logs/monitor.log \
  celery -A workflow_engine.celery.monitor_tasks worker \
  --concurrency=1 --loglevel=info -n monitor@blue_sky &
echo 'STARTING UI WORKER'
DEBUG_LOG=${BASE_DIR}/logs/ui.log python -m workflow_engine.ui_server &
echo 'STARTING CIRCUS'
DEBUG_LOG=${BASE_DIR}/logs/circus.log /bin/bash -c 'source activate circus; unset DJANGO_SETTING_MODULE; cd /blue_sky_workflow_engine/circus; /opt/conda/envs/circus/bin/circusd --daemon circus.ini; nohup celery -A workflow_client.tasks.circus_test worker --concurrency=1 --loglevel=info -n circus@blue_sky&'
DEBUG_LOG=${BASE_DIR}/logs/circus_status.log \
  celery -A workflow_engine.celery.circus_status_tasks worker \
  --concurrency=1 --loglevel=info -n circus_status@blue_sky &
echo 'STARTING NOTEBOOK WORKER'
/bin/bash -c 'source activate nb; cd notebooks; DEBUG_LOG=${BASE_DIR}/logs/nb.log nohup python -m manage shell_plus --notebook 2>&1 > /dev/null &'
sleep 20
echo 'STARTING MOAB BEAT'
DEBUG_LOG=${BASE_DIR}/logs/beat.log python -m celery -A workflow_engine.celery.moab_beat beat \
  --broker=amqp://blue_sky_user:blue_sky_user@${MESSAGE_QUEUE_HOST}:${MESSAGE_QUEUE_PORT} &

