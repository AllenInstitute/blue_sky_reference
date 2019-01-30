#!/bin/bash

pkill -9 -f "circus_test"

source activate base

export BASE_DIR=/blue_sky

rm ${BASE_DIR}/logs/circus.log

export WORKFLOW_CONFIG_YAML=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.WORKFLOW_CONFIG_YAML)")
export APP_PACKAGE=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.APP_PACKAGE)")
export MESSAGE_QUEUE_HOST=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.MESSAGE_QUEUE_HOST)")
export MESSAGE_QUEUE_PORT=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.MESSAGE_QUEUE_PORT)")

DEBUG_LOG=${BASE_DIR}/logs/circus.log /bin/bash -c 'source activate circus; unset DJANGO_SETTING_MODULE; cd /blue_sky_workflow_engine/circus; /opt/conda/envs/circus/bin/circusd --daemon circus.ini; celery -A circus_test worker --concurrency=1 --loglevel=info -n circus@blue_sky'

