#!/bin/bash

pkill -9 -f "flower"
pkill -9 -f "circus"
pkill -9 -f "ui_server"
pkill -9 -f "beat"
pkill -9 -f "manage"
pkill -9 -f "notebook"

export MOAB_AUTH=':'

export BASE_DIR=/blue_sky
export PYTHONPATH=/blue_sky:/blue_sky_workflow_engine

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

unset DJANGO_SETTINGS_MODULE

source activate /conda_envs/py_36

/bin/bash -c "source activate /conda_envs/py_36; python -m workflow_engine.process.process_manager blue_sky /home/blue_sky_user/work&"

