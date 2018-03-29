# Allen Institute Software License - This software license is the 2-clause BSD
# license plus a third clause that prohibits redistribution for commercial
# purposes without further permission.
#
# Copyright 2018. Allen Institute. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Redistributions for commercial purposes are not permitted without the
# Allen Institute's written permission.
# For purposes of this license, commercial purposes is the incorporation of the
# Allen Institute's software into anything for which you will charge fees or
# other compensation. Contact terms@alleninstitute.org for commercial licensing
# opportunities.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
import pytest
#from tests.celery_helper import *
from mock import patch, Mock, MagicMock
from workflow_client.client_settings import settings_attr_dict
from workflow_engine.celery.workflow_tasks import *
from celery.contrib.pytest import celery_app, celery_worker
import time
from django.test.utils import override_settings
from tests.workflow.workflow_fixtures \
    import run_states, task_5, running_task_5


# @pytest.fixture(scope='session')
# def celery_parameters():
#     return {
#         'task_cls': 'workflow_client.celery_ingest_consumer'
#     }


@pytest.fixture(scope='session')
def celery_enable_logging():
    return True

@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'memory://',
        'result_backend': 'rpc',
        'task_default_exchange': 'blue_sky',
        'task_default_routing_key': 'result',
        'task_default_queue': 'result'
    }


@pytest.fixture(scope='session')
def celery_worker_parameters():
    return {
        'queues': ( 'workflow', 'result', 'null' )
    }

@pytest.fixture(scope='session')
def use_celery_app_trap():
    return True


@pytest.fixture(scope='session')
def celery_includes():
    return [
        'tests.workflow.test_result_worker'
    ]


@pytest.mark.django_db
@override_settings(
    APP_PACKAGE='blue_sky',
    PBS_MESSAGE_QUEUE_NAME='run', # TODO: not PBS QUEUE
    CELERY_MESSAGE_QUEUE_NAME='celery_blue_sky')
@pytest.mark.celery(task_cls='workflow_client.workflow_tasks')
def test_process_running(
        celery_app,
        celery_worker,
        task_5):
    configure_result_app(celery_app, 'blue_sky')

    result = process_running.apply_async(
        (5, ),
        queue='result')
    time.sleep(10)
    outpt = result.get()

    assert not result.failed()


@pytest.mark.django_db
@override_settings(
    APP_PACKAGE='blue_sky',
    PBS_MESSAGE_QUEUE_NAME='run', # TODO: not PBS QUEUE
    CELERY_MESSAGE_QUEUE_NAME='celery_blue_sky')
@pytest.mark.celery(task_cls='workflow_client.workflow_tasks')
def test_process_finished_execution(
        celery_app,
        celery_worker,
        running_task_5):
    configure_result_app(celery_app, 'blue_sky')

    result = process_finished_execution.apply_async(
        (5, ),
        queue='result')
    time.sleep(10)
    outpt = result.get()

    assert not result.failed()


@pytest.mark.django_db
@override_settings(
    APP_PACKAGE='blue_sky',
    PBS_MESSAGE_QUEUE_NAME='run', # TODO: not PBS QUEUE
    CELERY_MESSAGE_QUEUE_NAME='celery_blue_sky')
@pytest.mark.celery(task_cls='workflow_client.workflow_tasks')
def test_process_failed_execution(
        celery_app,
        celery_worker,
        running_task_5):
    configure_result_app(celery_app, 'blue_sky')

    result = process_failed_execution.apply_async(
        (5, ),
        queue='result')
    time.sleep(10)
    outpt = result.get()

    assert not result.failed()


@pytest.mark.django_db
@override_settings(
    APP_PACKAGE='blue_sky',
    PBS_MESSAGE_QUEUE_NAME='run', # TODO: not PBS QUEUE
    CELERY_MESSAGE_QUEUE_NAME='celery_blue_sky')
@pytest.mark.celery(task_cls='workflow_client.workflow_tasks')
def test_process_pbs_id(
        celery_app,
        celery_worker,
        task_5):
    configure_result_app(celery_app, 'blue_sky')

    mock_pbs_id = "123"

    assert task_5.pbs_id != mock_pbs_id

    result = process_pbs_id.apply_async(
        (task_5.id, mock_pbs_id),
        queue='result')
    time.sleep(10)
    outpt = result.get()

    assert not result.failed()
    updated_task = Task.objects.get(id=task_5.id)
    assert updated_task.pbs_id == mock_pbs_id
