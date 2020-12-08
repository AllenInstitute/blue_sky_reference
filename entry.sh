#!/bin/bash

BASE_DIR=/blue_sky

export WORKFLOW_CONFIG_YAML=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.WORKFLOW_CONFIG_YAML)")
export APP_PACKAGE=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.APP_PACKAGE)")
export MESSAGE_QUEUE_HOST=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.MESSAGE_QUEUE_HOST)")
export MESSAGE_QUEUE_PORT=$(python -c "import ${DJANGO_SETTINGS_MODULE} as settings; print(settings.MESSAGE_QUEUE_PORT)")

#sleep 15
#DEBUG_LOG=${BASE_DIR}/logs/makemigrations.log python -m manage makemigrations --noinput
sleep 15
DEBUG_LOG=${BASE_DIR}/logs/migrate.log python -m manage migrate  --noinput
sleep 15

export DEBUG_LOG=${BASE_DIR}/logs/create_superuser.log
echo "from django.contrib.auth.models import User; User.objects.filter(email='admin@example.com').delete(); User.objects.create_superuser('blue_sky_user', 'admin@example.com', 'blue_sky_user')" | python -m manage shell

export DEBUG_LOG=${BASE_DIR}/logs/superuser_pass.log
printf "blue_sky_user\nt@a.org\nblue_sky_user\n" | python -m manage createsuperuser

echo "reading workflows from workflow config yaml: " ${WORKFLOW_CONFIG_YAML}
DEBUG_LOG=${BASE_DIR}/logs/import_workflows.log python -m manage import_workflows ${WORKFLOW_CONFIG_YAML}

#/bin/bash restart_workers.sh

while true; do sleep 3600; done
